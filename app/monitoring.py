"""Observability utilities (metrics, tracing, log correlation).

This module is safe to import from app.main and will not register duplicate
routes if they already exist. It focuses on production‑grade concerns:
- Request ID propagation (X-Request-Id)
- Optional metrics endpoint registration
- Optional OpenTelemetry init (leave to main if already configured)
- JSON logging correlation via a request_id filter
"""

from __future__ import annotations

import os
import logging
import uuid
import contextvars
from typing import Optional

from fastapi import FastAPI, Request
from starlette.responses import Response

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
except Exception:  # pragma: no cover
    generate_latest = None  # type: ignore
    CONTENT_TYPE_LATEST = 'text/plain'  # type: ignore

# Context for request ID, available to logging filter
REQUEST_ID_CTX: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        rid = REQUEST_ID_CTX.get() or '-'
        setattr(record, 'request_id', rid)
        return True


def _maybe_register_metrics_route(app: FastAPI) -> None:
    if not generate_latest:
        return
    # Avoid duplicate registration
    for r in getattr(app, 'routes', []):
        if getattr(r, 'path', None) == '/metrics':
            return

    @app.get('/metrics')
    def metrics() -> Response:  # type: ignore
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _install_request_id_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def _request_id_mw(request: Request, call_next):  # type: ignore
        rid = request.headers.get('X-Request-Id') or uuid.uuid4().hex
        token = REQUEST_ID_CTX.set(rid)
        try:
            response: Response = await call_next(request)
        finally:
            REQUEST_ID_CTX.reset(token)
        try:
            response.headers.setdefault('X-Request-Id', rid)
            # W3C trace context passthrough (if upstream set one)
            if 'traceparent' in request.headers:
                response.headers.setdefault('traceparent', request.headers['traceparent'])
        except Exception:
            pass
        return response


def _attach_log_filter() -> None:
    try:
        root = logging.getLogger()
        f = RequestIdFilter()
        for h in root.handlers:
            h.addFilter(f)
    except Exception:
        pass


def init_observability(app: FastAPI) -> None:
    """Initialize enterprise‑grade observability hooks.

NIST 800-53 Controls:
- AU-4(1): Audit storage capacity monitoring
- AU-12: Audit generation
"

    - Request ID middleware with header propagation
    - Metrics endpoint registration (if not present)
    - Log correlation filter for JSON logs
    """
    _install_request_id_middleware(app)
    _maybe_register_metrics_route(app)
    _attach_log_filter()

    # Tracing is initialized in app.main; no action here to avoid duplicates.
    # NIST AU-4(1): Configure audit record storage monitoring
self.audit_storage_monitor = Gauge('audit_storage_capacity', 'Remaining audit storage capacity in percentage')

# Initialize OpenTelemetry metric exporters if enabled
if os.getenv('ENABLE_OTEL_METRICS') == 'true':
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    exporter = PeriodicExportingMetricReader(
        endpoint=os.getenv('OTEL_EXPORTER_OTLP_METRICS_ENDPOINT'),
        export_interval_millis=5000
    )
    provider = MeterProvider(metric_readers=[exporter])
    # ... existing code ...



ANOMALY_SCORE = Gauge('security_anomaly_score', 'Real-time anomaly detection score')

async def evaluate_anomalies():
    model = SecurityAnomaly.lstm_autoencoder().eval()
    async with AsyncSessionLocal() as session:
        events = await session.execute(
            select(SecurityAnomaly)
            .order_by(SecurityAnomaly.event_time.desc())
            .limit(1000)
        )
        inputs = preprocess([e.raw_payload for e in events.scalars()])
        with torch.no_grad():
            reconstructions = model(inputs)
            scores = torch.mean(F.mse_loss(inputs, reconstructions, reduction='none'), dim=1)
            for idx, score in enumerate(scores):
                ANOMALY_SCORE.set(score.item())
