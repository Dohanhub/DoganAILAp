#!/bin/bash

# DoganAI Compliance Kit - Production Deployment Script
# This script provides comprehensive production deployment with health checks, monitoring, and rollback

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_NAME="doganai-compliance-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_DIR="$PROJECT_ROOT/logs"
ENV_FILE="$PROJECT_ROOT/env.production"

# =============================================================================
# FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed. Please install it and try again."
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Please copy env.production to .env and configure it for your environment."
        exit 1
    fi
    
    # Check if required directories exist
    local required_dirs=("microservices" "monitoring" "nginx")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
            log_error "Required directory not found: $dir"
            exit 1
        fi
    done
    
    log_success "Prerequisites check passed"
}

create_backup() {
    log_info "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker ps --format "{{.Names}}" | grep -q "doganai-postgres"; then
        log_info "Backing up PostgreSQL database..."
        docker exec doganai-postgres pg_dump -U doganai_user -d doganai_compliance > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        log_success "Database backup created"
    fi
    
    # Backup configuration files
    log_info "Backing up configuration files..."
    tar -czf "$BACKUP_DIR/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
        -C "$PROJECT_ROOT" \
        microservices/docker-compose.production.yml \
        env.production \
        monitoring/ \
        nginx/
    
    log_success "Configuration backup created"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    # Source environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required environment variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "GRAFANA_PASSWORD"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Validate secret key length
    if [[ ${#SECRET_KEY} -lt 32 ]]; then
        log_error "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

deploy_services() {
    log_info "Deploying DoganAI Compliance Kit services..."
    
    cd "$PROJECT_ROOT/microservices"
    
    # Stop existing services if running
    if docker-compose -f docker-compose.production.yml ps --services | grep -q .; then
        log_info "Stopping existing services..."
        docker-compose -f docker-compose.production.yml down
    fi
    
    # Build and start services
    log_info "Building and starting services..."
    docker-compose -f docker-compose.production.yml up --build -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    log_success "Services deployed successfully"
}

health_check() {
    log_info "Performing health checks..."
    
    local services=(
        "http://localhost:8000/health"
        "http://localhost:8001/health"
        "http://localhost:8002/health"
        "http://localhost:8003/health"
        "http://localhost:8501/health"
        "http://localhost:9090/-/healthy"
        "http://localhost:3000/api/health"
    )
    
    local failed_services=()
    
    for service in "${services[@]}"; do
        log_info "Checking $service..."
        if curl -f -s "$service" >/dev/null; then
            log_success "$service is healthy"
        else
            log_error "$service is unhealthy"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Health check failed for services: ${failed_services[*]}"
        return 1
    fi
    
    log_success "All services are healthy"
    return 0
}

monitor_deployment() {
    log_info "Monitoring deployment..."
    
    # Check service status
    cd "$PROJECT_ROOT/microservices"
    docker-compose -f docker-compose.production.yml ps
    
    # Check resource usage
    log_info "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    # Check logs for errors
    log_info "Checking for errors in logs..."
    local services=("compliance-engine" "ai-ml" "benchmarks" "integrations" "ui")
    
    for service in "${services[@]}"; do
        if docker logs "doganai-$service" 2>&1 | grep -i "error\|exception\|traceback" >/dev/null; then
            log_warning "Errors found in $service logs"
        fi
    done
}

setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Create monitoring directories
    mkdir -p "$PROJECT_ROOT/monitoring/grafana/provisioning/datasources"
    mkdir -p "$PROJECT_ROOT/monitoring/grafana/provisioning/dashboards"
    mkdir -p "$PROJECT_ROOT/monitoring/grafana/dashboards"
    
    # Create Prometheus configuration
    cat > "$PROJECT_ROOT/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'compliance-engine'
    static_configs:
      - targets: ['compliance-engine:8000']
    metrics_path: '/metrics'

  - job_name: 'ai-ml'
    static_configs:
      - targets: ['ai-ml:8002']
    metrics_path: '/metrics'

  - job_name: 'benchmarks'
    static_configs:
      - targets: ['benchmarks:8001']
    metrics_path: '/metrics'

  - job_name: 'integrations'
    static_configs:
      - targets: ['integrations:8003']
    metrics_path: '/metrics'
EOF
    
    # Create Grafana datasource configuration
    cat > "$PROJECT_ROOT/monitoring/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    # Create Grafana dashboard configuration
    cat > "$PROJECT_ROOT/monitoring/grafana/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF
    
    log_success "Monitoring configuration created"
}

setup_nginx() {
    log_info "Setting up Nginx load balancer..."
    
    mkdir -p "$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$PROJECT_ROOT/nginx/logs"
    
    # Create Nginx configuration
    cat > "$PROJECT_ROOT/nginx/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream compliance_api {
        server compliance-engine:8000;
    }
    
    upstream ui {
        server ui:8501;
    }
    
    upstream benchmarks {
        server benchmarks:8001;
    }
    
    upstream ai_ml {
        server ai-ml:8002;
    }
    
    upstream integrations {
        server integrations:8003;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ui:10m rate=30r/s;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    server {
        listen 80;
        server_name _;
        
        # Redirect to HTTPS
        return 301 https://$host$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://compliance_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Benchmarks
        location /benchmarks/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://benchmarks/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # AI-ML
        location /ai-ml/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://ai_ml/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Integrations
        location /integrations/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://integrations/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # UI
        location / {
            limit_req zone=ui burst=50 nodelay;
            proxy_pass http://ui/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }
    }
}
EOF
    
    # Create self-signed SSL certificate for testing
    if [[ ! -f "$PROJECT_ROOT/nginx/ssl/cert.pem" ]]; then
        log_info "Creating self-signed SSL certificate..."
        openssl req -x509 -newkey rsa:4096 -keyout "$PROJECT_ROOT/nginx/ssl/key.pem" \
            -out "$PROJECT_ROOT/nginx/ssl/cert.pem" -days 365 -nodes \
            -subj "/C=SA/ST=Riyadh/L=Riyadh/O=DoganAI/OU=Compliance/CN=localhost"
        log_success "SSL certificate created"
    fi
    
    log_success "Nginx configuration created"
}

create_deployment_summary() {
    log_info "Creating deployment summary..."
    
    cat > "$PROJECT_ROOT/DEPLOYMENT_SUMMARY.md" << EOF
# DoganAI Compliance Kit - Production Deployment Summary

## Deployment Information
- **Deployment Date**: $(date)
- **Deployment ID**: $DEPLOYMENT_NAME
- **Environment**: Production
- **Status**: Deployed Successfully

## Service Endpoints

### Core Services
- **Compliance Engine API**: https://localhost/api/
- **Benchmarks Service**: https://localhost/benchmarks/
- **AI-ML Service**: https://localhost/ai-ml/
- **Integrations Service**: https://localhost/integrations/
- **User Interface**: https://localhost/

### Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger Tracing**: http://localhost:16686

### Health Checks
- **Load Balancer**: https://localhost/health
- **API Health**: https://localhost/api/health

## Configuration
- **Environment File**: $ENV_FILE
- **Docker Compose**: microservices/docker-compose.production.yml
- **Nginx Config**: nginx/nginx.conf
- **Monitoring Config**: monitoring/

## Next Steps
1. Update DNS records to point to your domain
2. Replace self-signed SSL certificate with proper certificate
3. Configure external monitoring and alerting
4. Set up backup and disaster recovery procedures
5. Configure log aggregation and analysis

## Support
For support and issues, please refer to the project documentation or contact the development team.
EOF
    
    log_success "Deployment summary created: DEPLOYMENT_SUMMARY.md"
}

rollback() {
    log_error "Deployment failed. Rolling back..."
    
    cd "$PROJECT_ROOT/microservices"
    
    # Stop all services
    docker-compose -f docker-compose.production.yml down
    
    # Restore from backup if available
    if [[ -d "$BACKUP_DIR" ]]; then
        local latest_backup=$(ls -t "$BACKUP_DIR"/config_backup_*.tar.gz 2>/dev/null | head -1)
        if [[ -n "$latest_backup" ]]; then
            log_info "Restoring from backup: $latest_backup"
            tar -xzf "$latest_backup" -C "$PROJECT_ROOT"
        fi
    fi
    
    log_error "Rollback completed. Please check the logs and fix the issues before retrying."
    exit 1
}

# =============================================================================
# MAIN DEPLOYMENT SCRIPT
# =============================================================================

main() {
    log_info "Starting DoganAI Compliance Kit production deployment..."
    log_info "Deployment ID: $DEPLOYMENT_NAME"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Log deployment start
    echo "$(date): Deployment started - $DEPLOYMENT_NAME" >> "$LOG_DIR/deployment.log"
    
    # Execute deployment steps
    if ! check_prerequisites; then
        rollback
    fi
    
    if ! validate_environment; then
        rollback
    fi
    
    create_backup
    
    setup_monitoring
    
    setup_nginx
    
    if ! deploy_services; then
        rollback
    fi
    
    if ! health_check; then
        rollback
    fi
    
    monitor_deployment
    
    create_deployment_summary
    
    # Log successful deployment
    echo "$(date): Deployment completed successfully - $DEPLOYMENT_NAME" >> "$LOG_DIR/deployment.log"
    
    log_success "Production deployment completed successfully!"
    log_info "Deployment summary: DEPLOYMENT_SUMMARY.md"
    log_info "Access the application at: https://localhost"
    log_info "Monitor the deployment with: ./monitor-deployment.sh"
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# Check if script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    main "$@"
else
    # Script is being sourced
    log_info "Deployment script loaded. Use 'main' function to execute deployment."
fi
