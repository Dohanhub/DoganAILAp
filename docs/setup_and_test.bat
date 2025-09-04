@echo off
REM DoganAI Compliance Kit - Quick Setup & Test Script (Windows)
REM Run this to see everything in action!

:MENU
cls
echo ╔══════════════════════════════════════════════╗
echo ║              Choose an Option:               ║
echo ╠══════════════════════════════════════════════╣
echo ║  1. 🚀 Quick Demo (See Performance)         ║
echo ║  2. 🌐 Start Web API Server                  ║
echo ║  3. 📊 Run Performance Tests                 ║
echo ║  4. 🔧 Setup & Install Dependencies         ║
echo ║  5. 📖 Open Documentation                    ║
echo ║  6. ❌ Exit                                  ║
echo ╚══════════════════════════════════════════════╝

set /p option="Enter your choice (1-6): "

if "%option%"=="1" goto QUICK_DEMO
if "%option%"=="2" goto START_API
if "%option%"=="3" goto RUN_TESTS
if "%option%"=="4" goto SETUP_DEPENDENCIES
if "%option%"=="5" goto OPEN_DOCS
if "%option%"=="6" exit
goto MENU

:QUICK_DEMO
echo 🚀 Running Quick Demo...
REM Command for quick demo
python quick_demo.py
pause
goto MENU

:START_API
echo 🌐 Starting Web API Server...
REM Command to start web API server
python improvements/enhanced_api.py
pause
goto MENU

:RUN_TESTS
echo 📊 Running Performance Tests...
REM Command to run performance tests
python test_performance.py
pause
goto MENU

:SETUP_DEPENDENCIES
echo 🔧 Setting up & Installing Dependencies...
REM Commands to setup and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo ✅ Dependencies installed!
pause
goto MENU

:OPEN_DOCS
echo 📖 Opening Documentation...
REM Command to open documentation
start "" "docs/index.html"
pause
goto MENU

# Right-click and "Run as Administrator"
.\Create_Desktop_Shortcut.ps1