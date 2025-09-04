@echo off
echo Creating Desktop Icon for DoganAI Compliance Kit...
echo.
echo This will create a desktop shortcut with the Ai-Dogan.ico icon
echo.

powershell -ExecutionPolicy Bypass -File "create-new-desktop-icon.ps1"

echo.
echo Press any key to exit...
pause >nul
