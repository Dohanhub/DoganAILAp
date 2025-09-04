# 🚀 Local Deployment Guide - DoganAI Compliance Kit

This guide will help you deploy and test the DoganAI Compliance Kit locally on your Windows machine.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (latest version)
- **PowerShell** (Windows 10/11)
- **Git** (for cloning the repository)

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Deployment with Desktop Icon

1. **Double-click** `deploy-local.bat` in the project root
2. The script will automatically:
   - Check prerequisites
   - Start PostgreSQL and Redis
   - Deploy all microservices
   - Create a desktop icon
   - Perform health checks

### Option 2: PowerShell Deployment

1. **Open PowerShell** as Administrator
2. **Navigate** to the project directory
3. **Run** the deployment script:

```powershell
# Full deployment with desktop icon
.\deploy-local.ps1 -CreateDesktopIcon

# Or customize the deployment:
.\deploy-local.ps1 -SkipDatabase -SkipRedis -CreateDesktopIcon
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or encounter issues:

### 1. Start Database Services

```powershell
# PostgreSQL
docker run -d --name postgres-local `
    -e POSTGRES_DB=doganai_local `
    -e POSTGRES_USER=doganai_user `
    -e POSTGRES_PASSWORD=doganai_password `
    -p 5432:5432 `
    postgres:15-alpine

# Redis
docker run -d --name redis-local `
    -p 6379:6379 `
    redis:7-alpine
```

### 2. Deploy Microservices

```powershell
cd microservices
docker-compose up -d --build
```

### 3. Create Desktop Icon

```powershell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$iconPath = Join-Path $desktopPath "DoganAI Compliance Kit.url"

$iconContent = @"
[InternetShortcut]
URL=http://localhost:8501
IconFile=C:\Windows\System32\SHELL32.dll
IconIndex=1
"@

$iconContent | Out-File -FilePath $iconPath -Encoding ASCII
```

## 🌐 Access Points

Once deployed, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Main UI** | http://localhost:8501 | Streamlit-based user interface |
| **Compliance API** | http://localhost:8000 | Core compliance engine API |
| **Benchmarks** | http://localhost:8001 | KPI benchmarks service |
| **AI/ML** | http://localhost:8002 | AI/ML processing service |
| **Integrations** | http://localhost:8003 | External integrations service |
| **Prometheus** | http://localhost:9090 | Metrics and monitoring |
| **Grafana** | http://localhost:3000 | Dashboards (admin/admin) |

## 🧪 Testing the Application

### 1. Basic Health Check

Visit each service's health endpoint:
- http://localhost:8000/health
- http://localhost:8001/health
- http://localhost:8002/health
- http://localhost:8003/health

### 2. Main UI Testing

1. **Open** http://localhost:8501 in your browser
2. **Navigate** through the compliance evaluation interface
3. **Test** the policy evaluation features
4. **Check** the monitoring dashboards

### 3. API Testing

Use tools like Postman or curl to test the API endpoints:

```bash
# Test compliance evaluation
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local_dev_key_12345" \
  -d '{"vendor": "IBM", "policy": "NCA"}'
```

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```powershell
# Check what's using a port
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

#### Docker Issues
```powershell
# Restart Docker Desktop
# Or restart the service
Restart-Service docker
```

#### Service Not Starting
```powershell
# Check logs
docker-compose logs compliance-engine

# Restart specific service
docker-compose restart compliance-engine
```

### Reset Everything

```powershell
# Stop all services
docker-compose down

# Remove containers
docker rm -f postgres-local redis-local prometheus-local grafana-local

# Remove volumes (WARNING: This will delete all data)
docker volume prune -f

# Start fresh
.\deploy-local.ps1
```

## 📊 Monitoring and Logs

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f compliance-engine

# Real-time logs
docker-compose logs -f --tail=100
```

### Check Metrics

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Database Status

```powershell
# Connect to PostgreSQL
docker exec -it postgres-local psql -U doganai_user -d doganai_local

# Check Redis
docker exec -it redis-local redis-cli ping
```

## 🛠️ Development Mode

For development work:

```powershell
# Enable hot reload
$env:API_RELOAD="true"
$env:UI_RELOAD="true"

# Start with development settings
docker-compose -f docker-compose.dev.yml up
```

## 📁 File Structure

```
DoganAI-Compliance-Kit/
├── deploy-local.ps1          # PowerShell deployment script
├── deploy-local.bat          # Batch file for easy execution
├── env.local                 # Local environment template
├── monitoring/
│   └── prometheus.yml        # Prometheus configuration
├── microservices/
│   ├── docker-compose.yml    # Local development compose
│   ├── compliance-engine/    # Core compliance service
│   ├── benchmarks/           # KPI benchmarks
│   ├── ai-ml/               # AI/ML processing
│   ├── integrations/         # External integrations
│   └── ui/                  # Streamlit UI
└── LOCAL_DEPLOYMENT_GUIDE.md # This guide
```

## 🚀 Next Steps

After successful local deployment:

1. **Test** all compliance evaluation features
2. **Explore** the monitoring dashboards
3. **Review** logs for any issues
4. **Customize** configurations as needed
5. **Scale** services for your requirements

## 📞 Support

If you encounter issues:

1. **Check** the troubleshooting section above
2. **Review** the logs for error messages
3. **Verify** all prerequisites are installed
4. **Check** port availability
5. **Restart** Docker Desktop if needed

---

**Happy Testing! 🎉**

The DoganAI Compliance Kit is now running locally on your machine with a convenient desktop icon for easy access.
