#!/usr/bin/env python3
"""
Health Check Monitoring System
Implements comprehensive health check monitoring for all services and components
"""

import sqlite3
import requests
import json
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict
import logging

class HealthCheckMonitor:
    """Comprehensive health check monitoring system"""
    
    def __init__(self):
        self.services = {
            'compliance-engine': {'url': 'http://localhost:8000', 'critical': True},
            'benchmarks': {'url': 'http://localhost:8001', 'critical': False},
            'ai-ml': {'url': 'http://localhost:8002', 'critical': False},
            'integrations': {'url': 'http://localhost:8003', 'critical': True},
            'ui': {'url': 'http://localhost:8501', 'critical': True},
            'auth': {'url': 'http://localhost:8004', 'critical': True},
            'ai-agent': {'url': 'http://localhost:8005', 'critical': False},
            'autonomous-testing': {'url': 'http://localhost:8006', 'critical': False}
        }
        self.health_history = []
        self.monitoring_active = False
        self.check_interval = 30  # seconds
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('health_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HealthMonitor')
    
    def run_comprehensive_health_check(self) -> Dict:
        """Run comprehensive health check across all components"""
        
        print("🩺 COMPREHENSIVE HEALTH CHECK")
        print("="*35)
        print(f"Health Check Time: {datetime.now().isoformat()}")
        print()
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'HEALTHY',
            'components': {}
        }
        
        # 1. System Resource Health
        print("💻 SYSTEM RESOURCES")
        print("="*20)
        system_health = self._check_system_resources()
        health_report['components']['system'] = system_health
        
        # 2. Database Health
        print("\n🗄️ DATABASE HEALTH")
        print("="*20)
        database_health = self._check_database_health()
        health_report['components']['database'] = database_health
        
        # 3. Service Health
        print("\n🌐 SERVICE HEALTH")
        print("="*18)
        service_health = self._check_all_services()
        health_report['components']['services'] = service_health
        
        # 4. File System Health
        print("\n📁 FILESYSTEM HEALTH")
        print("="*22)
        filesystem_health = self._check_filesystem_health()
        health_report['components']['filesystem'] = filesystem_health
        
        # 5. Configuration Health
        print("\n⚙️ CONFIGURATION HEALTH")
        print("="*25)
        config_health = self._check_configuration_health()
        health_report['components']['configuration'] = config_health
        
        # Determine overall status
        health_report['overall_status'] = self._calculate_overall_status(health_report['components'])
        
        # Save health report
        self._save_health_report(health_report)
        
        print("\n🎯 OVERALL HEALTH STATUS")
        print("="*30)
        print(f"   Status: {self._format_status(health_report['overall_status'])}")
        print("   Report saved: health_report.json")
        
        return health_report
    
    def _check_system_resources(self) -> Dict:
        """Check system resource health"""
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_health = {
                'status': 'HEALTHY',
                'metrics': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'available_memory_gb': round(memory.available / (1024**3), 2),
                    'available_disk_gb': round(disk.free / (1024**3), 2)
                },
                'issues': []
            }
            
            # Check thresholds
            if cpu_percent > 80:
                system_health['issues'].append(f"High CPU usage: {cpu_percent}%")
                system_health['status'] = 'WARNING'
            
            if memory.percent > 85:
                system_health['issues'].append(f"High memory usage: {memory.percent}%")
                system_health['status'] = 'WARNING'
            
            if disk.percent > 90:
                system_health['issues'].append(f"High disk usage: {disk.percent}%")
                system_health['status'] = 'CRITICAL'
            
            print(f"   CPU: {cpu_percent}% | Memory: {memory.percent}% | Disk: {disk.percent}%")
            print(f"   Status: {self._format_status(system_health['status'])}")
            
            return system_health
            
        except Exception as e:
            error_health = {
                'status': 'CRITICAL',
                'error': str(e),
                'metrics': {},
                'issues': [f"System monitoring error: {e}"]
            }
            print(f"   ❌ System monitoring error: {e}")
            return error_health
    
    def _check_database_health(self) -> Dict:
        """Check database health and connectivity"""
        
        try:
            conn = sqlite3.connect('doganai_compliance.db')
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM evaluation_results")
            eval_count = cursor.fetchone()[0]
            query_time = time.time() - start_time
            
            cursor.execute("SELECT COUNT(*) FROM policies")
            policy_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM vendors")
            vendor_count = cursor.fetchone()[0]
            
            # Check database file size
            db_path = Path('doganai_compliance.db')
            db_size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
            
            conn.close()
            
            db_health = {
                'status': 'HEALTHY',
                'metrics': {
                    'evaluation_records': eval_count,
                    'policy_records': policy_count,
                    'vendor_records': vendor_count,
                    'query_response_time': round(query_time, 3),
                    'database_size_mb': round(db_size_mb, 2)
                },
                'issues': []
            }
            
            # Check for issues
            if query_time > 5.0:
                db_health['issues'].append(f"Slow query response: {query_time:.3f}s")
                db_health['status'] = 'WARNING'
            
            if eval_count == 0:
                db_health['issues'].append("No evaluation results found")
                db_health['status'] = 'WARNING'
            
            if policy_count < 9:
                db_health['issues'].append(f"Incomplete policy data: {policy_count}/9 authorities")
                db_health['status'] = 'WARNING'
            
            print(f"   Records: {eval_count} evaluations, {policy_count} policies, {vendor_count} vendors")
            print(f"   Query time: {query_time:.3f}s | Size: {db_size_mb:.1f}MB")
            print(f"   Status: {self._format_status(db_health['status'])}")
            
            return db_health
            
        except Exception as e:
            error_health = {
                'status': 'CRITICAL',
                'error': str(e),
                'metrics': {},
                'issues': [f"Database connection error: {e}"]
            }
            print(f"   ❌ Database error: {e}")
            return error_health
    
    def _check_all_services(self) -> Dict:
        """Check health of all microservices"""
        
        service_health = {
            'status': 'HEALTHY',
            'services': {},
            'summary': {
                'total': len(self.services),
                'healthy': 0,
                'unhealthy': 0,
                'critical_down': 0
            }
        }
        
        for service_name, config in self.services.items():
            health = self._check_service_health(service_name, config)
            service_health['services'][service_name] = health
            
            if health['status'] == 'HEALTHY':
                service_health['summary']['healthy'] += 1
            else:
                service_health['summary']['unhealthy'] += 1
                if config['critical']:
                    service_health['summary']['critical_down'] += 1
        
        # Determine overall service status
        if service_health['summary']['critical_down'] > 0:
            service_health['status'] = 'CRITICAL'
        elif service_health['summary']['unhealthy'] > 0:
            service_health['status'] = 'WARNING'
        
        print(f"   Healthy: {service_health['summary']['healthy']}/{service_health['summary']['total']}")
        print(f"   Critical services down: {service_health['summary']['critical_down']}")
        print(f"   Status: {self._format_status(service_health['status'])}")
        
        return service_health
    
    def _check_service_health(self, service_name: str, config: Dict) -> Dict:
        """Check health of a single service"""
        
        try:
            start_time = time.time()
            
            # Try multiple health endpoints
            health_endpoints = ['/health', '/health/ready', '/ready', '/']
            response = None
            
            for endpoint in health_endpoints:
                try:
                    response = requests.get(f"{config['url']}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    continue
            
            response_time = time.time() - start_time
            
            if response and response.status_code == 200:
                health = {
                    'status': 'HEALTHY',
                    'url': config['url'],
                    'response_time': round(response_time, 3),
                    'critical': config['critical']
                }
                print(f"      ✅ {service_name}: {response_time:.3f}s")
            else:
                health = {
                    'status': 'UNHEALTHY',
                    'url': config['url'],
                    'error': f"HTTP {response.status_code if response else 'Connection failed'}",
                    'critical': config['critical']
                }
                status_icon = '🚨' if config['critical'] else '⚠️'
                print(f"      {status_icon} {service_name}: {health['error']}")
            
            return health
            
        except Exception as e:
            health = {
                'status': 'UNHEALTHY',
                'url': config['url'],
                'error': str(e),
                'critical': config['critical']
            }
            status_icon = '🚨' if config['critical'] else '⚠️'
            print(f"      {status_icon} {service_name}: {e}")
            return health
    
    def _check_filesystem_health(self) -> Dict:
        """Check filesystem health"""
        
        fs_health = {
            'status': 'HEALTHY',
            'checks': {},
            'issues': []
        }
        
        # Check critical directories and files
        critical_paths = [
            {'path': 'policies/', 'type': 'directory', 'required': True},
            {'path': 'doganai_compliance.db', 'type': 'file', 'required': True},
            {'path': 'engine/', 'type': 'directory', 'required': True},
            {'path': 'ui/', 'type': 'directory', 'required': True},
            {'path': 'microservices/', 'type': 'directory', 'required': False}
        ]
        
        for item in critical_paths:
            path = Path(item['path'])
            exists = path.exists()
            
            if item['type'] == 'directory':
                is_valid = exists and path.is_dir()
            else:
                is_valid = exists and path.is_file()
            
            fs_health['checks'][item['path']] = {
                'exists': exists,
                'valid': is_valid,
                'required': item['required']
            }
            
            if item['required'] and not is_valid:
                fs_health['issues'].append(f"Missing required {item['type']}: {item['path']}")
                fs_health['status'] = 'CRITICAL'
            
            status = '✅' if is_valid else ('❌' if item['required'] else '⚠️')
            print(f"      {status} {item['path']}")
        
        print(f"   Status: {self._format_status(fs_health['status'])}")
        return fs_health
    
    def _check_configuration_health(self) -> Dict:
        """Check configuration health"""
        
        config_health = {
            'status': 'HEALTHY',
            'configs': {},
            'issues': []
        }
        
        # Check configuration files
        config_files = [
            'requirements.txt',
            'docker-compose.yml',
            'microservices/docker-compose.yml'
        ]
        
        for config_file in config_files:
            path = Path(config_file)
            exists = path.exists()
            
            config_health['configs'][config_file] = {
                'exists': exists,
                'size': path.stat().st_size if exists else 0
            }
            
            if not exists and config_file in ['requirements.txt']:
                config_health['issues'].append(f"Missing configuration: {config_file}")
                config_health['status'] = 'WARNING'
            
            status = '✅' if exists else '⚠️'
            print(f"      {status} {config_file}")
        
        # Check policy files completeness
        policies_dir = Path('policies')
        if policies_dir.exists():
            policy_files = list(policies_dir.glob('*.yaml'))
            expected_policies = 9  # 9 regulatory authorities
            
            config_health['configs']['policy_files'] = {
                'count': len(policy_files),
                'expected': expected_policies,
                'complete': len(policy_files) >= expected_policies
            }
            
            if len(policy_files) < expected_policies:
                config_health['issues'].append(f"Incomplete policies: {len(policy_files)}/{expected_policies}")
                config_health['status'] = 'WARNING'
            
            print(f"      {'✅' if len(policy_files) >= expected_policies else '⚠️'} Policy files: {len(policy_files)}/{expected_policies}")
        
        print(f"   Status: {self._format_status(config_health['status'])}")
        return config_health
    
    def _calculate_overall_status(self, components: Dict) -> str:
        """Calculate overall system health status"""
        
        statuses = [comp.get('status', 'UNKNOWN') for comp in components.values()]
        
        if 'CRITICAL' in statuses:
            return 'CRITICAL'
        elif 'WARNING' in statuses:
            return 'WARNING'
        else:
            return 'HEALTHY'
    
    def _format_status(self, status: str) -> str:
        """Format status with appropriate emoji"""
        
        status_map = {
            'HEALTHY': '✅ HEALTHY',
            'WARNING': '⚠️ WARNING', 
            'CRITICAL': '🚨 CRITICAL',
            'UNKNOWN': '❓ UNKNOWN'
        }
        return status_map.get(status, status)
    
    def _save_health_report(self, report: Dict):
        """Save health report to file"""
        
        with open('health_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also append to health history
        self.health_history.append(report)
        
        # Keep only last 100 reports
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    def start_continuous_monitoring(self, interval_seconds: int = 30):
        """Start continuous health monitoring"""
        
        self.check_interval = interval_seconds
        self.monitoring_active = True
        
        print(f"🔄 Starting continuous health monitoring (every {interval_seconds}s)")
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.logger.info("Running scheduled health check")
                    health_report = self.run_comprehensive_health_check()
                    
                    # Log any critical issues
                    if health_report['overall_status'] == 'CRITICAL':
                        self.logger.critical("CRITICAL system health detected")
                    elif health_report['overall_status'] == 'WARNING':
                        self.logger.warning("WARNING system health detected")
                    
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Health monitoring error: {e}")
                    time.sleep(self.check_interval)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        
        self.monitoring_active = False
        print("🛑 Stopping health monitoring")

def main():
    """Main health monitoring function"""
    
    monitor = HealthCheckMonitor()
    health_report = monitor.run_comprehensive_health_check()
    
    # Optionally start continuous monitoring
    # monitor.start_continuous_monitoring(60)  # Every 60 seconds
    
    return health_report['overall_status'] == 'HEALTHY'

if __name__ == "__main__":
    main()
