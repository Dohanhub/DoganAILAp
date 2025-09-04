$ErrorActionPreference = 'Stop'

function New-Shortcut {
    param(
        [Parameter(Mandatory)] [string]$Path,
        [Parameter(Mandatory)] [string]$TargetPath,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [string]$Description,
        [string]$IconLocation
    )

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Path)
    $shortcut.TargetPath = $TargetPath
    if ($Arguments) { $shortcut.Arguments = $Arguments }
    if ($WorkingDirectory) { $shortcut.WorkingDirectory = $WorkingDirectory }
    if ($Description) { $shortcut.Description = $Description }
    if ($IconLocation) { $shortcut.IconLocation = $IconLocation }
    $shortcut.Save()
}

$repoRoot = (Resolve-Path "$PSScriptRoot\..\").Path.TrimEnd('\')
$target = Join-Path $repoRoot 'Start-All.bat'
$iconPath = Join-Path $repoRoot 'docs\Ai-Dogan.ico'
$icon = if (Test-Path $iconPath) { $iconPath } else { "$env:SystemRoot\System32\shell32.dll,0" }

# Create on current user Desktop
$userDesktop = [Environment]::GetFolderPath('Desktop')
$userLink = Join-Path $userDesktop 'DoganAI Start All.lnk'
New-Shortcut -Path $userLink -TargetPath $target -WorkingDirectory $repoRoot -Description 'Start DoganAI API + Web (one click)' -IconLocation $icon
Write-Host "Created desktop shortcut: $userLink" -ForegroundColor Green

# Also create on Public Desktop (all users), best-effort
try {
    $publicDesktop = Join-Path $env:PUBLIC 'Desktop'
    if (Test-Path $publicDesktop) {
        $publicLink = Join-Path $publicDesktop 'DoganAI Start All.lnk'
        New-Shortcut -Path $publicLink -TargetPath $target -WorkingDirectory $repoRoot -Description 'Start DoganAI API + Web (one click)' -IconLocation $icon
        Write-Host "Created desktop shortcut for all users: $publicLink" -ForegroundColor Green
    }
} catch { }
