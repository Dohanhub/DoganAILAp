# Local Deployment Script for DoganAI Compliance Kit
# Run this script in PowerShell to deploy locally for testing

param(
    [switch]$SkipDatabase,
    [switch]$SkipRedis,
    [switch]$SkipMonitoring,
    [switch]$CreateDesktopIcon
)

Write-Host "🚀 DoganAI Compliance Kit - Local Deployment" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Check if ports are available
$ports = @(8000, 8001, 8002, 8003, 8501, 5432, 6379, 9090, 3000)
$occupiedPorts = @()

foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            $occupiedPorts += $port
        }
    } catch {
        # Port check failed, assume it's available
    }
}

if ($occupiedPorts.Count -gt 0) {
    Write-Host "⚠️  Warning: Some ports are already in use: $($occupiedPorts -join ', ')" -ForegroundColor Yellow
    Write-Host "   You may need to stop other services using these ports." -ForegroundColor Yellow
}

# Create .env.local if it doesn't exist
if (-not (Test-Path ".env.local")) {
    Write-Host "`n📝 Creating .env.local from template..." -ForegroundColor Yellow
    Copy-Item "env.local" ".env.local"
    Write-Host "✅ Created .env.local" -ForegroundColor Green
}

# Start database if not skipped
if (-not $SkipDatabase) {
    Write-Host "`n🗄️  Starting PostgreSQL database..." -ForegroundColor Yellow
    
    # Check if PostgreSQL container is already running
    $postgresRunning = docker ps --filter "name=postgres" --format "{{.Names}}" | Select-String "postgres"
    
    if (-not $postgresRunning) {
        docker run -d --name postgres-local `
            -e POSTGRES_DB=doganai_local `
            -e POSTGRES_USER=doganai_user `
            -e POSTGRES_PASSWORD=doganai_password `
            -p 5432:5432 `
            postgres:15-alpine
        
        Write-Host "✅ PostgreSQL started on port 5432" -ForegroundColor Green
        
        # Wait for database to be ready
        Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    } else {
        Write-Host "✅ PostgreSQL already running" -ForegroundColor Green
    }
}

# Start Redis if not skipped
if (-not $SkipRedis) {
    Write-Host "`n🔴 Starting Redis..." -ForegroundColor Yellow
    
    $redisRunning = docker ps --filter "name=redis" --format "{{.Names}}" | Select-String "redis"
    
    if (-not $redisRunning) {
        docker run -d --name redis-local `
            -p 6379:6379 `
            redis:7-alpine
        
        Write-Host "✅ Redis started on port 6379" -ForegroundColor Green
    } else {
        Write-Host "✅ Redis already running" -ForegroundColor Green
    }
}

# Start monitoring if not skipped
if (-not $SkipMonitoring) {
    Write-Host "`n📊 Starting monitoring services..." -ForegroundColor Yellow
    
    # Start Prometheus
    $prometheusRunning = docker ps --filter "name=prometheus" --format "{{.Names}}" | Select-String "prometheus"
    if (-not $prometheusRunning) {
        docker run -d --name prometheus-local `
            -p 9090:9090 `
            -v "${PWD}/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml" `
            prom/prometheus:latest
        
        Write-Host "✅ Prometheus started on port 9090" -ForegroundColor Green
    }
    
    # Start Grafana
    $grafanaRunning = docker ps --filter "name=grafana" --format "{{.Names}}" | Select-String "grafana"
    if (-not $grafanaRunning) {
        docker run -d --name grafana-local `
            -p 3000:3000 `
            -e GF_SECURITY_ADMIN_PASSWORD=admin `
            grafana/grafana:latest
        
        Write-Host "✅ Grafana started on port 3000 (admin/admin)" -ForegroundColor Green
    }
}

# Deploy microservices
Write-Host "`n🚀 Deploying microservices..." -ForegroundColor Yellow

# Change to microservices directory
Push-Location "microservices"

try {
    # Build and start services
    Write-Host "Building and starting services..." -ForegroundColor Yellow
    docker-compose up -d --build
    
    Write-Host "✅ All services deployed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error deploying services: $_" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

# Wait for services to be ready
Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Health check
Write-Host "`n🏥 Performing health checks..." -ForegroundColor Yellow

$services = @(
    @{Name="Compliance Engine"; URL="http://localhost:8000/health"},
    @{Name="Benchmarks"; URL="http://localhost:8001/health"},
    @{Name="AI/ML"; URL="http://localhost:8002/health"},
    @{Name="Integrations"; URL="http://localhost:8003/health"},
    @{Name="UI"; URL="http://localhost:8501"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($service.Name): Healthy" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $($service.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ $($service.Name): Unreachable" -ForegroundColor Red
    }
}

# Create desktop icon if requested
if ($CreateDesktopIcon) {
    Write-Host "`n🖥️  Creating desktop icon..." -ForegroundColor Yellow
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $iconPath = Join-Path $desktopPath "DoganAI Compliance Kit.url"
    
    $iconContent = @"
[InternetShortcut]
URL=http://localhost:8501
IconFile=C:\Windows\System32\SHELL32.dll
IconIndex=1
"@
    
    $iconContent | Out-File -FilePath $iconPath -Encoding ASCII
    Write-Host "✅ Desktop icon created: $iconPath" -ForegroundColor Green
}

# Display access information
Write-Host "`n🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "`n📱 Access Points:" -ForegroundColor Cyan
Write-Host "   • Main UI: http://localhost:8501" -ForegroundColor White
Write-Host "   • Compliance API: http://localhost:8000" -ForegroundColor White
Write-Host "   • Benchmarks: http://localhost:8001" -ForegroundColor White
Write-Host "   • AI/ML: http://localhost:8002" -ForegroundColor White
Write-Host "   • Integrations: http://localhost:8003" -ForegroundColor White
Write-Host "   • Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   • Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White

Write-Host "`n🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "   • View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   • Stop services: docker-compose down" -ForegroundColor White
Write-Host "   • Restart services: docker-compose restart" -ForegroundColor White

Write-Host "`n📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:8501 in your browser" -ForegroundColor White
Write-Host "   2. Test the compliance evaluation features" -ForegroundColor White
Write-Host "   3. Check monitoring dashboards" -ForegroundColor White
Write-Host "   4. Review logs for any issues" -ForegroundColor White

Write-Host "`n🚀 Happy testing!" -ForegroundColor Green
