@echo off
cd /d "%~dp0"
title Felicia Misenheimer - LifeStraw Business Systems Command Center
where py >nul 2>nul
if %errorlevel%==0 (set PYTHON=py) else (set PYTHON=python)
%PYTHON% --version
if errorlevel 1 (
 echo Python was not found. Install Python 3 and select Add Python to PATH.
 pause
 exit /b 1
)
%PYTHON% -c "import flask" >nul 2>nul
if errorlevel 1 %PYTHON% -m pip install -r requirements.txt
echo Starting demo at http://127.0.0.1:8000
start "" http://127.0.0.1:8000
%PYTHON% app.py
pause
