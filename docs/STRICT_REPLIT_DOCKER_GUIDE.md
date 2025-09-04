# 🚀 Strict Replit Environment with Docker Automation

## 📋 Overview

This guide provides a complete setup for a **strict Replit environment** with Docker automation, automated IP allocation, and security best practices for the DoganAI Compliance Kit.

## 🎯 Key Features

- 🔒 **Strict Security**: Non-root containers, security scanning, best practices
- 🌐 **Automated IP Allocation**: Dynamic IP management and networking
- 🐳 **Docker Automation**: Complete CI/CD pipeline with testing
- 📊 **Monitoring**: Prometheus, Grafana, health checks
- 🔍 **Security Scanning**: Vulnerability detection and compliance checks
- 🚀 **Production Ready**: Multi-stage builds, optimization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Strict Replit Environment                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Nginx     │  │  Prometheus │  │   Grafana   │         │
│  │  Reverse    │  │  Monitoring │  │  Dashboard  │         │
│  │   Proxy     │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Main App  │  │ PostgreSQL  │  │    Redis    │         │
│  │ (Streamlit) │  │  Database   │  │    Cache    │         │
│  │ (FastAPI)   │  │             │  │             │         │
│  │ (React)     │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Security  │  │   Testing   │  │   Build     │         │
│  │   Scanner   │  │   Container │  │ Automation  │         │
│  │  (Trivy)    │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Step 1: Build and Deploy

```bash
# Build the complete environment
docker-compose -f docker-compose.strict.yml build

# Deploy all services
docker-compose -f docker-compose.strict.yml up -d

# Check status
docker-compose -f docker-compose.strict.yml ps
```

### Step 2: Run Automation Pipeline

```bash
# Run complete build pipeline
python docker/automation/build_automation.py pipeline

# Or run individual steps
python docker/automation/build_automation.py build
python docker/automation/build_automation.py test
python docker/automation/build_automation.py scan
python docker/automation/build_automation.py deploy
```

### Step 3: Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:5000 | Main compliance interface |
| **FastAPI Backend** | http://localhost:8000 | REST API |
| **React Frontend** | http://localhost:3000 | Modern web interface |
| **Nginx Proxy** | http://localhost:80 | Reverse proxy |
| **Prometheus** | http://localhost:9090 | Metrics monitoring |
| **Grafana** | http://localhost:3001 | Dashboard (admin/admin) |

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Application
SECRET_KEY=your-super-secret-key-change-this
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://postgres:postgres@doganai-db:5432/doganai_compliance
REDIS_URL=redis://doganai-redis:6379

# Docker Registry (optional)
DOCKER_REGISTRY=your-registry.com
IMAGE_TAG=latest

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Network Configuration

The system automatically allocates IPs in the `172.20.0.0/16` subnet:

```bash
# View network configuration
docker network ls
docker network inspect doganai-network

# Check IP allocation
python docker/automation/ip_allocator.py
```

## 🔒 Security Features

### Automated Security Scanning

```bash
# Run comprehensive security scan
python docker/automation/security_scan.py full

# Scan specific components
python docker/automation/security_scan.py image
python docker/automation/security_scan.py dockerfile
python docker/automation/security_scan.py compose
python docker/automation/security_scan.py environment
python docker/automation/security_scan.py network
```

### Security Best Practices Implemented

- ✅ **Non-root containers**: All services run as non-root users
- ✅ **Multi-stage builds**: Optimized image sizes
- ✅ **Health checks**: Automatic service monitoring
- ✅ **Network isolation**: Custom bridge network
- ✅ **Vulnerability scanning**: Trivy integration
- ✅ **Secret management**: Environment variables
- ✅ **Read-only filesystems**: Where possible
- ✅ **Security options**: Docker security profiles

## 📊 Monitoring & Observability

### Prometheus Metrics

```bash
# View metrics
curl http://localhost:9090/metrics

# Check targets
curl http://localhost:9090/api/v1/targets
```

### Grafana Dashboards

1. Access Grafana: http://localhost:3001
2. Login: `admin` / `admin`
3. Import dashboards from `monitoring/grafana/dashboards/`

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker exec doganai-compliance-db pg_isready -U postgres

# Redis health
docker exec doganai-compliance-redis redis-cli ping
```

## 🔄 Automation Pipeline

### Build Pipeline Steps

1. **Build Image**: Multi-stage Docker build
2. **Run Tests**: Unit, integration, security tests
3. **Security Scan**: Vulnerability and configuration checks
4. **Push Image**: To registry (if configured)
5. **Deploy**: Automatic deployment

### Pipeline Commands

```bash
# Full pipeline
python docker/automation/build_automation.py pipeline

# Individual steps
python docker/automation/build_automation.py build
python docker/automation/build_automation.py test
python docker/automation/build_automation.py scan
python docker/automation/build_automation.py deploy production
```

## 🌐 IP Allocation System

### Automatic IP Management

```bash
# Run IP allocation
python docker/automation/ip_allocator.py

# View network info
docker network inspect doganai-network

# Check container IPs
docker inspect doganai-compliance-app | grep IPAddress
```

### Network Configuration

The system automatically:
- Creates custom bridge network
- Allocates unique IPs to containers
- Updates DNS resolution
- Generates network configuration
- Runs connectivity diagnostics

## 🧪 Testing

### Automated Testing

```bash
# Run all tests
docker-compose -f docker-compose.strict.yml run doganai-tests

# Run specific test suites
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/security/
```

### Test Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

## 📈 Performance Optimization

### Multi-stage Builds

```dockerfile
# Development stage
FROM python:3.11-slim as development
# ... development setup

# Production stage
FROM python:3.11-slim as production
# ... optimized production setup
```

### Resource Limits

```yaml
# In docker-compose.strict.yml
services:
  doganai-app:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Startup Failures

```bash
# Check container logs
docker-compose -f docker-compose.strict.yml logs doganai-app

# Check health status
docker-compose -f docker-compose.strict.yml ps
```

#### 2. Network Connectivity

```bash
# Test network connectivity
docker exec doganai-compliance-app ping doganai-db

# Check DNS resolution
docker exec doganai-compliance-app nslookup doganai-db
```

#### 3. Security Scan Failures

```bash
# Run security scan with verbose output
python docker/automation/security_scan.py full --verbose

# Check specific vulnerabilities
python docker/automation/security_scan.py image doganai-compliance:latest
```

### Debug Commands

```bash
# Enter container for debugging
docker exec -it doganai-compliance-app bash

# Check network configuration
docker exec doganai-compliance-app cat /app/config/network.conf

# View logs
docker logs -f doganai-compliance-app

# Check resource usage
docker stats doganai-compliance-app
```

## 📚 Best Practices

### Development Workflow

1. **Local Development**:
   ```bash
   docker-compose -f docker-compose.strict.yml up -d
   ```

2. **Testing**:
   ```bash
   python docker/automation/build_automation.py test
   ```

3. **Security Check**:
   ```bash
   python docker/automation/security_scan.py full
   ```

4. **Deployment**:
   ```bash
   python docker/automation/build_automation.py deploy
   ```

### Production Deployment

1. **Environment Setup**:
   ```bash
   export ENVIRONMENT=production
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Deploy**:
   ```bash
   docker-compose -f docker-compose.strict.yml -f docker-compose.production.yml up -d
   ```

3. **Monitor**:
   ```bash
   # Check health
   curl http://localhost:8000/health
   
   # View metrics
   curl http://localhost:9090/metrics
   ```

## 🚀 Advanced Features

### Custom Health Checks

```python
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "services": {
            "database": check_database(),
            "redis": check_redis(),
            "api": check_api_endpoints()
        },
        "metrics": {
            "uptime": get_uptime(),
            "memory": get_memory_usage(),
            "requests": get_request_count()
        }
    }
```

### Custom Monitoring

```yaml
# Add custom metrics to Prometheus
- job_name: 'doganai-compliance'
  static_configs:
    - targets: ['doganai-app:8000']
  metrics_path: '/metrics'
  scrape_interval: 30s
```

### Backup and Recovery

```bash
# Database backup
docker exec doganai-compliance-db pg_dump -U postgres doganai_compliance > backup.sql

# Restore database
docker exec -i doganai-compliance-db psql -U postgres doganai_compliance < backup.sql
```

## 📞 Support

### Getting Help

1. **Check Logs**: `docker-compose logs [service-name]`
2. **Health Checks**: `curl http://localhost:8000/health`
3. **Network Issues**: `python docker/automation/ip_allocator.py`
4. **Security Issues**: `python docker/automation/security_scan.py full`

### Useful Commands

```bash
# View all containers
docker ps -a

# Check resource usage
docker stats

# View network configuration
docker network ls
docker network inspect doganai-network

# Run diagnostics
python docker/automation/ip_allocator.py
python docker/automation/security_scan.py full
```

---

**🎯 Ready to deploy? Run `docker-compose -f docker-compose.strict.yml up -d` and start building!**
