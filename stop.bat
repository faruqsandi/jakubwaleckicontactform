@echo off
echo Stopping Flask and Huey services...

REM Kill Flask processes (typically runs on port 5000)
echo Stopping Flask application...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Killing process ID: %%a
    taskkill /f /pid %%a 2>nul
)

REM Also kill Flask by window title
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq Flask App*" 2>nul
taskkill /f /im "cmd.exe" /fi "WINDOWTITLE eq Flask App*" 2>nul

REM Kill Huey consumer processes
echo Stopping Huey consumer...
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq Huey Consumer*" 2>nul
taskkill /f /im "cmd.exe" /fi "WINDOWTITLE eq Huey Consumer*" 2>nul

REM Alternative method: Kill by process name pattern
wmic process where "CommandLine like '%%huey_consumer%%'" delete 2>nul

echo Services stopped.
pause
