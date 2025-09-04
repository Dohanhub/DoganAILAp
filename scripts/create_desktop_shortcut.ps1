# Create Desktop Shortcut for DoganAI Compliance Kit
# This version doesn't require admin rights

$ErrorActionPreference = 'Continue'

# Get the repository root path
$repoRoot = (Resolve-Path "$PSScriptRoot\..\").Path.TrimEnd('\')
$target = Join-Path $repoRoot 'Start-All-Fixed.bat'

# Check if the target file exists
if (-not (Test-Path $target)) {
    Write-Host "ERROR: Start-All-Fixed.bat not found at: $target" -ForegroundColor Red
    exit 1
}

# Get desktop path for current user
$userDesktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $userDesktop 'DoganAI Compliance Kit.lnk'

# Create the shortcut
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $target
    $Shortcut.WorkingDirectory = $repoRoot
    $Shortcut.Description = "Start DoganAI Compliance Kit - One Click Launch"
    
    # Try to set an icon (optional)
    $iconPath = Join-Path $repoRoot 'docs\Ai-Dogan.ico'
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = $iconPath
    } else {
        $Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,0"
    }
    
    $Shortcut.Save()
    
    Write-Host "✓ Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host "Location: $shortcutPath" -ForegroundColor Cyan
    Write-Host "`nYou can now double-click the 'DoganAI Compliance Kit' icon on your desktop!" -ForegroundColor Yellow
    
} catch {
    Write-Host "ERROR: Could not create desktop shortcut: $_" -ForegroundColor Red
    Write-Host "`nAlternative: Right-click on Start-All-Fixed.bat and select 'Create shortcut'" -ForegroundColor Yellow
}

# Also create a simple batch file that can be run from anywhere
$simpleBatch = Join-Path $repoRoot 'Launch-DoganAI.bat'
@"
@echo off
cd /d "$repoRoot"
call Start-All-Fixed.bat
pause
"@ | Out-File -FilePath $simpleBatch -Encoding ASCII

Write-Host "`n✓ Also created: Launch-DoganAI.bat" -ForegroundColor Green
Write-Host "You can also double-click this file to start the application" -ForegroundColor Cyan
