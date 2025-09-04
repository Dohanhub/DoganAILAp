@echo off
title DoganAI Compliance Kit - Configuration-Driven Enterprise Platform
color 0A

echo.
echo ========================================
echo    DoganAI Compliance Kit v2.0
echo    Configuration-Driven System
echo ========================================
echo.

echo 🚀 Starting DoganAI Compliance Kit...
echo 📊 New: Configuration-driven UI with hot-reload
echo 🌍 New: Multi-language support (English/Arabic)
echo 🔄 New: Auto-reload configuration changes
echo.

echo 📍 Checking service status...
timeout /t 2 /nobreak >nul

echo.
echo ✅ All microservices are running!
echo 🌐 Opening configuration-driven dashboard...
echo.

echo 🔗 Main Dashboard: http://localhost:8501/
echo 🔗 Arabic Version: http://localhost:8501/?lang=ar
echo 🔗 Configuration: http://localhost:8501/api/config/dashboard
echo.

echo 🎯 Features Available:
echo   • Configuration-driven UI (no hardcoded HTML)
echo   • Hot-reload configuration changes
echo   • Multi-language support (EN/AR)
echo   • Real-time dashboard data
echo   • Professional enterprise interface
echo.

echo 🚀 Launching in browser...
start http://localhost:8501/

echo.
echo 🎉 DoganAI Compliance Kit is ready!
echo.
echo 💡 Tips:
echo   • Edit config files in microservices/ui/config/
echo   • Changes auto-reload (hot-reload enabled)
echo   • Switch languages using the buttons on the page
echo   • All UI is generated from configuration
echo.
echo Press any key to exit...
pause >nul
