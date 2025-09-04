#!/bin/bash

# DoganAI Compliance Kit - Internal Folder Deployment Script
# This script creates a self-contained deployment in any folder

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_NAME="doganai-compliance-kit"
DEFAULT_PORT=8080
DEFAULT_DB_PORT=5433
DEFAULT_REDIS_PORT=6380

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              DoganAI Compliance Kit                          ║"
    echo "║              Internal Deployment Setup                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "All requirements satisfied!"
}

create_deployment_folder() {
    local deployment_dir="${1:-./doganai-deployment}"
    
    print_status "Creating deployment folder: $deployment_dir"
    
    # Create deployment directory
    mkdir -p "$deployment_dir"
    mkdir -p "$deployment_dir/data/postgres"
    mkdir -p "$deployment_dir/data/redis"
    mkdir -p "$deployment_dir/logs"
    mkdir -p "$deployment_dir/config"
    mkdir -p "$deployment_dir/scripts"
    
    # Set permissions
    chmod 755 "$deployment_dir"
    chmod 755 "$deployment_dir/data"
    chmod 755 "$deployment_dir/logs"
    chmod 755 "$deployment_dir/config"
    
    print_success "Deployment folder created: $deployment_dir"
    echo "$deployment_dir"
}

create_env_file() {
    local deployment_dir="$1"
    local env_file="$deployment_dir/.env"
    
    print_status "Creating environment configuration..."
    
    cat > "$env_file" << 'EOF'
# DoganAI Compliance Kit - Internal Deployment Configuration

# Application Settings
APP_NAME=DoganAI Compliance Kit
APP_ENVIRONMENT=production
SECRET_KEY=your-secret-key-change-this-in-production-$(openssl rand -hex 32)
API_V1_STR=/api/v1

# Database Configuration
POSTGRES_SERVER=db
POSTGRES_USER=doganai_user
POSTGRES_PASSWORD=doganai_secure_password_2024
POSTGRES_DB=doganai_compliance
DATABASE_URL=postgresql://doganai_user:doganai_secure_password_2024@db:5432/doganai_compliance

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# CORS Settings
BACKEND_CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF

    # Secure the env file
    chmod 600 "$env_file"
    
    print_success "Environment file created: $env_file"
}

create_docker_compose() {
    local deployment_dir="$1"
    local compose_file="$deployment_dir/docker-compose.yml"
    
    print_status "Creating Docker Compose configuration..."
    
    cat > "$compose_file" << EOF
version: '3.8'

services:
  app:
    image: doganai/compliance-kit:latest
    container_name: ${DEPLOYMENT_NAME}-app
    restart: unless-stopped
    ports:
      - "${DEFAULT_PORT}:8000"
    environment:
      - DATABASE_URL=postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@db:5432/\${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - APP_ENVIRONMENT=production
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro
    networks:
      - doganai-network

  db:
    image: postgres:15-alpine
    container_name: ${DEPLOYMENT_NAME}-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
      - POSTGRES_DB=\${POSTGRES_DB}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    ports:
      - "${DEFAULT_DB_PORT}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - doganai-network

  redis:
    image: redis:7-alpine
    container_name: ${DEPLOYMENT_NAME}-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "${DEFAULT_REDIS_PORT}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - doganai-network

  # Optional: Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: ${DEPLOYMENT_NAME}-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./data/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - doganai-network
    profiles:
      - monitoring

  # Optional: Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: ${DEPLOYMENT_NAME}-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./config/grafana:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus
    networks:
      - doganai-network
    profiles:
      - monitoring

networks:
  doganai-network:
    driver: bridge
    name: ${DEPLOYMENT_NAME}-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
EOF

    print_success "Docker Compose file created: $compose_file"
}

create_management_scripts() {
    local deployment_dir="$1"
    
    print_status "Creating management scripts..."
    
    # Create start script
    cat > "$deployment_dir/start.sh" << 'EOF'
#!/bin/bash
echo "Starting DoganAI Compliance Kit..."
docker-compose up -d
echo "Services started! Application available at: http://localhost:8080"
echo "Grafana dashboard available at: http://localhost:3000 (admin/admin)"
EOF

    # Create stop script
    cat > "$deployment_dir/stop.sh" << 'EOF'
#!/bin/bash
echo "Stopping DoganAI Compliance Kit..."
docker-compose down
echo "Services stopped!"
EOF

    # Create status script
    cat > "$deployment_dir/status.sh" << 'EOF'
#!/bin/bash
echo "DoganAI Compliance Kit Status:"
docker-compose ps
echo ""
echo "Health Check:"
curl -s http://localhost:8080/health | jq '.' || echo "Application not responding"
EOF

    # Create logs script
    cat > "$deployment_dir/logs.sh" << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Showing all logs..."
    docker-compose logs -f
else
    echo "Showing logs for service: $1"
    docker-compose logs -f "$1"
fi
EOF

    # Create backup script
    cat > "$deployment_dir/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in: $BACKUP_DIR"

# Backup database
docker-compose exec -T db pg_dump -U doganai_user doganai_compliance > "$BACKUP_DIR/database.sql"

# Backup Redis data
docker-compose exec -T redis redis-cli --rdb - > "$BACKUP_DIR/redis.rdb"

# Backup configuration
cp -r config "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
EOF

    # Create update script
    cat > "$deployment_dir/update.sh" << 'EOF'
#!/bin/bash
echo "Updating DoganAI Compliance Kit..."
docker-compose pull
docker-compose up -d
echo "Update completed!"
EOF

    # Make scripts executable
    chmod +x "$deployment_dir"/*.sh
    
    print_success "Management scripts created!"
}

create_database_init() {
    local deployment_dir="$1"
    local init_file="$deployment_dir/scripts/init-db.sql"
    
    mkdir -p "$deployment_dir/scripts"
    
    cat > "$init_file" << 'EOF'
-- DoganAI Compliance Kit Database Initialization

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial admin user (change password in production)
-- This will be handled by the application
EOF

    print_success "Database initialization script created: $init_file"
}

create_monitoring_config() {
    local deployment_dir="$1"
    
    mkdir -p "$deployment_dir/config"
    
    # Prometheus configuration
    cat > "$deployment_dir/config/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'doganai-compliance-kit'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF

    print_success "Monitoring configuration created!"
}

create_readme() {
    local deployment_dir="$1"
    
    cat > "$deployment_dir/README.md" << EOF
# DoganAI Compliance Kit - Internal Deployment

This is a self-contained deployment of the DoganAI Compliance Kit for internal use.

## Quick Start

1. **Start the application:**
   \`\`\`bash
   ./start.sh
   \`\`\`

2. **Access the application:**
   - Main Application: http://localhost:${DEFAULT_PORT}
   - API Documentation: http://localhost:${DEFAULT_PORT}/docs
   - Health Check: http://localhost:${DEFAULT_PORT}/health

3. **Access databases:**
   - PostgreSQL: localhost:${DEFAULT_DB_PORT}
   - Redis: localhost:${DEFAULT_REDIS_PORT}

## Management Commands

- **Start services:** \`./start.sh\`
- **Stop services:** \`./stop.sh\`
- **Check status:** \`./status.sh\`
- **View logs:** \`./logs.sh [service_name]\`
- **Create backup:** \`./backup.sh\`
- **Update application:** \`./update.sh\`

## Monitoring (Optional)

To enable monitoring:
\`\`\`bash
docker-compose --profile monitoring up -d
\`\`\`

- **Grafana Dashboard:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090

## Configuration

- **Environment variables:** Edit \`.env\`
- **Docker services:** Edit \`docker-compose.yml\`
- **Database init:** Edit \`scripts/init-db.sql\`

## Data Persistence

All data is stored in the \`data/\` directory:
- \`data/postgres/\` - Database files
- \`data/redis/\` - Redis data
- \`logs/\` - Application logs

## Security Notes

1. Change the default passwords in \`.env\`
2. Update the SECRET_KEY in \`.env\`
3. Review firewall settings for internal network access
4. Regular backups are recommended

## Troubleshooting

1. **Check service status:** \`./status.sh\`
2. **View logs:** \`./logs.sh\`
3. **Restart services:** \`./stop.sh && ./start.sh\`
4. **Reset data:** Remove \`data/\` directory and restart

## Support

For issues and support, check the logs and configuration files.
EOF

    print_success "README created: $deployment_dir/README.md"
}

main() {
    print_header
    
    # Parse command line arguments
    DEPLOYMENT_DIR="\${1:-./doganai-internal-deployment}"
    
    print_status "Setting up DoganAI Compliance Kit internal deployment..."
    print_status "Deployment directory: \$DEPLOYMENT_DIR"
    
    # Run setup steps
    check_requirements
    DEPLOYMENT_DIR=\$(create_deployment_folder "\$DEPLOYMENT_DIR")
    create_env_file "\$DEPLOYMENT_DIR"
    create_docker_compose "\$DEPLOYMENT_DIR"
    create_management_scripts "\$DEPLOYMENT_DIR"
    create_database_init "\$DEPLOYMENT_DIR"
    create_monitoring_config "\$DEPLOYMENT_DIR"
    create_readme "\$DEPLOYMENT_DIR"
    
    print_success "Internal deployment setup completed!"
    echo ""
    print_status "Next steps:"
    echo "1. cd \$DEPLOYMENT_DIR"
    echo "2. Review and update .env file with your settings"
    echo "3. ./start.sh"
    echo ""
    print_status "The application will be available at:"
    echo "- Main App: http://localhost:${DEFAULT_PORT}"
    echo "- API Docs: http://localhost:${DEFAULT_PORT}/docs"
    echo "- Database: localhost:${DEFAULT_DB_PORT}"
    echo "- Redis: localhost:${DEFAULT_REDIS_PORT}"
}

# Run main function
main "\$@"
