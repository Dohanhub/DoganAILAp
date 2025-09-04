#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Observability Initialization
Integrates observability system with application startup
"""

import logging
import sys
from typing import Optional
from ..config.settings import Settings
from ..services.observability import observability, logger


class ObservabilityInitializer:
    """Initialize and configure observability system"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize observability system based on configuration"""
        try:
            if not self.settings.observability.enable_metrics:
                logger.info("Metrics collection disabled by configuration")
                return True
            
            # Initialize observability manager
            observability.initialize(
                app_name=self.settings.app_name,
                version=self.settings.app_version,
                environment=self.settings.environment
            )
            
            # Configure logging level
            self._configure_logging()
            
            # Start metrics server if enabled
            if self.settings.observability.enable_metrics:
                self._start_metrics_server()
            
            # Initialize health monitoring
            self._initialize_health_monitoring()
            
            self.initialized = True
            logger.info(
                "Observability system initialized successfully",
                metrics_port=self.settings.observability.metrics_port,
                environment=self.settings.environment,
                structured_logging=self.settings.observability.enable_structured_logging
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to initialize observability system",
                error=str(e),
                exc_info=True
            )
            return False
    
    def _configure_logging(self):
        """Configure logging based on settings"""
        log_level = getattr(logging, self.settings.observability.log_level.upper(), logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        if self.settings.observability.log_format == "json":
            # Structured logging is handled by structlog configuration
            pass
        else:
            # Use standard formatter for non-JSON logging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
        
        root_logger.addHandler(console_handler)
        
        logger.info(
            "Logging configured",
            log_level=self.settings.observability.log_level,
            log_format=self.settings.observability.log_format
        )
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            from prometheus_client import start_http_server
            start_http_server(self.settings.observability.metrics_port)
            
            logger.info(
                "Metrics server started",
                port=self.settings.observability.metrics_port,
                endpoint=f"http://localhost:{self.settings.observability.metrics_port}/metrics"
            )
            
        except Exception as e:
            logger.error(
                "Failed to start metrics server",
                port=self.settings.observability.metrics_port,
                error=str(e)
            )
            raise
    
    def _initialize_health_monitoring(self):
        """Initialize health monitoring for core services"""
        try:
            # Register core application services for health monitoring
            observability.health_monitor.register_service(
                service_name="database",
                endpoint=f"postgresql://{self.settings.database.host}:{self.settings.database.port}/{self.settings.database.database}",
                check_interval=self.settings.observability.health_check_interval
            )
            
            if self.settings.redis.host:
                observability.health_monitor.register_service(
                    service_name="redis",
                    endpoint=f"redis://{self.settings.redis.host}:{self.settings.redis.port}/{self.settings.redis.database}",
                    check_interval=self.settings.observability.health_check_interval
                )
            
            logger.info(
                "Health monitoring initialized",
                check_interval=self.settings.observability.health_check_interval
            )
            
        except Exception as e:
            logger.warning(
                "Failed to initialize health monitoring",
                error=str(e)
            )
    
    def shutdown(self):
        """Shutdown observability system gracefully"""
        if self.initialized:
            logger.info("Shutting down observability system")
            # Add any cleanup logic here if needed
            self.initialized = False


# Global observability initializer instance
_observability_initializer: Optional[ObservabilityInitializer] = None


def initialize_observability(settings: Settings) -> bool:
    """Initialize observability system with given settings"""
    global _observability_initializer
    
    if _observability_initializer is None:
        _observability_initializer = ObservabilityInitializer(settings)
    
    return _observability_initializer.initialize()


def shutdown_observability():
    """Shutdown observability system"""
    global _observability_initializer
    
    if _observability_initializer:
        _observability_initializer.shutdown()
        _observability_initializer = None


def get_observability_status() -> dict:
    """Get current observability system status"""
    global _observability_initializer
    
    if _observability_initializer and _observability_initializer.initialized:
        return {
            "status": "initialized",
            "metrics_enabled": _observability_initializer.settings.observability.enable_metrics,
            "structured_logging": _observability_initializer.settings.observability.enable_structured_logging,
            "metrics_port": _observability_initializer.settings.observability.metrics_port,
            "log_level": _observability_initializer.settings.observability.log_level
        }
    else:
        return {
            "status": "not_initialized",
            "metrics_enabled": False,
            "structured_logging": False
        }