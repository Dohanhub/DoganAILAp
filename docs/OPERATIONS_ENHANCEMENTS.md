# Operations Enhancements (Roadmap)

High-Value Patterns
- Circuit Breaker: wrap outbound HTTP calls with timeouts + failure thresholds
- Rate Limiting: per-user and per-IP limits at gateway (e.g., middleware or reverse proxy)
- Connection Pooling: tune asyncpg / SQLAlchemy pools per-service
- Caching: L1 in-process + optional Redis L2 for expensive queries

Implementation Hints
- Inter-service JWT: use `INTERNAL_JWT_SECRET` and short-lived tokens; verify on `/api/*` endpoints
- Observability: standardize `/metrics` with consistent labels; dashboard templates in Grafana
- Performance: benchmark critical endpoints; set latency SLOs

Next Steps
- Add gateway middleware for rate limiting
- Introduce resilience helpers and migrate outbound calls
- Document standardized health/metrics contracts across services

