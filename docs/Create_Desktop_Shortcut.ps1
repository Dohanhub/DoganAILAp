# PowerShell script to create desktop shortcut automatically
# Run this as Administrator in PowerShell

param(
    [string]$DoganAIPath = (Get-Location).Path
)

Write-Host "?? Creating DoganAI Compliance Kit Desktop Shortcut..." -ForegroundColor Green
Write-Host "?? DoganAI Location: $DoganAIPath" -ForegroundColor Cyan

# Check if DoganAI_Launcher.bat exists
$LauncherPath = Join-Path $DoganAIPath "DoganAI_Launcher.bat"
if (-not (Test-Path $LauncherPath)) {
    Write-Host "? Error: DoganAI_Launcher.bat not found at $LauncherPath" -ForegroundColor Red
    Write-Host "   Please run this script from the DoganAI-Compliance-Kit directory" -ForegroundColor Yellow
    exit 1
}

try {
    # Create WScript Shell object
    $WshShell = New-Object -comObject WScript.Shell
    
    # Define shortcut path on desktop
    $DesktopPath = [System.Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "DoganAI Compliance Kit.lnk"
    
    # Create shortcut
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "cmd.exe"
    $Shortcut.Arguments = "/c cd /d `"$DoganAIPath`" && DoganAI_Launcher.bat"
    $Shortcut.WorkingDirectory = $DoganAIPath
    $Shortcut.Description = "DoganAI Compliance Kit - Saudi Arabia Enterprise Compliance Solution"
    $Shortcut.WindowStyle = 1  # Normal window
    
    # Try to set custom icon (optional)
    $IconPath = Join-Path $DoganAIPath "doganai_icon.ico"
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = $IconPath
        Write-Host "? Custom icon applied" -ForegroundColor Green
    } else {
        # Use default cmd icon
        $Shortcut.IconLocation = "cmd.exe,0"
        Write-Host "?? Using default icon (custom icon not found)" -ForegroundColor Yellow
    }
    
    # Save the shortcut
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "? SUCCESS! Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host "?? Shortcut location: $ShortcutPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "?? How to use:" -ForegroundColor Yellow
    Write-Host "   1. Double-click the 'DoganAI Compliance Kit' icon on your desktop"
    Write-Host "   2. Choose from the menu options:"
    Write-Host "      • Quick Demo (option 1) - See performance improvements"
    Write-Host "      • Start API Server (option 2) - Launch web interface"
    Write-Host "      • Run Tests (option 3) - Performance testing"
    Write-Host "      • Setup (option 4) - Install dependencies"
    Write-Host ""
    Write-Host "?? Your DoganAI Compliance Kit is ready for one-click access!" -ForegroundColor Green
    
} catch {
    Write-Host "? Error creating shortcut: $_" -ForegroundColor Red
    Write-Host "   Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

# Optional: Open the desktop to show the new shortcut
$OpenDesktop = Read-Host "Would you like to open the desktop to see the new shortcut? (y/n)"
if ($OpenDesktop -eq 'y' -or $OpenDesktop -eq 'Y') {
    explorer.exe $DesktopPath
}