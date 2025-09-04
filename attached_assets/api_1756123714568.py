
from fastapi import FastAPI, HTTPException, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os, json, glob, logging, time, uuid
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from .services.compliance import evaluate, ComplianceError
from .settings import settings
from .health import get_health_checker
logging.basicConfig(level=getattr(logging, settings.logging.level.upper()), format=settings.logging.format)
logger = logging.getLogger('engine.api')
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency in seconds', ['method', 'path', 'status'])
app = FastAPI(title=settings.app_name, version=settings.app_version, description='KSA Compliance and CX Operations API', docs_url='/docs', redoc_url='/redoc')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.middleware('http')
async def add_request_id_and_metrics(request: Request, call_next):
    start = time.time()
    req_id = (request.headers.get('X-Request-ID') or str(uuid.uuid4()))
    response = None
    try:
        response = (await call_next(request))
        return response
    except Exception as e:
        logger.error(f'Unhandled error in request {req_id}: {str(e)}')
        raise
    finally:
        status_code = str((response.status_code if response else 500))
        path = request.url.path
        method = request.method
        REQUEST_COUNT.labels(method=method, path=path, status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, path=path, status=status_code).observe((time.time() - start))
        if (response is not None):
            response.headers['X-Request-ID'] = req_id
            response.headers['X-Timestamp'] = settings.get_current_time().isoformat()

class EvaluateIn(BaseModel):
    mapping: str = Field(..., min_length=1, description='Mapping name to evaluate')

class EvaluateOut(BaseModel):
    mapping: str
    policy: str
    status: str
    required: List[str]
    provided: List[str]
    missing: List[str]
    vendors: List[dict]
    hash: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: str

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unhandled exception: {str(exc)}', exc_info=True)
    return JSONResponse(status_code=500, content=ErrorResponse(detail='Internal server error', error_code='INTERNAL_ERROR', timestamp=settings.get_current_time().isoformat()).dict())

def _list_mapping_names() -> List[str]:
    try:
        files = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'mappings', '*.yaml'))
        return [os.path.splitext(os.path.basename(f))[0] for f in files]
    except Exception as e:
        logger.error(f'Error listing mappings: {str(e)}')
        return []

@app.post('/evaluate', response_model=EvaluateOut, status_code=status.HTTP_200_OK)
def api_evaluate(data: EvaluateIn):
    try:
        names = _list_mapping_names()
        if (data.mapping not in names):
            raise HTTPException(status_code=404, detail=f"Mapping '{data.mapping}' not found. Available: {', '.join(names)}")
        res = evaluate(data.mapping)
        logger.info('evaluate mapping=%s status=%s', data.mapping, res.get('status'))
        return res
    except HTTPException:
        raise
    except ComplianceError as e:
        logger.error(f'Compliance evaluation error: {str(e)}')
        raise HTTPException(status_code=400, detail=f'Compliance error: {str(e)}')
    except Exception as e:
        logger.error(f'Unexpected error in evaluate: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error during evaluation')

@app.get('/mappings', response_model=List[str])
def list_mappings():
    return _list_mapping_names()

@app.get('/benchmarks')
def get_benchmarks():
    try:
        path = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'sector_kpis_2024_2025.json')
        if (not os.path.exists(path)):
            raise HTTPException(status_code=404, detail='Benchmarks file not found')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in benchmarks file: {str(e)}')
        raise HTTPException(status_code=500, detail='Invalid benchmarks data format')
    except Exception as e:
        logger.error(f'Error loading benchmarks: {str(e)}')
        raise HTTPException(status_code=500, detail='Error loading benchmarks')

@app.get('/health', response_model=HealthResponse)
def health():
    return HealthResponse(status='ok', timestamp=settings.get_current_time().isoformat(), version=settings.app_version)

@app.get('/health/detailed')
def detailed_health():
    'Comprehensive health check endpoint'
    health_checker = get_health_checker()
    return health_checker.run_all_checks()

@app.get('/version')
def version():
    return {'name': settings.app_name, 'version': settings.app_version, 'timestamp': settings.get_current_time().isoformat(), 'timezone_config': {'application_timezone': settings.timezone.application_timezone, 'display_timezone': settings.timezone.display_timezone, 'force_utc': settings.timezone.force_utc}}

@app.get('/metrics', response_class=Response)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
