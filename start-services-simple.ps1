# Simple script to start all services for Poultry Farm Management System
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  POULTRY FARM MANAGEMENT SYSTEM - STARTUP" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Base directory
$BASE = "D:\Research"

# 1. Start MongoDB
Write-Host "[1/4] Starting MongoDB..." -ForegroundColor Yellow
$mongoRunning = Get-Process mongod -ErrorAction SilentlyContinue
if ($mongoRunning) {
    Write-Host "      MongoDB already running (PID: $($mongoRunning.Id))" -ForegroundColor Green
} else {
    Start-Process -NoNewWindow -FilePath "mongod" -ArgumentList "--dbpath=C:\data\db", "--port=27017"
    Start-Sleep -Seconds 3
    Write-Host "      MongoDB started on port 27017" -ForegroundColor Green
}

# 2. Start ML Service (Python)
Write-Host "[2/4] Starting ML Service (Port 5000)..." -ForegroundColor Yellow
$mlRunning = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($mlRunning) {
    Write-Host "      ML Service already running on port 5000" -ForegroundColor Green
} else {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$BASE\Integrated-Farm-System-Backend\ml_service'; & '$BASE\.venv\Scripts\python.exe' app.py"
    Start-Sleep -Seconds 5
    Write-Host "      ML Service started on port 5000" -ForegroundColor Green
}

# 3. Start Backend API (Node.js)
Write-Host "[3/4] Starting Backend API (Port 3000)..." -ForegroundColor Yellow
$backendRunning = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($backendRunning) {
    Write-Host "      Backend already running on port 3000" -ForegroundColor Green
} else {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$BASE\Integrated-Farm-System-Backend'; node server.js"
    Start-Sleep -Seconds 3
    Write-Host "      Backend API started on port 3000" -ForegroundColor Green
}

# 4. Start Frontend (Expo)
Write-Host "[4/4] Starting Frontend (Port 8081)..." -ForegroundColor Yellow
$frontendRunning = Get-NetTCPConnection -LocalPort 8081 -State Listen -ErrorAction SilentlyContinue
if ($frontendRunning) {
    Write-Host "      Frontend already running on port 8081" -ForegroundColor Green
} else {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$BASE\Integrated-Farm-System-Frontend'; npm start"
    Start-Sleep -Seconds 5
    Write-Host "      Frontend started on port 8081" -ForegroundColor Green
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Frontend:    http://localhost:8081" -ForegroundColor White
Write-Host "  Backend:     http://localhost:3000" -ForegroundColor White
Write-Host "  ML Service:  http://localhost:5000/api/health" -ForegroundColor White
Write-Host "  MongoDB:     localhost:27017" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: .\stop-all-services.ps1" -ForegroundColor Cyan
