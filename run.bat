@echo off
REM One-click start for Windows (double-click or run in VS Code terminal)
cd /d "%~dp0"
if not exist venv ( python -m venv venv )
call venv\Scripts\activate
pip install -r requirements.txt
if not exist .env copy .env.example .env
python app.py
pause
