@echo off
REM DoganAI Compliance Kit - Internal Folder Deployment Script (Windows)
REM This script creates a self-contained deployment in any folder

setlocal enabledelayedexpansion

set "DEPLOYMENT_NAME=doganai-compliance-kit"
set "DEFAULT_PORT=8080"
set "DEFAULT_DB_PORT=5433"
set "DEFAULT_REDIS_PORT=6380"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              DoganAI Compliance Kit                          ║
echo ║              Internal Deployment Setup                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if deployment directory is provided
if "%~1"=="" (
    set "DEPLOYMENT_DIR=doganai-internal-deployment"
) else (
    set "DEPLOYMENT_DIR=%~1"
)

echo [INFO] Setting up DoganAI Compliance Kit internal deployment...
echo [INFO] Deployment directory: %DEPLOYMENT_DIR%

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

echo [SUCCESS] Docker is available and running!

REM Create deployment directory structure
echo [INFO] Creating deployment folder: %DEPLOYMENT_DIR%
mkdir "%DEPLOYMENT_DIR%" 2>nul
mkdir "%DEPLOYMENT_DIR%\data\postgres" 2>nul
mkdir "%DEPLOYMENT_DIR%\data\redis" 2>nul
mkdir "%DEPLOYMENT_DIR%\logs" 2>nul
mkdir "%DEPLOYMENT_DIR%\config" 2>nul
mkdir "%DEPLOYMENT_DIR%\scripts" 2>nul

REM Create .env file
echo [INFO] Creating environment configuration...
(
echo # DoganAI Compliance Kit - Internal Deployment Configuration
echo.
echo # Application Settings
echo APP_NAME=DoganAI Compliance Kit
echo APP_ENVIRONMENT=production
echo SECRET_KEY=your-secret-key-change-this-in-production
echo API_V1_STR=/api/v1
echo.
echo # Database Configuration
echo POSTGRES_SERVER=db
echo POSTGRES_USER=doganai_user
echo POSTGRES_PASSWORD=doganai_secure_password_2024
echo POSTGRES_DB=doganai_compliance
echo DATABASE_URL=postgresql://doganai_user:doganai_secure_password_2024@db:5432/doganai_compliance
echo.
echo # Redis Configuration
echo REDIS_URL=redis://redis:6379/0
echo.
echo # Security Settings
echo ACCESS_TOKEN_EXPIRE_MINUTES=1440
echo ALGORITHM=HS256
echo.
echo # CORS Settings
echo BACKEND_CORS_ORIGINS=["*"]
echo.
echo # Logging
echo LOG_LEVEL=INFO
echo LOG_FORMAT=%%(asctime^)s - %%(name^)s - %%(levelname^)s - %%(message^)s
echo.
echo # Monitoring
echo ENABLE_METRICS=true
echo METRICS_PORT=9090
) > "%DEPLOYMENT_DIR%\.env"

REM Create Docker Compose file
echo [INFO] Creating Docker Compose configuration...
(
echo version: '3.8'
echo.
echo services:
echo   app:
echo     image: doganai/compliance-kit:latest
echo     container_name: %DEPLOYMENT_NAME%-app
echo     restart: unless-stopped
echo     ports:
echo       - "%DEFAULT_PORT%:8000"
echo     environment:
echo       - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
echo       - REDIS_URL=redis://redis:6379/0
echo       - APP_ENVIRONMENT=production
echo     env_file:
echo       - .env
echo     depends_on:
echo       db:
echo         condition: service_healthy
echo       redis:
echo         condition: service_healthy
echo     healthcheck:
echo       test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
echo       interval: 30s
echo       timeout: 10s
echo       retries: 3
echo       start_period: 40s
echo     volumes:
echo       - ./logs:/app/logs
echo       - ./config:/app/config:ro
echo     networks:
echo       - doganai-network
echo.
echo   db:
echo     image: postgres:15-alpine
echo     container_name: %DEPLOYMENT_NAME%-postgres
echo     restart: unless-stopped
echo     environment:
echo       - POSTGRES_USER=${POSTGRES_USER}
echo       - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
echo       - POSTGRES_DB=${POSTGRES_DB}
echo     volumes:
echo       - ./data/postgres:/var/lib/postgresql/data
echo     ports:
echo       - "%DEFAULT_DB_PORT%:5432"
echo     healthcheck:
echo       test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
echo       interval: 10s
echo       timeout: 5s
echo       retries: 5
echo     networks:
echo       - doganai-network
echo.
echo   redis:
echo     image: redis:7-alpine
echo     container_name: %DEPLOYMENT_NAME%-redis
echo     restart: unless-stopped
echo     command: redis-server --appendonly yes
echo     volumes:
echo       - ./data/redis:/data
echo     ports:
echo       - "%DEFAULT_REDIS_PORT%:6379"
echo     healthcheck:
echo       test: ["CMD", "redis-cli", "ping"]
echo       interval: 10s
echo       timeout: 5s
echo       retries: 3
echo     networks:
echo       - doganai-network
echo.
echo networks:
echo   doganai-network:
echo     driver: bridge
echo     name: %DEPLOYMENT_NAME%-network
) > "%DEPLOYMENT_DIR%\docker-compose.yml"

REM Create management scripts
echo [INFO] Creating management scripts...

REM Start script
(
echo @echo off
echo echo Starting DoganAI Compliance Kit...
echo docker-compose up -d
echo echo Services started! Application available at: http://localhost:%DEFAULT_PORT%
echo echo API Documentation: http://localhost:%DEFAULT_PORT%/docs
) > "%DEPLOYMENT_DIR%\start.bat"

REM Stop script
(
echo @echo off
echo echo Stopping DoganAI Compliance Kit...
echo docker-compose down
echo echo Services stopped!
) > "%DEPLOYMENT_DIR%\stop.bat"

REM Status script
(
echo @echo off
echo echo DoganAI Compliance Kit Status:
echo docker-compose ps
echo echo.
echo echo Health Check:
echo powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:%DEFAULT_PORT%/health' } catch { Write-Host 'Application not responding' -ForegroundColor Red }"
) > "%DEPLOYMENT_DIR%\status.bat"

REM Logs script
(
echo @echo off
echo if "%%1"=="" ^(
echo     echo Showing all logs...
echo     docker-compose logs -f
echo ^) else ^(
echo     echo Showing logs for service: %%1
echo     docker-compose logs -f %%1
echo ^)
) > "%DEPLOYMENT_DIR%\logs.bat"

REM Backup script
(
echo @echo off
echo set BACKUP_DIR=backups\%%date:~10,4%%%%date:~4,2%%%%date:~7,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%
echo set BACKUP_DIR=%%BACKUP_DIR: =0%%
echo mkdir "%%BACKUP_DIR%%" 2^>nul
echo echo Creating backup in: %%BACKUP_DIR%%
echo docker-compose exec -T db pg_dump -U doganai_user doganai_compliance ^> "%%BACKUP_DIR%%\database.sql"
echo xcopy config "%%BACKUP_DIR%%\config\" /E /I /Q ^>nul
echo copy .env "%%BACKUP_DIR%%\" ^>nul
echo echo Backup completed: %%BACKUP_DIR%%
) > "%DEPLOYMENT_DIR%\backup.bat"

REM Update script
(
echo @echo off
echo echo Updating DoganAI Compliance Kit...
echo docker-compose pull
echo docker-compose up -d
echo echo Update completed!
) > "%DEPLOYMENT_DIR%\update.bat"

REM Create README
echo [INFO] Creating documentation...
(
echo # DoganAI Compliance Kit - Internal Deployment
echo.
echo This is a self-contained deployment of the DoganAI Compliance Kit for internal use.
echo.
echo ## Quick Start
echo.
echo 1. **Start the application:**
echo    ```
echo    start.bat
echo    ```
echo.
echo 2. **Access the application:**
echo    - Main Application: http://localhost:%DEFAULT_PORT%
echo    - API Documentation: http://localhost:%DEFAULT_PORT%/docs
echo    - Health Check: http://localhost:%DEFAULT_PORT%/health
echo.
echo 3. **Access databases:**
echo    - PostgreSQL: localhost:%DEFAULT_DB_PORT%
echo    - Redis: localhost:%DEFAULT_REDIS_PORT%
echo.
echo ## Management Commands
echo.
echo - **Start services:** `start.bat`
echo - **Stop services:** `stop.bat`
echo - **Check status:** `status.bat`
echo - **View logs:** `logs.bat [service_name]`
echo - **Create backup:** `backup.bat`
echo - **Update application:** `update.bat`
echo.
echo ## Configuration
echo.
echo - **Environment variables:** Edit `.env`
echo - **Docker services:** Edit `docker-compose.yml`
echo.
echo ## Data Persistence
echo.
echo All data is stored in the `data\` directory:
echo - `data\postgres\` - Database files
echo - `data\redis\` - Redis data
echo - `logs\` - Application logs
echo.
echo ## Security Notes
echo.
echo 1. Change the default passwords in `.env`
echo 2. Update the SECRET_KEY in `.env`
echo 3. Review firewall settings for internal network access
echo 4. Regular backups are recommended
echo.
echo ## Troubleshooting
echo.
echo 1. **Check service status:** `status.bat`
echo 2. **View logs:** `logs.bat`
echo 3. **Restart services:** `stop.bat` then `start.bat`
echo 4. **Reset data:** Remove `data\` directory and restart
) > "%DEPLOYMENT_DIR%\README.md"

echo [SUCCESS] Internal deployment setup completed!
echo.
echo [INFO] Next steps:
echo 1. cd %DEPLOYMENT_DIR%
echo 2. Review and update .env file with your settings
echo 3. start.bat
echo.
echo [INFO] The application will be available at:
echo - Main App: http://localhost:%DEFAULT_PORT%
echo - API Docs: http://localhost:%DEFAULT_PORT%/docs
echo - Database: localhost:%DEFAULT_DB_PORT%
echo - Redis: localhost:%DEFAULT_REDIS_PORT%
echo.

pause
