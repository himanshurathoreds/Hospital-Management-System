from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Appointment, Department, TimeSlot
from datetime import date, timedelta
from routes.util import role_required
from routes.tasks import cache  # Use the Flask-Caching instance

patient_api = Blueprint('patient_api', __name__)


@patient_api.route('/patient/dashboard', methods=['GET'])
@jwt_required()
@role_required('patient')
def patient_dashboard():
    patient_id = int(get_jwt_identity())

    # Cache
    departments = cache.get('departments_with_doctors')
    if not departments:
        departments = [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "doctors": [
                    {"id": doc.id, "full_name": doc.full_name, "specialization": doc.specialization}
                    for doc in d.doctors if doc.role == "doctor"
                ]
            }
            for d in Department.query.all()
        ]
        cache.set('departments_with_doctors', departments, timeout=600)

    # Upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date, Appointment.time).all()

    return jsonify({
        "departments": departments,
        "upcoming_appointments": [
            {
                "id": a.id,
                "doctor": {
                    "id": a.doctor.id,
                    "full_name": a.doctor.full_name,
                    "specialization": a.doctor.specialization
                },
                "date": a.date.strftime("%Y-%m-%d"),
                "time": a.time.strftime("%H:%M"),
                "status": a.status,
                "reason": a.reason
            } for a in upcoming_appointments
        ]
    })


@patient_api.route('/patient/doctor', methods=['GET'])
@jwt_required()
@role_required('patient')
def patient_doctors():
    search_query = request.args.get('search', '')
    specialization = request.args.get('specialization', '')

    query = User.query.filter_by(role='doctor', is_active=True)
    if search_query:
        query = query.filter(User.full_name.contains(search_query))
    if specialization:
        query = query.filter_by(specialization=specialization)

    doctors = query.all()
    return jsonify([
        {
            "id": doctor.id,
            "full_name": doctor.full_name,
            "email": doctor.email,
            "specialization": doctor.specialization,
            "contact": doctor.contact,
            "department": {
                "id": doctor.department.id,
                "name": doctor.department.name
            } if doctor.department else None
        } for doctor in doctors
    ])


@patient_api.route('/patient/book/<int:slot_id>', methods=['POST'])
@jwt_required()
@role_required('patient')
def patient_book(slot_id):
    patient_id = int(get_jwt_identity())

    # Get slot
    slot = TimeSlot.query.get_or_404(slot_id)
    data = request.json
    reason = data.get("reason")
    
    if not slot.available:
        return jsonify({"error": "Slot not available"}), 400

    # Prevent booking past slots
    from datetime import datetime
    if datetime.combine(slot.date, slot.time) < datetime.now():
        return jsonify({"error": "Cannot book past slot"}), 400

    # Create appointment
    appointment = Appointment(
        doctor_id=slot.doctor_id,
        patient_id=patient_id,
        date=slot.date,
        time=slot.time,
        reason=reason,
        status="Booked"
    )
    slot.available = False

    db.session.add(appointment)
    db.session.commit()

    cache.delete(f"doctor_slots_{slot.doctor_id}")
    cache.delete(f"patient_history_{patient_id}")
    cache.delete(f"doctor_timeslots_{doctor_id}")

    return jsonify({
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id
    }), 200


@patient_api.route('/patient/doctor/<int:doctor_id>/slots', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_doctor_slots(doctor_id):
    today = date.today()
    max_date = today + timedelta(days=7)

    cache_key = f"doctor_slots_{doctor_id}"
    slots = cache.get(cache_key)

    # Cache
    if slots is None:
        result = TimeSlot.query.filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.available == True,
            TimeSlot.date >= today,
            TimeSlot.date <= max_date
        ).order_by(TimeSlot.date, TimeSlot.time).all()

        slots = [
            {
                "id": s.id,
                "date": s.date.strftime("%Y-%m-%d"),
                "time": s.time.strftime("%H:%M")
            }
            for s in result
        ]

        cache.set(cache_key, slots, timeout=120)

    return jsonify(slots), 200


@patient_api.route('/patient/appointments', methods=['GET'])
@jwt_required()
@role_required('patient')
def patient_appointments():
    patient_id = int(get_jwt_identity())
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date.desc(), Appointment.time.desc()
    ).all()

    return jsonify([
        {
            "id": a.id,
            "doctor": {
                "id": a.doctor.id,
                "full_name": a.doctor.full_name,
                "specialization": a.doctor.specialization
            },
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M"),
            "status": a.status,
            "reason": a.reason
        } for a in appointments
    ])


@patient_api.route('/patient/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@role_required('patient')
def patient_cancel_appointment(appointment_id):
    patient_id = int(get_jwt_identity())
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient_id:
        return jsonify({"error": "Access denied"}), 403
    if appointment.status != 'Booked':
        return jsonify({"error": "Only booked appointments can be cancelled"}), 400

    appointment.status = 'Cancelled'
    appointment_slot_date = appointment.date
    doctor_id = appointment.doctor_id
    db.session.commit()

    # Delete caches
    cache.delete(f"doctor_slots_{appointment.doctor_id}")
    cache.delete(f"doctor_timeslots_{appointment.doctor_id}")
    cache.delete(f"patient_history_{patient_id}")

    return jsonify({"message": "Appointment cancelled"})

@patient_api.route('/patient/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
@jwt_required()
@role_required('patient')
def reschedule_appointment(appointment_id):
    patient_id = int(get_jwt_identity())
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient_id:
        return jsonify({"error": "Access denied"}), 403
    if appointment.status != 'Booked':
        return jsonify({"error": "Only booked appointments can be rescheduled"}), 400

    data = request.get_json()
    new_slot_id = data.get('slot_id')
    new_slot = TimeSlot.query.get_or_404(new_slot_id)

    if not new_slot.available:
        return jsonify({"error": "Slot not available"}), 400

    # Free old slot
    old_slot = TimeSlot.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time=appointment.time
    ).first()
    if old_slot:
        old_slot.available = True

    # New slot
    appointment.date = new_slot.date
    appointment.time = new_slot.time
    new_slot.available = False
    db.session.commit()

    cache.delete(f"doctor_timeslots_{appointment.doctor_id}")
    cache.delete(f"doctor_slots_{appointment.doctor_id}")

    return jsonify({"message": "Appointment rescheduled successfully"})


@patient_api.route('/patient/history', methods=['GET'])
@jwt_required()
@role_required('patient')
def patient_history():
    patient_id = int(get_jwt_identity())
    cache_key = f"patient_history_{patient_id}"

    history = cache.get(cache_key)

    if history is None:
        completed_appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            status='Completed'
        ).order_by(
            Appointment.date.desc(),
            Appointment.time.desc()
        ).all()

        history = []

        for a in completed_appointments:
            history.append({
                "id": a.id,
                "date": a.date.strftime("%Y-%m-%d"),
                "time": a.time.strftime("%H:%M"),
                "reason": a.reason,

                "doctor": {
                    "id": a.doctor.id,
                    "full_name": a.doctor.full_name,
                    "specialization": a.doctor.specialization
                } if a.doctor else None,

                "treatment": {
                    "id": a.treatment.id,
                    "diagnosis": a.treatment.diagnosis,
                    "prescription": a.treatment.prescription,
                    "notes": a.treatment.notes,
                    "created_at": a.treatment.created_at.strftime("%Y-%m-%d %H:%M")
                } if a.treatment else None
            })

        cache.set(cache_key, history, timeout=600)

    return jsonify(history), 200


@patient_api.route('/patient/profile', methods=['GET', 'PUT'])
@jwt_required()
@role_required('patient')
def patient_profile():
    patient_id = int(get_jwt_identity())
    user = User.query.get_or_404(patient_id)

    if request.method == 'GET':
        return jsonify({
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "contact": user.contact,
            "age": user.age,
            "gender": user.gender,
            "address": user.address,
            "is_active": user.is_active,
            "created_at": user.created_at.strftime("%d-%m-%Y")
        })

    data = request.get_json()
    existing_user = User.query.filter(User.email == data.get('email'), User.id != user.id).first()
    if existing_user:
        return jsonify({"error": "Email already in use"}), 400

    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.contact = data.get('contact')
    user.age = data.get('age')
    user.gender = data.get('gender')
    user.address = data.get('address')

    if data.get('password'):
        user.set_password(data.get('password'))

    db.session.commit()
    cache.delete(f"patient_history_{patient_id}")  # invalidate cache after profile update
    return jsonify({"message": "Profile updated successfully"})


@patient_api.route("/patient/history/export_csv", methods=["POST"])
@jwt_required()
@role_required("patient")
def export_csv():
    from flask import Response
    from sqlalchemy.orm import joinedload
    import io, csv

    try:
        patient_id = int(get_jwt_identity())
        patient = db.session.get(User, patient_id)
        if not patient or patient.role != "patient":
            return jsonify({"message": "Patient not found"}), 404

        appointments = Appointment.query.options(
            joinedload(Appointment.doctor),
            joinedload(Appointment.treatment)
        ).filter_by(
            patient_id=patient_id,
            status="Completed"
        ).order_by(Appointment.date.desc()).all()

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

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=treatment_history_{patient.id}.csv"}
        )

    except Exception as err:
        return jsonify({"err": str(err)}), 500
