# Stop all services
Write-Host "====================================================" -ForegroundColor Red
Write-Host "  STOPPING ALL SERVICES" -ForegroundColor Red
Write-Host "====================================================" -ForegroundColor Red
Write-Host ""

# Stop Node processes (Frontend + Backend)
Write-Host "[1/4] Stopping Node.js processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "      Node.js processes stopped" -ForegroundColor Green

# Stop Python processes (ML Service)
Write-Host "[2/4] Stopping Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Research*"} | Stop-Process -Force
Write-Host "      Python processes stopped" -ForegroundColor Green

# Stop MongoDB
Write-Host "[3/4] Stopping MongoDB..." -ForegroundColor Yellow
Get-Process mongod -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "      MongoDB stopped" -ForegroundColor Green

# Stop PowerShell jobs
Write-Host "[4/4] Cleaning up background jobs..." -ForegroundColor Yellow
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue
Write-Host "      Background jobs cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host "  ALL SERVICES STOPPED!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
