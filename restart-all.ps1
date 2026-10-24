# Restart All Services
$line = "-" * 80

Write-Host $line -ForegroundColor Cyan
Write-Host "RESTARTING ALL SERVICES" -ForegroundColor Green
Write-Host $line -ForegroundColor Cyan

# Stop all
Write-Host "`nStopping all services..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "Services stopped" -ForegroundColor Green

# Start ML Service
Write-Host "`nStarting ML Service..." -ForegroundColor Cyan
$mlJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Backend\ml_service'
    & 'd:\Research\.venv\Scripts\Activate.ps1'
    python app.py
} -Name "MLService"
Start-Sleep -Seconds 8

# Test ML Service
Write-Host "Testing ML Service..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get -TimeoutSec 5
    if ($response.models.weight_prediction) {
        Write-Host "ML Service ONLINE - Weight model loaded" -ForegroundColor Green
    }
} catch {
    Write-Host "ML Service ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test predictions
Write-Host "`nTesting Predictions:" -ForegroundColor Cyan
$testWeeks = @(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
foreach ($week in $testWeeks) {
    $days = $week * 7
    try {
        $body = "{`"age`":$days}"
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/predict/weight" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
        $weight = [math]::Round($response.predicted_weight)
        Write-Host "  Week $week : ${weight}g" -ForegroundColor Green
    } catch {
        Write-Host "  Week $week : ERROR" -ForegroundColor Red
    }
}
Write-Host $line -ForegroundColor Cyan

# Start Backend
Write-Host "`nStarting Backend..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Backend'
    node server.js
} -Name "BackendServer"
Start-Sleep -Seconds 3
Write-Host "Backend started" -ForegroundColor Green

# Start Frontend
Write-Host "`nStarting Frontend..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Frontend'
    npx expo start
} -Name "FrontendServer"
Start-Sleep -Seconds 10
Write-Host "Frontend started" -ForegroundColor Green

Write-Host "`n$line" -ForegroundColor Cyan
Write-Host "ALL SERVICES RUNNING" -ForegroundColor Green
Write-Host "ML Service:  http://localhost:5000" -ForegroundColor White
Write-Host "Backend:     http://localhost:3000" -ForegroundColor White
Write-Host "Frontend:    http://localhost:8081" -ForegroundColor White
Write-Host $line -ForegroundColor Cyan
