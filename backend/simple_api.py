"""
Simplified Dogan AI Compliance Platform API
Ready for production with Saudi compliance features
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from passlib.context import CryptContext
import uvicorn

from backend.models import *

# Environment configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Database setup
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Dogan AI Compliance Platform...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed initial data
    await seed_initial_data()
    
    yield
    
    print("🔄 Shutting down...")
    await engine.dispose()

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

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Seed initial data
async def seed_initial_data():
    async with async_session() as db:
        # Check if data exists
        result = await db.execute(select(func.count(Framework.id)))
        if result.scalar() > 0:
            return
        
        print("📦 Seeding initial data...")
        
        # Create demo user
        demo_user = User(
            email="admin@doganai.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrator",
            full_name_arabic="المسؤول",
            role=UserRole.ADMIN
        )
        db.add(demo_user)
        
        # Create control categories
        categories = [
            ControlCategory(name="Governance", name_arabic="الحوكمة"),
            ControlCategory(name="Risk Management", name_arabic="إدارة المخاطر"),
            ControlCategory(name="Access Control", name_arabic="التحكم في الوصول"),
            ControlCategory(name="Data Protection", name_arabic="حماية البيانات"),
            ControlCategory(name="Incident Response", name_arabic="الاستجابة للحوادث"),
        ]
        db.add_all(categories)
        
        # Create frameworks
        frameworks = [
            Framework(
                code="NCA",
                name="National Cybersecurity Authority",
                name_arabic="الهيئة الوطنية للأمن السيبراني",
                authority="NCA",
                is_saudi=True,
                is_mandatory=True,
                version="2024"
            ),
            Framework(
                code="SAMA",
                name="SAMA Cyber Security Framework",
                name_arabic="إطار الأمن السيبراني للبنك المركزي السعودي",
                authority="Saudi Central Bank",
                is_saudi=True,
                is_mandatory=True,
                version="2024"
            ),
            Framework(
                code="PDPL",
                name="Personal Data Protection Law",
                name_arabic="نظام حماية البيانات الشخصية",
                authority="NDMO",
                is_saudi=True,
                is_mandatory=True,
                version="2024"
            ),
            Framework(
                code="ISO27001",
                name="ISO 27001:2022",
                authority="ISO",
                is_saudi=False,
                version="2022"
            ),
            Framework(
                code="NIST",
                name="NIST Cybersecurity Framework",
                authority="NIST",
                is_saudi=False,
                version="2.0"
            ),
        ]
        db.add_all(frameworks)
        
        await db.commit()
        print("✅ Initial data seeded")

# API Routes

@app.get("/")
async def root():
    return {
        "platform": "Dogan AI Compliance Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "saudi_frameworks": ["NCA", "SAMA", "PDPL"],
            "international": ["ISO27001", "NIST"],
            "languages": ["English", "Arabic"],
            "database": "PostgreSQL"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "api": "operational"
        }
    }

# Authentication
@app.post("/auth/login")
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    # Get user
    from sqlalchemy import or_
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
    
    # Create simple token (for demo)
    access_token = f"token_{user.username}_{datetime.utcnow().timestamp()}"
    
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

@app.post("/auth/register")
async def register(
    email: str,
    username: str,
    password: str,
    full_name: str,
    full_name_arabic: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import or_
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
    await db.commit()
    await db.refresh(user)
    
    # Create token
    access_token = f"token_{user.username}_{datetime.utcnow().timestamp()}"
    
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

# Organizations
@app.get("/organizations")
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    
    query = select(Organization).options(selectinload(Organization.owner))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    organizations = result.scalars().all()
    
    return [
        {
            "id": org.id,
            "name": org.name,
            "name_arabic": org.name_arabic,
            "sector": org.sector.value if org.sector else None,
            "city": org.city,
            "size": org.size,
            "owner": org.owner.full_name if org.owner else None,
            "created_at": org.created_at
        } for org in organizations
    ]

@app.post("/organizations")
async def create_organization(
    name: str,
    sector: str,
    name_arabic: Optional[str] = None,
    city: Optional[str] = None,
    size: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    org = Organization(
        name=name,
        name_arabic=name_arabic,
        sector=Sector[sector.upper()],
        city=city,
        size=size
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    return {
        "id": org.id,
        "name": org.name,
        "sector": org.sector.value,
        "created_at": org.created_at
    }

# Frameworks
@app.get("/frameworks")
async def list_frameworks(
    saudi_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    
    query = select(Framework).options(selectinload(Framework.controls))
    if saudi_only:
        query = query.where(Framework.is_saudi == True)
    
    result = await db.execute(query)
    frameworks = result.scalars().all()
    
    return [
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

@app.get("/frameworks/{framework_code}/controls")
async def get_framework_controls(
    framework_code: str,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    
    # Get framework
    result = await db.execute(
        select(Framework).where(Framework.code == framework_code)
    )
    framework = result.scalar_one_or_none()
    
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Get controls
    query = select(Control).where(Control.framework_id == framework.id)
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
                "automation_possible": c.automation_possible
            } for c in controls
        ],
        "total": len(controls)
    }

# Assessments
@app.get("/assessments")
async def list_assessments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    
    query = select(Assessment).options(
        selectinload(Assessment.organization),
        selectinload(Assessment.framework),
        selectinload(Assessment.assessor)
    )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    assessments = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "organization": a.organization.name if a.organization else None,
            "framework": a.framework.name if a.framework else None,
            "type": a.assessment_type,
            "score": a.score,
            "maturity_level": a.maturity_level,
            "status": a.status,
            "assessor": a.assessor.full_name if a.assessor else None,
            "started_at": a.started_at,
            "completed_at": a.completed_at
        } for a in assessments
    ]

@app.post("/assessments")
async def create_assessment(
    organization_id: int,
    framework_code: str,
    assessment_type: str = "initial",
    db: AsyncSession = Depends(get_db)
):
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
        assessment_type=assessment_type,
        status="in_progress",
        started_at=datetime.utcnow()
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    return {
        "id": assessment.id,
        "framework": framework.name,
        "type": assessment_type,
        "status": assessment.status,
        "started_at": assessment.started_at
    }

# Risks
@app.get("/risks")
async def list_risks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    
    query = select(Risk).options(selectinload(Risk.organization))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    risks = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "organization": r.organization.name if r.organization else None,
            "title": r.title,
            "category": r.category,
            "severity": r.severity.value if r.severity else None,
            "likelihood": r.likelihood,
            "risk_score": r.inherent_risk_score,
            "status": r.status,
            "mitigation_status": r.mitigation_status,
            "owner": r.owner,
            "identified_date": r.identified_date,
            "mitigation_deadline": r.mitigation_deadline
        } for r in risks
    ]

@app.post("/risks")
async def create_risk(
    organization_id: int,
    title: str,
    severity: str,
    likelihood: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Calculate risk score
    severity_scores = {"critical": 5, "high": 4, "medium": 3, "low": 2, "minimal": 1}
    likelihood_scores = {"very_high": 5, "high": 4, "medium": 3, "low": 2, "very_low": 1}
    
    inherent_score = severity_scores.get(severity.lower(), 3) * likelihood_scores.get(likelihood.lower().replace(" ", "_"), 3)
    
    risk = Risk(
        organization_id=organization_id,
        title=title,
        description=description,
        category=category,
        severity=RiskSeverity[severity.upper()],
        likelihood=likelihood,
        inherent_risk_score=inherent_score,
        status="open"
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    
    return {
        "id": risk.id,
        "title": risk.title,
        "severity": risk.severity.value,
        "likelihood": risk.likelihood,
        "risk_score": inherent_score,
        "status": risk.status,
        "created_at": risk.created_at
    }

# Analytics Dashboard
@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    organization_id: Optional[int] = None,
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
    from sqlalchemy import cast, Integer
    risk_query = select(
        func.count(Risk.id),
        func.sum(cast(Risk.severity == RiskSeverity.CRITICAL, Integer)),
        func.sum(cast(Risk.severity == RiskSeverity.HIGH, Integer)),
        func.sum(cast(Risk.status == "open", Integer))
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
        "generated_at": datetime.utcnow().isoformat()
    }

# Reports
@app.post("/reports/generate")
async def generate_report(
    organization_id: int,
    report_type: str,
    framework_codes: List[str] = [],
    format: str = "pdf",
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
        generated_by="system",
        generated_at=datetime.utcnow()
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
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
async def download_report(report_id: int):
    # Return sample report content
    content = f"""
    Compliance Report #{report_id}
    Generated: {datetime.utcnow()}
    
    This is a sample report content.
    In production, this would contain the actual report data.
    """
    
    from fastapi.responses import StreamingResponse
    import io
    
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename=report_{report_id}.txt"
        }
    )

# Notifications
@app.get("/notifications")
async def get_notifications():
    # Return sample notifications
    return [
        {
            "id": 1,
            "title": "New Assessment Required",
            "message": "SAMA framework assessment is due for renewal",
            "type": "warning",
            "priority": "high",
            "is_read": False,
            "created_at": datetime.utcnow()
        },
        {
            "id": 2,
            "title": "Risk Mitigation Deadline",
            "message": "Critical risk mitigation deadline approaching",
            "type": "alert",
            "priority": "urgent",
            "is_read": False,
            "created_at": datetime.utcnow()
        }
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
