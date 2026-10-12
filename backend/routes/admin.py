from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.models import db, User, Department, Appointment
from routes.util import role_required

admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/admin/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_dashboard():
    total_doctors = User.query.filter_by(role='doctor', is_active=True).count()
    total_patients = User.query.filter_by(role='patient', is_active=True).count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='Booked').count()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()

    return jsonify({
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "recent_appointments": [a.to_dict() for a in recent_appointments]
    }), 200

@admin_api.route('/admin/doctor', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_doctors():
    search_query = request.args.get('search', '')
    if search_query:
        doctors = User.query.filter(
            User.role == 'doctor',
            (User.full_name.contains(search_query) | User.specialization.contains(search_query))
        ).all()
    else:
        doctors = User.query.filter_by(role='doctor').all()

    departments = Department.query.all()
    return jsonify({
        "doctors": [d.to_dict() for d in doctors],
        "departments": [dept.to_dict() for dept in departments],
        "search_query": search_query
    }), 200

@admin_api.route('/admin/doctor/add', methods=['POST'])
@jwt_required()
@role_required('admin')
def admin_add_doctor():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    contact = data.get('contact')
    specialization = data.get('specialization')
    department_id = data.get('department_id')

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    doctor = User(
        username=username,
        email=email,
        full_name=full_name,
        role='doctor',
        contact=contact,
        specialization=specialization,
        department_id=int(department_id) if department_id else None
    )
    doctor.set_password(password)

    db.session.add(doctor)
    db.session.commit()

    return jsonify({"msg": f"Doctor {full_name} added successfully!"}), 201

@admin_api.route('/admin/doctor/edit/<int:doctor_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def admin_edit_doctor(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    if doctor.role != 'doctor':
        return jsonify({"msg": "Invalid doctor ID"}), 400

    data = request.get_json()
    doctor.full_name = data.get('full_name', doctor.full_name)
    doctor.email = data.get('email', doctor.email)
    doctor.contact = data.get('contact', doctor.contact)
    doctor.specialization = data.get('specialization', doctor.specialization)
    department_id = data.get('department_id')
    doctor.department_id = int(department_id) if department_id else doctor.department_id

    password = data.get('password')
    if password:
        doctor.set_password(password)

    db.session.commit()
    return jsonify({"msg": f"Doctor {doctor.full_name} updated successfully!"}), 200

@admin_api.route('/admin/doctor/delete/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def admin_delete_doctor(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    if doctor.role != 'doctor':
        return jsonify({"msg": "Invalid doctor ID"}), 400

    doctor.is_active = False
    db.session.commit()
    return jsonify({"msg": f"Doctor {doctor.full_name} has been deactivated!"}), 200

@admin_api.route('/admin/patient', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_patients():
    search_query = request.args.get('search', '')
    if search_query:
        patients = User.query.filter(
            User.role == 'patient',
            (User.full_name.contains(search_query) |
             User.contact.contains(search_query) |
             User.email.contains(search_query))
        ).all()
    else:
        patients = User.query.filter_by(role='patient').all()

    return jsonify({
        "patients": [p.to_dict() for p in patients],
        "search_query": search_query
    }), 200

@admin_api.route('/admin/patient/edit/<int:patient_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def admin_edit_patient(patient_id):
    patient = User.query.get_or_404(patient_id)
    if patient.role != 'patient':
        return jsonify({"msg": "Invalid patient ID"}), 400

    data = request.get_json()
    patient.full_name = data.get('full_name', patient.full_name)
    patient.email = data.get('email', patient.email)
    patient.contact = data.get('contact', patient.contact)
    patient.age = int(data.get('age')) if data.get('age') else patient.age
    patient.gender = data.get('gender', patient.gender)
    patient.address = data.get('address', patient.address)

    db.session.commit()
    return jsonify({"msg": f"Patient {patient.full_name} updated successfully!"}), 200

@admin_api.route('/admin/patient/delete/<int:patient_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def admin_delete_patient(patient_id):
    patient = User.query.get_or_404(patient_id)
    if patient.role != 'patient':
        return jsonify({"msg": "Invalid patient ID"}), 400

    patient.is_active = False
    db.session.commit()
    return jsonify({"msg": f"Patient {patient.full_name} has been deactivated!"}), 200

@admin_api.route('/admin/appointments', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify({
        "appointments": [a.to_dict() for a in appointments]
    }), 200

@admin_api.route('/admin/departments', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_departments():
    departments = Department.query.all()
    return jsonify({
        "departments": [d.to_dict() for d in departments]
    }), 200

@admin_api.route('/admin/department/add', methods=['POST'])
@jwt_required()
@role_required('admin')
def admin_add_department():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if Department.query.filter_by(name=name).first():
        return jsonify({"msg": "Department already exists"}), 400

    department = Department(name=name, description=description)
    db.session.add(department)
    db.session.commit()

    return jsonify({"msg": f"Department {name} added successfully!"}), 201
