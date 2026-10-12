from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # Common
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Doctor
    specialization = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    availability_start = db.Column(db.Time)
    availability_end = db.Column(db.Time)

    # Patient
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    
    # Relationships
    appointments_as_patient = db.relationship('Appointment', backref='patient', lazy=True, foreign_keys='Appointment.patient_id')
    appointments_as_doctor = db.relationship('Appointment', backref='doctor', lazy=True, foreign_keys='Appointment.doctor_id')
    timeslots = db.relationship('TimeSlot', backref='doctor', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "contact": self.contact,
            "specialization": self.specialization,
            "department_id": self.department_id,
            "department": self.department.to_dict() if self.department else None,
            "is_active": self.is_active,
            "age": self.age,
            "gender": self.gender,
            "address": self.address
        }

# Department
class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    doctors = db.relationship('User', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "doctors": [
                {
                "id": doctor.id,
                "full_name": doctor.full_name,
                "specialization": doctor.specialization
                }
            for doctor in self.doctors
            if doctor.role == "doctor"
        ]
        }

# Appointment
class Appointment(db.Model):
    __tablename__ = 'appointments'
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', 'time', name='unique_doctor_slot'),)
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False, index=True)
    status = db.Column(db.String(20), default='Booked')
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient": {
                "id": self.patient.id,
                "full_name": self.patient.full_name,
                "contact": self.patient.contact
            } if self.patient else None,
            "doctor": {
                "id": self.doctor.id,
                "full_name": self.doctor.full_name,
                "department": self.doctor.department.to_dict() if self.doctor and self.doctor.department else None
            } if self.doctor else None,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "time": self.time.strftime("%H:%M") if self.time else None,
            "status": self.status,
            "reason": self.reason or ""
        }

# Treatment
class Treatment(db.Model):
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Treatment for Appointment {self.appointment_id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "diagnosis": self.diagnosis,
            "prescription": self.prescription,
            "notes": self.notes
        }

# TimeSlot
class TimeSlot(db.Model):
    __tablename__ = 'timeslots'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    available = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TimeSlot {self.date} {self.time} - Doctor {self.doctor_id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.full_name if self.doctor else None,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "time": self.time.strftime("%H:%M") if self.time else None,
            "available": self.available
        }