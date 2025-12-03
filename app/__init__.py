"""
Flask application factory
"""
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from config import Config
from app.database import db

# Load environment variables from .env file
load_dotenv()

login_manager = LoginManager()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables automatically when app starts
    # This ensures tables exist even on first deployment
    with app.app_context():
        try:
            db.create_all()
            print("Database tables verified/created")
        
        # Check if we need to initialize sample data
            from app.models import User
            if User.query.count() == 0:
                print("Database is empty - initializing sample data...")
                init_sample_data()
        except Exception as e:
            import sys
            print(f"WARNING: could not create DB tables: {e}", file=sys.stderr)
    
    return app

def init_sample_data():
    """Initialize sample data if database is empty"""
    from datetime import datetime, time, date, timedelta
    from app.models import User, Patient, Specialty, Doctor, Schedule, Appointment
    from app.database import db
    
    try:
        # Create admin user
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create patient user
        patient_user = User(username='patient', role='patient')
        patient_user.set_password('patient123')
        db.session.add(patient_user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=patient_user.id,
            full_name='John Doe',
            phone='+251911234567',
            email='john.doe@example.com',
            date_of_birth=date(1990, 5, 15),
            gender='Male',
            address='Addis Ababa, Ethiopia'
        )
        db.session.add(patient)
        
        # Create specialties
        specialties_data = [
            {
                'name': 'General Medicine',
                'description': 'Primary care and treatment of common illnesses',
                'department_location': 'Building A, Floor 1'
            },
            {
                'name': 'Cardiology',
                'description': 'Heart and cardiovascular system care',
                'department_location': 'Building B, Floor 2'
            },
            {
                'name': 'Pediatrics',
                'description': 'Medical care for infants, children, and adolescents',
                'department_location': 'Building A, Floor 2'
            },
            {
                'name': 'Orthopedics',
                'description': 'Treatment of bones, joints, and muscles',
                'department_location': 'Building C, Floor 1'
            },
            {
                'name': 'Dermatology',
                'description': 'Skin, hair, and nail conditions',
                'department_location': 'Building B, Floor 3'
            }
        ]
        
        specialties = []
        for spec_data in specialties_data:
            specialty = Specialty(**spec_data)
            db.session.add(specialty)
            specialties.append(specialty)
        
        db.session.flush()
        
        # Create doctors
        doctors_data = [
            {
                'name': 'Dr. Abebe Bekele',
                'specialty_id': specialties[0].id,
                'qualification': 'MD, Internal Medicine',
                'experience_years': 10,
                'phone': '+251911111111',
                'email': 'abebe.bekele@hospital.com'
            },
            {
                'name': 'Dr. Tigist Haile',
                'specialty_id': specialties[1].id,
                'qualification': 'MD, Cardiologist',
                'experience_years': 15,
                'phone': '+251911111112',
                'email': 'tigist.haile@hospital.com'
            },
            {
                'name': 'Dr. Yohannes Tesfaye',
                'specialty_id': specialties[2].id,
                'qualification': 'MD, Pediatrician',
                'experience_years': 8,
                'phone': '+251911111113',
                'email': 'yohannes.tesfaye@hospital.com'
            },
            {
                'name': 'Dr. Meseret Alemayehu',
                'specialty_id': specialties[3].id,
                'qualification': 'MD, Orthopedic Surgeon',
                'experience_years': 12,
                'phone': '+251911111114',
                'email': 'meseret.alemayehu@hospital.com'
            },
            {
                'name': 'Dr. Hana Wolde',
                'specialty_id': specialties[4].id,
                'qualification': 'MD, Dermatologist',
                'experience_years': 7,
                'phone': '+251911111115',
                'email': 'hana.wolde@hospital.com'
            }
        ]
        
        doctors = []
        for doc_data in doctors_data:
            doctor = Doctor(**doc_data)
            db.session.add(doctor)
            doctors.append(doctor)
        
        db.session.flush()
        
        # Create schedules
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for doctor in doctors:
            for day in days:
                morning = Schedule(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(12, 0),
                    slot_duration=30
                )
                afternoon = Schedule(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(14, 0),
                    end_time=time(17, 0),
                    slot_duration=30
                )
                db.session.add(morning)
                db.session.add(afternoon)
        
        db.session.commit()
        print("Sample data initialized successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing sample data: {e}")