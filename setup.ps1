# DoganAI Compliance Kit Setup Script

Write-Host "=== DoganAI Compliance Kit Setup ===" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "✓ .env file created from env.example" -ForegroundColor Green
    } else {
        Write-Host "✗ env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Install Python dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
}

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run: make bootstrap" -ForegroundColor White
Write-Host "3. Run: make up" -ForegroundColor White
Write-Host "4. Run: make migrate" -ForegroundColor White
Write-Host "5. Run: make seed" -ForegroundColor White
Write-Host "6. Run: make health" -ForegroundColor White
