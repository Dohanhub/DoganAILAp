"""
Database connection and session management for DoganAI Compliance Kit
Production-ready with connection pooling, health checks, and error handling
"""

import os
import logging
import time
import threading
import weakref
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any, List, Set
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError, TimeoutError
from sqlalchemy.dialects.postgresql import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime, timezone, timedelta
import structlog
from collections import defaultdict

from .settings import settings
from .models import Base, create_tables, drop_tables

logger = structlog.get_logger(__name__)

# =============================================================================
# CONNECTION LEAK DETECTION
# =============================================================================

class ConnectionLeakDetector:
    """Detect and track database connection leaks"""
    
    def __init__(self):
        self._active_connections: Set[int] = set()
        self._connection_timestamps: Dict[int, datetime] = {}
        self._lock = threading.Lock()
        self._leak_threshold = 300  # 5 minutes
        self._max_connections = 100
        
    def register_connection(self, connection_id: int):
        """Register a new connection"""
        with self._lock:
            self._active_connections.add(connection_id)
            self._connection_timestamps[connection_id] = datetime.now(timezone.utc)
            
            if len(self._active_connections) > self._max_connections:
                logger.warning(
                    "High number of active connections detected",
                    active_count=len(self._active_connections),
                    max_threshold=self._max_connections
                )
    
    def unregister_connection(self, connection_id: int):
        """Unregister a connection"""
        with self._lock:
            self._active_connections.discard(connection_id)
            self._connection_timestamps.pop(connection_id, None)
    
    def check_for_leaks(self) -> Dict[str, Any]:
        """Check for potential connection leaks"""
        with self._lock:
            current_time = datetime.now(timezone.utc)
            leaked_connections = []
            
            for conn_id, timestamp in self._connection_timestamps.items():
                age = (current_time - timestamp).total_seconds()
                if age > self._leak_threshold:
                    leaked_connections.append({
                        "connection_id": conn_id,
                        "age_seconds": age,
                        "timestamp": timestamp.isoformat()
                    })
            
            return {
                "active_connections": len(self._active_connections),
                "leaked_connections": leaked_connections,
                "leak_count": len(leaked_connections),
                "max_threshold": self._max_connections,
                "leak_threshold_seconds": self._leak_threshold
            }

# =============================================================================
# ENHANCED DATABASE CONNECTION POOL
# =============================================================================

class EnhancedDatabaseManager:
    """Enhanced database connection manager with advanced pooling and monitoring"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.connection_pool: Optional[SimpleConnectionPool] = None
        self._lock = threading.Lock()
        self._health_status = "unknown"
        self._last_health_check = None
        self._health_check_interval = 30  # seconds
        self._connection_errors = 0
        self._max_connection_errors = 5
        self._leak_detector = ConnectionLeakDetector()
        self._connection_metrics = defaultdict(int)
        self._last_metrics_reset = datetime.now(timezone.utc)
        self._metrics_reset_interval = 3600  # 1 hour
        
        # Enhanced timeout configurations
        self._connect_timeout = 10
        self._read_timeout = 30
        self._write_timeout = 30
        self._pool_timeout = 30
        self._statement_timeout = 300  # 5 minutes
        
    def initialize(self) -> bool:
        """Initialize database connections with enhanced configuration"""
        try:
            with self._lock:
                if self.engine is not None:
                    logger.info("Database already initialized")
                    return True
                
                # Create database URL with optimized parameters
                database_url = self._build_enhanced_database_url()
                
                # Create engine with enhanced connection pooling
                self.engine = create_engine(
                    database_url,
                    poolclass=QueuePool,
                    pool_size=settings.database.pool_size,
                    max_overflow=settings.database.max_overflow,
                    pool_pre_ping=True,
                    pool_recycle=3600,  # Recycle connections every hour
                    pool_timeout=self._pool_timeout,
                    pool_reset_on_return='commit',  # Reset connections on return
                    echo=settings.database.echo,
                    connect_args={
                        "connect_timeout": self._connect_timeout,
                        "application_name": f"{settings.app_name}-{settings.app_version}",
                        "options": f"-c timezone={settings.database.timezone} -c statement_timeout={self._statement_timeout}000"
                    }
                )
                
                # Create session factory with optimized settings
                self.session_factory = sessionmaker(
                    bind=self.engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
                
                # Test connection with timeout
                if not self._test_connection_with_timeout():
                    raise Exception("Failed to establish initial database connection")
                
                # Set up enhanced connection event listeners
                self._setup_enhanced_connection_events()
                
                # Create tables if they don't exist
                self._create_tables_if_needed()
                
                logger.info(
                    "Enhanced database initialized successfully",
                    host=settings.database.host,
                    database=settings.database.database,
                    pool_size=settings.database.pool_size,
                    max_overflow=settings.database.max_overflow,
                    connect_timeout=self._connect_timeout,
                    statement_timeout=self._statement_timeout
                )
                
                return True
            
        except Exception as e:
            logger.error(
                "Failed to initialize enhanced database",
                error=str(e),
                host=settings.database.host,
                database=settings.database.database,
                exc_info=True
            )
            return False
    
    def _build_enhanced_database_url(self) -> str:
        """Build database connection URL with optimized parameters"""
        base_url = f"postgresql://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.database}"
        
        # Enhanced connection parameters
        params = []
        
        # Timezone
        params.append(f"timezone={settings.database.timezone}")
        
        # SSL configuration
        if settings.database.ssl_mode != "disable":
            params.append(f"sslmode={settings.database.ssl_mode}")
            
            if settings.database.ssl_cert:
                params.append(f"sslcert={settings.database.ssl_cert}")
            if settings.database.ssl_key:
                params.append(f"sslkey={settings.database.ssl_key}")
            if settings.database.ssl_ca:
                params.append(f"sslrootcert={settings.database.ssl_ca}")
        
        # Optimized connection parameters
        params.extend([
            "connect_timeout=10",
            "application_name=DoganAI-Compliance-Kit",
            "client_encoding=utf8",
            "tcp_keepalives_idle=600",
            "tcp_keepalives_interval=30",
            "tcp_keepalives_count=3"
        ])
        
        return f"{base_url}?{'&'.join(params)}"
    
    def _setup_enhanced_connection_events(self):
        """Set up enhanced database connection event listeners"""
        @event.listens_for(self.engine, "connect")
        def set_enhanced_connection_params(dbapi_connection, connection_record):
            """Set enhanced PostgreSQL connection parameters"""
            if hasattr(dbapi_connection, 'set_session'):
                with dbapi_connection.cursor() as cursor:
                    # Set optimized session parameters
                    cursor.execute(f"SET timezone = '{settings.database.timezone}'")
                    cursor.execute("SET client_encoding = 'UTF8'")
                    cursor.execute("SET application_name = %s", (f"{settings.app_name}-{settings.app_version}",))
                    cursor.execute(f"SET statement_timeout = {self._statement_timeout}000")
                    cursor.execute("SET lock_timeout = 30000")  # 30 seconds
                    cursor.execute("SET idle_in_transaction_session_timeout = 300000")  # 5 minutes
                    
                    # Register connection for leak detection
                    conn_id = id(dbapi_connection)
                    self._leak_detector.register_connection(conn_id)
                    self._connection_metrics['connections_created'] += 1
        
        @event.listens_for(self.engine, "checkout")
        def receive_enhanced_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle enhanced connection checkout"""
            conn_id = id(dbapi_connection)
            self._connection_metrics['connections_checked_out'] += 1
            logger.debug("Database connection checked out", connection_id=conn_id)
        
        @event.listens_for(self.engine, "checkin")
        def receive_enhanced_checkin(dbapi_connection, connection_record):
            """Handle enhanced connection checkin"""
            conn_id = id(dbapi_connection)
            self._connection_metrics['connections_checked_in'] += 1
            self._leak_detector.unregister_connection(conn_id)
            logger.debug("Database connection checked in", connection_id=conn_id)
        
        @event.listens_for(self.engine, "disconnect")
        def receive_enhanced_disconnect(dbapi_connection, connection_record):
            """Handle enhanced connection disconnect"""
            conn_id = id(dbapi_connection)
            self._leak_detector.unregister_connection(conn_id)
            self._connection_metrics['connections_disconnected'] += 1
            logger.warning("Database connection disconnected", connection_id=conn_id)
    
    def _test_connection_with_timeout(self) -> bool:
        """Test database connection with timeout"""
        try:
            with self.engine.connect() as connection:
                # Set a timeout for the test query
                connection.execute(text("SET statement_timeout = 10000"))  # 10 seconds
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                return True
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            return False
    
    def _create_tables_if_needed(self):
        """Create database tables if they don't exist"""
        try:
            create_tables(self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            raise
    
    def get_session(self) -> Session:
        """Get a new database session with leak detection"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.session_factory()
        self._connection_metrics['sessions_created'] += 1
        return session
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with enhanced monitoring"""
        session = self.get_session()
        start_time = time.time()
        
        try:
            yield session
            session.commit()
            self._connection_metrics['sessions_committed'] += 1
        except Exception as e:
            session.rollback()
            self._connection_metrics['sessions_rolled_back'] += 1
            logger.error(
                "Database session error",
                error=str(e),
                duration=time.time() - start_time,
                exc_info=True
            )
            raise
        finally:
            session.close()
            self._connection_metrics['sessions_closed'] += 1
    
    def health_check(self) -> Dict[str, Any]:
        """Perform enhanced database health check"""
        current_time = time.time()
        
        # Check if we need to perform health check
        if (self._last_health_check and 
            current_time - self._last_health_check < self._health_check_interval):
            return {
                "status": self._health_status,
                "last_check": self._last_health_check,
                "message": "Using cached health status"
            }
        
        try:
            # Test connection with timeout
            if self._test_connection_with_timeout():
                self._health_status = "healthy"
                self._connection_errors = 0
                message = "Database connection is healthy"
            else:
                self._health_status = "unhealthy"
                self._connection_errors += 1
                message = f"Database connection test failed ({self._connection_errors} consecutive failures)"
            
            # Get enhanced pool status
            pool_status = self._get_enhanced_pool_status()
            
            # Check for connection leaks
            leak_status = self._leak_detector.check_for_leaks()
            
            # Get connection metrics
            connection_metrics = self._get_connection_metrics()
            
            self._last_health_check = current_time
            
            return {
                "status": self._health_status,
                "last_check": current_time,
                "message": message,
                "connection_errors": self._connection_errors,
                "pool_status": pool_status,
                "leak_status": leak_status,
                "connection_metrics": connection_metrics,
                "timeout_config": {
                    "connect_timeout": self._connect_timeout,
                    "read_timeout": self._read_timeout,
                    "write_timeout": self._write_timeout,
                    "pool_timeout": self._pool_timeout,
                    "statement_timeout": self._statement_timeout
                }
            }
            
        except Exception as e:
            self._health_status = "error"
            self._connection_errors += 1
            logger.error("Enhanced database health check failed", error=str(e), exc_info=True)
            
            return {
                "status": "error",
                "last_check": current_time,
                "message": f"Health check error: {str(e)}",
                "connection_errors": self._connection_errors
            }
    
    def _get_enhanced_pool_status(self) -> Dict[str, Any]:
        """Get enhanced connection pool status"""
        if not self.engine:
            return {"error": "Engine not initialized"}
        
        try:
            pool = self.engine.pool
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "pool_class": pool.__class__.__name__,
                "pool_timeout": self._pool_timeout
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_connection_metrics(self) -> Dict[str, Any]:
        """Get connection metrics"""
        current_time = datetime.now(timezone.utc)
        
        # Reset metrics if interval has passed
        if (current_time - self._last_metrics_reset).total_seconds() > self._metrics_reset_interval:
            self._connection_metrics.clear()
            self._last_metrics_reset = current_time
        
        return dict(self._connection_metrics)
    
    def close(self):
        """Close all database connections with cleanup"""
        try:
            with self._lock:
                if self.engine:
                    # Check for leaks before closing
                    leak_status = self._leak_detector.check_for_leaks()
                    if leak_status['leak_count'] > 0:
                        logger.warning(
                            "Connection leaks detected during shutdown",
                            leak_count=leak_status['leak_count'],
                            leaked_connections=leak_status['leaked_connections']
                        )
                    
                    self.engine.dispose()
                    self.engine = None
                    self.session_factory = None
                    logger.info("Enhanced database connections closed")
        except Exception as e:
            logger.error("Error closing enhanced database connections", error=str(e))
    
    def reset_connection_pool(self):
        """Reset the connection pool with leak detection"""
        try:
            with self._lock:
                if self.engine:
                    # Check for leaks before reset
                    leak_status = self._leak_detector.check_for_leaks()
                    if leak_status['leak_count'] > 0:
                        logger.warning(
                            "Connection leaks detected before pool reset",
                            leak_count=leak_status['leak_count']
                        )
                    
                    self.engine.dispose()
                    logger.info("Enhanced database connection pool reset")
        except Exception as e:
            logger.error("Error resetting enhanced connection pool", error=str(e))

# =============================================================================
# GLOBAL ENHANCED DATABASE MANAGER INSTANCE
# =============================================================================

_db_manager: Optional[EnhancedDatabaseManager] = None

def get_db_manager() -> EnhancedDatabaseManager:
    """Get the global enhanced database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = EnhancedDatabaseManager()
    return _db_manager

def initialize_database() -> bool:
    """Initialize the global enhanced database connection"""
    return get_db_manager().initialize()

def close_database():
    """Close the global enhanced database connection"""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None

# =============================================================================
# ENHANCED SESSION MANAGEMENT FUNCTIONS
# =============================================================================

def get_db_session() -> Generator[Session, None, None]:
    """Get a database session with enhanced monitoring (for dependency injection)"""
    db_manager = get_db_manager()
    
    if not db_manager.engine:
        raise RuntimeError("Database not initialized")
    
    session = db_manager.get_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def get_db_session_context() -> Generator[Session, None, None]:
    """Context manager for database sessions with enhanced monitoring"""
    db_manager = get_db_manager()
    
    if not db_manager.engine:
        raise RuntimeError("Database not initialized")
    
    with db_manager.get_session_context() as session:
        yield session

# =============================================================================
# ENHANCED DATABASE UTILITY FUNCTIONS
# =============================================================================

def execute_query(query: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> Any:
    """Execute a raw SQL query with timeout support"""
    with get_db_session_context() as session:
        try:
            if timeout:
                session.execute(text(f"SET statement_timeout = {timeout * 1000}"))
            
            result = session.execute(text(query), params or {})
            return result.fetchall()
        except Exception as e:
            logger.error("Query execution failed", query=query, params=params, timeout=timeout, error=str(e))
            raise

def execute_transaction(queries: list, timeout: Optional[int] = None) -> bool:
    """Execute multiple queries in a transaction with timeout"""
    with get_db_session_context() as session:
        try:
            if timeout:
                session.execute(text(f"SET statement_timeout = {timeout * 1000}"))
            
            for query, params in queries:
                session.execute(text(query), params or {})
                session.commit()
                return True
        except Exception as e:
            logger.error("Transaction execution failed", queries=queries, timeout=timeout, error=str(e))
            session.rollback()
            return False
    
def get_table_info(table_name: str) -> Dict[str, Any]:
    """Get information about a database table"""
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length
    FROM information_schema.columns 
    WHERE table_name = :table_name
    ORDER BY ordinal_position
    """
    
    try:
        result = execute_query(query, {"table_name": table_name})
        return {
            "table_name": table_name,
            "columns": [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] == "YES",
                    "default": row[3],
                    "max_length": row[4]
                }
                for row in result
            ]
        }
    except Exception as e:
        logger.error("Failed to get table info", table_name=table_name, error=str(e))
        return {"error": str(e)}

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        # Get table sizes
        size_query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """
        
        # Get connection count
        conn_query = "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
        
        # Get database size
        db_size_query = "SELECT pg_size_pretty(pg_database_size(current_database()))"
        
        with get_db_session_context() as session:
            # Table sizes
            size_result = session.execute(text(size_query))
            table_sizes = [{"table": row[1], "size": row[2]} for row in size_result]
            
            # Connection count
            conn_result = session.execute(text(conn_query))
            connection_count = conn_result.scalar()
            
            # Database size
            db_size_result = session.execute(text(db_size_query))
            database_size = db_size_result.scalar()
            
            return {
                "database_size": database_size,
                "active_connections": connection_count,
                "table_sizes": table_sizes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error("Failed to get database stats", error=str(e))
        return {"error": str(e)}

# =============================================================================
# MIGRATION AND SCHEMA MANAGEMENT
# =============================================================================

def run_migrations() -> bool:
    """Run database migrations"""
    try:
        # This would integrate with Alembic for proper migrations
        # For now, we'll just create tables
        db_manager = get_db_manager()
        if db_manager.engine:
            create_tables(db_manager.engine)
            logger.info("Database migrations completed successfully")
            return True
        return False
    except Exception as e:
        logger.error("Database migration failed", error=str(e))
        return False
    
def backup_database(backup_path: str) -> bool:
    """Create database backup"""
    try:
        # This would use pg_dump for PostgreSQL backups
        import subprocess
        
        backup_cmd = [
            "pg_dump",
            "-h", settings.database.host,
            "-p", str(settings.database.port),
            "-U", settings.database.user,
            "-d", settings.database.database,
            "-f", backup_path,
            "--verbose"
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.database.password
        
        result = subprocess.run(
            backup_cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Database backup created successfully: {backup_path}")
            return True
        else:
            logger.error("Database backup failed", stderr=result.stderr)
            return False
                
    except Exception as e:
        logger.error("Database backup failed", error=str(e))
        return False
    
# =============================================================================
# HEALTH CHECK INTEGRATION
# =============================================================================

def check_database_health() -> Dict[str, Any]:
    """Check database health for health check endpoints"""
    db_manager = get_db_manager()
    return db_manager.health_check()

# =============================================================================
# INITIALIZATION
# =============================================================================

def setup_database():
    """Setup database during application startup"""
    try:
        if initialize_database():
            logger.info("Database setup completed successfully")
            return True
        else:
            logger.error("Database setup failed")
            return False
    except Exception as e:
        logger.error("Database setup error", error=str(e), exc_info=True)
        return False

# =============================================================================
# CLEANUP
# =============================================================================

def cleanup_database():
    """Cleanup database during application shutdown"""
    try:
        close_database()
        logger.info("Database cleanup completed")
    except Exception as e:
        logger.error("Database cleanup error", error=str(e))

def get_db_service():
    """Get database service for health checks"""
    return get_db_manager()

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'EnhancedDatabaseManager',
    'get_db_manager',
    'get_db_service',
    'initialize_database',
    'close_database',
    'get_db_session',
    'get_db_session_context',
    'execute_query',
    'execute_transaction',
    'get_table_info',
    'get_database_stats',
    'run_migrations',
    'backup_database',
    'check_database_health',
    'setup_database',
    'cleanup_database'
]