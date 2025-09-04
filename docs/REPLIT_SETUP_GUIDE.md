# 🚀 DoganAI Compliance Kit - Replit Setup Guide

## 📋 Overview
This guide will help you set up and run the DoganAI Compliance Kit on Replit. The platform provides automated compliance validation against Saudi Arabia's regulatory landscape (NCA, SAMA, PDPL) and international standards.

## 🎯 Quick Start (5 minutes)

### Step 1: Fork/Create Replit
1. Go to [Replit](https://replit.com)
2. Create a new Repl or fork this project
3. Choose **"Python"** as the language

### Step 2: Run Quick Setup
```bash
python quick_start.py
```

### Step 3: Start the Application
Click the **"Run"** button in Replit. The application will automatically:
- Install all dependencies
- Setup the database
- Start the Streamlit dashboard
- Launch the backend API
- Start the React frontend

## 🔧 Manual Setup (If Quick Start Fails)

### 1. Install Dependencies
```bash
# Python dependencies
python -m pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Setup Database
```bash
python setup_database.py
```

### 3. Start Services

#### Option A: Streamlit Dashboard (Recommended)
```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

#### Option B: Backend API
```bash
python backend/server_complete.py
```

#### Option C: React Frontend
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit Dashboard** | Main Replit URL | Primary compliance interface |
| **React Frontend** | `https://your-repl.your-username.repl.co:3000` | Modern web interface |
| **Backend API** | `https://your-repl.your-username.repl.co:8000` | REST API endpoints |
| **Health Check** | `https://your-repl.your-username.repl.co:8000/health` | System status |

## 📊 Features Available

### 🛡️ Compliance Frameworks
- **NCA** (National Cybersecurity Authority)
- **SAMA** (Saudi Arabian Monetary Authority)
- **PDPL** (Personal Data Protection Law)
- **ISO 27001** (Information Security)
- **NIST CSF** (Cybersecurity Framework)

### 📈 Dashboard Features
- Real-time compliance scoring
- Risk assessment and management
- Automated evidence collection
- Regulatory reporting
- Arabic language support

### 🔐 Security Features
- OAuth2 + JWT authentication
- Role-based access control
- Audit logging
- Data encryption

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if PostgreSQL is running
python -c "import psycopg2; print('PostgreSQL available')"

# Recreate database
python setup_database.py
```

#### 2. Port Already in Use
```bash
# Kill existing processes
pkill -f streamlit
pkill -f uvicorn
pkill -f node
```

#### 3. Dependencies Not Found
```bash
# Reinstall dependencies
python -m pip install --force-reinstall -r requirements.txt
cd frontend && npm install --force
```

#### 4. Frontend Build Error
```bash
# Clear npm cache
cd frontend
npm cache clean --force
npm install
```

### Environment Variables
Make sure these are set in your `.replit` file:
```toml
[env]
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/doganai_compliance"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-secret-key-here"
ENVIRONMENT = "development"
```

## 🔄 Development Workflow

### 1. Making Changes
- Edit files in the Replit editor
- Changes are automatically saved
- Click "Run" to restart the application

### 2. Testing
```bash
# Run backend tests
python -m pytest tests/

# Run frontend tests
cd frontend && npm test
```

### 3. Database Changes
```bash
# Reset database
python setup_database.py
```

## 📱 Mobile/Desktop Access

### From Mobile Device
1. Get your Replit URL
2. Open in mobile browser
3. The interface is responsive and mobile-friendly

### From Desktop
1. Use the main Replit URL
2. Full desktop experience with all features
3. Export reports and data

## 🔒 Security Notes

### Production Deployment
- Change `SECRET_KEY` to a strong random string
- Set `ENVIRONMENT = "production"`
- Configure proper database credentials
- Enable HTTPS

### Data Privacy
- All data is stored locally in Replit
- No data is sent to external services
- Compliance with Saudi data protection laws

## 📞 Support

### Getting Help
1. Check the troubleshooting section above
2. Review the logs in the Replit console
3. Check the health endpoint: `/health`

### Useful Commands
```bash
# Check system status
python health_check.py

# View logs
tail -f logs/app.log

# Database backup
pg_dump doganai_compliance > backup.sql
```

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ "Setup completed successfully!" message
- ✅ Streamlit dashboard loads with compliance data
- ✅ Health check returns "healthy" status
- ✅ No error messages in the console

## 🚀 Next Steps

After successful setup:
1. Explore the compliance dashboard
2. Add your organization's data
3. Run compliance assessments
4. Generate reports
5. Customize for your specific needs

---

**🎯 Ready to start? Run `python quick_start.py` and click "Run"!**
