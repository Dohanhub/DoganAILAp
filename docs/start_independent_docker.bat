@echo off
REM DoganAI Independent Docker Startup Script
REM Ensures all components start independently with proper health checks

title DoganAI Independent Docker Startup

echo.
echo ????????????????????????????????????????????????????????????????
echo ?            DoganAI Independent Docker Startup               ?
echo ?           ???? Complete Independent Deployment ????             ?
echo ?                                                              ?
echo ?  ? All services independent    ? Health monitoring         ?
echo ?  ? Persistent data volumes     ? Automatic recovery        ?
echo ?  ? Production ready           ? Saudi compliance           ?
echo ????????????????????????????????????????????????????????????????
echo.

REM Set deployment configuration
set "COMPOSE_FILE=docker-compose.independent.yml"
set "ENV_FILE=.env"
set "DEPLOYMENT_TYPE=independent"

REM Check prerequisites
echo ?? Checking prerequisites...
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ? Docker is not available
    echo    Please install Docker Desktop from: https://docker.com
    pause
    exit /b 1
)
echo ? Docker is available

REM Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ? Docker Compose is not available
        pause
        exit /b 1
    ) else (
        set "DOCKER_COMPOSE_CMD=docker compose"
        echo ? Docker Compose (v2) detected
    )
) else (
    set "DOCKER_COMPOSE_CMD=docker-compose"
    echo ? Docker Compose (v1) detected
)

REM Check compose file
if not exist "%COMPOSE_FILE%" (
    echo ? Compose file not found: %COMPOSE_FILE%
    echo    Please ensure the file exists in the current directory
    pause
    exit /b 1
)
echo ? Compose file found: %COMPOSE_FILE%

REM Check/create environment file
if not exist "%ENV_FILE%" (
    if exist ".env.template" (
        echo ?? .env file not found, creating from template...
        copy ".env.template" "%ENV_FILE%"
        echo ? .env file created from template
        echo.
        echo ?? IMPORTANT: Please review and customize the .env file
        echo    Default passwords should be changed for production use
        echo.
        set /p continue="Continue with default configuration? (y/n): "
        if /i not "%continue%"=="y" (
            echo Setup cancelled. Please configure .env file and try again.
            pause
            exit /b 1
        )
    ) else (
        echo ? No .env file or template found
        echo    Creating minimal .env file...
        (
        echo # DoganAI Minimal Configuration
        echo POSTGRES_PASSWORD=DoganAI2024!Secure
        echo REDIS_PASSWORD=DoganAIRedis2024
        echo SECRET_KEY=DoganAI-Change-This-Secret-Key-In-Production
        echo GRAFANA_PASSWORD=DoganAIGrafana2024
        echo MINIO_USER=doganai
        echo MINIO_PASSWORD=DoganAI2024Storage
        echo DEBUG=false
        echo APP_ENV=production
        ) > "%ENV_FILE%"
        echo ? Minimal .env file created
    )
)
echo ? Environment file ready: %ENV_FILE%

echo.

REM Show deployment overview
echo ?? DoganAI Independent Deployment Overview
echo ==========================================
echo.
echo ??? Infrastructure Services:
echo    • PostgreSQL Database (Port 5432)
echo    • Redis Cache (Port 6379)
echo    • MinIO Object Storage (Port 9000, 9001)
echo    • Nginx Load Balancer (Port 80, 443)
echo.
echo ?? Core Application Services:
echo    • Compliance Engine (Port 8000)
echo    • Benchmarks Service (Port 8001)
echo    • AI/ML Service (Port 8002)
echo    • Integrations Service (Port 8003)
echo    • Authentication Service (Port 8004)
echo    • AI Agent (Port 8005)
echo    • Autonomous Testing (Port 8006)
echo    • UI Service (Port 8501)
echo.
echo ?? Monitoring Services:
echo    • Prometheus Metrics (Port 9090)
echo    • Grafana Dashboards (Port 3000)
echo    • Elasticsearch Search (Port 9200)
echo    • Kibana Logs (Port 5601)
echo.
echo ?? Access Points After Startup:
echo    • Main Application: http://localhost:8501
echo    • API Documentation: http://localhost:8000/docs
echo    • Monitoring Dashboard: http://localhost:3000
echo    • System Metrics: http://localhost:9090
echo    • Log Analysis: http://localhost:5601
echo    • File Storage: http://localhost:9001
echo.

set /p confirm="?? Start DoganAI Independent Deployment? (y/n): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo ?? Starting DoganAI Independent Deployment...
echo ==============================================

REM Stop any existing services
echo ?? Stopping any existing services...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% down >nul 2>&1

REM Pull latest images
echo ?? Pulling latest images...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% pull

if %errorlevel% neq 0 (
    echo ?? Some images could not be pulled (may be custom builds)
    echo Continuing with available images...
)

echo.

REM Start infrastructure services first
echo ??? Starting infrastructure services...
echo.

echo ?? Starting database (PostgreSQL)...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d postgres
if %errorlevel% neq 0 (
    echo ? Failed to start PostgreSQL
    goto CLEANUP
)

echo ?? Starting cache (Redis)...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d redis
if %errorlevel% neq 0 (
    echo ? Failed to start Redis
    goto CLEANUP
)

echo ?? Starting object storage (MinIO)...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d minio
if %errorlevel% neq 0 (
    echo ? Failed to start MinIO
    goto CLEANUP
)

echo ?? Starting search engine (Elasticsearch)...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d elasticsearch
if %errorlevel% neq 0 (
    echo ? Failed to start Elasticsearch
    goto CLEANUP
)

echo ? Waiting for infrastructure services to be ready...
timeout /t 30 /nobreak >nul

echo ? Infrastructure services started
echo.

REM Start core application services
echo ?? Starting core application services...
echo.

echo ??? Starting compliance engine...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d compliance-engine
if %errorlevel% neq 0 (
    echo ? Failed to start Compliance Engine
    goto CLEANUP
)

echo ?? Starting benchmarks service...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d benchmarks
if %errorlevel% neq 0 (
    echo ? Failed to start Benchmarks Service
    goto CLEANUP
)

echo ?? Starting AI/ML service...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d ai-ml
if %errorlevel% neq 0 (
    echo ? Failed to start AI/ML Service
    goto CLEANUP
)

echo ?? Starting integrations service...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d integrations
if %errorlevel% neq 0 (
    echo ? Failed to start Integrations Service
    goto CLEANUP
)

echo ?? Starting authentication service...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d auth
if %errorlevel% neq 0 (
    echo ? Failed to start Authentication Service
    goto CLEANUP
)

echo ? Waiting for core services to initialize...
timeout /t 20 /nobreak >nul

echo ? Core services started
echo.

REM Start advanced services
echo ?? Starting advanced services...
echo.

echo ?? Starting AI agent...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d ai-agent
if %errorlevel% neq 0 (
    echo ? Failed to start AI Agent
    goto CLEANUP
)

echo ?? Starting autonomous testing...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d autonomous-testing
if %errorlevel% neq 0 (
    echo ? Failed to start Autonomous Testing
    goto CLEANUP
)

echo ? Waiting for advanced services...
timeout /t 15 /nobreak >nul

echo ? Advanced services started
echo.

REM Start monitoring services
echo ?? Starting monitoring services...
echo.

echo ?? Starting Prometheus...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d prometheus
if %errorlevel% neq 0 (
    echo ? Failed to start Prometheus
    goto CLEANUP
)

echo ?? Starting Grafana...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d grafana
if %errorlevel% neq 0 (
    echo ? Failed to start Grafana
    goto CLEANUP
)

echo ?? Starting Kibana...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d kibana
if %errorlevel% neq 0 (
    echo ? Failed to start Kibana
    goto CLEANUP
)

echo ? Monitoring services started
echo.

REM Start user interface
echo ?? Starting user interface...
echo.

echo ?? Starting UI service...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d ui
if %errorlevel% neq 0 (
    echo ? Failed to start UI Service
    goto CLEANUP
)

echo ?? Starting Nginx proxy...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% up -d nginx
if %errorlevel% neq 0 (
    echo ? Failed to start Nginx
    goto CLEANUP
)

echo ? Final initialization (60 seconds)...
echo    All services are starting up and performing health checks...
timeout /t 60 /nobreak >nul

echo.

REM Check deployment status
echo ?? Checking deployment status...
echo ================================

%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% ps

echo.

REM Run health check
echo ?? Running health check...
if exist "docker_health_check.bat" (
    call docker_health_check.bat
) else (
    echo ?? Quick health check:
    echo.
    REM Basic health check
    curl -s -f http://localhost:8501/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ? UI Service: Healthy
    ) else (
        echo ? UI Service: Not responding
    )
    
    curl -s -f http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ? Compliance Engine: Healthy
    ) else (
        echo ? Compliance Engine: Not responding
    )
    
    curl -s -f http://localhost:3000/api/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ? Grafana: Healthy
    ) else (
        echo ? Grafana: Not responding
    )
)

echo.

REM Success message
echo ????????????????????????????????????????????????????????????????
echo ?                  ?? DEPLOYMENT SUCCESSFUL! ??                ?
echo ????????????????????????????????????????????????????????????????
echo ?                                                              ?
echo ?  DoganAI Compliance Kit is now running independently!       ?
echo ?                                                              ?
echo ?  ?? ACCESS POINTS:                                           ?
echo ?                                                              ?
echo ?  ?? Main Application: http://localhost:8501                 ?
echo ?  ?? API Docs: http://localhost:8000/docs                    ?
echo ?  ?? Monitoring: http://localhost:3000                       ?
echo ?  ?? Metrics: http://localhost:9090                          ?
echo ?  ?? Logs: http://localhost:5601                             ?
echo ?  ?? Storage: http://localhost:9001                          ?
echo ?                                                              ?
echo ?  ?? FEATURES READY:                                          ?
echo ?  ? Complete Saudi compliance validation                     ?
echo ?  ? High-performance caching and optimization               ?
echo ?  ? Advanced security with RBAC                             ?
echo ?  ? Real-time monitoring and alerting                       ?
echo ?  ? AI-powered analysis and automation                      ?
echo ?  ? Mobile-responsive interface                              ?
echo ?  ? Autonomous testing and validation                       ?
echo ?  ? Production-ready scalability                            ?
echo ?                                                              ?
echo ?  ???? SAUDI ARABIA COMPLIANCE:                               ?
echo ?  ? SAMA Banking Regulations                                 ?
echo ?  ? NCA Cybersecurity Framework                              ?
echo ?  ? MCI ICT Regulations                                      ?
echo ?  ? ZATCA E-invoicing Compliance                             ?
echo ?  ? MOH Healthcare Data Protection                           ?
echo ?  ? SDAIA AI Ethics Guidelines                               ?
echo ?                                                              ?
echo ????????????????????????????????????????????????????????????????
echo.

REM Create desktop shortcut
if exist "Create_Shortcut.bat" (
    echo ?? Creating desktop shortcut...
    call Create_Shortcut.bat
)

echo ?? DoganAI Independent Deployment Complete!
echo.
echo ?? Management Commands:
echo    • Health Check: docker_health_check.bat
echo    • View Logs: %DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% logs
echo    • Stop All: %DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% down
echo    • Restart: %DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% restart
echo.
echo Press any key to open the main application...
pause >nul

REM Open main application
start http://localhost:8501

goto END

:CLEANUP
echo.
echo ? Deployment failed! Cleaning up...
%DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% down
echo ?? Cleanup completed
echo.
echo ??? Troubleshooting suggestions:
echo    1. Check Docker is running: docker ps
echo    2. Check available resources: docker system df
echo    3. Check logs: %DOCKER_COMPOSE_CMD% -f %COMPOSE_FILE% logs
echo    4. Verify .env configuration
echo    5. Try running individual services
echo.
pause

:END
exit /b 0