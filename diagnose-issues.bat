@echo off
setlocal enabledelayedexpansion

echo ========================================
echo DoganAI Compliance Kit - Issue Diagnostics
echo ========================================
echo.

rem Check current directory
echo [1] Current Directory:
echo %CD%
echo.

rem Check if required files exist
echo [2] Required Files Check:
if exist "scripts\bootstrap.ps1" (
    echo ✓ scripts\bootstrap.ps1 - FOUND
) else (
    echo ✗ scripts\bootstrap.ps1 - MISSING
)

if exist "scripts\create_start_all_shortcut.ps1" (
    echo ✓ scripts\create_start_all_shortcut.ps1 - FOUND
) else (
    echo ✗ scripts\create_start_all_shortcut.ps1 - MISSING
)

if exist "scripts\setup_env.ps1" (
    echo ✓ scripts\setup_env.ps1 - FOUND
) else (
    echo ✗ scripts\setup_env.ps1 - MISSING
)

if exist "scripts\seed_policies.py" (
    echo ✓ scripts\seed_policies.py - FOUND
) else (
    echo ✗ scripts\seed_policies.py - MISSING
)

if exist "scripts\seed_vendors.py" (
    echo ✓ scripts\seed_vendors.py - FOUND
) else (
    echo ✗ scripts\seed_vendors.py - MISSING
)

if exist "scripts\seed_csv_matrices.py" (
    echo ✓ scripts\seed_csv_matrices.py - FOUND
) else (
    echo ✗ scripts\seed_csv_matrices.py - MISSING
)

if exist "scripts\generate_openapi.py" (
    echo ✓ scripts\generate_openapi.py - FOUND
) else (
    echo ✗ scripts\generate_openapi.py - MISSING
)
echo.

rem Check PowerShell execution policy
echo [3] PowerShell Execution Policy:
powershell -Command "Get-ExecutionPolicy" 2>nul
if errorlevel 1 (
    echo ✗ Could not check execution policy
)
echo.

rem Check Python
echo [4] Python Check:
python --version 2>nul
if errorlevel 1 (
    echo ✗ Python not found or not in PATH
) else (
    echo ✓ Python is available
)
echo.

rem Check Node.js
echo [5] Node.js Check:
node --version 2>nul
if errorlevel 1 (
    echo ✗ Node.js not found or not in PATH
) else (
    echo ✓ Node.js is available
)
echo.

rem Check Docker
echo [6] Docker Check:
docker --version 2>nul
if errorlevel 1 (
    echo ✗ Docker not found or not running
) else (
    echo ✓ Docker is available
)
echo.

rem Check permissions
echo [7] Permission Check:
echo Current user: %USERNAME%
echo Running as admin: 
net session >nul 2>&1
if errorlevel 1 (
    echo ✗ Not running as administrator
) else (
    echo ✓ Running as administrator
)
echo.

echo ========================================
echo DIAGNOSTIC SUMMARY
echo ========================================
echo.
echo If you see any MISSING files above, that's likely the cause.
echo If PowerShell execution policy is restricted, run as administrator:
echo   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo.
echo If Python/Node.js/Docker are missing, install them first.
echo.
echo Try running the fixed version: Start-All-Fixed.bat
echo.
pause
