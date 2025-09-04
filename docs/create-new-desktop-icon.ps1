# Create New Desktop Icon for DoganAI Compliance Kit
# This script creates a desktop shortcut with the Ai-Dogan.ico icon

# Get the current directory (where the script is located)
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$IconPath = Join-Path $ScriptPath "Ai-Dogan.ico"
$AppUrl = "http://localhost:8501"

# Get the desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Create the shortcut path
$ShortcutPath = Join-Path $DesktopPath "DoganAI Compliance Kit.lnk"

Write-Host "Creating desktop icon for DoganAI Compliance Kit..." -ForegroundColor Green
Write-Host "Icon file: $IconPath" -ForegroundColor Yellow
Write-Host "Target URL: $AppUrl" -ForegroundColor Yellow
Write-Host "Desktop path: $DesktopPath" -ForegroundColor Yellow

try {
    # Create WScript Shell object
    $WScriptShell = New-Object -ComObject WScript.Shell
    
    # Create shortcut object
    $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
    
    # Set shortcut properties
    $Shortcut.TargetPath = "C:\Windows\System32\cmd.exe"
    $Shortcut.Arguments = "/c start $AppUrl"
    $Shortcut.WorkingDirectory = $ScriptPath
    $Shortcut.Description = "DoganAI Compliance Kit - KSA Regulatory Compliance Platform"
    $Shortcut.IconLocation = $IconPath
    $Shortcut.WindowStyle = 7  # Minimized
    
    # Save the shortcut
    $Shortcut.Save()
    
    Write-Host "✅ Desktop icon created successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $ShortcutPath" -ForegroundColor Cyan
    Write-Host "🎯 Icon: $IconPath" -ForegroundColor Cyan
    Write-Host "🌐 Will open: $AppUrl" -ForegroundColor Cyan
    
    # Test if the icon file exists
    if (Test-Path $IconPath) {
        Write-Host "✅ Icon file found and will be used" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Warning: Icon file not found at $IconPath" -ForegroundColor Yellow
        Write-Host "   The shortcut will use the default icon" -ForegroundColor Yellow
    }
    
    # Show the created shortcut
    Write-Host "`n📋 Shortcut Details:" -ForegroundColor Magenta
    Write-Host "   Name: DoganAI Compliance Kit" -ForegroundColor White
    Write-Host "   Target: Opens $AppUrl in default browser" -ForegroundColor White
    Write-Host "   Icon: $IconPath" -ForegroundColor White
    Write-Host "   Working Directory: $ScriptPath" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error creating desktop icon: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please run this script as Administrator if needed" -ForegroundColor Yellow
}

Write-Host "`n🎉 Desktop icon creation completed!" -ForegroundColor Green
Write-Host "You can now double-click the icon on your desktop to open the application" -ForegroundColor Cyan
