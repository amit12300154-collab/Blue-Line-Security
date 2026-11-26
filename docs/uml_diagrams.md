# BLUE LINE – UML & System Diagrams Document

All diagrams are written in standard Mermaid specification and can be rendered directly in GitHub markdown viewers, VS Code Markdown preview, or Mermaid Live Editor.

---

## 1. System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client ["Client Device (Browser / Mobile)"]
        Sensors["Motion Sensor (DeviceMotionEvent)"]
        Voice["Voice Listener (Web Speech API)"]
        GPS["GPS Geolocation (navigator.geolocation)"]
        UI["Bootstrap 5 UI & Leaflet.js Map"]
    end

    subgraph Server ["Blue Line Application Server (Flask)"]
        Router["Route Controllers (/auth, /dashboard, /emergency, /admin)"]
        API["REST API Layer (/api/...)"]
        AlertMgr["AlertService"]
        LocMgr["LocationService"]
        PoliceMgr["PoliceService (Haversine Formula)"]
        NotifyMgr["NotificationService (Provider Strategy)"]
    end

    subgraph Storage ["Persistence & Third Party"]
        DB[(SQLAlchemy ORM / SQLite)]
        SMTP["SMTP Mail Dispatcher"]
        OSM["OpenStreetMap Tile Server"]
    end

    Sensors --> UI
    Voice --> UI
    GPS --> UI
    UI --> Router
    UI --> API
    Router --> AlertMgr
    API --> AlertMgr
    API --> LocMgr
    AlertMgr --> LocMgr
    AlertMgr --> PoliceMgr
    AlertMgr --> NotifyMgr
    AlertMgr --> DB
    LocMgr --> DB
    PoliceMgr --> DB
    NotifyMgr --> SMTP
    UI <--> OSM
```

---

## 2. Use Case Diagram

```mermaid
flowchart LR
    Citizen(["Citizen / User"])
    Admin(["Administrator"])
    Contacts(["Emergency Contacts"])
    PoliceStation(["Police Station Registry"])

    subgraph BlueLineSystem ["BLUE LINE Platform"]
        UC1["Register / Login"]
        UC2["Manage Emergency Contacts"]
        UC3["Toggle Motion / Voice Sensors"]
        UC4["Trigger SOS / Manual Report"]
        UC5["10-Second Safety Countdown"]
        UC6["Cancel Alert (I Am Safe)"]
        UC7["Stream Live GPS Location"]
        UC8["View Nearest Police Station"]
        UC9["Resolve Emergency Incident"]
        UC10["Audit Live Incident Fleet"]
        UC11["Manage Police Stations"]
        UC12["Manage Emergency Numbers"]
    end

    Citizen --> UC1
    Citizen --> UC2
    Citizen --> UC3
    Citizen --> UC4
    Citizen --> UC5
    Citizen --> UC6
    Citizen --> UC7
    Citizen --> UC8
    Citizen --> UC9

    UC5 -.->|On Timeout/Confirm| UC7
    UC7 --> Contacts
    UC8 --> PoliceStation

    Admin --> UC1
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
```

---

## 3. Data Flow Diagrams (DFD)

### 3.1 DFD Level 0 (Context Diagram)

```mermaid
flowchart TD
    User["Registered User / Citizen"]
    System["BLUE LINE System (Process 0.0)"]
    Contacts["Emergency Contacts"]
    Admin["System Administrator"]
    DB[(Incident Database)]

    User -->|"Credentials, Sensor Data, Emergency Trigger, GPS"| System
    System -->|"Safety Countdown, Live Map, Incident Status"| User
    System -->|"Emergency Alert Notification, Google Maps Link"| Contacts
    System -->|"Read / Write Records"| DB
    DB -->|"User, Station & Alert Data"| System
    Admin -->|"Police Station CRUD, Number Management"| System
    System -->|"Incident Surveillance Metrics"| Admin
```

### 3.2 DFD Level 1

```mermaid
flowchart TD
    User["Citizen"]
    P1["1.0 User Authentication & Profile"]
    P2["2.0 Contact Registry Management"]
    P3["3.0 Sensor & Trigger Ingestion"]
    P4["4.0 Geolocation & Proximity Engine"]
    P5["5.0 Notification Dispatcher"]
    P6["6.0 Admin Oversight & Audit"]
    
    D1[("Users Store")]
    D2[("Contacts Store")]
    D3[("Alerts Store")]
    D4[("Police Stations Store")]
    D5[("Breadcrumbs Store")]

    User -->|Credentials| P1
    P1 <--> D1
    User -->|Contact Info| P2
    P2 <--> D2
    User -->|SOS / Impact / Voice| P3
    P3 -->|Create Alert| D3
    P3 -->|Trigger GPS Request| P4
    P4 -->|Store Breadcrumb| D5
    P4 <--> D4
    D3 --> P5
    D2 --> P5
    P5 -->|Simulated Alert| ExtContacts["Contacts"]
    P6 <--> D1
    P6 <--> D3
    P6 <--> D4
```

---

## 4. Class Diagram

```mermaid
classDiagram
    class User {
        +int id
        +string full_name
        +string email
        +string phone
        +string password_hash
        +string role
        +boolean is_active
        +set_password(password)
        +check_password(password) bool
        +is_admin() bool
        +to_dict() dict
    }

    class EmergencyContact {
        +int id
        +int user_id
        +string name
        +string relationship
        +string phone
        +string email
        +int priority
        +boolean is_active
        +to_dict() dict
    }

    class EmergencyAlert {
        +int id
        +int user_id
        +string trigger_type
        +string emergency_type
        +string status
        +float latitude
        +float longitude
        +float accuracy
        +int nearest_police_station_id
        +datetime created_at
        +datetime resolved_at
        +google_maps_url() string
        +to_dict() dict
    }

    class LocationUpdate {
        +int id
        +int alert_id
        +float latitude
        +float longitude
        +float accuracy
        +datetime timestamp
        +to_dict() dict
    }

    class PoliceStation {
        +int id
        +string station_name
        +string address
        +string city
        +string state
        +float latitude
        +float longitude
        +string emergency_number
        +boolean is_verified
        +to_dict() dict
    }

    class EmergencyNumber {
        +int id
        +string name
        +string number
        +string country
        +boolean is_active
        +to_dict() dict
    }

    User "1" --> "*" EmergencyContact : owns
    User "1" --> "*" EmergencyAlert : triggers
    EmergencyAlert "1" --> "*" LocationUpdate : breadcrumbs
    EmergencyAlert "*" --> "0..1" PoliceStation : matches_nearest
```

---

## 5. Sequence Diagram: Emergency Trigger & Dispatch

```mermaid
sequenceDiagram
    actor Citizen
    participant ClientUI as Web UI / Sensors
    participant AlertController as Emergency Controller
    participant AlertService as AlertService
    participant PoliceService as PoliceService
    participant NotificationService as NotificationService
    actor Contacts as Emergency Contacts

    Citizen->>ClientUI: Tap Large SOS / Physical Shake (>25 m/s²) / Say "HELP"
    ClientUI->>ClientUI: Start 10-Second Safety Countdown Modal
    alt User taps "I Am Safe"
        Citizen->>ClientUI: Tap "I Am Safe - Cancel"
        ClientUI->>ClientUI: Halt Countdown (No Alert Created)
    else 10 Seconds Expire / User confirms
        ClientUI->>ClientUI: Acquire GPS via navigator.geolocation
        ClientUI->>AlertController: POST /api/emergency/create (coords, type, trigger)
        AlertController->>AlertService: create_alert(user_id, coords, ...)
        AlertService->>PoliceService: find_nearest_station(lat, lon)
        PoliceService-->>AlertService: Nearest Police Station Record & Distance
        AlertService->>AlertService: Save EmergencyAlert in Database
        AlertService->>NotificationService: notify_emergency_contacts(alert, user, contacts)
        NotificationService->>Contacts: Send Simulated SMS / Email with Google Maps URL
        AlertService-->>AlertController: Alert Created (#ID)
        AlertController-->>ClientUI: 201 Created & Redirect /emergency/
        ClientUI->>ClientUI: Initialize Leaflet Map & watchPosition live stream
    end
```

---

## 6. Activity Diagram: Full Incident Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Standby: User Logged In
    Standby --> ThreatDetected: SOS Click / Shake / "HELP" Spoken
    ThreatDetected --> Countdown: Display 10-Second Countdown
    
    state Countdown {
        [*] --> CountingDown
        CountingDown --> CheckSafe: User Clicks "I Am Safe"
        CountingDown --> Timeout: 10s Elapsed or User Confirms
    }
    
    CheckSafe --> Standby: Cancelled (Safe)
    
    Timeout --> FetchGPS: Query HTML5 Geolocation
    FetchGPS --> RecordAlert: Persist Alert to Database
    RecordAlert --> CalculatePolice: Compute Haversine Distance to Stations
    CalculatePolice --> NotifyContacts: Dispatch Email/Console Alert with Map Link
    NotifyContacts --> LiveTracking: Display Emergency Screen (Leaflet Map)
    
    state LiveTracking {
        [*] --> StreamingCoordinates
        StreamingCoordinates --> PostBreadcrumb: watchPosition Callback (Throttled 5s)
        PostBreadcrumb --> StreamingCoordinates
    }

    LiveTracking --> Resolved: User taps "Resolve Emergency"
    LiveTracking --> FalseAlarm: User taps "Mark False Alarm"
    
    Resolved --> HistorySaved: Stop GPS watch, record resolved_at
    FalseAlarm --> HistorySaved: Stop GPS watch, record status
    HistorySaved --> [*]
```
