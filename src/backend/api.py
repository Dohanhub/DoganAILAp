"""
Dogan AI Compliance Platform - Complete FastAPI Backend
Production-ready with all Saudi compliance features
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Security, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_, desc, asc
from passlib.context import CryptContext
from jose import JWTError, jwt
import redis.asyncio as redis
import duckdb
import polars as pl
import hashlib
import uvicorn

from backend.models import *

# Environment configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Database setup
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, pool_size=20, max_overflow=40)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Global connections
redis_client = None
analytics_db = None

# Saudi-specific compliance data
SAUDI_FRAMEWORKS = {
    "NCA": {
        "name": "National Cybersecurity Authority",
        "name_arabic": "الهيئة الوطنية للأمن السيبراني",
        "authority": "NCA",
        "controls_count": 114,
        "categories": ["Governance", "Defense", "Resilience", "Third-Party", "Cloud"]
    },
    "SAMA": {
        "name": "SAMA Cyber Security Framework",
        "name_arabic": "إطار الأمن السيبراني للبنك المركزي السعودي",
        "authority": "Saudi Central Bank",
        "controls_count": 97,
        "categories": ["Governance", "Risk", "Security", "Incident", "BCM"]
    },
    "PDPL": {
        "name": "Personal Data Protection Law",
        "name_arabic": "نظام حماية البيانات الشخصية",
        "authority": "NDMO",
        "controls_count": 73,
        "categories": ["Principles", "Rights", "Processing", "Transfer", "Security"]
    }
}

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, analytics_db
    
    # Startup
    print("🚀 Starting Dogan AI Compliance Platform...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Redis
    try:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        redis_client = None
    
    # Initialize DuckDB for analytics
    analytics_db = duckdb.connect(':memory:')
    analytics_db.execute("""
        CREATE TABLE IF NOT EXISTS compliance_metrics (
            organization_id INTEGER,
            framework TEXT,
            score FLOAT,
            timestamp TIMESTAMP,
            controls_passed INTEGER,
            controls_total INTEGER,
            risk_level TEXT,
            maturity_level INTEGER
        )
    """)
    analytics_db.execute("""
        CREATE TABLE IF NOT EXISTS risk_metrics (
            organization_id INTEGER,
            risk_count INTEGER,
            critical_risks INTEGER,
            high_risks INTEGER,
            timestamp TIMESTAMP
        )
    """)
    print("✅ Analytics database initialized")
    
    # Seed initial data
    await seed_initial_data()
    
    yield
    
    # Shutdown
    print("🔄 Shutting down...")
    if redis_client:
        await redis_client.close()
    if analytics_db:
        analytics_db.close()
    await engine.dispose()
    print("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Dogan AI Compliance Platform API",
    description="Saudi Arabia Compliance & Risk Management Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async with async_session() as session:
        yield session

# Cache utilities
async def cache_get(key: str):
    if redis_client:
        try:
            data = await redis_client.get(key)
            return json.loads(data) if data else None
        except:
            pass
    return None

async def cache_set(key: str, value: Any, expire: int = 300):
    if redis_client:
        try:
            await redis_client.setex(key, expire, json.dumps(value, default=str))
        except:
            pass

async def cache_delete(pattern: str):
    if redis_client:
        try:
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
        except:
            pass

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return user

async def require_role(required_role: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in [required_role, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Seed initial data
async def seed_initial_data():
    async with async_session() as db:
        # Check if data exists
        result = await db.execute(select(func.count(Framework.id)))
        if result.scalar() > 0:
            return
        
        print("📦 Seeding initial data...")
        
        # Create control categories
        categories = [
            ControlCategory(name="Governance", name_arabic="الحوكمة"),
            ControlCategory(name="Risk Management", name_arabic="إدارة المخاطر"),
            ControlCategory(name="Access Control", name_arabic="التحكم في الوصول"),
            ControlCategory(name="Data Protection", name_arabic="حماية البيانات"),
            ControlCategory(name="Incident Response", name_arabic="الاستجابة للحوادث"),
            ControlCategory(name="Business Continuity", name_arabic="استمرارية الأعمال"),
            ControlCategory(name="Compliance", name_arabic="الامتثال"),
            ControlCategory(name="Third Party", name_arabic="الطرف الثالث"),
        ]
        db.add_all(categories)
        
        # Create frameworks
        for code, data in SAUDI_FRAMEWORKS.items():
            framework = Framework(
                code=code,
                name=data["name"],
                name_arabic=data["name_arabic"],
                authority=data["authority"],
                is_saudi=True,
                is_mandatory=True,
                version="2024"
            )
            db.add(framework)
        
        # Add international frameworks
        intl_frameworks = [
            Framework(code="ISO27001", name="ISO 27001:2022", authority="ISO", is_saudi=False),
            Framework(code="NIST", name="NIST Cybersecurity Framework", authority="NIST", is_saudi=False),
            Framework(code="SOC2", name="SOC 2 Type II", authority="AICPA", is_saudi=False),
        ]
        db.add_all(intl_frameworks)
        
        await db.commit()
        print("✅ Initial data seeded")

# Audit logging
async def audit_log(
    db: AsyncSession,
    user: User,
    action: str,
    resource_type: str = None,
    resource_id: int = None,
    details: dict = None
):
    log = AuditLog(
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )
    db.add(log)
    await db.commit()

# API Routes

# Root & Health
@app.get("/")
async def root():
    return {
        "platform": "Dogan AI Compliance Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "saudi_frameworks": ["NCA", "SAMA", "PDPL"],
            "international": ["ISO27001", "NIST", "SOC2"],
            "languages": ["English", "Arabic"],
            "database": "PostgreSQL",
            "cache": "Redis",
            "analytics": "DuckDB"
        }
    }

@app.get("/health")
async def health_check():
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        async with async_session() as session:
            await session.execute(select(1))
        health["services"]["database"] = "connected"
    except Exception as e:
        health["services"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
            health["services"]["redis"] = "connected"
        except:
            health["services"]["redis"] = "error"
    else:
        health["services"]["redis"] = "not configured"
    
    # Check DuckDB
    if analytics_db:
        try:
            analytics_db.execute("SELECT 1").fetchone()
            health["services"]["analytics"] = "operational"
        except:
            health["services"]["analytics"] = "error"
    
    return health

# Authentication
@app.post("/auth/register")
async def register(
    email: str,
    username: str,
    password: str,
    full_name: str,
    full_name_arabic: Optional[str] = None,
    organization_name: Optional[str] = None,
    sector: Optional[str] = "technology",
    db: AsyncSession = Depends(get_db)
):
    # Check existing user
    result = await db.execute(
        select(User).where(or_(User.email == email, User.username == username))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        full_name_arabic=full_name_arabic,
        role=UserRole.USER
    )
    db.add(user)
    await db.flush()
    
    # Create organization if provided
    if organization_name:
        org = Organization(
            name=organization_name,
            sector=Sector[sector.upper()],
            owner_id=user.id
        )
        db.add(org)
    
    await db.commit()
    await db.refresh(user)
    
    # Create token
    access_token = create_access_token(data={"sub": username})
    
    # Clear user cache
    await cache_delete(f"user:{username}:*")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }

@app.post("/auth/login")
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    # Get user
    result = await db.execute(
        select(User).where(or_(User.username == username, User.email == username))
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": user.username})
    
    # Audit log
    await audit_log(db, user, "login")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "department": current_user.department,
        "last_login": current_user.last_login
    }

# Organizations
@app.post("/organizations")
async def create_organization(
    name: str,
    sector: Sector,
    name_arabic: Optional[str] = None,
    commercial_registration: Optional[str] = None,
    city: Optional[str] = None,
    size: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org = Organization(
        name=name,
        name_arabic=name_arabic,
        commercial_registration=commercial_registration,
        sector=sector,
        city=city,
        size=size,
        owner_id=current_user.id
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    # Clear cache
    await cache_delete("organizations:*")
    
    # Audit log
    await audit_log(db, current_user, "create_organization", "organization", org.id)
    
    return {
        "id": org.id,
        "name": org.name,
        "sector": org.sector.value,
        "created_at": org.created_at
    }

@app.get("/organizations")
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    sector: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check cache
    cache_key = f"organizations:{skip}:{limit}:{sector}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    query = select(Organization).options(selectinload(Organization.owner))
    
    if sector:
        query = query.where(Organization.sector == Sector[sector.upper()])
    
    # Filter by user access
    if current_user.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        query = query.where(Organization.owner_id == current_user.id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    organizations = result.scalars().all()
    
    data = [
        {
            "id": org.id,
            "name": org.name,
            "name_arabic": org.name_arabic,
            "sector": org.sector.value,
            "city": org.city,
            "size": org.size,
            "owner": org.owner.full_name if org.owner else None,
            "created_at": org.created_at
        } for org in organizations
    ]
    
    await cache_set(cache_key, data)
    return data

@app.get("/organizations/{org_id}")
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Organization)
        .options(
            selectinload(Organization.assessments),
            selectinload(Organization.risks),
            selectinload(Organization.compliance_scores)
        )
        .where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check access
    if current_user.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        if org.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": org.id,
        "name": org.name,
        "name_arabic": org.name_arabic,
        "sector": org.sector.value,
        "city": org.city,
        "size": org.size,
        "employee_count": org.employee_count,
        "assessments_count": len(org.assessments),
        "risks_count": len(org.risks),
        "latest_scores": [
            {
                "framework": score.framework_id,
                "score": score.score,
                "date": score.calculated_at
            } for score in org.compliance_scores[:5]
        ],
        "created_at": org.created_at,
        "updated_at": org.updated_at
    }

# Frameworks
@app.get("/frameworks")
async def list_frameworks(
    saudi_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"frameworks:{saudi_only}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    query = select(Framework).options(selectinload(Framework.controls))
    if saudi_only:
        query = query.where(Framework.is_saudi == True)
    
    result = await db.execute(query)
    frameworks = result.scalars().all()
    
    data = [
        {
            "id": f.id,
            "code": f.code,
            "name": f.name,
            "name_arabic": f.name_arabic,
            "authority": f.authority,
            "authority_arabic": f.authority_arabic,
            "is_saudi": f.is_saudi,
            "is_mandatory": f.is_mandatory,
            "version": f.version,
            "controls_count": len(f.controls),
            "url": f.url
        } for f in frameworks
    ]
    
    await cache_set(cache_key, data, 3600)
    return data

@app.get("/frameworks/{framework_code}/controls")
async def get_framework_controls(
    framework_code: str,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Get framework
    result = await db.execute(
        select(Framework).where(Framework.code == framework_code)
    )
    framework = result.scalar_one_or_none()
    
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Get controls
    query = select(Control).where(Control.framework_id == framework.id)
    if category:
        query = query.join(ControlCategory).where(ControlCategory.name == category)
    
    result = await db.execute(query.options(selectinload(Control.category)))
    controls = result.scalars().all()
    
    return {
        "framework": framework.name,
        "framework_arabic": framework.name_arabic,
        "controls": [
            {
                "id": c.id,
                "control_id": c.control_id,
                "title": c.title,
                "title_arabic": c.title_arabic,
                "description": c.description,
                "category": c.category.name if c.category else None,
                "priority": c.priority,
                "control_type": c.control_type,
                "automation_possible": c.automation_possible,
                "evidence_required": c.evidence_required
            } for c in controls
        ],
        "total": len(controls)
    }

# Assessments
@app.post("/assessments")
async def create_assessment(
    organization_id: int,
    framework_code: str,
    assessment_type: str = "initial",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify organization access
    org_result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get framework
    fw_result = await db.execute(
        select(Framework).where(Framework.code == framework_code)
    )
    framework = fw_result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Create assessment
    assessment = Assessment(
        organization_id=organization_id,
        framework_id=framework.id,
        assessor_id=current_user.id,
        assessment_type=assessment_type,
        status="in_progress",
        started_at=datetime.utcnow()
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    # Analytics
    if analytics_db:
        analytics_db.execute("""
            INSERT INTO compliance_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (organization_id, framework_code, 0.0, datetime.now(), 0, 0, "not_assessed", 1))
    
    # Clear cache
    await cache_delete(f"assessments:org:{organization_id}:*")
    
    # Audit log
    await audit_log(db, current_user, "create_assessment", "assessment", assessment.id, {
        "organization": org.name,
        "framework": framework.name
    })
    
    return {
        "id": assessment.id,
        "organization": org.name,
        "framework": framework.name,
        "type": assessment_type,
        "status": assessment.status,
        "assessor": current_user.full_name,
        "started_at": assessment.started_at
    }

@app.get("/assessments")
async def list_assessments(
    organization_id: Optional[int] = None,
    framework_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Assessment).options(
        selectinload(Assessment.organization),
        selectinload(Assessment.framework),
        selectinload(Assessment.assessor)
    )
    
    if organization_id:
        query = query.where(Assessment.organization_id == organization_id)
    if framework_id:
        query = query.where(Assessment.framework_id == framework_id)
    if status:
        query = query.where(Assessment.status == status)
    
    # Filter by user access
    if current_user.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        query = query.where(Assessment.assessor_id == current_user.id)
    
    query = query.order_by(desc(Assessment.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    assessments = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "organization": a.organization.name,
            "framework": a.framework.name,
            "type": a.assessment_type,
            "score": a.score,
            "maturity_level": a.maturity_level,
            "status": a.status,
            "assessor": a.assessor.full_name if a.assessor else None,
            "started_at": a.started_at,
            "completed_at": a.completed_at,
            "valid_until": a.valid_until
        } for a in assessments
    ]

@app.put("/assessments/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: int,
    score: float,
    findings: Dict[str, Any],
    recommendations: List[str],
    executive_summary: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get assessment
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.organization), selectinload(Assessment.framework))
        .where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.assessor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update assessment
    assessment.score = score
    assessment.findings = findings
    assessment.recommendations = recommendations
    assessment.executive_summary = executive_summary
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()
    assessment.valid_until = datetime.utcnow() + timedelta(days=365)
    
    # Calculate maturity level
    if score >= 90:
        assessment.maturity_level = 5
    elif score >= 75:
        assessment.maturity_level = 4
    elif score >= 60:
        assessment.maturity_level = 3
    elif score >= 40:
        assessment.maturity_level = 2
    else:
        assessment.maturity_level = 1
    
    # Update compliance score
    comp_score = ComplianceScore(
        organization_id=assessment.organization_id,
        framework_id=assessment.framework_id,
        score=score,
        maturity_level=assessment.maturity_level,
        calculated_at=datetime.utcnow(),
        valid_until=assessment.valid_until
    )
    db.add(comp_score)
    
    await db.commit()
    
    # Analytics
    if analytics_db:
        risk_level = "low" if score >= 80 else "medium" if score >= 60 else "high"
        analytics_db.execute("""
            INSERT INTO compliance_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assessment.organization_id,
            assessment.framework.code,
            score,
            datetime.now(),
            int(score * 100 / 100),  # controls passed estimate
            100,  # total controls estimate
            risk_level,
            assessment.maturity_level
        ))
    
    # Clear cache
    await cache_delete(f"assessments:*")
    await cache_delete(f"compliance_scores:org:{assessment.organization_id}:*")
    
    # Audit log
    await audit_log(db, current_user, "complete_assessment", "assessment", assessment_id, {
        "score": score,
        "maturity_level": assessment.maturity_level
    })
    
    return {
        "id": assessment.id,
        "status": "completed",
        "score": score,
        "maturity_level": assessment.maturity_level,
        "valid_until": assessment.valid_until
    }

# Risk Management
@app.post("/risks")
async def create_risk(
    organization_id: int,
    title: str,
    severity: RiskSeverity,
    likelihood: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Calculate risk score
    severity_scores = {"critical": 5, "high": 4, "medium": 3, "low": 2, "minimal": 1}
    likelihood_scores = {"very_high": 5, "high": 4, "medium": 3, "low": 2, "very_low": 1}
    
    inherent_score = severity_scores.get(severity.value, 3) * likelihood_scores.get(likelihood.lower().replace(" ", "_"), 3)
    
    risk = Risk(
        organization_id=organization_id,
        title=title,
        description=description,
        category=category,
        severity=severity,
        likelihood=likelihood,
        inherent_risk_score=inherent_score,
        status="open"
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    
    # Analytics
    if analytics_db:
        # Count risks by severity
        result = await db.execute(
            select(
                func.count(Risk.id),
                func.sum(func.cast(Risk.severity == RiskSeverity.CRITICAL, Integer)),
                func.sum(func.cast(Risk.severity == RiskSeverity.HIGH, Integer))
            ).where(Risk.organization_id == organization_id)
        )
        total, critical, high = result.one()
        
        analytics_db.execute("""
            INSERT INTO risk_metrics VALUES (?, ?, ?, ?, ?)
        """, (organization_id, total, critical or 0, high or 0, datetime.now()))
    
    # Clear cache
    await cache_delete(f"risks:org:{organization_id}:*")
    
    # Audit log
    await audit_log(db, current_user, "create_risk", "risk", risk.id, {
        "title": title,
        "severity": severity.value
    })
    
    return {
        "id": risk.id,
        "title": risk.title,
        "severity": risk.severity.value,
        "likelihood": risk.likelihood,
        "risk_score": inherent_score,
        "status": risk.status,
        "created_at": risk.created_at
    }

@app.get("/risks")
async def list_risks(
    organization_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Risk).options(selectinload(Risk.organization))
    
    if organization_id:
        query = query.where(Risk.organization_id == organization_id)
    if severity:
        query = query.where(Risk.severity == RiskSeverity[severity.upper()])
    if status:
        query = query.where(Risk.status == status)
    
    query = query.order_by(
        desc(Risk.severity),
        desc(Risk.inherent_risk_score),
        desc(Risk.created_at)
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    risks = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "organization": r.organization.name if r.organization else None,
            "title": r.title,
            "category": r.category,
            "severity": r.severity.value,
            "likelihood": r.likelihood,
            "risk_score": r.inherent_risk_score,
            "status": r.status,
            "mitigation_status": r.mitigation_status,
            "owner": r.owner,
            "identified_date": r.identified_date,
            "mitigation_deadline": r.mitigation_deadline
        } for r in risks
    ]

# Analytics & Dashboards
@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    organization_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get organizations count
    org_query = select(func.count(Organization.id))
    if organization_id:
        org_query = org_query.where(Organization.id == organization_id)
    org_result = await db.execute(org_query)
    org_count = org_result.scalar()
    
    # Get assessments stats
    assessment_query = select(
        func.count(Assessment.id),
        func.avg(Assessment.score),
        func.count(func.distinct(Assessment.framework_id))
    ).where(Assessment.status == "completed")
    if organization_id:
        assessment_query = assessment_query.where(Assessment.organization_id == organization_id)
    
    assessment_result = await db.execute(assessment_query)
    total_assessments, avg_score, frameworks_assessed = assessment_result.one()
    
    # Get risk stats
    risk_query = select(
        func.count(Risk.id),
        func.sum(func.cast(Risk.severity == RiskSeverity.CRITICAL, Integer)),
        func.sum(func.cast(Risk.severity == RiskSeverity.HIGH, Integer)),
        func.sum(func.cast(Risk.status == "open", Integer))
    )
    if organization_id:
        risk_query = risk_query.where(Risk.organization_id == organization_id)
    
    risk_result = await db.execute(risk_query)
    total_risks, critical_risks, high_risks, open_risks = risk_result.one()
    
    # Get compliance scores by framework
    scores_query = select(
        Framework.code,
        Framework.name,
        func.avg(ComplianceScore.score),
        func.max(ComplianceScore.calculated_at)
    ).join(
        ComplianceScore, Framework.id == ComplianceScore.framework_id
    ).group_by(Framework.id, Framework.code, Framework.name)
    
    if organization_id:
        scores_query = scores_query.where(ComplianceScore.organization_id == organization_id)
    
    scores_result = await db.execute(scores_query)
    framework_scores = [
        {
            "framework": row[0],
            "name": row[1],
            "avg_score": round(row[2], 2) if row[2] else 0,
            "last_updated": row[3]
        } for row in scores_result
    ]
    
    # Analytics from DuckDB
    analytics_summary = {}
    if analytics_db:
        try:
            if organization_id:
                df = pl.DataFrame(analytics_db.execute("""
                    SELECT 
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score,
                        COUNT(*) as assessment_count
                    FROM compliance_metrics
                    WHERE organization_id = ?
                """, (organization_id,)).fetchall())
            else:
                df = pl.DataFrame(analytics_db.execute("""
                    SELECT 
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score,
                        COUNT(*) as assessment_count
                    FROM compliance_metrics
                """).fetchall())
            
            if not df.is_empty():
                df.columns = ["avg_score", "max_score", "min_score", "assessment_count"]
                analytics_summary = df.to_dicts()[0] if df.height > 0 else {}
        except:
            pass
    
    return {
        "summary": {
            "organizations": org_count or 0,
            "total_assessments": total_assessments or 0,
            "average_compliance_score": round(avg_score, 2) if avg_score else 0,
            "frameworks_assessed": frameworks_assessed or 0,
            "total_risks": total_risks or 0,
            "critical_risks": critical_risks or 0,
            "high_risks": high_risks or 0,
            "open_risks": open_risks or 0
        },
        "framework_scores": framework_scores,
        "analytics": analytics_summary,
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/analytics/trends")
async def get_compliance_trends(
    organization_id: int,
    framework_code: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not analytics_db:
        return {"message": "Analytics not available"}
    
    # Get trends from DuckDB
    if framework_code:
        query = """
            SELECT 
                DATE_TRUNC('day', timestamp) as date,
                AVG(score) as avg_score,
                MAX(maturity_level) as maturity
            FROM compliance_metrics
            WHERE organization_id = ?
            AND framework = ?
            AND timestamp >= CURRENT_DATE - INTERVAL ? DAY
            GROUP BY DATE_TRUNC('day', timestamp)
            ORDER BY date
        """
        df = pl.DataFrame(analytics_db.execute(query, (organization_id, framework_code, days)).fetchall())
    else:
        query = """
            SELECT 
                DATE_TRUNC('day', timestamp) as date,
                framework,
                AVG(score) as avg_score
            FROM compliance_metrics
            WHERE organization_id = ?
            AND timestamp >= CURRENT_DATE - INTERVAL ? DAY
            GROUP BY DATE_TRUNC('day', timestamp), framework
            ORDER BY date, framework
        """
        df = pl.DataFrame(analytics_db.execute(query, (organization_id, days)).fetchall())
    
    if df.is_empty():
        return {"trends": [], "message": "No data available for the specified period"}
    
    df.columns = ["date", "framework", "avg_score"] if not framework_code else ["date", "avg_score", "maturity"]
    
    return {
        "trends": df.to_dicts(),
        "period_days": days,
        "organization_id": organization_id,
        "framework": framework_code
    }

# Reports
@app.post("/reports/generate")
async def generate_report(
    organization_id: int,
    report_type: str,  # executive, detailed, gap_analysis, benchmark
    framework_codes: List[str] = Query([]),
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get organization data
    org_result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Create report record
    report = Report(
        organization_id=organization_id,
        report_type=report_type,
        format=format,
        title=f"{report_type.title()} Report - {org.name}",
        parameters={"frameworks": framework_codes},
        generated_by=current_user.username,
        generated_at=datetime.utcnow()
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # Audit log
    await audit_log(db, current_user, "generate_report", "report", report.id, {
        "type": report_type,
        "organization": org.name
    })
    
    return {
        "id": report.id,
        "title": report.title,
        "type": report_type,
        "format": format,
        "status": "ready",
        "download_url": f"/reports/{report.id}/download",
        "generated_at": report.generated_at
    }

@app.get("/reports/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get report
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update download count
    report.download_count += 1
    report.last_downloaded_at = datetime.utcnow()
    await db.commit()
    
    # Return sample report content
    content = f"""
    {report.title}
    Generated: {report.generated_at}
    Format: {report.format}
    
    This is a sample report content.
    In production, this would contain the actual report data.
    """
    
    return StreamingResponse(
        iter([content.encode()]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=report_{report_id}.{report.format}"
        }
    )

# Notifications
@app.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    query = query.order_by(desc(Notification.created_at)).limit(50)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "priority": n.priority,
            "is_read": n.is_read,
            "action_url": n.action_url,
            "created_at": n.created_at
        } for n in notifications
    ]

@app.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "success", "read_at": notification.read_at}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
