from celery import Celery
import io
import csv
import os
import smtplib
from celery.schedules import crontab
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import calendar
from datetime import date, datetime, timedelta
from sqlalchemy.orm import joinedload
from flask_caching import Cache

from models.models import db, User, Appointment

cache = Cache()

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['broker_url'],
        backend=app.config['result_backend']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Set time
    celery.conf.beat_schedule = {
        'daily-appointment-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        'monthly-doctor-report': {
            'task': 'tasks.send_monthly_reports',
            'schedule': crontab(day_of_month=11, hour=18, minute=5),
        },
    }

    return celery

# Send email
def send_email(to_email, subject, body_html, attachment=None, filename=None):
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")

    if not mail_username or not mail_password:
        print(f"[EMAIL MOCK] To: {to_email}, Subject: {subject}")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = mail_username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        if attachment and filename:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)

        with smtplib.SMTP(mail_server, 587) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email error:", e)
        return False

# TASKS
def register_tasks(celery, app):
    # Daily reminder
    @celery.task(name="tasks.send_daily_reminders")
    def send_daily_reminders():
        with app.app_context():
            today = date.today()
            appointments = Appointment.query.options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor)
            ).filter(
                Appointment.date == today,
                Appointment.status == "Booked"
            ).all()

            for appt in appointments:
                patient = appt.patient
                doctor = appt.doctor

                if not patient or not doctor or not patient.email:
                    continue

                message = (
                    f"🏥 Appointment Reminder\n"
                    f"Dear {patient.full_name}, you have an appointment today at "
                    f"{appt.time.strftime('%H:%M')} with Dr. {doctor.full_name} "
                    f"({doctor.specialization})."
                )

                send_email(
                    patient.email,
                    "Appointment Reminder - Today",
                    f"<p>{message.replace(chr(10), '<br>')}</p>"
                )

            print(f"Sent {len(appointments)} reminders")
            return len(appointments)

    # Monthly report
    @celery.task(name="tasks.send_monthly_reports")
    def send_monthly_reports():
        with app.app_context():
            today = date.today()
            prev_month = today.month - 1 or 12
            year = today.year if today.month != 1 else today.year - 1
            first_day = date(year, prev_month, 1)
            last_day = date(year, prev_month, calendar.monthrange(year, prev_month)[1])

            doctors = User.query.filter_by(role="doctor").all()
            for doctor in doctors:
                appointments = Appointment.query.options(
                    joinedload(Appointment.patient),
                    joinedload(Appointment.treatment)
                ).filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= first_day,
                    Appointment.date <= last_day
                ).all()

                if not appointments or not doctor.email:
                    continue

                html = generate_monthly_report_html(doctor, appointments, first_day)
                send_email(
                    doctor.email,
                    f"Monthly Activity Report - {first_day.strftime('%B %Y')}",
                    html
                )

            print(f"Sent monthly reports to {len(doctors)} doctors")
            return len(doctors)

    # Export patient CSV
    @celery.task(name="tasks.export_patient_csv")
    def export_patient_csv(patient_id):
        with app.app_context():
            patient = db.session.get(User, patient_id)
            if not patient or patient.role != "patient":
                return {"status": "error", "message": "Patient not found or invalid role"}

            appointments = Appointment.query.options(
                joinedload(Appointment.doctor),
                joinedload(Appointment.treatment)
            ).filter_by(
                patient_id=patient_id,
                status="Completed"
            ).order_by(Appointment.date.desc()).all()

            if not appointments:
                return {"status": "success", "rows": 0, "message": "No completed appointments"}

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Patient ID", "Patient Name", "Doctor", "Specialization", "Date", "Time", "Diagnosis", "Prescription", "Notes"])

            for appt in appointments:
                treatment = appt.treatment
                writer.writerow([
                    patient.id,
                    patient.full_name,
                    appt.doctor.full_name if appt.doctor else "",
                    appt.doctor.specialization if appt.doctor else "",
                    appt.date.isoformat(),
                    appt.time.strftime("%H:%M") if appt.time else "",
                    treatment.diagnosis if treatment else "",
                    treatment.prescription if treatment else "",
                    treatment.notes if treatment else "",
                ])

            csv_bytes = output.getvalue().encode("utf-8")
            if patient.email:
                send_email(
                    patient.email,
                    "Your Treatment History Export",
                    "<p>Please find your treatment history attached.</p>",
                    attachment=csv_bytes,
                    filename=f"treatment_history_{patient.id}.csv"
                )

            return {"status": "success", "rows": len(appointments)}

    return {
        "send_daily_reminders": send_daily_reminders,
        "send_monthly_reports": send_monthly_reports,
        "export_patient_csv": export_patient_csv
    }

# Report html
def generate_monthly_report_html(doctor, appointments, month):
    completed = [a for a in appointments if a.status.lower() == "completed"]
    cancelled = [a for a in appointments if a.status.lower() == "cancelled"]

    rows = ""
    for appt in appointments:
        t = appt.treatment
        rows += f"""
        <tr>
            <td>{appt.date}</td>
            <td>{appt.time.strftime('%H:%M') if appt.time else ''}</td>
            <td>{appt.patient.full_name if appt.patient else 'N/A'}</td>
            <td>{appt.status}</td>
            <td>{t.diagnosis if t else '-'}</td>
            <td>{t.prescription if t else '-'}</td>
        </tr>"""

    return f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
    <h2>Monthly Activity Report</h2>
    <h3>Dr. {doctor.full_name} - {month.strftime('%B %Y')}</h3>
    <p><strong>Specialization:</strong> {doctor.specialization or 'N/A'}</p>
    <p><strong>Total Appointments:</strong> {len(appointments)}</p>
    <p><strong>Completed:</strong> {len(completed)}</p>
    <p><strong>Cancelled:</strong> {len(cancelled)}</p>

    <table style="width: 100%; border-collapse: collapse;" border="1" cellpadding="5">
        <thead>
            <tr style="background: #1a73e8; color: white;">
                <th>Date</th>
                <th>Time</th>
                <th>Patient</th>
                <th>Status</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    </body></html>
    """