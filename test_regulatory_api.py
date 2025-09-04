#!/usr/bin/env python3
"""
Test script for regulatory monitoring API endpoints
"""

import requests
import json
import sqlite3
from datetime import datetime

def test_existing_api():
    """Test existing API endpoints"""
    base_url = "http://localhost:8001"
    
    print("Testing existing DoganAI Compliance Kit API...")
    print("="*50)
    
    # Test main endpoints
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
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_type': response.headers.get('content-type', 'unknown')
            }
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK ({response.status_code})")
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if endpoint == "/":
                            print(f"   Service: {data.get('service', 'Unknown')}")
                            print(f"   Version: {data.get('version', 'Unknown')}")
                        elif endpoint == "/health":
                            print(f"   Status: {data.get('status', 'Unknown')}")
                    except:
                        pass
            else:
                print(f"⚠️ {endpoint} - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            results[endpoint] = {'error': str(e)}
            print(f"❌ {endpoint} - ERROR: {e}")
    
    return results

def check_database():
    """Check database status"""
    print("\nChecking database status...")
    print("="*30)
    
    db_files = ['regulatory_monitor.db', 'audit_firms.db']
    db_status = {}
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_status[db_file] = {
                'exists': True,
                'tables': [table[0] for table in tables],
                'table_count': len(tables)
            }
            
            print(f"✅ {db_file} - {len(tables)} tables")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   {table[0]}: {count} records")
            
            conn.close()
            
        except Exception as e:
            db_status[db_file] = {'exists': False, 'error': str(e)}
            print(f"❌ {db_file} - ERROR: {e}")
    
    return db_status

def test_regulatory_endpoints():
    """Test specific regulatory monitoring endpoints"""
    print("\nTesting regulatory-specific endpoints...")
    print("="*40)
    
    base_url = "http://localhost:8001"
    
    # Try to find regulatory endpoints
    regulatory_endpoints = [
        "/api/v1/regulators",
        "/api/v1/regulations", 
        "/api/v1/monitoring/status",
        "/api/v1/integration/health",
        "/regulatory/status",
        "/monitoring/health"
    ]
    
    found_endpoints = []
    
    for endpoint in regulatory_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - FOUND")
                found_endpoints.append(endpoint)
                
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Returns: List with {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   Returns: Dict with keys: {list(data.keys())[:5]}")
                except:
                    print(f"   Returns: Non-JSON response")
                    
            elif response.status_code == 404:
                print(f"⚪ {endpoint} - Not found")
            else:
                print(f"⚠️ {endpoint} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - ERROR: {e}")
    
    return found_endpoints

def create_regulatory_data():
    """Create sample regulatory data in database"""
    print("\nCreating sample regulatory data...")
    print("="*35)
    
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        # Create tables if they don't exist
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
        
        # Insert KSA regulators
        ksa_regulators = [
            ('sama', 'Saudi Central Bank (SAMA)', 'central_bank', 'Banking & Finance', 'https://www.sama.gov.sa', 'active'),
            ('nca', 'National Cybersecurity Authority', 'cybersecurity', 'Cybersecurity', 'https://nca.gov.sa', 'active'),
            ('citc', 'Communications & IT Commission', 'telecom_regulator', 'Telecommunications', 'https://www.citc.gov.sa', 'active'),
            ('cma', 'Capital Market Authority', 'financial_regulator', 'Capital Markets', 'https://cma.org.sa', 'active'),
            ('zatca', 'Zakat, Tax and Customs Authority', 'tax_authority', 'Tax & Customs', 'https://zatca.gov.sa', 'active'),
            ('sfda', 'Saudi Food & Drug Authority', 'health_regulator', 'Healthcare & Pharmaceuticals', 'https://www.sfda.gov.sa', 'active'),
            ('scfhs', 'Saudi Commission for Health Specialties', 'health_regulator', 'Healthcare Professionals', 'https://www.scfhs.org.sa', 'active'),
            ('moh', 'Ministry of Health', 'ministry', 'Public Health', 'https://www.moh.gov.sa', 'active'),
            ('mci', 'Ministry of Commerce & Investment', 'ministry', 'Commerce & Investment', 'https://mci.gov.sa', 'active'),
            ('mol', 'Ministry of Labor', 'ministry', 'Labor & Employment', 'https://www.mol.gov.sa', 'active')
        ]
        
        for reg_data in ksa_regulators:
            cursor.execute('''
                INSERT OR REPLACE INTO regulators 
                (id, name, type, domain, website, last_updated, status, regulations_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*reg_data, datetime.now().isoformat(), 0))
        
        # Insert sample regulations
        sample_regulations = [
            ('sama_001', 'sama', 'Banking Control Law', 'law', '2024-01-01', 'active', 'https://www.sama.gov.sa/en-US/Laws/BankingRules/Pages/default.aspx'),
            ('nca_001', 'nca', 'Cybersecurity Framework', 'framework', '2024-01-01', 'active', 'https://nca.gov.sa/pages/framework.html'),
            ('citc_001', 'citc', 'Telecommunications Act', 'act', '2024-01-01', 'active', 'https://www.citc.gov.sa/en/RulesandSystems/Pages/default.aspx'),
            ('cma_001', 'cma', 'Capital Market Law', 'law', '2024-01-01', 'active', 'https://cma.org.sa/en/RulesRegulations/Regulations/Pages/default.aspx'),
            ('zatca_001', 'zatca', 'Value Added Tax Implementing Regulations', 'regulation', '2024-01-01', 'active', 'https://zatca.gov.sa/en/RulesRegulations/Pages/default.aspx')
        ]
        
        for reg_data in sample_regulations:
            cursor.execute('''
                INSERT OR REPLACE INTO regulations 
                (id, regulator_id, title, type, effective_date, status, source_url, last_modified, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*reg_data, datetime.now().isoformat(), 'sample_hash'))
        
        # Update regulator counts
        cursor.execute('''
            UPDATE regulators SET regulations_count = (
                SELECT COUNT(*) FROM regulations WHERE regulator_id = regulators.id
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Sample regulatory data created successfully")
        print(f"   - {len(ksa_regulators)} regulators added")
        print(f"   - {len(sample_regulations)} regulations added")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create regulatory data: {e}")
        return False

def generate_test_report(api_results, db_status, regulatory_endpoints):
    """Generate comprehensive test report"""
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'api_status': api_results,
        'database_status': db_status,
        'regulatory_endpoints': regulatory_endpoints,
        'summary': {
            'api_healthy': any(result.get('status_code') == 200 for result in api_results.values() if isinstance(result, dict)),
            'database_connected': any(status.get('exists', False) for status in db_status.values()),
            'regulatory_endpoints_found': len(regulatory_endpoints)
        }
    }
    
    with open('regulatory_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("REGULATORY MONITORING SYSTEM TEST REPORT")
    print("="*60)
    print(f"Test Time: {report['test_timestamp']}")
    print(f"API Status: {'HEALTHY' if report['summary']['api_healthy'] else 'ISSUES'}")
    print(f"Database: {'CONNECTED' if report['summary']['database_connected'] else 'ISSUES'}")
    print(f"Regulatory Endpoints: {report['summary']['regulatory_endpoints_found']} found")
    print("\n📊 Detailed Report: regulatory_test_report.json")
    print("="*60)
    
    return report

def main():
    """Main test function"""
    print("DoganAI Regulatory Monitoring System - API Test")
    print("="*50)
    
    # Test existing API
    api_results = test_existing_api()
    
    # Check databases
    db_status = check_database()
    
    # Create sample data if needed
    create_regulatory_data()
    
    # Test regulatory endpoints
    regulatory_endpoints = test_regulatory_endpoints()
    
    # Generate report
    report = generate_test_report(api_results, db_status, regulatory_endpoints)
    
    return report

if __name__ == "__main__":
    main()
