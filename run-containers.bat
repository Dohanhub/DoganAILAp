@echo off
echo Building and running DoganAI Compliance Kit in containers...
echo.

REM Stop any existing containers
docker-compose -f docker-compose.dev.yml down

REM Build and start containers
echo Building containers...
docker-compose -f docker-compose.dev.yml build

echo Starting containers...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo Containers are starting...
echo Frontend UI: http://localhost:3001
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Database: localhost:5432
echo.
echo To view logs: docker-compose -f docker-compose.dev.yml logs -f
echo To stop: docker-compose -f docker-compose.dev.yml down
echo.
pause
