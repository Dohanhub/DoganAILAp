@echo off
echo Quick UI Test - DoganAI Compliance Kit
echo.

REM Set development environment
set VITE_ENV=development
set VITE_API_URL=http://localhost:8000

REM Navigate to frontend and start dev server
cd /d "%~dp0frontend"

echo Installing dependencies if needed...
if not exist "node_modules" (
    npm install
)

echo.
echo Starting frontend development server...
echo UI will be available at: http://localhost:3001
echo.
npm run dev
