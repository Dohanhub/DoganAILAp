# ??? DoganAI Compliance Kit - Unified Enterprise Platform

> **Advanced Saudi Arabia Regulatory Compliance Management System**

A comprehensive, production-ready compliance management platform designed specifically for Saudi Arabian regulatory frameworks with modern enterprise architecture.

## ?? Key Features

### ??? Saudi Regulatory Compliance
- **NCA Framework** - National Cybersecurity Authority compliance
- **SAMA Framework** - Saudi Central Bank cybersecurity requirements  
- **PDPL Compliance** - Personal Data Protection Law implementation
- **Arabic Language Support** - Full RTL support and localization

### ??? Modern Architecture
- **FastAPI Backend** - High-performance async REST API
- **React Frontend** - Modern, responsive web interface (replaces Streamlit)
- **PostgreSQL Database** - Enterprise-grade data persistence
- **Microservices Ready** - Scalable service architecture

### ?? Enterprise Security
- **JWT Authentication** - Secure token-based auth
- **Role-Based Access Control** - Granular permissions
- **API Rate Limiting** - DoS protection
- **Audit Logging** - Comprehensive activity tracking

### ?? Advanced Analytics
- **Real-time Dashboards** - Live compliance monitoring
- **Risk Management** - Advanced risk assessment and tracking
- **Report Generation** - Automated compliance reporting
- **Data Visualization** - Interactive charts and graphs

## ?? Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** 
- **PostgreSQL 13+** (optional, defaults to SQLite for development)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Dohanhub/DoganAI-Compliance-Kit.git
cd DoganAI-Compliance-Kit

# Run project consolidation (one-time setup)
python consolidate_project.py

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configuration

```bash
# Copy environment configuration
cp .env.example .env

# Edit configuration for your environment
# Set DATABASE_URL for PostgreSQL or leave blank for SQLite
```

### 3. Start the Application

```bash
# Start unified application (API + Frontend)
python main_unified.py

# Or start components separately:
python main_unified.py --api-only     # API only
python main_unified.py --frontend-only # Frontend only
```

### 4. Access the Application

- **Frontend**: http://localhost:3001
- **API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## ?? Project Structure (After Consolidation)

```
DoganAI-Compliance-Kit/
??? main_unified.py              # ?? Unified application entry point
??? main.py                      # ?? Legacy entry point (redirects)
??? consolidate_project.py       # ?? Project consolidation script
??? src/                         # ?? Consolidated source code
?   ??? core/                    # ? Core application logic
?   ?   ??? app.py              # FastAPI application factory
?   ?   ??? database.py         # Database configuration
?   ?   ??? settings.py         # Application settings
?   ??? api/                     # ?? REST API endpoints
?   ?   ??? v1/                 # API version 1
?   ?   ??? health.py           # Health check endpoints
?   ??? models/                  # ?? Data models
?   ?   ??? database.py         # SQLAlchemy models
?   ?   ??? schemas.py          # Pydantic schemas
?   ??? services/               # ?? Business logic services
?   ?   ??? compliance.py       # Compliance engine
?   ?   ??? risk.py            # Risk management
?   ?   ??? reporting.py       # Report generation
?   ??? utils/                  # ??? Utility functions
??? frontend/                   # ?? Modern React frontend
?   ??? src/
?   ?   ??? components/         # Reusable UI components
?   ?   ??? pages/             # Application pages
?   ?   ??? hooks/             # Custom React hooks
?   ?   ??? providers/         # Context providers
?   ?   ??? lib/               # Utilities and API client
?   ??? package.json           # Frontend dependencies
?   ??? vite.config.ts         # Vite configuration
??? tests/                      # ?? Test suites
??? docs/                       # ?? Documentation
??? config/                     # ?? Configuration files
??? docker/                     # ?? Container configuration
```

## ?? Development Guide

### Project Consolidation

This project has been consolidated from multiple duplicate directories:

```bash
# Before consolidation
platform/microservices/
microservices/
src/api/microservices/
# Multiple main.py files with different implementations

# After consolidation  
src/services/           # ? Unified services
main_unified.py         # ? Single entry point
```

### Backend Development

```bash
# Install backend dependencies
pip install -r requirements.txt

# Start API server only
python main_unified.py --api-only

# Run tests
pytest

# Check code quality
flake8 src/
mypy src/
```

### Frontend Development

```bash
# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Database Management

```bash
# Development (SQLite)
export DATABASE_URL="sqlite:///./compliance.db"

# Production (PostgreSQL)
export DATABASE_URL="postgresql://user:pass@localhost:5432/compliance"

# Run migrations
alembic upgrade head
```

## ?? Saudi Compliance Frameworks

### National Cybersecurity Authority (NCA)
- **Controls**: 114 cybersecurity controls
- **Sectors**: Critical infrastructure, government, healthcare
- **Implementation**: Mandatory for all covered entities

### Saudi Central Bank (SAMA)
- **Controls**: 97 financial cybersecurity controls  
- **Sectors**: Banking, fintech, payment services
- **Implementation**: Mandatory for financial institutions

### Personal Data Protection Law (PDPL)
- **Controls**: 73 data protection requirements
- **Sectors**: All sectors processing personal data
- **Implementation**: Mandatory nationwide

## ?? API Documentation

### Authentication
```bash
# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "jwt_token_here",
  "user": { "id": 1, "email": "user@example.com" }
}
```

### Compliance Frameworks
```bash
# Get frameworks
GET /api/v1/compliance/frameworks

# Response
{
  "frameworks": [
    {
      "code": "NCA",
      "name": "National Cybersecurity Authority",
      "name_arabic": "?????? ??????? ????? ?????????",
      "mandatory": true,
      "controls": 114
    }
  ]
}
```

### Risk Management
```bash
# Create risk
POST /api/v1/risks
{
  "title": "Data breach risk",
  "severity": "high",
  "likelihood": "medium"
}
```

## ?? Docker Deployment

```bash
# Build images
docker build -t doganai-api .
docker build -f frontend/Dockerfile -t doganai-frontend ./frontend

# Run with docker-compose
docker-compose up -d

# Kubernetes deployment
kubectl apply -f k8s/
```

## ?? Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Auditor, User)
- API key authentication for service-to-service
- Session management and timeout

### Data Protection
- Encryption at rest and in transit
- Personal data anonymization
- Audit trail for all operations
- GDPR/PDPL compliance features

### API Security
- Rate limiting per endpoint
- CORS protection
- Input validation and sanitization
- SQL injection prevention

## ?? Performance Features

### Backend Optimization
- Async/await throughout
- Database connection pooling
- Redis caching integration
- Background task processing

### Frontend Optimization
- Code splitting and lazy loading
- Progressive Web App (PWA)
- Responsive design
- Real-time updates via WebSocket

## ?? Internationalization

### Supported Languages
- **English** (Left-to-Right)
- **Arabic** (Right-to-Left) 

### Features
- Complete UI translation
- Cultural date/number formatting
- Arabic typography support
- Dynamic direction switching

## ?? Testing

```bash
# Backend tests
pytest src/tests/
pytest --cov=src --cov-report=html

# Frontend tests  
cd frontend
npm test
npm run test:coverage

# E2E tests
npm run test:e2e
```

## ?? Production Deployment

### Environment Setup
```bash
# Production environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
export SECRET_KEY=your-secret-key
export ALLOWED_ORIGINS=https://yourdomain.com
```

### Deployment Options

#### 1. Traditional Server
```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build

# Start application
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

#### 2. Docker Containers
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Kubernetes
```bash
kubectl apply -f k8s/production/
```

## ?? Monitoring & Observability

### Metrics
- Application performance metrics
- Business metrics (compliance scores, risks)
- Infrastructure metrics (CPU, memory, disk)

### Logging
- Structured JSON logging
- Correlation IDs for tracing
- Centralized log aggregation

### Health Checks
- `/health` - Basic health check
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

## ?? Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Run consolidation**: `python consolidate_project.py` (if needed)
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Development Workflow
1. Run `python consolidate_project.py` if project structure changes
2. Follow the unified structure in `src/`
3. Use absolute imports: `from src.core.app import create_app`
4. Update tests and documentation
5. Run quality checks before committing

## ?? Support

- **Documentation**: [Project Wiki](https://github.com/Dohanhub/DoganAI-Compliance-Kit/wiki)
- **Issues**: [GitHub Issues](https://github.com/Dohanhub/DoganAI-Compliance-Kit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Dohanhub/DoganAI-Compliance-Kit/discussions)

## ?? License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ?? Acknowledgments

- Saudi regulatory authorities (NCA, SAMA, SDAIA)
- FastAPI and React communities
- Open source compliance frameworks
- Contributors and early adopters

---

**Built with ?? for Saudi Arabia's digital transformation**