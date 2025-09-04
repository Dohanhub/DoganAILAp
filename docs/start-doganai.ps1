#!/usr/bin/env pwsh
# DoganAI Compliance Kit - Windows PowerShell Launcher

Write-Host "========================================" -ForegroundColor Green
Write-Host "   DoganAI Compliance Kit Launcher" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonVersion = python --version
$nodeVersion = node --version
Write-Host "Python: $pythonVersion" -ForegroundColor Green
Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Check if services are already running
$apiRunning = Test-Port -Port 8000
$webRunning = Test-Port -Port 3001

if ($apiRunning -and $webRunning) {
    Write-Host "DoganAI is already running!" -ForegroundColor Green
    Write-Host "Opening in browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:3001"
    exit 0
}

Write-Host "Starting DoganAI Compliance Kit..." -ForegroundColor Cyan
Write-Host ""

# Start API server if not running
if (-not $apiRunning) {
    Write-Host "[1/2] Starting API Server on port 8000..." -ForegroundColor Yellow
    $apiProcess = Start-Process -FilePath "uvicorn" -ArgumentList "run:app", "--port", "8000", "--reload" -WindowStyle Minimized -PassThru
    Start-Sleep -Seconds 3
} else {
    Write-Host "[1/2] API Server already running on port 8000" -ForegroundColor Green
}

# Start web application if not running
if (-not $webRunning) {
    Write-Host "[2/2] Starting Web Application on port 3001..." -ForegroundColor Yellow
    $webPath = Join-Path $PSScriptRoot "doganai-monorepo\apps\web"
    if (Test-Path $webPath) {
        Set-Location $webPath
        $webProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev", "--", "--port", "3001" -WindowStyle Minimized -PassThru
        Set-Location $PSScriptRoot
    } else {
        Write-Host "ERROR: Web application directory not found" -ForegroundColor Red
        Write-Host "Expected path: $webPath" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[2/2] Web Application already running on port 3001" -ForegroundColor Green
}

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test if services are responding
$maxRetries = 10
$retryCount = 0
$servicesReady = $false

while ($retryCount -lt $maxRetries -and -not $servicesReady) {
    $retryCount++
    Write-Host "Checking services... (attempt $retryCount/$maxRetries)" -ForegroundColor Gray
    
    $apiReady = Test-Port -Port 8000
    $webReady = Test-Port -Port 3001
    
    if ($apiReady -and $webReady) {
        $servicesReady = $true
    } else {
        Start-Sleep -Seconds 2
    }
}

if ($servicesReady) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "DoganAI Compliance Kit is now running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  Web App:     http://localhost:3001" -ForegroundColor White
    Write-Host "  Simulator:   http://localhost:3001/simulate" -ForegroundColor White
    Write-Host "  Health:      http://localhost:3001/health" -ForegroundColor White
    Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    
    # Open web browser
    Write-Host "Opening DoganAI in your default browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:3001"
    
    Write-Host ""
    Write-Host "Services are running in the background." -ForegroundColor Yellow
    Write-Host "Close this window when you're done using DoganAI." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "ERROR: Services failed to start properly" -ForegroundColor Red
    Write-Host "Please check the error messages above and try again" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to close this window"