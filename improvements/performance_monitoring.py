"""
Performance Monitoring and Optimization System
Comprehensive monitoring for database connections and error handling
"""

import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import structlog
import psutil

from .error_handling import correlation_manager, error_monitor

logger = structlog.get_logger()

# =============================================================================
# PERFORMANCE METRICS
# =============================================================================

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    connection_count: int = 0
    active_connections: int = 0
    connection_errors: int = 0
    query_count: int = 0
    slow_queries: int = 0
    avg_query_time: float = 0.0
    max_query_time: float = 0.0
    total_query_time: float = 0.0
    connection_leaks: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class ErrorMetrics:
    """Error handling performance metrics"""
    total_errors: int = 0
    error_rate: float = 0.0
    avg_error_response_time: float = 0.0
    error_by_type: Dict[str, int] = None
    retry_success_rate: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.error_by_type is None:
            self.error_by_type = {}

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    thread_count: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

# =============================================================================
# PERFORMANCE MONITORING CORE
# =============================================================================

class PerformanceMonitor:
    """Core performance monitoring system"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._lock = threading.Lock()
        
        # Metrics storage
        self._db_metrics_history: deque = deque(maxlen=max_history)
        self._error_metrics_history: deque = deque(maxlen=max_history)
        self._system_metrics_history: deque = deque(maxlen=max_history)
        
        # Current metrics
        self._current_db_metrics = DatabaseMetrics()
        self._current_error_metrics = ErrorMetrics()
        self._current_system_metrics = SystemMetrics()
        
        # Performance tracking
        self._query_times: deque = deque(maxlen=1000)
        self._error_response_times: deque = deque(maxlen=1000)
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_thread = None
        self._monitor_interval = 30  # seconds
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self._monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring_active:
            try:
                self._collect_metrics()
                time.sleep(self._monitor_interval)
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                time.sleep(5)
    
    def _collect_metrics(self):
        """Collect all performance metrics"""
        # Collect system metrics
        self._collect_system_metrics()
        
        # Collect error metrics
        self._collect_error_metrics()
        
        # Store current metrics in history
        with self._lock:
            self._system_metrics_history.append(self._current_system_metrics)
            self._error_metrics_history.append(self._current_error_metrics)
            self._db_metrics_history.append(self._current_db_metrics)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            self._current_system_metrics.cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._current_system_metrics.memory_usage = memory.percent
            
            # Thread count
            self._current_system_metrics.thread_count = threading.active_count()
            
            self._current_system_metrics.timestamp = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
    
    def _collect_error_metrics(self):
        """Collect error handling metrics"""
        try:
            error_stats = error_monitor.get_error_stats()
            
            self._current_error_metrics.total_errors = error_stats.get("total_errors", 0)
            self._current_error_metrics.error_by_type = error_stats.get("error_counts", {})
            
            # Calculate error rate (errors per minute)
            if self._error_metrics_history:
                last_metrics = self._error_metrics_history[-1]
                time_diff = (self._current_error_metrics.timestamp - last_metrics.timestamp).total_seconds() / 60
                if time_diff > 0:
                    error_diff = self._current_error_metrics.total_errors - last_metrics.total_errors
                    self._current_error_metrics.error_rate = error_diff / time_diff
            
            # Calculate average error response time
            if self._error_response_times:
                self._current_error_metrics.avg_error_response_time = sum(self._error_response_times) / len(self._error_response_times)
            
            self._current_error_metrics.timestamp = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error("Error collecting error metrics", error=str(e))
    
    def update_database_metrics(self, metrics: DatabaseMetrics):
        """Update database metrics"""
        with self._lock:
            self._current_db_metrics = metrics
    
    def record_query_time(self, query_time: float):
        """Record query execution time"""
        self._query_times.append(query_time)
        
        # Update database metrics
        with self._lock:
            self._current_db_metrics.query_count += 1
            self._current_db_metrics.total_query_time += query_time
            
            if query_time > self._current_db_metrics.max_query_time:
                self._current_db_metrics.max_query_time = query_time
            
            # Mark as slow query if > 1 second
            if query_time > 1.0:
                self._current_db_metrics.slow_queries += 1
            
            # Update average query time
            if self._current_db_metrics.query_count > 0:
                self._current_db_metrics.avg_query_time = (
                    self._current_db_metrics.total_query_time / self._current_db_metrics.query_count
                )
    
    def record_error_response_time(self, response_time: float):
        """Record error response time"""
        self._error_response_times.append(response_time)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self._lock:
            return {
                "database": asdict(self._current_db_metrics),
                "errors": asdict(self._current_error_metrics),
                "system": asdict(self._current_system_metrics),
                "history": {
                    "database_count": len(self._db_metrics_history),
                    "error_count": len(self._error_metrics_history),
                    "system_count": len(self._system_metrics_history)
                },
                "monitoring": {
                    "active": self._monitoring_active,
                    "interval": self._monitor_interval
                }
            }

# =============================================================================
# DATABASE PERFORMANCE MONITORING
# =============================================================================

class DatabasePerformanceMonitor:
    """Specialized database performance monitoring"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
    
    @contextmanager
    def monitor_query(self, query: str, params: Dict[str, Any] = None):
        """Monitor database query execution"""
        start_time = time.time()
        correlation_id = correlation_manager.get_correlation_id()
        
        try:
            yield
            query_time = time.time() - start_time
            self.performance_monitor.record_query_time(query_time)
            
            # Log slow queries
            if query_time > 1.0:
                logger.warning(
                    "Slow database query detected",
                    correlation_id=correlation_id,
                    query=query[:100] + "..." if len(query) > 100 else query,
                    duration=query_time,
                    params=params
                )
            
            logger.debug(
                "Database query completed",
                correlation_id=correlation_id,
                duration=query_time
            )
            
        except Exception as e:
            query_time = time.time() - start_time
            self.performance_monitor.record_query_time(query_time)
            
            logger.error(
                "Database query failed",
                correlation_id=correlation_id,
                query=query[:100] + "..." if len(query) > 100 else query,
                duration=query_time,
                error=str(e)
            )
            raise

# =============================================================================
# ERROR HANDLING PERFORMANCE MONITORING
# =============================================================================

class ErrorHandlingPerformanceMonitor:
    """Monitor error handling performance"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
    
    @contextmanager
    def monitor_error_handling(self, error_type: str):
        """Monitor error handling execution"""
        start_time = time.time()
        correlation_id = correlation_manager.get_correlation_id()
        
        try:
            yield
            response_time = time.time() - start_time
            self.performance_monitor.record_error_response_time(response_time)
            
            logger.debug(
                "Error handling completed",
                error_type=error_type,
                correlation_id=correlation_id,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.performance_monitor.record_error_response_time(response_time)
            
            logger.error(
                "Error handling failed",
                error_type=error_type,
                correlation_id=correlation_id,
                response_time=response_time,
                error=str(e)
            )
            raise

# =============================================================================
# PERFORMANCE OPTIMIZATION RECOMMENDATIONS
# =============================================================================

class PerformanceOptimizer:
    """Provide performance optimization recommendations"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
    
    def get_database_recommendations(self) -> List[Dict[str, Any]]:
        """Get database performance recommendations"""
        recommendations = []
        db_metrics = self.performance_monitor._current_db_metrics
        
        # Slow query recommendations
        if db_metrics.slow_queries > 0:
            recommendations.append({
                "type": "slow_queries",
                "severity": "high",
                "message": f"{db_metrics.slow_queries} slow queries detected",
                "recommendation": "Review and optimize slow queries",
                "current_value": db_metrics.slow_queries,
                "suggested_action": "Add database indexes or optimize query logic"
            })
        
        # Connection leak recommendations
        if db_metrics.connection_leaks > 0:
            recommendations.append({
                "type": "connection_leaks",
                "severity": "critical",
                "message": f"{db_metrics.connection_leaks} connection leaks detected",
                "recommendation": "Fix connection leak issues immediately",
                "current_value": db_metrics.connection_leaks,
                "suggested_action": "Ensure proper connection cleanup in all code paths"
            })
        
        return recommendations
    
    def get_error_handling_recommendations(self) -> List[Dict[str, Any]]:
        """Get error handling performance recommendations"""
        recommendations = []
        error_metrics = self.performance_monitor._current_error_metrics
        
        # High error rate recommendations
        if error_metrics.error_rate > 10:  # More than 10 errors per minute
            recommendations.append({
                "type": "error_rate",
                "severity": "high",
                "message": f"High error rate: {error_metrics.error_rate:.2f} errors/minute",
                "recommendation": "Investigate root cause of errors",
                "current_value": error_metrics.error_rate,
                "suggested_action": "Review error logs and fix underlying issues"
            })
        
        # Slow error response recommendations
        if error_metrics.avg_error_response_time > 1.0:  # More than 1 second
            recommendations.append({
                "type": "error_response_time",
                "severity": "medium",
                "message": f"Slow error response time: {error_metrics.avg_error_response_time:.2f}s",
                "recommendation": "Optimize error handling logic",
                "current_value": error_metrics.avg_error_response_time,
                "suggested_action": "Simplify error handling or add caching"
            })
        
        return recommendations
    
    def get_system_recommendations(self) -> List[Dict[str, Any]]:
        """Get system performance recommendations"""
        recommendations = []
        system_metrics = self.performance_monitor._current_system_metrics
        
        # High CPU usage recommendations
        if system_metrics.cpu_usage > 80:
            recommendations.append({
                "type": "cpu_usage",
                "severity": "high",
                "message": f"High CPU usage: {system_metrics.cpu_usage:.1f}%",
                "recommendation": "Consider scaling or optimization",
                "current_value": system_metrics.cpu_usage,
                "suggested_action": "Add more CPU resources or optimize code"
            })
        
        # High memory usage recommendations
        if system_metrics.memory_usage > 85:
            recommendations.append({
                "type": "memory_usage",
                "severity": "high",
                "message": f"High memory usage: {system_metrics.memory_usage:.1f}%",
                "recommendation": "Check for memory leaks or add more RAM",
                "current_value": system_metrics.memory_usage,
                "suggested_action": "Investigate memory usage patterns"
            })
        
        return recommendations
    
    def get_all_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all performance recommendations"""
        return {
            "database": self.get_database_recommendations(),
            "error_handling": self.get_error_handling_recommendations(),
            "system": self.get_system_recommendations()
        }

# =============================================================================
# GLOBAL PERFORMANCE MONITORING INSTANCE
# =============================================================================

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
db_performance_monitor = DatabasePerformanceMonitor(performance_monitor)
error_performance_monitor = ErrorHandlingPerformanceMonitor(performance_monitor)
performance_optimizer = PerformanceOptimizer(performance_monitor)

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'PerformanceMonitor',
    'DatabasePerformanceMonitor',
    'ErrorHandlingPerformanceMonitor',
    'PerformanceOptimizer',
    'DatabaseMetrics',
    'ErrorMetrics',
    'SystemMetrics',
    'performance_monitor',
    'db_performance_monitor',
    'error_performance_monitor',
    'performance_optimizer'
]
