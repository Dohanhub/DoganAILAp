"""
Complete Database Models for Dogan AI Compliance Platform
PostgreSQL with SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Table, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

# Enums for standardized values
class UserRole(enum.Enum):
    ADMIN = "admin"
    AUDITOR = "auditor"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class ComplianceStatus(enum.Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"
    IN_PROGRESS = "in_progress"

class RiskSeverity(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class Sector(enum.Enum):
    BANKING = "banking"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    TECHNOLOGY = "technology"
    ENERGY = "energy"
    RETAIL = "retail"
    TELECOM = "telecom"
    EDUCATION = "education"

# Association tables for many-to-many relationships
assessment_controls = Table(
    'assessment_controls',
    Base.metadata,
    Column('assessment_id', Integer, ForeignKey('assessments.id')),
    Column('control_id', Integer, ForeignKey('controls.id'))
)

user_organizations = Table(
    'user_organizations',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('organization_id', Integer, ForeignKey('organizations.id'))
)

# Core Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    full_name_arabic = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    department = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preferences = Column(JSON, default={})
    
    # Relationships
    organizations = relationship("Organization", secondary=user_organizations, back_populates="users")
    owned_organizations = relationship("Organization", back_populates="owner")
    assessments = relationship("Assessment", back_populates="assessor")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    name_arabic = Column(String)
    commercial_registration = Column(String, unique=True)
    sector = Column(Enum(Sector), nullable=False)
    sub_sector = Column(String)
    country = Column(String, default="Saudi Arabia")
    city = Column(String)
    size = Column(String)  # Small, Medium, Large, Enterprise
    employee_count = Column(Integer)
    annual_revenue = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    parent_org_id = Column(Integer, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    owner = relationship("User", back_populates="owned_organizations")
    users = relationship("User", secondary=user_organizations, back_populates="organizations")
    parent = relationship("Organization", remote_side=[id])
    assessments = relationship("Assessment", back_populates="organization")
    control_implementations = relationship("ControlImplementation", back_populates="organization")
    risks = relationship("Risk", back_populates="organization")
    incidents = relationship("Incident", back_populates="organization")
    evidence_items = relationship("Evidence", back_populates="organization")
    compliance_scores = relationship("ComplianceScore", back_populates="organization")

class Framework(Base):
    __tablename__ = "frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    name_arabic = Column(String)
    version = Column(String)
    description = Column(Text)
    description_arabic = Column(Text)
    authority = Column(String)
    authority_arabic = Column(String)
    is_saudi = Column(Boolean, default=False)
    is_mandatory = Column(Boolean, default=False)
    effective_date = Column(DateTime)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    controls = relationship("Control", back_populates="framework")
    assessments = relationship("Assessment", back_populates="framework")
    compliance_scores = relationship("ComplianceScore", back_populates="framework")

class ControlCategory(Base):
    __tablename__ = "control_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_arabic = Column(String)
    description = Column(Text)
    icon = Column(String)
    order_index = Column(Integer, default=0)
    
    # Relationships
    controls = relationship("Control", back_populates="category")

class Control(Base):
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("control_categories.id"))
    control_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    title_arabic = Column(String)
    description = Column(Text)
    description_arabic = Column(Text)
    implementation_guidance = Column(Text)
    implementation_guidance_arabic = Column(Text)
    priority = Column(String)  # Critical, High, Medium, Low
    control_type = Column(String)  # Preventive, Detective, Corrective
    automation_possible = Column(Boolean, default=False)
    evidence_required = Column(JSON, default=[])
    related_controls = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    framework = relationship("Framework", back_populates="controls")
    category = relationship("ControlCategory", back_populates="controls")
    implementations = relationship("ControlImplementation", back_populates="control")
    assessments = relationship("Assessment", secondary=assessment_controls, back_populates="controls")

class ControlImplementation(Base):
    __tablename__ = "control_implementations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED)
    implementation_percentage = Column(Float, default=0.0)
    implementation_date = Column(DateTime)
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)
    responsible_person = Column(String)
    evidence_ids = Column(JSON, default=[])
    notes = Column(Text)
    remediation_plan = Column(Text)
    remediation_deadline = Column(DateTime)
    automated_check_result = Column(JSON)
    manual_override = Column(Boolean, default=False)
    override_reason = Column(Text)
    override_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="control_implementations")
    control = relationship("Control", back_populates="implementations")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(String)  # Initial, Periodic, Continuous, Gap Analysis
    score = Column(Float, default=0.0)
    maturity_level = Column(Integer, default=1)  # 1-5 scale
    status = Column(String, default="planned")  # planned, in_progress, completed, expired
    findings = Column(JSON, default={})
    recommendations = Column(JSON, default=[])
    executive_summary = Column(Text)
    detailed_report = Column(Text)
    evidence_collected = Column(JSON, default=[])
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    valid_until = Column(DateTime)
    next_assessment_date = Column(DateTime)
    approval_status = Column(String)  # draft, pending_review, approved, rejected
    approved_by = Column(String)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="assessments")
    framework = relationship("Framework", back_populates="assessments")
    assessor = relationship("User", back_populates="assessments")
    controls = relationship("Control", secondary=assessment_controls, back_populates="assessments")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String, nullable=False)
    title_arabic = Column(String)
    description = Column(Text)
    description_arabic = Column(Text)
    category = Column(String)  # Strategic, Operational, Financial, Compliance, Reputational
    source = Column(String)  # Internal, External
    severity = Column(Enum(RiskSeverity), nullable=False)
    likelihood = Column(String, nullable=False)  # Very High, High, Medium, Low, Very Low
    inherent_risk_score = Column(Float)
    residual_risk_score = Column(Float)
    risk_appetite = Column(String)
    risk_tolerance = Column(String)
    impact_description = Column(Text)
    affected_assets = Column(JSON, default=[])
    affected_controls = Column(JSON, default=[])
    mitigation_plan = Column(Text)
    mitigation_status = Column(String)  # Not Started, In Progress, Implemented, Verified
    mitigation_deadline = Column(DateTime)
    owner = Column(String)
    reviewer = Column(String)
    status = Column(String, default="open")  # open, under_review, mitigated, accepted, closed
    identified_date = Column(DateTime, default=datetime.utcnow)
    review_date = Column(DateTime)
    resolved_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="risks")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    incident_number = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    incident_type = Column(String)  # Security, Privacy, Operational, Compliance
    severity = Column(Enum(RiskSeverity), nullable=False)
    status = Column(String, default="open")  # open, investigating, contained, resolved, closed
    detected_at = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow)
    contained_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    detection_method = Column(String)
    affected_systems = Column(JSON, default=[])
    affected_data = Column(JSON, default=[])
    root_cause = Column(Text)
    immediate_actions = Column(Text)
    remediation_steps = Column(Text)
    lessons_learned = Column(Text)
    reported_to_authorities = Column(Boolean, default=False)
    authorities_notified = Column(JSON, default=[])
    financial_impact = Column(Float)
    assigned_to = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="incidents")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    evidence_type = Column(String)  # Document, Screenshot, Log, Report, Certificate
    file_path = Column(String)
    file_hash = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    collected_by = Column(String)
    collected_at = Column(DateTime, default=datetime.utcnow)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String)
    verified_at = Column(DateTime)
    tags = Column(JSON, default=[])
    related_controls = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="evidence_items")

class ComplianceScore(Base):
    __tablename__ = "compliance_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    score = Column(Float, nullable=False)
    previous_score = Column(Float)
    score_change = Column(Float)
    maturity_level = Column(Integer)
    controls_total = Column(Integer)
    controls_implemented = Column(Integer)
    controls_partial = Column(Integer)
    controls_not_implemented = Column(Integer)
    high_risk_findings = Column(Integer, default=0)
    medium_risk_findings = Column(Integer, default=0)
    low_risk_findings = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    trend = Column(String)  # improving, stable, declining
    benchmark_percentile = Column(Float)  # Industry benchmark
    
    # Relationships
    organization = relationship("Organization", back_populates="compliance_scores")
    framework = relationship("Framework", back_populates="compliance_scores")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(Integer)
    details = Column(JSON, default={})
    ip_address = Column(String)
    user_agent = Column(String)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    title_arabic = Column(String)
    message = Column(Text, nullable=False)
    message_arabic = Column(Text)
    notification_type = Column(String)  # info, warning, error, success, alert
    priority = Column(String, default="normal")  # low, normal, high, urgent
    is_read = Column(Boolean, default=False)
    is_email_sent = Column(Boolean, default=False)
    is_sms_sent = Column(Boolean, default=False)
    action_url = Column(String)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    report_type = Column(String, nullable=False)  # executive, detailed, gap_analysis, benchmark
    format = Column(String, default="pdf")  # pdf, excel, word, json
    title = Column(String, nullable=False)
    description = Column(Text)
    parameters = Column(JSON, default={})
    file_path = Column(String)
    file_size = Column(Integer)
    generated_by = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime)

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    name_arabic = Column(String)
    vendor_type = Column(String)  # Technology, Consulting, Cloud, Security
    criticality = Column(String)  # Critical, High, Medium, Low
    risk_rating = Column(String)
    compliance_status = Column(Enum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED)
    contract_start = Column(DateTime)
    contract_end = Column(DateTime)
    last_assessment = Column(DateTime)
    next_assessment = Column(DateTime)
    contact_person = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    services_provided = Column(JSON, default=[])
    compliance_requirements = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)