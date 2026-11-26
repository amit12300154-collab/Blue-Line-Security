# BlueLine Secure – Smart Security, Emergency Detection & Alert System

## ⚡ Quick Start in VS Code (3 steps)

1. **Install Python 3.10+** (tick *Add Python to PATH*) and open this folder in VS Code (`File > Open Folder`).
2. Open the VS Code terminal (`Ctrl + ~`) and run:
   - **Windows:** `run.bat`  (or manually: `python -m venv venv` → `venv\Scripts\activate` → `pip install -r requirements.txt` → `python app.py`)
   - **macOS / Linux:** `bash run.sh`
3. Open **http://127.0.0.1:5000** in Chrome/Edge.
   Demo user: `demo@example.com` / `Demo@12345` · Admin: `admin@blueline.local` / `Admin@12345`

You can also press **F5** in VS Code and pick *Blue Line: Run (python app.py)*. Run tests with `pytest -v`.
The first run needs internet (Bootstrap, icons and Leaflet maps load from CDNs).
Shake detection, microphone and GPS work on `localhost`; on a phone the site must be served over **HTTPS**.

### What changed in this version
- **Fixed crash on startup:** `services/location_service.py` used a type alias before defining it (NameError).
- **Countdown timer now works:** the value saved in *Settings* (preset or custom 3-120 s) is actually used; the voice keyword setting also works.
- **Choose emergency type during the countdown** (Fire, Robbery, Theft, Assault, Harassment, Medical, Accident, Other), even for shake/voice triggers.
- **Shake detection** needs 2 strong spikes (fewer false alarms); the sensor can now really be switched off.
- **Voice detection** also understands *sos, bachao, madad* (Hindi/Punjabi too) and no longer restarts the countdown repeatedly.
- Security: open-redirect fix on login, SameSite/HttpOnly cookies, safe parsing of GPS values, JS-safe police-station data on the emergency page.
- Added `.vscode` config, `run.bat` / `run.sh`, ready `.env`, and extra tests (`tests/test_security.py`).

**BlueLine Secure** (Blue Line Security System) is a complete, full-stack emergency response, personal security, and tactical dispatch platform. Built with Python, Flask, SQLite/SQLAlchemy, Leaflet.js, and Bootstrap 5, BlueLine Secure bridges citizen distress signals with immediate family notifications, spatial geolocation tracking, and proximity-based nearest police station dispatch.

---

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Main Features](#main-features)
- [Technologies Used](#technologies-used)
- [Project Architecture](#project-architecture)
- [Folder Structure](#folder-structure)
- [Database Models & Schema](#database-models--schema)
- [REST API Routes](#rest-api-routes)
- [Installation Requirements](#installation-requirements)
- [Installation Commands](#installation-commands)
- [Environment Variable Setup](#environment-variable-setup)
- [Database Setup & Seeding](#database-setup--seeding)
- [How to Start the Project](#how-to-start-the-project)
- [Running Automated Tests](#running-automated-tests)
- [Demo Accounts & Login Information](#demo-accounts--login-information)
- [Academic Integrity & Demo Mode](#academic-integrity--demo-mode)
- [Future Improvements](#future-improvements)

---

## 🌟 Project Overview
When an individual faces physical assault, a road accident, medical shock, or duress, conventional emergency reporting (such as unlocking a smartphone, looking up contact numbers, and verbally describing landmarks) suffers from unacceptable latency and high failure rates.

**BlueLine Secure** solves this crisis by combining:
1. **Multi-Modal Threat Detection:** One-click SOS trigger, automatic phone shake/fall impact detection via hardware accelerometers, and hands-free voice recognition ("HELP").
2. **False Alarm Mitigation:** A client-side 10-second verification countdown window allows safe cancellation ("I Am Safe") before external dispatches occur.
3. **Live Geolocation Tracking:** Streams real-time GPS coordinates to interactive Leaflet.js maps with historical breadcrumbs and direct Google Maps navigation links.
4. **Proximity Optimization:** Calculates spherical great-circle distances via the **Haversine formula** to identify the closest verified police station.
5. **Admin Tactical Command Hub:** Provides emergency operators with real-time incident monitoring, station registries, and audit logs.

---

## 🚀 Main Features

### Citizen Safety Features
- **1-Click Emergency SOS:** Large, high-contrast panic button triggering immediate response protocols.
- **Fall / Impact Detection:** Monitors `window.devicemotion` vector acceleration ($\sqrt{x^2 + y^2 + z^2}$) exceeding threshold ($25.0\text{ m/s}^2$).
- **Voice Recognition Trigger:** Browser Web Speech API listens for distress keywords (*"HELP"* or *"EMERGENCY"*).
- **10-Second Safety Countdown:** Prevents spurious alarms by providing an instant "I Am Safe" cancellation button.
- **Continuous Geolocation Breadcrumbs:** Periodically uploads latitude/longitude updates every 5 seconds during active emergencies.
- **Emergency Contacts Management:** Complete CRUD interface with contact priority ranking, relationship labels, phone, and email.
- **Direct Navigation:** Auto-generates turn-by-turn navigation URLs to the nearest police station.

### Administrative Command Center
- **Tactical Fleet Map:** Live Leaflet.js overview displaying active emergencies across the jurisdiction.
- **Incident Audit Trails:** Full historical inspection of resolved, false-alarm, and active incidents.
- **Police Station Registry:** Add, verify, edit, and coordinate local police stations and station contacts.
- **Emergency Helpline Directory:** Manage state/national helplines (112, 100, 108, 1091).

---

## 🛠️ Technologies Used

| Domain | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Python 3.11+ / Flask 3.1 | Modular Application Factory & Blueprint routing |
| **ORM & Database** | Flask-SQLAlchemy 3.1 / SQLite 3 | Relational data persistence with foreign keys |
| **User Authentication** | Flask-Login 0.6 / Werkzeug | Session management, PBKDF2-SHA256 password hashing |
| **Form & CSRF Validation**| Flask-WTF / email-validator | Form parsing, CSRF token validation, input sanitization |
| **Frontend Framework** | Bootstrap 5.3 / Font Awesome 6 | Responsive, mobile-first emergency UI |
| **Mapping Engine** | Leaflet.js 1.9 / OpenStreetMap | Live spatial GPS marker rendering & breadcrumbs |
| **Device Sensors** | HTML5 Geolocation, DeviceMotionEvent | Motion thresholding, browser GPS acquisition |
| **Speech Processing** | Web Speech API (`SpeechRecognition`) | Client-side keyword distress detection |
| **Distance Algorithm** | Haversine Formula (Trigonometric) | Great-circle distance calculations on spherical coordinates |
| **Automated Testing** | Pytest 8.x / StaticPool SQLite | Full unit and integration test coverage |

---

## 🏛️ Project Architecture
BlueLine Secure follows a standard **3-Tier MVC / Service-Layer Architecture**:

```text
┌────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                   │
│   Jinja2 Templates | Bootstrap 5.3 | Leaflet.js Maps   │
│   Sensor Handlers: motion.js | voice.js | location.js  │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP / JSON REST APIs
┌───────────────────────────▼────────────────────────────┐
│                    CONTROLLER LAYER                    │
│   auth_bp | dashboard_bp | contacts_bp | emergency_bp  │
│   api_bp  | admin_bp                                   │
└───────────────────────────▲────────────────────────────┘
                            │ Service Invocations
┌───────────────────────────▼────────────────────────────┐
│                  SERVICE / BUSINESS LAYER              │
│   AlertService    LocationService   PoliceService      │
│   EmergencyService  NotificationService (Simulator)    │
│   Haversine Formula Engine (utils/distance.py)         │
└───────────────────────────▲────────────────────────────┘
                            │ SQLAlchemy ORM
┌───────────────────────────▼────────────────────────────┐
│                       DATA LAYER                       │
│   SQLite Database (instance/blue_line.db)             │
│   Models: User, EmergencyContact, EmergencyAlert,      │
│           LocationUpdate, PoliceStation, EmergencyNum  │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```text
BlueLineSecureOfficial-main/
├── .env.example              # Safe environment variable configuration template
├── .gitignore                # Git exclusion list (venv, pycache, db, logs)
├── app.py                    # Flask application factory and main entry point
├── config.py                 # Development, Testing, and Production configurations
├── requirements.txt          # Python dependency specifications
├── README.md                 # Complete project documentation and guide
│
├── database/                 # Database initialization and seed scripts
│   ├── __init__.py           # Database extension instance
│   └── seed_data.py          # Auto-seeding script with verified demo records
│
├── docs/                     # Academic documentation & Major Project Report
│   ├── api.md                # REST API documentation
│   ├── architecture.md       # Architectural blueprints & Data Flow Diagrams
│   ├── database.md           # Database data dictionary & schema
│   ├── project_report.md     # 22-Chapter B.Tech Major Project Report
│   ├── setup.md              # Setup and execution guide
│   ├── srs.md                # Software Requirements Specification (IEEE standard)
│   └── uml_diagrams.md       # Complete UML diagrams (Use Case, Class, Sequence)
│
├── models/                   # SQLAlchemy Relational Models
│   ├── __init__.py           # Model exports
│   ├── emergency_alert.py    # Emergency alerts & status lifecycle
│   ├── emergency_contact.py  # Prioritized emergency family/guardian contacts
│   ├── emergency_number.py   # Civil helpline directory (112, 100, 108, 1091)
│   ├── location_update.py    # GPS coordinate breadcrumbs for active alerts
│   ├── police_station.py     # Verified police stations with geo-coordinates
│   └── user.py               # User identity, password hashes, and roles
│
├── routes/                   # Flask Blueprints & HTTP Controllers
│   ├── __init__.py           # Route blueprint registrations
│   ├── admin.py              # Admin tactical dashboard, fleet monitoring, station CRUD
│   ├── api.py                # Mobile/AJAX REST API endpoints
│   ├── auth.py               # User registration, login, logout, profile
│   ├── contacts.py           # Contact management web interface
│   ├── dashboard.py          # Citizen main dashboard and safety tips
│   └── emergency.py          # SOS trigger, countdown, and active incident view
│
├── services/                 # Business Logic & Service Layer
│   ├── __init__.py           # Service exports
│   ├── alert_service.py      # Alert creation, dispatch, resolution orchestration
│   ├── emergency_service.py  # High-level incident queries and dashboard metrics
│   ├── location_service.py   # Coordinate validation and breadcrumb recording
│   ├── notification_service.py # Simulated notification dispatch (Console/Email)
│   └── police_service.py     # Nearest station query using Haversine calculation
│
├── static/                   # Static Web Assets
│   ├── css/                  # Styling & high-contrast emergency themes
│   │   ├── dashboard.css     # Dashboard & admin layout styles
│   │   └── style.css         # Main application styles, alerts, countdown banner
│   ├── images/               # Application icons and branding assets
│   └── js/                   # Client-side hardware sensor scripts
│       ├── dashboard.js      # Dashboard charts and dynamic components
│       ├── emergency.js      # SOS countdown timer & incident resolution
│       ├── location.js       # HTML5 GPS continuous position streaming
│       ├── map.js            # Leaflet.js interactive maps & markers
│       ├── motion.js         # DeviceMotionEvent accelerometer thresholding
│       └── voice.js          # SpeechRecognition hands-free keyword matching
│
├── templates/                # Jinja2 HTML Templates
│   ├── admin/                # Admin portal views
│   │   ├── alert_details.html
│   │   ├── alerts.html
│   │   ├── dashboard.html
│   │   ├── emergency_numbers.html
│   │   ├── police_stations.html
│   │   ├── user_details.html
│   │   └── users.html
│   ├── errors/               # Custom HTTP error pages (403, 404, 500)
│   ├── base.html             # Master layout with responsive navbar & alerts
│   ├── contacts.html         # Emergency contact CRUD view
│   ├── dashboard.html        # Citizen control hub with SOS panic button
│   ├── emergency.html        # Active emergency tracking interface
│   ├── history.html          # User past alert history
│   ├── how_it_works.html     # System overview and trigger explanation
│   ├── index.html            # Landing homepage with public helpline directory
│   ├── login.html            # User authentication page
│   ├── map.html              # Dedicated full-screen tactical map
│   ├── privacy.html          # Data protection and privacy policy
│   ├── profile.html          # User profile view and update
│   ├── register.html         # User account registration
│   └── settings.html         # User notification & sensor preferences
│
├── tests/                    # Automated Test Suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures and isolated in-memory DB client
│   ├── test_auth.py          # Authentication and authorization tests
│   ├── test_contacts.py      # Contact CRUD and isolation tests
│   ├── test_emergency.py     # SOS trigger and resolution tests
│   ├── test_location.py      # GPS coordinate and breadcrumb tests
│   └── test_police.py        # Haversine distance and station API tests
│
└── utils/                    # Utility Functions & Mathematical Algorithms
    ├── __init__.py
    ├── distance.py           # Haversine spherical trigonometric calculation
    ├── helpers.py            # Standardized JSON API response formatters
    └── validators.py         # Phone, email, and coordinate input validators
```

---

## 🗄️ Database Models & Schema

The application uses six normalized relational tables:
1. **`users`**: User ID, full name, email (unique), password hash (PBKDF2), phone, address, blood group, role (`USER` or `ADMIN`), is_active, created_at.
2. **`emergency_contacts`**: Contact ID, user_id (FK), name, relationship, phone, email, priority, is_active, created_at.
3. **`emergency_alerts`**: Alert ID, user_id (FK), trigger_type (`PANIC_BUTTON`, `SHAKE_FALL`, `VOICE_HELP`, `MANUAL`), emergency_type (`MEDICAL`, `ACCIDENT`, `ASSAULT`, `FIRE`, `OTHER`), status (`ACTIVE`, `RESOLVED`, `FALSE_ALARM`), initial latitude/longitude, accuracy, nearest_police_station_id (FK), resolved_at, created_at.
4. **`location_updates`**: Update ID, alert_id (FK), latitude, longitude, accuracy, recorded_at.
5. **`police_stations`**: Station ID, station_name, address, city, state, latitude, longitude, phone_number, emergency_number (112), is_verified, created_at.
6. **`emergency_numbers`**: Helpline ID, title, number, category, description, is_active.

---

## 🔌 REST API Routes

### Authentication
- `POST /api/login`: Authenticate and start session.
- `POST /api/logout`: Terminate active session.

### Emergency & Dispatch
- `POST /api/emergency/create`: Trigger distress alert (payload: `trigger_type`, `emergency_type`, `latitude`, `longitude`, `accuracy`).
- `GET /api/emergency/<id>`: Retrieve alert details, breadcrumbs, and nearest station.
- `POST /api/emergency/<id>/location`: Record live GPS breadcrumb update.
- `POST /api/emergency/<id>/resolve`: Mark incident as safely resolved.
- `POST /api/emergency/<id>/false-alarm`: Mark incident as false alarm during countdown.

### Contacts
- `GET /api/contacts`: List all prioritized emergency contacts.
- `POST /api/contacts`: Create new emergency contact.
- `PUT /api/contacts/<id>`: Update contact details or priority.
- `DELETE /api/contacts/<id>`: Delete contact.

### Stations & Helplines
- `GET /api/police-stations`: List all verified police stations.
- `GET /api/police-stations/nearest?lat=<lat>&lon=<lon>`: Query closest station via Haversine.
- `GET /api/emergency-numbers`: Retrieve national emergency helplines.
- `GET /api/dashboard/stats`: Retrieve operational statistics.

---

## ⚙️ Installation Requirements

- **Operating System:** Windows 10/11, Linux, or macOS.
- **Python Version:** Python 3.11, 3.12, 3.13, or 3.14.
- **Browser:** Google Chrome or Microsoft Edge (recommended for Web Speech API and Geolocation).

---

## 💻 Installation Commands

### 1. Clone or Extract the Project
```bash
cd BlueLineSecureOfficial-main
```

### 2. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Environment Variable Setup

Copy the `.env.example` template to `.env`:
```powershell
Copy-Item .env.example .env
```
*(On Linux/macOS: `cp .env.example .env`)*

The default configuration is pre-tuned for local evaluation:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=blue-line-insecure-dev-key-change-me
DATABASE_URL=sqlite:///instance/blue_line.db
DEMO_MODE=true
IMPACT_THRESHOLD=25.0
EMERGENCY_COUNTDOWN=10
ADMIN_DEFAULT_EMAIL=admin@blueline.local
ADMIN_DEFAULT_PASSWORD=Admin@12345
DEMO_USER_EMAIL=demo@example.com
DEMO_USER_PASSWORD=Demo@12345
```

---

## 💾 Database Setup & Seeding

The database will be automatically created on first launch. To explicitly initialize and seed demo records, run:
```powershell
python database/seed_data.py
```
**Output:**
```text
[Seed] Created Administrator: admin@blueline.local
[Seed] Created Demo User: demo@example.com
[Seed] Added 3 demo emergency contacts for demo@example.com
[Seed] Added 5 verified police station records (DEMO)
[Seed] Added 6 emergency helpline numbers
[Seed] Database seeding completed successfully.
```

---

## 🚀 How to Start the Project

Run the application:
```powershell
python app.py
```

Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the complete test suite:
```powershell
pytest -v
```
All **16 unit and integration tests** will execute and pass:
```text
tests/test_auth.py::test_user_registration PASSED
tests/test_auth.py::test_duplicate_email_registration PASSED
tests/test_auth.py::test_login_successful PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_admin_access_control PASSED
tests/test_auth.py::test_logout PASSED
tests/test_contacts.py::test_add_emergency_contact PASSED
tests/test_contacts.py::test_edit_emergency_contact PASSED
tests/test_contacts.py::test_delete_emergency_contact PASSED
tests/test_emergency.py::test_emergency_alert_creation_and_resolve PASSED
tests/test_emergency.py::test_false_alarm_marking PASSED
tests/test_location.py::test_coordinate_validation PASSED
tests/test_location.py::test_live_location_updates PASSED
tests/test_police.py::test_haversine_distance_calculation PASSED
tests/test_police.py::test_nearest_police_station_lookup PASSED
tests/test_police.py::test_police_station_api PASSED
============================= 16 passed in 7.68s =============================
```

---

## 👤 Demo Accounts & Login Information

| Role | Email | Password | Access Privileges |
|---|---|---|---|
| **System Administrator** | `admin@blueline.local` | `Admin@12345` | Real-time incident fleet map, station registry, system audits |
| **Citizen User** | `demo@example.com` | `Demo@12345` | SOS panic button, sensor triggers, contact CRUD, live tracking |

---

## 🛡️ Academic Integrity & Demo Mode
During academic demonstrations and examinations:
- **`DEMO_MODE=true`** is active by default.
- Simulated notification dispatches are logged to the console rather than charging commercial SMS gateways or inadvertently calling state 112 emergency phone lines.
- All police stations and contacts are explicitly tagged with `(DEMO DATA)` markers.

---

## 🔮 Future Improvements
1. **Native Mobile App:** Build Flutter / React Native wrappers for background sensor execution when the screen is locked.
2. **ERSS 112 Direct API Integration:** Secure integration with official state Emergency Response Support Systems.
3. **IoT Smart Wearables:** Bluetooth BLE integration with panic wristbands and smart clothing.
4. **Machine Learning Fall Classifier:** Train a tinyML fall-detection model using TensorFlow Lite to distinguish accidental phone drops from actual human falls.
