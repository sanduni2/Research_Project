@echo off
echo ============================================================
echo  Integrated Farm System - Installation Script
echo ============================================================
echo.

echo [1/4] Installing Backend Dependencies...
cd Integrated-Farm-System-Backend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Backend installation failed!
    pause
    exit /b 1
)
echo Backend dependencies installed successfully!
echo.

echo [2/4] Installing ML Service Dependencies...
cd ml_service
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: ML Service installation failed!
    pause
    exit /b 1
)
cd ..
echo ML Service dependencies installed successfully!
echo.

echo [3/4] Installing Frontend Dependencies...
cd ..\Integrated-Farm-System-Frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Frontend installation failed!
    pause
    exit /b 1
)
echo Frontend dependencies installed successfully!
echo.

echo [4/4] Checking MongoDB...
where mongod >nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is installed!
) else (
    echo WARNING: MongoDB not found in PATH
    echo Please install MongoDB from: https://www.mongodb.com/try/download/community
)
echo.

echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo Next Steps:
echo 1. Start MongoDB (if not running as service)
echo 2. Open 3 terminals and run:
echo.
echo    Terminal 1: cd Integrated-Farm-System-Backend\ml_service
echo                python app.py
echo.
echo    Terminal 2: cd Integrated-Farm-System-Backend
echo                npm start
echo.
echo    Terminal 3: cd Integrated-Farm-System-Frontend
echo                npm start
echo.
echo For detailed instructions, see QUICKSTART.md
echo.
pause
