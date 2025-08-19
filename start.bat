@echo off
echo Starting Flask and Huey services...


REM UV Environment Setup
uv sync --frozen

REM Set environment variables for Flask
set FLASK_APP=app\app.py
set FLASK_DEBUG=1

REM Start Flask in a new window
echo Starting Flask application...
start "Flask App" cmd /k "uv run flask run --no-debugger --no-reload"

REM Wait a moment before starting Huey
timeout /t 2 /nobreak > nul

REM Start Huey consumer in a new window
echo Starting Huey consumer...
start "Huey Consumer" cmd /k "uv run huey_consumer huey_config.huey --workers=2 --verbose"

echo Both services started in separate windows.
echo Press any key to exit this script (services will continue running)...
pause > nul
