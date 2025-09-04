#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Ministry of Interior API Service
Urgent Delivery - Production Ready

Ministry-specific API endpoints for continuous database upload system
with operational technology principles and security compliance.
"""

import asyncio
import asyncpg
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid
import hashlib
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

APP_NAME = "Ministry of Interior API Service"
APP_VERSION = "1.0.0"
ENVIRONMENT = "production"

# Setup structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "ministry_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "ministry_api_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)

ACTIVE_OPERATIONS = Gauge(
    "ministry_active_operations",
    "Number of active operations"
)

PERSONNEL_COUNT = Gauge(
    "ministry_personnel_count",
    "Total personnel count",
    ["department", "status"]
)

INCIDENT_COUNT = Gauge(
    "ministry_incidents_count",
    "Number of incidents",
    ["severity", "status"]
)

# =============================================================================
# DATA MODELS
# =============================================================================

class MinistryClassification(str, Enum):
    UNCLASSIFIED = "unclassified"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class MinistryPriority(str, Enum):
    ROUTINE = "routine"
    PRIORITY = "priority"
    IMMEDIATE = "immediate"
    FLASH = "flash"
    CRITICAL = "critical"

class MinistryDepartment(str, Enum):
    CIVIL_DEFENSE = "civil_defense"
    PUBLIC_SECURITY = "public_security"
    BORDER_GUARD = "border_guard"
    EMERGENCY_MANAGEMENT = "emergency_management"
    PASSPORT_DIRECTORATE = "passport_directorate"
    INVESTIGATION = "investigation"
    FORENSICS = "forensics"
    CYBER_SECURITY = "cyber_security"
    INTELLIGENCE = "intelligence"
    ADMINISTRATION = "administration"

class OperationStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"

# Request/Response Models
class OperationCreate(BaseModel):
    operation_id: str = Field(..., min_length=1, max_length=100)
    department: MinistryDepartment
    operation_type: str = Field(..., min_length=1, max_length=100)
    classification: MinistryClassification = MinistryClassification.UNCLASSIFIED
    priority: MinistryPriority = MinistryPriority.ROUTINE
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    personnel_involved: Optional[List[str]] = None
    resources_allocated: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    estimated_duration: Optional[str] = None  # ISO 8601 duration
    created_by: str = Field(..., min_length=1, max_length=100)

class OperationResponse(BaseModel):
    id: str
    operation_id: str
    department: MinistryDepartment
    operation_type: str
    classification: MinistryClassification
    priority: MinistryPriority
    title: str
    description: Optional[str]
    status: OperationStatus
    location: Optional[Dict[str, Any]]
    personnel_involved: Optional[List[str]]
    resources_allocated: Optional[Dict[str, Any]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    estimated_duration: Optional[str]
    actual_duration: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int

class IncidentCreate(BaseModel):
    incident_id: str = Field(..., min_length=1, max_length=100)
    incident_type: str = Field(..., min_length=1, max_length=100)
    severity: IncidentSeverity
    classification: MinistryClassification = MinistryClassification.UNCLASSIFIED
    priority: MinistryPriority = MinistryPriority.ROUTINE
    department: MinistryDepartment
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    location: Dict[str, Any] = Field(...)
    reported_by: str = Field(..., min_length=1, max_length=100)
    occurred_at: Optional[datetime] = None
    discovered_at: Optional[datetime] = None

class IncidentResponse(BaseModel):
    id: str
    incident_id: str
    incident_type: str
    severity: IncidentSeverity
    classification: MinistryClassification
    priority: MinistryPriority
    department: MinistryDepartment
    title: str
    description: str
    location: Dict[str, Any]
    status: str
    reported_by: str
    reported_at: datetime
    occurred_at: Optional[datetime]
    discovered_at: Optional[datetime]
    assigned_to: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

class PersonnelResponse(BaseModel):
    id: str
    personnel_id: str
    rank: str
    department: MinistryDepartment
    full_name: str
    position: str
    security_clearance: MinistryClassification
    deployment_status: str
    current_assignment: Optional[str]
    active: bool
    created_at: datetime

class AssetResponse(BaseModel):
    id: str
    asset_id: str
    asset_type: str
    category: str
    name: str
    department: Optional[MinistryDepartment]
    assigned_to: Optional[str]
    operational_status: str
    condition: str
    location: Optional[Dict[str, Any]]
    created_at: datetime

class SystemStatus(BaseModel):
    service: str
    version: str
    status: str
    timestamp: datetime
    database_connected: bool
    active_operations: int
    total_personnel: int
    recent_incidents: int
    system_health: float

class MinistryDataResponse(BaseModel):
    operations: List[OperationResponse]
    incidents: List[IncidentResponse]
    personnel_summary: Dict[str, int]
    asset_summary: Dict[str, int]
    metrics: Dict[str, Any]
    timestamp: datetime

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.connected = False
    
    async def connect(self):
        """Connect to the database"""
        try:
            database_url = "postgresql://doganai:MinistrySecure2024!@ministry_postgres:5432/ministry_db"
            
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=30,
                server_settings={
                    'application_name': 'Ministry_API_Service',
                    'timezone': 'Asia/Riyadh'
                }
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            
            self.connected = True
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.pool:
            await self.pool.close()
            self.connected = False
            logger.info("Database connection closed")
    
    async def get_connection(self):
        """Get a database connection"""
        if not self.connected or not self.pool:
            await self.connect()
        return self.pool.acquire()

# Global database manager
db_manager = DatabaseManager()

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Ministry of Interior API Service for Continuous Database Upload System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    try:
        await db_manager.connect()
        await update_metrics()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")
    await db_manager.disconnect()
    logger.info("Application shutdown completed")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def update_metrics():
    """Update Prometheus metrics"""
    try:
        async with db_manager.get_connection() as conn:
            # Active operations
            active_ops = await conn.fetchval(
                "SELECT COUNT(*) FROM ministry_operations WHERE status IN ('planned', 'in_progress', 'on_hold')"
            )
            ACTIVE_OPERATIONS.set(active_ops or 0)
            
            # Personnel count by department
            personnel_stats = await conn.fetch(
                "SELECT department, deployment_status, COUNT(*) as count FROM ministry_personnel WHERE active = TRUE GROUP BY department, deployment_status"
            )
            
            for row in personnel_stats:
                PERSONNEL_COUNT.labels(
                    department=row['department'],
                    status=row['deployment_status']
                ).set(row['count'])
            
            # Incident count by severity
            incident_stats = await conn.fetch(
                "SELECT severity, status, COUNT(*) as count FROM ministry_incidents WHERE reported_at >= NOW() - INTERVAL '7 days' GROUP BY severity, status"
            )
            
            for row in incident_stats:
                INCIDENT_COUNT.labels(
                    severity=row['severity'],
                    status=row['status']
                ).set(row['count'])
                
    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")

def calculate_checksum(data: Dict[str, Any]) -> str:
    """Calculate data checksum for integrity"""
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_str.encode()).hexdigest()

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with db_manager.get_connection() as conn:
            await conn.execute('SELECT 1')
            db_connected = True
    except:
        db_connected = False
    
    # Get basic stats
    active_ops = 0
    total_personnel = 0
    recent_incidents = 0
    
    if db_connected:
        try:
            async with db_manager.get_connection() as conn:
                active_ops = await conn.fetchval(
                    "SELECT COUNT(*) FROM ministry_operations WHERE status IN ('planned', 'in_progress', 'on_hold')"
                ) or 0
                
                total_personnel = await conn.fetchval(
                    "SELECT COUNT(*) FROM ministry_personnel WHERE active = TRUE"
                ) or 0
                
                recent_incidents = await conn.fetchval(
                    "SELECT COUNT(*) FROM ministry_incidents WHERE reported_at >= NOW() - INTERVAL '24 hours'"
                ) or 0
        except:
            pass
    
    # Calculate health score
    health_score = 100.0 if db_connected else 0.0
    
    return SystemStatus(
        service=APP_NAME,
        version=APP_VERSION,
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.now(timezone.utc),
        database_connected=db_connected,
        active_operations=active_ops,
        total_personnel=total_personnel,
        recent_incidents=recent_incidents,
        system_health=health_score
    )

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    await update_metrics()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/ministry/data", response_model=MinistryDataResponse)
async def get_ministry_data(
    department: Optional[MinistryDepartment] = None,
    classification: Optional[MinistryClassification] = None,
    limit: int = 100
):
    """Get comprehensive ministry data for continuous upload system"""
    try:
        async with db_manager.get_connection() as conn:
            # Build WHERE clauses
            where_conditions = []
            params = []
            
            if department:
                where_conditions.append(f"department = ${len(params) + 1}")
                params.append(department.value)
            
            if classification:
                where_conditions.append(f"classification = ${len(params) + 1}")
                params.append(classification.value)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Get operations
            operations_query = f"""
                SELECT id, operation_id, department, operation_type, classification, priority,
                       title, description, status, location, personnel_involved, resources_allocated,
                       start_time, end_time, estimated_duration, actual_duration,
                       created_by, created_at, updated_at, version
                FROM ministry_operations 
                WHERE {where_clause}
                ORDER BY created_at DESC 
                LIMIT ${len(params) + 1}
            """
            
            operations_rows = await conn.fetch(operations_query, *params, limit)
            operations = [
                OperationResponse(
                    id=str(row['id']),
                    operation_id=row['operation_id'],
                    department=MinistryDepartment(row['department']),
                    operation_type=row['operation_type'],
                    classification=MinistryClassification(row['classification']),
                    priority=MinistryPriority(row['priority']),
                    title=row['title'],
                    description=row['description'],
                    status=OperationStatus(row['status']),
                    location=row['location'],
                    personnel_involved=row['personnel_involved'],
                    resources_allocated=row['resources_allocated'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    estimated_duration=row['estimated_duration'],
                    actual_duration=row['actual_duration'],
                    created_by=row['created_by'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    version=row['version']
                ) for row in operations_rows
            ]
            
            # Get incidents
            incidents_query = f"""
                SELECT id, incident_id, incident_type, severity, classification, priority,
                       department, title, description, location, status, reported_by,
                       reported_at, occurred_at, discovered_at, assigned_to,
                       created_at, updated_at
                FROM ministry_incidents 
                WHERE {where_clause}
                ORDER BY reported_at DESC 
                LIMIT ${len(params) + 1}
            """
            
            incidents_rows = await conn.fetch(incidents_query, *params, limit)
            incidents = [
                IncidentResponse(
                    id=str(row['id']),
                    incident_id=row['incident_id'],
                    incident_type=row['incident_type'],
                    severity=IncidentSeverity(row['severity']),
                    classification=MinistryClassification(row['classification']),
                    priority=MinistryPriority(row['priority']),
                    department=MinistryDepartment(row['department']),
                    title=row['title'],
                    description=row['description'],
                    location=row['location'],
                    status=row['status'],
                    reported_by=row['reported_by'],
                    reported_at=row['reported_at'],
                    occurred_at=row['occurred_at'],
                    discovered_at=row['discovered_at'],
                    assigned_to=row['assigned_to'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ) for row in incidents_rows
            ]
            
            # Get personnel summary
            personnel_summary_rows = await conn.fetch(
                "SELECT department, deployment_status, COUNT(*) as count FROM ministry_personnel WHERE active = TRUE GROUP BY department, deployment_status"
            )
            personnel_summary = {}
            for row in personnel_summary_rows:
                key = f"{row['department']}_{row['deployment_status']}"
                personnel_summary[key] = row['count']
            
            # Get asset summary
            asset_summary_rows = await conn.fetch(
                "SELECT asset_type, operational_status, COUNT(*) as count FROM ministry_assets GROUP BY asset_type, operational_status"
            )
            asset_summary = {}
            for row in asset_summary_rows:
                key = f"{row['asset_type']}_{row['operational_status']}"
                asset_summary[key] = row['count']
            
            # Calculate metrics
            metrics = {
                "total_operations": len(operations),
                "total_incidents": len(incidents),
                "active_operations": len([op for op in operations if op.status in [OperationStatus.PLANNED, OperationStatus.IN_PROGRESS]]),
                "critical_incidents": len([inc for inc in incidents if inc.severity == IncidentSeverity.CRITICAL]),
                "data_freshness": datetime.now(timezone.utc).isoformat(),
                "checksum": calculate_checksum({
                    "operations_count": len(operations),
                    "incidents_count": len(incidents),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
            
            return MinistryDataResponse(
                operations=operations,
                incidents=incidents,
                personnel_summary=personnel_summary,
                asset_summary=asset_summary,
                metrics=metrics,
                timestamp=datetime.now(timezone.utc)
            )
            
    except Exception as e:
        logger.error(f"Failed to get ministry data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ministry data: {str(e)}")

@app.get("/api/ministry/operations", response_model=List[OperationResponse])
async def get_operations(
    department: Optional[MinistryDepartment] = None,
    status: Optional[OperationStatus] = None,
    priority: Optional[MinistryPriority] = None,
    limit: int = 50
):
    """Get ministry operations"""
    try:
        async with db_manager.get_connection() as conn:
            where_conditions = []
            params = []
            
            if department:
                where_conditions.append(f"department = ${len(params) + 1}")
                params.append(department.value)
            
            if status:
                where_conditions.append(f"status = ${len(params) + 1}")
                params.append(status.value)
            
            if priority:
                where_conditions.append(f"priority = ${len(params) + 1}")
                params.append(priority.value)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT id, operation_id, department, operation_type, classification, priority,
                       title, description, status, location, personnel_involved, resources_allocated,
                       start_time, end_time, estimated_duration, actual_duration,
                       created_by, created_at, updated_at, version
                FROM ministry_operations 
                WHERE {where_clause}
                ORDER BY created_at DESC 
                LIMIT ${len(params) + 1}
            """
            
            rows = await conn.fetch(query, *params, limit)
            
            return [
                OperationResponse(
                    id=str(row['id']),
                    operation_id=row['operation_id'],
                    department=MinistryDepartment(row['department']),
                    operation_type=row['operation_type'],
                    classification=MinistryClassification(row['classification']),
                    priority=MinistryPriority(row['priority']),
                    title=row['title'],
                    description=row['description'],
                    status=OperationStatus(row['status']),
                    location=row['location'],
                    personnel_involved=row['personnel_involved'],
                    resources_allocated=row['resources_allocated'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    estimated_duration=row['estimated_duration'],
                    actual_duration=row['actual_duration'],
                    created_by=row['created_by'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    version=row['version']
                ) for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get operations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve operations: {str(e)}")

@app.post("/api/ministry/operations", response_model=OperationResponse)
async def create_operation(operation: OperationCreate, background_tasks: BackgroundTasks):
    """Create a new ministry operation"""
    try:
        async with db_manager.get_connection() as conn:
            # Check if operation_id already exists
            existing = await conn.fetchval(
                "SELECT id FROM ministry_operations WHERE operation_id = $1",
                operation.operation_id
            )
            
            if existing:
                raise HTTPException(status_code=400, detail="Operation ID already exists")
            
            # Insert new operation
            operation_id = str(uuid.uuid4())
            
            row = await conn.fetchrow("""
                INSERT INTO ministry_operations 
                (id, operation_id, department, operation_type, classification, priority,
                 title, description, location, personnel_involved, resources_allocated,
                 start_time, estimated_duration, created_by, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 'planned')
                RETURNING id, operation_id, department, operation_type, classification, priority,
                          title, description, status, location, personnel_involved, resources_allocated,
                          start_time, end_time, estimated_duration, actual_duration,
                          created_by, created_at, updated_at, version
            """, 
                operation_id, operation.operation_id, operation.department.value,
                operation.operation_type, operation.classification.value, operation.priority.value,
                operation.title, operation.description, operation.location,
                operation.personnel_involved, operation.resources_allocated,
                operation.start_time, operation.estimated_duration, operation.created_by
            )
            
            # Schedule metrics update
            background_tasks.add_task(update_metrics)
            
            return OperationResponse(
                id=str(row['id']),
                operation_id=row['operation_id'],
                department=MinistryDepartment(row['department']),
                operation_type=row['operation_type'],
                classification=MinistryClassification(row['classification']),
                priority=MinistryPriority(row['priority']),
                title=row['title'],
                description=row['description'],
                status=OperationStatus(row['status']),
                location=row['location'],
                personnel_involved=row['personnel_involved'],
                resources_allocated=row['resources_allocated'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                estimated_duration=row['estimated_duration'],
                actual_duration=row['actual_duration'],
                created_by=row['created_by'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                version=row['version']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create operation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create operation: {str(e)}")

@app.get("/api/ministry/incidents", response_model=List[IncidentResponse])
async def get_incidents(
    department: Optional[MinistryDepartment] = None,
    severity: Optional[IncidentSeverity] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get ministry incidents"""
    try:
        async with db_manager.get_connection() as conn:
            where_conditions = []
            params = []
            
            if department:
                where_conditions.append(f"department = ${len(params) + 1}")
                params.append(department.value)
            
            if severity:
                where_conditions.append(f"severity = ${len(params) + 1}")
                params.append(severity.value)
            
            if status:
                where_conditions.append(f"status = ${len(params) + 1}")
                params.append(status)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT id, incident_id, incident_type, severity, classification, priority,
                       department, title, description, location, status, reported_by,
                       reported_at, occurred_at, discovered_at, assigned_to,
                       created_at, updated_at
                FROM ministry_incidents 
                WHERE {where_clause}
                ORDER BY reported_at DESC 
                LIMIT ${len(params) + 1}
            """
            
            rows = await conn.fetch(query, *params, limit)
            
            return [
                IncidentResponse(
                    id=str(row['id']),
                    incident_id=row['incident_id'],
                    incident_type=row['incident_type'],
                    severity=IncidentSeverity(row['severity']),
                    classification=MinistryClassification(row['classification']),
                    priority=MinistryPriority(row['priority']),
                    department=MinistryDepartment(row['department']),
                    title=row['title'],
                    description=row['description'],
                    location=row['location'],
                    status=row['status'],
                    reported_by=row['reported_by'],
                    reported_at=row['reported_at'],
                    occurred_at=row['occurred_at'],
                    discovered_at=row['discovered_at'],
                    assigned_to=row['assigned_to'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ) for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get incidents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve incidents: {str(e)}")

@app.get("/api/ministry/personnel", response_model=List[PersonnelResponse])
async def get_personnel(
    department: Optional[MinistryDepartment] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Get ministry personnel"""
    try:
        async with db_manager.get_connection() as conn:
            where_conditions = ["active = TRUE"]
            params = []
            
            if department:
                where_conditions.append(f"department = ${len(params) + 1}")
                params.append(department.value)
            
            if status:
                where_conditions.append(f"deployment_status = ${len(params) + 1}")
                params.append(status)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, personnel_id, rank, department, full_name, position,
                       security_clearance, deployment_status, current_assignment,
                       active, created_at
                FROM ministry_personnel 
                WHERE {where_clause}
                ORDER BY department, rank 
                LIMIT ${len(params) + 1}
            """
            
            rows = await conn.fetch(query, *params, limit)
            
            return [
                PersonnelResponse(
                    id=str(row['id']),
                    personnel_id=row['personnel_id'],
                    rank=row['rank'],
                    department=MinistryDepartment(row['department']),
                    full_name=row['full_name'],
                    position=row['position'],
                    security_clearance=MinistryClassification(row['security_clearance']),
                    deployment_status=row['deployment_status'],
                    current_assignment=row['current_assignment'],
                    active=row['active'],
                    created_at=row['created_at']
                ) for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get personnel: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve personnel: {str(e)}")

@app.get("/api/ministry/assets", response_model=List[AssetResponse])
async def get_assets(
    asset_type: Optional[str] = None,
    department: Optional[MinistryDepartment] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Get ministry assets"""
    try:
        async with db_manager.get_connection() as conn:
            where_conditions = []
            params = []
            
            if asset_type:
                where_conditions.append(f"asset_type = ${len(params) + 1}")
                params.append(asset_type)
            
            if department:
                where_conditions.append(f"department = ${len(params) + 1}")
                params.append(department.value)
            
            if status:
                where_conditions.append(f"operational_status = ${len(params) + 1}")
                params.append(status)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT id, asset_id, asset_type, category, name, department,
                       assigned_to, operational_status, condition, location, created_at
                FROM ministry_assets 
                WHERE {where_clause}
                ORDER BY asset_type, name 
                LIMIT ${len(params) + 1}
            """
            
            rows = await conn.fetch(query, *params, limit)
            
            return [
                AssetResponse(
                    id=str(row['id']),
                    asset_id=row['asset_id'],
                    asset_type=row['asset_type'],
                    category=row['category'],
                    name=row['name'],
                    department=MinistryDepartment(row['department']) if row['department'] else None,
                    assigned_to=row['assigned_to'],
                    operational_status=row['operational_status'],
                    condition=row['condition'],
                    location=row['location'],
                    created_at=row['created_at']
                ) for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get assets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assets: {str(e)}")

@app.get("/api/ministry/reports")
async def get_ministry_reports(
    report_type: Optional[str] = None,
    department: Optional[MinistryDepartment] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """Get ministry reports and analytics"""
    try:
        async with db_manager.get_connection() as conn:
            # Operations summary
            ops_summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_operations,
                    COUNT(*) FILTER (WHERE status = 'planned') as planned,
                    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE priority = 'critical') as critical_priority
                FROM ministry_operations
                WHERE created_at >= COALESCE($1, NOW() - INTERVAL '30 days')
                  AND created_at <= COALESCE($2, NOW())
            """, date_from, date_to)
            
            # Incidents summary
            incidents_summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_incidents,
                    COUNT(*) FILTER (WHERE severity = 'critical') as critical,
                    COUNT(*) FILTER (WHERE severity = 'high') as high,
                    COUNT(*) FILTER (WHERE status = 'reported') as open_incidents,
                    AVG(EXTRACT(EPOCH FROM (COALESCE(closed_at, NOW()) - reported_at))/3600) as avg_resolution_hours
                FROM ministry_incidents
                WHERE reported_at >= COALESCE($1, NOW() - INTERVAL '30 days')
                  AND reported_at <= COALESCE($2, NOW())
            """, date_from, date_to)
            
            # Personnel deployment
            personnel_deployment = await conn.fetch("""
                SELECT department, deployment_status, COUNT(*) as count
                FROM ministry_personnel 
                WHERE active = TRUE
                GROUP BY department, deployment_status
                ORDER BY department
            """)
            
            # Asset utilization
            asset_utilization = await conn.fetch("""
                SELECT asset_type, operational_status, COUNT(*) as count
                FROM ministry_assets
                GROUP BY asset_type, operational_status
                ORDER BY asset_type
            """)
            
            return {
                "operations_summary": dict(ops_summary) if ops_summary else {},
                "incidents_summary": dict(incidents_summary) if incidents_summary else {},
                "personnel_deployment": [dict(row) for row in personnel_deployment],
                "asset_utilization": [dict(row) for row in asset_utilization],
                "report_generated_at": datetime.now(timezone.utc).isoformat(),
                "period": {
                    "from": date_from.isoformat() if date_from else (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "to": date_to.isoformat() if date_to else datetime.now(timezone.utc).isoformat()
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to generate reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate reports: {str(e)}")

# =============================================================================
# MAIN APPLICATION
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=False,
        log_level="info",
        access_log=True
    )