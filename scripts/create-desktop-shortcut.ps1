$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$shortcutName = 'DoganAI Compliance Kit.lnk'
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop $shortcutName

$target = 'powershell.exe'
$args = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$repoRoot\scripts\run-app.ps1`""

$shell = New-Object -ComObject WScript.Shell
$sc = $shell.CreateShortcut($shortcutPath)
$sc.TargetPath = $target
$sc.Arguments = $args
$sc.WorkingDirectory = $repoRoot
$sc.WindowStyle = 1
$sc.IconLocation = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe,0'
$sc.Description = 'Start DoganAI Compliance Kit (Docker Compose)'
$sc.Save()

Write-Host "Created shortcut: $shortcutPath" -ForegroundColor Green

