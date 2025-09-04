"""
Advanced Monitoring and Observability Improvements
"""
import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import uuid
from contextvars import ContextVar
from collections import defaultdict, deque
import psutil
import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, Info, 
    CollectorRegistry, generate_latest,
    CONTENT_TYPE_LATEST
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    JAEGER_AVAILABLE = True
except ImportError:
    JaegerExporter = None
    JAEGER_AVAILABLE = False
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# Context Variables for Request Tracing
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    metric_name: str
    condition: str  # e.g., "> 0.95", "< 100"
    threshold: float
    duration_seconds: int = 60
    severity: str = "warning"  # warning, critical
    description: str = ""
    enabled: bool = True


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    description: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    is_active: bool = True


class StructuredLogger:
    """Enhanced structured logging with context"""
    
    def __init__(self, service_name: str, log_level: LogLevel = LogLevel.INFO):
        self.service_name = service_name
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="ISO"),
                self._add_service_context,
                structlog.dev.ConsoleRenderer() if log_level == LogLevel.DEBUG 
                else structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, log_level.upper())
            ),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def _add_service_context(self, logger, method_name, event_dict):
        """Add service context to log entries"""
        event_dict["service"] = self.service_name
        event_dict["request_id"] = request_id_var.get()
        event_dict["user_id"] = user_id_var.get()
        return event_dict
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)


class MetricsCollector:
    """Comprehensive metrics collection"""
    
    def __init__(self, service_name: str, enable_default_metrics: bool = True):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        if enable_default_metrics:
            self._setup_default_metrics()
        
        self.custom_metrics: Dict[str, Any] = {}
        
        # System metrics update interval
        self._metrics_update_interval = 5.0
        self._metrics_task: Optional[asyncio.Task] = None
    
    def _setup_default_metrics(self):
        """Setup default application metrics"""
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Compliance metrics
        self.compliance_evaluations_total = Counter(
            'compliance_evaluations_total',
            'Total compliance evaluations',
            ['mapping_type', 'status'],
            registry=self.registry
        )
        
        self.compliance_evaluation_duration = Histogram(
            'compliance_evaluation_duration_seconds',
            'Compliance evaluation duration',
            ['mapping_type'],
            registry=self.registry
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections_active = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Application info
        self.app_info = Info(
            'application_info',
            'Application information',
            registry=self.registry
        )
        self.app_info.info({
            'service': self.service_name,
            'version': '1.0.0',  # Should come from config
            'build_time': datetime.utcnow().isoformat()
        })
    
    def create_counter(self, name: str, description: str, labels: List[str] = None) -> Counter:
        """Create custom counter metric"""
        counter = Counter(name, description, labels or [], registry=self.registry)
        self.custom_metrics[name] = counter
        return counter
    
    def create_gauge(self, name: str, description: str, labels: List[str] = None) -> Gauge:
        """Create custom gauge metric"""
        gauge = Gauge(name, description, labels or [], registry=self.registry)
        self.custom_metrics[name] = gauge
        return gauge
    
    def create_histogram(self, name: str, description: str, labels: List[str] = None) -> Histogram:
        """Create custom histogram metric"""
        histogram = Histogram(name, description, labels or [], registry=self.registry)
        self.custom_metrics[name] = histogram
        return histogram
    
    async def start_system_metrics_collection(self):
        """Start collecting system metrics"""
        if self._metrics_task is None:
            self._metrics_task = asyncio.create_task(self._collect_system_metrics())
    
    async def stop_system_metrics_collection(self):
        """Stop collecting system metrics"""
        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass
            self._metrics_task = None
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_memory_usage.set(memory.used)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_disk_usage.set(disk_percent)
                
                await asyncio.sleep(self._metrics_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self._metrics_update_interval)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)


class AlertManager:
    """Alert management system"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable] = []
        self._check_interval = 30.0  # seconds
        self._check_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
    
    def add_alert_rule(self, rule: AlertRule):
        """Add alert rule"""
        with self._lock:
            self.alert_rules[rule.name] = rule
    
    def remove_alert_rule(self, rule_name: str):
        """Remove alert rule"""
        with self._lock:
            if rule_name in self.alert_rules:
                del self.alert_rules[rule_name]
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start alert monitoring"""
        if self._check_task is None:
            self._check_task = asyncio.create_task(self._check_alerts())
    
    async def stop_monitoring(self):
        """Stop alert monitoring"""
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self._check_task = None
    
    async def _check_alerts(self):
        """Check alert conditions periodically"""
        while True:
            try:
                with self._lock:
                    for rule_name, rule in self.alert_rules.items():
                        if not rule.enabled:
                            continue
                        
                        await self._evaluate_rule(rule)
                
                await asyncio.sleep(self._check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error checking alerts: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _evaluate_rule(self, rule: AlertRule):
        """Evaluate a single alert rule"""
        try:
            # Get current metric value (simplified - in real implementation,
            # you would query the metrics collector)
            current_value = self._get_metric_value(rule.metric_name)
            
            if current_value is None:
                return
            
            # Check condition
            condition_met = self._evaluate_condition(current_value, rule.condition, rule.threshold)
            
            alert_id = f"{rule.name}_{rule.metric_name}"
            
            if condition_met:
                if alert_id not in self.active_alerts:
                    # Create new alert
                    alert = Alert(
                        id=alert_id,
                        rule_name=rule.name,
                        metric_name=rule.metric_name,
                        current_value=current_value,
                        threshold=rule.threshold,
                        severity=rule.severity,
                        description=rule.description,
                        triggered_at=datetime.utcnow()
                    )
                    
                    self.active_alerts[alert_id] = alert
                    self.alert_history.append(alert)
                    
                    # Send notifications
                    for handler in self.notification_handlers:
                        try:
                            handler(alert)
                        except Exception as e:
                            logging.error(f"Notification handler error: {e}")
            else:
                # Resolve alert if it exists
                if alert_id in self.active_alerts:
                    alert = self.active_alerts[alert_id]
                    alert.resolved_at = datetime.utcnow()
                    alert.is_active = False
                    del self.active_alerts[alert_id]
                    
                    # Send resolution notification
                    for handler in self.notification_handlers:
                        try:
                            handler(alert)
                        except Exception as e:
                            logging.error(f"Notification handler error: {e}")
        
        except Exception as e:
            logging.error(f"Error evaluating rule {rule.name}: {e}")
    
    def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value of a metric (simplified)"""
        # In a real implementation, this would query the metrics collector
        # For now, return a dummy value
        import random
        return random.uniform(0, 100)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        try:
            if condition.startswith('>'):
                return value > threshold
            elif condition.startswith('<'):
                return value < threshold
            elif condition.startswith('>='):
                return value >= threshold
            elif condition.startswith('<='):
                return value <= threshold
            elif condition.startswith('=='):
                return value == threshold
            elif condition.startswith('!='):
                return value != threshold
            else:
                return False
        except Exception:
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.triggered_at >= cutoff_time
        ]


class DistributedTracing:
    """Distributed tracing with OpenTelemetry"""
    
    def __init__(self, service_name: str, jaeger_endpoint: Optional[str] = None):
        self.service_name = service_name
        
        # Configure tracing
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)
        
        if jaeger_endpoint and JAEGER_AVAILABLE:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
    
    def trace_function(self, operation_name: Optional[str] = None):
        """Decorator for tracing functions"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                span_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add request context
                    span.set_attribute("request.id", request_id_var.get())
                    span.set_attribute("user.id", user_id_var.get())
                    
                    try:
                        if asyncio.iscoroutinefunction(func):
                            result = await func(*args, **kwargs)
                        else:
                            result = func(*args, **kwargs)
                        
                        span.set_attribute("success", True)
                        return result
                        
                    except Exception as e:
                        span.set_attribute("success", False)
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(async_wrapper(*args, **kwargs))
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and metrics"""
    
    def __init__(
        self, 
        app, 
        metrics_collector: MetricsCollector,
        logger: StructuredLogger
    ):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.logger = logger
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Extract user ID from headers or token (simplified)
        user_id = request.headers.get('X-User-ID', 'anonymous')
        user_id_var.set(user_id)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get('user-agent'),
            remote_addr=request.client.host if request.client else None
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Update metrics
            self.metrics_collector.http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            self.metrics_collector.http_request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Log response
            self.logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=duration * 1000
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Update error metrics
            self.metrics_collector.http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()
            
            # Log error
            self.logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration_ms=duration * 1000
            )
            
            raise


class HealthMonitor:
    """Comprehensive health monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.health_checks: Dict[str, Callable] = {}
        self.last_check_results: Dict[str, Dict[str, Any]] = {}
        self._check_interval = 30.0
        self._check_task: Optional[asyncio.Task] = None
    
    def register_health_check(self, name: str, check_func: Callable[[], Dict[str, Any]]):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    async def start_monitoring(self):
        """Start health monitoring"""
        if self._check_task is None:
            self._check_task = asyncio.create_task(self._run_health_checks())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self._check_task = None
    
    async def _run_health_checks(self):
        """Run health checks periodically"""
        while True:
            try:
                for name, check_func in self.health_checks.items():
                    try:
                        result = check_func()
                        self.last_check_results[name] = {
                            "status": "healthy",
                            "details": result,
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": None
                        }
                    except Exception as e:
                        self.last_check_results[name] = {
                            "status": "unhealthy",
                            "details": {},
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": str(e)
                        }
                
                await asyncio.sleep(self._check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self._check_interval)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        overall_status = "healthy"
        
        for result in self.last_check_results.values():
            if result["status"] != "healthy":
                overall_status = "unhealthy"
                break
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": self.last_check_results.copy()
        }


# Example notification handlers
def slack_notification_handler(alert: Alert):
    """Send alert notification to Slack"""
    # Implementation would send to Slack webhook
    logging.info(f"Slack notification: {alert.description} - {alert.current_value}")


def email_notification_handler(alert: Alert):
    """Send alert notification via email"""
    # Implementation would send email
    logging.info(f"Email notification: {alert.description} - {alert.current_value}")


# Setup default alert rules
def setup_default_alert_rules(alert_manager: AlertManager):
    """Setup default alert rules"""
    
    # High CPU usage
    alert_manager.add_alert_rule(AlertRule(
        name="high_cpu_usage",
        metric_name="system_cpu_usage_percent",
        condition="> 80",
        threshold=80.0,
        duration_seconds=300,
        severity="warning",
        description="High CPU usage detected"
    ))
    
    # High memory usage
    alert_manager.add_alert_rule(AlertRule(
        name="high_memory_usage",
        metric_name="system_memory_usage_percent", 
        condition="> 90",
        threshold=90.0,
        duration_seconds=300,
        severity="critical",
        description="High memory usage detected"
    ))
    
    # High error rate
    alert_manager.add_alert_rule(AlertRule(
        name="high_error_rate",
        metric_name="http_errors_rate",
        condition="> 0.05",
        threshold=0.05,
        duration_seconds=60,
        severity="critical", 
        description="High HTTP error rate detected"
    ))