@echo off
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   DoganAI Compliance Kit Builder
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+ and add to PATH.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 20+ and add to PATH.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Run the Python build script
echo 🚀 Starting build process...
python build.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Process Completed Successfully!
echo ========================================
echo.
echo 📦 Output files are in the 'dist' directory
echo 💾 Build artifacts are in the 'build' directory
echo.
echo Next steps:
echo 1. Test the portable version in the 'build' directory
echo 2. Distribute the installer from the 'dist' directory
echo.
pause
