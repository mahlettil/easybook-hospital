# Easybook - Hospital Appointment Management System

A Flask-based web application for managing hospital appointments, doctors, schedules, and patient profiles. Patients can book appointments online, and administrators can manage the system.

## Features

- **Patient Registration & Login** — secure account creation and authentication
- **Book Appointments** — select doctor, date, time with real-time availability
- **Patient Dashboard** — view upcoming and past appointments
- **Patient Profile** — update personal information (name, phone, email, gender, DOB, address)
- **Admin Dashboard** — manage doctors, specialties, schedules, and appointments
- **Doctor Management** — add/edit/remove doctors with qualifications and experience
- **Specialty Management** — create medical specialties (Cardiology, Pediatrics, etc.)
- **Schedule Management** — define doctor working hours and appointment slots
- **Double-Booking Prevention** — automatic conflict detection
- **Secure Sessions** — Flask-Login with password hashing

## Tech Stack

- **Backend:** Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3
- **Database:** PostgreSQL (production) / SQLite (local dev)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Authentication:** Flask-Login with bcrypt-style password hashing
- **Server:** Gunicorn (production) / Flask dev server (local)
- **Deployment:** Vercel (serverless Python)

## Project Structure

```
easybook/
├── app/
│   ├── __init__.py          # Flask app factory, extensions initialization
│   ├── auth.py              # Authentication decorators (@admin_required, @patient_required)
│   ├── database.py          # SQLAlchemy database instance
│   ├── models.py            # Database models (User, Patient, Doctor, Appointment, etc.)
│   ├── routes.py            # All application routes (login, book, admin, API)
│   └── __pycache__/
├── templates/               # Jinja2 HTML templates
│   ├── base.html            # Base layout (navbar, footer)
│   ├── index.html           # Landing page
│   ├── login.html           # Login form
│   ├── register.html        # Patient registration
│   ├── patient_dashboard.html
│   ├── patient_profile.html
│   ├── book_appointment.html
│   ├── admin_dashboard.html
│   ├── admin_doctors.html
│   ├── admin_schedules.html
│   ├── admin_specialties.html
│   └── admin_appointments.html
├── static/
│   ├── css/
│   │   └── style.css        # Global styles
│   └── js/
│       └── main.js          # Client-side logic
├── config.py                # Configuration (database, session, security)
├── run.py                   # Application entry point
├── init_db.py               # Database initialization & seeding
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel deployment config
├── .env                     # Environment variables (local, .gitignored)
├── .env.example             # Template for required env vars
└── README.md                # This file
```

## Local Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone or download the project:**

   ```bash
   git clone <repo-url>
   cd easybook
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies:**

   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   copy .env.example .env
   # Edit .env and add SECRET_KEY if needed (one is already provided)
   ```

5. **Initialize the database:**

   ```bash
   python init_db.py
   ```

   This creates:

   - Database tables
   - Admin user: `admin` / `admin123`
   - Sample patient: `patient` / `patient123`
   - 5 sample doctors with schedules
   - Sample appointment

6. **Run the development server:**
   ```bash
   python run.py
   ```
   Open: http://localhost:5000

### Default Credentials (Local)

- **Admin:**

  - Username: `admin`
  - Password: `admin123`

- **Patient:**
  - Username: `patient`
  - Password: `patient123`

## Database Models

### User

- `id` (primary key)
- `username` (unique)
- `password_hash` (bcrypt)
- `role` ('admin' or 'patient')
- `created_at`, `updated_at`

### Patient

- `id`, `user_id` (foreign key to User)
- `full_name`, `phone`, `email`
- `gender` ('Male' or 'Female')
- `date_of_birth`, `address`
- `created_at`, `updated_at`

### Specialty

- `id`, `name`, `description`, `department_location`

### Doctor

- `id`, `name`, `specialty_id` (foreign key)
- `qualification`, `experience_years`
- `phone`, `email`, `is_active`
- `created_at`, `updated_at`

### Schedule

- `id`, `doctor_id`, `day_of_week`
- `start_time`, `end_time`, `slot_duration` (minutes)
- `is_active`, `created_at`, `updated_at`

### Appointment

- `id`, `reference_number` (unique)
- `patient_id`, `doctor_id` (foreign keys)
- `appointment_date`, `appointment_time`
- `status` ('scheduled', 'completed', 'cancelled')
- `notes`, `created_at`, `updated_at`

## API Endpoints

### Public Routes

- `GET /` — Landing page
- `GET/POST /login` — User login
- `GET/POST /register` — Patient registration
- `GET /logout` — Logout (requires login)

### Patient Routes (require `@login_required` and `@patient_required`)

- `GET /patient/dashboard` — View appointments
- `GET/POST /patient/profile` — Update profile
- `GET/POST /book-appointment` — Book new appointment
- `POST /cancel-appointment/<id>` — Cancel appointment

### Admin Routes (require `@login_required` and `@admin_required`)

- `GET /admin/dashboard` — Admin home
- `GET/POST /admin/doctors` — Manage doctors
- `GET/POST /admin/schedules` — Manage schedules
- `GET/POST /admin/specialties` — Manage specialties
- `GET/POST /admin/appointments` — Manage appointments

### API Routes

- `GET /api/doctors/<specialty_id>` — Get doctors by specialty (JSON)
- `GET /api/doctor-availability/<doctor_id>` — Get available time slots (JSON)

## Common Tasks

### Add a new specialty

1. Log in as admin
2. Go to Admin Dashboard → Manage Specialties
3. Fill in name, description, location
4. Click "Add Specialty"

### Add a doctor

1. Admin Dashboard → Manage Doctors
2. Fill in name, qualification, years, contact info
3. Select specialty
4. Click "Add Doctor"

### Set doctor's schedule

1. Admin Dashboard → Manage Schedules
2. Select doctor, day, start/end times, slot duration (e.g., 30 min)
3. Click "Add Schedule"

### Book an appointment (as patient)

1. Log in as patient
2. Patient Dashboard → Book Appointment
3. Select specialty → doctor → date → time
4. Click "Book"

### Reset database (local dev)

```bash
del easybook.db
python init_db.py
```

## Performance & Scaling

- **Current:** SQLite (local) or PostgreSQL (production)
- **Caching:** None (consider Redis for high traffic)
- **Load balancing:** Vercel handles auto-scaling
- **Database:** PostgreSQL recommended for production (supports concurrent connections)

## Future Enhancements

- Email notifications (appointment confirmations, reminders)
- SMS notifications
- Payment integration
- Appointment rescheduling
- Doctor reviews/ratings
- Mobile app (React Native)
- Advanced analytics & reporting
