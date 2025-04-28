@echo off
call init_check.bat || exit /b
start "Backend Server" cmd /k "cd app && python app.py"