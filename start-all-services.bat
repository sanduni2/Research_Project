@echo off
REM Simple batch file to run the PowerShell script

echo Starting all services...
powershell -ExecutionPolicy Bypass -File "%~dp0start-all-services.ps1"
pause
