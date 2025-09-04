@echo off
echo DogAI Compliance Kit - Local Deployment
echo =============================================
echo.
echo Starting local deployment with desktop icon creation...
echo.

powershell -ExecutionPolicy Bypass -File "deploy-local-fixed.ps1" -CreateDesktopIcon

echo.
echo Deployment script completed!
echo Check the output above for any errors.
echo.
pause
