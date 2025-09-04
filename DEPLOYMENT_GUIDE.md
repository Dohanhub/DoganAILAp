# DoganAI Compliance Kit - Internal Folder Deployment Guide

This guide provides multiple options for deploying the DoganAI Compliance Kit internally within your organization or on local systems.

## 📁 Deployment Options

### Option 1: Quick Internal Deployment (Recommended)

**Use Case**: Production-ready deployment in internal networks

**Setup**:
```bash
# Linux/macOS
bash deploy-internal.sh [target-folder]

# Windows
deploy-internal.bat [target-folder]
```

**Features**:
- ✅ Production-ready configuration
- ✅ Monitoring with Prometheus/Grafana
- ✅ Automated backup scripts
- ✅ Health checks and management tools
- ✅ Secure defaults

### Option 2: Portable Development Deployment

**Use Case**: Development, testing, demonstrations

**Setup**:
```bash
bash create-portable.sh [target-folder]
```

**Features**:
- ✅ Includes source code
- ✅ Self-contained
- ✅ Easy to move between systems
- ✅ Quick setup

### Option 3: Current Directory Deployment

**Use Case**: Using your current workspace

You already have everything set up! Just run:

```bash
# Start current environment
docker-compose -f docker-compose.production.yml up -d

# Or use convenience scripts
./docker-start.sh start    # Linux/macOS
docker-start.bat start     # Windows
```

## 🚀 Quick Start Guide

### For Internal Production Deployment:

1. **Run the deployment script**:
   ```bash
   # This creates a complete deployment folder
   bash deploy-internal.sh my-doganai-deployment
   ```

2. **Navigate to deployment folder**:
   ```bash
   cd my-doganai-deployment
   ```

3. **Review configuration**:
   ```bash
   # Edit environment variables
   nano .env
   ```

4. **Start the application**:
   ```bash
   ./start.sh              # Linux/macOS
   start.bat               # Windows
   ```

5. **Access your application**:
   - **Main App**: http://localhost:8080
   - **API Docs**: http://localhost:8080/docs
   - **Health Check**: http://localhost:8080/health

## 🔧 Configuration Options

### Environment Variables (.env)

```env
# Application Settings
APP_NAME=DoganAI Compliance Kit
APP_ENVIRONMENT=production
SECRET_KEY=your-secret-key-change-this-in-production

# Database Configuration
POSTGRES_USER=doganai_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=doganai_compliance

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Port Configuration

Default ports:
- **Application**: 8080
- **Database**: 5433
- **Redis**: 6380
- **Grafana**: 3000 (if monitoring enabled)
- **Prometheus**: 9090 (if monitoring enabled)

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:8000"  # Change YOUR_PORT
```

## 📊 Management Commands

### Linux/macOS Commands:
```bash
./start.sh              # Start all services
./stop.sh               # Stop all services
./status.sh             # Check service status
./logs.sh               # View all logs
./logs.sh app           # View app logs only
./backup.sh             # Create backup
./update.sh             # Update application
```

### Windows Commands:
```cmd
start.bat               REM Start all services
stop.bat                REM Stop all services
status.bat              REM Check service status
logs.bat                REM View all logs
logs.bat app            REM View app logs only
backup.bat              REM Create backup
update.bat              REM Update application
```

## 🗂️ Folder Structure

After deployment, you'll have:

```
doganai-deployment/
├── docker-compose.yml          # Service definitions
├── .env                        # Environment configuration
├── README.md                   # Quick reference
│
├── scripts/                    # Management scripts
│   ├── start.sh / start.bat
│   ├── stop.sh / stop.bat
│   ├── status.sh / status.bat
│   ├── logs.sh / logs.bat
│   ├── backup.sh / backup.bat
│   └── update.sh / update.bat
│
├── config/                     # Configuration files
│   ├── prometheus.yml          # Monitoring config
│   └── grafana/               # Dashboard configs
│
├── data/                       # Persistent data
│   ├── postgres/              # Database files
│   ├── redis/                 # Redis data
│   ├── prometheus/            # Metrics data
│   └── grafana/               # Dashboard data
│
├── logs/                       # Application logs
│
└── backups/                    # Automated backups
    └── YYYYMMDD_HHMMSS/       # Timestamped backups
```

## 🔒 Security Considerations

### Essential Security Steps:

1. **Change default passwords**:
   ```bash
   # Edit .env file
   POSTGRES_PASSWORD=your-strong-password
   SECRET_KEY=your-secret-key
   ```

2. **Network security**:
   - Use firewall rules to restrict access
   - Consider VPN for remote access
   - Use HTTPS in production

3. **Regular backups**:
   ```bash
   ./backup.sh  # Creates timestamped backup
   ```

4. **Monitor logs**:
   ```bash
   ./logs.sh    # Check for suspicious activity
   ```

## 🏥 Health Monitoring

### Built-in Health Checks:

- **Application Health**: http://localhost:8080/health
- **Service Status**: `./status.sh`
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)

### Monitoring Commands:
```bash
# Check application health
curl http://localhost:8080/health

# Check all services
docker-compose ps

# Monitor resources
docker stats
```

## 🚨 Troubleshooting

### Common Issues:

1. **Port conflicts**:
   ```bash
   # Check what's using port 8080
   netstat -tulpn | grep 8080
   # Or on Windows
   netstat -an | findstr :8080
   ```

2. **Docker not running**:
   ```bash
   # Check Docker status
   docker info
   ```

3. **Permission issues**:
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER ./data
   ```

4. **Service not starting**:
   ```bash
   # Check logs for specific service
   ./logs.sh app
   ./logs.sh db
   ./logs.sh redis
   ```

### Reset Everything:
```bash
# Stop services
./stop.sh

# Remove data (WARNING: This deletes all data!)
rm -rf data/

# Start fresh
./start.sh
```

## 📈 Scaling and Performance

### For Higher Load:

1. **Increase application replicas**:
   ```yaml
   # In docker-compose.yml
   services:
     app:
       deploy:
         replicas: 3
   ```

2. **Add load balancer**:
   ```yaml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
     # Add nginx config for load balancing
   ```

3. **Database optimization**:
   ```yaml
   db:
     environment:
       - POSTGRES_SHARED_BUFFERS=256MB
       - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
   ```

## 🆘 Support and Maintenance

### Regular Maintenance:

1. **Weekly backups**:
   ```bash
   # Add to crontab
   0 2 * * 0 /path/to/deployment/backup.sh
   ```

2. **Update checks**:
   ```bash
   ./update.sh  # Pull latest versions
   ```

3. **Log rotation**:
   ```bash
   # Clear old logs (optional)
   docker-compose logs --tail=1000 > recent.log
   ```

### Getting Help:

1. **Check application logs**: `./logs.sh app`
2. **Check database logs**: `./logs.sh db`
3. **Check system resources**: `docker stats`
4. **Review configuration**: Check `.env` and `docker-compose.yml`

## 🎯 Next Steps

After successful deployment:

1. **Configure authentication** - Set up user accounts
2. **Import policies** - Add your compliance policies
3. **Set up monitoring** - Configure alerts and dashboards
4. **Schedule backups** - Set up automated backups
5. **Train users** - Provide access to documentation

---

**Your DoganAI Compliance Kit is ready for internal deployment!** 🚀

Choose the deployment option that best fits your needs and follow the corresponding setup guide above.
