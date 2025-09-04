param(
  [switch]$Prod
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO ] $msg" -ForegroundColor Cyan }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Load .env if present to populate environment
$envPath = Join-Path $repoRoot '.env'
if (Test-Path $envPath) {
  Write-Info "Loading environment from .env"
  Get-Content $envPath | ForEach-Object {
    if ($_ -match '^[#\s]') { return }
    if ($_ -match '^(?<k>[A-Za-z_][A-Za-z0-9_]*)=(?<v>.*)$') {
      $k = $Matches['k']
      $v = $Matches['v']
      $v = $v.Trim().Trim('"').Trim("'")
      if (-not $env:$k) { $env:$k = $v }
    }
  }
}

# Validate required env
$missing = @()
foreach ($name in @('DATABASE_URL','SECRET_KEY')) {
  if (-not $env:$name) { $missing += $name }
}
if ($missing.Count -gt 0) {
  Write-Err "Missing required environment variables: $($missing -join ', ')"
  Write-Host "Set them in your shell or .env file in the repo root." -ForegroundColor Yellow
  exit 1
}

# Ensure Docker is available
try { docker version | Out-Null } catch { Write-Err "Docker is not available on PATH"; exit 1 }

$compose = if ($Prod) { 'docker-compose.prod.yml' } else { 'docker-compose.simple.yml' }
if (-not (Test-Path (Join-Path $repoRoot $compose))) { Write-Err "Compose file not found: $compose"; exit 1 }

Write-Info "Starting stack with $compose"
docker compose -f $compose up -d --build

if ($LASTEXITCODE -ne 0) { Write-Err "docker compose up failed"; exit $LASTEXITCODE }

Write-Host "App is starting. API: http://localhost:8010  Web: http://localhost:3001" -ForegroundColor Green

