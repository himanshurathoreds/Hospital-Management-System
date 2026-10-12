from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Appointment, Treatment, TimeSlot
from datetime import datetime, date, timedelta
from routes.tasks import cache

doctor_api = Blueprint('doctor_api', __name__)


# Dashboard
@doctor_api.route('/doctor/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    doctor_id = int(get_jwt_identity())
    cache_key = f"doctor_dashboard_{doctor_id}"
    dashboard = cache.get(cache_key)

    if dashboard is None:
        today = date.today()
        week_later = today + timedelta(days=7)

        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date >= today,
            Appointment.date <= week_later,
            Appointment.status == 'Booked'
        ).order_by(Appointment.date, Appointment.time).all()

        myPatients = User.query.join(Appointment, Appointment.patient_id == User.id).filter(
            Appointment.doctor_id == doctor_id,
            User.role == 'patient'
        ).distinct().all()

        dashboard = {
            "upcoming_appointments": [
                {
                    "id": apt.id,
                    "patient": {
                        "id": apt.patient.id,
                        "full_name": apt.patient.full_name,
                        "contact": apt.patient.contact
                    },
                    "date": str(apt.date),
                    "time": apt.time.strftime("%H:%M"),
                    "reason": apt.reason,
                    "status": apt.status
                } for apt in upcoming_appointments
            ],
            "myPatients": [
                {"id": p.id, "full_name": p.full_name, "contact": p.contact}
                for p in myPatients
            ]
        }
        cache.set(cache_key, dashboard, timeout=120)

    return jsonify(dashboard)

@doctor_api.route('/doctor/patients', methods=['GET'])
@jwt_required()
def doctor_patients():
    doctor_id = int(get_jwt_identity())
    patients = User.query.join(Appointment, Appointment.patient_id == User.id).filter(
        Appointment.doctor_id == doctor_id,
        User.role == 'patient'
    ).distinct().all()
    return jsonify([{"id": p.id, "full_name": p.full_name, "contact": p.contact} for p in patients])

@doctor_api.route('/doctor/patient/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def doctor_patient_history(patient_id):
    doctor_id = int(get_jwt_identity())
    cache_key = f"doctor_patient_history_{doctor_id}_{patient_id}"
    history = cache.get(cache_key)

    if history is None:
        patient = User.query.get_or_404(patient_id)
        if patient.role != 'patient':
            return jsonify({"error": "Invalid patient"}), 400

        appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            doctor_id=doctor_id,
            status='Completed'
        ).order_by(Appointment.date.desc()).all()

        history = {
            "patient": {
                "id": patient.id,
                "full_name": patient.full_name,
                "email": patient.email,
                "contact": patient.contact,
                "age": patient.age,
                "gender": patient.gender,
                "address": patient.address
            },
            "appointments": [
                {
                    "id": apt.id,
                    "date": apt.date.isoformat(),
                    "time": apt.time.strftime("%H:%M") if apt.time else None,
                    "reason": apt.reason or "Not provided",
                    "treatment": {
                        "diagnosis": apt.treatment.diagnosis if apt.treatment else None,
                        "prescription": apt.treatment.prescription if apt.treatment else None,
                        "notes": apt.treatment.notes if apt.treatment else None,
                        "created_at": apt.treatment.created_at.isoformat() if apt.treatment else None
                    } if apt.treatment else None
                } for apt in appointments
            ]
        }
        cache.set(cache_key, history, timeout=600)

    return jsonify(history)

# Appointments
@doctor_api.route('/doctor/appointments', methods=['GET'])
@jwt_required()
def doctor_appointments():
    doctor_id = int(get_jwt_identity())
    status_filter = request.args.get('status', 'all')

    query = Appointment.query.filter_by(doctor_id=doctor_id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify({
    "appointments": [apt.to_dict() for apt in appointments]
    }), 200


@doctor_api.route('/doctor/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def doctor_get_appointment(appointment_id):
    doctor_id = int(get_jwt_identity())
    apt = Appointment.query.get_or_404(appointment_id)
    if apt.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403
    return jsonify({
        "appointment": apt.to_dict()
    }), 200


@doctor_api.route('/doctor/appointments/<int:appointment_id>/complete', methods=['POST'])
@jwt_required()
def doctor_complete_appointment(appointment_id):
    doctor_id = int(get_jwt_identity())
    apt = Appointment.query.get_or_404(appointment_id)
    if apt.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403

    data = request.json
    apt.status = 'Completed'
    treatment = Treatment(
        appointment_id=apt.id,
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        notes=data.get('notes')
    )
    db.session.add(treatment)
    db.session.commit()

    cache.delete(f"doctor_patient_history_{doctor_id}_{patient_id}")
    cache.delete(f"patient_history_{patient_id}")
    
    return jsonify({"message": "Appointment completed and treatment recorded"})

@doctor_api.route('/doctor/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def doctor_cancel_appointment(appointment_id):
    doctor_id = int(get_jwt_identity())
    apt = Appointment.query.get_or_404(appointment_id)
    if apt.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403

    apt.status = 'Cancelled'
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})

# Treatments
@doctor_api.route('/doctor/treatment/<int:appointment_id>', methods=['GET'])
@jwt_required()
def doctor_get_treatment(appointment_id):
    doctor_id = int(get_jwt_identity())
    apt = Appointment.query.get_or_404(appointment_id)
    if apt.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403
    if not apt.treatment:
        return jsonify({"error": "No treatment recorded"}), 404
    t = apt.treatment
    return jsonify({"diagnosis": t.diagnosis, "prescription": t.prescription, "notes": t.notes})

@doctor_api.route('/doctor/treatment/<int:treatment_id>', methods=['PUT'])
@jwt_required()
def doctor_update_treatment(treatment_id):
    doctor_id = int(get_jwt_identity())
    t = Treatment.query.get_or_404(treatment_id)
    if t.appointment.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403
    data = request.json
    t.diagnosis = data.get('diagnosis', t.diagnosis)
    t.prescription = data.get('prescription', t.prescription)
    t.notes = data.get('notes', t.notes)
    db.session.commit()
    return jsonify({"message": "Treatment updated"})

@doctor_api.route('/doctor/treatment/<int:treatment_id>', methods=['DELETE'])
@jwt_required()
def doctor_delete_treatment(treatment_id):
    doctor_id = int(get_jwt_identity())
    t = Treatment.query.get_or_404(treatment_id)
    if t.appointment.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Treatment deleted"})

# Time Slots
@doctor_api.route('/doctor/timeslots', methods=['POST'])
@jwt_required()
def doctor_add_timeslot():
    doctor_id = int(get_jwt_identity())
    data = request.json
    slot_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
    slot_time = datetime.strptime(data['time'], "%H:%M").time()
    slot_datetime = datetime.combine(slot_date, slot_time)

    if slot_datetime < datetime.now():
        return jsonify({"message": "Cannot add a slot in the past"}), 400

    timeslot = TimeSlot(
        doctor_id=doctor_id,
        date=slot_date,
        time=slot_time,
        available=True
    )
    db.session.add(timeslot)
    db.session.commit()

    # Clear timeslot cache
    cache.delete(f"doctor_timeslots_{doctor_id}")
    cache.delete(f"doctor_slots_{doctor_id}")

    return jsonify({"message": "Time slot added"}), 201

@doctor_api.route('/doctor/timeslots', methods=['GET'])
@jwt_required()
def doctor_get_timeslots():
    doctor_id = int(get_jwt_identity())
    cache_key = f"doctor_timeslots_{doctor_id}"
    slots = cache.get(cache_key)

    if slots is None:
        slots = TimeSlot.query.filter_by(doctor_id=doctor_id).all()
        slots = [{"id": s.id, "date": str(s.date), "time": s.time.strftime("%H:%M"), "available": s.available} for s in slots]
        cache.set(cache_key, slots, timeout=120)  # 2 min

    return jsonify(slots)


@doctor_api.route('/doctor/timeslots/<int:slot_id>', methods=['DELETE'])
@jwt_required()
def doctor_delete_timeslot(slot_id):
    doctor_id = int(get_jwt_identity())
    slot = TimeSlot.query.get_or_404(slot_id)
    if slot.doctor_id != doctor_id:
        return jsonify({"error": "Access denied"}), 403

    db.session.delete(slot)
    db.session.commit()

    # Clear timeslot cache
    cache.delete(f"doctor_timeslots_{doctor_id}")

    return jsonify({"message": "Time slot deleted"}), 201
