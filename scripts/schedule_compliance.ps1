$ErrorActionPreference = 'Stop'
param(
  [Parameter(Mandatory)] [string]$Standard,
  [string]$ApiBase = 'http://localhost:8010',
  [string]$ApiKey = '',
  [string]$Time = '08:00'
)

$taskName = "DoganAI-Compliance-Run-$Standard"
$script = @"


$Headers = @{}
if ('$ApiKey' -ne '') { $Headers['X-API-Key'] = '$ApiKey' }

try {
  Invoke-RestMethod -Method Post -Uri "$ApiBase/api/compliance/run/$Standard" -Headers $Headers | Out-Null
} catch {}

"@

$tmp = Join-Path $env:TEMP "$taskName.ps1"
$script | Set-Content -Path $tmp -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$tmp`""
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::ParseExact($Time, 'HH:mm', $null).TimeOfDay)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Run DoganAI compliance for $Standard" -Force | Out-Null

Write-Host "Scheduled daily compliance run for $Standard at $Time" -ForegroundColor Green

