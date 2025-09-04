# DoganAI Compliance Kit: Next-Gen Saudi Enterprise Platform (Microservices Roadmap)

## Vision
- **On-prem, modular, microservices-based platform** for Saudi banking and government sectors
- **100% KSA regulatory coverage** (NCA, SAMA, MoH, etc.)
- **Local LLM/AI** (no cloud dependency)
- **Unique, world-class UI/UX** (bilingual, mobile-first, dashboard-driven)
- **Hardware-aligned** for mobile service stations and field maneuvering
- **Extensible**: plug-in modules, integrations, and marketplace-ready

## Core Microservices (Phase 1)
- **compliance-engine**: Modular compliance logic, API-first
- **benchmarks**: Unified, extensible regulatory benchmark database
- **ai-ml**: Local LLM inference, compliance Q&A, risk prediction
- **integrations**: Evidence collection, reporting, connectors
- **ui**: Next-gen dashboard, AR/EN, mobile, accessible
- **shared-libs**: Common models, utilities, and schemas

## Pipeline & Operations
- Automated CI/CD for all services
- Security, linting, type-checking, and test automation
- Hardware-aware deployment (resource constraints, mobile stations)

---

# AI-Compliance-Kit (KSA Enterprise Blueprint) - Enhanced Version

One-click, bilingual (AR/EN) **Compliance + CX Ops** suite for Government, Banking, Health, Energy, Smart City.
Runs air-gapped on an AI Mobile Kit or on-prem.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker compose -f compose/compose.gov.yml up -d
# UI: http://localhost:8501
# API: http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# 1. Setup and install
python manage.py setup

# 2. Start API (in first terminal)
python manage.py api

# 3. Start UI (in second terminal)
python manage.py ui
```

### Option 3: Manual Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
uvicorn engine.api:app --host 0.0.0.0 --port 8000 &
streamlit run ui/app.py
```

## 🧪 Testing & Validation

```bash
# Quick test
python test_quick.py

# Test imports
python scripts/test_imports.py

# Full validation
python scripts/validate_config.py

# Run test suite
pytest tests/
```

## 🔧 Environment Configuration

Copy `.env.example` to `.env` and adjust values:

### Key Variables
- `API_URL` (default `http://localhost:8000`)
- `CORS_ORIGINS` (comma separated)
- `POSTGRES_*` (database configuration)
- `DEBUG` (enable/disable debug mode)
- `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)

### Example .env
```bash
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
DEBUG=true
LOG_LEVEL=INFO
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ksa
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

## 📊 API Endpoints

### Core Endpoints
- `GET /health` → Basic health status
- `GET /health/detailed` → Comprehensive health check
- `GET /version` → Application version info
- `GET /mappings` → List available mapping names
- `GET /benchmarks` → KPI JSON data
- `POST /evaluate` → Evaluate compliance mapping
- `GET /metrics` → Prometheus metrics

### Enhanced Features
- **Request Tracking**: All requests include unique IDs
- **Error Handling**: Structured error responses
- **Monitoring**: Prometheus metrics for performance
- **Validation**: Comprehensive input validation

### Example API Usage
```bash
# Evaluate a mapping
curl -X POST "http://localhost:8000/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"mapping": "MAP-GOV-SecurePortal-IBM-Lenovo"}'

# Get health status
curl "http://localhost:8000/health/detailed"

# List available mappings
curl "http://localhost:8000/mappings"
```

## 🏗️ Development

### Setup Development Environment
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
cp .env.example .env
```

### Development Commands
```bash
# Format code
black . && isort .

# Lint code
ruff .

# Type checking
mypy .

# Run tests
pytest

# Run with coverage
pytest --cov=engine --cov=ui

# Start development servers
python manage.py api    # API with auto-reload
python manage.py ui     # Streamlit UI
```

### Docker Development
```bash
# Start development environment with database
docker compose -f compose/docker-compose.dev.yml up -d

# View logs
docker compose -f compose/docker-compose.dev.yml logs -f
```

## 🎯 Enhanced Features

### ✅ Improved Error Handling
- Custom exception classes for different error types
- Structured error responses with timestamps
- Comprehensive logging with request tracing
- Graceful degradation for missing dependencies

### 📈 Performance Optimizations
- Database caching for evaluation results
- Intelligent file caching with TTL
- Request/response monitoring
- Connection pooling for database operations

### 🔒 Security Enhancements
- Input validation with Pydantic models
- CORS configuration for web security
- Request rate limiting (configurable)
- Structured logging for audit trails

### 📊 Monitoring & Observability
- Prometheus metrics for APIs and system resources
- Health checks for all system components
- Performance tracking and reporting
- Database audit logging

### 🧪 Testing Infrastructure
- Comprehensive test suite with fixtures
- API integration tests
- Database transaction testing
- Configuration validation tests

## 🐳 Production Deployment

### Environment Variables for Production
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secure-secret-key
POSTGRES_HOST=your-db-host
POSTGRES_PASSWORD=secure-password
LOG_LEVEL=INFO
ENABLE_METRICS=true
RATE_LIMIT_ENABLED=true
```

### Docker Production Setup
```bash
# Build and deploy
docker compose -f compose/compose.gov.yml up -d

# Scale API instances
docker compose -f compose/compose.gov.yml up -d --scale api=3

# Monitor logs
docker compose logs -f api ui
```

### Production Notes
- API served by `gunicorn` with `uvicorn` workers
- Use environment variable `GUNICORN_WORKERS` to tune worker count
- Enable PostgreSQL for persistent data storage
- Configure reverse proxy (nginx/traefik) for SSL termination
- Set up monitoring with Prometheus and Grafana

## 📁 Project Structure

```
DoganAI-Compliance-Kit/
├── engine/                 # Core engine modules
│   ├── api.py             # FastAPI application
│   ├── compliance.py      # Compliance evaluation logic
│   ├── settings.py        # Configuration management
│   ├── health.py          # Health monitoring
│   ├── database.py        # Database operations
│   └── models.py          # Data models
├── ui/                    # Streamlit user interface
│   └── app.py             # Main UI application
├── tests/                 # Test suite
│   ├── test_api.py        # API tests
│   ├── test_compliance.py # Compliance tests
│   └── conftest.py        # Test fixtures
├── scripts/               # Utility scripts
│   ├── validate_config.py # Configuration validation
│   └── test_imports.py    # Import testing
├── mappings/              # Compliance mappings
├── policies/              # Regulatory policies
├── vendors/               # Vendor capabilities
├── benchmarks/            # Performance benchmarks
├── i18n/                  # Internationalization
├── compose/               # Docker configurations
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── manage.py              # Management script
└── test_quick.py          # Quick validation test
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   python scripts/test_imports.py  # Test all imports
   ```

2. **Configuration Issues**
   ```bash
   python scripts/validate_config.py  # Validate configuration
   ```

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt  # Install dependencies
   ```

4. **Database Connection Issues**
   - Check PostgreSQL service is running
   - Verify database credentials in `.env`
   - Test connection: `python -c "from engine.database import get_db_service; get_db_service().initialize()"`
   - Check if the PostgreSQL server is running and accessible.
   - Ensure the database, user, and password are correctly set in the `.env` file.
   - Test the connection manually using a PostgreSQL client.

5. **Port Conflicts**
   - API default: 8000
   - UI default: 8501
   - Change ports in `.env` if needed

6. **Docker Issues**
   - Ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is running.
   - For permission issues on Linux, use `sudo` or adjust your Docker group memberships.
   - If you encounter network issues, try resetting Docker's network settings to default.

7. **Environment Variable Issues**
   - Ensure all required environment variables are set.
   - Check for typos or incorrect values in the `.env` file.

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python manage.py api  # Start with verbose logging
```

### Performance Issues
```bash
# Check system health
curl http://localhost:8000/health/detailed

# Monitor metrics
curl http://localhost:8000/metrics
```

## 📖 Documentation

- **API Documentation**: Available at `/docs` when `DEBUG=true`
- **Health Monitoring**: Real-time status at `/health/detailed`
- **Metrics**: Prometheus metrics at `/metrics`
- **Configuration**: Use `python scripts/validate_config.py`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Pull Request Checklist
- [ ] Code formatted with `black` and `isort`
- [ ] Linting passes with `ruff`
- [ ] Type checking passes with `mypy`
- [ ] Tests pass with `pytest`
- [ ] Configuration validation passes
- [ ] Documentation updated

## 📜 License

This project maintains compatibility with the original license while adding significant enterprise-grade improvements for production use.

## 🆘 Support

- Check [troubleshooting section](#-troubleshooting)
- Review logs for error details
- Use health checks: `curl localhost:8000/health/detailed`
- Validate setup: `python test_quick.py`
