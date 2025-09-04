@echo off
echo Starting DoganAI Compliance Kit Docker Deployment...

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and start it first
    pause
    exit /b 1
)

echo Docker is available, proceeding with deployment...

REM Stop any existing containers
echo Stopping existing containers...
docker-compose down

REM Build and start services
echo Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo Waiting for services to start...
timeout /t 30 /nobreak

REM Check service status
echo Checking service status...
docker-compose ps

REM Show logs
echo Recent logs:
docker-compose logs --tail=50

echo.
echo ========================================
echo DoganAI Compliance Kit is now running!
echo ========================================
echo Frontend: http://localhost:3001
echo Backend API: http://localhost:8000
echo PgAdmin: http://localhost:5050
echo ========================================
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
echo.
pause
