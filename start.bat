@echo off
echo [SYSTEM] Launching Rocket Telemetry Dashboard...

REM Go to project root (assuming start.bat is in the root folder)
cd /d "%~dp0"

REM Optional: activate venv (uncomment if needed)
call venv\Scripts\activate

REM Launch dashboard via main.py
python backend\main.py

pause