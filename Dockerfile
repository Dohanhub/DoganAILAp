##
# Multi-stage, security-hardened, non-root, Gunicorn-powered image with healthcheck
##

ARG PYTHON_VERSION=3.11.9

# Builder stage: install build tools and Python deps into a venv
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Update packages and remove unnecessary packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
 && apt-get upgrade -y \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /tmp/* \
 && rm -rf /var/tmp/*

WORKDIR /app

# Create virtualenv and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt ./
COPY requirements-api.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements-api.txt \
 && pip check

# Final stage: minimal runtime with non-root user
FROM python:${PYTHON_VERSION}-slim AS runtime

# Security labels
LABEL maintainer="DoganAI Team <team@doganai.com>" \
      org.opencontainers.image.title="DoganAI Compliance Kit" \
      org.opencontainers.image.description="Comprehensive compliance and governance platform" \
      org.opencontainers.image.vendor="DoganAI" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/Dohanhub/DoganAILAp"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    TINI_VERSION=v0.19.0

# Security: Update packages and install minimal runtime dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tini \
 && apt-get upgrade -y \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /tmp/* \
 && rm -rf /var/tmp/* \
 && rm -rf /usr/share/doc/* \
 && rm -rf /usr/share/man/*

# Create non-root user with minimal privileges
RUN groupadd -r -g 1001 app \
 && useradd -r -g app -u 1001 -m -d /home/app -s /bin/bash app \
 && mkdir -p /app/logs /app/data \
 && chown -R app:app /app

WORKDIR /app

# Copy venv and application source with proper ownership
COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --chown=app:app . /app

# Security: Remove any unnecessary files and set proper permissions
RUN find /app -type f -name "*.pyc" -delete \
 && find /app -type d -name "__pycache__" -exec rm -rf {} + \
 && chmod -R 755 /app \
 && chmod 644 /app/requirements*.txt \
 && if [ -f "/app/.env" ]; then chmod 600 /app/.env; fi

# Drop privileges to non-root user
USER app

# Expose port (non-privileged)
EXPOSE 8000

# Security: Use tini as init system to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Healthcheck on the FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS --max-time 5 http://127.0.0.1:8000/health || exit 1

# Use Uvicorn directly for simplicity
CMD ["/opt/venv/bin/uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--loop", "uvloop", \
     "--http", "httptools"]
