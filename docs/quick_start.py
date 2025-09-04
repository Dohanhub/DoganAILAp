#!/usr/bin/env python3
"""
Quick Start Script for DoganAI Compliance Kit
Automates the setup process for Replit deployment
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if we're in Replit
    if os.path.exists("/home/runner"):
        print("✅ Running in Replit environment")
    else:
        print("⚠️  Not running in Replit - some features may not work")
    
    return True

def setup_python_dependencies():
    """Install Python dependencies"""
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("python -m pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def setup_frontend_dependencies():
    """Install frontend dependencies"""
    if not os.path.exists("frontend"):
        print("❌ Frontend directory not found")
        return False
    
    if not run_command("cd frontend && npm install", "Installing frontend dependencies"):
        return False
    
    return True

def setup_database():
    """Setup the database"""
    if not run_command("python setup_database.py", "Setting up database"):
        return False
    
    return True

def create_health_check():
    """Create a health check endpoint"""
    health_check_content = '''
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psycopg2
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Replit"""
    try:
        # Check database connection
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/doganai_compliance")
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        
        return JSONResponse({
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("health_check.py", "w") as f:
        f.write(health_check_content)
    
    print("✅ Health check endpoint created")

def main():
    """Main setup function"""
    print("🚀 DoganAI Compliance Kit - Quick Start Setup")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Setup Python dependencies
    if not setup_python_dependencies():
        sys.exit(1)
    
    # Step 3: Setup frontend dependencies
    if not setup_frontend_dependencies():
        sys.exit(1)
    
    # Step 4: Setup database
    if not setup_database():
        sys.exit(1)
    
    # Step 5: Create health check
    create_health_check()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Click the 'Run' button in Replit")
    print("2. The application will start automatically")
    print("3. Access the Streamlit dashboard at the main URL")
    print("4. Access the React frontend at: https://your-repl-name.your-username.repl.co:3000")
    print("5. Access the API at: https://your-repl-name.your-username.repl.co:8000")
    print("6. Health check at: https://your-repl-name.your-username.repl.co:8000/health")
    
    print("\n🔧 Available Commands:")
    print("- streamlit run app.py (Streamlit Dashboard)")
    print("- python backend/server_complete.py (Backend API)")
    print("- cd frontend && npm run dev (React Frontend)")
    print("- python health_check.py (Health Check)")

if __name__ == "__main__":
    main()
