@echo off
setlocal ENABLEDELAYEDEXPANSION
title DoganAI Compliance Kit - Local App

:: Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Python is required (3.11+). Please install from https://www.python.org/downloads/
  pause
  exit /b 1
)

:: Create virtual environment
set VENV=.runenv
if not exist %VENV% (
  echo Creating virtual environment in %VENV% ...
  python -m venv %VENV%
)

:: Activate venv and install deps
call %VENV%\Scripts\activate.bat
python -m pip install --upgrade pip >nul
if exist requirements.lock.txt (
  echo Installing dependencies (locked)...
  pip install --require-hashes -r requirements.lock.txt || goto :fallback
) else (
  goto :fallback
)
goto :after_install

:fallback
echo Installing dependencies (requirements-api.txt)...
pip install -r requirements-api.txt || (
  echo Failed to install dependencies.
  pause
  exit /b 1
)

:after_install
:: Environment for local development
set ENV=development
set ENVIRONMENT=development
set ALLOW_SQLITE=true
set SECRET_KEY=dev-secret-please-change
set API_KEY=dev-api-key
set ALLOWED_ORIGINS=*
set REQUIRE_REDIS_FOR_RATELIMIT=false
set ALLOWED_OUTBOUND_HOSTS=.github.com,example.com

:: Start the app
echo.
echo Starting DoganAI Compliance API at http://127.0.0.1:8000 ...
start "Open App" Open-App.url
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
if %ERRORLEVEL% NEQ 0 (
  echo App exited with error code %ERRORLEVEL%.
  pause
)
exit /b 0

