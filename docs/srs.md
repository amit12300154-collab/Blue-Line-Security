# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## FOR
# BLUE LINE – Smart Security, Emergency Detection, Live Location & Alert System

**Degree:** Bachelor of Technology (B.Tech) in Computer Science & Engineering  
**Academic Year:** 2025–2026  
**Document Version:** 1.0  
**Status:** Approved for Major Project Submission  

---

### CERTIFICATE
This is to certify that the project report entitled **“BLUE LINE – Smart Security, Emergency Detection, Live Location & Alert System”** is a bonafide work carried out in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science & Engineering**.

\
*(Project Guide / Mentor)* &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; *(Head of Department)*

---

### DECLARATION
I hereby declare that this project work entitled **“BLUE LINE”** submitted to the Department of Computer Science & Engineering is an authentic record of our own research and development carried out under academic supervision. The results embodied in this report have not been submitted to any other University or Institute for the award of any degree or diploma.

\
*(Student Signature / Roll Number)*

---

### ACKNOWLEDGEMENT
We express our deepest gratitude to our project guide, faculty mentors, and the Department of Computer Science & Engineering for their constant guidance, technical feedback, and encouragement throughout the inception and development of the **Blue Line** safety platform.

---

### ABSTRACT
Personal security in urban environments requires proactive, frictionless, and automated response capabilities. Traditional emergency handling relies on physical voice calls or delayed text communication, which can be impossible during critical duress such as accidents, assaults, or medical crises. 

This project presents **BLUE LINE**, a comprehensive, full-stack personal safety and emergency dispatch prototype. Built on Python 3, Flask, and SQLAlchemy with modern HTML5 sensors and Leaflet.js mapping, Blue Line integrates three multi-modal distress triggers: (1) an immediate manual SOS panic mechanism, (2) automated sudden impact/shake detection leveraging device accelerometers (`DeviceMotionEvent`), and (3) hands-free voice distress keyword recognition via the browser Web Speech API. 

To eliminate spurious alarms, the architecture incorporates an automated 10-second cancellation countdown window. Upon validation, the system instantly acquires high-precision GPS coordinates, computes the nearest verified police station using the mathematical Haversine spherical distance formula, broadcasts structured emergency dispatches to registered family contacts with live Google Maps links, and streams continuous real-time breadcrumbs to an administrative monitoring dashboard. Blue Line is specifically architected as an academic prototype with an integrated Demo Mode to ensure safe, zero-cost university demonstration without burdening public emergency infrastructure.

---

## 1. INTRODUCTION

### 1.1 Purpose
The purpose of this document is to define the functional, non-functional, interface, and operational requirements for the **BLUE LINE – Smart Security, Emergency Detection, Live Location & Alert System**. It serves as the authoritative specification for developers, quality assurance engineers, project guides, and university evaluators.

### 1.2 Scope
Blue Line encompasses:
1. Citizen authentication and profile management (with medical blood group indexing).
2. Priority-ordered emergency contact management.
3. Multi-modal emergency triggering: manual SOS, acceleration shake detection, and voice keywords.
4. False alarm prevention via a 10-second verification countdown.
5. High-accuracy geolocation capture and continuous breadcrumb streaming.
6. Proximity-based nearest police station discovery using the Haversine formula.
7. Multi-channel contact dispatching abstraction (Email/SMTP and console simulator).
8. Live administrative command dashboard with real-time mapping.

### 1.3 Definitions, Acronyms, and Abbreviations
- **GPS:** Global Positioning System.
- **Haversine Formula:** Mathematical formulation calculating great-circle distances between coordinate pairs on a sphere.
- **API:** Application Programming Interface.
- **ORM:** Object-Relational Mapping (SQLAlchemy).
- **SRS:** Software Requirements Specification.
- **PBKDF2:** Password-Based Key Derivation Function 2.
- **REST:** Representational State Transfer.

---

## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective
Blue Line functions as a cloud-ready, responsive web service accessible across desktop workstations and mobile smart devices. It relies on standard browser Web APIs (Geolocation, DeviceMotion, Web Speech) without mandating proprietary native hardware drivers.

### 2.2 Product Functions
- Citizen registration with password hashing and phone validation.
- Emergency contact CRUD operations with priority rank and active state toggles.
- Panic button activation with emergency categorization (Robbery, Accident, Medical, Assault, Fire, etc.).
- Continuous device acceleration monitoring with configurable sensitivity thresholds (default 25.0 m/s²).
- Voice recognition listening for the keyword "HELP".
- Interactive Leaflet.js OpenStreetMap visualization displaying user beacon, accuracy radius, and nearest police post.
- Central administrator surveillance panel monitoring active distress signals.

### 2.3 User Classes and Characteristics
1. **Citizen / User:** General public seeking personal security. Minimal technical skills required.
2. **Administrator:** System monitors, emergency desk personnel, and university evaluators with permissions to manage police stations, helplines, and review system-wide incidents.

### 2.4 Operating Environment
- **Server:** Windows 10/11, Linux (Ubuntu 22.04+), Python 3.11+.
- **Database:** SQLite (default development) / PostgreSQL 15+.
- **Client Browsers:** Google Chrome 90+, Microsoft Edge 90+, Mozilla Firefox 88+, Safari 14+.

### 2.5 Design Constraints
- Must run cleanly on local Windows developer environments without paid third-party API dependencies.
- Passwords must never be stored in plaintext.
- Audio from voice triggers must never be recorded, uploaded, or stored.
- Must provide an unambiguous Demo Mode separating simulated dispatches from real-world civil emergency lines.

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 Module 1: Authentication & User Management
- **FR-1.1:** System shall permit citizen registration requiring Full Name, Email, Phone, and Password.
- **FR-1.2:** System shall securely hash passwords using PBKDF2 before storage.
- **FR-1.3:** System shall reject duplicate email registrations.
- **FR-1.4:** System shall support role-based session authorization (`USER` vs `ADMIN`).

### 3.2 Module 2: Emergency Contact Directory
- **FR-2.1:** Users shall be able to register multiple emergency contacts with Name, Relationship, Phone, Email, and Priority.
- **FR-2.2:** Users shall be able to update, activate, deactivate, or delete emergency contacts.
- **FR-2.3:** System shall enforce strict data isolation preventing one user from accessing another user's contacts.

### 3.3 Module 3: Threat Detection & Safety Countdown
- **FR-3.1:** System shall provide a prominent 1-click SOS button.
- **FR-3.2:** System shall prompt users to specify the nature of the emergency (Robbery, Accident, Medical, etc.).
- **FR-3.3:** When acceleration exceeds the configured threshold or voice keyword is heard, system shall trigger an automated 10-second countdown.
- **FR-3.4:** If the user selects "I Am Safe - Cancel", the countdown shall abort immediately without creating an alert.

### 3.4 Module 4: Geolocation & Live Breadcrumb Tracking
- **FR-4.1:** System shall query `navigator.geolocation` for latitude, longitude, and accuracy upon alert activation.
- **FR-4.2:** System shall generate direct navigation links formatted as `https://www.google.com/maps?q={lat},{lon}`.
- **FR-4.3:** System shall stream live coordinate updates via `watchPosition` throttled to at least 5-second intervals.
- **FR-4.4:** System shall immediately terminate GPS streaming when an emergency is marked `RESOLVED` or `FALSE_ALARM`.

### 3.5 Module 5: Proximity Engine & Helplines
- **FR-5.1:** System shall calculate distances to all stored police stations using the Haversine formula.
- **FR-5.2:** System shall associate the nearest police station with the emergency record.
- **FR-5.3:** System shall display official national civil emergency numbers (112, 100, 108, 1091).

### 3.6 Module 6: Notification Dispatch
- **FR-6.1:** System shall format standardized emergency alert payloads containing citizen name, incident type, trigger, time, coordinates, and map link.
- **FR-6.2:** System shall route notifications through an abstract provider (Console fallback in Demo Mode, SMTP in production).

### 3.7 Module 7: Administrative Command Center
- **FR-7.1:** Administrators shall access an overview dashboard showing active alerts, resolved incidents, and system metrics.
- **FR-7.2:** Administrators shall view a live map plotting all concurrent active incidents.
- **FR-7.3:** Administrators shall be able to add, edit, verify, or remove police stations and emergency numbers.

---

## 4. NON-FUNCTIONAL REQUIREMENTS

- **NFR-1 (Performance):** Dashboard metrics and active alert queries shall execute within 200 milliseconds on local instances.
- **NFR-2 (Security):** All user sessions must be protected against CSRF and session hijacking. Plaintext passwords are strictly prohibited.
- **NFR-3 (Privacy):** Location data is collected strictly during an active emergency. No ambient background tracking is permitted outside emergency states.
- **NFR-4 (Reliability):** In the event of sensor or network failure, the client shall present graceful fallback messages and prompt manual dialing of 112.
- **NFR-5 (Usability):** High-contrast UI with prominent emergency buttons suitable for high-stress operation.

---

## 5. SYSTEM VERIFICATION & ACCEPTANCE CRITERIA
Acceptance testing is validated when all 16 automated unit and integration tests in the pytest suite execute with zero failures, confirming functional accuracy across authentication, contact management, incident creation, location streaming, and Haversine mathematics.
