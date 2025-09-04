param(
  [int]$ApiPort = 8010
)

$ErrorActionPreference = 'Stop'
Write-Host "DoganAI Bootstrap starting..." -ForegroundColor Green
Set-Location -Path (Resolve-Path "$PSScriptRoot/..")
New-Item -ItemType Directory -Path logs -Force | Out-Null

# 0) Ensure .env and web env are set
try { powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_env.ps1 } catch { Write-Warning "setup_env failed: $_" }

# 1) Python env check
Write-Host "[1/6] Checking Python and deps..." -ForegroundColor Yellow
try {
  $pyver = & python -c "import sys;print(sys.version.split()[0])"
  Write-Host "Python: $pyver" -ForegroundColor Green
} catch {
  Write-Error "Python not found. Install Python 3.11+ and re-run."
  exit 1
}

function Test-PyMod($m) {
  try { & python - << 'PY'
import importlib,sys
mods = sys.argv[1:]
missing=[]
for m in mods:
  try: importlib.import_module(m)
  except Exception as e: missing.append(m)
print(';'.join(missing))
PY
  } catch { return '' }
}

$missing = & python - << 'PY'
import importlib
mods = ['fastapi','uvicorn','sqlalchemy','passlib','python_dotenv','prometheus_client','bs4','boto3','pydantic']
missing=[m for m in mods if __import__('importlib').import_module('importlib').util.find_spec(m) is None]
print(' '.join(missing))
PY
if ($missing) {
  Write-Host "Installing Python deps: $missing" -ForegroundColor Yellow
  python -m pip install -e . | Out-Null
}

# 2) Start API (seed once)
  Write-Host "[2/6] Starting API on port $ApiPort..." -ForegroundColor Yellow
try {
  $env:PYTHONPATH=(Get-Location).Path
  Start-Process -WindowStyle Minimized -FilePath python -ArgumentList @('scripts/seed_policies.py') -NoNewWindow -RedirectStandardOutput logs\seed_policies.out.log -RedirectStandardError logs\seed_policies.err.log -ErrorAction SilentlyContinue | Out-Null
  Start-Process -WindowStyle Minimized -FilePath python -ArgumentList @('scripts/seed_vendors.py') -NoNewWindow -RedirectStandardOutput logs\seed_vendors.out.log -RedirectStandardError logs\seed_vendors.err.log -ErrorAction SilentlyContinue | Out-Null
  Start-Process -WindowStyle Minimized -FilePath python -ArgumentList @('scripts/seed_csv_matrices.py') -NoNewWindow -RedirectStandardOutput logs\seed_csv.out.log -RedirectStandardError logs\seed_csv.err.log -ErrorAction SilentlyContinue | Out-Null
  # Alembic migrations (auto-generate initial if none)
  $versions = Get-ChildItem -Path alembic\versions -ErrorAction SilentlyContinue
  if (-not $versions) {
    try { alembic revision --autogenerate -m "init" } catch { Write-Warning "alembic revision failed: $_" }
  }
  try { alembic upgrade head } catch { Write-Warning "alembic upgrade failed: $_" }
  Start-Process -PassThru -WindowStyle Minimized -FilePath python -ArgumentList @('-m','uvicorn','--app-dir','app','main:app','--host','0.0.0.0','--port',"$ApiPort") -RedirectStandardOutput logs\api.out.log -RedirectStandardError logs\api.err.log | Out-Null
} catch {
  Write-Warning "Failed to start API: $_"
}

# 3) Node + pnpm check
Write-Host "[3/6] Checking Node/pnpm..." -ForegroundColor Yellow
$node = (node -v) 2>$null
if (-not $node) { Write-Warning "Node not found. Install Node 20 and run: corepack enable; corepack prepare pnpm@9 --activate" }
else {
  Write-Host "Node: $node" -ForegroundColor Green
  # Enforce major version 20
  try {
    $major = [int]($node.TrimStart('v').Split('.')[0])
    if ($major -ne 20) {
      Write-Error "Unsupported Node version ($node). Please use Node 20.x."
      exit 1
    }
  } catch {
    Write-Warning "Could not parse Node version: $node"
  }
  try { corepack enable | Out-Null } catch {}
  try { corepack prepare pnpm@9 --activate | Out-Null } catch {}
  $pnpm = (pnpm -v) 2>$null
  if (-not $pnpm) { Write-Warning "pnpm not available; install/activate corepack." }
  else {
    Write-Host "pnpm: $pnpm" -ForegroundColor Green
    Write-Host "[4/6] Installing workspace deps..." -ForegroundColor Yellow
    pnpm -w install
    Write-Host "[5/6] Building tokens and SDK..." -ForegroundColor Yellow
    pnpm -w run tokens:build
    python scripts/generate_openapi.py
    pnpm -w run sdk:generate
    Write-Host "[6/6] Starting Web (http://localhost:3001)..." -ForegroundColor Yellow
    Start-Process -PassThru -WindowStyle Minimized -FilePath pnpm -ArgumentList @('--filter','@apps/web','dev') -RedirectStandardOutput logs\web.out.log -RedirectStandardError logs\web.err.log | Out-Null
    Start-Sleep -Seconds 5
    try { Start-Process "http://localhost:3001" } catch {}
    try { Start-Process "http://localhost:$ApiPort/health" } catch {}
}
}

Write-Host "Bootstrap complete. Open: http://localhost:$ApiPort and http://localhost:3001" -ForegroundColor Green
Write-Host "Logs: .\\logs\\api.out.log, .\\logs\\api.err.log, .\\logs\\web.out.log, .\\logs\\web.err.log" -ForegroundColor Yellow

# Create desktop shortcut if missing
try { powershell -NoProfile -ExecutionPolicy Bypass -File scripts\create_start_all_shortcut.ps1 } catch {}
