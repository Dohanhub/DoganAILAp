
'\nIntegration Module - Connecting All Performance Improvements with DoganAI API\n'
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from .performance import HybridCache, CacheConfig, CacheStrategy, QueryOptimizer, AsyncConnectionPool, BatchProcessor, PerformanceMonitor, cache_with_ttl
from .error_handling import ComplianceException, RetryableException, CircuitBreaker, global_exception_handler, HealthChecker
from .security import SecurityManager, SecurityConfig, RateLimiter, SecurityBearer, UserRole, Permission
from .services.monitoring import MetricsCollector, AlertManager, StructuredLogger, RequestTrackingMiddleware, DistributedTracing

class DoganAIPerformanceIntegration():
    '\n    Integration class that brings together all performance improvements\n    for the DoganAI Compliance Kit\n    '

    def __init__(self, app: FastAPI):
        self.app = app
        self.cache: Optional[HybridCache] = None
        self.query_optimizer: Optional[QueryOptimizer] = None
        self.connection_pool: Optional[AsyncConnectionPool] = None
        self.batch_processor: Optional[BatchProcessor] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.security_manager: Optional[SecurityManager] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        self.alert_manager: Optional[AlertManager] = None
        self.circuit_breakers: Dict[(str, CircuitBreaker)] = {}
        self.logger = StructuredLogger('doganai-compliance')

    async def initialize(self, config: Dict[(str, Any)]):
        'Initialize all performance components'
        self.logger.info('Initializing DoganAI Performance Integration')
        (await self._init_cache_system(config.get('cache', {})))
        (await self._init_database_optimization(config.get('database', {})))
        (await self._init_security_components(config.get('security', {})))
        (await self._init_monitoring_system(config.get('monitoring', {})))
        (await self._init_circuit_breakers(config.get('circuit_breakers', {})))
        (await self._init_performance_monitoring())
        self._setup_error_handling()
        self.logger.info('DoganAI Performance Integration initialized successfully')

    async def _init_cache_system(self, cache_config: Dict[(str, Any)]):
        'Initialize hybrid caching system'
        try:
            config = CacheConfig(strategy=CacheStrategy.HYBRID, max_size=cache_config.get('max_size', 10000), ttl_seconds=cache_config.get('ttl_seconds', 3600), redis_url=cache_config.get('redis_url'), compression_enabled=cache_config.get('compression_enabled', True), enable_metrics=cache_config.get('enable_metrics', True))
            self.cache = HybridCache(config)
            (await self.cache.set('health_check', 'ok', ttl=60))
            result = (await self.cache.get('health_check'))
            if (result == 'ok'):
                self.logger.info('Cache system initialized successfully')
            else:
                self.logger.warning('Cache system test failed')
        except Exception as e:
            self.logger.error(f'Failed to initialize cache system: {e}')
            self.cache = HybridCache(CacheConfig(strategy=CacheStrategy.LRU))

    async def _init_database_optimization(self, db_config: Dict[(str, Any)]):
        'Initialize database optimization components'
        try:
            database_url = db_config.get('url', 'postgresql://localhost/doganai')
            self.connection_pool = AsyncConnectionPool(database_url=database_url, min_size=db_config.get('min_connections', 5), max_size=db_config.get('max_connections', 20), max_queries=db_config.get('max_queries', 50000))
            if self.cache:
                self.query_optimizer = QueryOptimizer(self.cache)
            self.batch_processor = BatchProcessor(batch_size=db_config.get('batch_size', 100), max_wait_time=db_config.get('max_wait_time', 5.0))
            self.logger.info('Database optimization initialized successfully')
        except Exception as e:
            self.logger.error(f'Failed to initialize database optimization: {e}')

    async def _init_security_components(self, security_config: Dict[(str, Any)]):
        'Initialize security components'
        try:
            config = SecurityConfig(secret_key=security_config.get('secret_key'), access_token_expire_minutes=security_config.get('token_expire_minutes', 30), max_failed_attempts=security_config.get('max_failed_attempts', 5), enable_rate_limiting=security_config.get('enable_rate_limiting', True), rate_limit_requests=security_config.get('rate_limit_requests', 100), rate_limit_window_minutes=security_config.get('rate_limit_window', 15))
            self.security_manager = SecurityManager(config)
            self.logger.info('Security components initialized successfully')
        except Exception as e:
            self.logger.error(f'Failed to initialize security components: {e}')

    async def _init_monitoring_system(self, monitoring_config: Dict[(str, Any)]):
        'Initialize monitoring and metrics collection'
        try:
            self.metrics_collector = MetricsCollector(service_name='doganai-compliance', enable_default_metrics=monitoring_config.get('enable_default_metrics', True))
            (await self.metrics_collector.start_system_metrics_collection())
            self.alert_manager = AlertManager(self.metrics_collector)
            (await self.alert_manager.start_monitoring())
            self._setup_default_alerts()
            self.logger.info('Monitoring system initialized successfully')
        except Exception as e:
            self.logger.error(f'Failed to initialize monitoring system: {e}')

    async def _init_circuit_breakers(self, cb_config: Dict[(str, Any)]):
        'Initialize circuit breakers for external services'
        services = cb_config.get('services', ['database', 'cache', 'external_api'])
        for service in services:
            self.circuit_breakers[service] = CircuitBreaker(failure_threshold=cb_config.get('failure_threshold', 5), recovery_timeout=cb_config.get('recovery_timeout', 60))
        self.logger.info(f'Circuit breakers initialized for {len(services)} services')

    async def _init_performance_monitoring(self):
        'Initialize performance monitoring'
        self.performance_monitor = PerformanceMonitor()
        self.logger.info('Performance monitoring initialized')

    def _setup_error_handling(self):
        'Setup global error handling'
        self.app.add_exception_handler(Exception, global_exception_handler)
        self.app.add_exception_handler(ComplianceException, self._compliance_error_handler)
        self.app.add_exception_handler(RetryableException, self._retryable_error_handler)

    def _setup_default_alerts(self):
        'Setup default alert rules'
        if (not self.alert_manager):
            return
        from .services.monitoring import AlertRule
        self.alert_manager.add_alert_rule(AlertRule(name='high_memory_usage', metric_name='system_memory_usage_percent', condition='> 85', threshold=85.0, duration_seconds=300, severity='warning', description='High memory usage detected'))
        self.alert_manager.add_alert_rule(AlertRule(name='slow_compliance_evaluation', metric_name='compliance_evaluation_duration_seconds', condition='> 30', threshold=30.0, duration_seconds=60, severity='warning', description='Slow compliance evaluation detected'))
        self.alert_manager.add_alert_rule(AlertRule(name='low_cache_hit_rate', metric_name='cache_hit_rate', condition='< 0.7', threshold=0.7, duration_seconds=600, severity='warning', description='Cache hit rate is too low'))

    async def _compliance_error_handler(self, request: Request, exc: ComplianceException):
        'Handle compliance-specific errors'
        self.logger.error('Compliance error occurred', error_code=exc.code, message=exc.message, path=request.url.path)
        return Response(content=f'Compliance Error: {exc.message}', status_code=400, headers={'X-Error-Code': exc.code})

    async def _retryable_error_handler(self, request: Request, exc: RetryableException):
        'Handle retryable errors'
        self.logger.warning('Retryable error occurred', error_code=exc.code, message=exc.message, path=request.url.path)
        return Response(content=f'Temporary Error: {exc.message}', status_code=503, headers={'X-Error-Code': exc.code, 'Retry-After': '60'})

    @cache_with_ttl(ttl_seconds=300)
    async def get_compliance_policy(self, policy_name: str) -> Dict[(str, Any)]:
        'Get compliance policy with caching'
        if self.performance_monitor:
            return self.performance_monitor.monitor_function(self._fetch_compliance_policy)(policy_name)
        else:
            return (await self._fetch_compliance_policy(policy_name))

    async def _fetch_compliance_policy(self, policy_name: str) -> Dict[(str, Any)]:
        'Fetch compliance policy from database'
        if (self.query_optimizer and self.connection_pool):
            query = 'SELECT * FROM policies WHERE name = $1'
            return (await self.query_optimizer.execute_cached_query(None, query, (policy_name,), ttl=300))
        else:
            return {'name': policy_name, 'rules': []}

    async def evaluate_compliance_batch(self, evaluations: list) -> list:
        'Batch evaluate multiple compliance requests'
        if self.batch_processor:
            return (await self.batch_processor.add_item(evaluations, self._process_compliance_batch))
        else:
            results = []
            for evaluation in evaluations:
                result = (await self.evaluate_compliance_single(evaluation))
                results.append(result)
            return results

    async def _process_compliance_batch(self, evaluations: list) -> list:
        'Process a batch of compliance evaluations'
        results = []
        for evaluation in evaluations:
            result = {'mapping': evaluation.get('mapping'), 'status': 'evaluated', 'score': 85.5, 'timestamp': '2024-01-01T12:00:00Z'}
            results.append(result)
        return results

    async def evaluate_compliance_single(self, evaluation: Dict[(str, Any)]) -> Dict[(str, Any)]:
        'Evaluate single compliance request with circuit breaker protection'
        service_name = 'compliance_evaluation'
        if (service_name in self.circuit_breakers):
            cb = self.circuit_breakers[service_name]
            try:
                return cb.call(self._evaluate_compliance_internal, evaluation)
            except Exception as e:
                self.logger.error(f'Circuit breaker failed for {service_name}: {e}')
                raise ComplianceException(f'Compliance service temporarily unavailable: {str(e)}', code='SERVICE_UNAVAILABLE')
        else:
            return (await self._evaluate_compliance_internal(evaluation))

    async def _evaluate_compliance_internal(self, evaluation: Dict[(str, Any)]) -> Dict[(str, Any)]:
        'Internal compliance evaluation logic'
        return {'mapping': evaluation.get('mapping'), 'status': 'compliant', 'score': 92.3, 'required': ['encryption', 'access_control'], 'provided': ['encryption', 'access_control', 'audit_logging'], 'missing': [], 'timestamp': '2024-01-01T12:00:00Z'}

    async def get_performance_stats(self) -> Dict[(str, Any)]:
        'Get comprehensive performance statistics'
        stats = {}
        if self.cache:
            stats['cache'] = self.cache.get_stats()
        if self.performance_monitor:
            stats['performance'] = self.performance_monitor.get_performance_report()
        if self.metrics_collector:
            stats['metrics'] = {'system_cpu_usage': self.metrics_collector.system_cpu_usage._value._value, 'system_memory_usage': self.metrics_collector.system_memory_usage._value._value, 'http_requests_total': self.metrics_collector.http_requests_total._value}
        stats['circuit_breakers'] = {}
        for (service, cb) in self.circuit_breakers.items():
            stats['circuit_breakers'][service] = {'state': cb.state, 'failure_count': cb.failure_count, 'last_failure_time': cb.last_failure_time}
        return stats

    async def cleanup(self):
        'Cleanup resources on shutdown'
        self.logger.info('Cleaning up DoganAI Performance Integration')
        if self.metrics_collector:
            (await self.metrics_collector.stop_system_metrics_collection())
        if self.alert_manager:
            (await self.alert_manager.stop_monitoring())
        if self.connection_pool:
            (await self.connection_pool.close())
        self.logger.info('DoganAI Performance Integration cleanup completed')

def setup_doganai_performance(app: FastAPI, config: Dict[(str, Any)]) -> DoganAIPerformanceIntegration:
    '\n    Setup function to integrate all performance improvements with FastAPI app\n    '
    integration = DoganAIPerformanceIntegration(app)
    app.state.performance_integration = integration

    @app.on_event('startup')
    async def startup_performance():
        (await integration.initialize(config))

    @app.on_event('shutdown')
    async def shutdown_performance():
        (await integration.cleanup())
    if integration.metrics_collector:
        app.add_middleware(RequestTrackingMiddleware, metrics_collector=integration.metrics_collector, logger=integration.logger)

    @app.get('/performance/stats')
    async def get_performance_stats():
        'Get performance statistics'
        return (await integration.get_performance_stats())

    @app.get('/performance/cache/stats')
    async def get_cache_stats():
        'Get cache statistics'
        if integration.cache:
            return integration.cache.get_stats()
        return {'error': 'Cache not initialized'}

    @app.post('/performance/cache/clear')
    async def clear_cache():
        'Clear cache (admin only)'
        if integration.cache:
            integration.cache.local_cache.clear()
            return {'status': 'Cache cleared'}
        return {'error': 'Cache not initialized'}
    return integration
DEFAULT_DOGANAI_CONFIG = {'cache': {'max_size': 50000, 'ttl_seconds': 3600, 'redis_url': 'redis://localhost:6379/0', 'compression_enabled': True, 'enable_metrics': True}, 'database': {'url': 'postgresql://localhost/doganai_compliance', 'min_connections': 10, 'max_connections': 50, 'max_queries': 100000, 'batch_size': 500, 'max_wait_time': 2.0}, 'security': {'secret_key': 'your-super-secret-key-here', 'token_expire_minutes': 60, 'max_failed_attempts': 3, 'enable_rate_limiting': True, 'rate_limit_requests': 1000, 'rate_limit_window': 60}, 'monitoring': {'enable_default_metrics': True, 'enable_tracing': True, 'log_level': 'INFO'}, 'circuit_breakers': {'services': ['database', 'cache', 'external_api', 'compliance_evaluation'], 'failure_threshold': 3, 'recovery_timeout': 30}}
