@echo off
setlocal
cd /d %~dp0
rem Ensure Desktop shortcut is present for current user and Public
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\create_start_all_shortcut.ps1" 1>nul 2>nul
rem Run bootstrap (starts API + Web and opens browser)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\bootstrap.ps1"
endlocal
