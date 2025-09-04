@echo off
REM DoganAI Compliance Kit - Desktop Launcher
REM This script launches the DoganAI application from desktop

title DoganAI Compliance Kit Launcher

echo.
echo    ????????????????????????????????????????????????
echo    ?          DoganAI Compliance Kit              ?
echo    ?        Saudi Arabia Enterprise Solution      ?
echo    ????????????????????????????????????????????????
echo.

REM Get the script directory (where this launcher is located)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if we're in the right directory
if not exist "improvements\performance.py" (
    echo ? Error: DoganAI files not found in current directory
    echo    Expected location: %SCRIPT_DIR%
    echo    Please place this launcher in your DoganAI-Compliance-Kit folder
    echo.
    pause
    exit /b 1
)

echo ? DoganAI Compliance Kit found
echo ?? Location: %SCRIPT_DIR%
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ? Python is not installed or not in PATH
    echo    Please install Python from: https://python.org
    echo.
    pause
    exit /b 1
)

echo ? Python installation verified
echo.

REM Create menu for user selection
:MENU
echo ????????????????????????????????????????????????
echo ?              Choose an Option:               ?
echo ????????????????????????????????????????????????
echo ?  1. ?? Quick Demo (See Performance)         ?
echo ?  2. ?? Start Web API Server                  ?
echo ?  3. ?? Run Performance Tests                 ?
echo ?  4. ?? Setup & Install Dependencies         ?
echo ?  5. ?? Open Documentation                    ?
echo ?  6. ? Exit                                  ?
echo ????????????????????????????????????????????????
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto DEMO
if "%choice%"=="2" goto API
if "%choice%"=="3" goto TESTS
if "%choice%"=="4" goto SETUP
if "%choice%"=="5" goto DOCS
if "%choice%"=="6" goto EXIT

echo Invalid choice. Please enter 1-6.
echo.
goto MENU

:DEMO
echo.
echo ?? Starting DoganAI Performance Demo...
echo    This will show you the performance improvements in action
echo.
python quick_demo.py
echo.
echo Demo completed! Press any key to return to menu...
pause >nul
goto MENU

:API
echo.
echo ?? Starting DoganAI Web API Server...
echo    The server will start at: http://localhost:8000
echo    Press Ctrl+C to stop the server
echo.

REM Check if FastAPI is installed
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ?? FastAPI not installed. Installing dependencies...
    pip install fastapi uvicorn aioredis asyncpg prometheus-client structlog
    echo.
)

echo ? Starting API server...
echo ?? Access points:
echo    • Main API: http://localhost:8000
echo    • Health Check: http://localhost:8000/health/enhanced
echo    • Performance Metrics: http://localhost:8000/metrics/performance
echo    • Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server and return to menu
echo.

python improvements/enhanced_api.py
echo.
echo Server stopped. Press any key to return to menu...
pause >nul
goto MENU

:TESTS
echo.
echo ?? Running DoganAI Performance Tests...
echo    This will test all performance optimizations
echo.
python test_performance.py
echo.
echo Tests completed! Press any key to return to menu...
pause >nul
goto MENU

:SETUP
echo.
echo ?? Setting up DoganAI Compliance Kit...
echo    Installing all required dependencies...
echo.

REM Install all dependencies
echo Installing core dependencies...
pip install psutil matplotlib pandas

echo Installing web dependencies...
pip install fastapi uvicorn aioredis asyncpg prometheus-client structlog

echo Installing security dependencies...
pip install cryptography passlib python-jose slowapi

echo Installing monitoring dependencies...
pip install opentelemetry-api opentelemetry-sdk

echo.
echo ? Setup completed!
echo.
echo ?? Optional components:
echo    • Redis: winget install Redis.Redis
echo    • PostgreSQL: winget install PostgreSQL.PostgreSQL
echo    • Docker: winget install Docker.DockerDesktop
echo.
pause
goto MENU

:DOCS
echo.
echo ?? Opening DoganAI Documentation...
echo.

REM Try to open documentation files
if exist "README.md" (
    start "" "README.md"
    echo ? README.md opened
)

if exist "INTEGRATION_GUIDE.md" (
    start "" "INTEGRATION_GUIDE.md"
    echo ? Integration Guide opened
)

if exist "HOW_TO_TEST.md" (
    start "" "HOW_TO_TEST.md"
    echo ? Testing Guide opened
)

echo.
echo ?? Online Resources:
echo    • API Docs (when server running): http://localhost:8000/docs
echo    • Health Status: http://localhost:8000/health/enhanced
echo    • Performance Metrics: http://localhost:8000/metrics/performance
echo.
pause
goto MENU

:EXIT
echo.
echo ?? Thank you for using DoganAI Compliance Kit!
echo    ???? Built for Saudi Arabia's Digital Transformation
echo.
exit /b 0