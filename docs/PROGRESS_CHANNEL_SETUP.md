# 🚀 Progress Channel & Reporter Setup Guide

## 📋 Overview

The Progress Channel & Reporter system creates a seamless connection between GitHub and Replit for your DoganAI Compliance Kit. It provides:

- 🔄 **Automated Monitoring**: Build, test, and health status updates
- 💬 **ChatOps**: `/ops` commands for quick configuration changes
- 📊 **Real-time Status**: Live updates on Replit deployment health
- 🔗 **Team Coordination**: Single channel for all development updates

## 🎯 Quick Setup (5 minutes)

### Step 1: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

1. **REPLIT_HEALTH_URL**: Your Replit health endpoint
   ```
   https://your-repl-name.your-username.repl.co/health
   ```

2. **SLACK_WEBHOOK** (optional): Slack notifications
   ```
   https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

### Step 2: Create Progress Channel Issue

1. Go to your GitHub repository Issues
2. Create a new issue titled **"Progress Channel"**
3. Add labels: `ops`, `automation`
4. Use the template from `.github/ISSUE_TEMPLATE/progress.md`

### Step 3: Enable Workflows

The following workflows are now active:

- **Progress Reporter** (`.github/workflows/progress-reporter.yml`)
- **ChatOps Handler** (`.github/workflows/chatops.yml`)

## 🔧 How It Works

### Automated Monitoring

Every 30 minutes and on every push, the system:

1. ✅ **Builds Frontend**: React/Next.js compilation
2. 🔧 **Tests Backend**: FastAPI module imports
3. 🧪 **Runs Tests**: pytest test suite
4. 🌐 **Health Check**: Pings Replit health endpoint
5. 🗄️ **Database Check**: PostgreSQL connectivity
6. 💬 **Posts Update**: Comments on Progress Channel issue

### ChatOps Commands

Use `/ops` in issue comments to:

```yaml
/ops
set_env:
  .replit:
    NODE_ENV: production
    DATABASE_URL: "your-new-db-url"
write_files:
  - path: config/production.json
    content: |
      {"environment": "production"}
commit:
  message: "ops: production configuration"
```

## 📊 Status Indicators

| Status | Emoji | Meaning |
|--------|-------|---------|
| `success` | ✅ | All checks passed |
| `up` | 🟢 | Replit is online |
| `connected` | 🔗 | Database connected |
| `failed` | ❌ | Build/test failed |
| `down` | 🔴 | Replit is offline |
| `disconnected` | 🔌 | Database disconnected |

## 🛠️ Available Commands

### Environment Management

**Set environment variables:**
```yaml
/ops
set_env:
  .replit:
    NODE_ENV: production
    DATABASE_URL: "postgresql://..."
    SECRET_KEY: "your-secret"
```

### File Operations

**Create/update files:**
```yaml
/ops
write_files:
  - path: backend/config.py
    content: |
      DATABASE_URL = "postgresql://..."
      SECRET_KEY = "your-secret"
```

**Apply patches:**
```yaml
/ops
patches:
  - path: app.py
    find: "DEBUG = True"
    replace: "DEBUG = False"
```

### Git Operations

**Commit changes:**
```yaml
/ops
commit:
  message: "ops: production deployment"
```

## 🔍 Monitoring Your Replit

### Health Endpoint

Your Replit should expose a health endpoint at `/health`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    }
```

### Health Check Script

The system includes a health check script (`health_check.py`) that:

- ✅ Tests database connectivity
- 🔗 Verifies API endpoints
- 📊 Reports system status
- 🚨 Alerts on failures

## 🚨 Troubleshooting

### Common Issues

#### 1. Health Check Failing
```bash
# Check if health endpoint exists
curl https://your-repl.your-username.repl.co/health

# Verify Replit is running
# Check console for errors
```

#### 2. Database Connection Issues
```bash
# Test database connection
python .github/scripts/db_check.py

# Check DATABASE_URL in .replit
cat .replit | grep DATABASE_URL
```

#### 3. Build Failures
```bash
# Check frontend build
cd frontend && npm run build

# Check backend imports
python .github/scripts/backend_check.py
```

#### 4. ChatOps Not Working
- Ensure you have write permissions to the repository
- Check that the issue has the `ops` label
- Verify YAML syntax in `/ops` commands

### Debugging Commands

```bash
# Test health endpoint locally
python health_check.py

# Check workflow logs
# Go to Actions tab in GitHub

# Test ChatOps locally
echo '/ops
set_env:
  .replit:
    TEST: "value"' > test_ops.txt
python .github/scripts/chatops_handler.py test_ops.txt
```

## 📱 Team Workflow

### For Replit Teammate:
1. `git pull` before starting work
2. Press **Run** in Replit
3. Monitor console for any errors
4. Check Progress Channel for status updates

### For GitHub Manager:
1. Watch Progress Channel issue
2. Use `/ops` commands for quick changes
3. Tag teammates for urgent issues
4. Monitor build/test results

## 🔒 Security Considerations

### Permissions
- Only users with repository write access can use `/ops`
- Workflows run with minimal required permissions
- All changes are logged and traceable

### Secrets Management
- Store sensitive data in GitHub Secrets
- Never commit API keys or passwords
- Use environment variables for configuration

### Audit Trail
- All `/ops` commands are logged
- Git commits show who made changes
- Progress Channel maintains history

## 🚀 Advanced Features

### Custom Health Checks

Add custom health checks to your Replit:

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

### Slack Integration

Configure Slack notifications:

1. Create Slack app and webhook
2. Add `SLACK_WEBHOOK` secret
3. Receive notifications for:
   - Build failures
   - Health check failures
   - ChatOps commands

### Custom Workflows

Extend the system with custom workflows:

```yaml
# .github/workflows/custom-check.yml
name: Custom Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  custom:
    runs-on: ubuntu-latest
    steps:
      - name: Custom validation
        run: |
          # Your custom checks here
```

## 📈 Success Metrics

Track these metrics to ensure the system is working:

- ✅ **Build Success Rate**: >95%
- 🟢 **Health Check Uptime**: >99%
- ⚡ **Response Time**: <30 seconds
- 🔄 **Deployment Frequency**: Daily

## 🆘 Getting Help

1. **Check Progress Channel**: Latest status and errors
2. **Review Workflow Logs**: Detailed error information
3. **Test Locally**: Use provided scripts
4. **Contact Team**: Tag relevant team members

## 📚 Related Documentation

- [Replit Setup Guide](./REPLIT_SETUP_GUIDE.md)
- [API Configuration](./API_CONFIGURATION_GUIDE.md)
- [Database Setup](./setup_database.py)
- [Quick Start](./quick_start.py)

---

**🎯 Ready to start? Create the Progress Channel issue and watch the magic happen!**
