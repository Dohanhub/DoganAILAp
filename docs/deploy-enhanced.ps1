# Enhanced Database Architecture Deployment Script
param([switch]$SkipMigration = $false)

Write-Host "🚀 Deploying Enhanced Database Architecture..." -ForegroundColor Cyan

# Stop existing services
Write-Host "Stopping existing services..." -ForegroundColor Yellow
docker-compose down --remove-orphans 2>$null

# Start enhanced services
Write-Host "Starting enhanced database services..." -ForegroundColor Yellow
docker-compose -f docker-compose.enhanced.yml up -d

# Wait for services
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Run migration if not skipped
if (-not $SkipMigration) {
    Write-Host "Running data migration..." -ForegroundColor Yellow
    python scripts/migrate_to_enhanced_architecture.py
}

Write-Host "✅ Enhanced architecture deployed successfully!" -ForegroundColor Green
Write-Host "📊 API: http://localhost:8000" -ForegroundColor Green
Write-Host "📈 Grafana: http://localhost:3000" -ForegroundColor Green
