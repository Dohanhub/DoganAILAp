
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default='user')  # user, auditor, admin
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tenant = relationship('Tenant', back_populates='users')

class ComplianceStandard(Base):
    __tablename__ = 'compliance_standards'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    description = Column(String)
    regulator_id = Column(Integer, ForeignKey('regulators.id'), nullable=True)
    regulator = relationship('Regulator', back_populates='standards')

class Control(Base):
    __tablename__ = 'controls'
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey('compliance_standards.id'))
    control_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    implementation_guidance = Column(String)
    is_mandatory = Column(Boolean, default=True)
    standard = relationship('ComplianceStandard')

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey('controls.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='Not Started')
    evidence = Column(String)
    notes = Column(String)
    assessed_at = Column(DateTime, default=datetime.utcnow)
    next_review_date = Column(DateTime)


class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship('User', back_populates='tenant')


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    user_email = Column(String, nullable=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    tenant_id = Column(Integer, nullable=True)
    ip = Column(String, nullable=True)


class Regulator(Base):
    __tablename__ = 'regulators'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    country = Column(String, default='KSA')
    sector = Column(String, nullable=True)
    website = Column(String, nullable=True)
    standards = relationship('ComplianceStandard', back_populates='regulator')


class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)  # e.g., SIEM, IAM, DLP
    website = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    description = Column(Text, nullable=True)


class VendorRegulator(Base):
    __tablename__ = 'vendor_regulator'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    regulator_id = Column(Integer, ForeignKey('regulators.id'), nullable=False)
    notes = Column(Text, nullable=True)


class VendorTenant(Base):
    __tablename__ = 'vendor_tenant'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    notes = Column(Text, nullable=True)


class Connector(Base):
    __tablename__ = 'connectors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=True)
    regulator_id = Column(Integer, ForeignKey('regulators.id'), nullable=True)
    description = Column(Text, nullable=True)


class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    control_id = Column(Integer, ForeignKey('controls.id'), nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    original_filename = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=True)
    storage = Column(String, default='local')  # local or s3
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Helpful indices
Index('ix_evidence_control', Evidence.control_id)

def create_tables():
    from .core.database import engine
    Base.metadata.create_all(bind=engine)
