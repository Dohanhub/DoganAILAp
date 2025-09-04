#!/bin/bash

# DoganAI Compliance Kit - Docker Startup Script
# This script provides easy commands to manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f ".env.template" ]; then
            cp .env.template .env
            print_success ".env file created from template. Please review and update the values."
        else
            print_error ".env.template not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Function to build the Docker image
build() {
    print_status "Building DoganAI Compliance Kit Docker image..."
    docker build -t doganai-compliance-kit:latest .
    print_success "Docker image built successfully!"
}

# Function to start services
start() {
    print_status "Starting DoganAI Compliance Kit services..."
    docker-compose -f docker-compose.production.yml up -d
    print_success "Services started successfully!"
    print_status "Application will be available at: http://localhost:8000"
    print_status "Database (PostgreSQL) available at: localhost:5432"
    print_status "Cache (Redis) available at: localhost:6379"
}

# Function to start with monitoring
start_monitoring() {
    print_status "Starting services with monitoring stack..."
    docker-compose -f docker-compose.production.yml --profile monitoring up -d
    print_success "Services with monitoring started successfully!"
    print_status "Application: http://localhost:8000"
    print_status "Grafana Dashboard: http://localhost:3000 (admin/admin)"
    print_status "Prometheus: http://localhost:9090"
}

# Function to stop services
stop() {
    print_status "Stopping DoganAI Compliance Kit services..."
    docker-compose -f docker-compose.production.yml down
    print_success "Services stopped successfully!"
}

# Function to restart services
restart() {
    print_status "Restarting DoganAI Compliance Kit services..."
    stop
    start
}

# Function to view logs
logs() {
    docker-compose -f docker-compose.production.yml logs -f
}

# Function to show status
status() {
    print_status "Service Status:"
    docker-compose -f docker-compose.production.yml ps
    
    print_status "\nHealth Status:"
    docker-compose -f docker-compose.production.yml exec app curl -s http://localhost:8000/health || print_warning "Application health check failed"
}

# Function to clean up
clean() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up Docker environment..."
        docker-compose -f docker-compose.production.yml down -v --rmi all
        docker system prune -f
        print_success "Docker environment cleaned up!"
    else
        print_status "Clean up cancelled."
    fi
}

# Function to run database migrations
migrate() {
    print_status "Running database migrations..."
    docker-compose -f docker-compose.production.yml exec app alembic upgrade head
    print_success "Database migrations completed!"
}

# Function to open shell in container
shell() {
    print_status "Opening shell in application container..."
    docker-compose -f docker-compose.production.yml exec app /bin/bash
}

# Function to backup database
backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_status "Creating database backup: $BACKUP_FILE"
    docker-compose -f docker-compose.production.yml exec -T db pg_dump -U postgres compliance_kit > "$BACKUP_FILE"
    print_success "Database backup created: $BACKUP_FILE"
}

# Function to show help
show_help() {
    echo "DoganAI Compliance Kit - Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build           Build the Docker image"
    echo "  start           Start all services"
    echo "  start-monitoring Start services with monitoring stack"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  logs            View service logs"
    echo "  status          Show service status"
    echo "  migrate         Run database migrations"
    echo "  shell           Open shell in app container"
    echo "  backup          Backup the database"
    echo "  clean           Clean up all Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 start"
    echo "  $0 start-monitoring"
    echo "  $0 logs"
}

# Main script logic
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build
            ;;
        "start")
            check_docker
            check_env
            start
            ;;
        "start-monitoring")
            check_docker
            check_env
            start_monitoring
            ;;
        "stop")
            check_docker
            stop
            ;;
        "restart")
            check_docker
            restart
            ;;
        "logs")
            check_docker
            logs
            ;;
        "status")
            check_docker
            status
            ;;
        "migrate")
            check_docker
            migrate
            ;;
        "shell")
            check_docker
            shell
            ;;
        "backup")
            check_docker
            backup
            ;;
        "clean")
            check_docker
            clean
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run the main function with all arguments
main "$@"
