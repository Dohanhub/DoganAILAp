#!/usr/bin/env pwsh
# DoganAI Compliance Kit - Fast Development Startup Script

Write-Host "🚀 Starting DoganAI Compliance Kit Development Environment..." -ForegroundColor Green
Write-Host ""

# Set environment variables for development
$env:VITE_ENV = "development"
$env:VITE_API_URL = "http://localhost:8000"
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"

# Create frontend .env file if it doesn't exist
$frontendEnvPath = "frontend\.env"
if (-not (Test-Path $frontendEnvPath)) {
    Write-Host "📝 Creating frontend environment file..." -ForegroundColor Yellow
    @"
# Development environment for DoganAI Compliance Kit Frontend
VITE_ENV=development
VITE_API_URL=http://localhost:8000
VITE_GATEWAY_URL=http://localhost:8080
VITE_APP_NAME=DoganAI Compliance Kit
VITE_APP_VERSION=2.0.0
"@ | Out-File -FilePath $frontendEnvPath -Encoding UTF8
}

# Function to start backend
function Start-Backend {
    Write-Host "🔧 Starting Backend API Server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
}

# Function to start frontend
function Start-Frontend {
    Write-Host "🎨 Starting Frontend Development Server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal
}

# Check if Python is available
try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    node --version | Out-Null
    Write-Host "✅ Node.js found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Install Python dependencies if needed
if (-not (Test-Path "venv") -and -not (Test-Path ".venv")) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements-api.txt
}

# Install Node.js dependencies if needed
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Start services
Start-Backend
Start-Sleep -Seconds 3
Start-Frontend

Write-Host ""
Write-Host "🎉 Development servers are starting..." -ForegroundColor Green
Write-Host "📍 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "📍 Frontend UI: http://localhost:3001" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "📍 Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "Shutting down development environment..." -ForegroundColor Red
}
