"""
Database models for DoganAI-Compliance-Kit
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()

def utc_now():
    """Return current UTC timestamp for database defaults"""
    return datetime.now(timezone.utc)

class AuditLog(Base):
    """Audit log for compliance evaluations"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    mapping_name = Column(String(255), nullable=False, index=True)
    policy_ref = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    result_hash = Column(String(64), nullable=False)
    evaluation_data = Column(JSON, nullable=False)
    user_id = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, mapping={self.mapping_name}, status={self.status})>"

class ComplianceCache(Base):
    """Cache for compliance evaluation results"""
    __tablename__ = "compliance_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mapping_name = Column(String(255), nullable=False, unique=True, index=True)
    policy_ref = Column(String(255), nullable=False)
    result_hash = Column(String(64), nullable=False)
    evaluation_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<ComplianceCache(mapping={self.mapping_name}, hash={self.result_hash})>"

class PolicyVersion(Base):
    """Track policy versions and changes"""
    __tablename__ = "policy_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulator = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<PolicyVersion(regulator={self.regulator}, version={self.version})>"

class VendorCapability(Base):
    """Track vendor capabilities and updates"""
    __tablename__ = "vendor_capabilities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_name = Column(String(255), nullable=False)
    solution_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    capabilities_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<VendorCapability(vendor={self.vendor_name}, solution={self.solution_name})>"

class SystemHealth(Base):
    """System health and monitoring data"""
    __tablename__ = "system_health"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    component = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # healthy, warning, error
    message = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<SystemHealth(component={self.component}, status={self.status})>"