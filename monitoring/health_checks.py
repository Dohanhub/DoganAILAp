#!/usr/bin/env python3
"""
Enhanced Health Check System for DoganAI Compliance Kit
Implements comprehensive health checks for all system components
"""

import asyncio
import aiohttp
import sqlite3
import redis
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Health check result data structure"""
    component: str
    status: str  # 'healthy', 'unhealthy', 'degraded'
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime
    critical: bool = False

class HealthChecker:
    """Comprehensive health check system"""
    
    def __init__(self):
        self.services = {
            'compliance-engine': {
                'url': 'http://localhost:8000',
                'critical': True,
                'endpoints': ['/health', '/health/ready']
            },
            'database': {
                'type': 'sqlite',
                'path': 'doganai_compliance.db',
                'critical': True
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'critical': False
            },
            'api-server': {
                'url': 'http://localhost:8000',
                'critical': True,
                'endpoints': ['/health', '/api/health']
            },
            'ui-service': {
                'url': 'http://localhost:8501',
                'critical': False,
                'endpoints': ['/health', '/']
            }
        }
        
        self.health_history = []
        self.max_history_size = 100
    
    async def check_service_health(self, service_name: str, config: Dict) -> HealthCheckResult:
        """Check health of a specific service"""
        start_time = time.time()
        
        try:
            if 'url' in config:
                # HTTP service check
                result = await self._check_http_service(service_name, config)
            elif config.get('type') == 'sqlite':
                # Database check
                result = await self._check_database(service_name, config)
            elif 'host' in config and 'port' in config:
                # Redis check
                result = await self._check_redis(service_name, config)
            else:
                result = HealthCheckResult(
                    component=service_name,
                    status='unhealthy',
                    response_time=0.0,
                    details={'error': 'Unknown service type'},
                    timestamp=datetime.now(timezone.utc),
                    critical=config.get('critical', False)
                )
            
            result.response_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return HealthCheckResult(
                component=service_name,
                status='unhealthy',
                response_time=time.time() - start_time,
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc),
                critical=config.get('critical', False)
            )
    
    async def _check_http_service(self, service_name: str, config: Dict) -> HealthCheckResult:
        """Check HTTP service health"""
        url = config['url']
        endpoints = config.get('endpoints', ['/health'])
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return HealthCheckResult(
                                component=service_name,
                                status='healthy',
                                response_time=0.0,
                                details={
                                    'url': f"{url}{endpoint}",
                                    'status_code': response.status,
                                    'response': data
                                },
                                timestamp=datetime.now(timezone.utc),
                                critical=config.get('critical', False)
                            )
            except Exception as e:
                logger.warning(f"Failed to check {url}{endpoint}: {e}")
                continue
        
        return HealthCheckResult(
            component=service_name,
            status='unhealthy',
            response_time=0.0,
            details={'error': 'All endpoints failed'},
            timestamp=datetime.now(timezone.utc),
            critical=config.get('critical', False)
        )
    
    async def _check_database(self, service_name: str, config: Dict) -> HealthCheckResult:
        """Check database health"""
        try:
            db_path = config['path']
            
            # Check if database file exists
            import os
            if not os.path.exists(db_path):
                return HealthCheckResult(
                    component=service_name,
                    status='unhealthy',
                    response_time=0.0,
                    details={'error': f'Database file not found: {db_path}'},
                    timestamp=datetime.now(timezone.utc),
                    critical=config.get('critical', False)
                )
            
            # Test database connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            # Check database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            # Check database version
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            
            conn.close()
            
            return HealthCheckResult(
                component=service_name,
                status='healthy',
                response_time=0.0,
                details={
                    'path': db_path,
                    'integrity': integrity_result[0] if integrity_result else 'unknown',
                    'page_count': page_count,
                    'version': version,
                    'file_size': os.path.getsize(db_path)
                },
                timestamp=datetime.now(timezone.utc),
                critical=config.get('critical', False)
            )
            
        except Exception as e:
            return HealthCheckResult(
                component=service_name,
                status='unhealthy',
                response_time=0.0,
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc),
                critical=config.get('critical', False)
            )
    
    async def _check_redis(self, service_name: str, config: Dict) -> HealthCheckResult:
        """Check Redis health"""
        try:
            r = redis.Redis(
                host=config['host'],
                port=config['port'],
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            r.ping()
            
            # Get Redis info
            info = r.info()
            
            return HealthCheckResult(
                component=service_name,
                status='healthy',
                response_time=0.0,
                details={
                    'host': config['host'],
                    'port': config['port'],
                    'version': info.get('redis_version', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory', 0),
                    'uptime': info.get('uptime_in_seconds', 0)
                },
                timestamp=datetime.now(timezone.utc),
                critical=config.get('critical', False)
            )
            
        except Exception as e:
            return HealthCheckResult(
                component=service_name,
                status='unhealthy',
                response_time=0.0,
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc),
                critical=config.get('critical', False)
            )
    
    async def check_system_health(self) -> HealthCheckResult:
        """Check overall system health"""
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine system status
            status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = 'degraded'
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = 'unhealthy'
            
            return HealthCheckResult(
                component='system',
                status=status,
                response_time=time.time() - start_time,
                details={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available,
                    'disk_percent': disk.percent,
                    'disk_free': disk.free,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                timestamp=datetime.now(timezone.utc),
                critical=True
            )
            
        except Exception as e:
            return HealthCheckResult(
                component='system',
                status='unhealthy',
                response_time=time.time() - start_time,
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc),
                critical=True
            )
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        start_time = time.time()
        results = []
        
        # Check all services
        for service_name, config in self.services.items():
            result = await self.check_service_health(service_name, config)
            results.append(result)
        
        # Check system health
        system_result = await self.check_system_health()
        results.append(system_result)
        
        # Determine overall status
        critical_services = [r for r in results if r.critical]
        unhealthy_critical = [r for r in critical_services if r.status == 'unhealthy']
        
        if unhealthy_critical:
            overall_status = 'unhealthy'
        elif any(r.status == 'degraded' for r in results):
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        # Store in history
        self.health_history.append({
            'timestamp': datetime.now(timezone.utc),
            'status': overall_status,
            'results': results
        })
        
        # Trim history
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
        
        return {
            'status': overall_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'response_time': time.time() - start_time,
            'checks': {
                result.component: {
                    'status': result.status,
                    'response_time': result.response_time,
                    'details': result.details,
                    'critical': result.critical
                }
                for result in results
            },
            'summary': {
                'total_checks': len(results),
                'healthy': len([r for r in results if r.status == 'healthy']),
                'degraded': len([r for r in results if r.status == 'degraded']),
                'unhealthy': len([r for r in results if r.status == 'unhealthy']),
                'critical_unhealthy': len(unhealthy_critical)
            }
        }
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get health check history"""
        return self.health_history[-limit:] if self.health_history else []
    
    def get_component_status(self, component: str) -> Optional[HealthCheckResult]:
        """Get status of a specific component"""
        if not self.health_history:
            return None
        
        latest = self.health_history[-1]
        for result in latest['results']:
            if result.component == component:
                return result
        return None

# Global health checker instance
health_checker = HealthChecker()

def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    return health_checker
