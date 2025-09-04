@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                 DoganAI Compliance Kit                                  ║
echo ║           60-Second Auto-Update ^& Validation System                     ║
echo ║                                                                          ║
echo ║  🏛️ Regulatory Sources: NCA, SAMA, MOH, CITC, CMA                      ║
echo ║  🔧 Vendor Sources: IBM Watson, Microsoft Azure, AWS                    ║
echo ║  🏛️ Government Sources: MOI, SDAIA                                      ║
echo ║  ⏰ Update Frequency: Every 60 seconds                                  ║
echo ║  🔄 Non-blocking operations                                              ║
echo ║  🛡️ Real-time validation                                                 ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

:: Check if required files exist
if not exist "auto_update_validation_60s.py" (
    echo ❌ auto_update_validation_60s.py not found in current directory.
    pause
    exit /b 1
)

if not exist "start_auto_update_60s.py" (
    echo ❌ start_auto_update_60s.py not found in current directory.
    pause
    exit /b 1
)

echo 🚀 Starting DoganAI Auto-Update System...
echo.

:: Start the auto-update system
python start_auto_update_60s.py

echo.
echo 🛑 Auto-Update System stopped.
pause
