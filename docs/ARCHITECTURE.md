# DoganAI Compliance Kit - System Architecture

## Overview

The DoganAI Compliance Kit is a comprehensive enterprise-grade compliance management platform designed for regulatory compliance in the Kingdom of Saudi Arabia (KSA). The system follows a modern microservices architecture with clear separation of concerns, robust observability, and production-ready deployment capabilities.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DoganAI Compliance Kit                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              Presentation Layer                                 │
├─────────────────────┬─────────────────────┬─────────────────────────────────────┤
│   Streamlit UI      │    FastAPI REST     │       CLI Tools                     │
│   (Port 8501)      │    (Port 8000)      │   (dai-cli, dai-health, etc.)      │
├─────────────────────┼─────────────────────┼─────────────────────────────────────┤
│                              Application Layer                                  │
├─────────────────────┬─────────────────────┬─────────────────────────────────────┤
│  Compliance Engine  │  Feature Flags      │    Observability                   │
│  - Policy Eval      │  - A/B Testing      │    - Metrics                       │
│  - Mapping Mgmt     │  - Rollout Control  │    - Logging                       │
│  - Audit Logging    │  - Config Mgmt      │    - Tracing                       │
├─────────────────────┼─────────────────────┼─────────────────────────────────────┤
│                               Service Layer                                     │
├─────────────────────┬─────────────────────┬─────────────────────────────────────┤
│   Database Service  │   Monitoring Svc    │    Security Service                 │
│   - Connection Pool │   - Health Checks   │    - Authentication                 │
│   - Transaction Mgmt│   - Metrics Collect │    - Authorization                  │
│   - Migration Mgmt  │   - Alert Manager   │    - Rate Limiting                  │
├─────────────────────┼─────────────────────┼─────────────────────────────────────┤
│                              Infrastructure Layer                               │
├─────────────────────┬─────────────────────┬─────────────────────────────────────┤
│    PostgreSQL       │      Redis          │       File System                  │
│    (Primary DB)     │    (Caching)        │    - Config Files                  │
│                     │                     │    - Policy Documents              │
│                     │                     │    - Mapping Files                 │
└─────────────────────┴─────────────────────┴─────────────────────────────────────┘
```

## Directory Structure & Import Policy

### Project Structure

```
DoganAI-Compliance-Kit/
├── src/                          # All application code resides here
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # FastAPI application entry point
│   ├── run.py                    # Uvicorn server entry point
│   ├── api/                      # REST API endpoints
│   │   ├── __init__.py
│   │   └── health.py             # Health check endpoints
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection management
│   │   ├── settings.py           # Configuration management
│   │   ├── models.py             # Database models
│   │   └── compliance.py         # Compliance evaluation engine
│   ├── services/                 # Business services
│   │   ├── __init__.py
│   │   ├── compliance.py         # Compliance service layer
│   │   ├── monitoring.py         # Monitoring and metrics
│   │   ├── observability.py      # Observability management
│   │   └── feature_flags.py      # Feature flag management
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py         # Data validation utilities
│   │   ├── monitoring.py         # Monitoring utilities
│   │   └── shard_router.py       # Database sharding utilities
│   ├── cli/                      # Command-line interface
│   │   ├── __init__.py
│   │   └── cli.py                # CLI commands implementation
│   ├── tests/                    # Test suites
│   │   ├── api/                  # API tests
│   │   ├── db/                   # Database tests
│   │   ├── e2e/                  # End-to-end tests
│   │   ├── perf/                 # Performance tests
│   │   └── smoke/                # Smoke tests
│   └── governance/               # Governance and compliance
│       ├── service_catalog.yml   # Service catalog definition
│       ├── governance_manager.py # Governance management
│       └── governance_dashboard.py # Governance dashboard
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # This file
│   └── runbooks/                # Operational runbooks
│       └── report-generator.md  # Report generator runbook
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml                   # Continuous integration
│   ├── deploy-staging.yml       # Staging deployment
│   └── deploy-production.yml    # Production deployment
├── pyproject.toml               # Package configuration
├── pytest.ini                  # Test configuration
└── README.md                    # Project documentation
```

### Import Policy

**Core Principle**: All application code resides under `src/*`; root directory contains entry points only.

#### Import Rules

1. **Absolute Imports Only**: Use absolute imports starting with `src.`
   ```python
   # ✅ Correct
   from src.core.database import get_db_service
   from src.services.compliance import ComplianceEngine
   
   # ❌ Incorrect
   from .core.database import get_db_service
   from ..services.compliance import ComplianceEngine
   ```

2. **Module Organization**:
   - `src.core.*`: Core business logic and infrastructure
   - `src.services.*`: Business service layer
   - `src.api.*`: REST API endpoints and handlers
   - `src.utils.*`: Shared utility functions
   - `src.cli.*`: Command-line interface components

3. **Dependency Direction**:
   ```
   API Layer → Service Layer → Core Layer → Utils
   ```
   - API layer depends on services
   - Services depend on core components
   - Core components may use utilities
   - No circular dependencies allowed

4. **External Dependencies**:
   - All external packages defined in `pyproject.toml`
   - Use dependency injection for testability
   - Prefer composition over inheritance

## Core Components

### 1. FastAPI Application (`src/main.py`)

- **Purpose**: Main REST API server
- **Port**: 8000 (configurable)
- **Features**:
  - CORS middleware configuration
  - Lifespan management (startup/shutdown)
  - Health check endpoints
  - Compliance evaluation endpoints
  - Feature flag management
  - Audit logging

### 2. Database Layer (`src/core/database.py`)

- **Purpose**: Database connection and session management
- **Features**:
  - Connection pooling with SQLAlchemy
  - Enhanced connection leak detection
  - Health monitoring and metrics
  - Transaction management
  - Migration support

### 3. Compliance Engine (`src/core/compliance.py`)

- **Purpose**: Core compliance evaluation logic
- **Features**:
  - Policy mapping evaluation
  - Regulatory framework support (CMA, MOI, MoH, NCA)
  - Caching for performance
  - Audit trail generation

### 4. Observability System

- **Logging**: Structured JSON logging with correlation IDs
- **Metrics**: Prometheus-compatible metrics collection
- **Tracing**: Distributed tracing support
- **Health Checks**: Comprehensive system health monitoring

### 5. Feature Flag Management (`src/services/feature_flags.py`)

- **Purpose**: Configuration-driven feature rollouts
- **Features**:
  - A/B testing support
  - Gradual rollout strategies
  - User segmentation
  - Real-time configuration updates

## Data Flow

### 1. Compliance Evaluation Flow

```
1. API Request → FastAPI Endpoint
2. Request Validation → Pydantic Models
3. Service Layer → ComplianceEngine
4. Policy Evaluation → Mapping Files
5. Database Operations → Audit Logging
6. Response Generation → JSON Response
```

### 2. Health Check Flow

```
1. Health Request → Health Endpoint
2. System Checks → Database, Cache, File System
3. Metrics Collection → Performance Data
4. Status Aggregation → Overall Health Status
5. Response → Health Report
```

## Configuration Management

### Settings Hierarchy

1. **Environment Variables**: Highest priority
2. **Configuration Files**: `.env` files
3. **Default Values**: Defined in `src/core/settings.py`

### Configuration Categories

- **Database**: Connection strings, pool settings
- **API**: Host, port, CORS settings
- **Security**: Authentication, rate limiting
- **Observability**: Logging, metrics, tracing
- **Feature Flags**: Rollout configurations

## Security Architecture

### Security Layers

1. **Network Security**: HTTPS, CORS, rate limiting
2. **Authentication**: API key validation
3. **Authorization**: Role-based access control
4. **Data Protection**: Encryption at rest and in transit
5. **Audit Logging**: Comprehensive audit trails

### Security Best Practices

- No secrets in code or configuration files
- Environment-based secret management
- Regular security scanning in CI/CD
- Principle of least privilege
- Input validation and sanitization

## Deployment Architecture

### Development Environment

- Local development with hot reload
- SQLite for local testing
- Docker Compose for full stack

### Staging Environment

- Kubernetes deployment
- PostgreSQL database
- Redis caching
- Full observability stack

### Production Environment

- High availability Kubernetes cluster
- Database clustering and replication
- Load balancing and auto-scaling
- Comprehensive monitoring and alerting

## Monitoring and Observability

### Metrics

- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Compliance evaluations, policy coverage
- **Infrastructure Metrics**: CPU, memory, disk, network

### Logging

- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized log collection and analysis

### Alerting

- **Critical Alerts**: System failures, security incidents
- **Warning Alerts**: Performance degradation, capacity issues
- **Business Alerts**: Compliance violations, audit failures

## Performance Considerations

### Optimization Strategies

1. **Database Optimization**:
   - Connection pooling
   - Query optimization
   - Indexing strategies
   - Read replicas for scaling

2. **Caching Strategy**:
   - Redis for session data
   - Application-level caching
   - CDN for static assets

3. **API Performance**:
   - Async/await patterns
   - Request/response compression
   - Pagination for large datasets

## Scalability Architecture

### Horizontal Scaling

- Stateless application design
- Load balancer distribution
- Database read replicas
- Microservices decomposition

### Vertical Scaling

- Resource optimization
- Performance profiling
- Memory management
- CPU optimization

## Disaster Recovery

### Backup Strategy

- **Database Backups**: Daily automated backups
- **Configuration Backups**: Version-controlled configs
- **Application Backups**: Container image versioning

### Recovery Procedures

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Failover Procedures**: Automated with manual override

## Compliance and Governance

### Regulatory Compliance

- **Data Protection**: GDPR, local data protection laws
- **Financial Regulations**: CMA compliance
- **Healthcare Regulations**: MoH compliance
- **Telecommunications**: NCA compliance

### Governance Framework

- **Service Catalog**: Centralized service registry
- **SLA Management**: Service level agreements
- **Change Management**: Controlled deployment processes
- **Incident Management**: Structured incident response

## Future Architecture Considerations

### Planned Enhancements

1. **Microservices Migration**: Gradual decomposition
2. **Event-Driven Architecture**: Async messaging
3. **Machine Learning Integration**: AI-powered compliance
4. **Multi-Region Deployment**: Global availability

### Technology Roadmap

- **Container Orchestration**: Kubernetes adoption
- **Service Mesh**: Istio implementation
- **Serverless Functions**: Event processing
- **Data Analytics**: Real-time compliance analytics

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-29  
**Next Review**: 2025-11-29  
**Owner**: DoganAI Platform Team