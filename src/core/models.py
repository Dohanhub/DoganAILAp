"""Database models for DoganAI Compliance Kit"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger(__name__)

Base = declarative_base()

class ComplianceCache(Base):
    """Cache table for compliance evaluation results"""
    __tablename__ = 'compliance_cache'
    
    id = Column(Integer, primary_key=True)
    mapping_name = Column(String(255), nullable=False)
    policy_name = Column(String(255), nullable=False)
    cache_key = Column(String(255), unique=True, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    """Audit log table for tracking compliance operations"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    operation = Column(String(255), nullable=False)
    user_id = Column(String(255))
    resource = Column(String(255))
    details = Column(JSON)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    success = Column(Boolean, default=True)
    error_message = Column(Text)

class ConfigurationLog(Base):
    """Configuration changes log"""
    __tablename__ = 'configuration_logs'
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(255), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(255))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reason = Column(Text)

def create_tables(engine: Engine):
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise

__all__ = ['Base', 'ComplianceCache', 'AuditLog', 'ConfigurationLog', 'create_tables']