@echo off
echo ========================================
echo  DOGANAI COMPLIANCE KIT - WORLD CLASS UI
echo  Starting International Competition Level
echo ========================================

echo.
echo [1/5] Installing dependencies...
cd next
call npm install

echo.
echo [2/5] Building production assets...
call npm run build

echo.
echo [3/5] Starting development server...
start "DoganAI UI" cmd /k "npm run dev"

echo.
echo [4/5] Starting API backend...
cd ..\..\
start "DoganAI API" cmd /k "python main.py"

echo.
echo [5/5] Opening browser...
timeout /t 3 /nobreak > nul
start http://localhost:3000

echo.
echo ========================================
echo  🚀 WORLD-CLASS UI LAUNCHED!
echo  
echo  🌐 UI Dashboard: http://localhost:3000
echo  🔧 API Backend:  http://localhost:8000
echo  📊 Features:
echo    ✅ React + TypeScript
echo    ✅ Material-UI Components
echo    ✅ Real-time Data
echo    ✅ Advanced Charts
echo    ✅ Performance Optimized
echo    ✅ International Ready
echo ========================================

pause
