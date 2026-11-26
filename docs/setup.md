# BLUE LINE – Windows Installation & Execution Guide

This document provides step-by-step setup instructions for running **BLUE LINE** on a Windows workstation using PowerShell, Command Prompt, or VS Code.

---

## 1. System Requirements

* **Operating System:** Windows 10 or Windows 11 (64-bit)
* **Python Runtime:** Python 3.11, 3.12, 3.13, or 3.14
* **Browser:** Google Chrome or Microsoft Edge (recommended for Web Speech API and Geolocation support)
* **Terminal:** PowerShell or Windows Command Prompt

---

## 2. Step-by-Step Installation

### Step 1: Open PowerShell as Administrator or Normal User
Open Windows PowerShell and navigate to the project directory:
```powershell
cd C:\Users\srk\Desktop\blue_line
```

### Step 2: Create a Python Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
If PowerShell restricts script execution, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```
*(In Command Prompt `cmd.exe`, simply run `.\venv\Scripts\activate.bat`)*

### Step 4: Install Project Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Ensure `.env` exists in the project root:
```powershell
Copy-Item .env.example .env
```
*(The default `.env` is pre-configured with `DEMO_MODE=true` and local SQLite storage).*

### Step 6: Initialize & Seed Database
Seed the application with demo administrators, users, emergency contacts, verified police stations, and helplines:
```powershell
.\venv\Scripts\python.exe database/seed_data.py
```
**Expected Output:**
```
[Seed] Created Administrator: admin@blueline.local
[Seed] Created Demo User: demo@example.com
[Seed] Added 3 demo emergency contacts for demo@example.com
[Seed] Added 5 verified police station records (DEMO)
[Seed] Added 6 emergency helpline numbers
[Seed] Database seeding completed successfully.
```

### Step 7: Run the Test Suite
Verify that all system tests pass:
```powershell
.\venv\Scripts\python.exe -m pytest -v
```
**Expected Output:** `16 passed in X.XXs`

### Step 8: Launch the Blue Line Server
```powershell
.\venv\Scripts\python.exe app.py
```
The server will start at:
👉 **`http://127.0.0.1:5000`**

---

## 3. Pre-Configured Demo Accounts for Evaluation

| Role | Email | Password | Dashboard Features |
|---|---|---|---|
| **System Admin** | `admin@blueline.local` | `Admin@12345` | Real-time emergency tactical map, incident audits, station management, user controls |
| **Demo Citizen** | `demo@example.com` | `Demo@12345` | Panic SOS button, phone shake detection, voice triggers, live GPS streaming, contacts |

---

## 4. Troubleshooting Guide

### 1. `execution of scripts is disabled on this system` (PowerShell Policy)
Run this command in your active PowerShell window to permit virtual environment activation for that session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. `Address already in use: Port 5000`
If port 5000 is occupied by another application, find and terminate the process:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```
Or start Flask on port 5050 in `app.py`: `app.run(port=5050, debug=True)`.

### 3. Geolocation Permission Denied in Browser
When the browser prompts for location access, click **"Allow"**. If blocked:
1. Click the site settings lock icon next to `http://127.0.0.1:5000` in the URL bar.
2. Toggle **Location** from *Block* to *Allow*.
3. Refresh the page.

### 4. Voice Trigger ("HELP") not responding
* The Web Speech API is supported natively on **Google Chrome** and **Microsoft Edge**.
* Ensure microphone permissions are allowed.
* Alternatively, use the convenient **"Simulate Voice 'HELP' (Demo Viva)"** button on the dashboard for instant demonstration!
