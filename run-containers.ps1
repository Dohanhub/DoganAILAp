#!/usr/bin/env pwsh
# DoganAI Compliance Kit - Container Development Environment

Write-Host "Building and running DoganAI Compliance Kit in containers..." -ForegroundColor Green
Write-Host ""

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

# Build and start containers
Write-Host "Building containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml build

Write-Host "Starting containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml up -d

Write-Host ""
Write-Host "Containers are starting..." -ForegroundColor Green
Write-Host "Frontend UI: http://localhost:3001" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Database: localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Gray
Write-Host "  Stop containers: docker-compose -f docker-compose.dev.yml down" -ForegroundColor Gray
Write-Host "  Rebuild: docker-compose -f docker-compose.dev.yml build --no-cache" -ForegroundColor Gray
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$backendHealth = try { 
    Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    "OK"
} catch { "Failed" }

$frontendHealth = try {
    Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 5 | Out-Null
    "OK"
} catch { "Failed" }

Write-Host "Service Status:" -ForegroundColor Green
Write-Host "  Backend: $backendHealth" -ForegroundColor $(if($backendHealth -eq "OK") {"Green"} else {"Red"})
Write-Host "  Frontend: $frontendHealth" -ForegroundColor $(if($frontendHealth -eq "OK") {"Green"} else {"Red"})

if ($backendHealth -eq "OK" -and $frontendHealth -eq "OK") {
    Write-Host ""
    Write-Host "All services are ready! Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost:3001"
} else {
    Write-Host ""
    Write-Host "Some services may still be starting. Check logs if needed." -ForegroundColor Yellow
}
