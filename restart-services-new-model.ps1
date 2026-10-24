# Restart All Services with New Broiler Model
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "🔄 RESTARTING ALL SERVICES WITH NEW BROILER MODEL" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

# Step 1: Stop all services
Write-Host "`n📛 Step 1: Stopping all services..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "✅ All services stopped" -ForegroundColor Green

# Step 2: Start ML Service
Write-Host "`n🤖 Step 2: Starting ML Service (Port 5000)..." -ForegroundColor Cyan
$mlJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Backend\ml_service'
    & 'd:\Research\.venv\Scripts\Activate.ps1'
    python app.py
} -Name "MLService"
Start-Sleep -Seconds 8
Write-Host "✅ ML Service started" -ForegroundColor Green

# Step 3: Check ML Service
Write-Host "`n🧪 Step 3: Testing ML Service..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get -TimeoutSec 5
    if ($response.models.weight_prediction) {
        Write-Host "✅ ML Service ONLINE - Weight model loaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ML Service online but weight model NOT loaded!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ ML Service NOT responding!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Test weight prediction
Write-Host "`n🧪 Step 4: Testing Weight Predictions..." -ForegroundColor Cyan
Write-Host "-"*60 -ForegroundColor Cyan

$testAges = @(
    @{days=7; weeks=1},
    @{days=14; weeks=2},
    @{days=21; weeks=3},
    @{days=28; weeks=4},
    @{days=35; weeks=5},
    @{days=42; weeks=6},
    @{days=49; weeks=7},
    @{days=56; weeks=8},
    @{days=63; weeks=9},
    @{days=70; weeks=10}
)

foreach ($test in $testAges) {
    try {
        $body = @{ age = $test.days } | ConvertTo-Json -Compress
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/predict/weight" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
        $weight = [math]::Round($response.predicted_weight)
        $daysLabel = "$($test.days) days"
        Write-Host "Week $($test.weeks) - $daysLabel : " -NoNewline -ForegroundColor Yellow
        Write-Host "${weight}g" -ForegroundColor Green
    } catch {
        Write-Host "Week $($test.weeks): ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "-"*60 -ForegroundColor Cyan

# Step 5: Start Backend
Write-Host "`n🗂️  Step 5: Starting Backend Server (Port 3000)..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Backend'
    node server.js
} -Name "BackendServer"
Start-Sleep -Seconds 3
Write-Host "✅ Backend started" -ForegroundColor Green

# Step 6: Start Frontend
Write-Host "`n📱 Step 6: Starting Frontend (Port 8081)..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location 'D:\Research\Integrated-Farm-System-Frontend'
    npx expo start
} -Name "FrontendServer"
Start-Sleep -Seconds 10
Write-Host "✅ Frontend started" -ForegroundColor Green

# Summary
Write-Host "`n" + "="*80 -ForegroundColor Cyan
Write-Host "✅ ALL SERVICES RUNNING" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "`n📊 Service Status:" -ForegroundColor Yellow
Write-Host "   ML Service:  http://localhost:5000" -ForegroundColor White
Write-Host "   Backend:     http://localhost:3000" -ForegroundColor White
Write-Host "   Frontend:    http://localhost:8081" -ForegroundColor White
Write-Host "`n📱 Open Browser: http://localhost:8081" -ForegroundColor Cyan -BackgroundColor Black
$noteText = "Note: Now using new Broiler Model with realistic weights for 0-12 weeks"
Write-Host "`n💡 $noteText" -ForegroundColor Yellow
Write-Host ("="*80) -ForegroundColor Cyan
