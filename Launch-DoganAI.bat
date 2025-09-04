@echo off
title DoganAI Compliance Kit Launcher
color 0A

echo ========================================
echo    DoganAI Compliance Kit Launcher
echo ========================================
echo.

rem Change to the script directory
cd /d "%~dp0"

rem Check if we're in the right directory
if not exist "scripts\bootstrap.ps1" (
    echo ERROR: bootstrap.ps1 not found!
    echo Please run this from the DoganAI-Compliance-Kit directory
    pause
    exit /b 1
)

echo Starting DoganAI Compliance Kit...
echo.

rem Run the bootstrap script with error handling
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { & '.\scripts\bootstrap-final.ps1' } catch { Write-Host 'Error: ' + $_.Exception.Message -ForegroundColor Red; pause }"

echo.
echo Application startup complete!
echo.
echo If you see any errors above, please check:
echo 1. Python 3.11+ is installed
echo 2. Node.js LTS is installed  
echo 3. Docker is running (if using containers)
echo 4. All required files are present
echo.
pause
