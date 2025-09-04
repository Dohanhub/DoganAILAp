@echo off
REM DoganAI Independent Docker Health Check Script (Windows)
REM This script validates that all Docker services are running independently

title DoganAI Docker Health Check

echo.
echo ?? DoganAI Independent Docker Health Check
echo ==========================================
echo ?? %date% %time%
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ? Docker is not installed or not in PATH
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
        echo ? Docker Compose (v2) is available
        set "DOCKER_COMPOSE_CMD=docker compose"
    )
) else (
    echo ? Docker Compose (v1) is available
    set "DOCKER_COMPOSE_CMD=docker-compose"
)

echo.

REM Check compose file
if not exist "docker-compose.independent.yml" (
    echo ? docker-compose.independent.yml not found
    echo    Please ensure the file exists in the current directory
    pause
    exit /b 1
)
echo ? Docker Compose file found
echo.

REM Check container status
echo ?? Checking container status...
echo ================================
%DOCKER_COMPOSE_CMD% -f docker-compose.independent.yml ps
echo.

REM Check service health
echo ?? Checking service health...
echo ==============================

set "total_services=0"
set "healthy_services=0"

REM Define services and ports to check
set "services=postgres:5432 redis:6379 minio:9000 compliance-engine:8000 benchmarks:8001 ai-ml:8002 integrations:8003 auth:8004 ai-agent:8005 autonomous-testing:8006 ui:8501 nginx:80 prometheus:9090 grafana:3000 elasticsearch:9200 kibana:5601"

for %%s in (%services%) do (
    set /a total_services+=1
    
    for /f "tokens=1,2 delims=:" %%a in ("%%s") do (
        set "service=%%a"
        set "port=%%b"
        
        echo|set /p="?? %%a: "
        
        REM Check if container is running
        %DOCKER_COMPOSE_CMD% -f docker-compose.independent.yml ps %%a | findstr /c:"Up" >nul 2>&1
        if !errorlevel! equ 0 (
            REM Check if port is responding
            powershell -command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('localhost', %%b); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
            if !errorlevel! equ 0 (
                echo ? Healthy (port %%b responding^)
                set /a healthy_services+=1
            ) else (
                echo ?? Running but port %%b not responding
            )
        ) else (
            echo ? Not running
        )
    )
)

echo.

REM Health check summary
echo ?? Health Check Summary
echo =======================
echo Total services: %total_services%
echo Healthy services: %healthy_services%
set /a unhealthy_services=%total_services%-%healthy_services%
echo Unhealthy services: %unhealthy_services%

set /a health_percentage=%healthy_services%*100/%total_services%
echo Health percentage: %health_percentage%%%

if %health_percentage% geq 90 (
    echo ?? Excellent health! All systems operational
) else if %health_percentage% geq 75 (
    echo ? Good health! Minor issues detected
) else if %health_percentage% geq 50 (
    echo ?? Moderate health! Some services need attention
) else (
    echo ? Poor health! Multiple services failing
)

echo.

REM Check resource usage
echo ?? Resource Usage
echo ==================
echo ?? Container resource usage:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>nul || echo No containers found
echo.

REM Check volumes
echo ?? Volume Status
echo ================
echo ?? DoganAI volumes:
docker volume ls | findstr doganai || echo No DoganAI volumes found
echo.

REM Check networks
echo ?? Network Status
echo ==================
echo ?? DoganAI networks:
docker network ls | findstr doganai || echo No DoganAI networks found
echo.

REM API endpoint checks
echo ?? API Endpoint Checks
echo =======================

set "working_endpoints=0"
set "total_endpoints=0"

set "endpoints=8000:/health:Compliance_Engine 8001:/health:Benchmarks 8002:/health:AI_ML 8003:/health:Integrations 8004:/health:Authentication 8005:/health:AI_Agent 8006:/health:Autonomous_Testing 8501:/health:UI_Service 9090:/-/healthy:Prometheus 3000:/api/health:Grafana 9200:/_cluster/health:Elasticsearch"

for %%e in (%endpoints%) do (
    set /a total_endpoints+=1
    
    for /f "tokens=1,2,3 delims=:" %%a in ("%%e") do (
        set "port=%%a"
        set "path=%%b"
        set "description=%%c"
        
        echo|set /p="?? %%c: "
        
        REM Use curl to check endpoint
        curl -s -f "http://localhost:%%a%%b" >nul 2>&1
        if !errorlevel! equ 0 (
            echo ? Responding
            set /a working_endpoints+=1
        ) else (
            echo ? Not responding
        )
    )
)

echo.
echo ?? API Endpoint Summary:
echo Working endpoints: %working_endpoints%/%total_endpoints%
set /a endpoint_percentage=%working_endpoints%*100/%total_endpoints%
echo Endpoint health: %endpoint_percentage%%%
echo.

REM Overall system health
echo ?? Overall System Health
echo =========================
set /a overall_health=(%health_percentage%+%endpoint_percentage%)/2
echo Overall health score: %overall_health%%%

if %overall_health% geq 90 (
    echo ?? DoganAI is running excellently!
    echo ? Ready for production workloads
) else if %overall_health% geq 75 (
    echo ? DoganAI is running well with minor issues
    echo ?? Some fine-tuning recommended
) else if %overall_health% geq 50 (
    echo ?? DoganAI has moderate issues
    echo ??? Troubleshooting required
) else (
    echo ? DoganAI has significant issues
    echo ?? Immediate attention required
)

echo.

REM Quick access information
echo ?? Quick Access URLs
echo ====================
echo Main UI: http://localhost:8501
echo API Documentation: http://localhost:8000/docs
echo Grafana Dashboard: http://localhost:3000
echo Prometheus Metrics: http://localhost:9090
echo Kibana Logs: http://localhost:5601
echo MinIO Console: http://localhost:9001
echo.

REM Troubleshooting suggestions
if %overall_health% lss 75 (
    echo ??? Troubleshooting Suggestions
    echo ===============================
    echo 1. Check logs: %DOCKER_COMPOSE_CMD% -f docker-compose.independent.yml logs
    echo 2. Restart services: %DOCKER_COMPOSE_CMD% -f docker-compose.independent.yml restart
    echo 3. Check resource usage: docker stats
    echo 4. Verify .env configuration
    echo 5. Check disk space
    echo 6. Check available memory
    echo.
)

REM Save results to file
set "timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "report_file=docker_health_report_%timestamp%.txt"

(
echo DoganAI Docker Health Report
echo Generated: %date% %time%
echo Overall Health: %overall_health%%%
echo Container Health: %health_percentage%%%
echo Endpoint Health: %endpoint_percentage%%%
echo Healthy Services: %healthy_services%/%total_services%
echo Working Endpoints: %working_endpoints%/%total_endpoints%
) > "%report_file%"

echo ?? Health report saved to: %report_file%
echo.

echo Press any key to continue...
pause >nul