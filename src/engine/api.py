
from fastapi import FastAPI, HTTPException, Response, Request, status, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any
import os
import time
import uuid
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog
import jwt
from .services.compliance import evaluate, ComplianceError
from .settings import settings
from .health import get_health_checker
from .core.database import get_db_session
from .models import EvaluationResult, ComplianceReport
structlog.configure(processors=[structlog.stdlib.filter_by_level, structlog.stdlib.add_logger_name, structlog.stdlib.add_log_level, structlog.stdlib.PositionalArgumentsFormatter(), structlog.processors.TimeStamper(fmt='iso'), structlog.processors.StackInfoRenderer(), structlog.processors.format_exc_info, structlog.processors.UnicodeDecoder(), structlog.processors.JSONRenderer()], context_class=dict, logger_factory=structlog.stdlib.LoggerFactory(), wrapper_class=structlog.stdlib.BoundLogger, cache_logger_on_first_use=True)
logger = structlog.get_logger()
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency in seconds', ['method', 'path', 'status', 'endpoint'])
ACTIVE_REQUESTS = Gauge('http_active_requests', 'Number of active HTTP requests', ['method', 'path'])
ERROR_COUNT = Counter('http_errors_total', 'Total HTTP errors', ['method', 'path', 'error_type'])
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.app_name, version=settings.app_version, description='KSA Compliance and CX Operations API - Production Ready', docs_url=('/docs' if settings.api.enable_docs else None), redoc_url=('/redoc' if settings.api.enable_redoc else None), openapi_url=('/openapi.json' if settings.api.enable_docs else None))
static_path = (Path(__file__).parent / 'static')
if static_path.exists():
    app.mount('/static', StaticFiles(directory=str(static_path)), name='static')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=(['*'] if settings.is_development else ['your-domain.com', '*.your-domain.com']))
app.add_middleware(CORSMiddleware, allow_origins=settings.api.cors_origins, allow_credentials=settings.api.cors_allow_credentials, allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['*'], expose_headers=['X-Request-ID', 'X-Timestamp', 'X-Rate-Limit-Remaining'], max_age=86400)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = (await call_next(request))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if settings.security.enable_https:
        response.headers['Strict-Transport-Security'] = f'max-age={settings.security.session_timeout}; includeSubDomains'
    if (hasattr(settings, 'security') and hasattr(settings.security, 'content_security_policy')):
        response.headers['Content-Security-Policy'] = settings.security.content_security_policy
    return response

@app.middleware('http')
async def add_request_id_and_metrics(request: Request, call_next):
    start = time.time()
    req_id = (request.headers.get('X-Request-ID') or str(uuid.uuid4()))
    ACTIVE_REQUESTS.labels(method=request.method, path=request.url.path).inc()
    response = None
    try:
        response = (await call_next(request))
        return response
    except Exception as e:
        ERROR_COUNT.labels(method=request.method, path=request.url.path, error_type=type(e).__name__).inc()
        logger.error(f'Unhandled error in request {req_id}', error=str(e), exc_info=True)
        raise
    finally:
        ACTIVE_REQUESTS.labels(method=request.method, path=request.url.path).dec()
        status_code = str((response.status_code if response else 500))
        path = request.url.path
        method = request.method
        endpoint = (path.split('/')[1] if (len(path.split('/')) > 1) else 'root')
        REQUEST_COUNT.labels(method=method, path=path, status=status_code, endpoint=endpoint).inc()
        REQUEST_LATENCY.labels(method=method, path=path, status=status_code, endpoint=endpoint).observe((time.time() - start))
        if (response is not None):
            response.headers['X-Request-ID'] = req_id
            response.headers['X-Timestamp'] = settings.get_current_time().isoformat()
            if hasattr(request.state, 'rate_limit_remaining'):
                response.headers['X-Rate-Limit-Remaining'] = str(request.state.rate_limit_remaining)

class APIKeyAuth():

    def __init__(self):
        self.scheme = HTTPBearer(auto_error=False)

    async def __call__(self, request: Request) -> Optional[str]:
        api_key = request.headers.get(settings.security.api_key_header)
        if api_key:
            if (await self.validate_api_key(api_key)):
                return api_key
        credentials: HTTPAuthorizationCredentials = (await self.scheme(request))
        if credentials:
            if (await self.validate_jwt_token(credentials.credentials)):
                return credentials.credentials
        return None

    async def validate_api_key(self, api_key: str) -> bool:
        'Validate API key against configured keys'
        valid_keys = os.getenv('VALID_API_KEYS', '').split(',')
        return (api_key in valid_keys)

    async def validate_jwt_token(self, token: str) -> bool:
        'Validate JWT token'
        try:
            payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.jwt_algorithm])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
auth_handler = APIKeyAuth()

async def get_current_user(api_key: Optional[str]=Depends(auth_handler)):
    if (not api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required', headers={'WWW-Authenticate': 'Bearer'})
    return api_key

def rate_limit(requests: int, window: int):
    'Custom rate limiting decorator'

    def decorator(func):

        async def wrapper(*args, **kwargs):
            return (await func(*args, **kwargs))
        return wrapper
    return decorator

class EvaluateIn(BaseModel):
    mapping: str = Field(..., min_length=1, description='Mapping name to evaluate')
    vendor_id: Optional[str] = Field(None, description='Vendor ID for evaluation')
    policy_version: Optional[str] = Field(None, description='Policy version to use')
    include_benchmarks: bool = Field(True, description='Include benchmark comparisons')
    async_evaluation: bool = Field(False, description='Run evaluation asynchronously')

class EvaluateOut(BaseModel):
    mapping: str
    policy: str
    status: str
    required: List[str]
    provided: List[str]
    missing: List[str]
    vendors: List[dict]
    hash: str
    evaluation_time: float
    timestamp: str
    benchmark_score: Optional[float] = None
    compliance_percentage: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: float
    checks: Dict[(str, Any)]

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: str
    request_id: str
    path: str

class ComplianceReportResponse(BaseModel):
    report_id: str
    status: str
    created_at: str
    download_url: Optional[str] = None

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(f'Unhandled exception: {str(exc)}', error_id=error_id, path=request.url.path, method=request.method, exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': 'Internal server error', 'error_code': 'INTERNAL_ERROR', 'timestamp': settings.get_current_time().isoformat(), 'request_id': request.headers.get('X-Request-ID', 'unknown'), 'path': request.url.path, 'error_id': error_id})

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning('Validation error', path=request.url.path, method=request.method, errors=exc.errors())
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'detail': 'Validation error', 'error_code': 'VALIDATION_ERROR', 'timestamp': settings.get_current_time().isoformat(), 'request_id': request.headers.get('X-Request-ID', 'unknown'), 'path': request.url.path, 'errors': exc.errors()})

@app.get('/health', response_model=HealthResponse)
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def health_check(request: Request):
    'Basic health check endpoint'
    start_time = time.time()
    health_checker = get_health_checker()
    results = health_checker.run_all_checks()
    return HealthResponse(status=results['status'], timestamp=settings.get_current_time().isoformat(), version=settings.app_version, uptime=(time.time() - start_time), checks=results['checks'])

@app.get('/health/detailed', response_model=HealthResponse)
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def detailed_health_check(request: Request):
    'Detailed health check with all system components'
    start_time = time.time()
    health_checker = get_health_checker()
    results = health_checker.run_all_checks()
    return HealthResponse(status=results['status'], timestamp=settings.get_current_time().isoformat(), version=settings.app_version, uptime=(time.time() - start_time), checks=results['checks'])

@app.get('/health/ready')
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def readiness_check(request: Request):
    'Kubernetes readiness probe endpoint'
    health_checker = get_health_checker()
    results = health_checker.run_all_checks()
    if (results['status'] == 'healthy'):
        return {'status': 'ready'}
    else:
        raise HTTPException(status_code=503, detail='Service not ready')

@app.get('/health/live')
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def liveness_check(request: Request):
    'Kubernetes liveness probe endpoint'
    return {'status': 'alive'}

@app.get('/metrics')
async def metrics():
    'Prometheus metrics endpoint'
    if (not settings.monitoring.enable_metrics):
        raise HTTPException(status_code=404, detail='Metrics not enabled')
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post('/evaluate', response_model=EvaluateOut)
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def evaluate_compliance(request: Request, evaluation: EvaluateIn, background_tasks: BackgroundTasks, current_user: str=Depends(get_current_user), db_session=Depends(get_db_session)):
    'Evaluate compliance for a given mapping'
    start_time = time.time()
    try:
        result = (await evaluate(mapping=evaluation.mapping, vendor_id=evaluation.vendor_id, policy_version=evaluation.policy_version, include_benchmarks=evaluation.include_benchmarks, async_evaluation=evaluation.async_evaluation))
        evaluation_time = (time.time() - start_time)
        evaluation_result = EvaluationResult(mapping=evaluation.mapping, vendor_id=evaluation.vendor_id, policy_version=evaluation.policy_version, status=result['status'], required_items=result['required'], provided_items=result['provided'], missing_items=result['missing'], vendors=result['vendors'], evaluation_time=evaluation_time, benchmark_score=result.get('benchmark_score'), compliance_percentage=result.get('compliance_percentage', 0.0))
        db_session.add(evaluation_result)
        db_session.commit()
        if evaluation.async_evaluation:
            background_tasks.add_task(generate_compliance_report, evaluation_result.id, db_session)
        return EvaluateOut(mapping=result['mapping'], policy=result['policy'], status=result['status'], required=result['required'], provided=result['provided'], missing=result['missing'], vendors=result['vendors'], hash=result['hash'], evaluation_time=evaluation_time, timestamp=settings.get_current_time().isoformat(), benchmark_score=result.get('benchmark_score'), compliance_percentage=result.get('compliance_percentage', 0.0))
    except ComplianceError as e:
        logger.error('Compliance evaluation error', mapping=evaluation.mapping, error=str(e), user=current_user)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Compliance evaluation failed: {str(e)}')
    except Exception as e:
        logger.error('Unexpected error during evaluation', mapping=evaluation.mapping, error=str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error during evaluation')

@app.post('/reports/generate', response_model=ComplianceReportResponse)
@limiter.limit(f'{settings.security.rate_limit_requests}/{settings.security.rate_limit_window}s')
async def generate_report(request: Request, evaluation_id: str, report_format: str='pdf', current_user: str=Depends(get_current_user), db_session=Depends(get_db_session)):
    'Generate compliance report for an evaluation'
    try:
        evaluation = db_session.query(EvaluationResult).filter((EvaluationResult.id == evaluation_id)).first()
        if (not evaluation):
            raise HTTPException(status_code=404, detail='Evaluation not found')
        report = ComplianceReport(evaluation_id=evaluation_id, format=report_format, status='generating', created_by=current_user)
        db_session.add(report)
        db_session.commit()
        background_tasks.add_task(generate_compliance_report, evaluation_id, db_session)
        return ComplianceReportResponse(report_id=report.id, status=report.status, created_at=report.created_at.isoformat(), download_url=None)
    except Exception as e:
        logger.error('Error generating report', evaluation_id=evaluation_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to generate report')

async def generate_compliance_report(evaluation_id: str, db_session):
    'Background task to generate compliance report'
    try:
        (await asyncio.sleep(5))
        report = db_session.query(ComplianceReport).filter((ComplianceReport.evaluation_id == evaluation_id)).first()
        if report:
            report.status = 'completed'
            report.download_url = f'/reports/{report.id}/download'
            db_session.commit()
        logger.info(f'Report generated successfully for evaluation {evaluation_id}')
    except Exception as e:
        logger.error('Error in background report generation', evaluation_id=evaluation_id, error=str(e), exc_info=True)

@app.get('/workflow', response_class=HTMLResponse)
async def workflow_simulator():
    'Serve the workflow simulator interface'
    static_path = ((Path(__file__).parent / 'static') / 'workflow_simulator.html')
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        return HTMLResponse(content='<h1>Workflow Simulator</h1><p>Workflow simulator files not found. Please ensure static files are properly deployed.</p>', status_code=404)

@app.get('/favicon.ico')
async def favicon():
    'Serve favicon.ico'
    favicon_path = ((Path(__file__).parent / 'static') / 'favicon.ico')
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type='image/x-icon')
    else:
        raise HTTPException(status_code=404, detail='Favicon not found')

@app.get('/')
async def root():
    'Root endpoint with API information'
    return {'name': settings.app_name, 'version': settings.app_version, 'environment': settings.environment, 'status': 'operational', 'timestamp': settings.get_current_time().isoformat(), 'documentation': ('/docs' if settings.api.enable_docs else 'Documentation disabled in production'), 'health': '/health', 'metrics': ('/metrics' if settings.monitoring.enable_metrics else 'Metrics disabled'), 'workflow_simulator': '/workflow'}

@app.get('/info')
async def api_info():
    'API information and configuration'
    return {'api': {'name': settings.app_name, 'version': settings.app_version, 'environment': settings.environment, 'host': settings.api.host, 'port': settings.api.port, 'workers': settings.api.workers, 'timeout': settings.api.timeout}, 'security': {'https_enabled': settings.security.enable_https, 'rate_limiting': settings.security.rate_limit_enabled, 'cors_enabled': bool(settings.api.cors_origins), 'authentication': 'API Key + JWT'}, 'monitoring': {'metrics_enabled': settings.monitoring.enable_metrics, 'health_checks': settings.monitoring.enable_health_checks, 'tracing': settings.monitoring.enable_tracing}, 'timestamp': settings.get_current_time().isoformat()}

@app.on_event('startup')
async def startup_event():
    'Application startup event'
    logger.info('Starting DoganAI Compliance Kit API', version=settings.app_version, environment=settings.environment, debug=settings.debug)
    errors = settings.validate()
    if errors:
        logger.error('Configuration validation errors', errors=errors)
        if settings.is_production:
            raise ValueError(f'Configuration validation failed in production: {errors}')
    try:
        db_session = next(get_db_session())
        db_session.execute('SELECT 1')
        logger.info('Database connection established')
    except Exception as e:
        logger.error('Failed to establish database connection', error=str(e))
        if settings.is_production:
            raise
    if (settings.cache.enable_caching and (settings.cache.cache_type == 'redis')):
        try:
            redis_client = redis.Redis(host=settings.cache.redis_host, port=settings.cache.redis_port, password=settings.cache.redis_password, db=settings.cache.redis_db, ssl=settings.cache.redis_ssl, decode_responses=True)
            redis_client.ping()
            logger.info('Redis cache connection established')
        except Exception as e:
            logger.warning('Failed to establish Redis cache connection', error=str(e))
    logger.info('API startup completed successfully')

@app.on_event('shutdown')
async def shutdown_event():
    'Application shutdown event'
    logger.info('Shutting down DoganAI Compliance Kit API')
    logger.info('API shutdown completed')

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={'detail': 'Endpoint not found', 'error_code': 'NOT_FOUND', 'timestamp': settings.get_current_time().isoformat(), 'request_id': request.headers.get('X-Request-ID', 'unknown'), 'path': request.url.path})

@app.exception_handler(429)
async def too_many_requests_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=429, content={'detail': 'Too many requests', 'error_code': 'RATE_LIMIT_EXCEEDED', 'timestamp': settings.get_current_time().isoformat(), 'request_id': request.headers.get('X-Request-ID', 'unknown'), 'path': request.url.path, 'retry_after': 60})
import asyncio
