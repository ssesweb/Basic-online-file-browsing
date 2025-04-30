@echo off
call init_check.bat || exit /b
set FLASK_ENV=production
start "Backend Server (Prod Mode)" cmd /k "cd app && python app.py"