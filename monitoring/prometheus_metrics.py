#!/usr/bin/env python3
"""
Prometheus Metrics System for DoganAI Compliance Kit
Implements comprehensive metrics collection for monitoring and observability
"""

import time
import psutil
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoganAIMetrics:
    """Comprehensive metrics collection for DoganAI Compliance Kit"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # API Metrics
        self.api_requests_total = Counter(
            'doganai_api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration_seconds = Histogram(
            'doganai_api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # Compliance Metrics
        self.compliance_evaluations_total = Counter(
            'doganai_compliance_evaluations_total',
            'Total number of compliance evaluations',
            ['mapping', 'status', 'standard'],
            registry=self.registry
        )
        
        self.compliance_score = Gauge(
            'doganai_compliance_score',
            'Current compliance score',
            ['mapping', 'standard'],
            registry=self.registry
        )
        
        self.compliance_evaluation_duration_seconds = Histogram(
            'doganai_compliance_evaluation_duration_seconds',
            'Compliance evaluation duration in seconds',
            ['mapping', 'standard'],
            buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        # Security Metrics
        self.security_events_total = Counter(
            'doganai_security_events_total',
            'Total number of security events',
            ['event_type', 'severity', 'source'],
            registry=self.registry
        )
        
        self.authentication_attempts_total = Counter(
            'doganai_authentication_attempts_total',
            'Total number of authentication attempts',
            ['method', 'status'],
            registry=self.registry
        )
        
        self.rate_limit_violations_total = Counter(
            'doganai_rate_limit_violations_total',
            'Total number of rate limit violations',
            ['endpoint', 'ip_address'],
            registry=self.registry
        )
        
        # Database Metrics
        self.database_connections_active = Gauge(
            'doganai_database_connections_active',
            'Number of active database connections',
            ['database', 'type'],
            registry=self.registry
        )
        
        self.database_query_duration_seconds = Histogram(
            'doganai_database_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type', 'table'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry
        )
        
        self.database_errors_total = Counter(
            'doganai_database_errors_total',
            'Total number of database errors',
            ['error_type', 'operation'],
            registry=self.registry
        )
        
        # Cache Metrics
        self.cache_hits_total = Counter(
            'doganai_cache_hits_total',
            'Total number of cache hits',
            ['cache_type', 'key_pattern'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'doganai_cache_misses_total',
            'Total number of cache misses',
            ['cache_type', 'key_pattern'],
            registry=self.registry
        )
        
        self.cache_size_bytes = Gauge(
            'doganai_cache_size_bytes',
            'Current cache size in bytes',
            ['cache_type'],
            registry=self.registry
        )
        
        # System Metrics
        self.system_cpu_usage_percent = Gauge(
            'doganai_system_cpu_usage_percent',
            'System CPU usage percentage',
            ['core'],
            registry=self.registry
        )
        
        self.system_memory_usage_bytes = Gauge(
            'doganai_system_memory_usage_bytes',
            'System memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.system_disk_usage_bytes = Gauge(
            'doganai_system_disk_usage_bytes',
            'System disk usage in bytes',
            ['mount_point'],
            registry=self.registry
        )
        
        # Business Metrics
        self.vendor_evaluations_total = Counter(
            'doganai_vendor_evaluations_total',
            'Total number of vendor evaluations',
            ['vendor_type', 'status'],
            registry=self.registry
        )
        
        self.policy_updates_total = Counter(
            'doganai_policy_updates_total',
            'Total number of policy updates',
            ['policy_type', 'action'],
            registry=self.registry
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'doganai_errors_total',
            'Total number of errors',
            ['error_type', 'module'],
            registry=self.registry
        )
        
        # Application Info
        self.app_info = Info(
            'doganai_app_info',
            'Application information',
            registry=self.registry
        )
        self.app_info.info({
            'version': '2.0.0',
            'name': 'DoganAI Compliance Kit',
            'environment': 'production'
        })
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        self.api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_compliance_evaluation(self, mapping: str, status: str, standard: str, score: float, duration: float):
        """Record compliance evaluation metrics"""
        self.compliance_evaluations_total.labels(
            mapping=mapping,
            status=status,
            standard=standard
        ).inc()
        
        self.compliance_score.labels(
            mapping=mapping,
            standard=standard
        ).set(score)
        
        self.compliance_evaluation_duration_seconds.labels(
            mapping=mapping,
            standard=standard
        ).observe(duration)
    
    def record_security_event(self, event_type: str, severity: str, source: str):
        """Record security event metrics"""
        self.security_events_total.labels(
            event_type=event_type,
            severity=severity,
            source=source
        ).inc()
    
    def record_authentication_attempt(self, method: str, status: str):
        """Record authentication attempt metrics"""
        self.authentication_attempts_total.labels(
            method=method,
            status=status
        ).inc()
    
    def record_rate_limit_violation(self, endpoint: str, ip_address: str):
        """Record rate limit violation metrics"""
        self.rate_limit_violations_total.labels(
            endpoint=endpoint,
            ip_address=ip_address
        ).inc()
    
    def record_database_connection(self, database: str, connection_type: str, count: int):
        """Record database connection metrics"""
        self.database_connections_active.labels(
            database=database,
            type=connection_type
        ).set(count)
    
    def record_database_query(self, query_type: str, table: str, duration: float):
        """Record database query metrics"""
        self.database_query_duration_seconds.labels(
            query_type=query_type,
            table=table
        ).observe(duration)
    
    def record_database_error(self, error_type: str, operation: str):
        """Record database error metrics"""
        self.database_errors_total.labels(
            error_type=error_type,
            operation=operation
        ).inc()
    
    def record_cache_hit(self, cache_type: str, key_pattern: str):
        """Record cache hit metrics"""
        self.cache_hits_total.labels(
            cache_type=cache_type,
            key_pattern=key_pattern
        ).inc()
    
    def record_cache_miss(self, cache_type: str, key_pattern: str):
        """Record cache miss metrics"""
        self.cache_misses_total.labels(
            cache_type=cache_type,
            key_pattern=key_pattern
        ).inc()
    
    def record_cache_size(self, cache_type: str, size_bytes: int):
        """Record cache size metrics"""
        self.cache_size_bytes.labels(
            cache_type=cache_type
        ).set(size_bytes)
    
    def record_system_metrics(self):
        """Record system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        for i, percent in enumerate(cpu_percent):
            self.system_cpu_usage_percent.labels(core=f"cpu_{i}").set(percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.system_memory_usage_bytes.labels(type="total").set(memory.total)
        self.system_memory_usage_bytes.labels(type="available").set(memory.available)
        self.system_memory_usage_bytes.labels(type="used").set(memory.used)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.system_disk_usage_bytes.labels(mount_point="/").set(disk.used)
    
    def record_vendor_evaluation(self, vendor_type: str, status: str):
        """Record vendor evaluation metrics"""
        self.vendor_evaluations_total.labels(
            vendor_type=vendor_type,
            status=status
        ).inc()
    
    def record_policy_update(self, policy_type: str, action: str):
        """Record policy update metrics"""
        self.policy_updates_total.labels(
            policy_type=policy_type,
            action=action
        ).inc()
    
    def record_error(self, error_type: str, module: str):
        """Record error metrics"""
        self.errors_total.labels(
            error_type=error_type,
            module=module
        ).inc()
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)
    
    async def start_metrics_collection(self, interval: int = 60):
        """Start periodic metrics collection"""
        logger.info("Starting metrics collection...")
        
        while True:
            try:
                self.record_system_metrics()
                logger.debug("System metrics recorded")
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                self.record_error("metrics_collection", "monitoring")
                await asyncio.sleep(interval)

# Global metrics instance
metrics = DoganAIMetrics()

def get_metrics() -> DoganAIMetrics:
    """Get the global metrics instance"""
    return metrics
