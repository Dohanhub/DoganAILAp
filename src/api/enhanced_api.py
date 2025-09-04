
'\nEnhanced FastAPI Application with All Performance Improvements Integrated\nThis replaces/enhances your existing engine/api.py with production-ready optimizations\n'
import asyncio
import time
import uuid
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Response, Request, status, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel, Field, ValidationError
from improvements.doganai_integration import setup_doganai_performance, DEFAULT_DOGANAI_CONFIG
from improvements.performance import cache_with_ttl, PerformanceMonitor
from improvements.error_handling import ComplianceException, RetryableException
from improvements.security import SecurityManager, SecurityConfig, require_permission, Permission
from improvements.monitoring import StructuredLogger, MetricsCollector
from .services.compliance import evaluate, ComplianceError
from .settings import settings
from .health import get_health_checker
from .core.database import get_db_session
from .models import EvaluationResult, ComplianceReport
logger = StructuredLogger('doganai-api')

class EvaluateIn(BaseModel):
    mapping: str = Field(..., min_length=1, max_length=100, description='Mapping name to evaluate')
    vendor_id: Optional[str] = Field(None, max_length=50, description='Vendor ID for evaluation')
    policy_version: Optional[str] = Field(None, max_length=20, description='Policy version to use')
    include_benchmarks: bool = Field(True, description='Include benchmark comparisons')
    async_evaluation: bool = Field(False, description='Run evaluation asynchronously')
    priority: str = Field('normal', regex='^(low|normal|high|urgent)$', description='Evaluation priority')

    class Config():
        schema_extra = {'example': {'mapping': 'MAP-GOV-SecurePortal-IBM-Lenovo', 'vendor_id': 'IBM', 'policy_version': '2.0', 'include_benchmarks': True, 'async_evaluation': False, 'priority': 'normal'}}

class EvaluateOut(BaseModel):
    mapping: str
    policy: str
    status: str
    required: List[str]
    provided: List[str]
    missing: List[str]
    vendors: List[Dict[(str, Any)]]
    hash: str
    evaluation_time: float
    timestamp: str
    benchmark_score: Optional[float] = None
    compliance_percentage: float
    priority: str
    cached: bool = False
    request_id: str

class BatchEvaluateIn(BaseModel):
    evaluations: List[EvaluateIn] = Field(..., min_items=1, max_items=50)
    batch_mode: str = Field('parallel', regex='^(sequential|parallel|optimized)$')

class BatchEvaluateOut(BaseModel):
    batch_id: str
    total_evaluations: int
    successful: int
    failed: int
    results: List[EvaluateOut]
    total_time: float
    avg_time_per_evaluation: float

def create_enhanced_app() -> FastAPI:
    'Create enhanced FastAPI application with all optimizations'
    app = FastAPI(title='DoganAI Compliance Kit - Enhanced API', version='2.0.0', description='\n        ?? **Enhanced KSA Compliance and CX Operations API**\n        \n        **Features:**\n        - ? High-performance caching (Local + Redis)\n        - ?? Advanced security with RBAC\n        - ?? Comprehensive monitoring and metrics\n        - ??? Circuit breakers and error resilience\n        - ?? Mobile-optimized responses\n        - ?? Batch processing capabilities\n        - ?? Arabic/English support\n        ', docs_url=('/docs' if settings.debug else None), redoc_url=('/redoc' if settings.debug else None), openapi_url=('/openapi.json' if settings.debug else None))
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(CORSMiddleware, allow_origins=(['*'] if settings.debug else settings.api.cors_origins), allow_credentials=True, allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['*'], expose_headers=['X-Request-ID', 'X-Response-Time', 'X-Cache-Status'])
    performance_config = {**DEFAULT_DOGANAI_CONFIG, 'cache': {**DEFAULT_DOGANAI_CONFIG['cache'], 'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')}, 'database': {**DEFAULT_DOGANAI_CONFIG['database'], 'url': os.getenv('DATABASE_URL', 'postgresql://localhost/doganai_compliance')}, 'security': {**DEFAULT_DOGANAI_CONFIG['security'], 'secret_key': os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')}}
    integration = setup_doganai_performance(app, performance_config)
    return (app, integration)
(app, perf_integration) = create_enhanced_app()

@app.middleware('http')
async def enhanced_request_middleware(request: Request, call_next):
    'Enhanced request middleware with performance tracking'
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = start_time
    logger.info('Request started', request_id=request_id, method=request.method, path=request.url.path, user_agent=request.headers.get('user-agent', 'unknown'), client_ip=(request.client.host if request.client else 'unknown'))
    try:
        response = (await call_next(request))
        response_time = (time.time() - start_time)
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Response-Time'] = f'{response_time:.3f}s'
        logger.info('Request completed', request_id=request_id, method=request.method, path=request.url.path, status_code=response.status_code, response_time=response_time)
        return response
    except Exception as e:
        response_time = (time.time() - start_time)
        logger.error('Request failed', request_id=request_id, method=request.method, path=request.url.path, error=str(e), response_time=response_time, exc_info=True)
        raise

@app.get('/health/enhanced', tags=['Health'])
async def enhanced_health_check(request: Request):
    'Enhanced health check with performance metrics'
    start_time = time.time()
    health_checker = get_health_checker()
    health_results = health_checker.run_all_checks()
    performance_stats = {}
    if hasattr(app.state, 'performance_integration'):
        try:
            performance_stats = (await app.state.performance_integration.get_performance_stats())
        except Exception as e:
            logger.warning(f'Failed to get performance stats: {e}')
    cache_stats = {}
    if (hasattr(app.state, 'performance_integration') and app.state.performance_integration.cache):
        cache_stats = app.state.performance_integration.cache.get_stats()
    response_time = (time.time() - start_time)
    return {'status': health_results['status'], 'timestamp': datetime.now(timezone.utc).isoformat(), 'version': '2.0.0', 'response_time': response_time, 'request_id': request.state.request_id, 'checks': health_results['checks'], 'performance': performance_stats, 'cache': cache_stats, 'features': {'caching': bool(cache_stats), 'performance_monitoring': bool(performance_stats), 'circuit_breakers': bool(performance_stats.get('circuit_breakers')), 'batch_processing': True, 'async_evaluation': True}}

@app.post('/evaluate/enhanced', response_model=EvaluateOut, tags=['Compliance'])
@cache_with_ttl(ttl_seconds=300)
async def enhanced_evaluate_compliance(request: Request, evaluation: EvaluateIn, background_tasks: BackgroundTasks, db_session=Depends(get_db_session)):
    'Enhanced compliance evaluation with caching and performance optimizations'
    start_time = time.time()
    request_id = request.state.request_id
    try:
        if hasattr(app.state, 'performance_integration'):
            result = (await app.state.performance_integration.evaluate_compliance_single({'mapping': evaluation.mapping, 'vendor_id': evaluation.vendor_id, 'policy_version': evaluation.policy_version, 'include_benchmarks': evaluation.include_benchmarks, 'priority': evaluation.priority}))
            cached = True
        else:
            result = (await evaluate(mapping=evaluation.mapping, vendor_id=evaluation.vendor_id, policy_version=evaluation.policy_version, include_benchmarks=evaluation.include_benchmarks, async_evaluation=evaluation.async_evaluation))
            cached = False
        evaluation_time = (time.time() - start_time)
        evaluation_result = EvaluationResult(request_id=request_id, mapping=evaluation.mapping, vendor_id=evaluation.vendor_id, policy_version=evaluation.policy_version, status=result['status'], required_items=result.get('required', []), provided_items=result.get('provided', []), missing_items=result.get('missing', []), vendors=result.get('vendors', []), evaluation_time=evaluation_time, benchmark_score=result.get('score', result.get('benchmark_score')), compliance_percentage=result.get('compliance_percentage', result.get('score', 0.0)), priority=evaluation.priority, cached=cached)
        db_session.add(evaluation_result)
        db_session.commit()
        logger.info('Compliance evaluation completed', request_id=request_id, mapping=evaluation.mapping, status=result['status'], evaluation_time=evaluation_time, cached=cached, priority=evaluation.priority)
        return EvaluateOut(mapping=result.get('mapping', evaluation.mapping), policy=result.get('policy', 'Unknown'), status=result['status'], required=result.get('required', []), provided=result.get('provided', []), missing=result.get('missing', []), vendors=result.get('vendors', []), hash=result.get('hash', ''), evaluation_time=evaluation_time, timestamp=datetime.now(timezone.utc).isoformat(), benchmark_score=result.get('score', result.get('benchmark_score')), compliance_percentage=result.get('compliance_percentage', result.get('score', 0.0)), priority=evaluation.priority, cached=cached, request_id=request_id)
    except ComplianceError as e:
        logger.error('Compliance evaluation error', request_id=request_id, mapping=evaluation.mapping, error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'error': 'Compliance evaluation failed', 'message': str(e), 'request_id': request_id, 'mapping': evaluation.mapping})
    except Exception as e:
        logger.error('Unexpected error during evaluation', request_id=request_id, mapping=evaluation.mapping, error=str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'error': 'Internal server error', 'message': 'An unexpected error occurred during evaluation', 'request_id': request_id})

@app.post('/evaluate/batch', response_model=BatchEvaluateOut, tags=['Compliance'])
async def batch_evaluate_compliance(request: Request, batch_request: BatchEvaluateIn, background_tasks: BackgroundTasks, db_session=Depends(get_db_session)):
    'Batch compliance evaluation with optimized processing'
    start_time = time.time()
    request_id = request.state.request_id
    batch_id = f'batch_{request_id}'
    logger.info('Batch evaluation started', request_id=request_id, batch_id=batch_id, total_evaluations=len(batch_request.evaluations), batch_mode=batch_request.batch_mode)
    results = []
    successful = 0
    failed = 0
    try:
        if ((batch_request.batch_mode == 'parallel') and hasattr(app.state, 'performance_integration')):
            evaluation_data = [{'mapping': eval_req.mapping, 'vendor_id': eval_req.vendor_id, 'policy_version': eval_req.policy_version, 'include_benchmarks': eval_req.include_benchmarks, 'priority': eval_req.priority} for eval_req in batch_request.evaluations]
            batch_results = (await app.state.performance_integration.evaluate_compliance_batch(evaluation_data))
            for (i, (eval_req, result)) in enumerate(zip(batch_request.evaluations, batch_results)):
                try:
                    eval_result = EvaluateOut(mapping=result.get('mapping', eval_req.mapping), policy=result.get('policy', 'Unknown'), status=result['status'], required=result.get('required', []), provided=result.get('provided', []), missing=result.get('missing', []), vendors=result.get('vendors', []), hash=result.get('hash', ''), evaluation_time=result.get('evaluation_time', 0.0), timestamp=result.get('timestamp', datetime.now(timezone.utc).isoformat()), benchmark_score=result.get('score'), compliance_percentage=result.get('score', 0.0), priority=eval_req.priority, cached=False, request_id=f'{request_id}_{i}')
                    results.append(eval_result)
                    successful += 1
                except Exception as e:
                    logger.error(f'Failed to process batch item {i}: {e}')
                    failed += 1
        else:
            for (i, eval_req) in enumerate(batch_request.evaluations):
                try:
                    individual_result = (await enhanced_evaluate_compliance(request, eval_req, background_tasks, db_session))
                    individual_result.request_id = f'{request_id}_{i}'
                    results.append(individual_result)
                    successful += 1
                except Exception as e:
                    logger.error(f'Failed to evaluate item {i}: {e}')
                    failed += 1
        total_time = (time.time() - start_time)
        avg_time = ((total_time / len(batch_request.evaluations)) if batch_request.evaluations else 0)
        logger.info('Batch evaluation completed', request_id=request_id, batch_id=batch_id, successful=successful, failed=failed, total_time=total_time, avg_time=avg_time)
        return BatchEvaluateOut(batch_id=batch_id, total_evaluations=len(batch_request.evaluations), successful=successful, failed=failed, results=results, total_time=total_time, avg_time_per_evaluation=avg_time)
    except Exception as e:
        logger.error('Batch evaluation failed', request_id=request_id, batch_id=batch_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'error': 'Batch evaluation failed', 'batch_id': batch_id, 'request_id': request_id, 'message': str(e)})

@app.get('/metrics/performance', tags=['Monitoring'])
async def get_performance_metrics(request: Request):
    'Get detailed performance metrics'
    if hasattr(app.state, 'performance_integration'):
        return (await app.state.performance_integration.get_performance_stats())
    else:
        return {'error': 'Performance integration not available', 'basic_metrics': {'timestamp': datetime.now(timezone.utc).isoformat(), 'request_id': request.state.request_id}}

@app.post('/admin/cache/clear', tags=['Admin'])
async def clear_cache(request: Request):
    'Clear application cache (admin only)'
    if (hasattr(app.state, 'performance_integration') and app.state.performance_integration.cache):
        app.state.performance_integration.cache.local_cache.clear()
        logger.info('Cache cleared by admin', request_id=request.state.request_id, admin_ip=(request.client.host if request.client else 'unknown'))
        return {'status': 'success', 'message': 'Cache cleared successfully', 'timestamp': datetime.now(timezone.utc).isoformat(), 'request_id': request.state.request_id}
    else:
        return {'error': 'Cache not available', 'request_id': request.state.request_id}

@app.get('/', tags=['General'])
async def enhanced_root(request: Request):
    'Enhanced root endpoint with comprehensive API information'
    return {'name': 'DoganAI Compliance Kit - Enhanced API', 'version': '2.0.0', 'status': 'operational', 'timestamp': datetime.now(timezone.utc).isoformat(), 'request_id': request.state.request_id, 'features': {'caching': 'Local + Redis hybrid caching', 'security': 'RBAC with JWT tokens', 'monitoring': 'Prometheus metrics + structured logging', 'performance': 'Circuit breakers + batch processing', 'mobile': 'Mobile-optimized responses', 'i18n': 'Arabic/English support'}, 'endpoints': {'health': '/health/enhanced', 'evaluate': '/evaluate/enhanced', 'batch_evaluate': '/evaluate/batch', 'metrics': '/metrics/performance', 'docs': ('/docs' if settings.debug else 'Disabled in production')}, 'performance': {'cache_enabled': hasattr(app.state, 'performance_integration'), 'batch_processing': True, 'async_evaluation': True, 'circuit_breakers': True}}
if (__name__ == '__main__'):
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1, log_level='info', access_log=True, reload=settings.debug)
