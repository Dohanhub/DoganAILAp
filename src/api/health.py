
'\nHealth check utilities for DoganAI-Compliance-Kit\n'
from typing import Dict, Any
from pathlib import Path
import time
import psutil
import logging
from src.core.database import get_db_service
from src.services.compliance import get_available_mappings
from src.core.settings import settings
logger = logging.getLogger(__name__)

class HealthChecker():
    'Comprehensive health checking system'

    def __init__(self):
        self.checks = {'database': self._check_database, 'filesystem': self._check_filesystem, 'mappings': self._check_mappings, 'system': self._check_system_resources, 'configuration': self._check_configuration, 'timezone': self._check_timezone}

    def run_all_checks(self) -> Dict[(str, Any)]:
        'Run all health checks and return status'
        start_time = time.time()
        current_time = settings.get_current_time()
        results = {'timestamp': current_time.isoformat(), 'status': 'healthy', 'checks': {}, 'summary': {'total_checks': len(self.checks), 'passed': 0, 'failed': 0, 'warnings': 0}}
        for (check_name, check_func) in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
                if (check_result['status'] == 'healthy'):
                    results['summary']['passed'] += 1
                elif (check_result['status'] == 'warning'):
                    results['summary']['warnings'] += 1
                else:
                    results['summary']['failed'] += 1
                    results['status'] = 'unhealthy'
            except Exception as e:
                logger.error(f'Health check {check_name} failed: {e}')
                results['checks'][check_name] = {'status': 'error', 'message': f'Check failed: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}
                results['summary']['failed'] += 1
                results['status'] = 'unhealthy'
        if (results['summary']['failed'] > 0):
            results['status'] = 'unhealthy'
        elif (results['summary']['warnings'] > 0):
            results['status'] = 'degraded'
        results['duration_ms'] = round(((time.time() - start_time) * 1000), 2)
        return results

    def _check_timezone(self) -> Dict[(str, Any)]:
        'Check timezone configuration - NEW check to detect timezone issues'
        try:
            current_utc = settings.timezone.now_utc()
            current_local = settings.timezone.now_local()
            current_display = settings.timezone.to_display_timezone(current_utc)
            utc_offset = current_local.utcoffset()
            display_offset = current_display.utcoffset()
            status = 'healthy'
            warnings = []
            if (utc_offset and (abs(utc_offset.total_seconds()) > 18000)):
                warnings.append(f'Large timezone offset detected: {utc_offset}')
                status = 'warning'
            logger.info(f'Timezone check - UTC: {current_utc}, Local: {current_local}, Display: {current_display}, UTC Offset: {utc_offset}')
            return {'status': status, 'message': 'Timezone configuration checked', 'utc_time': current_utc.isoformat(), 'local_time': current_local.isoformat(), 'display_time': current_display.isoformat(), 'application_timezone': settings.timezone.application_timezone, 'display_timezone': settings.timezone.display_timezone, 'force_utc': settings.timezone.force_utc, 'utc_offset_seconds': (utc_offset.total_seconds() if utc_offset else 0), 'warnings': warnings, 'timestamp': settings.get_current_time().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': f'Timezone check failed: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}

    def _check_database(self) -> Dict[(str, Any)]:
        'Check database connectivity and performance'
        try:
            db_service = get_db_service()
            start_time = time.time()
            with db_service.get_session() as session:
                result = session.execute("SELECT NOW(), CURRENT_SETTING('timezone')")
                (db_time, db_timezone) = result.fetchone()
            connection_time = round(((time.time() - start_time) * 1000), 2)
            status = 'healthy'
            warnings = []
            if (connection_time > 1000):
                status = 'warning'
                warnings.append(f'Slow database connection: {connection_time}ms')
            if (db_timezone != settings.database.timezone):
                warnings.append(f'Database timezone ({db_timezone}) differs from config ({settings.database.timezone})')
                status = 'warning'
            return {'status': status, 'connection_time_ms': connection_time, 'message': 'Database connection successful', 'database_time': (db_time.isoformat() if db_time else None), 'database_timezone': db_timezone, 'configured_timezone': settings.database.timezone, 'warnings': warnings, 'timestamp': settings.get_current_time().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': f'Database connection failed: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}

    def _check_filesystem(self) -> Dict[(str, Any)]:
        'Check filesystem access and required directories'
        base_path = Path(__file__).parent.parent
        required_dirs = ['mappings', 'policies', 'vendors', 'benchmarks']
        missing_dirs = []
        accessible_dirs = []
        for dir_name in required_dirs:
            dir_path = (base_path / dir_name)
            if (not dir_path.exists()):
                missing_dirs.append(dir_name)
            elif (not dir_path.is_dir()):
                missing_dirs.append(f'{dir_name} (not a directory)')
            else:
                accessible_dirs.append(dir_name)
        if missing_dirs:
            return {'status': 'error', 'message': f"Missing directories: {', '.join(missing_dirs)}", 'accessible': accessible_dirs, 'missing': missing_dirs, 'timestamp': settings.get_current_time().isoformat()}
        return {'status': 'healthy', 'message': 'All required directories accessible', 'accessible': accessible_dirs, 'timestamp': settings.get_current_time().isoformat()}

    def _check_mappings(self) -> Dict[(str, Any)]:
        'Check mapping files availability'
        try:
            mappings = get_available_mappings()
            if (not mappings):
                return {'status': 'warning', 'message': 'No mapping files found', 'count': 0, 'timestamp': settings.get_current_time().isoformat()}
            return {'status': 'healthy', 'message': f'Found {len(mappings)} mapping files', 'count': len(mappings), 'mappings': mappings[:5], 'timestamp': settings.get_current_time().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to check mappings: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}

    def _check_system_resources(self) -> Dict[(str, Any)]:
        'Check system resource usage'
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            status = 'healthy'
            warnings = []
            if (cpu_percent > 80):
                warnings.append(f'High CPU usage: {cpu_percent}%')
                status = 'warning'
            if (memory.percent > 85):
                warnings.append(f'High memory usage: {memory.percent}%')
                status = 'warning'
            if (disk.percent > 90):
                warnings.append(f'High disk usage: {disk.percent}%')
                status = 'warning'
            return {'status': status, 'message': ('System resources checked' if (not warnings) else '; '.join(warnings)), 'cpu_percent': cpu_percent, 'memory_percent': memory.percent, 'disk_percent': disk.percent, 'warnings': warnings, 'timestamp': settings.get_current_time().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to check system resources: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}

    def _check_configuration(self) -> Dict[(str, Any)]:
        'Check configuration validity'
        try:
            validation_errors = settings.validate()
            if validation_errors:
                return {'status': 'error', 'message': f"Configuration errors: {'; '.join(validation_errors)}", 'errors': validation_errors, 'timestamp': settings.get_current_time().isoformat()}
            warnings = []
            if settings.debug:
                warnings.append('Running in debug mode')
            if (not settings.security.secret_key):
                warnings.append('SECRET_KEY not configured')
            if ((not settings.timezone.force_utc) and settings.is_production):
                warnings.append('Consider using UTC timestamps in production')
            status = ('warning' if warnings else 'healthy')
            return {'status': status, 'message': ('Configuration valid' if (not warnings) else '; '.join(warnings)), 'warnings': warnings, 'app_name': settings.app_name, 'app_version': settings.app_version, 'environment': settings.environment, 'cache_ttl': settings.cache_ttl, 'timestamp': settings.get_current_time().isoformat()}
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to check configuration: {str(e)}', 'timestamp': settings.get_current_time().isoformat()}
health_checker = HealthChecker()

def get_health_checker() -> HealthChecker:
    'Get health checker instance'
    return health_checker
