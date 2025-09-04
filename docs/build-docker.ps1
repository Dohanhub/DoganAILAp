# DoganAI Compliance Kit - Docker Build and Deployment Script
# PowerShell script for building, testing, and deploying containerized application

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "build",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "latest",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$Push = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoBuildCache = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

# =============================================================================
# CONFIGURATION
# =============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Docker configuration
$ImageName = "doganai/compliance-kit"
$ContainerName = "doganai-compliance"
$Registry = "registry.doganai.com"  # Change to your registry

# Build configuration
$BuildDate = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
$VcsRef = ""

# Network and port configuration
$NetworkName = "doganai-network"
$ApiPort = 8000
$MetricsPort = 9090
$PrometheusPort = 9091
$GrafanaPort = 3000
$NginxPort = 80
$NginxSslPort = 443

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Log "Docker detected: $dockerVersion"
            return $true
        }
    }
    catch {
        Write-Log "Docker is not installed or not accessible" "ERROR"
        return $false
    }
    return $false
}

function Test-DockerComposeInstalled {
    try {
        $composeVersion = docker compose version 2>$null
        if ($composeVersion) {
            Write-Log "Docker Compose detected: $composeVersion"
            return $true
        }
    }
    catch {
        Write-Log "Docker Compose is not installed or not accessible" "ERROR"
        return $false
    }
    return $false
}

function Get-GitCommitHash {
    try {
        $gitHash = git rev-parse --short HEAD 2>$null
        if ($gitHash) {
            return $gitHash.Trim()
        }
    }
    catch {
        Write-Log "Git not available, using timestamp for VCS ref" "WARN"
    }
    return (Get-Date -Format "yyyyMMdd-HHmmss")
}

function Test-ContainerHealth {
    param([string]$ContainerName, [int]$TimeoutSeconds = 120)
    
    Write-Log "Checking health of container: $ContainerName"
    
    $elapsed = 0
    $interval = 5
    
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $health = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>$null
            
            if ($health -eq "healthy") {
                Write-Log "Container $ContainerName is healthy" "INFO"
                return $true
            }
            elseif ($health -eq "unhealthy") {
                Write-Log "Container $ContainerName is unhealthy" "ERROR"
                return $false
            }
            else {
                Write-Log "Container $ContainerName health status: $health" "DEBUG"
            }
        }
        catch {
            Write-Log "Error checking container health: $_" "WARN"
        }
        
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        
        if ($Verbose) {
            Write-Log "Health check elapsed: $elapsed/$TimeoutSeconds seconds" "DEBUG"
        }
    }
    
    Write-Log "Container $ContainerName health check timed out" "ERROR"
    return $false
}

# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

function Build-DockerImage {
    Write-Log "Building Docker image: $ImageName:$Version"
    
    # Get VCS reference
    $script:VcsRef = Get-GitCommitHash
    Write-Log "Using VCS reference: $VcsRef"
    
    # Prepare build arguments
    $buildArgs = @(
        "--build-arg", "BUILD_DATE=$BuildDate",
        "--build-arg", "VERSION=$Version",
        "--build-arg", "VCS_REF=$VcsRef"
    )
    
    # Add cache options
    if ($NoBuildCache) {
        $buildArgs += "--no-cache"
        Write-Log "Building without cache" "WARN"
    }
    
    # Add tags
    $buildArgs += @(
        "-t", "$ImageName:$Version",
        "-t", "$ImageName:latest"
    )
    
    if ($Environment -eq "production") {
        $buildArgs += "-t", "$ImageName:prod-$Version"
    }
    
    # Add context
    $buildArgs += "."
    
    try {
        Write-Log "Executing: docker build $($buildArgs -join ' ')"
        & docker build @buildArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker image built successfully" "INFO"
            return $true
        }
        else {
            Write-Log "Docker build failed with exit code: $LASTEXITCODE" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error during Docker build: $_" "ERROR"
        return $false
    }
}

function Test-DockerImage {
    Write-Log "Testing Docker image: $ImageName:$Version"
    
    try {
        # Test image exists
        $imageExists = docker images --format "table {{.Repository}}:{{.Tag}}" | Select-String "$ImageName:$Version"
        if (-not $imageExists) {
            Write-Log "Image $ImageName:$Version not found" "ERROR"
            return $false
        }
        
        # Test image can run
        Write-Log "Testing image startup..."
        $testContainer = "$ContainerName-test"
        
        # Remove existing test container
        docker rm -f $testContainer 2>$null | Out-Null
        
        # Run test container
        docker run -d --name $testContainer `
            -e DATABASE_URL="postgresql://test:test@localhost:5432/test" `
            -e REDIS_URL="redis://localhost:6379/0" `
            -e WAIT_FOR_DEPENDENCIES="false" `
            -e INIT_DATABASE="false" `
            -p 8001:8000 `
            "$ImageName:$Version" 2>$null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to start test container" "ERROR"
            return $false
        }
        
        # Wait for container to start
        Start-Sleep -Seconds 10
        
        # Test health endpoint
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Log "Health endpoint test passed" "INFO"
                $testPassed = $true
            }
            else {
                Write-Log "Health endpoint returned status: $($response.StatusCode)" "ERROR"
                $testPassed = $false
            }
        }
        catch {
            Write-Log "Health endpoint test failed: $_" "ERROR"
            $testPassed = $false
        }
        
        # Cleanup test container
        docker rm -f $testContainer 2>$null | Out-Null
        
        return $testPassed
    }
    catch {
        Write-Log "Error during image testing: $_" "ERROR"
        return $false
    }
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

function Deploy-Application {
    Write-Log "Deploying application stack"
    
    try {
        # Create network if it doesn't exist
        $networkExists = docker network ls --format "{{.Name}}" | Select-String "^$NetworkName$"
        if (-not $networkExists) {
            Write-Log "Creating Docker network: $NetworkName"
            docker network create $NetworkName
        }
        
        # Deploy using Docker Compose
        Write-Log "Starting services with Docker Compose"
        
        $env:BUILD_DATE = $BuildDate
        $env:VERSION = $Version
        $env:VCS_REF = $VcsRef
        
        docker compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Application stack deployed successfully" "INFO"
            
            # Wait for services to be healthy
            Write-Log "Waiting for services to become healthy..."
            
            $services = @("doganai-postgres", "doganai-redis", "doganai-api")
            $allHealthy = $true
            
            foreach ($service in $services) {
                if (-not (Test-ContainerHealth -ContainerName $service -TimeoutSeconds 120)) {
                    Write-Log "Service $service failed health check" "ERROR"
                    $allHealthy = $false
                }
            }
            
            if ($allHealthy) {
                Write-Log "All services are healthy and ready" "INFO"
                Show-ServiceUrls
                return $true
            }
            else {
                Write-Log "Some services failed health checks" "ERROR"
                return $false
            }
        }
        else {
            Write-Log "Docker Compose deployment failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error during deployment: $_" "ERROR"
        return $false
    }
}

function Show-ServiceUrls {
    Write-Log "Service URLs:" "INFO"
    Write-Host ""
    Write-Host "🌐 DoganAI Compliance Kit Services" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════" -ForegroundColor Cyan
    Write-Host "📊 Main API:        http://localhost:$ApiPort" -ForegroundColor Green
    Write-Host "📚 API Docs:        http://localhost:$ApiPort/docs" -ForegroundColor Green
    Write-Host "❤️  Health Check:    http://localhost:$ApiPort/health" -ForegroundColor Green
    Write-Host "📈 Metrics:         http://localhost:$MetricsPort" -ForegroundColor Yellow
    Write-Host "🔍 Prometheus:      http://localhost:$PrometheusPort" -ForegroundColor Yellow
    Write-Host "📊 Grafana:         http://localhost:$GrafanaPort (admin/admin123)" -ForegroundColor Yellow
    Write-Host "🌍 Load Balancer:   http://localhost:$NginxPort" -ForegroundColor Blue
    Write-Host ""
}

function Stop-Application {
    Write-Log "Stopping application stack"
    
    try {
        docker compose down
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Application stack stopped successfully" "INFO"
            return $true
        }
        else {
            Write-Log "Failed to stop application stack" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error stopping application: $_" "ERROR"
        return $false
    }
}

function Remove-Application {
    Write-Log "Removing application stack and volumes"
    
    try {
        docker compose down -v --remove-orphans
        
        # Remove custom network
        $networkExists = docker network ls --format "{{.Name}}" | Select-String "^$NetworkName$"
        if ($networkExists) {
            docker network rm $NetworkName 2>$null | Out-Null
        }
        
        Write-Log "Application stack removed successfully" "INFO"
        return $true
    }
    catch {
        Write-Log "Error removing application: $_" "ERROR"
        return $false
    }
}

function Push-DockerImage {
    if (-not $Push) {
        Write-Log "Skipping image push (use -Push to enable)" "INFO"
        return $true
    }
    
    Write-Log "Pushing Docker image to registry"
    
    try {
        # Tag for registry
        $registryImage = "$Registry/$ImageName:$Version"
        docker tag "$ImageName:$Version" $registryImage
        
        # Push to registry
        docker push $registryImage
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Image pushed successfully to $registryImage" "INFO"
            return $true
        }
        else {
            Write-Log "Failed to push image to registry" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error pushing image: $_" "ERROR"
        return $false
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    Write-Log "DoganAI Compliance Kit - Docker Build Script" "INFO"
    Write-Log "Action: $Action, Version: $Version, Environment: $Environment" "INFO"
    
    # Check prerequisites
    if (-not (Test-DockerInstalled)) {
        Write-Log "Docker is required but not installed" "ERROR"
        exit 1
    }
    
    if (-not (Test-DockerComposeInstalled)) {
        Write-Log "Docker Compose is required but not installed" "ERROR"
        exit 1
    }
    
    # Execute action
    switch ($Action.ToLower()) {
        "build" {
            if (Build-DockerImage) {
                if (Test-DockerImage) {
                    Push-DockerImage
                    Write-Log "Build completed successfully" "INFO"
                }
                else {
                    Write-Log "Image testing failed" "ERROR"
                    exit 1
                }
            }
            else {
                Write-Log "Build failed" "ERROR"
                exit 1
            }
        }
        
        "deploy" {
            if (-not (Deploy-Application)) {
                Write-Log "Deployment failed" "ERROR"
                exit 1
            }
        }
        
        "stop" {
            if (-not (Stop-Application)) {
                Write-Log "Stop failed" "ERROR"
                exit 1
            }
        }
        
        "remove" {
            if (-not (Remove-Application)) {
                Write-Log "Remove failed" "ERROR"
                exit 1
            }
        }
        
        "full" {
            if (Build-DockerImage) {
                if (Test-DockerImage) {
                    Push-DockerImage
                    if (Deploy-Application) {
                        Write-Log "Full deployment completed successfully" "INFO"
                    }
                    else {
                        Write-Log "Deployment failed" "ERROR"
                        exit 1
                    }
                }
                else {
                    Write-Log "Image testing failed" "ERROR"
                    exit 1
                }
            }
            else {
                Write-Log "Build failed" "ERROR"
                exit 1
            }
        }
        
        "test" {
            if (-not (Test-DockerImage)) {
                Write-Log "Image testing failed" "ERROR"
                exit 1
            }
        }
        
        "status" {
            Write-Log "Checking application status"
            docker compose ps
            Show-ServiceUrls
        }
        
        default {
            Write-Log "Unknown action: $Action" "ERROR"
            Write-Log "Available actions: build, deploy, stop, remove, full, test, status" "INFO"
            exit 1
        }
    }
    
    Write-Log "Script completed successfully" "INFO"
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

try {
    Main
}
catch {
    Write-Log "Script failed with error: $_" "ERROR"
    exit 1
}

# =============================================================================
# USAGE EXAMPLES
# =============================================================================
#
# Build image:
#   .\build-docker.ps1 -Action build -Version 1.0.0
#
# Build and deploy:
#   .\build-docker.ps1 -Action full -Version 1.0.0 -Environment production
#
# Deploy only:
#   .\build-docker.ps1 -Action deploy
#
# Stop application:
#   .\build-docker.ps1 -Action stop
#
# Remove everything:
#   .\build-docker.ps1 -Action remove
#
# Check status:
#   .\build-docker.ps1 -Action status
#
# Build with no cache and push:
#   .\build-docker.ps1 -Action build -Version 1.0.0 -NoBuildCache -Push
#
# =============================================================================