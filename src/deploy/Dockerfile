# DoganAI Compliance Kit - Production Dockerfile
# Multi-stage build for lightweight, secure container

# =============================================================================
# Stage 1: Build Dependencies
# =============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.lock.txt /tmp/requirements.lock.txt
COPY requirements-api.txt /tmp/requirements-api.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    (pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock.txt || pip install --no-cache-dir -r /tmp/requirements-api.txt)

# =============================================================================
# Stage 2: Production Runtime
# =============================================================================
FROM python:3.11-slim as production

# Metadata labels
LABEL maintainer="DoganAI Team <support@doganai.com>" \
      version="${VERSION}" \
      description="DoganAI Compliance Kit - Ministry of Interior" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}" \
      org.opencontainers.image.title="DoganAI Compliance Kit" \
      org.opencontainers.image.description="Compliance management system for KSA regulatory requirements" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="DoganAI" \
      org.opencontainers.image.licenses="MIT"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r doganai && \
    useradd -r -g doganai -d /app -s /bin/bash doganai && \
    mkdir -p /app /app/logs /app/data /app/temp && \
    chown -R doganai:doganai /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code with proper ownership
COPY --chown=doganai:doganai . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/engine/static /app/ui/static /app/logs /app/data /app/temp /var/log/doganai && \
    chown -R doganai:doganai /app /var/log/doganai && \
    chmod -R 755 /app /var/log/doganai && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true

# Set timezone to Saudi Arabia
ENV TZ=Asia/Riyadh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Environment variables for production
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    WORKERS=4 \
    MAX_WORKERS=8 \
    WORKER_CLASS=uvicorn.workers.UvicornWorker \
    TIMEOUT=120 \
    KEEPALIVE=5 \
    MAX_REQUESTS=1000 \
    MAX_REQUESTS_JITTER=100 \
    PRELOAD=true

# Security configurations
ENV SECURITY_HEADERS=true \
    RATE_LIMITING=true \
    CORS_ENABLED=true \
    API_DOCS_ENABLED=false \
    DEBUG_MODE=false

# Database and Redis configurations
ENV DATABASE_URL="" \
    REDIS_URL="" \
    DATABASE_POOL_SIZE=20 \
    DATABASE_MAX_OVERFLOW=30 \
    DATABASE_POOL_TIMEOUT=30 \
    DATABASE_POOL_RECYCLE=3600

# Monitoring and health check configurations
ENV HEALTH_CHECK_ENABLED=true \
    METRICS_ENABLED=true \
    PROMETHEUS_PORT=9090 \
    JAEGER_ENABLED=false \
    STRUCTURED_LOGGING=true

# API and service configurations
ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_PREFIX="/api/v1" \
    RATE_LIMIT_REQUESTS=100 \
    RATE_LIMIT_WINDOW=60

# Switch to non-root user
USER doganai

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Volume for persistent data
VOLUME ["/app/data", "/app/logs"]

# Copy startup script
COPY --chown=doganai:doganai docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Default command
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "engine.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log", "--log-level", "info"]

# =============================================================================
# Build Information
# =============================================================================
# Build command:
# docker build --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#              --build-arg VCS_REF=$(git rev-parse --short HEAD) \
#              -t doganai/compliance-kit:latest \
#              -t doganai/compliance-kit:v1.0.0 .
#
# Run command:
# docker run -d --name doganai-compliance \
#            -p 8000:8000 \
#            -p 9090:9090 \
#            -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
#            -e REDIS_URL="redis://host:6379/0" \
#            -v doganai-data:/app/data \
#            -v doganai-logs:/app/logs \
#            --restart unless-stopped \
#            doganai/compliance-kit:latest
# =============================================================================
