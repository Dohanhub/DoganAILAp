#!/usr/bin/env pwsh
# Create Desktop Shortcut for DoganAI Compliance Kit

Write-Host "Creating DoganAI Desktop Shortcut..." -ForegroundColor Green

# Get current script directory
$scriptDir = $PSScriptRoot
$batchFile = Join-Path $scriptDir "start-doganai.bat"
$iconFile = Join-Path $scriptDir "Ai-Dogan.ico"

# Create shortcut on desktop
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "DoganAI Compliance Kit.lnk"

# Create WScript Shell object
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)

# Set shortcut properties
$shortcut.TargetPath = $batchFile
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = "DoganAI Compliance Kit - AI-powered compliance solution"
$shortcut.WindowStyle = 1  # Normal window

# Set icon if it exists
if (Test-Path $iconFile) {
    $shortcut.IconLocation = $iconFile
    Write-Host "Using custom icon: $iconFile" -ForegroundColor Cyan
} else {
    Write-Host "Custom icon not found, using default" -ForegroundColor Yellow
}

# Save the shortcut
$shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $shortcutPath" -ForegroundColor Cyan

# Also create shortcut in Start Menu
$startMenuPath = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs"
$startMenuShortcut = Join-Path $startMenuPath "DoganAI Compliance Kit.lnk"

try {
    $startShortcut = $WScriptShell.CreateShortcut($startMenuShortcut)
    $startShortcut.TargetPath = $batchFile
    $startShortcut.WorkingDirectory = $scriptDir
    $startShortcut.Description = "DoganAI Compliance Kit - AI-powered compliance solution"
    $startShortcut.WindowStyle = 1
    
    if (Test-Path $iconFile) {
        $startShortcut.IconLocation = $iconFile
    }
    
    $startShortcut.Save()
    Write-Host "Start Menu shortcut created successfully!" -ForegroundColor Green
    Write-Host "Location: $startMenuShortcut" -ForegroundColor Cyan
} catch {
    Write-Host "Could not create Start Menu shortcut: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DoganAI Shortcuts Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Cyan
Write-Host "  1. Double-click the desktop icon to start DoganAI" -ForegroundColor White
Write-Host "  2. Find DoganAI in your Start Menu" -ForegroundColor White
Write-Host "  3. Pin the shortcut to your taskbar" -ForegroundColor White
Write-Host ""
Write-Host "The application will automatically:" -ForegroundColor Yellow
Write-Host "  - Start the API server" -ForegroundColor White
Write-Host "  - Start the web application" -ForegroundColor White
Write-Host "  - Open your browser to the app" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to close"