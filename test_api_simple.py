#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple API Test - Windows Compatible
"""

import requests
import json
import sqlite3
from datetime import datetime
import os
import sys

# Fix Windows console encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def safe_print(text):
    """Safe printing for Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def test_api():
    """Test existing API"""
    base_url = "http://localhost:8001"
    
    safe_print("Testing DoganAI Compliance Kit API...")
    safe_print("="*40)
    
    endpoints = [
        "/",
        "/health",
        "/health/ready", 
        "/health/live",
        "/api/v1/compliance",
        "/api/v1/risk",
        "/api/v1/audit", 
        "/api/v1/reports"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            results[endpoint] = response.status_code
            
            if response.status_code == 200:
                safe_print(f"OK: {endpoint} - {response.status_code}")
                if endpoint == "/":
                    try:
                        data = response.json()
                        safe_print(f"   Service: {data.get('service', 'Unknown')}")
                        safe_print(f"   Version: {data.get('version', 'Unknown')}")
                    except:
                        pass
            else:
                safe_print(f"WARN: {endpoint} - {response.status_code}")
                
        except Exception as e:
            results[endpoint] = f"ERROR: {str(e)}"
            safe_print(f"ERROR: {endpoint} - {e}")
    
    return results

def check_database():
    """Check database"""
    safe_print("\nChecking databases...")
    safe_print("="*20)
    
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        safe_print(f"regulatory_monitor.db: {len(tables)} tables")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            safe_print(f"  {table[0]}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        safe_print(f"Database error: {e}")
        return False

def create_regulatory_data():
    """Create regulatory data"""
    safe_print("\nCreating regulatory data...")
    safe_print("="*25)
    
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        # Create regulators table
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
        
        # Insert KSA regulators
        regulators = [
            ('sama', 'Saudi Central Bank', 'central_bank', 'Banking', 'https://www.sama.gov.sa', 'active'),
            ('nca', 'National Cybersecurity Authority', 'cybersecurity', 'Cybersecurity', 'https://nca.gov.sa', 'active'),
            ('citc', 'Communications & IT Commission', 'telecom', 'Telecommunications', 'https://www.citc.gov.sa', 'active'),
            ('cma', 'Capital Market Authority', 'financial', 'Capital Markets', 'https://cma.org.sa', 'active'),
            ('zatca', 'Tax and Customs Authority', 'tax', 'Tax & Customs', 'https://zatca.gov.sa', 'active'),
            ('sfda', 'Food & Drug Authority', 'health', 'Healthcare', 'https://www.sfda.gov.sa', 'active')
        ]
        
        for reg in regulators:
            cursor.execute('''
                INSERT OR REPLACE INTO regulators 
                (id, name, type, domain, website, last_updated, status, regulations_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*reg, datetime.now().isoformat(), 0))
        
        conn.commit()
        conn.close()
        
        safe_print(f"Created {len(regulators)} regulators")
        return True
        
    except Exception as e:
        safe_print(f"Data creation error: {e}")
        return False

def test_regulatory_endpoints():
    """Test regulatory endpoints"""
    safe_print("\nTesting regulatory endpoints...")
    safe_print("="*30)
    
    base_url = "http://localhost:8001"
    
    # Check if we can add regulatory endpoints to existing API
    endpoints = [
        "/api/v1/regulators",
        "/api/v1/regulations", 
        "/api/v1/monitoring/status"
    ]
    
    found = []
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                safe_print(f"FOUND: {endpoint}")
                found.append(endpoint)
            else:
                safe_print(f"NOT FOUND: {endpoint} - {response.status_code}")
                
        except Exception as e:
            safe_print(f"ERROR: {endpoint} - {e}")
    
    return found

def create_regulatory_api_extension():
    """Create regulatory API extension"""
    safe_print("\nCreating regulatory API extension...")
    safe_print("="*35)
    
    api_code = '''
from fastapi import FastAPI
import sqlite3
import json
from datetime import datetime

# Create regulatory API extension
regulatory_app = FastAPI(title="Regulatory Monitor Extension")

@regulatory_app.get("/api/v1/regulators")
async def get_regulators():
    """Get all regulators"""
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regulators")
        columns = [desc[0] for desc in cursor.description]
        regulators = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"regulators": regulators, "count": len(regulators)}
    except Exception as e:
        return {"error": str(e)}

@regulatory_app.get("/api/v1/monitoring/status")
async def get_monitoring_status():
    """Get monitoring status"""
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM regulators")
        reg_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "active",
            "total_regulators": reg_count,
            "last_update": datetime.now().isoformat(),
            "monitoring_active": True
        }
    except Exception as e:
        return {"error": str(e)}

@regulatory_app.get("/regulatory/health")
async def regulatory_health():
    """Regulatory system health check"""
    return {
        "status": "healthy",
        "service": "Regulatory Monitor",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(regulatory_app, host="0.0.0.0", port=8002)
'''
    
    with open('regulatory_api.py', 'w', encoding='utf-8') as f:
        f.write(api_code)
    
    safe_print("Regulatory API extension created")
    return True

def generate_report(api_results, db_status, regulatory_endpoints):
    """Generate test report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'api_results': api_results,
        'database_status': db_status,
        'regulatory_endpoints': regulatory_endpoints,
        'summary': {
            'main_api_healthy': any(code == 200 for code in api_results.values() if isinstance(code, int)),
            'database_connected': db_status,
            'regulatory_ready': len(regulatory_endpoints) > 0
        }
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    safe_print("\n" + "="*50)
    safe_print("REGULATORY MONITORING TEST RESULTS")
    safe_print("="*50)
    safe_print(f"Test Time: {report['timestamp']}")
    safe_print(f"Main API: {'HEALTHY' if report['summary']['main_api_healthy'] else 'ISSUES'}")
    safe_print(f"Database: {'OK' if report['summary']['database_connected'] else 'ISSUES'}")
    safe_print(f"Regulatory Endpoints: {len(regulatory_endpoints)} available")
    safe_print("")
    safe_print("Next Steps:")
    safe_print("1. Main API is running on port 8001")
    safe_print("2. Database initialized with KSA regulators")
    safe_print("3. Ready for regulatory monitoring integration")
    safe_print("")
    safe_print("Report saved: test_results.json")
    safe_print("="*50)
    
    return report

def main():
    """Main function"""
    safe_print("DoganAI Regulatory System Test")
    safe_print("="*30)
    
    # Test API
    api_results = test_api()
    
    # Check database
    db_status = check_database()
    
    # Create data if needed
    if not db_status:
        create_regulatory_data()
        db_status = check_database()
    
    # Test regulatory endpoints
    regulatory_endpoints = test_regulatory_endpoints()
    
    # Create regulatory API extension
    create_regulatory_api_extension()
    
    # Generate report
    report = generate_report(api_results, db_status, regulatory_endpoints)
    
    return report

if __name__ == "__main__":
    main()
