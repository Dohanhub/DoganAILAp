"""
Enhanced monitoring and metrics for DoganAI-Compliance-Kit
"""
from typing import Dict, List, Any, Optional
import time
import psutil
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Create custom registry for better control
custom_registry = CollectorRegistry()

# Enhanced Prometheus metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code', 'client_ip'],
    registry=custom_registry
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=custom_registry
)

COMPLIANCE_EVALUATIONS = Counter(
    'compliance_evaluations_total',
    'Total compliance evaluations',
    ['mapping_name', 'policy', 'status'],
    registry=custom_registry
)

EVALUATION_DURATION = Histogram(
    'compliance_evaluation_duration_seconds',
    'Compliance evaluation duration in seconds',
    ['mapping_name', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
    registry=custom_registry
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result'],
    registry=custom_registry
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table', 'result'],
    registry=custom_registry
)

ERROR_COUNT = Counter(
    'application_errors_total',
    'Total application errors',
    ['component', 'error_type', 'severity'],
    registry=custom_registry
)

# System metrics
SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=custom_registry
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage',
    registry=custom_registry
)

SYSTEM_DISK_USAGE = Gauge(
    'system_disk_usage_percent',
    'System disk usage percentage',
    registry=custom_registry
)

APPLICATION_INFO = Info(
    'application_info',
    'Application information',
    registry=custom_registry
)

# Active connections and sessions
ACTIVE_CONNECTIONS = Gauge(
    'active_database_connections',
    'Number of active database connections',
    registry=custom_registry
)

ACTIVE_SESSIONS = Gauge(
    'active_user_sessions',
    'Number of active user sessions',
    registry=custom_registry
)

@dataclass
class PerformanceMetric:
    """Container for performance metric data"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Centralized metrics collection and reporting"""
    
    def __init__(self):
        self._metrics_buffer = []
        self._lock = threading.Lock()
        self._collection_interval = 60  # seconds
        self._last_collection = datetime.now(timezone.utc)
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        with self._lock:
            self._metrics_buffer.append(metric)
            
            # Auto-flush if buffer is getting large
            if len(self._metrics_buffer) > 1000:
                self._flush_metrics()
    
    def _flush_metrics(self):
        """Flush metrics buffer (internal use)"""
        # In a real implementation, this would send metrics to a time-series database
        logger.debug(f"Flushing {len(self._metrics_buffer)} metrics")
        self._metrics_buffer.clear()
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            SYSTEM_DISK_USAGE.set(disk.percent)
            
            # Record in buffer with proper timestamps
            self.record_metric(PerformanceMetric("cpu_usage", cpu_percent, "percent", current_time))
            self.record_metric(PerformanceMetric("memory_usage", memory.percent, "percent", current_time))
            self.record_metric(PerformanceMetric("disk_usage", disk.percent, "percent", current_time))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            ERROR_COUNT.labels(component="metrics", error_type="collection", severity="warning").inc()

# Global metrics collector
metrics_collector = MetricsCollector()

def track_performance(operation_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_tags = tags or {}
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metric with proper timestamp
                metric = PerformanceMetric(
                    name=f"{operation_name}_duration",
                    value=duration,
                    unit="seconds",
                    timestamp=datetime.now(timezone.utc),
                    tags={**operation_tags, "status": "success"}
                )
                metrics_collector.record_metric(metric)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metric with proper timestamp
                metric = PerformanceMetric(
                    name=f"{operation_name}_duration",
                    value=duration,
                    unit="seconds",
                    timestamp=datetime.now(timezone.utc),
                    tags={**operation_tags, "status": "error", "error_type": type(e).__name__}
                )
                metrics_collector.record_metric(metric)
                
                ERROR_COUNT.labels(
                    component=operation_name,
                    error_type=type(e).__name__,
                    severity="error"
                ).inc()
                
                raise
        
        return wrapper
    return decorator

@contextmanager
def track_operation_time(operation_name: str, labels: Optional[Dict[str, str]] = None):
    """Context manager to track operation time"""
    start_time = time.time()
    operation_labels = labels or {}
    
    try:
        yield
        duration = time.time() - start_time
        
        # Record success with proper timestamp
        metric = PerformanceMetric(
            name=f"{operation_name}_duration",
            value=duration,
            unit="seconds",
            timestamp=datetime.now(timezone.utc),
            tags={**operation_labels, "status": "success"}
        )
        metrics_collector.record_metric(metric)
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Record error with proper timestamp
        metric = PerformanceMetric(
            name=f"{operation_name}_duration",
            value=duration,
            unit="seconds",
            timestamp=datetime.now(timezone.utc),
            tags={**operation_labels, "status": "error", "error_type": type(e).__name__}
        )
        metrics_collector.record_metric(metric)
        
        ERROR_COUNT.labels(
            component=operation_name,
            error_type=type(e).__name__,
            severity="error"
        ).inc()
        
        raise

class HealthMonitor:
    """Advanced health monitoring system"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_results = {}
        self._lock = threading.Lock()
    
    def register_check(self, name: str, check_func, interval_seconds: int = 60):
        """Register a health check function"""
        with self._lock:
            self.checks[name] = {
                'function': check_func,
                'interval': interval_seconds,
                'last_run': None,
                'enabled': True
            }
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        if name not in self.checks:
            return {"status": "error", "message": f"Check '{name}' not found"}
        
        check_config = self.checks[name]
        
        try:
            start_time = time.time()
            result = check_config['function']()
            duration = time.time() - start_time
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"status": "error", "message": "Check returned invalid result"}
            
            current_time = datetime.now(timezone.utc)
            result.setdefault("timestamp", current_time.isoformat())
            result.setdefault("duration_ms", round(duration * 1000, 2))
            result.setdefault("check_name", name)
            
            # Update tracking
            with self._lock:
                self.checks[name]['last_run'] = current_time
                self.last_check_results[name] = result
            
            return result
            
        except Exception as e:
            current_time = datetime.now(timezone.utc)
            error_result = {
                "status": "error",
                "message": f"Check failed: {str(e)}",
                "timestamp": current_time.isoformat(),
                "check_name": name,
                "error_type": type(e).__name__
            }
            
            with self._lock:
                self.last_check_results[name] = error_result
            
            ERROR_COUNT.labels(
                component="health_check",
                error_type=type(e).__name__,
                severity="error"
            ).inc()
            
            return error_result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        overall_start = time.time()
        current_time = datetime.now(timezone.utc)
        results = {"checks": {}, "summary": {}}
        
        # Run individual checks
        for check_name in self.checks:
            if self.checks[check_name]['enabled']:
                results["checks"][check_name] = self.run_check(check_name)
        
        # Calculate summary
        total_checks = len(results["checks"])
        healthy_checks = sum(1 for r in results["checks"].values() if r.get("status") == "healthy")
        warning_checks = sum(1 for r in results["checks"].values() if r.get("status") == "warning")
        error_checks = sum(1 for r in results["checks"].values() if r.get("status") == "error")
        
        # Overall status logic
        if error_checks > 0:
            overall_status = "unhealthy"
        elif warning_checks > 0:
            overall_status = "degraded"
        elif healthy_checks > 0:
            overall_status = "healthy"
        else:
            overall_status = "unknown"
        
        results["summary"] = {
            "status": overall_status,
            "total_checks": total_checks,
            "healthy": healthy_checks,
            "warning": warning_checks,
            "error": error_checks,
            "duration_ms": round((time.time() - overall_start) * 1000, 2),
            "timestamp": current_time.isoformat()
        }
        
        return results
    
    def get_check_history(self, name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical check results (placeholder for real implementation)"""
        # In a real implementation, this would query a time-series database
        return []

# Global health monitor
health_monitor = HealthMonitor()

def setup_application_info(app_name: str, version: str, environment: str):
    """Setup application information metrics"""
    start_time = datetime.now(timezone.utc)
    APPLICATION_INFO.info({
        'name': app_name,
        'version': version,
        'environment': environment,
        'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        'start_time': start_time.isoformat()
    })

# Metric recording helpers
def record_api_request(method: str, endpoint: str, status_code: int, 
                      duration: float, client_ip: str = "unknown"):
    """Record API request metrics"""
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code),
        client_ip=client_ip
    ).inc()
    
    REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).observe(duration)

def record_compliance_evaluation(mapping_name: str, policy: str, status: str, duration: float):
    """Record compliance evaluation metrics"""
    COMPLIANCE_EVALUATIONS.labels(
        mapping_name=mapping_name,
        policy=policy,
        status=status
    ).inc()
    
    EVALUATION_DURATION.labels(
        mapping_name=mapping_name,
        status=status
    ).observe(duration)

def record_cache_operation(operation: str, result: str):
    """Record cache operation metrics"""
    CACHE_OPERATIONS.labels(operation=operation, result=result).inc()

def record_database_operation(operation: str, table: str, result: str):
    """Record database operation metrics"""
    DATABASE_OPERATIONS.labels(operation=operation, table=table, result=result).inc()

def record_error(component: str, error_type: str, severity: str = "error"):
    """Record error metrics"""
    ERROR_COUNT.labels(component=component, error_type=error_type, severity=severity).inc()

def get_metrics_registry():
    """Get the custom metrics registry"""
    return custom_registry

# Background metrics collection
class MetricsBackgroundCollector:
    """Background thread for collecting system metrics"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
        self.thread = None
        self.last_collection = datetime.now(timezone.utc)
    
    def start(self):
        """Start background metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started background metrics collection (interval: {self.interval}s)")
    
    def stop(self):
        """Stop background metrics collection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Stopped background metrics collection")
    
    def _collect_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                metrics_collector.collect_system_metrics()
                self.last_collection = datetime.now(timezone.utc)
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(min(self.interval, 30))  # Shorter sleep on error

# Global background collector
background_collector = MetricsBackgroundCollector()

def start_metrics_collection():
    """Start all metrics collection"""
    background_collector.start()

def stop_metrics_collection():
    """Stop all metrics collection"""
    background_collector.stop()