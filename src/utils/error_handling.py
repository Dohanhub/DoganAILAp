"""
Enhanced Error Handling and Resilience Improvements
Production-ready error handling with structured responses, correlation IDs, and monitoring
"""

import traceback
import uuid
import time
import asyncio
import logging
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum, Set
from typing import Any, Dict, Optional, Union, List, Callable
from contextlib import asynccontextmanager
from functools import wraps
from collections import defaultdict

from pydantic import BaseModel, Field
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import structlog

# Configure structured logging
logger = structlog.get_logger()

# =============================================================================
# CORRELATION ID MANAGEMENT
# =============================================================================

class CorrelationIDManager:
    """Manage correlation IDs for request tracing"""
    
    def __init__(self):
        self._local = threading.local()
        self._correlation_ids: Set[str] = set()
        self._lock = threading.Lock()
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread"""
        self._local.correlation_id = correlation_id
        with self._lock:
            self._correlation_ids.add(correlation_id)
    
    def get_correlation_id(self) -> str:
        """Get correlation ID for current thread"""
        if not hasattr(self._local, 'correlation_id'):
            correlation_id = str(uuid.uuid4())
            self.set_correlation_id(correlation_id)
        return self._local.correlation_id
    
    def clear_correlation_id(self):
        """Clear correlation ID for current thread"""
        if hasattr(self._local, 'correlation_id'):
            with self._lock:
                self._correlation_ids.discard(self._local.correlation_id)
            delattr(self._local, 'correlation_id')
    
    def get_active_correlation_ids(self) -> List[str]:
        """Get all active correlation IDs"""
        with self._lock:
            return list(self._correlation_ids)

# Global correlation ID manager
correlation_manager = CorrelationIDManager()

# =============================================================================
# ENHANCED ERROR CODES
# =============================================================================

class ErrorCode(str, Enum):
    """Enhanced standardized error codes for better error handling"""
    # Database Errors
    DATABASE_CONNECTION_ERROR = "DB_001"
    DATABASE_QUERY_ERROR = "DB_002"
    DATABASE_TIMEOUT_ERROR = "DB_003"
    DATABASE_CONSTRAINT_ERROR = "DB_004"
    DATABASE_DEADLOCK_ERROR = "DB_005"
    
    # Compliance Errors
    COMPLIANCE_VALIDATION_ERROR = "COMPLIANCE_001"
    COMPLIANCE_POLICY_ERROR = "COMPLIANCE_002"
    COMPLIANCE_AUDIT_ERROR = "COMPLIANCE_003"
    
    # External Service Errors
    EXTERNAL_SERVICE_ERROR = "EXT_001"
    EXTERNAL_SERVICE_TIMEOUT = "EXT_002"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXT_003"
    
    # Authentication & Authorization
    AUTHENTICATION_ERROR = "AUTH_001"
    AUTHORIZATION_ERROR = "AUTH_002"
    TOKEN_EXPIRED_ERROR = "AUTH_003"
    INSUFFICIENT_PERMISSIONS = "AUTH_004"
    
    # Rate Limiting & Throttling
    RATE_LIMIT_ERROR = "RATE_001"
    THROTTLE_ERROR = "RATE_002"
    
    # Configuration & System
    CONFIGURATION_ERROR = "CONFIG_001"
    RESOURCE_NOT_FOUND = "RESOURCE_001"
    PROCESSING_TIMEOUT = "TIMEOUT_001"
    VALIDATION_ERROR = "VALIDATION_001"
    
    # Network & Connectivity
    NETWORK_ERROR = "NETWORK_001"
    CONNECTION_TIMEOUT = "NETWORK_002"
    DNS_ERROR = "NETWORK_003"
    
    # Data & Processing
    DATA_PARSING_ERROR = "DATA_001"
    DATA_VALIDATION_ERROR = "DATA_002"
    DATA_TRANSFORMATION_ERROR = "DATA_003"

# =============================================================================
# ENHANCED ERROR DETAILS
# =============================================================================

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorContext(BaseModel):
    """Additional context for error details"""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ErrorDetail(BaseModel):
    """Enhanced structured error detail model"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    context: Optional[ErrorContext] = None
    stack_trace: Optional[str] = None
    retryable: bool = False
    suggested_action: Optional[str] = None
    
    class Config:
        use_enum_values = True

# =============================================================================
# ENHANCED EXCEPTIONS
# =============================================================================

class ComplianceException(Exception):
    """Enhanced base exception for compliance-related errors"""
    def __init__(
        self, 
        message: str, 
        code: ErrorCode = ErrorCode.COMPLIANCE_VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        correlation_id: Optional[str] = None,
        retryable: bool = False,
        suggested_action: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.severity = severity
        self.correlation_id = correlation_id or correlation_manager.get_correlation_id()
        self.retryable = retryable
        self.suggested_action = suggested_action
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)

class DatabaseException(ComplianceException):
    """Database-related exceptions"""
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.DATABASE_CONNECTION_ERROR,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = True
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            severity=ErrorSeverity.HIGH,
            retryable=retryable,
            suggested_action="Check database connectivity and retry"
        )

class ExternalServiceException(ComplianceException):
    """External service exceptions"""
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = True
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            severity=ErrorSeverity.MEDIUM,
            retryable=retryable,
            suggested_action="Retry the operation or contact support"
        )

class ValidationException(ComplianceException):
    """Validation exceptions"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details=details,
            severity=ErrorSeverity.LOW,
            retryable=False,
            suggested_action="Check input data and try again"
        )

class RetryableException(ComplianceException):
    """Exception that indicates the operation can be retried"""
    def __init__(self, message: str, code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=code,
            details=details,
            retryable=True,
            suggested_action="Retry the operation"
        )

class CircuitBreakerError(ComplianceException):
    """Circuit breaker is open, service unavailable"""
    def __init__(self, service_name: str):
        super().__init__(
            message=f"Circuit breaker is OPEN for {service_name}",
            code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            suggested_action="Wait for circuit breaker to close or use fallback"
        )

# =============================================================================
# ERROR MONITORING AND METRICS
# =============================================================================

class ErrorMonitor:
    """Monitor and track errors for analytics"""
    
    def __init__(self):
        self._error_counts = defaultdict(int)
        self._error_timestamps = defaultdict(list)
        self._severity_counts = defaultdict(int)
        self._correlation_errors = defaultdict(list)
        self._lock = threading.Lock()
        self._max_history = 1000
    
    def record_error(self, error_detail: ErrorDetail):
        """Record an error for monitoring"""
        with self._lock:
            # Count by error code
            self._error_counts[error_detail.code] += 1
            
            # Track by severity
            self._severity_counts[error_detail.severity] += 1
            
            # Track by correlation ID
            if error_detail.correlation_id:
                self._correlation_errors[error_detail.correlation_id].append({
                    "code": error_detail.code,
                    "message": error_detail.message,
                    "timestamp": error_detail.timestamp.isoformat(),
                    "severity": error_detail.severity
                })
            
            # Track timestamps
            self._error_timestamps[error_detail.code].append(error_detail.timestamp)
            
            # Clean up old timestamps
            if len(self._error_timestamps[error_detail.code]) > self._max_history:
                self._error_timestamps[error_detail.code] = self._error_timestamps[error_detail.code][-self._max_history:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            return {
                "error_counts": dict(self._error_counts),
                "severity_counts": dict(self._severity_counts),
                "total_errors": sum(self._error_counts.values()),
                "unique_error_codes": len(self._error_counts),
                "correlation_errors": dict(self._correlation_errors)
            }
    
    def get_error_rate(self, minutes: int = 60) -> Dict[str, float]:
        """Get error rate over specified time period"""
        with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            rates = {}
            
            for code, timestamps in self._error_timestamps.items():
                recent_errors = [ts for ts in timestamps if ts > cutoff_time]
                rates[code] = len(recent_errors) / (minutes / 60)  # errors per hour
            
            return rates

# Global error monitor
error_monitor = ErrorMonitor()

# =============================================================================
# ENHANCED CIRCUIT BREAKER
# =============================================================================

class EnhancedCircuitBreaker:
    """Enhanced circuit breaker pattern with monitoring"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        monitor_errors: bool = True
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.monitor_errors = monitor_errors
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
        
        # Monitoring
        self._success_count = 0
        self._total_requests = 0
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with enhanced circuit breaker protection"""
        with self._lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit breaker {self.name} attempting reset to HALF_OPEN")
                else:
                    raise CircuitBreakerError(self.name)
            
            self._total_requests += 1
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure(e)
            raise RetryableException(
                f"Circuit breaker failure in {self.name}: {str(e)}",
                code=ErrorCode.EXTERNAL_SERVICE_ERROR
            ) from e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        return (
            self.last_failure_time and
            (datetime.now(timezone.utc).timestamp() - self.last_failure_time) >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful operation"""
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"
            self._success_count += 1
            
            if self.monitor_errors:
                logger.info(
                    f"Circuit breaker {self.name} success",
                    success_count=self._success_count,
                    total_requests=self._total_requests
                )
    
    def _on_failure(self, exception: Exception):
        """Handle failed operation"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc).timestamp()
            
            if self.monitor_errors:
                logger.warning(
                    f"Circuit breaker {self.name} failure",
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold,
                    exception=str(exception)
                )
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker {self.name} opened")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold,
                "success_count": self._success_count,
                "total_requests": self._total_requests,
                "last_failure_time": self.last_failure_time,
                "recovery_timeout": self.recovery_timeout
            }

# =============================================================================
# ENHANCED RETRY DECORATOR
# =============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (RetryableException,)
):
    """Enhanced retry decorator with exponential backoff and monitoring"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            correlation_id = correlation_manager.get_correlation_id()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Log successful retry if not first attempt
                    if attempt > 0:
                        logger.info(
                            f"Retry successful on attempt {attempt + 1}",
                            correlation_id=correlation_id,
                            function=func.__name__
                        )
                    
                    return result
                    
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s",
                        correlation_id=correlation_id,
                        function=func.__name__,
                        error=str(e),
                        attempt=attempt + 1,
                        max_retries=max_retries
                    )
                    await asyncio.sleep(delay)
                except Exception as e:
                    # Non-retryable exception
                    logger.error(
                        f"Non-retryable error in {func.__name__}",
                        correlation_id=correlation_id,
                        error=str(e),
                        exc_info=True
                    )
                    raise ComplianceException(
                        f"Non-retryable error: {str(e)}",
                        code=ErrorCode.PROCESSING_TIMEOUT
                    ) from e
            
            # All retries exhausted
            logger.error(
                f"Max retries ({max_retries}) exhausted for {func.__name__}",
                correlation_id=correlation_id,
                final_error=str(last_exception)
            )
            raise ComplianceException(
                f"Max retries ({max_retries}) exhausted",
                code=ErrorCode.PROCESSING_TIMEOUT
            ) from last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# =============================================================================
# ENHANCED GLOBAL EXCEPTION HANDLER
# =============================================================================

async def enhanced_global_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler for FastAPI with structured responses"""
    
    # Generate correlation ID if not present
    correlation_id = getattr(request.state, 'correlation_id', None)
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
    
    # Create error context
    error_context = ErrorContext(
        request_path=str(request.url.path),
        request_method=request.method,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    if isinstance(exc, ComplianceException):
        error_detail = ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            correlation_id=correlation_id,
            severity=exc.severity,
            context=error_context,
            retryable=exc.retryable,
            suggested_action=exc.suggested_action
        )
        status_code = 400 if exc.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM] else 500
        
    elif isinstance(exc, HTTPException):
        error_detail = ErrorDetail(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=exc.detail,
            correlation_id=correlation_id,
            context=error_context,
            retryable=False
        )
        status_code = exc.status_code
        
    else:
        # Unexpected error
        error_detail = ErrorDetail(
            code=ErrorCode.PROCESSING_TIMEOUT,
            message="Internal server error",
            details={"trace": traceback.format_exc()},
            correlation_id=correlation_id,
            severity=ErrorSeverity.CRITICAL,
            context=error_context,
            stack_trace=traceback.format_exc(),
            retryable=False,
            suggested_action="Contact support with correlation ID"
        )
        status_code = 500
    
    # Record error for monitoring
    error_monitor.record_error(error_detail)
    
    # Log the error with structured logging
    logger.error(
        f"Request failed: {error_detail.code} - {error_detail.message}",
        correlation_id=correlation_id,
        error_code=error_detail.code,
        severity=error_detail.severity,
        path=error_context.request_path,
        method=error_context.request_method,
        retryable=error_detail.retryable,
        suggested_action=error_detail.suggested_action
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_detail.dict(),
        headers={
            "X-Correlation-ID": correlation_id,
            "X-Error-Code": error_detail.code,
            "X-Retryable": str(error_detail.retryable).lower()
        }
    )

# =============================================================================
# ENHANCED RESOURCE MANAGEMENT
# =============================================================================

@asynccontextmanager
async def enhanced_managed_resource(resource_factory, cleanup_func=None):
    """Enhanced context manager for proper resource cleanup with monitoring"""
    resource = None
    correlation_id = correlation_manager.get_correlation_id()
    
    try:
        resource = await resource_factory()
        logger.debug("Resource acquired", correlation_id=correlation_id)
        yield resource
    except Exception as e:
        logger.error(
            "Resource management error",
            correlation_id=correlation_id,
            error=str(e),
            exc_info=True
        )
        raise ComplianceException(
            f"Resource management failed: {str(e)}",
            code=ErrorCode.CONFIGURATION_ERROR,
            correlation_id=correlation_id
        ) from e
    finally:
        if resource and cleanup_func:
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func(resource)
                else:
                    cleanup_func(resource)
                logger.debug("Resource cleaned up", correlation_id=correlation_id)
            except Exception as cleanup_error:
                logger.error(
                    "Resource cleanup failed",
                    correlation_id=correlation_id,
                    error=str(cleanup_error)
                )

# =============================================================================
# ENHANCED HEALTH CHECKER
# =============================================================================

class EnhancedHealthChecker:
    """Enhanced health checker with circuit breaker pattern and monitoring"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, EnhancedCircuitBreaker] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get_circuit_breaker(self, service_name: str) -> EnhancedCircuitBreaker:
        """Get or create circuit breaker for service"""
        with self._lock:
            if service_name not in self.circuit_breakers:
                self.circuit_breakers[service_name] = EnhancedCircuitBreaker(
                    name=service_name,
                    failure_threshold=5,
                    recovery_timeout=60
                )
            return self.circuit_breakers[service_name]
    
    async def check_service_health(self, service_name: str, check_func) -> Dict[str, Any]:
        """Check health of a service with enhanced circuit breaker protection"""
        circuit_breaker = self.get_circuit_breaker(service_name)
        correlation_id = correlation_manager.get_correlation_id()
        
        try:
            result = circuit_breaker.call(check_func)
            self.health_status[service_name] = {
                "status": "healthy",
                "last_check": datetime.now(timezone.utc).isoformat(),
                "circuit_breaker_state": circuit_breaker.state,
                "correlation_id": correlation_id
            }
            return self.health_status[service_name]
            
        except CircuitBreakerError:
            self.health_status[service_name] = {
                "status": "circuit_breaker_open",
                "last_check": datetime.now(timezone.utc).isoformat(),
                "circuit_breaker_state": circuit_breaker.state,
                "correlation_id": correlation_id
            }
            return self.health_status[service_name]
            
        except Exception as e:
            self.health_status[service_name] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat(),
                "circuit_breaker_state": circuit_breaker.state,
                "correlation_id": correlation_id
            }
            return self.health_status[service_name]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all services"""
        with self._lock:
            return {
                "services": self.health_status,
                "circuit_breakers": {
                    name: cb.get_status() for name, cb in self.circuit_breakers.items()
                },
                "error_stats": error_monitor.get_error_stats(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# =============================================================================
# ERROR HANDLING UTILITIES
# =============================================================================

def handle_database_error(func: Callable) -> Callable:
    """Decorator to handle database errors with structured responses"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        correlation_id = correlation_manager.get_correlation_id()
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Database error in {func.__name__}",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise DatabaseException(
                message=f"Database operation failed: {str(e)}",
                details={"function": func.__name__},
                correlation_id=correlation_id
            ) from e
    return wrapper

def handle_external_service_error(func: Callable) -> Callable:
    """Decorator to handle external service errors with structured responses"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        correlation_id = correlation_manager.get_correlation_id()
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"External service error in {func.__name__}",
                correlation_id=correlation_id,
                error=str(e),
                exc_info=True
            )
            raise ExternalServiceException(
                message=f"External service call failed: {str(e)}",
                details={"function": func.__name__},
                correlation_id=correlation_id
            ) from e
    return wrapper

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'ErrorCode',
    'ErrorSeverity',
    'ErrorDetail',
    'ErrorContext',
    'ComplianceException',
    'DatabaseException',
    'ExternalServiceException',
    'ValidationException',
    'RetryableException',
    'CircuitBreakerError',
    'EnhancedCircuitBreaker',
    'retry_with_backoff',
    'enhanced_global_exception_handler',
    'enhanced_managed_resource',
    'EnhancedHealthChecker',
    'handle_database_error',
    'handle_external_service_error',
    'correlation_manager',
    'error_monitor'
]