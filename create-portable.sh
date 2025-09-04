#!/bin/bash

# DoganAI Compliance Kit - Portable Folder Deployment
# This script creates a completely portable deployment with source code

set -e

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

create_portable_deployment() {
    local target_dir="${1:-./doganai-portable}"
    
    print_status "Creating portable deployment in: $target_dir"
    
    # Create directory structure
    mkdir -p "$target_dir"
    mkdir -p "$target_dir/app"
    mkdir -p "$target_dir/data"
    mkdir -p "$target_dir/config"
    mkdir -p "$target_dir/scripts"
    
    # Copy application source
    print_status "Copying application source..."
    
    # Copy essential application files
    cp -r src/ "$target_dir/app/" 2>/dev/null || true
    cp requirements-api.txt "$target_dir/app/" 2>/dev/null || true
    cp Dockerfile "$target_dir/app/" 2>/dev/null || true
    cp .env.template "$target_dir/app/.env.example" 2>/dev/null || true
    
    # Create simplified Dockerfile for portable deployment
    cat > "$target_dir/app/Dockerfile.portable" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application
COPY src/ ./src/
COPY .env.example .env

# Create non-root user
RUN groupadd -r app && useradd -r -g app app && \
    chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    # Create portable docker-compose
    cat > "$target_dir/docker-compose.portable.yml" << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: ./app
      dockerfile: Dockerfile.portable
    container_name: doganai-portable-app
    restart: unless-stopped
    ports:
      - "8080:8000"
    environment:
      - DATABASE_URL=postgresql://doganai:doganai@db:5432/doganai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config:ro
    networks:
      - doganai-net

  db:
    image: postgres:15-alpine
    container_name: doganai-portable-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=doganai
      - POSTGRES_PASSWORD=doganai
      - POSTGRES_DB=doganai
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - doganai-net

  redis:
    image: redis:7-alpine
    container_name: doganai-portable-redis
    restart: unless-stopped
    volumes:
      - ./data/redis:/data
    ports:
      - "6380:6379"
    networks:
      - doganai-net

networks:
  doganai-net:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

    # Create run scripts
    cat > "$target_dir/run.sh" << 'EOF'
#!/bin/bash
echo "Starting DoganAI Compliance Kit (Portable)..."
docker-compose -f docker-compose.portable.yml up -d --build
echo ""
echo "✅ Started! Access the application at:"
echo "   📱 App: http://localhost:8080"
echo "   📚 Docs: http://localhost:8080/docs"
echo "   💾 DB: localhost:5433"
echo ""
echo "To stop: ./stop.sh"
echo "To view logs: docker-compose -f docker-compose.portable.yml logs -f"
EOF

    cat > "$target_dir/run.bat" << 'EOF'
@echo off
echo Starting DoganAI Compliance Kit (Portable)...
docker-compose -f docker-compose.portable.yml up -d --build
echo.
echo ✅ Started! Access the application at:
echo    📱 App: http://localhost:8080
echo    📚 Docs: http://localhost:8080/docs
echo    💾 DB: localhost:5433
echo.
echo To stop: stop.bat
echo To view logs: docker-compose -f docker-compose.portable.yml logs -f
pause
EOF

    cat > "$target_dir/stop.sh" << 'EOF'
#!/bin/bash
echo "Stopping DoganAI Compliance Kit..."
docker-compose -f docker-compose.portable.yml down
echo "Stopped!"
EOF

    cat > "$target_dir/stop.bat" << 'EOF'
@echo off
echo Stopping DoganAI Compliance Kit...
docker-compose -f docker-compose.portable.yml down
echo Stopped!
pause
EOF

    # Make scripts executable
    chmod +x "$target_dir"/*.sh

    # Create README
    cat > "$target_dir/README.md" << 'EOF'
# DoganAI Compliance Kit - Portable Deployment

This is a completely portable deployment that includes the application source code.

## Requirements

- Docker
- Docker Compose

## Quick Start

### Linux/macOS:
```bash
./run.sh
```

### Windows:
```cmd
run.bat
```

## Access Points

- **Application**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Database**: localhost:5433 (doganai/doganai)
- **Redis**: localhost:6380

## Management

- **Start**: `./run.sh` (or `run.bat` on Windows)
- **Stop**: `./stop.sh` (or `stop.bat` on Windows)
- **Logs**: `docker-compose -f docker-compose.portable.yml logs -f`
- **Status**: `docker-compose -f docker-compose.portable.yml ps`

## Features

✅ **Self-contained** - Includes all source code  
✅ **Portable** - Copy folder anywhere and run  
✅ **No build required** - Uses local Dockerfile  
✅ **Persistent data** - Data stored in `./data/`  
✅ **Cross-platform** - Works on Windows, macOS, Linux  

## Folder Structure

```
doganai-portable/
├── app/                    # Application source code
│   ├── src/               # Python source
│   ├── requirements-api.txt
│   └── Dockerfile.portable
├── data/                  # Persistent data
│   ├── postgres/         # Database files
│   └── redis/            # Redis data
├── config/               # Configuration files
├── docker-compose.portable.yml
├── run.sh / run.bat      # Start scripts
├── stop.sh / stop.bat    # Stop scripts
└── README.md             # This file
```

## Troubleshooting

1. **Port conflicts**: Edit `docker-compose.portable.yml` to change ports
2. **Permission issues**: Ensure Docker has access to the folder
3. **Build failures**: Check Docker logs with `docker-compose logs`

## Customization

- **Environment**: Edit `app/.env`
- **Ports**: Edit `docker-compose.portable.yml`
- **Database**: Default credentials are `doganai/doganai`

This deployment is perfect for:
- Development environments
- Internal testing
- Demonstrations
- Offline environments
EOF

    print_success "Portable deployment created in: $target_dir"
    print_status "To use:"
    echo "  1. cd $target_dir"
    echo "  2. ./run.sh (Linux/macOS) or run.bat (Windows)"
    echo "  3. Open http://localhost:8080"
}

# Run the function
create_portable_deployment "$1"
