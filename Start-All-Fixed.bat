@echo off
setlocal enabledelayedexpansion

echo ========================================
echo DoganAI Compliance Kit - Start All
echo ========================================

rem Change to the script directory
cd /d "%~dp0"

rem Check if we're in the right directory
if not exist "scripts\bootstrap.ps1" (
    echo ERROR: bootstrap.ps1 not found!
    echo Please run this from the DoganAI-Compliance-Kit directory
    pause
    exit /b 1
)

rem Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available!
    pause
    exit /b 1
)

rem Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python not found. Some features may not work.
    echo Please install Python 3.11+ and try again.
)

rem Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found. Web interface may not work.
    echo Please install Node.js LTS and try again.
)

echo.
echo Starting DoganAI Compliance Kit...
echo.

rem Run the bootstrap script with error handling
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { & '.\scripts\bootstrap.ps1' } catch { Write-Host 'Error: ' + $_.Exception.Message -ForegroundColor Red; pause }"

echo.
echo If you see any errors above, please check:
echo 1. Python 3.11+ is installed
echo 2. Node.js LTS is installed  
echo 3. Docker is running (if using containers)
echo 4. All required files are present
echo.
pause
