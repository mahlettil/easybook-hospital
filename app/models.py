"""
Database models for the Easybook Hospital Appointment System
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db

class User(UserMixin, db.Model):
    """User model for authentication (FR 1)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # 'patient' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Patient(db.Model):
    """Patient profile model (FR 1.1, FR 6)"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'


class Specialty(db.Model):
    """Medical specialty model (FR 4)"""
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    department_location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctors = db.relationship('Doctor', backref='specialty', lazy=True)
    
    def __repr__(self):
        return f'<Specialty {self.name}>'


class Doctor(db.Model):
    """Doctor model (FR 2.1, FR 5.2)"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('Schedule', backref='doctor', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.name}>'


class Schedule(db.Model):
    """Doctor schedule model (FR 2.2, FR 5.2)"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slot_duration = db.Column(db.Integer, default=30)  # minutes per appointment
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule Doctor:{self.doctor_id} {self.day_of_week}>'


class Appointment(db.Model):
    """Appointment model (FR 3)"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.reference_number}>'
    
    @staticmethod
    def generate_reference_number():
        """Generate unique reference number"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f'APT{timestamp}{random_str}'