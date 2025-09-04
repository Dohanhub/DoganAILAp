#!/bin/bash
# DoganAI Compliance Kit - Quick Setup & Test Script
# Run this to see everything in action!

echo "?? DoganAI Compliance Kit - Performance Setup & Test"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}? $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}?? $1${NC}"
}

print_error() {
    echo -e "${RED}? $1${NC}"
}

print_info() {
    echo -e "${BLUE}?? $1${NC}"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

print_status "Python 3 found"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    print_error "pip is required but not installed"
    exit 1
fi

print_status "pip found"

# Install required packages (basic ones only)
print_info "Installing required packages..."
pip install asyncio aiohttp requests matplotlib pandas psutil 2>/dev/null || pip3 install asyncio aiohttp requests matplotlib pandas psutil 2>/dev/null

# Check if Redis is available (optional)
if command -v redis-server &> /dev/null; then
    print_status "Redis server found"
    
    # Check if Redis is running
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running"
    else
        print_warning "Redis is not running. Starting Redis in background..."
        redis-server --daemonize yes --port 6379 2>/dev/null || print_warning "Could not start Redis"
    fi
else
    print_warning "Redis not found - some features will use local cache only"
fi

# Run the quick demo (no external dependencies)
print_info "Running performance demo (no external dependencies required)..."
echo ""

python quick_demo.py

echo ""
print_info "Demo completed!"

# Try to run the enhanced API if dependencies are available
echo ""
print_info "Checking if enhanced API can be started..."

# Check for FastAPI dependencies
python -c "import fastapi, uvicorn, aioredis" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "FastAPI dependencies found"
    
    echo ""
    print_info "Starting enhanced API server..."
    print_info "You can stop it with Ctrl+C"
    echo ""
    
    # Start the enhanced API
    python improvements/enhanced_api.py
else
    print_warning "FastAPI dependencies not found. Install with:"
    echo "pip install fastapi uvicorn aioredis asyncpg prometheus-client structlog"
    echo ""
    print_info "For now, you can still see the performance improvements in the demo above!"
fi

echo ""
print_info "Setup complete! Your DoganAI Compliance Kit performance improvements are ready."
echo ""
print_info "Next steps:"
echo "  1. Install missing dependencies if needed"
echo "  2. Configure Redis for optimal caching"
echo "  3. Set up PostgreSQL for production use"
echo "  4. Deploy to Kubernetes with: python improvements/deploy.py"
echo ""
print_status "All done! ??"