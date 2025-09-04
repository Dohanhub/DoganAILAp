"""
Database models for DoganAI Compliance Kit
Production-ready models with proper relationships, indexing, and audit trails
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import event
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import hashlib

Base = declarative_base()

# =============================================================================
# PYDANTIC MODELS FOR API
# =============================================================================

class EvaluationResultBase(BaseModel):
    """Base model for evaluation results"""
    mapping: str
    vendor_id: Optional[str] = None
    policy_version: Optional[str] = None
    status: str
    required_items: List[str]
    provided_items: List[str]
    missing_items: List[str]
    vendors: List[Dict[str, Any]]
    evaluation_time: float
    benchmark_score: Optional[float] = None
    compliance_percentage: float

class EvaluationResultCreate(EvaluationResultBase):
    """Model for creating evaluation results"""
    pass

class EvaluationResultResponse(EvaluationResultBase):
    """Model for evaluation result responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    hash: str

class ComplianceReportBase(BaseModel):
    """Base model for compliance reports"""
    evaluation_id: str
    format: str
    status: str
    created_by: str

class ComplianceReportCreate(ComplianceReportBase):
    """Model for creating compliance reports"""
    pass

class ComplianceReportResponse(ComplianceReportBase):
    """Model for compliance report responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

# =============================================================================
# SQLALCHEMY MODELS
# =============================================================================

class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class AuditMixin:
    """Mixin for audit fields"""
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(255), nullable=True)

class EvaluationResult(Base, TimestampMixin, AuditMixin):
    """Evaluation results table"""
    __tablename__ = "evaluation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mapping = Column(String(255), nullable=False, index=True)
    vendor_id = Column(String(255), nullable=True, index=True)
    policy_version = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, index=True)
    required_items = Column(ARRAY(String), nullable=False)
    provided_items = Column(ARRAY(String), nullable=False)
    missing_items = Column(ARRAY(String), nullable=False)
    vendors = Column(JSONB, nullable=False)
    hash = Column(String(64), nullable=False, unique=True, index=True)
    evaluation_time = Column(Float, nullable=False)
    benchmark_score = Column(Float, nullable=True)
    compliance_percentage = Column(Float, nullable=False)
    
    # Metadata
    source_ip = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    reports = relationship("ComplianceReport", back_populates="evaluation", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="evaluation", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('compliance_percentage >= 0 AND compliance_percentage <= 100', name='valid_compliance_percentage'),
        CheckConstraint('evaluation_time >= 0', name='valid_evaluation_time'),
        CheckConstraint('benchmark_score IS NULL OR (benchmark_score >= 0 AND benchmark_score <= 100)', name='valid_benchmark_score'),
        Index('idx_evaluation_results_mapping_status', 'mapping', 'status'),
        Index('idx_evaluation_results_vendor_status', 'vendor_id', 'status'),
        Index('idx_evaluation_results_created_at', 'created_at'),
        Index('idx_evaluation_results_compliance_percentage', 'compliance_percentage'),
    )

class ComplianceReport(Base, TimestampMixin, AuditMixin):
    """Compliance reports table"""
    __tablename__ = "compliance_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_results.id"), nullable=False, index=True)
    format = Column(String(50), nullable=False)  # pdf, html, json, xml
    status = Column(String(50), nullable=False, index=True)  # generating, completed, failed
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    download_url = Column(String(500), nullable=True)
    generation_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Report metadata
    report_type = Column(String(100), nullable=False, default="compliance")  # compliance, audit, summary
    language = Column(String(10), nullable=False, default="en")  # en, ar
    template_version = Column(String(50), nullable=True)
    
    # Relationships
    evaluation = relationship("EvaluationResult", back_populates="reports")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('status IN (\'generating\', \'completed\', \'failed\')', name='valid_report_status'),
        CheckConstraint('format IN (\'pdf\', \'html\', \'json\', \'xml\')', name='valid_report_format'),
        CheckConstraint('language IN (\'en\', \'ar\')', name='valid_language'),
        Index('idx_compliance_reports_evaluation_status', 'evaluation_id', 'status'),
        Index('idx_compliance_reports_format_status', 'format', 'status'),
        Index('idx_compliance_reports_created_at', 'created_at'),
    )

class Vendor(Base, TimestampMixin, AuditMixin):
    """Vendors table"""
    __tablename__ = "vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Vendor capabilities
    capabilities = Column(JSONB, nullable=False, default=dict)
    certifications = Column(ARRAY(String), nullable=False, default=list)
    compliance_levels = Column(JSONB, nullable=False, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_evaluation = Column(DateTime(timezone=True), nullable=True)
    overall_compliance_score = Column(Float, nullable=True)
    
    # Relationships
    evaluations = relationship("EvaluationResult", foreign_keys=[EvaluationResult.vendor_id], primaryjoin="Vendor.vendor_id == EvaluationResult.vendor_id")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('overall_compliance_score IS NULL OR (overall_compliance_score >= 0 AND overall_compliance_score <= 100)', name='valid_vendor_compliance_score'),
        Index('idx_vendors_vendor_id_active', 'vendor_id', 'is_active'),
        Index('idx_vendors_compliance_score', 'overall_compliance_score'),
        Index('idx_vendors_last_evaluation', 'last_evaluation'),
    )

class Policy(Base, TimestampMixin, AuditMixin):
    """Policies table"""
    __tablename__ = "policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(500), nullable=False)
    version = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    authority = Column(String(255), nullable=False)  # NCA, SAMA, MoH, etc.
    
    # Policy content
    requirements = Column(JSONB, nullable=False, default=dict)
    categories = Column(ARRAY(String), nullable=False, default=list)
    risk_level = Column(String(50), nullable=False, default="medium")  # low, medium, high, critical
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('risk_level IN (\'low\', \'medium\', \'high\', \'critical\')', name='valid_risk_level'),
        Index('idx_policies_policy_id_version', 'policy_id', 'version'),
        Index('idx_policies_authority_active', 'authority', 'is_active'),
        Index('idx_policies_risk_level', 'risk_level'),
        Index('idx_policies_effective_date', 'effective_date'),
        UniqueConstraint('policy_id', 'version', name='unique_policy_version'),
    )

class Mapping(Base, TimestampMixin, AuditMixin):
    """Mappings table"""
    __tablename__ = "mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mapping_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(100), nullable=False)
    
    # Mapping content
    source_policy = Column(String(255), nullable=False)
    target_policy = Column(String(255), nullable=False)
    mapping_rules = Column(JSONB, nullable=False, default=dict)
    transformation_logic = Column(JSONB, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Constraints
    __table_args__ = (
        Index('idx_mappings_mapping_id_version', 'mapping_id', 'version'),
        Index('idx_mappings_source_target', 'source_policy', 'target_policy'),
        Index('idx_mappings_active_usage', 'is_active', 'usage_count'),
        UniqueConstraint('mapping_id', 'version', name='unique_mapping_version'),
    )

class Benchmark(Base, TimestampMixin, AuditMixin):
    """Benchmarks table"""
    __tablename__ = "benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    benchmark_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=False, index=True)
    sector = Column(String(255), nullable=False, index=True)
    
    # Benchmark data
    metrics = Column(JSONB, nullable=False, default=dict)
    thresholds = Column(JSONB, nullable=False, default=dict)
    reference_data = Column(JSONB, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    update_frequency = Column(String(50), nullable=True)  # daily, weekly, monthly, quarterly
    
    # Constraints
    __table_args__ = (
        Index('idx_benchmarks_category_sector', 'category', 'sector'),
        Index('idx_benchmarks_active_updated', 'is_active', 'last_updated'),
    )

class AuditLog(Base, TimestampMixin):
    """Audit log table"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit details
    details = Column(JSONB, nullable=False, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    evaluation = relationship("EvaluationResult", foreign_keys=[resource_id], primaryjoin="AuditLog.resource_id == EvaluationResult.id")
    
    # Constraints
    __table_args__ = (
        Index('idx_audit_logs_user_action', 'user_id', 'action'),
        Index('idx_audit_logs_resource_type_id', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_request_id', 'request_id'),
    )

class SystemMetrics(Base, TimestampMixin):
    """System metrics table"""
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    
    # Metadata
    labels = Column(JSONB, nullable=False, default=dict)
    source = Column(String(255), nullable=False, index=True)  # api, ui, system, database
    
    # Constraints
    __table_args__ = (
        Index('idx_system_metrics_name_source', 'metric_name', 'source'),
        Index('idx_system_metrics_created_at', 'created_at'),
    )

class UserSession(Base, TimestampMixin):
    """User sessions table"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Session details
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Security
    last_activity = Column(DateTime(timezone=True), nullable=False, default=func.now())
    login_attempts = Column(Integer, default=0, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('login_attempts >= 0', name='valid_login_attempts'),
        Index('idx_user_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_user_sessions_expires_at', 'expires_at'),
        Index('idx_user_sessions_last_activity', 'last_activity'),
    )

# =============================================================================
# DATABASE EVENTS AND HOOKS
# =============================================================================

@event.listens_for(EvaluationResult, 'before_insert')
def set_evaluation_hash(mapper, connection, target):
    """Set hash for evaluation result before insert"""
    if not target.hash:
        # Create hash from mapping, vendor_id, and timestamp
        hash_input = f"{target.mapping}:{target.vendor_id}:{target.created_at.isoformat()}"
        target.hash = hashlib.sha256(hash_input.encode()).hexdigest()

@event.listens_for(EvaluationResult, 'before_update')
def update_evaluation_timestamp(mapper, connection, target):
    """Update timestamp before update"""
    target.updated_at = datetime.now(timezone.utc)

@event.listens_for(ComplianceReport, 'before_update')
def update_report_timestamp(mapper, connection, target):
    """Update timestamp before update"""
    target.updated_at = datetime.now(timezone.utc)

# =============================================================================
# DATABASE UTILITIES
# =============================================================================

def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(engine)

def drop_tables(engine):
    """Drop all tables"""
    Base.metadata.drop_all(engine)

def get_table_names():
    """Get all table names"""
    return Base.metadata.tables.keys()

# =============================================================================
# MODEL VALIDATION
# =============================================================================

def validate_model(model_instance):
    """Validate a model instance"""
    errors = []
    
    if hasattr(model_instance, 'compliance_percentage'):
        if not (0 <= model_instance.compliance_percentage <= 100):
            errors.append("Compliance percentage must be between 0 and 100")
    
    if hasattr(model_instance, 'evaluation_time'):
        if model_instance.evaluation_time < 0:
            errors.append("Evaluation time cannot be negative")
    
    if hasattr(model_instance, 'benchmark_score') and model_instance.benchmark_score is not None:
        if not (0 <= model_instance.benchmark_score <= 100):
            errors.append("Benchmark score must be between 0 and 100")
    
    return errors

# =============================================================================
# EXPORT MODELS
# =============================================================================

__all__ = [
    'Base',
    'EvaluationResult',
    'ComplianceReport', 
    'Vendor',
    'Policy',
    'Mapping',
    'Benchmark',
    'AuditLog',
    'SystemMetrics',
    'UserSession',
    'EvaluationResultBase',
    'EvaluationResultCreate',
    'EvaluationResultResponse',
    'ComplianceReportBase',
    'ComplianceReportCreate',
    'ComplianceReportResponse',
    'create_tables',
    'drop_tables',
    'get_table_names',
    'validate_model'
]