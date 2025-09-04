"""
Database service layer for DoganAI-Compliance-Kit
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone
import logging
import hashlib
import json

from .models import Base, AuditLog, ComplianceCache, PolicyVersion, VendorCapability, SystemHealth
from .settings import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for compliance operations"""
    
    def __init__(self):
        self._engine = None
        self._session_factory = None
        
    def initialize(self):
        """Initialize database connection"""
        try:
            self._engine = create_engine(
                settings.database_url,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                echo=settings.debug,
                # Ensure timezone handling
                connect_args={
                    "options": f"-c timezone={settings.database.timezone}"
                }
            )
            
            # Create tables
            Base.metadata.create_all(self._engine)
            
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self._session_factory:
            self.initialize()
        return self._session_factory()
    
    def _get_current_time(self) -> datetime:
        """Get current time with proper timezone handling"""
        return settings.get_current_time(use_utc=True)
    
    def log_evaluation(self, mapping_name: str, result: Dict[str, Any], 
                      user_id: Optional[str] = None, session_id: Optional[str] = None) -> bool:
        """Log compliance evaluation to audit trail"""
        try:
            with self.get_session() as session:
                audit_entry = AuditLog(
                    mapping_name=mapping_name,
                    policy_ref=result.get('policy', ''),
                    status=result.get('status', ''),
                    result_hash=result.get('hash', ''),
                    evaluation_data=result,
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=self._get_current_time()  # Use timezone-aware timestamp
                )
                session.add(audit_entry)
                session.commit()
                logger.info(f"Logged evaluation for mapping: {mapping_name}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to log evaluation: {e}")
            return False
    
    def get_cached_evaluation(self, mapping_name: str) -> Optional[Dict[str, Any]]:
        """Get cached evaluation result if valid"""
        try:
            current_time = self._get_current_time()
            logger.debug(f"Checking cache at {current_time}")
            
            with self.get_session() as session:
                cache_entry = session.query(ComplianceCache).filter(
                    and_(
                        ComplianceCache.mapping_name == mapping_name,
                        ComplianceCache.is_valid == True,
                        ComplianceCache.expires_at > current_time
                    )
                ).first()
                
                if cache_entry:
                    logger.info(f"Found cached evaluation for mapping: {mapping_name}, "
                               f"expires at: {cache_entry.expires_at}, current time: {current_time}")
                    return cache_entry.evaluation_data
                else:
                    logger.debug(f"No valid cache found for mapping: {mapping_name}")
                    
        except SQLAlchemyError as e:
            logger.error(f"Failed to get cached evaluation: {e}")
            
        return None
    
    def cache_evaluation(self, mapping_name: str, result: Dict[str, Any], 
                        ttl_minutes: int = None) -> bool:
        """Cache evaluation result"""
        if ttl_minutes is None:
            ttl_minutes = settings.cache_ttl // 60  # Convert seconds to minutes
            
        try:
            current_time = self._get_current_time()
            expires_at = current_time + timedelta(minutes=ttl_minutes)
            
            logger.debug(f"Caching evaluation for {mapping_name}, "
                        f"current time: {current_time}, expires at: {expires_at}")
            
            with self.get_session() as session:
                # Remove existing cache entry
                session.query(ComplianceCache).filter(
                    ComplianceCache.mapping_name == mapping_name
                ).delete()
                
                # Add new cache entry
                cache_entry = ComplianceCache(
                    mapping_name=mapping_name,
                    policy_ref=result.get('policy', ''),
                    result_hash=result.get('hash', ''),
                    evaluation_data=result,
                    created_at=current_time,
                    expires_at=expires_at
                )
                session.add(cache_entry)
                session.commit()
                logger.info(f"Cached evaluation for mapping: {mapping_name}, expires at: {expires_at}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to cache evaluation: {e}")
            return False
    
    def get_evaluation_history(self, mapping_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get evaluation history for a mapping"""
        try:
            with self.get_session() as session:
                history = session.query(AuditLog).filter(
                    AuditLog.mapping_name == mapping_name
                ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
                
                return [
                    {
                        'id': entry.id,
                        'timestamp': settings.timezone.to_display_timezone(entry.timestamp).isoformat(),
                        'status': entry.status,
                        'policy_ref': entry.policy_ref,
                        'result_hash': entry.result_hash
                    }
                    for entry in history
                ]
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get evaluation history: {e}")
            return []
    
    def track_policy_version(self, regulator: str, version: str, 
                           file_path: str, file_content: bytes) -> bool:
        """Track policy file version"""
        try:
            file_hash = hashlib.sha256(file_content).hexdigest()
            current_time = self._get_current_time()
            
            with self.get_session() as session:
                # Check if version already exists
                existing = session.query(PolicyVersion).filter(
                    and_(
                        PolicyVersion.regulator == regulator,
                        PolicyVersion.version == version,
                        PolicyVersion.file_hash == file_hash
                    )
                ).first()
                
                if existing:
                    return True
                
                # Deactivate old versions
                session.query(PolicyVersion).filter(
                    and_(
                        PolicyVersion.regulator == regulator,
                        PolicyVersion.version == version
                    )
                ).update({'is_active': False})
                
                # Add new version
                policy_version = PolicyVersion(
                    regulator=regulator,
                    version=version,
                    file_path=file_path,
                    file_hash=file_hash,
                    created_at=current_time
                )
                session.add(policy_version)
                session.commit()
                logger.info(f"Tracked policy version: {regulator}@{version}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to track policy version: {e}")
            return False
    
    def log_system_health(self, component: str, status: str, 
                         message: Optional[str] = None, metrics: Optional[Dict] = None) -> bool:
        """Log system health status"""
        try:
            with self.get_session() as session:
                health_entry = SystemHealth(
                    component=component,
                    status=status,
                    message=message,
                    metrics=metrics,
                    timestamp=self._get_current_time()
                )
                session.add(health_entry)
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to log system health: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old audit logs and cache entries"""
        try:
            current_time = self._get_current_time()
            cutoff_date = current_time - timedelta(days=days_to_keep)
            
            logger.info(f"Cleaning up data older than {cutoff_date}")
            
            with self.get_session() as session:
                # Clean old audit logs
                deleted_audits = session.query(AuditLog).filter(
                    AuditLog.timestamp < cutoff_date
                ).delete()
                
                # Clean expired cache entries
                deleted_cache = session.query(ComplianceCache).filter(
                    ComplianceCache.expires_at < current_time
                ).delete()
                
                # Clean old health logs
                deleted_health = session.query(SystemHealth).filter(
                    SystemHealth.timestamp < cutoff_date
                ).delete()
                
                session.commit()
                logger.info(f"Cleaned up {deleted_audits} audit logs, "
                           f"{deleted_cache} cache entries, {deleted_health} health logs")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False

# Global database service instance
db_service = DatabaseService()

def get_db_service() -> DatabaseService:
    """Get database service instance"""
    return db_service