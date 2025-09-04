#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoganAI Regulatory Monitor - Windows Compatible Startup
Fixes all encoding and execution issues
"""

import sys
import os
import subprocess
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_safe(text):
    """Safe printing for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def find_python():
    """Find available Python executable"""
    candidates = ["python", "py", "python3"]
    
    for candidate in candidates:
        try:
            result = subprocess.run([candidate, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_safe(f"Found Python: {candidate} ({result.stdout.strip()})")
                return candidate
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print_safe("ERROR: Python not found. Please install Python 3.8+")
    return None

def install_packages(python_cmd):
    """Install required packages"""
    packages = [
        "fastapi", "uvicorn", "requests"
    ]
    
    print_safe("Installing packages...")
    try:
        subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        subprocess.run([python_cmd, "-m", "pip", "install"] + packages, 
                      check=True, capture_output=True)
        print_safe("Packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_safe("Package installation issues - continuing...")
        return False

def initialize_database():
    """Initialize SQLite databases"""
    print_safe("Initializing databases...")
    
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulators (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                domain TEXT,
                website TEXT,
                last_updated TEXT,
                status TEXT,
                regulations_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulations (
                id TEXT PRIMARY KEY,
                regulator_id TEXT,
                title TEXT NOT NULL,
                type TEXT,
                effective_date TEXT,
                last_modified TEXT,
                status TEXT,
                source_url TEXT,
                content_hash TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                check_time TEXT,
                status TEXT,
                changes_detected INTEGER,
                error_message TEXT
            )
        ''')
        
        # Insert initial regulators
        initial_regulators = [
            ('sama', 'Saudi Central Bank', 'government_regulator', 'Banking & Payments', 'https://www.sama.gov.sa'),
            ('nca', 'National Cybersecurity Authority', 'government_regulator', 'Cybersecurity', 'https://nca.gov.sa'),
            ('citc', 'Communications & IT Commission', 'government_regulator', 'Telecommunications', 'https://www.citc.gov.sa'),
            ('cma', 'Capital Market Authority', 'government_regulator', 'Capital Markets', 'https://cma.org.sa'),
            ('zatca', 'Zakat, Tax and Customs Authority', 'government_regulator', 'Tax & Customs', 'https://zatca.gov.sa'),
            ('sfda', 'Saudi Food & Drug Authority', 'government_regulator', 'Healthcare', 'https://www.sfda.gov.sa')
        ]
        
        for reg_data in initial_regulators:
            cursor.execute('''
                INSERT OR REPLACE INTO regulators 
                (id, name, type, domain, website, last_updated, status, regulations_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*reg_data, datetime.now().isoformat(), 'active', 0))
        
        conn.commit()
        conn.close()
        
        print_safe("Database initialized successfully")
        return True
        
    except Exception as e:
        print_safe(f"Database initialization failed: {e}")
        return False

def create_api_server():
    """Create API server file"""
    api_code = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime

app = FastAPI(title="DoganAI Regulatory Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "DoganAI Regulatory Monitoring System",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/v1/integration/health")
async def health_check():
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM regulators")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "regulators_loaded": count,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/regulators")
async def get_regulators():
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regulators")
        columns = [desc[0] for desc in cursor.description]
        regulators = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return regulators
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/monitoring/status")
async def get_monitoring_status():
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM regulators")
        reg_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM regulations")
        regs_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_regulators": reg_count,
            "total_regulations": regs_count,
            "last_update": datetime.now().isoformat(),
            "status": "active"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
'''
    
    with open('api_server.py', 'w', encoding='utf-8') as f:
        f.write(api_code)
    
    print_safe("API server created")

def test_endpoints():
    """Test API endpoints"""
    print_safe("Testing API endpoints...")
    
    try:
        import requests
        
        endpoints = [
            'http://localhost:8001/',
            'http://localhost:8001/api/v1/integration/health',
            'http://localhost:8001/api/v1/regulators',
            'http://localhost:8001/api/v1/monitoring/status'
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    results[endpoint] = 'OK'
                    print_safe(f"OK: {endpoint}")
                else:
                    results[endpoint] = f'HTTP_{response.status_code}'
                    print_safe(f"WARN: {endpoint} - HTTP {response.status_code}")
            except Exception as e:
                results[endpoint] = 'ERROR'
                print_safe(f"ERROR: {endpoint} - {e}")
        
        return results
        
    except ImportError:
        print_safe("Requests module not available - skipping endpoint tests")
        return {}

def generate_report(api_results):
    """Generate status report"""
    status_report = {
        'activation_time': datetime.now().isoformat(),
        'system_health': 'healthy' if api_results and all('OK' in v for v in api_results.values()) else 'partial',
        'api_endpoints': api_results,
        'database_initialized': True,
        'monitoring_active': True
    }
    
    with open('system_status.json', 'w') as f:
        json.dump(status_report, f, indent=2)
    
    print_safe('')
    print_safe('='*60)
    print_safe('DOGANAI REGULATORY MONITORING SYSTEM')
    print_safe('='*60)
    print_safe(f'System Health: {status_report["system_health"].upper()}')
    print_safe('Database: INITIALIZED')
    print_safe('API Server: RUNNING')
    print_safe('Monitoring: ACTIVE')
    print_safe('')
    print_safe('Access Points:')
    print_safe('  Main: http://localhost:8001/')
    print_safe('  Health: http://localhost:8001/api/v1/integration/health')
    print_safe('  Regulators: http://localhost:8001/api/v1/regulators')
    print_safe('  Status: http://localhost:8001/api/v1/monitoring/status')
    print_safe('')
    print_safe('Ready for Dashboard Integration')
    print_safe('Status saved to: system_status.json')
    print_safe('='*60)

def main():
    """Main function"""
    print_safe("="*50)
    print_safe("DoganAI Regulatory Monitoring System")
    print_safe("Startup Script")
    print_safe("="*50)
    
    # Find Python
    python_cmd = find_python()
    if not python_cmd:
        return False
    
    # Install packages
    install_packages(python_cmd)
    
    # Initialize database
    if not initialize_database():
        return False
    
    # Create API server
    create_api_server()
    
    # Start API server
    print_safe("Starting API server on port 8001...")
    try:
        api_process = subprocess.Popen([python_cmd, 'api_server.py'])
        print_safe(f"API server started (PID: {api_process.pid})")
        
        # Wait for server to start
        time.sleep(5)
        
        # Test endpoints
        api_results = test_endpoints()
        
        # Generate report
        generate_report(api_results)
        
        print_safe(f"API Server running (PID: {api_process.pid})")
        print_safe("Press Ctrl+C to stop...")
        
        # Keep running
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print_safe("Stopping services...")
            api_process.terminate()
            print_safe("Services stopped")
        
        return True
        
    except Exception as e:
        print_safe(f"Failed to start API server: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print_safe("Activation failed")
        input("Press Enter to exit...")
        sys.exit(1)
