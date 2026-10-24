#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Stop all running services for the Poultry Farm Management System
#>

Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "🛑 STOPPING ALL SERVICES" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Yellow

# Get all running jobs
$jobs = Get-Job

if ($jobs.Count -eq 0) {
    Write-Host "ℹ️  No background services found" -ForegroundColor Cyan
} else {
    Write-Host "Found $($jobs.Count) running service(s)...`n" -ForegroundColor White
    
    foreach ($job in $jobs) {
        Write-Host "Stopping: $($job.Name) (ID: $($job.Id))..." -ForegroundColor Gray
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ Stopped" -ForegroundColor Green
    }
}

# Also kill any processes on the ports
Write-Host "`n🔍 Checking for processes on ports..." -ForegroundColor White

$ports = @(3000, 5000, 8081)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
                Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($process) {
        Write-Host "Found process on port $port (PID: $process)" -ForegroundColor Gray
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ Killed process on port $port" -ForegroundColor Green
    }
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "✅ ALL SERVICES STOPPED" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green
