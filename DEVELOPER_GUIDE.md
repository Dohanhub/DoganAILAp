# DoganAI Compliance Kit - Developer Guide

## Quick Start

### Installation

#### Development Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/dogan-ai/compliance-kit.git
cd compliance-kit

# Install in editable mode
cd src
pip install -e .
```

#### Production Installation
```bash
pip install doganai-compliance-kit
```

## Application Entry Points

### FastAPI Server (Primary)

#### Using uvicorn directly (Recommended for development)
```bash
# From src/ directory with editable installation
uvicorn run:app --reload --host 0.0.0.0 --port 8000

# Alternative: Using PYTHONPATH
export PYTHONPATH=src
uvicorn run:app --reload --host 0.0.0.0 --port 8000
```

#### Using console script (After installation)
```bash
dai-server
```

#### Using Python module
```bash
# From src/ directory
python run.py

# Or directly
python main.py
```

### Streamlit Applications

#### Root-level app.py
```bash
streamlit run app.py
```

#### App directory
```bash
export PYTHONPATH=src
streamlit run app/app.py
```

## CLI Tools

After installation, the following command-line tools are available:

### Core CLI Tool
```bash
dai-cli --help
```

### Health Monitoring
```bash
dai-health
```

### Database Operations
```bash
# Seed database with comprehensive data
dai-seed
```

### Data Ingestion
```bash
# Run regulatory web scraper
dai-scrape
```

### Observability
```bash
# Start observability monitoring
dai-observability
```

### Server Management
```bash
# Start the main server
dai-server
```

## Environment Configuration

### Development Environment
```bash
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG
export ENABLE_METRICS=true
export ENABLE_STRUCTURED_LOGGING=true
```

### Production Environment
```bash
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=INFO
export HOST=0.0.0.0
export PORT=8000
export ENABLE_METRICS=true
export METRICS_PORT=9090
```

## Development Workflow

### 1. Setup Development Environment
```bash
# Install in editable mode
cd src
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Start Development Server
```bash
# Option 1: Using uvicorn (recommended)
uvicorn run:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using console script
dai-server

# Option 3: Using Python directly
python run.py
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run specific test suites
pytest src/tests/api/
pytest src/tests/services/

# Run with coverage
pytest --cov=src --cov-report=html
```

### 4. Check Code Quality
```bash
# Linting
flake8 src/
pylint src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

## API Endpoints

### Core Endpoints
- `GET /` - Application status
- `GET /health` - Health check
- `GET /metrics` - System metrics

### Compliance Endpoints
- `GET /mappings` - List compliance mappings
- `POST /evaluate` - Evaluate compliance
- `GET /policies` - List policies
- `GET /vendors` - List vendors

### Observability Endpoints
- `GET /observability/status` - Observability system status
- `GET /observability/metrics` - Detailed metrics

### Feature Flags Endpoints
- `GET /feature-flags` - List feature flags
- `GET /feature-flags/status` - Feature flags status
- `POST /feature-flags/{flag_name}/evaluate` - Evaluate feature flag

### Audit Endpoints
- `GET /audit` - Get audit logs

## Monitoring and Observability

### Metrics Collection
- **Prometheus metrics**: http://localhost:9090/metrics
- **Application metrics**: http://localhost:8000/metrics
- **Observability status**: http://localhost:8000/observability/status

### Structured Logging
Logs are output in JSON format with correlation IDs for tracing:
```json
{
  "timestamp": "2025-08-29T10:56:17.827066Z",
  "level": "info",
  "logger": "src.core.observability_init",
  "event": "Observability system initialized successfully",
  "correlation_id": "d8fa4ded-0daf-4a4c-bf87-c9a549ed74d8",
  "metrics_port": 9090,
  "environment": "development"
}
```

### Feature Flags
Feature flags are configured in `feature_flags/flags.json` and support:
- Canary rollouts (10% initial)
- Gradual rollouts (25%, 50%, 75%)
- Full rollouts (100%)
- Kill switches for emergency shutdowns

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure editable installation
cd src && pip install -e .

# Or set PYTHONPATH
export PYTHONPATH=src
```

#### Port Already in Use
```bash
# Change port
export PORT=8001
dai-server

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

#### Database Connection Issues
```bash
# Check database configuration
dai-health

# Seed database
dai-seed
```

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
dai-server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

- **Documentation**: https://docs.dogan.ai/compliance-kit
- **Issues**: https://github.com/dogan-ai/compliance-kit/issues
- **Email**: platform@dogan.ai