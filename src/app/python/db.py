"""
DoganAI Compliance Kit - Database Adapter
Provides database connection and tenant session management
"""

import os
import uuid
from contextlib import contextmanager
from typing import Optional, Generator, Any
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import structlog

# Configure logging
logger = structlog.get_logger()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/doganai"
)

# Engine configuration for production
ENGINE = create_engine(
    DATABASE_URL,
    future=True,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("DB_ECHO", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(
    bind=ENGINE, 
    autoflush=False, 
    autocommit=False,
    expire_on_commit=False
)

# Tenant session context
class TenantContext:
    """Context manager for tenant-aware database sessions"""
    
    def __init__(self, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.session: Optional[Session] = None
    
    def __enter__(self):
        self.session = SessionLocal()
        # Set tenant context for RLS policies
        self.session.execute(
            text("SET app.current_tenant_id = :tid"), 
            {"tid": str(self.tenant_id)}
        )
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

@contextmanager
def tenant_session(tenant_id: uuid.UUID) -> Generator[Session, None, None]:
    """
    Context manager for tenant-aware database sessions.
    
    Args:
        tenant_id: UUID of the tenant to set in session context
        
    Yields:
        SQLAlchemy Session with tenant context set
        
    Example:
        ```python
        from db import tenant_session
        import uuid
        
        tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        
        with tenant_session(tenant_id) as session:
            # All queries will be scoped to this tenant
            users = session.execute(
                text("SELECT * FROM users")
            ).fetchall()
        ```
    """
    context = TenantContext(tenant_id)
    try:
        with context as session:
            yield session
    except SQLAlchemyError as e:
        logger.error("Database error in tenant session", 
                    tenant_id=str(tenant_id), 
                    error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error in tenant session", 
                    tenant_id=str(tenant_id), 
                    error=str(e))
        raise

def get_tenant_session(tenant_id: uuid.UUID) -> Session:
    """
    Get a tenant-aware database session.
    
    Args:
        tenant_id: UUID of the tenant to set in session context
        
    Returns:
        SQLAlchemy Session with tenant context set
        
    Note:
        This method returns a session that must be manually closed.
        Prefer using tenant_session() context manager for automatic cleanup.
    """
    session = SessionLocal()
    try:
        session.execute(
            text("SET app.current_tenant_id = :tid"), 
            {"tid": str(tenant_id)}
        )
        return session
    except SQLAlchemyError as e:
        session.close()
        logger.error("Failed to create tenant session", 
                    tenant_id=str(tenant_id), 
                    error=str(e))
        raise

def close_tenant_session(session: Session) -> None:
    """
    Close a tenant session.
    
    Args:
        session: SQLAlchemy Session to close
    """
    if session:
        session.close()

# Database health check
def check_database_health() -> dict[str, Any]:
    """
    Check database connectivity and health.
    
    Returns:
        Dictionary with health status and details
    """
    try:
        with ENGINE.connect() as conn:
            # Check basic connectivity
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            # Check PostgreSQL version
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # Check extensions
            extensions_result = conn.execute(text("""
                SELECT extname FROM pg_extension 
                WHERE extname IN ('pgcrypto','uuid-ossp','vector','pg_trgm','citext')
                ORDER BY extname
            """))
            extensions = [row[0] for row in extensions_result.fetchall()]
            
            # Check RLS status
            rls_result = conn.execute(text("""
                SELECT COUNT(*) FROM pg_tables 
                WHERE schemaname = 'public' AND rowsecurity = true
            """))
            rls_tables = rls_result.fetchone()[0]
            
            return {
                "status": "healthy",
                "version": version,
                "extensions": extensions,
                "rls_tables": rls_tables,
                "timestamp": "2025-08-26T00:00:00Z"
            }
            
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-08-26T00:00:00Z"
        }

# Database initialization
def init_database() -> None:
    """
    Initialize database connection and verify setup.
    """
    try:
        # Test connection
        health = check_database_health()
        if health["status"] == "healthy":
            logger.info("Database initialized successfully", 
                       extensions=health["extensions"],
                       rls_tables=health["rls_tables"])
        else:
            logger.error("Database health check failed", health=health)
            raise Exception("Database initialization failed")
            
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

# Connection pool monitoring
def get_connection_pool_status() -> dict[str, Any]:
    """
    Get connection pool status and statistics.
    
    Returns:
        Dictionary with pool status information
    """
    pool = ENGINE.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }

# Event listeners for connection management
@event.listens_for(ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection-level settings for SQLite (if used)"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@event.listens_for(ENGINE, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout events"""
    logger.debug("Database connection checked out", 
                connection_id=id(connection_proxy))

@event.listens_for(ENGINE, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin events"""
    logger.debug("Database connection checked in", 
                connection_id=id(connection_record))

# Utility functions
def execute_query(tenant_id: uuid.UUID, query: str, params: dict = None) -> list:
    """
    Execute a query in tenant context.
    
    Args:
        tenant_id: UUID of the tenant
        query: SQL query to execute
        params: Query parameters
        
    Returns:
        List of results
    """
    with tenant_session(tenant_id) as session:
        result = session.execute(text(query), params or {})
        return result.fetchall()

def execute_command(tenant_id: uuid.UUID, command: str, params: dict = None) -> int:
    """
    Execute a command (INSERT, UPDATE, DELETE) in tenant context.
    
    Args:
        tenant_id: UUID of the tenant
        command: SQL command to execute
        params: Command parameters
        
    Returns:
        Number of affected rows
    """
    with tenant_session(tenant_id) as session:
        result = session.execute(text(command), params or {})
        session.commit()
        return result.rowcount

# Initialize database on module import
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.warning("Database initialization deferred", error=str(e))
