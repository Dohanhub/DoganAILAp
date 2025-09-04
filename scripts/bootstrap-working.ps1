# Working Bootstrap Script for DoganAI Compliance Kit
# This version has correct PowerShell syntax

Write-Host "=== DoganAI Bootstrap ===" -ForegroundColor Green

# Change to the repository root
Set-Location -Path (Resolve-Path "$PSScriptRoot/..")
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path logs -Force | Out-Null
    Write-Host "✓ Logs directory created" -ForegroundColor Green
}

# Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$pyver = python --version 2>$null
if ($pyver) {
    Write-Host "✓ Python: $pyver" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
}

# Check Node.js
Write-Host "`n[2/4] Checking Node.js..." -ForegroundColor Yellow
$nodever = node --version 2>$null
if ($nodever) {
    Write-Host "✓ Node.js: $nodever" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
}

# Check Docker
Write-Host "`n[3/4] Checking Docker..." -ForegroundColor Yellow
$dockerver = docker --version 2>$null
if ($dockerver) {
    Write-Host "✓ Docker: $dockerver" -ForegroundColor Green
} else {
    Write-Host "✗ Docker not found" -ForegroundColor Red
}

# Try to start services
Write-Host "`n[4/4] Starting services..." -ForegroundColor Yellow

# Try to start API if Python is available
if ($pyver) {
    Write-Host "Starting API server..." -ForegroundColor Cyan
    if (Test-Path "main.py") {
        Start-Process -WindowStyle Minimized -FilePath python -ArgumentList @("main.py") -RedirectStandardOutput logs\api.out.log -RedirectStandardError logs\api.err.log
        Write-Host "✓ API server started" -ForegroundColor Green
    } elseif (Test-Path "app/main.py") {
        Start-Process -WindowStyle Minimized -FilePath python -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000") -RedirectStandardOutput logs\api.out.log -RedirectStandardError logs\api.err.log
        Write-Host "✓ API server started" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No main.py found" -ForegroundColor Yellow
    }
}

# Try to start web interface if Node.js is available
if ($nodever) {
    Write-Host "Starting web interface..." -ForegroundColor Cyan
    if (Test-Path "package.json") {
        Start-Process -WindowStyle Minimized -FilePath npm -ArgumentList @("start") -RedirectStandardOutput logs\web.out.log -RedirectStandardError logs\web.err.log
        Write-Host "✓ Web interface started" -ForegroundColor Green
    } elseif (Test-Path "frontend/package.json") {
        Set-Location frontend
        Start-Process -WindowStyle Minimized -FilePath npm -ArgumentList @("start") -RedirectStandardOutput ..\logs\web.out.log -RedirectStandardError ..\logs\web.err.log
        Set-Location ..
        Write-Host "✓ Web interface started" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No package.json found" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Bootstrap Complete ===" -ForegroundColor Green
Write-Host "Check the logs directory for any error messages" -ForegroundColor Yellow
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
