# 🔄 Application Update Guide for Enhanced Database Architecture

This guide provides step-by-step instructions for updating your application code to use the new unified database interface.

## 📋 Overview

The enhanced database architecture provides a unified interface that abstracts away the complexity of multiple database systems. Your application code will be simplified while gaining access to:

- **PostgreSQL**: Primary relational data storage
- **Redis**: High-performance caching and session management
- **TimescaleDB**: Time-series data optimization
- **Elasticsearch**: Advanced search and analytics

## 🚀 Quick Start

### 1. Import the Hybrid Database Manager

```python
from engine.hybrid_database_manager import get_hybrid_manager

# Get the global hybrid manager instance
hybrid_manager = get_hybrid_manager()
```

### 2. Initialize the System

```python
# Initialize all database connections
success = hybrid_manager.initialize()
if not success:
    raise Exception("Failed to initialize database connections")
```

## 📝 Data Operations

### Writing Data

The hybrid manager automatically routes data to the most appropriate database based on data type and operation.

```python
# Write compliance data (goes to PostgreSQL)
compliance_data = {
    "entity_id": "COMP_001",
    "compliance_type": "regulatory",
    "status": "active",
    "title": "GDPR Compliance Report",
    "description": "Annual GDPR compliance assessment",
    "details": {"regulation": "GDPR", "score": 95.5},
    "tags": ["gdpr", "privacy", "annual"]
}

success = hybrid_manager.write_data(
    data_type="compliance",
    data=compliance_data,
    operation="write"
)

# Write cache data (goes to Redis)
cache_data = {
    "key": "user_session_123",
    "value": {"user_id": "123", "permissions": ["read", "write"]},
    "ttl": 3600
}

success = hybrid_manager.write_data(
    data_type="cache",
    data=cache_data,
    operation="cache"
)

# Write performance metrics (goes to TimescaleDB)
metric_data = {
    "metric_name": "api_response_time",
    "value": 150.5,
    "unit": "ms",
    "tags": {"service": "compliance_api", "endpoint": "/api/v1/compliance"}
}

success = hybrid_manager.write_data(
    data_type="metric",
    data=metric_data,
    operation="timeseries"
)

# Write search documents (goes to Elasticsearch)
document_data = {
    "title": "Compliance Policy Document",
    "content": "This document outlines our compliance policies...",
    "document_type": "policy",
    "category": "compliance",
    "tags": ["policy", "compliance", "internal"]
}

success = hybrid_manager.write_data(
    data_type="document",
    data=document_data,
    operation="search"
)
```

### Reading Data

```python
# Read compliance data from PostgreSQL
compliance_records = hybrid_manager.read_data(
    data_type="compliance",
    filters={"status": "active", "compliance_type": "regulatory"},
    operation="read"
)

# Read cache data from Redis
cached_data = hybrid_manager.read_data(
    data_type="cache",
    filters={"key": "user_session_123"},
    operation="cache"
)

# Read time-series data from TimescaleDB
metrics = hybrid_manager.read_data(
    data_type="metric",
    filters={"metric_name": "api_response_time"},
    operation="timeseries"
)
```

### Searching Data

```python
# Search compliance documents
search_results = hybrid_manager.search_data(
    data_type="compliance",
    query="GDPR compliance",
    filters={"status": "active"},
    operation="search"
)

# Search audit trail
audit_results = hybrid_manager.search_data(
    data_type="audit",
    query="user login",
    filters={"action": "login"},
    operation="search"
)
```

### Getting Analytics

```python
# Get compliance analytics
compliance_analytics = hybrid_manager.get_analytics(
    data_type="compliance",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    operation="analytics"
)

# Get performance metrics analytics
performance_analytics = hybrid_manager.get_analytics(
    data_type="metric",
    start_date=datetime.now() - timedelta(hours=24),
    end_date=datetime.now(),
    operation="analytics"
)
```

## 🔧 Migration from Old Code

### Before (Old Database Code)

```python
# Old way - direct database operations
from engine.database import get_database_manager

db_manager = get_database_manager()

# Write compliance data
db_manager.execute_query(
    "INSERT INTO compliance (entity_id, type, status, title) VALUES (%s, %s, %s, %s)",
    (entity_id, compliance_type, status, title)
)

# Cache operations (if any)
# No built-in caching

# Search operations (if any)
# Basic SQL LIKE queries
```

### After (New Unified Interface)

```python
# New way - unified interface
from engine.hybrid_database_manager import get_hybrid_manager

hybrid_manager = get_hybrid_manager()

# Write compliance data (automatically optimized)
success = hybrid_manager.write_data(
    data_type="compliance",
    data={
        "entity_id": entity_id,
        "compliance_type": compliance_type,
        "status": status,
        "title": title
    },
    operation="write"
)

# Automatic caching
# Search capabilities included
```

## 🏗️ API Integration

### FastAPI Integration Example

```python
from fastapi import FastAPI, HTTPException
from engine.hybrid_database_manager import get_hybrid_manager
from datetime import datetime, timedelta

app = FastAPI()
hybrid_manager = get_hybrid_manager()

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    success = hybrid_manager.initialize()
    if not success:
        raise Exception("Failed to initialize database connections")

@app.post("/compliance")
async def create_compliance_record(compliance_data: dict):
    """Create a new compliance record"""
    try:
        success = hybrid_manager.write_data(
            data_type="compliance",
            data=compliance_data,
            operation="write"
        )
        
        if success:
            return {"status": "success", "message": "Compliance record created"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create record")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compliance/search")
async def search_compliance_records(query: str, status: str = None):
    """Search compliance records"""
    try:
        filters = {}
        if status:
            filters["status"] = status
            
        results = hybrid_manager.search_data(
            data_type="compliance",
            query=query,
            filters=filters,
            operation="search"
        )
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/compliance")
async def get_compliance_analytics(days: int = 30):
    """Get compliance analytics"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        analytics = hybrid_manager.get_analytics(
            data_type="compliance",
            start_date=start_date,
            end_date=end_date,
            operation="analytics"
        )
        
        return {"analytics": analytics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🔍 Health Monitoring

```python
# Check system health
health_status = hybrid_manager.health_check()

if health_status["status"] == "healthy":
    print("All databases are operational")
else:
    print(f"Health issues detected: {health_status['message']}")
    
# Get detailed health information
for db_type, status in health_status["database_health"].items():
    print(f"{db_type}: {status['status']}")
```

## 🎯 Best Practices

### 1. Use Appropriate Data Types

```python
# ✅ Good - Use specific data types
hybrid_manager.write_data(
    data_type="compliance",  # Clear data type
    data=compliance_data,
    operation="write"
)

# ❌ Avoid - Generic data types
hybrid_manager.write_data(
    data_type="data",  # Too generic
    data=compliance_data,
    operation="write"
)
```

### 2. Handle Errors Gracefully

```python
try:
    success = hybrid_manager.write_data(
        data_type="compliance",
        data=compliance_data,
        operation="write"
    )
    
    if not success:
        # Log error and handle gracefully
        logger.error("Failed to write compliance data")
        # Fallback to alternative storage or retry logic
        
except Exception as e:
    logger.error(f"Database operation failed: {e}")
    # Implement appropriate error handling
```

### 3. Use Transactions for Complex Operations

```python
# Use transaction context for multi-database operations
with hybrid_manager.transaction():
    # Write to PostgreSQL
    hybrid_manager.write_data(
        data_type="compliance",
        data=compliance_data,
        operation="write"
    )
    
    # Write to Elasticsearch for search
    hybrid_manager.write_data(
        data_type="document",
        data=search_data,
        operation="search"
    )
    
    # Write audit trail
    hybrid_manager.write_data(
        data_type="audit",
        data=audit_data,
        operation="write"
    )
```

### 4. Optimize for Performance

```python
# Use bulk operations for large datasets
bulk_data = [record1, record2, record3, ...]

for batch in chunks(bulk_data, 1000):  # Process in batches
    hybrid_manager.write_data(
        data_type="compliance",
        data=batch,
        operation="bulk_write"
    )
```

## 🔧 Configuration

### Environment Variables

Update your environment configuration to include the new database settings:

```bash
# PostgreSQL Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=doganai_compliance
PGUSER=postgres
PGPASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DATABASE=0

# TimescaleDB Configuration (uses PostgreSQL settings)
TIMESCALEDB_HOST=localhost
TIMESCALEDB_PORT=5432
TIMESCALEDB_DATABASE=doganai_compliance

# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
```

### Settings Integration

The new database configurations are automatically loaded from your `settings.py`:

```python
from settings import Settings

settings = Settings()

# Access database configurations
postgres_config = settings.database
redis_config = settings.redis
timescale_config = settings.timescaledb
elasticsearch_config = settings.elasticsearch
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from engine.hybrid_database_manager import get_hybrid_manager

@pytest.fixture
def hybrid_manager():
    """Test fixture for hybrid database manager"""
    manager = get_hybrid_manager()
    # Initialize for testing
    manager.initialize()
    yield manager
    # Cleanup after tests

def test_write_compliance_data(hybrid_manager):
    """Test writing compliance data"""
    test_data = {
        "entity_id": "TEST_001",
        "compliance_type": "test",
        "status": "active",
        "title": "Test Compliance Record"
    }
    
    success = hybrid_manager.write_data(
        data_type="compliance",
        data=test_data,
        operation="write"
    )
    
    assert success is True

def test_search_compliance_data(hybrid_manager):
    """Test searching compliance data"""
    results = hybrid_manager.search_data(
        data_type="compliance",
        query="test",
        operation="search"
    )
    
    assert "results" in results
```

## 📊 Monitoring and Observability

### Performance Metrics

```python
# Get performance metrics
metrics = hybrid_manager.get_analytics(
    data_type="metric",
    start_date=datetime.now() - timedelta(hours=1),
    end_date=datetime.now(),
    operation="analytics"
)

# Monitor database performance
for db_type, metrics in metrics.items():
    print(f"{db_type} performance: {metrics}")
```

### Health Checks

```python
# Regular health checks
def check_database_health():
    health = hybrid_manager.health_check()
    
    if health["status"] != "healthy":
        # Send alert
        send_alert(f"Database health issue: {health['message']}")
    
    return health["status"] == "healthy"

# Schedule health checks
import schedule
import time

schedule.every(5).minutes.do(check_database_health)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 🚀 Deployment Checklist

- [ ] Update environment variables with new database configurations
- [ ] Install new dependencies (`redis`, `elasticsearch`, etc.)
- [ ] Set up database servers (Redis, PostgreSQL with TimescaleDB, Elasticsearch)
- [ ] Run data migration script
- [ ] Update application code to use new unified interface
- [ ] Test all database operations
- [ ] Monitor performance and health
- [ ] Update documentation

## 📞 Support

If you encounter issues during the migration:

1. Check the health status: `hybrid_manager.health_check()`
2. Review the logs for detailed error messages
3. Verify database connections and configurations
4. Test individual database managers if needed

## 🎉 Benefits

After migrating to the enhanced database architecture, you'll have:

- **Simplified Code**: Single interface for all database operations
- **Better Performance**: Optimized data storage and retrieval
- **Advanced Search**: Full-text search capabilities
- **Real-time Analytics**: Time-series data analysis
- **High Availability**: Multiple database systems with failover
- **Scalability**: Each database optimized for its specific use case

---

**Next Steps**: 
1. Review your existing code and identify database operations
2. Update the operations to use the new unified interface
3. Test thoroughly in a staging environment
4. Deploy to production with monitoring enabled
