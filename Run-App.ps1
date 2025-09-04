param(
  [string]$HostIP = '127.0.0.1',
  [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'

function Ensure-Python() {
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host 'Python 3.11+ is required. Install from https://www.python.org/downloads/' -ForegroundColor Yellow
    exit 1
  }
}

function Ensure-Venv($Path) {
  if (-not (Test-Path $Path)) {
    Write-Host "Creating virtualenv at $Path ..."
    python -m venv $Path
  }
}

Ensure-Python
$venv = ".runenv"
Ensure-Venv $venv

. "$venv/Scripts/Activate.ps1"
python -m pip install --upgrade pip | Out-Null
if (Test-Path 'requirements.lock.txt') {
  try { pip install --require-hashes -r requirements.lock.txt } catch { pip install -r requirements-api.txt }
} else { pip install -r requirements-api.txt }

# Local development env
$env:ENV = 'development'
$env:ENVIRONMENT = 'development'
$env:ALLOW_SQLITE = 'true'
$env:SECRET_KEY = 'dev-secret-please-change'
$env:API_KEY = 'dev-api-key'
$env:ALLOWED_ORIGINS = '*'
$env:REQUIRE_REDIS_FOR_RATELIMIT = 'false'
$env:ALLOWED_OUTBOUND_HOSTS = '.github.com,example.com'

Write-Host "Launching API on http://$HostIP:$Port"
Start-Process Open-App.url | Out-Null
python -m uvicorn app.main:app --host $HostIP --port $Port --reload

