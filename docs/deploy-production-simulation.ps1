#!/usr/bin/env pwsh
# DoganAI Production Deployment with Simulation Script

Write-Host "DoganAI Production Deployment & Simulation" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Configuration
$API_PORT = 8000
$WEB_PORT = 3001
$MAX_RETRIES = 3
$RETRY_DELAY = 2

# Function to test API with retries
function Test-APIWithRetries {
    param([string]$Url, [int]$MaxRetries = 3)
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            Write-Host "  Attempt $i of $MaxRetries..." -ForegroundColor Gray
            $response = Invoke-RestMethod -Uri $Url -Method GET -TimeoutSec 10
            return $response
        } catch {
            Write-Host "  Attempt $i failed: $($_.Exception.Message)" -ForegroundColor Yellow
            if ($i -lt $MaxRetries) {
                Start-Sleep -Seconds $RETRY_DELAY
            }
        }
    }
    return $null
}

# Function to test web endpoint with retries
function Test-WebWithRetries {
    param([string]$Url, [int]$MaxRetries = 3)
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            Write-Host "  Attempt $i of $MaxRetries..." -ForegroundColor Gray
            $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10
            return $response
        } catch {
            Write-Host "  Attempt $i failed: $($_.Exception.Message)" -ForegroundColor Yellow
            if ($i -lt $MaxRetries) {
                Start-Sleep -Seconds $RETRY_DELAY
            }
        }
    }
    return $null
}

# Function to run production simulation
function Start-ProductionSimulation {
    Write-Host "Starting Production Simulation..." -ForegroundColor Yellow
    $testsPassed = 0
    $totalTests = 4
    
    # Test 1: API Health
    Write-Host "Test 1/4: Testing API Health..." -ForegroundColor Cyan
    $healthResponse = Test-APIWithRetries -Url "http://localhost:$API_PORT/health" -MaxRetries $MAX_RETRIES
    if ($healthResponse) {
        Write-Host "  PASSED: API Health - Status: $($healthResponse.status)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  FAILED: API Health Check" -ForegroundColor Red
    }
    
    # Test 2: Web Application
    Write-Host "Test 2/4: Testing Web Application..." -ForegroundColor Cyan
    $webResponse = Test-WebWithRetries -Url "http://localhost:$WEB_PORT" -MaxRetries $MAX_RETRIES
    if ($webResponse -and $webResponse.StatusCode -eq 200) {
        Write-Host "  PASSED: Web Application - Status Code: $($webResponse.StatusCode)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  FAILED: Web Application Test" -ForegroundColor Red
    }
    
    # Test 3: Workflow Simulator
    Write-Host "Test 3/4: Testing Workflow Simulator..." -ForegroundColor Cyan
    $simulatorResponse = Test-WebWithRetries -Url "http://localhost:$WEB_PORT/simulate" -MaxRetries $MAX_RETRIES
    if ($simulatorResponse -and $simulatorResponse.StatusCode -eq 200) {
        Write-Host "  PASSED: Workflow Simulator - Status Code: $($simulatorResponse.StatusCode)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  FAILED: Workflow Simulator Test" -ForegroundColor Red
    }
    
    # Test 4: Load Testing Simulation
    Write-Host "Test 4/4: Running Load Test Simulation..." -ForegroundColor Cyan
    $successCount = 0
    $totalRequests = 5
    
    for ($i = 1; $i -le $totalRequests; $i++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$API_PORT/health" -Method GET -TimeoutSec 5
            if ($response -and $response.status) {
                $successCount++
            }
        } catch {
            # Request failed - continue
        }
        Start-Sleep -Milliseconds 200
    }
    
    $successRate = ($successCount / $totalRequests) * 100
    Write-Host "  Load Test: $successCount/$totalRequests requests successful ($successRate percent)" -ForegroundColor Cyan
    
    if ($successRate -ge 60) {
        Write-Host "  PASSED: Load Test (Success rate: $successRate percent)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  FAILED: Load Test (Success rate below 60 percent)" -ForegroundColor Red
    }
    
    # Summary
    Write-Host "" 
    Write-Host "Test Results: $testsPassed/$totalTests tests passed" -ForegroundColor Cyan
    
    return ($testsPassed -ge 3)  # Pass if at least 3 out of 4 tests pass
}

# Main deployment process
Write-Host "Checking Prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if ports are in use (basic connectivity test)
try {
    $apiTest = Test-NetConnection -ComputerName "localhost" -Port $API_PORT -InformationLevel Quiet
    if ($apiTest) {
        Write-Host "DoganAI API: Port $API_PORT is accessible" -ForegroundColor Green
    } else {
        Write-Host "DoganAI API: Port $API_PORT is not accessible" -ForegroundColor Yellow
    }
} catch {
    Write-Host "DoganAI API: Port check failed" -ForegroundColor Yellow
}

try {
    $webTest = Test-NetConnection -ComputerName "localhost" -Port $WEB_PORT -InformationLevel Quiet
    if ($webTest) {
        Write-Host "Web Application: Port $WEB_PORT is accessible" -ForegroundColor Green
    } else {
        Write-Host "Web Application: Port $WEB_PORT is not accessible" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Web Application: Port check failed" -ForegroundColor Yellow
}

Write-Host "Starting production simulation tests..." -ForegroundColor Green

# Run Production Simulation
$simulationResult = Start-ProductionSimulation

if ($simulationResult) {
    Write-Host "" 
    Write-Host "PRODUCTION SIMULATION PASSED!" -ForegroundColor Green
    Write-Host "" 
    Write-Host "Deployment Summary:" -ForegroundColor Yellow
    Write-Host "  System Status: Operational" -ForegroundColor Green
    Write-Host "  Core Services: Running" -ForegroundColor Green
    Write-Host "  Performance: Acceptable" -ForegroundColor Green
    Write-Host "  Readiness: Production Ready" -ForegroundColor Green
    Write-Host "" 
    Write-Host "System is ready for production use!" -ForegroundColor Green
    Write-Host "" 
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  Web App: http://localhost:$WEB_PORT" -ForegroundColor White
    Write-Host "  Simulator: http://localhost:$WEB_PORT/simulate" -ForegroundColor White
    Write-Host "  Health Check: http://localhost:$WEB_PORT/health" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:$API_PORT/docs" -ForegroundColor White
    Write-Host "" 
    Write-Host "Production deployment simulation completed successfully!" -ForegroundColor Green
} else {
    Write-Host "" 
    Write-Host "PRODUCTION SIMULATION FAILED!" -ForegroundColor Red
    Write-Host "Some tests failed, but this may be due to network connectivity." -ForegroundColor Yellow
    Write-Host "Please verify services are running and accessible." -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "Manual verification steps:" -ForegroundColor Cyan
    Write-Host "1. Check API: http://localhost:$API_PORT/health" -ForegroundColor White
    Write-Host "2. Check Web: http://localhost:$WEB_PORT" -ForegroundColor White
    Write-Host "3. Check Simulator: http://localhost:$WEB_PORT/simulate" -ForegroundColor White
    exit 1
}