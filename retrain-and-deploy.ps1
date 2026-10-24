# QUICK RETRAIN AND DEPLOY
# Automates the entire retraining process

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🔄 AUTOMATED MODEL RETRAINING" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Retrain the feed consumption model (15-30 min)"
Write-Host "  2. Deploy the improved model"
Write-Host "  3. Restart all services"
Write-Host ""

# Confirm
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Red
    exit
}

# Navigate to data_anaysis folder
cd D:\Research\data_anaysis

Write-Host "`n🚀 Step 1: Starting Model Retraining..." -ForegroundColor Cyan
Write-Host "   This will take 15-30 minutes. Please wait..." -ForegroundColor Yellow
Write-Host ""

# Run retraining script (memory-efficient version)
& D:\Research\.venv\Scripts\python.exe retrain_feed_model_memory_efficient.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Training failed! Check error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Training completed successfully!" -ForegroundColor Green
Start-Sleep -Seconds 2

# Deploy model
Write-Host "`n🚀 Step 2: Deploying Improved Model..." -ForegroundColor Cyan
& D:\Research\.venv\Scripts\python.exe deploy_improved_model.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Deployment failed! Check error messages above." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Deployment completed!" -ForegroundColor Green
Start-Sleep -Seconds 2

# Restart services
Write-Host "`n🚀 Step 3: Restarting Services..." -ForegroundColor Cyan

# Stop existing processes
Write-Host "   Stopping existing services..." -ForegroundColor Yellow
Get-Process -Name python,node -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq '' } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

Write-Host "   ✅ Stopped old processes" -ForegroundColor Green

# Start ML service in background
Write-Host "`n   Starting ML Service (Port 5000)..." -ForegroundColor Cyan
cd D:\Research\Integrated-Farm-System-Backend\ml_service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'D:\Research\.venv\Scripts\Activate.ps1'; python app.py"
Start-Sleep -Seconds 5

# Start Backend in background
Write-Host "   Starting Backend (Port 3000)..." -ForegroundColor Cyan
cd D:\Research\Integrated-Farm-System-Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "node server.js"
Start-Sleep -Seconds 5

# Start Frontend in background
Write-Host "   Starting Frontend (Port 8081)..." -ForegroundColor Cyan
cd D:\Research\Integrated-Farm-System-Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx expo start"

Write-Host "`n✅ All services started!" -ForegroundColor Green
Start-Sleep -Seconds 2

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ RETRAINING COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📊 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Wait for all services to fully start (~30 seconds)"
Write-Host "   2. Open your browser: http://localhost:8081"
Write-Host "   3. Test feed consumption predictions:"
Write-Host "      - Try 25_percent images (should show ~75% consumption)"
Write-Host "      - Try 50_percent images (should show ~50% consumption)"
Write-Host "      - Check confidence levels (should be >60%)"
Write-Host ""
Write-Host "📈 Expected Improvements:" -ForegroundColor Yellow
Write-Host "   • 25% accuracy: Was 0-70% → Now >80%"
Write-Host "   • 50% accuracy: Was 30-50% → Now >80%"
Write-Host "   • Better confidence scores overall"
Write-Host "   • Fewer false 100% predictions"
Write-Host ""
Write-Host "📄 Full report saved to:" -ForegroundColor Yellow
Write-Host "   data_anaysis/models/resnet50/training_results_improved.png"
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
