
#!/usr/bin/env python3
"""
Health Monitoring System
Comprehensive health checks for 99.99% uptime
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, Any

class HealthMonitor:
    def __init__(self):
        self.health_checks = {}
        self.system_health = {
            'database': True,
            'cache': True,
            'shards': {},
            'overall': True
        }
    
    def register_health_check(self, name: str, check_function):
        """Register a health check function"""
        self.health_checks[name] = check_function
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        
        for name, check_function in self.health_checks.items():
            try:
                start_time = time.time()
                result = check_function()
                check_time = (time.time() - start_time) * 1000
                
                results[name] = {
                    'status': result,
                    'response_time_ms': check_time,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                results[name] = {
                    'status': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous health monitoring"""
        def monitor():
            while True:
                try:
                    results = self.run_health_checks()
                    
                    # Update system health
                    self.system_health['database'] = results.get('database', {}).get('status', False)
                    self.system_health['cache'] = results.get('cache', {}).get('status', False)
                    
                    # Calculate overall health
                    healthy_checks = sum(1 for result in results.values() if result.get('status', False))
                    total_checks = len(results)
                    uptime = (healthy_checks / total_checks) * 100 if total_checks > 0 else 100
                    
                    self.system_health['overall'] = uptime >= 95.0
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Health monitoring error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

# Global health monitor instance
health_monitor = HealthMonitor()
        