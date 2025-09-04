#!/bin/bash
# DoganAI Compliance Kit - Docker Entrypoint Script
# Handles container initialization, health checks, and graceful shutdown

set -e

# =============================================================================
# CONFIGURATION AND ENVIRONMENT
# =============================================================================

# Default values
DEFAULT_API_HOST="0.0.0.0"
DEFAULT_API_PORT="8000"
DEFAULT_WORKERS="4"
DEFAULT_LOG_LEVEL="info"

# Set defaults if not provided
export API_HOST=${API_HOST:-$DEFAULT_API_HOST}
export API_PORT=${API_PORT:-$DEFAULT_API_PORT}
export WORKERS=${WORKERS:-$DEFAULT_WORKERS}
export LOG_LEVEL=${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] $1" >&2
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_debug() {
    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] [DEBUG] $1"
    fi
}

# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

# PID of the main application process
APP_PID=0

# Graceful shutdown handler
shutdown_handler() {
    log_info "Received shutdown signal, initiating graceful shutdown..."
    
    if [[ $APP_PID -ne 0 ]]; then
        log_info "Sending SIGTERM to application process (PID: $APP_PID)"
        kill -TERM $APP_PID
        
        # Wait for graceful shutdown (max 30 seconds)
        local count=0
        while kill -0 $APP_PID 2>/dev/null && [[ $count -lt 30 ]]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 $APP_PID 2>/dev/null; then
            log_warn "Application did not shutdown gracefully, forcing termination"
            kill -KILL $APP_PID
        else
            log_info "Application shutdown gracefully"
        fi
    fi
    
    log_info "Container shutdown complete"
    exit 0
}

# Set up signal handlers
trap shutdown_handler SIGTERM SIGINT SIGQUIT

# =============================================================================
# HEALTH CHECK FUNCTIONS
# =============================================================================

check_database_connection() {
    log_info "Checking database connection..."
    
    if [[ -z "${DATABASE_URL}" ]]; then
        log_warn "DATABASE_URL not set, skipping database check"
        return 0
    fi
    
    # Simple connection test using Python
    python3 -c "
import os
import sys
try:
    import asyncpg
    import asyncio
    async def test_db():
        try:
            conn = await asyncpg.connect(os.environ.get('DATABASE_URL'))
            await conn.execute('SELECT 1')
            await conn.close()
            return True
        except Exception as e:
            print(f'Database connection failed: {e}')
            return False
    
    result = asyncio.run(test_db())
    sys.exit(0 if result else 1)
except ImportError:
    print('asyncpg not available, skipping database check')
    sys.exit(0)
" 2>/dev/null
    
    if [[ $? -eq 0 ]]; then
        log_info "Database connection successful"
        return 0
    else
        log_error "Database connection failed"
        return 1
    fi
}

check_redis_connection() {
    log_info "Checking Redis connection..."
    
    if [[ -z "${REDIS_URL}" ]]; then
        log_warn "REDIS_URL not set, skipping Redis check"
        return 0
    fi
    
    # Simple Redis connection test
    python3 -c "
import os
import sys
try:
    import redis
    r = redis.from_url(os.environ.get('REDIS_URL'))
    r.ping()
    print('Redis connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Redis connection failed: {e}')
    sys.exit(1)
" 2>/dev/null
    
    if [[ $? -eq 0 ]]; then
        log_info "Redis connection successful"
        return 0
    else
        log_error "Redis connection failed"
        return 1
    fi
}

wait_for_dependencies() {
    log_info "Waiting for dependencies to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Dependency check attempt $attempt/$max_attempts"
        
        local db_ok=true
        local redis_ok=true
        
        # Check database if URL is provided
        if [[ -n "${DATABASE_URL}" ]]; then
            check_database_connection || db_ok=false
        fi
        
        # Check Redis if URL is provided
        if [[ -n "${REDIS_URL}" ]]; then
            check_redis_connection || redis_ok=false
        fi
        
        if [[ "$db_ok" == "true" && "$redis_ok" == "true" ]]; then
            log_info "All dependencies are ready"
            return 0
        fi
        
        log_info "Dependencies not ready, waiting 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_error "Dependencies failed to become ready after $max_attempts attempts"
    return 1
}

# =============================================================================
# INITIALIZATION FUNCTIONS
# =============================================================================

initialize_directories() {
    log_info "Initializing application directories..."
    
    # Create necessary directories
    mkdir -p /app/logs /app/data /app/temp
    
    # Set proper permissions
    chmod 755 /app/logs /app/data /app/temp
    
    log_info "Directories initialized successfully"
}

initialize_database() {
    log_info "Initializing database schema..."
    
    if [[ -z "${DATABASE_URL}" ]]; then
        log_warn "DATABASE_URL not set, skipping database initialization"
        return 0
    fi
    
    # Run database migrations if available
    if [[ -f "/app/scripts/init_db.py" ]]; then
        log_info "Running database initialization script..."
        python3 /app/scripts/init_db.py || {
            log_error "Database initialization failed"
            return 1
        }
    fi
    
    log_info "Database initialization completed"
}

validate_configuration() {
    log_info "Validating application configuration..."
    
    # Check required environment variables
    local required_vars=("PYTHONPATH")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Required environment variable $var is not set"
            return 1
        fi
    done
    
    # Validate port numbers
    if ! [[ "$API_PORT" =~ ^[0-9]+$ ]] || [[ "$API_PORT" -lt 1 ]] || [[ "$API_PORT" -gt 65535 ]]; then
        log_error "Invalid API_PORT: $API_PORT"
        return 1
    fi
    
    # Validate worker count
    if ! [[ "$WORKERS" =~ ^[0-9]+$ ]] || [[ "$WORKERS" -lt 1 ]] || [[ "$WORKERS" -gt 32 ]]; then
        log_error "Invalid WORKERS count: $WORKERS"
        return 1
    fi
    
    log_info "Configuration validation successful"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    log_info "Starting DoganAI Compliance Kit container..."
    log_info "Container version: ${VERSION:-unknown}"
    log_info "Environment: ${ENVIRONMENT:-development}"
    log_info "Python path: ${PYTHONPATH}"
    log_info "API Host: ${API_HOST}:${API_PORT}"
    log_info "Workers: ${WORKERS}"
    log_info "Log level: ${LOG_LEVEL}"
    
    # Initialize container
    initialize_directories || {
        log_error "Failed to initialize directories"
        exit 1
    }
    
    # Validate configuration
    validate_configuration || {
        log_error "Configuration validation failed"
        exit 1
    }
    
    # Wait for dependencies
    if [[ "${WAIT_FOR_DEPENDENCIES:-true}" == "true" ]]; then
        wait_for_dependencies || {
            log_error "Dependencies check failed"
            exit 1
        }
    fi
    
    # Initialize database
    if [[ "${INIT_DATABASE:-true}" == "true" ]]; then
        initialize_database || {
            log_error "Database initialization failed"
            exit 1
        }
    fi
    
    log_info "Container initialization completed successfully"
    log_info "Starting application with command: $*"
    
    # Start the application
    exec "$@" &
    APP_PID=$!
    
    log_info "Application started with PID: $APP_PID"
    
    # Wait for the application to finish
    wait $APP_PID
    local exit_code=$?
    
    log_info "Application exited with code: $exit_code"
    exit $exit_code
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# Handle special commands
case "$1" in
    "health-check")
        log_info "Running health check..."
        curl -f "http://localhost:${API_PORT}/health" || exit 1
        log_info "Health check passed"
        exit 0
        ;;
    "version")
        echo "DoganAI Compliance Kit ${VERSION:-unknown}"
        exit 0
        ;;
    "help")
        echo "DoganAI Compliance Kit - Container Entrypoint"
        echo "Usage: docker run doganai/compliance-kit [command]"
        echo ""
        echo "Commands:"
        echo "  health-check    Run health check"
        echo "  version         Show version information"
        echo "  help            Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  API_HOST                Host to bind to (default: 0.0.0.0)"
        echo "  API_PORT                Port to bind to (default: 8000)"
        echo "  WORKERS                 Number of worker processes (default: 4)"
        echo "  LOG_LEVEL               Log level (default: info)"
        echo "  DATABASE_URL            PostgreSQL connection string"
        echo "  REDIS_URL               Redis connection string"
        echo "  WAIT_FOR_DEPENDENCIES   Wait for dependencies (default: true)"
        echo "  INIT_DATABASE           Initialize database (default: true)"
        echo "  DEBUG_MODE              Enable debug logging (default: false)"
        exit 0
        ;;
esac

# Run main function with all arguments
main "$@"