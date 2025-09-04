@echo off
REM DoganAI Compliance Kit - Docker Startup Script (Windows)
REM This script provides easy commands to manage the Docker environment

setlocal enabledelayedexpansion

set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "NC=[0m"

:main
if "%~1"=="build" goto build
if "%~1"=="start" goto start
if "%~1"=="start-monitoring" goto start_monitoring
if "%~1"=="stop" goto stop
if "%~1"=="restart" goto restart
if "%~1"=="logs" goto logs
if "%~1"=="status" goto status
if "%~1"=="migrate" goto migrate
if "%~1"=="shell" goto shell
if "%~1"=="backup" goto backup
if "%~1"=="clean" goto clean
if "%~1"=="help" goto help
goto help

:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Docker is not running. Please start Docker Desktop first.
    exit /b 1
)
goto :eof

:check_env
if not exist ".env" (
    echo %YELLOW%[WARNING]%NC% .env file not found. Creating from template...
    if exist ".env.template" (
        copy ".env.template" ".env" >nul
        echo %GREEN%[SUCCESS]%NC% .env file created from template. Please review and update the values.
    ) else (
        echo %RED%[ERROR]%NC% .env.template not found. Please create .env file manually.
        exit /b 1
    )
)
goto :eof

:build
call :check_docker
echo %BLUE%[INFO]%NC% Building DoganAI Compliance Kit Docker image...
docker build -t doganai-compliance-kit:latest .
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Docker build failed!
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Docker image built successfully!
goto :eof

:start
call :check_docker
call :check_env
echo %BLUE%[INFO]%NC% Starting DoganAI Compliance Kit services...
docker-compose -f docker-compose.production.yml up -d
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to start services!
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Services started successfully!
echo %BLUE%[INFO]%NC% Application will be available at: http://localhost:8000
echo %BLUE%[INFO]%NC% Database (PostgreSQL) available at: localhost:5432
echo %BLUE%[INFO]%NC% Cache (Redis) available at: localhost:6379
goto :eof

:start_monitoring
call :check_docker
call :check_env
echo %BLUE%[INFO]%NC% Starting services with monitoring stack...
docker-compose -f docker-compose.production.yml --profile monitoring up -d
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to start services with monitoring!
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Services with monitoring started successfully!
echo %BLUE%[INFO]%NC% Application: http://localhost:8000
echo %BLUE%[INFO]%NC% Grafana Dashboard: http://localhost:3000 (admin/admin)
echo %BLUE%[INFO]%NC% Prometheus: http://localhost:9090
goto :eof

:stop
call :check_docker
echo %BLUE%[INFO]%NC% Stopping DoganAI Compliance Kit services...
docker-compose -f docker-compose.production.yml down
echo %GREEN%[SUCCESS]%NC% Services stopped successfully!
goto :eof

:restart
call :check_docker
echo %BLUE%[INFO]%NC% Restarting DoganAI Compliance Kit services...
call :stop
call :start
goto :eof

:logs
call :check_docker
docker-compose -f docker-compose.production.yml logs -f
goto :eof

:status
call :check_docker
echo %BLUE%[INFO]%NC% Service Status:
docker-compose -f docker-compose.production.yml ps
echo.
echo %BLUE%[INFO]%NC% Health Status:
docker-compose -f docker-compose.production.yml exec app curl -s http://localhost:8000/health
if errorlevel 1 echo %YELLOW%[WARNING]%NC% Application health check failed
goto :eof

:migrate
call :check_docker
echo %BLUE%[INFO]%NC% Running database migrations...
docker-compose -f docker-compose.production.yml exec app alembic upgrade head
echo %GREEN%[SUCCESS]%NC% Database migrations completed!
goto :eof

:shell
call :check_docker
echo %BLUE%[INFO]%NC% Opening shell in application container...
docker-compose -f docker-compose.production.yml exec app /bin/bash
goto :eof

:backup
call :check_docker
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
set backup_file=backup_%mydate%_%mytime%.sql
echo %BLUE%[INFO]%NC% Creating database backup: %backup_file%
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U postgres compliance_kit > %backup_file%
echo %GREEN%[SUCCESS]%NC% Database backup created: %backup_file%
goto :eof

:clean
call :check_docker
echo %YELLOW%[WARNING]%NC% This will remove all containers, images, and volumes. Are you sure? (y/N)
set /p response=
if /i "%response%"=="y" (
    echo %BLUE%[INFO]%NC% Cleaning up Docker environment...
    docker-compose -f docker-compose.production.yml down -v --rmi all
    docker system prune -f
    echo %GREEN%[SUCCESS]%NC% Docker environment cleaned up!
) else (
    echo %BLUE%[INFO]%NC% Clean up cancelled.
)
goto :eof

:help
echo DoganAI Compliance Kit - Docker Management Script
echo.
echo Usage: %~0 [COMMAND]
echo.
echo Commands:
echo   build           Build the Docker image
echo   start           Start all services
echo   start-monitoring Start services with monitoring stack
echo   stop            Stop all services
echo   restart         Restart all services
echo   logs            View service logs
echo   status          Show service status
echo   migrate         Run database migrations
echo   shell           Open shell in app container
echo   backup          Backup the database
echo   clean           Clean up all Docker resources
echo   help            Show this help message
echo.
echo Examples:
echo   %~0 build
echo   %~0 start
echo   %~0 start-monitoring
echo   %~0 logs
goto :eof
