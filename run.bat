@echo off
title SIOTDA - Secure IoT Device Authentication
echo Starting SIOTDA Server...
cd /d "%~dp0Backend"
python app.py
pause
