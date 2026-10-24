# Integrated Farm System - Installation Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Integrated Farm System - Installation Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[Check] Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "  Node.js $nodeVersion installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "  Please install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Python
Write-Host "[Check] Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "  $pythonVersion installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please install from: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check MongoDB
Write-Host "[Check] MongoDB..." -ForegroundColor Yellow
if (Get-Command mongod -ErrorAction SilentlyContinue) {
    $mongoVersion = mongod --version | Select-String "db version"
    Write-Host "  MongoDB installed" -ForegroundColor Green
} else {
    Write-Host "  WARNING: MongoDB not found in PATH" -ForegroundColor Yellow
    Write-Host "  Please install from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Installing Dependencies" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Install Backend
Write-Host "[1/3] Installing Backend Dependencies..." -ForegroundColor Yellow
Set-Location -Path "Integrated-Farm-System-Backend"
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Backend installation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Backend dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Install ML Service
Write-Host "[2/3] Installing ML Service Dependencies..." -ForegroundColor Yellow
Set-Location -Path "ml_service"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: ML Service installation failed!" -ForegroundColor Red
    exit 1
}
Set-Location -Path ".."
Write-Host "  ML Service dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Install Frontend
Write-Host "[3/3] Installing Frontend Dependencies..." -ForegroundColor Yellow
Set-Location -Path "..\Integrated-Farm-System-Frontend"
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Frontend installation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Frontend dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Go back to root
Set-Location -Path ".."

Write-Host "============================================================" -ForegroundColor Green
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start MongoDB (if not running as service)" -ForegroundColor White
Write-Host "2. Open 3 PowerShell terminals and run:" -ForegroundColor White
Write-Host ""
Write-Host "   Terminal 1: " -ForegroundColor Yellow -NoNewline
Write-Host "cd Integrated-Farm-System-Backend\ml_service" -ForegroundColor White
Write-Host "               python app.py" -ForegroundColor White
Write-Host ""
Write-Host "   Terminal 2: " -ForegroundColor Yellow -NoNewline
Write-Host "cd Integrated-Farm-System-Backend" -ForegroundColor White
Write-Host "               npm start" -ForegroundColor White
Write-Host ""
Write-Host "   Terminal 3: " -ForegroundColor Yellow -NoNewline
Write-Host "cd Integrated-Farm-System-Frontend" -ForegroundColor White
Write-Host "               npm start" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
