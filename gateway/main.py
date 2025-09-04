from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import httpx
import os

from app.common.auth import verify_request, issue_token
from app.core.registry import svc_url


app = FastAPI(title="DoganAI Gateway")

REQS = Counter("gateway_http_requests_total", "requests", ["path", "method", "code"])
LAT = Histogram("gateway_http_request_duration_seconds", "latency", ["path", "method"])


@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    path = request.url.path
    method = request.method
    with LAT.labels(path=path, method=method).time():
        resp = await call_next(request)
    try:
        REQS.labels(path=path, method=method, code=str(resp.status_code)).inc()
    except Exception:
        pass
    return resp


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/compliance/validate")
async def validate(req: Request, _=Depends(lambda r=req: verify_request(r, "gateway"))):
    payload = await req.json()
    # basic audit log (DB optional)
    try:
        from app.database import SessionLocal  # type: ignore
        from app.models import AuditLog  # type: ignore
        db = SessionLocal()
        db.add(AuditLog(user_email=None, method="POST", path="/compliance/validate", status_code=200, ip=None))
        db.commit(); db.close()
    except Exception:
        pass

    # Test shortcut (local engine): use in-proc ASGI app when TEST_LOCAL_ENGINE=1
    if os.getenv("TEST_LOCAL_ENGINE", "0") in {"1", "true", "yes"}:
        from app.main import app as engine_app  # type: ignore
        async with httpx.AsyncClient(app=engine_app, base_url="http://engine") as c:
            r = await c.post("/api/v1/validate", json=payload)
            return JSONResponse(status_code=r.status_code, content=r.json())

    # Default: proxy to compliance-engine service
    url = svc_url("compliance-engine", port=int(os.getenv("ENGINE_PORT", "8000"))) + "/api/v1/validate"
    token = issue_token("gateway", "compliance-engine")
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(url, json=payload, headers={"authorization": f"Bearer {token}"})
        return JSONResponse(status_code=r.status_code, content=r.json())
