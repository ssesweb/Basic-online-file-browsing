@echo off
set FLASK_ENV=production
start "Backend Server (Prod Mode)" cmd /k "cd app && python app.py"