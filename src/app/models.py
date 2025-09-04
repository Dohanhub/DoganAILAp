
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .core.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceStandard(Base):
    __tablename__ = 'compliance_standards'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, nullable=False)
    description = Column(String)

class Control(Base):
    __tablename__ = 'controls'
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey('compliance_standards.id'))
    control_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    implementation_guidance = Column(String)
    is_mandatory = Column(Boolean, default=True)

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

def create_tables():
    from .core.database import engine
    Base.metadata.create_all(bind=engine)
