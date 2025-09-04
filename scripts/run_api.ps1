param(
    [int]$Port = 8000,
    [switch]$Reload
)

# Ensure we run from repo root
Set-Location -Path (Resolve-Path "$PSScriptRoot/..")

Write-Host "Starting DoganAI API on port $Port..." -ForegroundColor Green

# Load .env if present
if (Test-Path .env) {
    Write-Host "Loading environment from .env" -ForegroundColor Yellow
} else {
    Write-Host "No .env found. Using defaults or .env.example if you copy it." -ForegroundColor Yellow
}

$env:PYTHONPATH = (Get-Location).Path

$args = @('uvicorn', '--app-dir', 'app', 'main:app', '--host', '0.0.0.0', '--port', "$Port")
if ($Reload) { $args += '--reload' }

python -m $args
