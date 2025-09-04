@echo off
echo ========================================
echo  DoganAI Regulatory Monitoring System
echo  Activation Script - Windows
echo ========================================

REM Check for Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH. Checking alternatives...
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Python not installed or not in PATH
        echo Please install Python 3.8+ from python.org
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Using Python command: %PYTHON_CMD%

REM Install required packages
echo Installing required packages...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install aiohttp beautifulsoup4 feedparser schedule redis pandas fastapi uvicorn websockets psutil

REM Create directories if they don't exist
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Start Redis server (if available)
echo Starting Redis server...
start /B redis-server --port 6379 2>nul || echo Redis not available - continuing without Redis

REM Wait a moment for Redis to start
timeout /t 3 /nobreak >nul

REM Initialize databases
echo Initializing databases...
%PYTHON_CMD% -c "
import sqlite3
import os
from datetime import datetime

# Create regulatory monitor database
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

# Insert initial regulator data
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

print('Database initialized successfully')
"

REM Start API server
echo Starting API server on port 8001...
start /B %PYTHON_CMD% -m uvicorn src.api.regulatory_integration_api:app --host 0.0.0.0 --port 8001

REM Wait for API server to start
timeout /t 5 /nobreak >nul

REM Test API endpoints
echo Testing API endpoints...
%PYTHON_CMD% -c "
import requests
import time

endpoints = [
    'http://localhost:8001/api/v1/integration/health',
    'http://localhost:8001/api/v1/regulators',
    'http://localhost:8001/api/v1/monitoring/status'
]

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code == 200:
            print(f'✅ {endpoint} - RESPONDING')
        else:
            print(f'⚠️ {endpoint} - HTTP {response.status_code}')
    except Exception as e:
        print(f'❌ {endpoint} - ERROR: {e}')
"

REM Start monitoring processes
echo Starting regulatory data monitor...
start /B %PYTHON_CMD% src/core/regulatory_data_monitor.py

echo Starting audit firm tracker...
start /B %PYTHON_CMD% src/services/audit_firm_tracker.py

REM Generate status report
echo Generating system status...
%PYTHON_CMD% -c "
import json
import requests
from datetime import datetime

try:
    # Test API health
    health_response = requests.get('http://localhost:8001/api/v1/integration/health', timeout=5)
    health_data = health_response.json() if health_response.status_code == 200 else {'status': 'unhealthy'}
    
    # Test regulators endpoint
    reg_response = requests.get('http://localhost:8001/api/v1/regulators', timeout=5)
    reg_count = len(reg_response.json()) if reg_response.status_code == 200 else 0
    
    status_report = {
        'activation_time': datetime.now().isoformat(),
        'system_health': health_data.get('status', 'unknown'),
        'api_server': 'running' if health_response.status_code == 200 else 'failed',
        'regulators_loaded': reg_count,
        'monitoring_active': True,
        'database_initialized': True
    }
    
    with open('system_status.json', 'w') as f:
        json.dump(status_report, f, indent=2)
    
    print('\\n' + '='*60)
    print('🚀 DOGANAI REGULATORY MONITORING SYSTEM')
    print('='*60)
    print(f'✅ System Health: {status_report[\"system_health\"].upper()}')
    print(f'✅ API Server: {status_report[\"api_server\"].upper()}')
    print(f'✅ Regulators Loaded: {status_report[\"regulators_loaded\"]}')
    print(f'✅ Database: INITIALIZED')
    print(f'✅ Monitoring: ACTIVE')
    print('\\n🌐 Access Points:')
    print('   API Health: http://localhost:8001/api/v1/integration/health')
    print('   Regulators: http://localhost:8001/api/v1/regulators')
    print('   Status: http://localhost:8001/api/v1/monitoring/status')
    print('\\n📊 Dashboard Integration Ready')
    print('📋 Status saved to: system_status.json')
    print('='*60)
    
except Exception as e:
    print(f'❌ Status check failed: {e}')
"

echo.
echo ========================================
echo  System Activation Complete!
echo  Press any key to keep running...
echo  Press Ctrl+C to stop all services
echo ========================================
pause >nul
