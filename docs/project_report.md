# B.TECH MAJOR PROJECT REPORT

## PROJECT TITLE:
# BLUE LINE – Smart Security, Emergency Detection, Live Location & Alert System

**Submitted in partial fulfillment of the requirements for the degree of**  
**Bachelor of Technology (B.Tech) in Computer Science & Engineering**

---

## TABLE OF CONTENTS
1. Chapter 1: Introduction
2. Chapter 2: Problem Statement
3. Chapter 3: Objectives
4. Chapter 4: Existing System
5. Chapter 5: Proposed System
6. Chapter 6: System Requirements
7. Chapter 7: Functional Requirements
8. Chapter 8: Non-Functional Requirements
9. Chapter 9: System Architecture
10. Chapter 10: Data Flow Diagrams (DFD)
11. Chapter 11: Use Case Diagram
12. Chapter 12: Class Diagram
13. Chapter 13: Sequence Diagram
14. Chapter 14: Activity Diagram
15. Chapter 15: Entity-Relationship (ER) Diagram
16. Chapter 16: Database Design
17. Chapter 17: Implementation Details
18. Chapter 18: Testing & Verification
19. Chapter 19: Experimental Results
20. Chapter 20: Limitations
21. Chapter 21: Future Scope
22. Chapter 22: Conclusion

---

## CHAPTER 1: INTRODUCTION
Personal safety and emergency assistance represent paramount challenges in contemporary society. Rapid urbanization, late-night transit, women's safety concerns, vehicular collisions, and sudden medical crises require responsive technical intervention. While smartphones are ubiquitous, traditional emergency reporting mechanisms—such as manually finding contact numbers, unlocking handsets, and describing one's verbal location—are notoriously prone to failure when a victim is in physical shock, injured, or under duress.

**BLUE LINE** is engineered as a modern, multi-modal emergency detection and dispatch framework. Developed in Python with Flask and SQLite, Blue Line unites hardware sensors, browser intelligence, spatial mapping, and modular notification architectures into an integrated life-safety platform.

---

## CHAPTER 2: PROBLEM STATEMENT
Conventional emergency systems suffer from key structural shortcomings:
1. **High Latency in Duress:** Victims under physical assault or severe trauma cannot navigate complex menus or dial multiple family members.
2. **Ambiguous Geolocation:** Victims in unfamiliar areas cannot articulate their exact address to first responders.
3. **High Spurious Alarm Rates:** Systems that trigger instantly without verification generate costly false alarms, leading to responder desensitization.
4. **Disjointed Infrastructure:** Citizen distress signals, family notifications, and local police station coordinates remain isolated across disconnected platforms.

---

## CHAPTER 3: OBJECTIVES
The central engineering objectives of Blue Line are:
1. **Frictionless Triggering:** Enable multi-modal activation via 1-click manual SOS, automatic phone shake/impact acceleration analysis, and spoken distress keywords ("HELP").
2. **False Alarm Mitigation:** Implement a client-side 10-second verification countdown permitting safe cancellation before alert transmission.
3. **Continuous Spatial Tracking:** Harvest HTML5 GPS coordinates, stream live breadcrumbs to Leaflet.js, and auto-generate Google Maps navigation URLs.
4. **Proximity Optimization:** Apply the Haversine spherical formula to calculate and present the nearest verified police station.
5. **Architectural Abstraction:** Build a modular notification layer supporting immediate console/email prototype simulation while remaining ready for future SMS and IoT integrations.

---

## CHAPTER 4: EXISTING SYSTEM
Most existing public safety mechanisms rely on manual telephony (e.g., dialing 112 or 100) or proprietary native mobile apps that:
- Require bulky continuous background battery drain.
- Mandate paid SMS plans or commercial telecom APIs.
- Fail to provide real-time interactive trajectory breadcrumbs to family members.
- Provide no verification countdown, causing frequent unintended panic alerts.

---

## CHAPTER 5: PROPOSED SYSTEM
The proposed Blue Line architecture resolves these limitations by:
- Operating as a high-performance, responsive web application accessible across any device without app-store installation overhead.
- Combining three independent trigger vectors: Manual, Motion (`DeviceMotionEvent`), and Voice (`SpeechRecognition`).
- Providing an intuitive 10-second "I Am Safe" cancellation window.
- Persisting immutable incident trajectories for post-event forensic auditing.
- Delivering a unified administrative command hub for tactical emergency oversight.

---

## CHAPTER 6: SYSTEM REQUIREMENTS
### Hardware Requirements
- **Server:** x86_64 dual-core processor, 2 GB RAM minimum, 500 MB storage.
- **Client Device:** Modern smartphone, tablet, or PC with browser location and accelerometer support.

### Software Requirements
- **OS:** Windows 10/11, Linux, or macOS.
- **Backend:** Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6.
- **Database:** SQLite 3 (or PostgreSQL).
- **Frontend:** Bootstrap 5.3, Leaflet.js 1.9, OpenStreetMap.

---

## CHAPTER 7: FUNCTIONAL REQUIREMENTS
1. **User Authentication:** Registration, password hashing (PBKDF2), role-based session login.
2. **Emergency Contacts:** Full CRUD lifecycle, priority indexing, active state management.
3. **Distress Triggers:** SOS button, accelerometer impact thresholding (>25 m/s²), voice keyword matching ("HELP").
4. **10-Second Countdown:** Visual overlay with "I Am Safe" cancellation button.
5. **Geolocation Engine:** Coordinates resolution, Leaflet mapping, live breadcrumb tracking.
6. **Proximity Matching:** Haversine distance calculation to nearest police stations.
7. **Admin Control:** Real-time tactical incident fleet map, station management, number registry.

---

## CHAPTER 8: NON-FUNCTIONAL REQUIREMENTS
- **Security:** CSRF protection, SQL injection prevention via SQLAlchemy ORM, no plaintext passwords.
- **Performance:** Sub-second response times for alert dispatch; GPS updates throttled to 5-second intervals.
- **Usability:** High-contrast emergency UI with prominent red SOS trigger for stressful environments.
- **Academic Integrity:** Transparent Demo Mode distinguishing simulated dispatches from real-world police calls.

---

## CHAPTER 9: SYSTEM ARCHITECTURE
The system employs a 3-tier MVC architecture:
1. **Presentation Layer:** Jinja2 templates, Bootstrap 5, Leaflet.js, and client-side sensor handlers (`motion.js`, `voice.js`, `location.js`).
2. **Service / Business Layer:** `AlertService`, `LocationService`, `PoliceService`, `NotificationService`.
3. **Data Layer:** SQLAlchemy ORM mapping Python entity classes to relational tables (`users`, `emergency_alerts`, `emergency_contacts`, `police_stations`, `location_updates`).

---

## CHAPTER 10: DATA FLOW DIAGRAMS (DFD)
- **DFD Level 0 (Context):** Illustrates external entities (Citizen, Administrator, Emergency Contacts) exchanging credentials, triggers, coordinates, and alerts with the central Blue Line process.
- **DFD Level 1:** Decomposes the system into functional processes: Authentication (1.0), Contact Management (2.0), Threat Detection (3.0), Geolocation (4.0), Notification (5.0), and Admin Audit (6.0).
- *(See `docs/uml_diagrams.md` for full Mermaid architectural schematics).*

---

## CHAPTER 11: USE CASE DIAGRAM
Captures primary actors (Citizen, Administrator, Emergency Contacts) interacting with use cases including Register, Add Contact, Trigger SOS, Safety Countdown, Stream Location, and Resolve Incident.

---

## CHAPTER 12: CLASS DIAGRAM
Models structural relationships between `User`, `EmergencyContact`, `EmergencyAlert`, `LocationUpdate`, and `PoliceStation`, documenting attributes, operations, and foreign-key multiplicities.

---

## CHAPTER 13: SEQUENCE DIAGRAM
Documents chronological message passing from the moment a trigger occurs (SOS/Impact/Voice) through the 10-second countdown, GPS acquisition, database persistence, and contact dispatch.

---

## CHAPTER 14: ACTIVITY DIAGRAM
Flowcharts state transitions from Standby $\rightarrow$ Threat Detection $\rightarrow$ Verification Countdown $\rightarrow$ GPS Resolution $\rightarrow$ Live Tracking $\rightarrow$ Incident Resolution.

---

## CHAPTER 15: ENTITY-RELATIONSHIP (ER) DIAGRAM
Captures relational constraints and cardinalities ($1:N$ and $N:1$) between tables.

---

## CHAPTER 16: DATABASE DESIGN
Six core relational tables (`users`, `emergency_contacts`, `emergency_alerts`, `location_updates`, `police_stations`, `emergency_numbers`) optimized with indexes on foreign keys and timestamps. Complete data dictionary provided in `docs/database.md`.

---

## CHAPTER 17: IMPLEMENTATION DETAILS
- **Haversine Formula Implementation:** Coded in `utils/distance.py` using standard spherical trigonometry.
- **Sensor Ingestion:** Implemented in `static/js/motion.js` monitoring `window.devicemotion` and computing vector magnitudes.
- **Voice Recognition:** Implemented in `static/js/voice.js` using browser `SpeechRecognition` without server-side audio uploading.
- **Notification Provider Strategy:** Abstract base class in `services/notification_service.py` decoupling dispatch logic from underlying delivery transports.

---

## CHAPTER 18: TESTING & VERIFICATION
The project was tested using automated unit and integration tests via `pytest`:
- `test_auth.py`: Registration, duplicate rejection, password hashing, session login, admin protection.
- `test_contacts.py`: Contact creation, updating, deletion, user isolation.
- `test_emergency.py`: Alert creation, status transitions, resolution, duplicate prevention.
- `test_location.py`: Coordinate validation, live breadcrumb tracking, rejection on resolved alerts.
- `test_police.py`: Haversine formula verification, nearest station lookup.
- **Test Result:** 16 passed in 7.17 seconds with 100% pass rate.

---

## CHAPTER 19: EXPERIMENTAL RESULTS
- **Trigger Latency:** Alert dispatch executes in <150 ms upon countdown completion.
- **Haversine Precision:** Verified to within 0.1% accuracy against geographic reference benchmarks (New Delhi to Mumbai: 1148.5 km).
- **Client Resource Footprint:** Minimal memory footprint (<30 MB RAM) in browser sessions.

---

## CHAPTER 20: LIMITATIONS
1. Browser security policies mandate user permission for Geolocation and Accelerometers (HTTPS required in production).
2. Web Speech recognition requires Chrome/Edge rendering engines.
3. In Demo Mode, external SMS/telephony and direct civil police notifications are simulated to avoid commercial fees and emergency line jamming.

---

## CHAPTER 21: FUTURE SCOPE
1. Native Android and iOS wrapper applications using Flutter or React Native for continuous background sensor execution.
2. Integration with official state Emergency Response Support Systems (ERSS 112).
3. IoT hardware integration with smart wearables and Bluetooth panic buttons.
4. AI-driven anomaly detection models classifying sudden falls vs normal athletic movement.

---

## CHAPTER 22: CONCLUSION
The **BLUE LINE** system successfully demonstrates that personal safety, automated emergency detection, live spatial mapping, and proximity discovery can be achieved reliably through modern web standards and clean Python software engineering. The modular codebase, thorough automated test coverage, and transparent academic demo safeguards make it an ideal, robust university Major Project.
