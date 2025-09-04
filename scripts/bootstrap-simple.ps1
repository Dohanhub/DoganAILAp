$ErrorActionPreference = 'Stop'

Set-Location -Path (Resolve-Path "$PSScriptRoot/..")

# Ensure minimal env
try { powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_env.ps1 } catch {}

Write-Host "Starting API (dev) on 8010 and Web on 3001..." -ForegroundColor Green

$env:PYTHONPATH=(Get-Location).Path
Start-Process -PassThru -WindowStyle Minimized -FilePath python -ArgumentList @('-m','uvicorn','--app-dir','app','main:app','--host','0.0.0.0','--port','8010') | Out-Null

try { corepack enable | Out-Null } catch {}
try { corepack prepare pnpm@9 --activate | Out-Null } catch {}
pnpm -w install
pnpm -w run tokens:build
python scripts/generate_openapi.py
pnpm -w run sdk:generate

Start-Process -PassThru -WindowStyle Minimized -FilePath pnpm -ArgumentList @('--filter','@apps/web','dev','-p','3001') | Out-Null

Start-Sleep -Seconds 3
try { Start-Process "http://localhost:3001" } catch {}
try { Start-Process "http://localhost:8010/health" } catch {}

