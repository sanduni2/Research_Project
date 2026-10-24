# Simple Start Script - All Services
# Run this to start ML Service, Backend API, and Frontend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STARTING POULTRY FARM MANAGEMENT SYSTEM" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start ML Service (Flask)
Write-Host "[1/3] Starting ML Service (Port 5000)..." -ForegroundColor Yellow
$mlJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Backend\ml_service"
    & "C:/Users/Sanduni/Desktop/Research/.venv/Scripts/python.exe" "app.py"
}
Write-Host "      ML Service started (Job ID: $($mlJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 10

# 2. Start Backend API (Node.js)
Write-Host "[2/3] Starting Backend API (Port 3000)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Backend"
    & node "server.js"
}
Write-Host "      Backend API started (Job ID: $($backendJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 4

# 3. Start Frontend (Expo)
Write-Host "[3/3] Starting Frontend (Port 8081)..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Frontend"
    & npm "start"
}
Write-Host "      Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 5

# Check Status
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SERVICE STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$jobs = Get-Job
foreach ($job in $jobs) {
    if ($job.State -eq "Running") {
        Write-Host "[OK] Job $($job.Id): $($job.State)" -ForegroundColor Green
    } else {
        Write-Host "[!!] Job $($job.Id): $($job.State)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ACCESS URLS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ML Service:  http://localhost:5000/api/health" -ForegroundColor White
Write-Host "Backend API: http://localhost:3000/api/flocks" -ForegroundColor White
Write-Host "Frontend:    http://localhost:8081" -ForegroundColor White
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To stop all services, run: .\stop-all-services.ps1" -ForegroundColor Yellow
Write-Host "Or press Ctrl+C and run: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow
Write-Host ""
Write-Host "Showing live logs (Press Ctrl+C to exit)..." -ForegroundColor Cyan
Write-Host ""

# Show logs
try {
    while ($true) {
        $jobs = Get-Job
        foreach ($job in $jobs) {
            $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
            if ($output) {
                Write-Host "[Job $($job.Id)] $output" -ForegroundColor Gray
            }
        }
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "All services stopped." -ForegroundColor Green
}
