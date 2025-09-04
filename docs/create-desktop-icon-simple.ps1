# Create Enhanced Desktop Icon for DoganAI Compliance Kit
Write-Host "Creating Enhanced Desktop Icon for DoganAI Compliance Kit..." -ForegroundColor Green

# Desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Create the shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\DoganAI Compliance Kit.lnk")

# Set the target URL
$Shortcut.TargetPath = "http://localhost:8501"

# Set the working directory
$Shortcut.WorkingDirectory = $PWD

# Set the icon (using a default browser icon)
$Shortcut.IconLocation = "C:\Windows\System32\SHELL32.dll,1"

# Set description
$Shortcut.Description = "DoganAI Compliance Kit - KSA Regulatory Compliance Platform"

# Save the shortcut
$Shortcut.Save()

Write-Host "Desktop icon created successfully!" -ForegroundColor Green
Write-Host "Location: $DesktopPath\DoganAI Compliance Kit.lnk" -ForegroundColor Yellow
Write-Host "Target: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Double-click to open your compliance platform!" -ForegroundColor Cyan
