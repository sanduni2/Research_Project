#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start all services for the Poultry Farm Management System
.DESCRIPTION
    This script starts:
    1. ML Flask Service (Port 5000)
    2. Backend Node.js API (Port 3000)
    3. Frontend React Native Expo
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING POULTRY FARM MANAGEMENT SYSTEM" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Store PIDs for cleanup
$global:ServicePIDs = @{}

# Function to start a service
function Start-Service-InBackground {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDir,
        [int]$Port
    )
    
    Write-Host "[$Name] Starting on port $Port..." -ForegroundColor Yellow
    
    $job = Start-Job -ScriptBlock {
        param($dir, $cmd)
        Set-Location $dir
        Invoke-Expression $cmd
    } -ArgumentList $WorkingDir, $Command
    
    $global:ServicePIDs[$Name] = $job.Id
    
    Start-Sleep -Seconds 2
    Write-Host "[$Name] ✅ Started (Job ID: $($job.Id))" -ForegroundColor Green
}

# 1. Start ML Flask Service
Write-Host "`n1️⃣  ML SERVICE (Python Flask)" -ForegroundColor Cyan
Write-Host "   └─ Port: 5000" -ForegroundColor Gray
Start-Service-InBackground `
    -Name "ML-Service" `
    -Command "C:/Users/Sanduni/Desktop/Research/.venv/Scripts/python.exe app.py" `
    -WorkingDir "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Backend\ml_service" `
    -Port 5000

Start-Sleep -Seconds 8

# 2. Start Backend API
Write-Host "`n2️⃣  BACKEND API (Node.js + Express)" -ForegroundColor Cyan
Write-Host "   └─ Port: 3000" -ForegroundColor Gray
Start-Service-InBackground `
    -Name "Backend-API" `
    -Command "node server.js" `
    -WorkingDir "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Backend" `
    -Port 3000

Start-Sleep -Seconds 3

# 3. Start Frontend
Write-Host "`n3️⃣  FRONTEND (React Native + Expo)" -ForegroundColor Cyan
Write-Host "   └─ Port: 8081" -ForegroundColor Gray
Start-Service-InBackground `
    -Name "Frontend-Expo" `
    -Command "npm start" `
    -WorkingDir "C:\Users\Sanduni\Desktop\Research\Integrated-Farm-System-Frontend" `
    -Port 8081

Start-Sleep -Seconds 5

# Check services status
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📊 SERVICE STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

foreach ($service in $global:ServicePIDs.Keys) {
    $job = Get-Job -Id $global:ServicePIDs[$service] -ErrorAction SilentlyContinue
    if ($job -and $job.State -eq "Running") {
        Write-Host "✅ $service : Running (Job ID: $($job.Id))" -ForegroundColor Green
    } else {
        Write-Host "❌ $service : Failed" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎯 ACCESS POINTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ML Service:    http://localhost:5000/api/health" -ForegroundColor White
Write-Host "Backend API:   http://localhost:3000/api/flocks" -ForegroundColor White
Write-Host "Frontend:      http://localhost:8081" -ForegroundColor White
Write-Host "Expo Mobile:   exp://192.168.8.148:8081" -ForegroundColor White

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📱 MOBILE APP TESTING" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Install 'Expo Go' app on your phone" -ForegroundColor White
Write-Host "2. Scan the QR code that appears in the Expo window" -ForegroundColor White
Write-Host "3. Or press 'a' in Expo terminal for Android emulator" -ForegroundColor White

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🛑 TO STOP ALL SERVICES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Run this command:" -ForegroundColor White
Write-Host "  .\stop-all-services.ps1" -ForegroundColor Yellow
Write-Host "`nOr manually:" -ForegroundColor White
Write-Host "  Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n💡 TIP: Keep this PowerShell window open to see service logs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop all services`n" -ForegroundColor Yellow

# Keep script running and show logs
Write-Host "`n📋 SERVICE LOGS (Press Ctrl+C to exit):" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

try {
    while ($true) {
        foreach ($service in $global:ServicePIDs.Keys) {
            $job = Get-Job -Id $global:ServicePIDs[$service] -ErrorAction SilentlyContinue
            if ($job) {
                $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
                if ($output) {
                    Write-Host "[$service] $output" -ForegroundColor Gray
                }
            }
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host "`n`n🛑 Stopping all services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "✅ All services stopped" -ForegroundColor Green
}
