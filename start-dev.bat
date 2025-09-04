@echo off
echo Starting DoganAI Compliance Kit Development Environment...
echo.

REM Copy environment file if it doesn't exist
if not exist "frontend\.env" (
    echo Creating frontend environment file...
    copy "frontend\.env.example" "frontend\.env"
)

REM Start backend API server
echo Starting Backend API Server...
start "DoganAI Backend" cmd /k "cd /d %~dp0 && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend development server
echo Starting Frontend Development Server...
start "DoganAI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Development servers are starting...
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3001
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause >nul
