
from fastapi import FastAPI, Request, HTTPException, Depends, status, UploadFile, File, Form
import inspect
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .database import get_db, SessionLocal, engine
from . import models
import socket
import time
from urllib.parse import urlparse, urljoin
import ipaddress
import json
import requests
try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None  # type: ignore
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST  # type: ignore
import logging
try:
    from pythonjsonlogger import jsonlogger  # type: ignore
except Exception:
    jsonlogger = None

# Optional OpenTelemetry tracing
try:
    from opentelemetry import trace  # type: ignore
    from opentelemetry.sdk.resources import Resource  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
    OTEL_AVAILABLE = True
except Exception:
    OTEL_AVAILABLE = False
from app.report_pdf import build_html, render_pdf
from .db import healthcheck as _db_health  # type: ignore
from .schemas import ValidateRequest, ValidateResponse  # type: ignore
from .services.validation import validate_vendor  # type: ignore
from .services.events import sse_stream  # type: ignore
from .services.monitor import monitor_loop  # type: ignore
from .services.engine import ComplianceEngine  # type: ignore
from .common.auth import verify_request  # type: ignore
from .services.health import HealthMonitor  # type: ignore
from fastapi import Request

load_dotenv()
# Secrets must be provided via environment. Accept JWT_SECRET alias. Do not use defaults in production.
_sk = os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET')
if not _sk or _sk.strip() in {'', 'your-secret-key-here', 'change-this-to-a-long-random-string'}:
    raise RuntimeError('SECRET_KEY is not configured. Set SECRET_KEY (or JWT_SECRET) environment variable.')
SECRET_KEY = _sk
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
app = FastAPI(title='Dogan AI Compliance MVP')

# Basic liveness/readiness for probes
@app.get('/health')
def health():
    return {"ok": True}
# CORS configuration via env var
allowed_origins = os.getenv('ALLOWED_ORIGINS')
origins = [o.strip() for o in allowed_origins.split(',')] if allowed_origins else ['*']
env_name = os.getenv('ENV', os.getenv('ENVIRONMENT', 'development')).lower()
if env_name == 'production':
    # Do not allow wildcard in production
    if not allowed_origins or any(x in {'*', "'*'"} for x in origins):
        raise RuntimeError('ALLOWED_ORIGINS must be set to explicit origins in production')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
# Trusted hosts (optional, recommended in production)
allowed_hosts = os.getenv('ALLOWED_HOSTS')
if allowed_hosts:
    hosts = [h.strip() for h in allowed_hosts.split(',') if h.strip()]
    if hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
# Enforce HTTPS redirect if configured
if os.getenv('FORCE_HTTPS', 'false').lower() in {'1','true','yes'}:
    app.add_middleware(HTTPSRedirectMiddleware)
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

# Structured logging (optional)
if os.getenv('JSON_LOGS', 'true').lower() in {'1','true','yes'} and jsonlogger is not None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

# Utilities
def _rand_hex(n: int = 24) -> str:
    import secrets
    return secrets.token_hex(n)

# --- Security helpers: API Key (optional) and rate limiting ---
API_KEY = os.getenv('API_KEY')

async def require_api_key(request: Request):
    # Enforce API key for all non-public endpoints
    if not API_KEY:
        raise HTTPException(status_code=401, detail='API key is required and not configured')
    provided = request.headers.get('X-API-Key')
    if provided != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')

from collections import defaultdict, deque
_RATE_STORE: Dict[str, deque] = defaultdict(deque)

def _redis_client():
    try:
        import redis  # type: ignore
        url = os.getenv('REDIS_URL')
        if url:
            return redis.from_url(url)
    except Exception:
        return None
    return None

def make_rate_limiter(limit: int = 60, window_seconds: int = 60):
    rc = _redis_client()

    async def _limiter(request: Request):
        key = f"rate:{request.client.host if request.client else 'unknown'}:{request.url.path}"
        if rc is not None:
            try:
                # Use atomic INCR with TTL
                current = rc.incr(key)
                if current == 1:
                    rc.expire(key, window_seconds)
                if current > limit:
                    raise HTTPException(status_code=429, detail='Rate limit exceeded')
                return
            except Exception:
                # Fallback to in-memory on Redis error
                pass
        # In-memory fallback (single-instance only)
        now = time.time()
        dq = _RATE_STORE[key]
        while dq and now - dq[0] > window_seconds:
            dq.popleft()
        if len(dq) >= limit:
            raise HTTPException(status_code=429, detail='Rate limit exceeded')
        dq.append(now)

    return _limiter

_rl = int(os.getenv('RATE_LIMIT', '60'))
_rw = int(os.getenv('RATE_WINDOW', '60'))
rate_limited = make_rate_limiter(limit=_rl, window_seconds=_rw)

# Current user dependency and roles (avoid early reference to get_current_user)
async def _dep_current_user(*args, **kwargs):
    # Lazy import to avoid import-time evaluation and circulars
    try:
        from .auth import get_current_user as _gcu  # preferred if modularized
    except Exception:
        from app.main import get_current_user as _gcu  # fallback to local
    if inspect.iscoroutinefunction(_gcu):
        return await _gcu(*args, **kwargs)
    return _gcu(*args, **kwargs)

async def current_user(user: models.User = Depends(_dep_current_user)):
    return user

def require_roles(*roles: str):
    async def _dep(user: models.User = Depends(_dep_current_user)):
        if roles and user.role not in roles:
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return _dep

# Optional tenant from header
async def tenant_from_api_key(request: Request, db: SessionLocal = Depends(get_db)):
    key = request.headers.get('X-Tenant-Key')
    if not key:
        return None
    try:
        from models import Tenant  # type: ignore
        return db.query(Tenant).filter(Tenant.api_key == key).first()
    except Exception:
        return None

# --- Prometheus metrics ---
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latency of HTTP requests', ['method', 'path'])

@app.middleware('http')
async def metrics_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    REQUEST_COUNT.labels(method=method, path=path, status=str(response.status_code)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)
    # Best-effort audit log with sampling and toggle to prevent DoS via floods
    try:
        if os.getenv('ENABLE_AUDIT_LOGGING', 'false').lower() in {'1','true','yes'}:
            import random
            sample = float(os.getenv('AUDIT_SAMPLE_RATE', '0.01'))
            if sample >= 1 or random.random() < max(0.0, min(1.0, sample)):
                from models import AuditLog  # type: ignore
                db = SessionLocal()
                ip = request.client.host if request.client else None
                user_email = request.headers.get('X-User-Email')
                db.add(AuditLog(user_email=user_email, method=method, path=path, status_code=int(response.status_code), ip=ip))
                db.commit()
    except Exception:
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass
    # Security headers
    try:
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        response.headers.setdefault('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        # HSTS if HTTPS enforced/expected
        if os.getenv('HSTS_ENABLED', 'true').lower() in {'1','true','yes'}:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    except Exception:
        pass
    return response

@app.get('/metrics')
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# DB health (specific)
@app.get('/health/db')
def db_health():
    return {"ok": bool(_db_health())}


@app.get('/health/services')
async def health_services():
    mon = HealthMonitor()
    db = await mon.check_service_health('db')
    # Additional services can be added here (gateway, integrations) when applicable
    ext = await mon.monitor_external_apis()
    return {"db": db, "external": ext}

# Strict readiness endpoint: validates DB connectivity, secrets and (optionally) Redis
@app.get('/ready')
def ready():
    # SECRET_KEY validated on import; API_KEY must be present
    if not os.getenv('API_KEY'):
        return JSONResponse(status_code=503, content={"ok": False, "error": "API_KEY not set"})
    # Database connectivity check
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        return JSONResponse(status_code=503, content={"ok": False, "error": f"db: {e}"})
    # Optional Redis check if configured
    rurl = os.getenv('REDIS_URL')
    if rurl:
        try:
            import redis  # type: ignore
            _r = redis.from_url(rurl, socket_timeout=2)
            _r.ping()
        except Exception as e:
            return JSONResponse(status_code=503, content={"ok": False, "error": f"redis: {e}"})
    # Production CORS sanity: should not be wildcard
    env_name = os.getenv('ENV', os.getenv('ENVIRONMENT', 'development')).lower()
    if env_name == 'production':
        allowed_origins = os.getenv('ALLOWED_ORIGINS')
        origins = [o.strip() for o in allowed_origins.split(',')] if allowed_origins else []
        if not origins or any(x in {'*', "'*'"} for x in origins):
            return JSONResponse(status_code=503, content={"ok": False, "error": "ALLOWED_ORIGINS invalid in production"})
    return {"ok": True}

# Validation API (MVP)
@app.post('/api/v1/validate', response_model=ValidateResponse)
async def api_validate(payload: ValidateRequest):
    res = await validate_vendor(payload.model_dump())
    return res

# SSE events stream (feature-flagged via FEATURE_SSE)
@app.get('/api/v1/events')
async def api_events():
    if os.getenv('FEATURE_SSE', 'true').lower() not in {'1','true','yes'}:
        raise HTTPException(status_code=404, detail='SSE disabled')
    return StreamingResponse(sse_stream(), media_type='text/event-stream')

# Compliance engine wiring (internal)
async def _internal_auth(request: Request):
    return await verify_request(request, 'compliance-engine')


@app.post('/api/v1/compliance/evaluate')
async def api_compliance_evaluate(payload: dict, _=Depends(_internal_auth)):
    return await ComplianceEngine().evaluate_compliance(payload)

# Version endpoint (for diagnostics)
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
VCS_REF = os.getenv('VCS_REF')
BUILD_DATE = os.getenv('BUILD_DATE')

@app.get('/version')
def version():
    return {"version": APP_VERSION, "vcs_ref": VCS_REF, "build_date": BUILD_DATE}

@app.get('/api/me')
async def me(current_user: models.User = Depends(_dep_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id,
        "is_superuser": getattr(current_user, 'is_superuser', False),
    }

@app.get('/api/diagnostics', dependencies=[Depends(require_api_key)])
def diagnostics():
    """Return a quick status summary for UI diagnostics."""
    report: Dict[str, Any] = {"ok": True, "checks": {}}
    db = SessionLocal()
    try:
        report["checks"]["users"] = db.query(models.User).count()
        report["checks"]["tenants"] = db.query(models.Tenant).count()
        report["checks"]["regulators"] = db.query(models.Regulator).count()
        report["checks"]["vendors"] = db.query(models.Vendor).count()
        report["checks"]["standards"] = db.query(models.ComplianceStandard).count()
        report["checks"]["controls"] = db.query(models.Control).count()
        report["checks"]["evidence"] = db.query(models.Evidence).count()
        # Optional mapping tables
        try:
            report["checks"]["vendor_regulator"] = db.query(models.VendorRegulator).count()
        except Exception:
            pass
        try:
            report["checks"]["vendor_tenant"] = db.query(models.VendorTenant).count()
        except Exception:
            pass
        try:
            report["checks"]["connectors"] = db.query(models.Connector).count()
        except Exception:
            pass
    except Exception as e:
        report["ok"] = False
        report["error"] = str(e)
    finally:
        db.close()
    return report

@app.get('/api/compliance/status/{standard_name}', dependencies=[Depends(require_api_key)])
def compliance_status(standard_name: str):
    """Return latest assessment status per control and overdue counts for a standard."""
    db = SessionLocal()
    try:
        std = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == standard_name).first()
        if not std:
            raise HTTPException(status_code=404, detail='Standard not found')
        controls = db.query(models.Control).filter(models.Control.standard_id == std.id).all()
        now = datetime.utcnow()
        items = []
        overdue = 0
        for c in controls:
            last = (
                db.query(models.Assessment)
                .filter(models.Assessment.control_id == c.id)
                .order_by(models.Assessment.assessed_at.desc())
                .first()
            )
            due = last.next_review_date if last and last.next_review_date else None
            if due and due < now:
                overdue += 1
            items.append({
                "control_id": c.control_id,
                "title": c.title,
                "status": (last.status if last else None),
                "assessed_at": (last.assessed_at.isoformat() if last and last.assessed_at else None),
                "next_review_date": (due.isoformat() if due else None),
                "overdue": bool(due and due < now),
            })
        return {"standard": standard_name, "total": len(controls), "overdue": overdue, "items": items}
    finally:
        db.close()

@app.post('/api/compliance/run/{standard_name}', dependencies=[Depends(require_api_key)])
def compliance_run(standard_name: str, db: SessionLocal = Depends(get_db)):
    """Create placeholder assessments for any controls missing an entry; returns counts.
    Intended to be called by scheduler to enforce on-time validation windows.
    """
    std = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == standard_name).first()
    if not std:
        raise HTTPException(status_code=404, detail='Standard not found')
    controls = db.query(models.Control).filter(models.Control.standard_id == std.id).all()
    created = 0
    for c in controls:
        last = (
            db.query(models.Assessment)
            .filter(models.Assessment.control_id == c.id)
            .order_by(models.Assessment.assessed_at.desc())
            .first()
        )
        if not last:
            a = models.Assessment(control_id=c.id, user_id=None, status='Not Started', assessed_at=datetime.utcnow(), next_review_date=datetime.utcnow()+timedelta(days=90))
            db.add(a)
            created += 1
    db.commit()
    return {"standard": standard_name, "created": created, "total_controls": len(controls)}

# Version endpoint (for diagnostics)
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
VCS_REF = os.getenv('VCS_REF')
BUILD_DATE = os.getenv('BUILD_DATE')

@app.get('/version')
def version():
    return {"version": APP_VERSION, "vcs_ref": VCS_REF, "build_date": BUILD_DATE}

# --- RBAC helpers ---
def role_required(*roles: str):
    async def _dep(user: models.User = Depends(lambda token=Depends(oauth2_scheme), db=Depends(get_db): get_current_user(token, db))):  # type: ignore
        if user is None or (roles and user.role not in roles):
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return _dep

# --- Tenant API key support (per-tenant optional header) ---
async def tenant_from_api_key(request: Request, db: SessionLocal = Depends(get_db)):
    key = request.headers.get('X-Tenant-Key')
    if not key:
        return None
    try:
        from models import Tenant  # type: ignore
        return db.query(Tenant).filter(Tenant.api_key == key).first()
    except Exception:
        return None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserInDB(UserCreate):
    hashed_password: str

class ComplianceCheck(BaseModel):
    standard: str
    control_id: str

class ComplianceResult(BaseModel):
    standard: str
    control_id: str
    status: str
    details: Dict[str, Any]

class PingRequest(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    timeout: float = 3.0

class ScrapeRequest(BaseModel):
    url: str
    same_domain_only: bool = True
    max_pages: int = 1
    timeout: float = 5.0

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    return db.query(models.User).filter((models.User.email == email)).first()

def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if ((not user) or (not verify_password(password, user.hashed_password))):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = (datetime.utcnow() + expires_delta)
    else:
        expire = (datetime.utcnow() + timedelta(minutes=15))
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def _get_claim(obj: Any, path: str) -> Any:
    try:
        cur = obj
        for part in path.split('.'):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur
    except Exception:
        return None

_jwks_cache: Dict[str, Any] = {}
_jwks_cache_at: float = 0.0

def _load_jwks() -> Optional[Dict[str, Any]]:
    url = os.getenv('OIDC_JWKS_URL')
    if not url:
        return None
    global _jwks_cache, _jwks_cache_at
    now = time.time()
    if _jwks_cache and now - _jwks_cache_at < 300:
        return _jwks_cache
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        _jwks_cache = r.json()
        _jwks_cache_at = now
        return _jwks_cache
    except Exception:
        return _jwks_cache or None

def _try_verify_oidc(token: str) -> Optional[Dict[str, Any]]:
    issuer = os.getenv('OIDC_ISSUER')
    audience = os.getenv('OIDC_AUDIENCE')
    if not issuer:
        return None
    jwks = _load_jwks()
    if not jwks:
        return None
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        alg = header.get('alg', 'RS256')
        allowed_algs = [a.strip() for a in os.getenv('OIDC_ALLOWED_ALGS', 'RS256').split(',') if a.strip()]
        if alg not in allowed_algs:
            return None
        keys = jwks.get('keys') if isinstance(jwks, dict) else None
        if not keys:
            return None
        key_dict = None
        if kid:
            key_dict = next((k for k in keys if k.get('kid') == kid), None)
        if key_dict is None and len(keys) == 1:
            key_dict = keys[0]
        if not key_dict:
            return None
        # Build public key from JWK
        if alg.startswith('RS'):
            from jose.utils import base64url_decode  # type: ignore
            from jose.backends.cryptography_backend import CryptographyRSAKey  # type: ignore
            public_key = CryptographyRSAKey(key_dict).to_pem()
        elif alg.startswith('ES'):
            from jose.backends.cryptography_backend import CryptographyECKey  # type: ignore
            public_key = CryptographyECKey(key_dict).to_pem()
        else:
            return None
        allow_no_aud = os.getenv('OIDC_ALLOW_NO_AUDIENCE', 'false').lower() in {'1','true','yes'}
        if not audience and not allow_no_aud:
            return None
        options = {"verify_aud": True, "require_iat": False} if audience else {"verify_aud": False, "require_iat": False}
        data = jwt.decode(token, public_key, algorithms=[alg], audience=audience, issuer=issuer, options=options)
        return data
    except Exception:
        return None

async def get_current_user(token: str=Depends(oauth2_scheme), db: SessionLocal=Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    # Try OIDC first if configured
    data = _try_verify_oidc(token)
    email: Optional[str] = None
    role: Optional[str] = None
    if data:
        email_claim = os.getenv('OIDC_EMAIL_CLAIM', 'email')
        roles_claim = os.getenv('OIDC_ROLES_CLAIM', 'roles')
        tenant_claim = os.getenv('OIDC_TENANT_CLAIM')
        email = _get_claim(data, email_claim) or data.get('sub')
        roles_val = _get_claim(data, roles_claim)
        # Map roles with allowlist
        if isinstance(roles_val, list):
            rs = set([str(x).lower() for x in roles_val])
            allowed_roles = set([r.strip().lower() for r in os.getenv('ALLOWED_OIDC_ROLES', 'admin,auditor,user').split(',') if r.strip()])
            if 'admin' in rs and 'admin' in allowed_roles:
                role = 'admin'
            elif 'auditor' in rs and 'auditor' in allowed_roles:
                role = 'auditor'
            else:
                role = 'user' if 'user' in allowed_roles else None
        # Auto-provision user
        if email:
            user = get_user(db, email)
            if not user:
                user = models.User(email=email, hashed_password=get_password_hash(os.urandom(8).hex()), full_name=email.split('@')[0], role=role or 'user')
                # Optional tenant auto-create
                if tenant_claim:
                    tname = _get_claim(data, tenant_claim)
                    if tname:
                        from models import Tenant  # type: ignore
                        t = db.query(Tenant).filter(Tenant.name == tname).first()
                        if not t and os.getenv('AUTO_CREATE_TENANT', 'false').lower() in {'1','true','yes'}:
                            t = models.Tenant(name=str(tname))
                            db.add(t)
                            db.flush()
                        if t:
                            user.tenant_id = t.id
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        # If email missing, fall back to local
    # Fallback: local JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
        if (email is None):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email)
    if (user is None):
        raise credentials_exception
    return user

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends(), db: SessionLocal=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if (not user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password', headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/api/register', response_model=dict, dependencies=[Depends(rate_limited), Depends(require_csrf)])
async def register_user(user: UserCreate, db: SessionLocal=Depends(get_db)):
    # Avoid user enumeration: always return generic response
    existed = db.query(models.User).filter((models.User.email == user.email)).first() is not None
    if not existed:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    # Generic message regardless of prior existence
    return {'message': 'If eligible, you will receive further instructions via email.'}

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/api/compliance/check', response_model=ComplianceResult, dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def check_compliance(check: ComplianceCheck, current_user: models.User=Depends(_dep_current_user), db: SessionLocal=Depends(get_db)):
    'Check compliance for a specific standard and control'
    control = db.query(models.Control).join(models.ComplianceStandard).filter((models.ComplianceStandard.name == check.standard), (models.Control.control_id == check.control_id)).first()
    if (not control):
        raise HTTPException(status_code=404, detail='Control not found')
    details = {'title': control.title, 'description': (control.description or 'No description available'), 'is_mandatory': control.is_mandatory, 'last_checked': datetime.utcnow().isoformat()}
    # Optional: consult engine mapping if available (best-effort)
    try:
        import importlib
        engine_mod = importlib.import_module('src.core.engine.compliance')
        if hasattr(engine_mod, 'evaluate'):
            mapping_name = f"{check.standard}"
            engine_result = engine_mod.evaluate(mapping_name)
            # attempt to compute basic coverage/gaps if available
            summary: Dict[str, Any] = {}
            for k in ('policy_ref', 'coverage', 'gaps', 'vendors'):
                if isinstance(engine_result, dict) and k in engine_result:
                    summary[k] = engine_result.get(k)
            if summary:
                details['engine'] = {'mapping': mapping_name, 'summary': summary}
    except Exception:
        pass
    result = {'standard': check.standard, 'control_id': check.control_id, 'status': 'Compliant', 'details': details}
    assessment = models.Assessment(control_id=control.id, user_id=current_user.id, status=result['status'], assessed_at=datetime.utcnow(), next_review_date=(datetime.utcnow() + timedelta(days=90)))
    db.add(assessment)
    db.commit()
    return result

@app.get('/api/standards', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def list_standards(db: SessionLocal=Depends(get_db)):
    'List all available compliance standards'
    standards = db.query(models.ComplianceStandard).all()
    return [{'id': std.id, 'name': std.name, 'version': std.version} for std in standards]

@app.get('/api/controls/{standard_id}', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def list_controls(standard_id: int, db: SessionLocal=Depends(get_db)):
    'List all controls for a specific standard'
    controls = db.query(models.Control).filter((models.Control.standard_id == standard_id)).all()
    return [{'id': c.id, 'control_id': c.control_id, 'title': c.title} for c in controls]

@app.get('/api/reports/standard/{standard_name}', dependencies=[Depends(require_api_key)])
async def report_by_standard(standard_name: str, db: SessionLocal = Depends(get_db)):
    from sqlalchemy import func  # type: ignore
    # counts of controls and recent assessments by status
    std = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == standard_name).first()
    if not std:
        raise HTTPException(status_code=404, detail='Standard not found')
    controls_count = db.query(func.count(models.Control.id)).filter(models.Control.standard_id == std.id).scalar() or 0
    status_counts = (
        db.query(models.Assessment.status, func.count(models.Assessment.id))
        .join(models.Control, models.Assessment.control_id == models.Control.id)
        .filter(models.Control.standard_id == std.id)
        .group_by(models.Assessment.status)
        .all()
    )
    status_map = {k: v for k, v in status_counts}
    return {"standard": standard_name, "controls": controls_count, "assessments": status_map}

@app.get('/api/reports/standard/{standard_name}/export', dependencies=[Depends(require_api_key)])
async def export_report_by_standard(standard_name: str, fmt: str = 'csv', db: SessionLocal = Depends(get_db)):
    from sqlalchemy import func  # type: ignore
    import io, csv, json
    std = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == standard_name).first()
    if not std:
        raise HTTPException(status_code=404, detail='Standard not found')
    rows = (
        db.query(models.Control.control_id, models.Control.title, models.Assessment.status, models.Assessment.assessed_at)
        .outerjoin(models.Assessment, models.Assessment.control_id == models.Control.id)
        .filter(models.Control.standard_id == std.id)
        .all()
    )
    if fmt.lower() == 'csv':
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['control_id','title','status','assessed_at'])
        for cid, title, status, at in rows:
            w.writerow([cid, title, status or '', at.isoformat() if at else ''])
        return Response(content=buf.getvalue(), media_type='text/csv')
    elif fmt.lower() == 'json':
        data = [
            {"control_id": cid, "title": title, "status": status, "assessed_at": (at.isoformat() if at else None)}
            for cid, title, status, at in rows
        ]
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=400, detail='Unsupported format')

@app.get('/api/reports/standard/{standard_name}/pdf', dependencies=[Depends(require_api_key)])
async def export_report_pdf(standard_name: str, db: SessionLocal = Depends(get_db)):
    status = compliance_status(standard_name)
    html = build_html(standard_name, status['items'])
    pdf = render_pdf(html)
    if pdf is None:
        return HTMLResponse(content=html)
    return Response(content=pdf, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="report_{standard_name}.pdf"'})

@app.post('/api/evidence/upload', dependencies=[Depends(require_api_key), Depends(rate_limited), Depends(require_csrf)])
async def upload_evidence(
    file: UploadFile = File(...),
    control_id: int | None = Form(default=None),
    tenant = Depends(tenant_from_api_key),
    user: models.User | None = Depends(lambda: None)
):
    """Accept an evidence file and store it under UPLOAD_DIR; returns path and metadata."""
    upload_dir = os.getenv('UPLOAD_DIR', 'app/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    # Validate filename and content-type
    base = os.path.basename(file.filename or '')
    if not base:
        raise HTTPException(status_code=400, detail='Missing filename')
    name, ext = os.path.splitext(base)
    import mimetypes, hashlib
    allowed_types = {t.strip().lower() for t in os.getenv('UPLOAD_ALLOWED_TYPES', 'application/pdf,image/png,image/jpeg,text/plain,application/zip').split(',') if t.strip()}
    content_type = (file.content_type or mimetypes.guess_type(base)[0] or '').lower()
    if content_type and allowed_types and content_type not in allowed_types:
        raise HTTPException(status_code=400, detail='Unsupported content type')
    # Limits
    max_bytes = int(os.getenv('UPLOAD_MAX_BYTES', '10485760'))  # 10 MiB default
    # Ensure unique safe filename
    from datetime import datetime as _dt
    stamp = _dt.utcnow().strftime('%Y%m%d%H%M%S%f')
    safe_stem = ''.join(c for c in name if c.isalnum() or c in ('-', '_'))[:80] or 'file'
    safe_ext = ''.join(c for c in ext if c.isalnum() or c in ('.',))
    safe_name = f"{safe_stem}_{stamp}{safe_ext}"
    dest_path = os.path.join(upload_dir, safe_name)
    # Stream to disk and compute hash
    hasher = hashlib.sha256()
    total = 0
    try:
        with open(dest_path, 'wb') as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=413, detail='File too large')
                hasher.update(chunk)
                out.write(chunk)
    finally:
        await file.close()
    sha256 = hasher.hexdigest()
    storage = 'local'
    # Optional malware scan (clamd) best-effort
    try:
        if os.getenv('ENABLE_CLAMAV_SCAN', 'false').lower() in {'1','true','yes'}:
            import clamd  # type: ignore
            cd = clamd.ClamdNetworkSocket()
            scan_res = cd.scan(dest_path) or {}
            status = list(scan_res.values())[0][0] if scan_res else 'OK'
            if status != 'OK':
                # Remove infected file
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
                raise HTTPException(status_code=400, detail='Malware detected')
    except Exception:
        # Log-only; do not fail if scanner unavailable
        pass
    # Persist record if DB model exists
    try:
        from models import Evidence  # type: ignore
        db = SessionLocal()
        ev = Evidence(
            user_id=None,
            control_id=control_id,
            tenant_id=(tenant.id if tenant else None),
            original_filename=base,
            filename=safe_name,
            path=dest_path,
            size=len(content),
            content_type=content_type,
            sha256=sha256,
            storage=storage,
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        db.close()
        return {"id": ev.id, "filename": safe_name, "size": total, "sha256": sha256, "storage": storage}
    except Exception:
        return {"filename": safe_name, "size": total, "sha256": sha256}

@app.get('/api/evidence', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def list_evidence(tenant = Depends(tenant_from_api_key)):
    from models import Evidence  # type: ignore
    db = SessionLocal()
    try:
        q = db.query(Evidence)
        if tenant:
            q = q.filter(Evidence.tenant_id == tenant.id)
        items = q.order_by(Evidence.uploaded_at.desc()).limit(200).all()
        return [
            {"id": e.id, "filename": e.filename, "size": e.size, "uploaded_at": e.uploaded_at.isoformat(), "storage": getattr(e, 'storage', 'local')}
            for e in items
        ]
    finally:
        db.close()

@app.get('/api/evidence/export', dependencies=[Depends(require_api_key)])
async def export_evidence(fmt: str = 'csv', tenant = Depends(tenant_from_api_key)):
    from models import Evidence  # type: ignore
    import io, csv, json
    db = SessionLocal()
    try:
        q = db.query(Evidence)
        if tenant:
            q = q.filter(Evidence.tenant_id == tenant.id)
        items = q.order_by(Evidence.uploaded_at.desc()).limit(1000).all()
        if fmt.lower() == 'csv':
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(['id','filename','original_filename','size','content_type','sha256','storage','uploaded_at'])
            for e in items:
                w.writerow([e.id, e.filename, e.original_filename or '', e.size, e.content_type or '', e.sha256 or '', e.storage, e.uploaded_at.isoformat()])
            return Response(content=buf.getvalue(), media_type='text/csv')
        elif fmt.lower() == 'json':
            data = [
                {"id": e.id, "filename": e.filename, "original_filename": e.original_filename, "size": e.size, "content_type": e.content_type, "sha256": e.sha256, "storage": e.storage, "uploaded_at": e.uploaded_at.isoformat()}
                for e in items
            ]
            return JSONResponse(content=data)
        else:
            raise HTTPException(status_code=400, detail='Unsupported format')
    finally:
        db.close()

@app.get('/api/evidence/{evidence_id}/download', dependencies=[Depends(require_api_key)])
async def download_evidence(evidence_id: int, db: SessionLocal = Depends(get_db)):
    from models import Evidence  # type: ignore
    e = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not e:
        raise HTTPException(status_code=404, detail='Not found')
    if e.storage == 'local':
        from fastapi.responses import FileResponse
        return FileResponse(path=e.path, media_type=e.content_type or 'application/octet-stream', filename=e.original_filename or e.filename)
    elif e.storage == 's3':
        try:
            import boto3  # type: ignore
            bucket = os.getenv('AWS_S3_BUCKET')
            s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
            url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': e.filename}, ExpiresIn=300)
            return {"presigned_url": url}
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f'Failed to generate presigned URL: {ex}')
    else:
        raise HTTPException(status_code=500, detail='Unknown storage type')

@app.get('/api/regulators', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key)])
async def list_regulators():
    from models import Regulator  # type: ignore
    db = SessionLocal()
    try:
        regs = db.query(Regulator).order_by(Regulator.name.asc()).all()
        return [
            {"id": r.id, "name": r.name, "country": r.country, "sector": r.sector, "website": r.website}
            for r in regs
        ]
    finally:
        db.close()

@app.get('/api/vendors', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key)])
async def list_vendors():
    from models import Vendor  # type: ignore
    db = SessionLocal()
    try:
        v = db.query(Vendor).order_by(Vendor.name.asc()).all()
        return [
            {"id": i.id, "name": i.name, "category": i.category, "website": i.website, "contact_email": i.contact_email}
            for i in v
        ]
    finally:
        db.close()

@app.post('/api/users/assign-role', dependencies=[Depends(require_api_key), Depends(require_roles('admin'))])
async def assign_role(payload: Dict[str, Any], db: SessionLocal = Depends(get_db)):
    email = payload.get('email')
    role = (payload.get('role') or '').lower()
    if role not in {'admin','auditor','user'}:
        raise HTTPException(status_code=400, detail='Invalid role')
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.role = role
    db.add(user)
    db.commit()
    return {"email": user.email, "role": user.role}

@app.get('/api/connectors', response_model=List[Dict[str, Any]], dependencies=[Depends(require_api_key)])
async def list_connectors(vendor: Optional[str] = None, regulator: Optional[str] = None):
    from models import Connector, Vendor, Regulator  # type: ignore
    db = SessionLocal()
    try:
        q = db.query(Connector)
        if vendor:
            v = db.query(Vendor).filter(Vendor.name == vendor).first()
            if v:
                q = q.filter(Connector.vendor_id == v.id)
        if regulator:
            g = db.query(Regulator).filter(Regulator.name == regulator).first()
            if g:
                q = q.filter(Connector.regulator_id == g.id)
        items = q.order_by(Connector.name.asc()).limit(500).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "vendor_id": c.vendor_id,
                "regulator_id": c.regulator_id,
                "description": c.description,
            }
            for c in items
        ]
    finally:
        db.close()

@app.post('/api/tenants', dependencies=[Depends(require_api_key), Depends(require_roles('admin'))])
async def create_tenant(payload: Dict[str, Any], db: SessionLocal = Depends(get_db)):
    from models import Tenant  # type: ignore
    name = payload.get('name')
    api_key = payload.get('api_key')
    if not name:
        raise HTTPException(status_code=400, detail='name is required')
    exists = db.query(Tenant).filter(Tenant.name == name).first()
    if exists:
        raise HTTPException(status_code=409, detail='Tenant exists')
    t = Tenant(name=name, api_key=api_key)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "name": t.name, "api_key": t.api_key}

@app.get('/api/tenants', dependencies=[Depends(require_api_key), Depends(require_roles('admin'))])
async def list_tenants(db: SessionLocal = Depends(get_db)):
    from models import Tenant  # type: ignore
    tenants = db.query(Tenant).order_by(Tenant.name.asc()).all()
    return [{"id": t.id, "name": t.name, "api_key": t.api_key} for t in tenants]

@app.post('/api/tenants/{tenant_id}/rotate-key', dependencies=[Depends(require_api_key), Depends(require_roles('admin'))])
async def rotate_tenant_api_key(tenant_id: int, db: SessionLocal = Depends(get_db)):
    from models import Tenant  # type: ignore
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail='Tenant not found')
    t.api_key = _rand_hex(16)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "name": t.name, "api_key": t.api_key}

@app.post('/api/network/ping', dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def network_ping(req: PingRequest):
    """TCP connect to host:port or HTTP GET to URL. ICMP ping is avoided for portability."""
    result: Dict[str, Any] = {"ok": False}
    start = time.perf_counter()
    try:
        if req.url:
            u = urlparse(req.url)
            if u.scheme not in {"http", "https"} or not u.hostname:
                raise HTTPException(status_code=400, detail="Invalid URL")
            if _is_private_address(u.hostname) or not _is_allowed_host(u.hostname):
                raise HTTPException(status_code=403, detail="Host not allowed")
            timeout = min(max(req.timeout or 2.0, 0.5), 5.0)
            r = requests.get(req.url, timeout=timeout, allow_redirects=False)
            result.update({
                "mode": "http",
                "status_code": r.status_code,
                "elapsed_ms": int((time.perf_counter() - start) * 1000),
            })
            result["ok"] = 200 <= r.status_code < 400
        elif req.host and req.port:
            host = req.host
            if _is_private_address(host) or not _is_allowed_host(host):
                raise HTTPException(status_code=403, detail="Host not allowed")
            timeout = min(max(req.timeout or 2.0, 0.5), 5.0)
            with socket.create_connection((host, int(req.port)), timeout=timeout):
                pass
            result.update({
                "mode": "tcp",
                "host": host,
                "port": req.port,
                "elapsed_ms": int((time.perf_counter() - start) * 1000),
                "ok": True,
            })
        else:
            raise HTTPException(status_code=400, detail="Provide either url or host+port")
        return result
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"ok": False, "error": he.detail, "elapsed_ms": int((time.perf_counter() - start) * 1000)})
    except Exception:
        # Avoid leaking internal error details
        return JSONResponse(status_code=502, content={"ok": False, "error": "connection_failed", "elapsed_ms": int((time.perf_counter() - start) * 1000)})

@app.post('/api/scrape', dependencies=[Depends(require_api_key), Depends(rate_limited)])
async def scrape(req: ScrapeRequest):
    """Lightweight scraper: fetches the URL, extracts title/meta/links (depth 1) and optionally saves HTML."""
    if BeautifulSoup is None:
        raise HTTPException(status_code=500, detail="beautifulsoup4 is not installed")
    u = urlparse(req.url)
    if u.scheme not in {"http", "https"} or not u.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")
    if _is_private_address(u.hostname) or not _is_allowed_host(u.hostname):
        raise HTTPException(status_code=403, detail="Host not allowed")
    try:
        timeout = min(max(req.timeout or 3.0, 0.5), 8.0)
        cap = int(os.getenv('SCRAPE_MAX_BYTES', '1048576'))  # 1 MiB
        r = requests.get(req.url, timeout=timeout, headers={"User-Agent": "DoganAI-ComplianceKit/1.0"}, stream=True, allow_redirects=False)
        r.raise_for_status()
        total = 0
        chunks: list[bytes] = []
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                break
            total += len(chunk)
            if total > cap:
                break
            chunks.append(chunk)
        html = b''.join(chunks).decode(r.encoding or 'utf-8', errors='ignore')
    except Exception:
        raise HTTPException(status_code=502, detail="Fetch failed")
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    metas = {}
    for m in soup.find_all('meta'):
        n = m.get('name') or m.get('property')
        v = m.get('content')
        if n and v and len(metas) < 20:
            metas[str(n)] = str(v)

    # Extract links (depth 1)
    parsed = urlparse(req.url)
    links: List[str] = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        abs_url = urljoin(req.url, href)
        if req.same_domain_only and urlparse(abs_url).netloc != parsed.netloc:
            continue
        if abs_url not in links:
            links.append(abs_url)
        if len(links) >= 100:
            break

    # Save HTML snapshot
    snap_dir = os.getenv('SCRAPE_DIR', 'app/scraped')
    os.makedirs(snap_dir, exist_ok=True)
    import hashlib
    h = hashlib.sha256(req.url.encode('utf-8')).hexdigest()[:16]
    filename = f"snap_{h}.html"
    path = os.path.join(snap_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    return {
        "ok": True,
        "status_code": r.status_code,
        "title": title,
        "meta": metas,
        "links": links[: min(len(links), req.max_pages * 100)],
    }

@app.get('/api/auto/connectivity', dependencies=[Depends(require_api_key)])
async def auto_connectivity():
    """Check connectivity to core components: database, redis (if configured)."""
    report: Dict[str, Any] = {"database": {}, "redis": {}}
    # Database
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        report["database"] = {"ok": True}
    except Exception as e:
        report["database"] = {"ok": False, "error": str(e)}

    # Redis
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            import redis  # type: ignore
            r = redis.from_url(redis_url, socket_timeout=2)
            pong = r.ping()
            report["redis"] = {"ok": bool(pong)}
        except Exception as e:
            report["redis"] = {"ok": False, "error": str(e)}
    else:
        report["redis"] = {"configured": False}

    return report

@app.on_event('startup')
def startup_event():
    # Fail-fast on production misconfigurations
    env = os.getenv('ENV', os.getenv('ENVIRONMENT', 'development')).lower()
    # Disallow SQLite in production environments
    try:
        from database import DATABASE_URL as _DB_URL  # type: ignore
    except Exception:
        _DB_URL = None
    if env == 'production' and (not _DB_URL or str(_DB_URL).startswith('sqlite')):
        raise RuntimeError('Production environment requires a non-SQLite DATABASE_URL')

    # Optional DB readiness wait (non-SQLite)
    try:
        db_url = str(_DB_URL or '')
        if db_url and not db_url.startswith('sqlite'):
            import time as _t
            max_wait = int(os.getenv('DB_CONNECT_MAX_WAIT', '60'))
            interval = int(os.getenv('DB_CONNECT_RETRY_INTERVAL', '3'))
            deadline = _t.time() + max_wait
            while _t.time() < deadline:
                try:
                    with engine.connect() as conn:
                        conn.execute('SELECT 1')
                    break
                except Exception:
                    _t.sleep(interval)
    except Exception:
        pass

    # Additional preflight validations
    try:
        # API key must be configured for protected endpoints
        if not os.getenv('API_KEY'):
            raise RuntimeError('API_KEY is required; set it via environment or secrets management')
        # CORS is validated above for production; warning for development wildcard left as-is
        # Optional: verify Redis connectivity if REDIS_URL set
        rurl = os.getenv('REDIS_URL')
        if rurl:
            try:
                import redis  # type: ignore
                _r = redis.from_url(rurl, socket_timeout=2)
                _r.ping()
            except Exception as _e:
                # Log-only; app still starts
                import logging as _logging
                _logging.getLogger(__name__).warning(f"Redis connectivity check failed: {_e}")
        elif env == 'production' and os.getenv('REQUIRE_REDIS_FOR_RATELIMIT', 'true').lower() in {'1','true','yes'}:
            raise RuntimeError('REDIS_URL is required in production for distributed rate limiting')
    except Exception as _pf:
        # Fail fast in production
        if env == 'production':
            raise
    models.Base.metadata.create_all(bind=engine)
    # Background monitor (optional)
    try:
        import asyncio as _asyncio
        vids = [v.strip() for v in (os.getenv('MONITOR_VENDOR_IDS','demo').split(',')) if v.strip()]
        if vids and os.getenv('FEATURE_MONITORING','true').lower() in {'1','true','yes'}:
            _asyncio.get_event_loop().create_task(monitor_loop(vids))
    except Exception:
        pass
    # Optional: only seed admin in non-production when explicitly enabled
    if env != 'production' and os.getenv('ENABLE_ADMIN_SEED', 'false').lower() in {'1','true','yes'}:
        db = SessionLocal()
        try:
            admin = db.query(models.User).filter((models.User.email == 'admin@example.com')).first()
            if (not admin):
                hashed_password = get_password_hash('admin123')
                admin = models.User(email='admin@example.com', hashed_password=hashed_password, full_name='Admin User', is_superuser=True)
                db.add(admin)
                db.commit()
        finally:
            db.close()
if (__name__ == '__main__'):
    import uvicorn
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
# Basic health endpoint
@app.get('/health')
def health():
    return {"ok": True}
# Initialize tracing if enabled
def _init_otel():
    if not OTEL_AVAILABLE:
        return
    if os.getenv('OTEL_ENABLED', 'false').lower() not in {'1','true','yes'}:
        return
    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'doganai-api')
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        pass

_init_otel()

# --- Security utilities for SSRF/transport and CSRF ---
def _is_private_address(host: str) -> bool:
    try:
        # Resolve to IP(s) and test each
        for info in socket.getaddrinfo(host, None):
            ip = info[4][0]
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                return True
        return False
    except Exception:
        return True  # Fail closed

def _is_allowed_host(host: str) -> bool:
    allowlist = os.getenv('ALLOWED_OUTBOUND_HOSTS', '')
    # Comma/space separated hostnames or suffixes, e.g. example.com,.example.org
    allowed = [h.strip().lower() for h in allowlist.replace(';', ',').split(',') if h.strip()]
    if not allowed:
        return False  # Deny by default unless explicitly allowed
    host_l = host.lower()
    for entry in allowed:
        if entry.startswith('.'):
            if host_l.endswith(entry):
                return True
        elif host_l == entry:
            return True
    return False

async def require_csrf(request: Request):
    if os.getenv('ENABLE_CSRF', 'false').lower() not in {'1','true','yes'}:
        return
    token = request.headers.get('X-CSRF-Token')
    expected = os.getenv('CSRF_TOKEN')
    if not expected or token != expected:
        raise HTTPException(status_code=403, detail='CSRF validation failed')
