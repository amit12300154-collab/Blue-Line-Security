# BLUE LINE – REST API Documentation

All REST API endpoints adhere to a standardized JSON response format:

```json
{
  "success": true,
  "message": "Human-readable status description",
  "data": {}
}
```

---

## 1. Authentication APIs

### `POST /api/login`
Authenticates a user and starts a session.

- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "email": "demo@example.com",
    "password": "Demo@12345"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "id": 2,
      "full_name": "Demo User",
      "email": "demo@example.com",
      "phone": "+91 9876543210",
      "role": "USER",
      "is_active": true
    }
  }
  ```
- **Error Codes:** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`

### `POST /api/logout`
Terminates user session.
- **Authentication:** Required (`login_required`)
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Successfully logged out",
    "data": {}
  }
  ```

---

## 2. Emergency Alert Lifecycle APIs

### `POST /api/emergency/create`
Triggers a new emergency alert, calculates nearest police station, and dispatches contact notifications.
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "trigger_type": "PANIC_BUTTON",
    "emergency_type": "ROBBERY",
    "description": "Someone attempted to snatch bag near metro gate 2",
    "latitude": 28.6315,
    "longitude": 77.2167,
    "accuracy": 12.5
  }
  ```
- **Allowed `trigger_type` values:** `PANIC_BUTTON`, `IMPACT_DETECTED`, `VOICE_TRIGGER`, `MANUAL_REPORT`
- **Allowed `emergency_type` values:** `ROBBERY`, `THEFT`, `ACCIDENT`, `MEDICAL`, `ASSAULT`, `HARASSMENT`, `FIRE`, `OTHER`
- **Response (201 Created):**
  ```json
  {
    "success": true,
    "message": "Emergency alert created successfully",
    "data": {
      "alert": {
        "id": 1,
        "status": "ACTIVE",
        "emergency_type": "ROBBERY",
        "trigger_type": "PANIC_BUTTON",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "accuracy": 12.5,
        "google_maps_url": "https://www.google.com/maps?q=28.6315,77.2167",
        "nearest_police_station_details": {
          "id": 1,
          "station_name": "Connaught Place Police Station (DEMO DATA)",
          "distance_km": 0.05,
          "formatted_distance": "50 meters",
          "notification_status": "SIMULATED (Demo Mode - No real emergency transmission)"
        }
      },
      "notifications_dispatched": [
        {
          "name": "Rajesh Kumar (Father)",
          "recipient": "father.demo@example.com",
          "status": "SENT",
          "provider": "ConsoleNotificationProvider"
        }
      ]
    }
  }
  ```
- **Error Codes:** `400 Bad Request` (invalid type or coordinates), `409 Conflict` (existing active emergency ongoing)

### `GET /api/emergency/<int:alert_id>`
Retrieves incident overview, breadcrumb trails, and assigned police station.
- **Authentication:** Required (User owns alert or has ADMIN role)
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Alert retrieved successfully",
    "data": {
      "id": 1,
      "status": "ACTIVE",
      "breadcrumbs": [
        {"latitude": 28.6315, "longitude": 77.2167, "accuracy": 12.5, "timestamp": "2026-09-22T10:00:00Z"},
        {"latitude": 28.6318, "longitude": 77.2170, "accuracy": 10.0, "timestamp": "2026-09-22T10:00:15Z"}
      ]
    }
  }
  ```

### `POST /api/emergency/<int:alert_id>/location`
Ingests periodic live GPS breadcrumb during an active emergency.
- **Request Body:**
  ```json
  {
    "latitude": 28.6319,
    "longitude": 77.2172,
    "accuracy": 8.0
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Location recorded successfully",
    "data": {
      "alert_id": 1,
      "latitude": 28.6319,
      "longitude": 77.2172,
      "accuracy": 8.0,
      "timestamp": "2026-09-22T10:00:25Z"
    }
  }
  ```
- **Error Codes:** `400 Bad Request` (Coordinates invalid or alert is already RESOLVED)

### `POST /api/emergency/<int:alert_id>/resolve`
Marks an alert as `RESOLVED`. Halts live tracking.
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Emergency alert marked as resolved",
    "data": {"id": 1, "status": "RESOLVED"}
  }
  ```

### `POST /api/emergency/<int:alert_id>/false-alarm`
Marks an alert as `FALSE_ALARM`.
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Emergency alert marked as false alarm",
    "data": {"id": 1, "status": "FALSE_ALARM"}
  }
  ```

---

## 3. Emergency Contacts APIs

### `GET /api/contacts`
Lists all contacts registered for the authenticated citizen.
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Contacts retrieved",
    "data": [
      {
        "id": 1,
        "name": "Rajesh Kumar (Father)",
        "relationship": "Father",
        "phone": "+91 9876500001",
        "email": "father.demo@example.com",
        "priority": 1,
        "is_active": true
      }
    ]
  }
  ```

### `POST /api/contacts`
Creates an emergency contact.
- **Request Body:**
  ```json
  {
    "name": "Sunita Devi",
    "relationship": "Mother",
    "phone": "+91 9876500002",
    "email": "mother@example.com",
    "priority": 2
  }
  ```
- **Response (201 Created)**

### `PUT /api/contacts/<int:id>`
Updates existing contact information.

### `DELETE /api/contacts/<int:id>`
Removes contact from user's emergency directory.

---

## 4. Police Station & Helpline APIs

### `GET /api/police-stations`
Returns all registered police stations.

### `GET /api/police-stations/nearest?lat={lat}&lon={lon}`
Computes the closest station to the specified coordinate point using Haversine formula.
- **Parameters:** `lat` (decimal degree), `lon` (decimal degree)
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Nearest police station calculated",
    "data": {
      "id": 1,
      "station_name": "Connaught Place Police Station (DEMO DATA)",
      "address": "Connaught Circus, Sector 1, Central Delhi",
      "city": "New Delhi",
      "state": "Delhi",
      "latitude": 28.6315,
      "longitude": 77.2167,
      "distance_km": 0.42,
      "formatted_distance": "420 meters",
      "emergency_number": "112",
      "notification_status": "SIMULATED (Demo Mode - No real emergency transmission)"
    }
  }
  ```

### `GET /api/emergency-numbers`
Returns active civil emergency response numbers (112, 100, 1091, 108, 101, 1033).
