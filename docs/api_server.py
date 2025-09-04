"""
Advanced Compliance Platform - FastAPI Backend
Production-ready with SQLAlchemy, PostgreSQL, Redis, DuckDB
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, select, func
from passlib.context import CryptContext
from jose import JWTError, jwt
import redis.asyncio as redis
import duckdb
import polars as pl
import json
import uvicorn

# Environment configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/compliance")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# Convert to async URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Redis client
redis_client = None

# DuckDB connection for analytics
analytics_db = duckdb.connect(':memory:')

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organizations = relationship("Organization", back_populates="owner")
    assessments = relationship("Assessment", back_populates="assessor")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sector = Column(String, nullable=False)
    country = Column(String, default="Saudi Arabia")
    size = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    owner = relationship("User", back_populates="organizations")
    assessments = relationship("Assessment", back_populates="organization")
    controls = relationship("ControlImplementation", back_populates="organization")

class Framework(Base):
    __tablename__ = "frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    version = Column(String)
    description = Column(Text)
    authority = Column(String)
    is_saudi = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    controls = relationship("Control", back_populates="framework")
    assessments = relationship("Assessment", back_populates="framework")

class Control(Base):
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id"))
    control_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    priority = Column(String)
    evidence_required = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    
    framework = relationship("Framework", back_populates="controls")
    implementations = relationship("ControlImplementation", back_populates="control")

class ControlImplementation(Base):
    __tablename__ = "control_implementations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    control_id = Column(Integer, ForeignKey("controls.id"))
    status = Column(String, default="not_implemented")
    implementation_date = Column(DateTime)
    evidence = Column(JSON, default={})
    notes = Column(Text)
    score = Column(Float, default=0.0)
    
    organization = relationship("Organization", back_populates="controls")
    control = relationship("Control", back_populates="implementations")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    framework_id = Column(Integer, ForeignKey("frameworks.id"))
    assessor_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float, nullable=False)
    status = Column(String, default="in_progress")
    findings = Column(JSON, default={})
    recommendations = Column(JSON, default=[])
    assessed_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    organization = relationship("Organization", back_populates="assessments")
    framework = relationship("Framework", back_populates="assessments")
    assessor = relationship("User", back_populates="assessments")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    severity = Column(String, nullable=False)
    likelihood = Column(String, nullable=False)
    risk_score = Column(Float)
    mitigation_plan = Column(Text)
    owner = Column(String)
    status = Column(String, default="open")
    identified_date = Column(DateTime, default=datetime.utcnow)
    resolved_date = Column(DateTime)

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Redis
    try:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        print("✅ Redis connected")
    except:
        print("⚠️ Redis not available, continuing without cache")
        redis_client = None
    
    # Initialize DuckDB analytics tables
    analytics_db.execute("""
        CREATE TABLE IF NOT EXISTS compliance_metrics (
            organization_id INTEGER,
            framework TEXT,
            score FLOAT,
            timestamp TIMESTAMP,
            controls_passed INTEGER,
            controls_total INTEGER
        )
    """)
    
    # Seed initial frameworks if empty
    async with async_session() as session:
        result = await session.execute(select(func.count(Framework.id)))
        count = result.scalar()
        if count == 0:
            frameworks = [
                Framework(code="NCA", name="National Cybersecurity Authority", authority="NCA Saudi Arabia", is_saudi=True),
                Framework(code="SAMA", name="Saudi Arabian Monetary Authority", authority="SAMA", is_saudi=True),
                Framework(code="PDPL", name="Personal Data Protection Law", authority="NDMO", is_saudi=True),
                Framework(code="ISO27001", name="ISO 27001:2022", authority="ISO", is_saudi=False),
                Framework(code="NIST", name="NIST Cybersecurity Framework", authority="NIST", is_saudi=False),
            ]
            session.add_all(frameworks)
            await session.commit()
            print("✅ Frameworks initialized")
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    analytics_db.close()
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="Dogan AI Compliance Platform API",
    description="Advanced compliance platform with real-time analytics",
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

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session

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
    return user

# Cache decorator
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
            await redis_client.setex(key, expire, json.dumps(value))
        except:
            pass

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Dogan AI Advanced Compliance Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": ["PostgreSQL", "Redis Cache", "DuckDB Analytics", "JWT Auth", "Real-time Processing"]
    }

@app.post("/auth/register")
async def register(
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    result = await db.execute(select(User).where((User.email == email) | (User.username == username)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }

@app.post("/auth/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role}
    }

@app.get("/frameworks")
async def list_frameworks(db: AsyncSession = Depends(get_db)):
    # Check cache
    cached = await cache_get("frameworks")
    if cached:
        return cached
    
    result = await db.execute(select(Framework))
    frameworks = result.scalars().all()
    
    data = [
        {
            "id": f.id,
            "code": f.code,
            "name": f.name,
            "authority": f.authority,
            "is_saudi": f.is_saudi
        } for f in frameworks
    ]
    
    await cache_set("frameworks", data)
    return data

@app.post("/organizations")
async def create_organization(
    name: str,
    sector: str,
    size: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org = Organization(
        name=name,
        sector=sector,
        size=size,
        owner_id=current_user.id
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    return {
        "id": org.id,
        "name": org.name,
        "sector": org.sector,
        "created": org.created_at
    }

@app.post("/assessments")
async def create_assessment(
    organization_id: int,
    framework_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get framework
    result = await db.execute(select(Framework).where(Framework.code == framework_code))
    framework = result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    # Create assessment
    assessment = Assessment(
        organization_id=organization_id,
        framework_id=framework.id,
        assessor_id=current_user.id,
        score=0.0,
        status="in_progress"
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    # Store in analytics
    analytics_db.execute("""
        INSERT INTO compliance_metrics VALUES (?, ?, ?, ?, ?, ?)
    """, (organization_id, framework_code, 0.0, datetime.now(), 0, 0))
    
    return {
        "id": assessment.id,
        "organization_id": assessment.organization_id,
        "framework": framework_code,
        "status": assessment.status,
        "assessor": current_user.username
    }

@app.get("/analytics/summary")
async def get_analytics_summary(current_user: User = Depends(get_current_user)):
    # Query DuckDB for analytics
    df = pl.DataFrame(analytics_db.execute("""
        SELECT 
            framework,
            AVG(score) as avg_score,
            COUNT(DISTINCT organization_id) as org_count,
            MAX(timestamp) as last_assessment
        FROM compliance_metrics
        GROUP BY framework
    """).fetchall())
    
    if df.is_empty():
        return {"message": "No analytics data available yet"}
    
    df.columns = ["framework", "avg_score", "org_count", "last_assessment"]
    
    return {
        "summary": df.to_dicts(),
        "generated_at": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected" if redis_client else "not available",
            "analytics": "operational"
        }
    }
    
    # Check database
    try:
        async with async_session() as session:
            await session.execute(select(1))
    except:
        health["services"]["database"] = "error"
        health["status"] = "degraded"
    
    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
        except:
            health["services"]["redis"] = "error"
    
    return health

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)