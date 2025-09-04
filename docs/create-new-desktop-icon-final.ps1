# DoganAI Compliance Kit - Final Desktop Icon Creator
# Creates a new desktop icon for the complete system structure

param(
    [string]$IconPath = "Ai-Dogan.ico",
    [string]$DesktopPath = "$env:USERPROFILE\Desktop",
    [switch]$Force
)

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

# Function to create VBS script for admin elevation
function Create-ElevationScript {
    $vbsContent = @"
Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "powershell.exe", "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Force", "", "runas", 1
"@
    
    $vbsPath = "$env:TEMP\elevate.vbs"
    $vbsContent | Out-File -FilePath $vbsPath -Encoding ASCII
    
    return $vbsPath
}

# Function to check if running as admin
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to create desktop shortcut
function Create-DesktopShortcut {
    param(
        [string]$Name,
        [string]$TargetPath,
        [string]$Arguments = "",
        [string]$WorkingDirectory = "",
        [string]$IconPath = "",
        [string]$Description = ""
    )
    
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$DesktopPath\$Name.lnk")
        
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Arguments = $Arguments
        $Shortcut.WorkingDirectory = $WorkingDirectory
        $Shortcut.IconLocation = $IconPath
        $Shortcut.Description = $Description
        
        $Shortcut.Save()
        
        Write-ColorOutput "✅ Created shortcut: $Name" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Failed to create shortcut: $Name - $($_.Exception.Message)" "Red"
        return $false
    }
}

# Function to create batch file launcher
function Create-BatchLauncher {
    param(
        [string]$Name,
        [string]$Content
    )
    
    try {
        $batchPath = "$DesktopPath\$Name.bat"
        $Content | Out-File -FilePath $batchPath -Encoding ASCII
        
        Write-ColorOutput "✅ Created batch launcher: $Name" "Green"
        return $batchPath
    }
    catch {
        Write-ColorOutput "❌ Failed to create batch launcher: $Name - $($_.Exception.Message)" "Red"
        return $null
    }
}

# Main execution
Write-ColorOutput "🚀 DoganAI Compliance Kit - Final Desktop Icon Creator" "Cyan"
Write-Host "================================================================"
Write-Host ""

# Check if running as admin
if (-not (Test-Admin)) {
    Write-ColorOutput "⚠️  This script requires administrative privileges" "Yellow"
    Write-Host "Creating elevation script..."
    
    $vbsPath = Create-ElevationScript
    Write-Host "Running elevation script..."
    Start-Process "wscript.exe" -ArgumentList $vbsPath -Wait
    
    # Clean up
    Remove-Item $vbsPath -Force -ErrorAction SilentlyContinue
    exit 0
}

Write-ColorOutput "✅ Running with administrative privileges" "Green"
Write-Host ""

# Check if icon file exists
if (-not (Test-Path $IconPath)) {
    Write-ColorOutput "❌ Icon file not found: $IconPath" "Red"
    Write-Host "Please ensure the icon file exists in the current directory"
    exit 1
}

Write-ColorOutput "✅ Icon file found: $IconPath" "Green"
Write-Host ""

# Create main system launcher
$mainLauncherContent = @"
@echo off
echo.
echo ========================================
echo   🚀 DOGANAI COMPLIANCE KIT 🚀
echo ========================================
echo.
echo Starting all services...
echo.

cd /d "%~dp0microservices"
echo Starting microservices...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   🌐 SYSTEM STATUS
echo ========================================
echo.
echo UI Dashboard: http://localhost:8501
echo Compliance Engine: http://localhost:8000/health
echo AI/ML Engine: http://localhost:8002/health
echo Auth Service: http://localhost:8004/health
echo Integration Service: http://localhost:8003/health
echo Benchmark Service: http://localhost:8001/health
echo AI Agent: http://localhost:8005/health
echo Auto Testing: http://localhost:8006/health
echo.
echo ========================================
echo   🚀 OPENING MAIN DASHBOARD
echo ========================================
echo.
start http://localhost:8501

echo.
echo System is ready! 🎉
echo Press any key to exit...
pause >nul
"@

# Create service manager
$serviceManagerContent = @"
@echo off
echo.
echo ========================================
echo   🔧 DOGANAI SERVICE MANAGER
echo ========================================
echo.
echo 1. Start All Services
echo 2. Stop All Services
echo 3. Restart All Services
echo 4. Show Service Status
echo 5. Open Dashboard
echo 6. Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto dashboard
if "%choice%"=="6" goto exit

:start
echo Starting all services...
cd /d "%~dp0microservices"
docker-compose up -d
echo Services started!
pause
goto menu

:stop
echo Stopping all services...
cd /d "%~dp0microservices"
docker-compose down
echo Services stopped!
pause
goto menu

:restart
echo Restarting all services...
cd /d "%~dp0microservices"
docker-compose restart
echo Services restarted!
pause
goto menu

:status
echo Checking service status...
cd /d "%~dp0microservices"
docker-compose ps
echo.
pause
goto menu

:dashboard
echo Opening dashboard...
start http://localhost:8501
goto menu

:exit
echo Goodbye!
exit /b 0

:menu
cls
goto :eof
"@

# Create validation launcher
$validationLauncherContent = @"
@echo off
echo.
echo ========================================
echo   🔍 DOGANAI VALIDATION SYSTEM
echo ========================================
echo.
echo Running comprehensive validation...
echo.

cd /d "%~dp0"

echo Running PowerShell validation script...
powershell -ExecutionPolicy Bypass -File "validation-script.ps1"

echo.
echo Validation complete!
pause
"@

# Create production deployment launcher
$productionLauncherContent = @"
@echo off
echo.
echo ========================================
echo   🚀 PRODUCTION DEPLOYMENT
echo ========================================
echo.
echo WARNING: This will deploy to production!
echo Are you sure you want to continue?
echo.
set /p confirm="Type 'YES' to confirm: "

if not "%confirm%"=="YES" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo Starting production deployment...
echo.

cd /d "%~dp0k8s"

echo Running Kubernetes deployment...
powershell -ExecutionPolicy Bypass -File "deploy-k8s.ps1"

echo.
echo Production deployment initiated!
pause
"@

# Create the shortcuts and launchers
Write-ColorOutput "📱 Creating desktop shortcuts and launchers..." "Cyan"
Write-Host ""

# 1. Main System Launcher
$mainBatchPath = Create-BatchLauncher "🚀 DoganAI Compliance Kit" $mainLauncherContent
if ($mainBatchPath) {
    Create-DesktopShortcut -Name "🚀 DoganAI Compliance Kit" -TargetPath $mainBatchPath -IconPath $IconPath -Description "Launch DoganAI Compliance Kit - Complete System"
}

# 2. Service Manager
$serviceBatchPath = Create-BatchLauncher "🔧 DoganAI Service Manager" $serviceManagerContent
if ($serviceBatchPath) {
    Create-DesktopShortcut -Name "🔧 DoganAI Service Manager" -TargetPath $serviceBatchPath -IconPath $IconPath -Description "Manage DoganAI services (start/stop/restart)"
}

# 3. Validation System
$validationBatchPath = Create-BatchLauncher "🔍 DoganAI Validation" $validationLauncherContent
if ($validationBatchPath) {
    Create-DesktopShortcut -Name "🔍 DoganAI Validation" -TargetPath $validationBatchPath -IconPath $IconPath -Description "Run comprehensive system validation"
}

# 4. Production Deployment
$productionBatchPath = Create-BatchLauncher "🚀 Production Deployment" $productionLauncherContent
if ($productionBatchPath) {
    Create-DesktopShortcut -Name "🚀 Production Deployment" -TargetPath $productionBatchPath -IconPath $IconPath -Description "Deploy to production environment"
}

# 5. Direct Dashboard Access
Create-DesktopShortcut -Name "🌐 DoganAI Dashboard" -TargetPath "http://localhost:8501" -IconPath $IconPath -Description "Open DoganAI Dashboard directly"

# 6. System Overview
$overviewPath = "$PWD\FINAL_SYSTEM_OVERVIEW.md"
if (Test-Path $overviewPath) {
    Create-DesktopShortcut -Name "📋 System Overview" -TargetPath "notepad.exe" -Arguments $overviewPath -IconPath $IconPath -Description "View complete system overview"
}

Write-Host ""
Write-ColorOutput "🎉 Desktop shortcuts created successfully!" "Green"
Write-Host ""

# Display summary
Write-ColorOutput "📱 Created Shortcuts:" "Cyan"
Write-Host "  🚀 DoganAI Compliance Kit - Main launcher"
Write-Host "  🔧 DoganAI Service Manager - Service control"
Write-Host "  🔍 DoganAI Validation - System validation"
Write-Host "  🚀 Production Deployment - Production deployment"
Write-Host "  🌐 DoganAI Dashboard - Direct dashboard access"
Write-Host "  📋 System Overview - System documentation"
Write-Host ""

Write-ColorOutput "🚀 Quick Start:" "Cyan"
Write-Host "  1. Double-click '🚀 DoganAI Compliance Kit' to start all services"
Write-Host "  2. Wait for services to start (about 10 seconds)"
Write-Host "  3. Dashboard will open automatically at http://localhost:8501"
Write-Host ""

Write-ColorOutput "🔧 Service Management:" "Cyan"
Write-Host "  Use '🔧 DoganAI Service Manager' to start/stop/restart services"
Write-Host "  Use '🔍 DoganAI Validation' to validate system health"
Write-Host ""

Write-ColorOutput "📊 System Status:" "Cyan"
Write-Host "  All services run on localhost with different ports:"
Write-Host "  - UI Dashboard: Port 8501"
Write-Host "  - Compliance Engine: Port 8000"
Write-Host "  - AI/ML Engine: Port 8002"
Write-Host "  - Auth Service: Port 8004"
Write-Host "  - Integration Service: Port 8003"
Write-Host "  - Benchmark Service: Port 8001"
Write-Host "  - AI Agent: Port 8005"
Write-Host "  - Auto Testing: Port 8006"
Write-Host ""

Write-ColorOutput "✅ Setup Complete!" "Green"
Write-Host "Your DoganAI Compliance Kit is ready to use!"
Write-Host ""

# Optional: Start services automatically
$autoStart = Read-Host "Would you like to start the services now? (y/n)"
if ($autoStart -eq "y" -or $autoStart -eq "Y") {
    Write-Host "Starting services..."
    cd microservices
    docker-compose up -d
    
    Write-Host "Waiting for services to start..."
    Start-Sleep -Seconds 10
    
    Write-Host "Opening dashboard..."
    Start-Process "http://localhost:8501"
    
    Write-ColorOutput "🎉 Services started and dashboard opened!" "Green"
}

Write-Host ""
Write-ColorOutput "🚀 DoganAI Compliance Kit is ready!" "Cyan"
Write-Host "================================================================"
