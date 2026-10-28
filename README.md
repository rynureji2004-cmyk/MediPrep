# MediPrep - Hospital Pre-Procedure Preparation & Readiness System

MediPrep is an enterprise-grade Clinical Readiness and Procedure Preparation Platform built with **Python Flask** and **MySQL / MariaDB**. It streamlines pre-operative workflows by coordinating clinical preparation tasks between patients, attending surgeons, laboratory staff, and hospital administrators.

---

## Key Features

- **Role-Based Access Control (RBAC):** Dedicated workflows and dashboards for **Admins**, **Attending Surgeons (Doctors)**, **Patients**, and **Diagnostic Laboratories**.
- **Automated Clinical Readiness Engine:** Tracks mandatory pre-op tasks, diagnostic lab investigations, vital thresholds, fasting checklists, and surgical consents in real time.
- **Dynamic Checklist Templates:** Procedure-specific templates (e.g., Cardiac Catheterization, MRI Brain with Contrast, Endoscopy, Laparoscopic Cholecystectomy, Orthopedic Surgeries).
- **Document Management & Lab Integration:** Upload and review diagnostic reports (ECG, renal function, coagulation profiles) with PDF generation powered by ReportLab.
- **Surgical Scheduling & Room Allocation:** Schedule procedures, designate preparation bays and procedure suites, and monitor pre-op clearance status.
- **Patient Self-Service Portal:** View preparation instructions, track checklist milestones, complete pre-assessment questionnaires, and review procedure details.

---

## System Architecture

MediPrep follows the **Model-View-Controller (MVC)** design pattern using Flask Blueprints:

```
flask_auth_mvc/
│── app/
│   ├── models/            # Domain entities (User, Procedure, Checklist)
│   ├── repositories/      # Data access layer (MySQL raw queries with connection pooling)
│   ├── routes/            # Blueprint route controllers (Admin, Doctor, Patient, Lab, Auth)
│   ├── services/          # Business logic, readiness evaluation, report generation
│   ├── static/            # CSS styles, JS client logic, and branding assets
│   ├── templates/         # Jinja2 HTML templates partitioned by role
│   └── utilities/         # Custom decorators (@role_required, @login_required) and validators
│── config.py              # Environment configuration loader
│── database.py            # MySQL Connection Pool and context wrappers
│── run.py                 # Application entry point
│── requirements.txt       # Python dependencies
│── schema.sql             # Full DDL database schema
│── seed_data.sql          # Demo records, procedures, and test accounts
│── seed_rooms.py          # Procedure room allocation seeding script
│── reset_doctor_passwords.py # Credential reset utility for testing
└── uploads/               # Directory for uploaded clinical files (auto-created)
```

---

## Prerequisites

1. **Operating System:** Windows 10/11 (or macOS / Linux)
2. **Python:** Python 3.10 or higher ([python.org](https://www.python.org/))
3. **Database Server:** MySQL 8.0+ or MariaDB 10.4+ (Included with [XAMPP](https://www.apachefriends.org/))

---

## Quick Start on Windows

### 1. Database Setup (Using XAMPP)

1. Open the **XAMPP Control Panel** and start **Apache** and **MySQL**.
2. Open your browser and navigate to `http://localhost/phpmyadmin/`.
3. Create a new database named `hospital_readiness_db` with collation `utf8mb4_unicode_ci`.
4. Import the schema and seed data:
   - Click on `hospital_readiness_db` in the left sidebar.
   - Click the **Import** tab.
   - Choose `schema.sql` and click **Import**.
   - Next, choose `seed_data.sql` and click **Import**.

*Alternatively, import via MySQL Command Line / PowerShell:*
```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS hospital_readiness_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p hospital_readiness_db < schema.sql
mysql -u root -p hospital_readiness_db < seed_data.sql
```

5. (Optional) Run the room allocation seeding script to populate preparation and procedure rooms:
```powershell
python seed_rooms.py
```

---

### 2. Python Environment Configuration

1. Open **Command Prompt** or **PowerShell** in the project root directory:
```powershell
cd C:\path\to\flask_auth_mvc
```

2. Create and activate a Python virtual environment:
```powershell
python -m venv venv
venv\Scripts\activate
```

3. Upgrade pip and install required dependencies:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Environment Variables

1. Copy the example configuration file:
```powershell
copy .env.example .env
```

2. Adjust variables in `.env` if your local MySQL configuration differs from defaults:
```ini
FLASK_ENV=development
SECRET_KEY=change_this_to_a_secure_random_key_in_production
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=
DB_NAME=hospital_readiness_db
DB_POOL_SIZE=10
PORT=5000
```
*(By default, XAMPP uses user `root` with no password, so no changes are necessary for standard XAMPP installs.)*

---

### 4. Running the Application

Start the Flask development server:
```powershell
python run.py
```

The application will launch at:
```
http://127.0.0.1:5000/
```

---

## Demo Accounts

The seed database includes pre-configured demo users for demonstration and testing:

| Role | Username | Default Password | Access / Dashboard |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin_priya` | `Password123!` | User management, doctor profiles, procedure templates |
| **Surgeon / Doctor** | `doctor_robert` | `Password123!` | Surgical schedule, patient readiness scores, clearance |
| **Patient** | `patient_john` | `Password123!` | Personal checklist, pre-op instructions, vital uploads |

*(Note: In a production deployment, all default demo credentials must be updated.)*

---

## Running Verification / Diagnostic Scripts

To verify database connectivity and user authentication without opening the web browser:
```powershell
python test_db_auth.py
```

To safely reset or synchronize doctor passwords:
```powershell
python reset_doctor_passwords.py
```

---

## Security & Sensitive Information

- **Credentials & API Keys:** Passwords and secrets are stored as environment variables. Never commit `.env` to version control.
- **Patient Privacy:** The repository contains no real patient identifiable records or medical reports. All seed records and test data are synthetic.
- **Uploaded Documents:** Patient-uploaded diagnostic files are stored locally in the `uploads/` directory, which is excluded from Git tracking.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
