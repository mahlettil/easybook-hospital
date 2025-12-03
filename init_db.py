"""
Database initialization script with sample data
Run this file to create the database and populate it with initial data
"""
from datetime import datetime, time, date, timedelta
from app import create_app
from app.database import db
from app.models import User, Patient, Specialty, Doctor, Schedule, Appointment

def init_database():
    """Initialize database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        try:
            db.drop_all()
            print("Dropped existing tables (if any)")
        except Exception as e:
            print(f"Note: {e}")
        
        db.create_all()
        print("Tables created successfully!")
        
        # Create admin user
        print("Creating admin user...")
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create patient user
        print("Creating sample patient user...")
        patient_user = User(username='patient', role='patient')
        patient_user.set_password('patient123')
        db.session.add(patient_user)
        
        db.session.commit()
        
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
        print("Creating medical specialties...")
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
        
        db.session.commit()
        
        # Create doctors
        print("Creating doctors...")
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
        
        db.session.commit()
        
        # Create schedules for doctors
        print("Creating doctor schedules...")
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for doctor in doctors:
            for day in days:
                # Morning schedule
                morning_schedule = Schedule(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(12, 0),
                    slot_duration=30
                )
                db.session.add(morning_schedule)
                
                # Afternoon schedule
                afternoon_schedule = Schedule(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(14, 0),
                    end_time=time(17, 0),
                    slot_duration=30
                )
                db.session.add(afternoon_schedule)
        
        db.session.commit()
        
        # Create a sample appointment
        print("Creating sample appointment...")
        tomorrow = date.today() + timedelta(days=1)
        appointment = Appointment(
            reference_number=Appointment.generate_reference_number(),
            patient_id=patient.id,
            doctor_id=doctors[0].id,
            appointment_date=tomorrow,
            appointment_time=time(10, 0),
            status='scheduled',
            notes='Regular checkup'
        )
        db.session.add(appointment)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nDefault Login Credentials:")
        print("-" * 30)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nPatient:")
        print("  Username: patient")
        print("  Password: patient123")
        print("="*50)

if __name__ == '__main__':
    init_database()