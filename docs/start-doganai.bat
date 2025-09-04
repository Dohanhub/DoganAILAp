@echo off
REM DoganAI Compliance Kit - Windows Launcher
REM This script starts both the API server and web application

echo ========================================
echo    DoganAI Compliance Kit Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 20+ and try again
    pause
    exit /b 1
)

echo Starting DoganAI Compliance Kit...
echo.

REM Start API server in background
echo [1/2] Starting API Server on port 8000...
start "DoganAI API Server" /min cmd /c "uvicorn run:app --port 8000 --reload"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

REM Start web application
echo [2/2] Starting Web Application on port 3001...
cd /d "%~dp0doganai-monorepo\apps\web"
start "DoganAI Web App" /min cmd /c "npm run dev -- --port 3001"

REM Wait for services to start
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Open web browser
echo.
echo Opening DoganAI in your default browser...
start "" "http://localhost:3001"

echo.
echo ========================================
echo DoganAI Compliance Kit is now running!
echo ========================================
echo.
echo Access Points:
echo   Web App:     http://localhost:3001
echo   Simulator:   http://localhost:3001/simulate
echo   Health:      http://localhost:3001/health
echo   API Docs:    http://localhost:8000/docs
echo.
echo Press any key to close this window...
echo (The applications will continue running in background)
pause >nul