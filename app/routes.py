"""
Application routes and views
This file contains all the routes for the Easybook system
"""
from datetime import datetime, date, time, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.database import db
from app.models import User, Patient, Specialty, Doctor, Schedule, Appointment
from app.auth import admin_required, patient_required
from config import Config

main = Blueprint('main', __name__)

# ============= PUBLIC ROUTES =============

@main.route('/')
def index():
    """Landing page (FR 7)"""
    specialties = Specialty.query.all()
    return render_template('index.html', 
                         hospital_name=Config.HOSPITAL_NAME,
                         operating_hours=Config.HOSPITAL_OPERATING_HOURS,
                         services=Config.HOSPITAL_SERVICES,
                         specialties=specialties)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login (FR 1.2)"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.patient_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Welcome back, {username}!', 'success')
            
            # Redirect based on role
            if user.is_admin():
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.patient_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration (FR 1.1)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.patient_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        gender = request.form.get('gender', '')
        dob_str = request.form.get('date_of_birth', '')
        address = request.form.get('address', '').strip()
        
        # Validation
        if not all([username, password, full_name, phone]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(username=username, role='patient')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Parse date of birth
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            email=email if email else None,
            date_of_birth=dob,
            gender=gender if gender else None,
            address=address if address else None
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# ============= PATIENT ROUTES =============

@main.route('/patient/dashboard')
@login_required
@patient_required
def patient_dashboard():
    """Patient dashboard (FR 6)"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        flash('Patient profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    # Get appointment history
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        db.or_(
            Appointment.appointment_date < today,
            Appointment.status.in_(['completed', 'cancelled'])
        )
    ).order_by(Appointment.appointment_date.desc()).limit(10).all()
    
    return render_template('patient_dashboard.html', 
                         patient=patient,
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments)

@main.route('/patient/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def patient_profile():
    """Update patient profile (FR 6.2)"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        patient.full_name = request.form.get('full_name', patient.full_name)
        patient.phone = request.form.get('phone', patient.phone)
        patient.email = request.form.get('email', patient.email)
        patient.address = request.form.get('address', patient.address)
        patient.gender = request.form.get('gender', patient.gender)
        
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            try:
                patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.patient_dashboard'))
    
    return render_template('patient_profile.html', patient=patient)

@main.route('/book-appointment', methods=['GET', 'POST'])
@login_required
@patient_required
def book_appointment():
    """Book new appointment (FR 2, FR 3.1)"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        notes = request.form.get('notes', '')
        
        # Validation
        if not all([doctor_id, appointment_date_str, appointment_time_str]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('main.book_appointment'))
        
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'error')
            return redirect(url_for('main.book_appointment'))
        
        # Check if date is in the past
        if appointment_date < date.today():
            flash('Cannot book appointments in the past.', 'error')
            return redirect(url_for('main.book_appointment'))
        
        # Check for double booking (FR 3.3)
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='scheduled'
        ).first()
        
        if existing:
            flash('This time slot is already booked. Please choose another.', 'error')
            return redirect(url_for('main.book_appointment'))
        
        # Create appointment
        appointment = Appointment(
            reference_number=Appointment.generate_reference_number(),
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            status='scheduled'
        )
        db.session.add(appointment)
        db.session.commit()
        
        flash(f'Appointment booked successfully! Reference: {appointment.reference_number}', 'success')
        return redirect(url_for('main.patient_dashboard'))
    
    # GET request - show booking form
    specialties = Specialty.query.all()
    return render_template('book_appointment.html', specialties=specialties)

@main.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
@patient_required
def cancel_appointment(appointment_id):
    """Cancel appointment (FR 3.2)"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify ownership
    if appointment.patient_id != patient.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.patient_dashboard'))
    
    # Only cancel scheduled appointments
    if appointment.status != 'scheduled':
        flash('This appointment cannot be cancelled.', 'error')
        return redirect(url_for('main.patient_dashboard'))
    
    appointment.status = 'cancelled'
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Appointment cancelled successfully.', 'info')
    return redirect(url_for('main.patient_dashboard'))

# ============= API ROUTES =============

@main.route('/api/doctors/<int:specialty_id>')
def get_doctors_by_specialty(specialty_id):
    """Get doctors by specialty (FR 2.1)"""
    doctors = Doctor.query.filter_by(specialty_id=specialty_id, is_active=True).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'qualification': d.qualification,
        'experience_years': d.experience_years
    } for d in doctors])

@main.route('/api/doctor-availability/<int:doctor_id>')
def get_doctor_availability(doctor_id):
    """Get doctor's available slots (FR 2.2)"""
    doctor = Doctor.query.get_or_404(doctor_id)
    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_active=True).all()
    
    # Group by day
    availability = {}
    for schedule in schedules:
        day = schedule.day_of_week
        if day not in availability:
            availability[day] = []
        
        availability[day].append({
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'slot_duration': schedule.slot_duration
        })
    
    return jsonify(availability)

@main.route('/api/available-slots/<int:doctor_id>/<date_str>')
def get_available_slots(doctor_id, date_str):
    """Get available time slots for a specific date"""
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get day of week
    day_name = appointment_date.strftime('%A')
    
    # Get doctor's schedule for this day
    schedules = Schedule.query.filter_by(
        doctor_id=doctor_id,
        day_of_week=day_name,
        is_active=True
    ).all()
    
    if not schedules:
        return jsonify([])
    
    # Get booked appointments for this date
    booked = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        status='scheduled'
    ).all()
    booked_times = [a.appointment_time for a in booked]
    
    # Generate available slots
    available_slots = []
    for schedule in schedules:
        current_time = datetime.combine(date.today(), schedule.start_time)
        end_time = datetime.combine(date.today(), schedule.end_time)
        
        while current_time < end_time:
            slot_time = current_time.time()
            if slot_time not in booked_times:
                available_slots.append(slot_time.strftime('%H:%M'))
            current_time += timedelta(minutes=schedule.slot_duration)
    
    return jsonify(available_slots)

# ============= ADMIN ROUTES =============

@main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard (FR 5.1)"""
    # Statistics
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()
    
    today = date.today()
    today_appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='scheduled'
    ).count()
    
    # Recent appointments
    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_appointments=total_appointments,
                         today_appointments=today_appointments,
                         recent_appointments=recent_appointments)

@main.route('/admin/doctors', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_doctors():
    """Manage doctors (FR 5.2)"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            doctor = Doctor(
                name=request.form.get('name'),
                specialty_id=request.form.get('specialty_id'),
                qualification=request.form.get('qualification'),
                experience_years=request.form.get('experience_years'),
                phone=request.form.get('phone'),
                email=request.form.get('email')
            )
            db.session.add(doctor)
            db.session.commit()
            flash('Doctor added successfully!', 'success')
        
        elif action == 'edit':
            doctor_id = request.form.get('doctor_id')
            doctor = Doctor.query.get(doctor_id)
            if doctor:
                doctor.name = request.form.get('name')
                doctor.specialty_id = request.form.get('specialty_id')
                doctor.qualification = request.form.get('qualification')
                doctor.experience_years = request.form.get('experience_years')
                doctor.phone = request.form.get('phone')
                doctor.email = request.form.get('email')
                db.session.commit()
                flash('Doctor updated successfully!', 'success')
        
        elif action == 'delete':
            doctor_id = request.form.get('doctor_id')
            doctor = Doctor.query.get(doctor_id)
            if doctor:
                doctor.is_active = False
                db.session.commit()
                flash('Doctor deactivated successfully!', 'success')
        
        return redirect(url_for('main.admin_doctors'))
    
    doctors = Doctor.query.all()
    specialties = Specialty.query.all()
    return render_template('admin_doctors.html', doctors=doctors, specialties=specialties)

@main.route('/admin/schedules', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_schedules():
    """Manage doctor schedules (FR 5.2)"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            schedule = Schedule(
                doctor_id=request.form.get('doctor_id'),
                day_of_week=request.form.get('day_of_week'),
                start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
                end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
                slot_duration=int(request.form.get('slot_duration', 30))
            )
            db.session.add(schedule)
            db.session.commit()
            flash('Schedule added successfully!', 'success')
        
        return redirect(url_for('main.admin_schedules'))
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    schedules = Schedule.query.filter_by(is_active=True).all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render_template('admin_schedules.html', doctors=doctors, schedules=schedules, days=days)

@main.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments():
    """View all appointments"""
    appointments = Appointment.query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()
    
    return render_template('admin_appointments.html', appointments=appointments)

@main.route('/admin/specialties', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_specialties():
    """Manage specialties (FR 4)"""
    if request.method == 'POST':
        specialty = Specialty(
            name=request.form.get('name'),
            description=request.form.get('description'),
            department_location=request.form.get('department_location')
        )
        db.session.add(specialty)
        db.session.commit()
        flash('Specialty added successfully!', 'success')
        return redirect(url_for('main.admin_specialties'))
    
    specialties = Specialty.query.all()
    return render_template('admin_specialties.html', specialties=specialties)