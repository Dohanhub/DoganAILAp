"""
Monitoring and metrics for DoganAI-Compliance-Kit
"""
from typing import Dict
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Container for performance metric data"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        self._metrics_buffer = []
        self._lock = threading.Lock()
        self._collection_interval = 60  # seconds
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        with self._lock:
            self._metrics_buffer.append(metric)
            
            # Auto-flush if buffer is getting large
            if len(self._metrics_buffer) > 1000:
                self._flush_metrics()
    
    def _flush_metrics(self):
        """Flush metrics buffer"""
        logger.debug(f"Flushing {len(self._metrics_buffer)} metrics")
        self._metrics_buffer.clear()
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Basic system metrics - simplified for Replit
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Record metrics
            self.record_metric(PerformanceMetric("cpu_usage", cpu_percent, "percent", current_time))
            self.record_metric(PerformanceMetric("memory_usage", memory.percent, "percent", current_time))
            
        except ImportError:
            # psutil not available, skip system metrics
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

# Global metrics collector
metrics_collector = MetricsCollector()
