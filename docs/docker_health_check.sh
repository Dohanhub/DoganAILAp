#!/bin/bash
# DoganAI Independent Docker Health Check Script
# This script validates that all Docker services are running independently

echo "?? DoganAI Independent Docker Health Check"
echo "=========================================="
echo "?? $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}? Docker is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}? Docker is available${NC}"

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}? Docker Compose (v1) is available${NC}"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo -e "${GREEN}? Docker Compose (v2) is available${NC}"
else
    echo -e "${RED}? Docker Compose is not available${NC}"
    exit 1
fi

echo ""

# Check if compose file exists
if [ ! -f "docker-compose.independent.yml" ]; then
    echo -e "${RED}? docker-compose.independent.yml not found${NC}"
    exit 1
fi

echo -e "${GREEN}? Docker Compose file found${NC}"
echo ""

# Define services to check
SERVICES=(
    "postgres:5432"
    "redis:6379"
    "minio:9000"
    "compliance-engine:8000"
    "benchmarks:8001"
    "ai-ml:8002"
    "integrations:8003"
    "auth:8004"
    "ai-agent:8005"
    "autonomous-testing:8006"
    "ui:8501"
    "nginx:80"
    "prometheus:9090"
    "grafana:3000"
    "elasticsearch:9200"
    "kibana:5601"
)

# Check container status
echo "?? Checking container status..."
echo "================================"

$DOCKER_COMPOSE_CMD -f docker-compose.independent.yml ps

echo ""

# Check service health
echo "?? Checking service health..."
echo "=============================="

total_services=0
healthy_services=0

for service_port in "${SERVICES[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)
    
    total_services=$((total_services + 1))
    
    # Check if container is running
    if $DOCKER_COMPOSE_CMD -f docker-compose.independent.yml ps $service | grep -q "Up"; then
        echo -ne "${BLUE}?? $service:${NC} "
        
        # Check if port is responding
        if timeout 5s bash -c "</dev/tcp/localhost/$port" 2>/dev/null; then
            echo -e "${GREEN}? Healthy (port $port responding)${NC}"
            healthy_services=$((healthy_services + 1))
        else
            echo -e "${YELLOW}??  Running but port $port not responding${NC}"
        fi
    else
        echo -e "${BLUE}?? $service:${NC} ${RED}? Not running${NC}"
    fi
done

echo ""

# Health check summary
echo "?? Health Check Summary"
echo "======================="
echo -e "Total services: ${BLUE}$total_services${NC}"
echo -e "Healthy services: ${GREEN}$healthy_services${NC}"
echo -e "Unhealthy services: ${RED}$((total_services - healthy_services))${NC}"

health_percentage=$((healthy_services * 100 / total_services))
echo -e "Health percentage: ${BLUE}$health_percentage%${NC}"

if [ $health_percentage -ge 90 ]; then
    echo -e "${GREEN}?? Excellent health! All systems operational${NC}"
elif [ $health_percentage -ge 75 ]; then
    echo -e "${YELLOW}? Good health! Minor issues detected${NC}"
elif [ $health_percentage -ge 50 ]; then
    echo -e "${YELLOW}??  Moderate health! Some services need attention${NC}"
else
    echo -e "${RED}? Poor health! Multiple services failing${NC}"
fi

echo ""

# Check resource usage
echo "?? Resource Usage"
echo "=================="

echo "?? Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" $(docker ps --format "{{.Names}}" | grep doganai) 2>/dev/null || echo "No DoganAI containers found"

echo ""

# Check volumes
echo "?? Volume Status"
echo "================"

echo "?? DoganAI volumes:"
docker volume ls | grep doganai || echo "No DoganAI volumes found"

echo ""

# Check networks
echo "?? Network Status"
echo "=================="

echo "?? DoganAI networks:"
docker network ls | grep doganai || echo "No DoganAI networks found"

echo ""

# API endpoint checks
echo "?? API Endpoint Checks"
echo "======================="

API_ENDPOINTS=(
    "http://localhost:8000/health:Compliance Engine"
    "http://localhost:8001/health:Benchmarks"
    "http://localhost:8002/health:AI/ML"
    "http://localhost:8003/health:Integrations"
    "http://localhost:8004/health:Authentication"
    "http://localhost:8005/health:AI Agent"
    "http://localhost:8006/health:Autonomous Testing"
    "http://localhost:8501/health:UI Service"
    "http://localhost:9090/-/healthy:Prometheus"
    "http://localhost:3000/api/health:Grafana"
    "http://localhost:9200/_cluster/health:Elasticsearch"
)

working_endpoints=0
total_endpoints=${#API_ENDPOINTS[@]}

for endpoint_desc in "${API_ENDPOINTS[@]}"; do
    endpoint=$(echo $endpoint_desc | cut -d: -f1)
    description=$(echo $endpoint_desc | cut -d: -f2)
    
    echo -ne "${BLUE}?? $description:${NC} "
    
    if curl -s -f "$endpoint" >/dev/null 2>&1; then
        echo -e "${GREEN}? Responding${NC}"
        working_endpoints=$((working_endpoints + 1))
    else
        echo -e "${RED}? Not responding${NC}"
    fi
done

echo ""
echo "?? API Endpoint Summary:"
echo -e "Working endpoints: ${GREEN}$working_endpoints${NC}/$total_endpoints"
endpoint_percentage=$((working_endpoints * 100 / total_endpoints))
echo -e "Endpoint health: ${BLUE}$endpoint_percentage%${NC}"

echo ""

# Overall system health
echo "?? Overall System Health"
echo "========================="

overall_health=$(((health_percentage + endpoint_percentage) / 2))
echo -e "Overall health score: ${BLUE}$overall_health%${NC}"

if [ $overall_health -ge 90 ]; then
    echo -e "${GREEN}?? DoganAI is running excellently!${NC}"
    echo -e "${GREEN}? Ready for production workloads${NC}"
elif [ $overall_health -ge 75 ]; then
    echo -e "${YELLOW}? DoganAI is running well with minor issues${NC}"
    echo -e "${YELLOW}?? Some fine-tuning recommended${NC}"
elif [ $overall_health -ge 50 ]; then
    echo -e "${YELLOW}??  DoganAI has moderate issues${NC}"
    echo -e "${YELLOW}???  Troubleshooting required${NC}"
else
    echo -e "${RED}? DoganAI has significant issues${NC}"
    echo -e "${RED}?? Immediate attention required${NC}"
fi

echo ""

# Quick access information
echo "?? Quick Access URLs"
echo "===================="
echo -e "${BLUE}Main UI:${NC} http://localhost:8501"
echo -e "${BLUE}API Documentation:${NC} http://localhost:8000/docs"
echo -e "${BLUE}Grafana Dashboard:${NC} http://localhost:3000"
echo -e "${BLUE}Prometheus Metrics:${NC} http://localhost:9090"
echo -e "${BLUE}Kibana Logs:${NC} http://localhost:5601"
echo -e "${BLUE}MinIO Console:${NC} http://localhost:9001"

echo ""

# Troubleshooting suggestions
if [ $overall_health -lt 75 ]; then
    echo "???  Troubleshooting Suggestions"
    echo "==============================="
    echo "1. Check logs: docker-compose -f docker-compose.independent.yml logs"
    echo "2. Restart services: docker-compose -f docker-compose.independent.yml restart"
    echo "3. Check resource usage: docker stats"
    echo "4. Verify .env configuration"
    echo "5. Check disk space: df -h"
    echo "6. Check memory usage: free -h"
    echo ""
fi

# Save results to file
timestamp=$(date +"%Y%m%d_%H%M%S")
report_file="docker_health_report_$timestamp.txt"

{
    echo "DoganAI Docker Health Report"
    echo "Generated: $(date)"
    echo "Overall Health: $overall_health%"
    echo "Container Health: $health_percentage%"
    echo "Endpoint Health: $endpoint_percentage%"
    echo "Healthy Services: $healthy_services/$total_services"
    echo "Working Endpoints: $working_endpoints/$total_endpoints"
} > "$report_file"

echo "?? Health report saved to: $report_file"

exit 0