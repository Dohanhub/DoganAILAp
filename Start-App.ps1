param(
    [int]$Port = 8010,
    [switch]$Reload,
    [switch]$Seed
)

# Always run from repo root
Set-Location -Path (Resolve-Path $PSScriptRoot)

Write-Host "Launching DoganAI Compliance API on port $Port..." -ForegroundColor Green

$env:PYTHONPATH = (Get-Location).Path

$args = @('uvicorn','--app-dir','app','main:app','--host','0.0.0.0','--port',"$Port")
if ($Reload) { $args += '--reload' }

# Optionally seed policies and vendors before starting
if ($Seed) {
  Write-Host "Seeding policies and vendors..." -ForegroundColor Yellow
  try { python scripts/seed_policies.py } catch { Write-Warning "Policy seeding failed: $_" }
  try { python scripts/seed_vendors.py } catch { Write-Warning "Vendor seeding failed: $_" }
  try { python scripts/seed_csv_matrices.py } catch { Write-Warning "CSV/XLSX seeding failed: $_" }
}

python -m $args
