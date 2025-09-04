#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Status Checker - Real System Status Only
No documentation, no expectations - only actual running reality
"""

import requests
import sqlite3
import json
import subprocess
import psutil
import socket
from datetime import datetime
import os
import sys

# Fix Windows console
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def check_running_processes():
    """Check what's actually running"""
    safe_print("ACTUAL RUNNING PROCESSES:")
    safe_print("-" * 30)
    
    python_processes = []
    api_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(keyword in cmdline.lower() for keyword in ['api', 'server', 'uvicorn', 'fastapi']):
                    api_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
                python_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    safe_print(f"Python processes running: {len(python_processes)}")
    for proc in python_processes:
        safe_print(f"  PID {proc['pid']}: {proc['cmdline'][:100]}...")
    
    safe_print(f"API/Server processes: {len(api_processes)}")
    for proc in api_processes:
        safe_print(f"  PID {proc['pid']}: {proc['cmdline'][:100]}...")
    
    return python_processes, api_processes

def check_open_ports():
    """Check what ports are actually open"""
    safe_print("\nACTUAL OPEN PORTS:")
    safe_print("-" * 20)
    
    open_ports = []
    test_ports = [8000, 8001, 8002, 8003, 3000, 5000, 9000]
    
    for port in test_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            open_ports.append(port)
            safe_print(f"  Port {port}: OPEN")
        sock.close()
    
    return open_ports

def test_live_endpoints():
    """Test what endpoints actually respond"""
    safe_print("\nACTUAL RESPONDING ENDPOINTS:")
    safe_print("-" * 30)
    
    responding = {}
    
    # Test discovered ports
    open_ports = check_open_ports()
    
    for port in open_ports:
        base_url = f"http://localhost:{port}"
        
        # Test common endpoints
        endpoints = [
            "/",
            "/health",
            "/api/v1/regulators",
            "/api/v1/compliance",
            "/docs"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=3)
                
                if response.status_code == 200:
                    responding[url] = {
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'response_size': len(response.content)
                    }
                    safe_print(f"  {url} -> {response.status_code}")
                    
                    # Try to get JSON data
                    try:
                        if 'application/json' in response.headers.get('content-type', ''):
                            data = response.json()
                            if isinstance(data, dict):
                                keys = list(data.keys())[:5]
                                safe_print(f"    JSON keys: {keys}")
                    except:
                        pass
                        
            except Exception as e:
                pass
    
    return responding

def check_database_reality():
    """Check actual database contents"""
    safe_print("\nACTUAL DATABASE STATUS:")
    safe_print("-" * 25)
    
    db_status = {}
    
    # Check for database files
    db_files = ['regulatory_monitor.db', 'audit_firms.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Get actual tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                db_status[db_file] = {'tables': {}}
                
                safe_print(f"{db_file}:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    db_status[db_file]['tables'][table] = count
                    safe_print(f"  {table}: {count} records")
                    
                    # Show sample data
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        safe_print(f"    Columns: {columns[:5]}")
                        for row in rows:
                            safe_print(f"    Sample: {row[:3]}...")
                
                conn.close()
                
            except Exception as e:
                db_status[db_file] = {'error': str(e)}
                safe_print(f"{db_file}: ERROR - {e}")
        else:
            safe_print(f"{db_file}: NOT FOUND")
    
    return db_status

def test_regulator_connectivity():
    """Test actual connectivity to KSA regulators"""
    safe_print("\nACTUAL REGULATOR CONNECTIVITY:")
    safe_print("-" * 35)
    
    # Real KSA regulator websites
    regulators = {
        'SAMA': 'https://www.sama.gov.sa',
        'NCA': 'https://nca.gov.sa',
        'CITC': 'https://www.citc.gov.sa',
        'CMA': 'https://cma.org.sa',
        'ZATCA': 'https://zatca.gov.sa',
        'SFDA': 'https://www.sfda.gov.sa'
    }
    
    connectivity = {}
    
    for name, url in regulators.items():
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            connectivity[name] = {
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'response_time': response.elapsed.total_seconds(),
                'final_url': response.url
            }
            
            status = "ACCESSIBLE" if response.status_code == 200 else f"HTTP {response.status_code}"
            safe_print(f"{name}: {status} ({response.elapsed.total_seconds():.2f}s)")
            
        except Exception as e:
            connectivity[name] = {'error': str(e), 'accessible': False}
            safe_print(f"{name}: ERROR - {e}")
    
    return connectivity

def get_system_resources():
    """Get actual system resource usage"""
    safe_print("\nACTUAL SYSTEM RESOURCES:")
    safe_print("-" * 25)
    
    resources = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('.').percent,
        'network_connections': len(psutil.net_connections())
    }
    
    safe_print(f"CPU Usage: {resources['cpu_percent']:.1f}%")
    safe_print(f"Memory Usage: {resources['memory_percent']:.1f}%")
    safe_print(f"Disk Usage: {resources['disk_usage']:.1f}%")
    safe_print(f"Network Connections: {resources['network_connections']}")
    
    return resources

def generate_reality_report():
    """Generate report based only on actual findings"""
    safe_print("\n" + "="*60)
    safe_print("LIVE SYSTEM STATUS REPORT - REALITY ONLY")
    safe_print("="*60)
    safe_print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Collect all actual data
    python_procs, api_procs = check_running_processes()
    open_ports = check_open_ports()
    responding_endpoints = test_live_endpoints()
    db_status = check_database_reality()
    regulator_connectivity = test_regulator_connectivity()
    system_resources = get_system_resources()
    
    # Create reality report
    reality_report = {
        'timestamp': datetime.now().isoformat(),
        'system_reality': {
            'python_processes_running': len(python_procs),
            'api_processes_running': len(api_procs),
            'open_ports': open_ports,
            'responding_endpoints': list(responding_endpoints.keys()),
            'databases_found': list(db_status.keys()),
            'accessible_regulators': [name for name, data in regulator_connectivity.items() if data.get('accessible', False)],
            'system_resources': system_resources
        },
        'detailed_findings': {
            'processes': {'python': python_procs, 'api': api_procs},
            'endpoints': responding_endpoints,
            'databases': db_status,
            'regulators': regulator_connectivity,
            'resources': system_resources
        }
    }
    
    # Save reality report
    with open('live_system_reality.json', 'w') as f:
        json.dump(reality_report, f, indent=2)
    
    # Summary
    safe_print("\nREALITY SUMMARY:")
    safe_print(f"- {len(python_procs)} Python processes running")
    safe_print(f"- {len(api_procs)} API/server processes active")
    safe_print(f"- {len(open_ports)} ports open: {open_ports}")
    safe_print(f"- {len(responding_endpoints)} endpoints responding")
    safe_print(f"- {len([name for name, data in regulator_connectivity.items() if data.get('accessible', False)])} regulators accessible")
    safe_print(f"- System load: CPU {system_resources['cpu_percent']:.1f}%, RAM {system_resources['memory_percent']:.1f}%")
    
    safe_print(f"\nFull reality report: live_system_reality.json")
    safe_print("="*60)
    
    return reality_report

def main():
    """Main reality check"""
    safe_print("LIVE SYSTEM REALITY CHECK")
    safe_print("="*25)
    safe_print("Checking actual running systems only...")
    
    report = generate_reality_report()
    return report

if __name__ == "__main__":
    main()
