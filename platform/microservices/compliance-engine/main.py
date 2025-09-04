"""
Compliance Engine Microservice - Production Ready
API-first, modular compliance engine for KSA regulations with full evaluation capabilities
"""

import os
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Removed for development
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ValidationError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import redis
import jwt
from cryptography.fernet import Fernet

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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

logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment variables
APP_NAME = os.getenv("APP_NAME", "Compliance Engine Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "compliance_engine")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "7bBxUxlAEQjNKLYw_lzR3dzBxjtEZVwu-QWd9zyeImI")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "false").lower() == "true"

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# =============================================================================
# DATABASE SETUP
# =============================================================================

def get_database_engine():
    """Get database engine with connection pooling"""
    database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=DEBUG
    )
    
    return engine

def get_db_session():
    """Get database session"""
    engine = get_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# REDIS SETUP
# =============================================================================

def get_redis_client():
    """Get Redis client for caching"""
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.warning("Redis connection failed, using in-memory cache", error=str(e))
        return None

# =============================================================================
# SECURITY
# =============================================================================

class APIKeyAuth:
    """API Key authentication"""
    def __init__(self):
        self.scheme = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request) -> Optional[str]:
        # Check API key header first
        api_key = request.headers.get(API_KEY_HEADER)
        if api_key:
            if await self.validate_api_key(api_key):
                return api_key
        
        # Fall back to Bearer token
        credentials: HTTPAuthorizationCredentials = await self.scheme(request)
        if credentials:
            if await self.validate_jwt_token(credentials.credentials):
                return credentials.credentials
        
        return None
    
    async def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
        return api_key in valid_keys
    
    async def validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

# Authentication dependency
auth_handler = APIKeyAuth()

async def get_current_user(api_key: Optional[str] = Depends(auth_handler)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

REQUEST_COUNT = Counter(
    "compliance_engine_requests_total",
    "Total compliance engine requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "compliance_engine_request_duration_seconds",
    "Compliance engine request latency in seconds",
    ["method", "endpoint"]
)

EVALUATION_COUNT = Counter(
    "compliance_evaluations_total",
    "Total compliance evaluations",
    ["benchmark_id", "status", "policy_type"]
)

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class EvidenceItem(BaseModel):
    """Evidence item for compliance evaluation"""
    id: str = Field(..., description="Unique identifier for the evidence")
    type: str = Field(..., description="Type of evidence (document, metric, test_result, etc.)")
    value: Any = Field(..., description="Evidence value")
    source: str = Field(..., description="Source of the evidence")
    timestamp: Optional[datetime] = Field(None, description="When the evidence was collected")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_001",
                "type": "document",
                "value": "Security Policy Document v2.1",
                "source": "internal_documentation",
                "timestamp": "2024-01-15T10:30:00Z",
                "metadata": {
                    "file_size": "2.5MB",
                    "format": "PDF",
                    "reviewed_by": "security_team"
                }
            }
        }

class EvaluationRequest(BaseModel):
    """Compliance evaluation request"""
    benchmark_id: str = Field(..., description="ID of the benchmark to evaluate against")
    evidence: List[EvidenceItem] = Field(..., description="List of evidence items")
    vendor_id: Optional[str] = Field(None, description="Vendor ID for vendor-specific evaluation")
    policy_version: Optional[str] = Field(None, description="Policy version to use")
    evaluation_mode: str = Field("standard", description="Evaluation mode: standard, strict, lenient")
    include_recommendations: bool = Field(True, description="Include improvement recommendations")
    
    class Config:
        schema_extra = {
            "example": {
                "benchmark_id": "NCA_CYBERSECURITY_2024",
                "evidence": [
                    {
                        "id": "doc_001",
                        "type": "document",
                        "value": "Security Policy Document",
                        "source": "internal_documentation"
                    }
                ],
                "vendor_id": "vendor_123",
                "policy_version": "2024.1",
                "evaluation_mode": "standard",
                "include_recommendations": True
            }
        }

class EvaluationResult(BaseModel):
    """Compliance evaluation result"""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    benchmark_id: str = Field(..., description="Benchmark that was evaluated")
    status: str = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., description="Compliance score (0-100)")
    required_items: List[str] = Field(..., description="List of required compliance items")
    provided_items: List[str] = Field(..., description="List of provided compliance items")
    missing_items: List[str] = Field(..., description="List of missing compliance items")
    partial_items: List[str] = Field(..., description="List of partially compliant items")
    evidence_mapping: Dict[str, List[str]] = Field(..., description="Mapping of evidence to requirements")
    recommendations: List[str] = Field(..., description="List of improvement recommendations")
    evaluation_time: float = Field(..., description="Time taken for evaluation in seconds")
    timestamp: datetime = Field(..., description="When the evaluation was performed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional evaluation metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "evaluation_id": "eval_001",
                "benchmark_id": "NCA_CYBERSECURITY_2024",
                "status": "partially_compliant",
                "compliance_score": 75.5,
                "required_items": ["policy", "training", "monitoring"],
                "provided_items": ["policy", "training"],
                "missing_items": ["monitoring"],
                "partial_items": [],
                "evidence_mapping": {
                    "policy": ["doc_001"],
                    "training": ["doc_002"]
                },
                "recommendations": ["Implement continuous monitoring system"],
                "evaluation_time": 2.5,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class BenchmarkInfo(BaseModel):
    """Benchmark information"""
    id: str = Field(..., description="Benchmark identifier")
    name: str = Field(..., description="Benchmark name")
    description: str = Field(..., description="Benchmark description")
    policy_type: str = Field(..., description="Type of policy (NCA, SAMA, MoH, etc.)")
    version: str = Field(..., description="Benchmark version")
    effective_date: Optional[datetime] = Field(None, description="When the benchmark becomes effective")
    expiry_date: Optional[datetime] = Field(None, description="When the benchmark expires")
    requirements: List[str] = Field(..., description="List of compliance requirements")
    risk_level: str = Field(..., description="Risk level (low, medium, high, critical)")
    is_active: bool = Field(..., description="Whether the benchmark is currently active")

class PolicyInfo(BaseModel):
    """Policy information"""
    id: str = Field(..., description="Policy identifier")
    name: str = Field(..., description="Policy name")
    authority: str = Field(..., description="Regulatory authority")
    version: str = Field(..., description="Policy version")
    description: str = Field(..., description="Policy description")
    requirements: List[str] = Field(..., description="List of policy requirements")
    categories: List[str] = Field(..., description="Policy categories")
    risk_level: str = Field(..., description="Risk level")
    effective_date: Optional[datetime] = Field(None, description="Effective date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")

# =============================================================================
# COMPLIANCE ENGINE CORE
# =============================================================================

class ComplianceEngine:
    """Core compliance evaluation engine"""
    
    def __init__(self):
        self.benchmarks: Dict[str, Dict[str, Any]] = {}
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.redis_client = get_redis_client()
        self._load_benchmarks()
    
    def _load_benchmarks(self):
        """Load benchmarks from configuration files"""
        try:
            # Load from benchmarks directory
            benchmarks_dir = Path(__file__).parent.parent.parent / "benchmarks"
            if benchmarks_dir.exists():
                for benchmark_file in benchmarks_dir.glob("*.json"):
                    try:
                        with open(benchmark_file, 'r', encoding='utf-8') as f:
                            benchmark_data = json.load(f)
                            self.benchmarks[benchmark_data['id']] = benchmark_data
                    except Exception as e:
                        logger.warning(f"Failed to load benchmark {benchmark_file}", error=str(e))
            
            # Load from policies directory
            policies_dir = Path(__file__).parent.parent.parent / "policies"
            if policies_dir.exists():
                for policy_file in policies_dir.glob("*.yaml"):
                    try:
                        with open(policy_file, 'r', encoding='utf-8') as f:
                            policy_data = yaml.safe_load(f)
                            if 'id' in policy_data:
                                self.policies[policy_data['id']] = policy_data
                    except Exception as e:
                        logger.warning(f"Failed to load policy {policy_file}", error=str(e))
            
            logger.info(f"Loaded {len(self.benchmarks)} benchmarks and {len(self.policies)} policies")
            
        except Exception as e:
            logger.error("Failed to load benchmarks and policies", error=str(e))
    
    def evaluate_compliance(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate compliance against a benchmark"""
        start_time = time.time()
        
        try:
            # Get benchmark
            benchmark = self.benchmarks.get(request.benchmark_id)
            if not benchmark:
                raise ValueError(f"Benchmark {request.benchmark_id} not found")
            
            # Get policy
            policy = self.policies.get(benchmark.get('policy_id', ''))
            
            # Evaluate evidence against requirements
            evaluation_result = self._evaluate_evidence(
                benchmark, policy, request.evidence, request.evaluation_mode
            )
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(evaluation_result)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(evaluation_result) if request.include_recommendations else []
            
            # Create result
            result = EvaluationResult(
                evaluation_id=str(uuid.uuid4()),
                benchmark_id=request.benchmark_id,
                status=evaluation_result['status'],
                compliance_score=compliance_score,
                required_items=evaluation_result['required_items'],
                provided_items=evaluation_result['provided_items'],
                missing_items=evaluation_result['missing_items'],
                partial_items=evaluation_result['partial_items'],
                evidence_mapping=evaluation_result['evidence_mapping'],
                recommendations=recommendations,
                evaluation_time=time.time() - start_time,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "vendor_id": request.vendor_id,
                    "policy_version": request.policy_version,
                    "evaluation_mode": request.evaluation_mode
                }
            )
            
            # Cache result
            if self.redis_client:
                cache_key = f"evaluation:{result.evaluation_id}"
                self.redis_client.setex(
                    cache_key, 
                    3600,  # 1 hour TTL
                    json.dumps(result.dict(), default=str)
                )
            
            # Record metrics
            EVALUATION_COUNT.labels(
                benchmark_id=request.benchmark_id,
                status=result.status,
                policy_type=benchmark.get('policy_type', 'unknown')
            ).inc()
            
            return result
            
        except Exception as e:
            logger.error("Compliance evaluation failed", error=str(e), exc_info=True)
            raise
    
    def _evaluate_evidence(self, benchmark: Dict[str, Any], policy: Dict[str, Any], 
                          evidence: List[EvidenceItem], mode: str) -> Dict[str, Any]:
        """Evaluate evidence against benchmark requirements"""
        requirements = benchmark.get('requirements', [])
        evidence_map = {item.id: item for item in evidence}
        
        required_items = []
        provided_items = []
        missing_items = []
        partial_items = []
        evidence_mapping = {}
        
        for req in requirements:
            req_id = req.get('id', '')
            req_type = req.get('type', '')
            req_evidence = req.get('evidence', [])
            
            required_items.append(req_id)
            
            # Check if evidence exists for this requirement
            matching_evidence = []
            for evidence_id in req_evidence:
                if evidence_id in evidence_map:
                    matching_evidence.append(evidence_id)
            
            if matching_evidence:
                provided_items.append(req_id)
                evidence_mapping[req_id] = matching_evidence
                
                # Check if fully compliant based on mode
                if mode == "strict" and len(matching_evidence) < len(req_evidence):
                    partial_items.append(req_id)
                elif mode == "lenient" or len(matching_evidence) >= len(req_evidence):
                    pass  # Fully compliant
                else:
                    partial_items.append(req_id)
            else:
                missing_items.append(req_id)
                evidence_mapping[req_id] = []
        
        # Determine overall status
        if not missing_items and not partial_items:
            status = "fully_compliant"
        elif not missing_items:
            status = "partially_compliant"
        else:
            status = "non_compliant"
        
        return {
            "status": status,
            "required_items": required_items,
            "provided_items": provided_items,
            "missing_items": missing_items,
            "partial_items": partial_items,
            "evidence_mapping": evidence_mapping
        }
    
    def _calculate_compliance_score(self, evaluation_result: Dict[str, Any]) -> float:
        """Calculate compliance score (0-100)"""
        total_requirements = len(evaluation_result['required_items'])
        if total_requirements == 0:
            return 100.0
        
        provided_count = len(evaluation_result['provided_items'])
        partial_count = len(evaluation_result['partial_items'])
        
        # Full compliance = 100%, partial = 50%, missing = 0%
        score = (provided_count * 100 + partial_count * 50) / total_requirements
        
        return round(score, 2)
    
    def _generate_recommendations(self, evaluation_result: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Recommendations for missing items
        for missing_item in evaluation_result['missing_items']:
            recommendations.append(f"Implement {missing_item} to achieve full compliance")
        
        # Recommendations for partial items
        for partial_item in evaluation_result['partial_items']:
            recommendations.append(f"Complete implementation of {partial_item} for full compliance")
        
        # General recommendations
        if evaluation_result['status'] == "non_compliant":
            recommendations.append("Conduct a comprehensive compliance review and gap analysis")
        elif evaluation_result['status'] == "partially_compliant":
            recommendations.append("Prioritize missing compliance items based on risk assessment")
        
        return recommendations
    
    def get_benchmark(self, benchmark_id: str) -> Optional[BenchmarkInfo]:
        """Get benchmark information"""
        benchmark = self.benchmarks.get(benchmark_id)
        if not benchmark:
            return None
        
        return BenchmarkInfo(
            id=benchmark['id'],
            name=benchmark.get('name', ''),
            description=benchmark.get('description', ''),
            policy_type=benchmark.get('policy_type', ''),
            version=benchmark.get('version', ''),
            effective_date=benchmark.get('effective_date'),
            expiry_date=benchmark.get('expiry_date'),
            requirements=benchmark.get('requirements', []),
            risk_level=benchmark.get('risk_level', 'medium'),
            is_active=benchmark.get('is_active', True)
        )
    
    def list_benchmarks(self) -> List[BenchmarkInfo]:
        """List all available benchmarks"""
        return [
            self.get_benchmark(bid) for bid in self.benchmarks.keys()
            if self.get_benchmark(bid) is not None
        ]
    
    def get_policy(self, policy_id: str) -> Optional[PolicyInfo]:
        """Get policy information"""
        policy = self.policies.get(policy_id)
        if not policy:
            return None
        
        return PolicyInfo(
            id=policy['id'],
            name=policy.get('name', ''),
            authority=policy.get('authority', ''),
            version=policy.get('version', ''),
            description=policy.get('description', ''),
            requirements=policy.get('requirements', []),
            categories=policy.get('categories', []),
            risk_level=policy.get('risk_level', 'medium'),
            effective_date=policy.get('effective_date'),
            expiry_date=policy.get('expiry_date')
        )
    
    def list_policies(self) -> List[PolicyInfo]:
        """List all available policies"""
        return [
            self.get_policy(pid) for pid in self.policies.keys()
            if self.get_policy(pid) is not None
        ]

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="DoganAI Compliance Engine",
    description="API-first, modular compliance engine for KSA regulations",
    version="1.0.0"
)

# Add middleware
# TrustedHostMiddleware removed for development - ENABLE FOR PRODUCTION
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["*"]  # Allow all hosts for development - CONFIGURE FOR PRODUCTION
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize compliance engine
compliance_engine = ComplianceEngine()

# =============================================================================
# MIDDLEWARE FOR METRICS
# =============================================================================

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks_loaded": len(compliance_engine.benchmarks),
        "policies_loaded": len(compliance_engine.policies)
    }

@app.get("/config")
async def config():
    """Return current configuration"""
    return {
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "regulations": list(set(b.get('policy_type', '') for b in compliance_engine.benchmarks.values())),
        "benchmarks_count": len(compliance_engine.benchmarks),
        "policies_count": len(compliance_engine.policies)
    }

@app.get("/benchmarks", response_model=List[BenchmarkInfo])
async def list_benchmarks():
    """List all available benchmarks"""
    return compliance_engine.list_benchmarks()

@app.get("/benchmarks/{benchmark_id}", response_model=BenchmarkInfo)
async def get_benchmark(benchmark_id: str):
    """Get specific benchmark information"""
    benchmark = compliance_engine.get_benchmark(benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark {benchmark_id} not found")
    return benchmark

@app.get("/policies", response_model=List[PolicyInfo])
async def list_policies():
    """List all available policies"""
    return compliance_engine.list_policies()

@app.get("/policies/{policy_id}", response_model=PolicyInfo)
async def get_policy(policy_id: str):
    """Get specific policy information"""
    policy = compliance_engine.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return policy

@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Evaluate compliance for a given benchmark and evidence"""
    try:
        # Run evaluation
        result = compliance_engine.evaluate_compliance(request)
        
        # Background task for result processing
        background_tasks.add_task(process_evaluation_result, result)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Evaluation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during evaluation")

@app.get("/evaluations/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation(evaluation_id: str):
    """Get evaluation result by ID"""
    # Try to get from cache first
    if compliance_engine.redis_client:
        cached_result = compliance_engine.redis_client.get(f"evaluation:{evaluation_id}")
        if cached_result:
            return json.loads(cached_result)
    
    raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# =============================================================================
# ENHANCED FEATURES ENDPOINTS
# =============================================================================

@app.post("/monitoring/start")
async def start_real_time_monitoring(
    vendor_id: str,
    compliance_rules: List[Dict],
    current_user: str = Depends(get_current_user)
):
    """Start real-time compliance monitoring for a vendor"""
    try:
        from enhanced_features import RealTimeComplianceMonitor
        monitor = RealTimeComplianceMonitor(redis_client)
        result = await monitor.start_monitoring(vendor_id, compliance_rules)
        return result
    except Exception as e:
        logger.error("Failed to start monitoring", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start monitoring")

@app.get("/monitoring/status/{vendor_id}")
async def get_monitoring_status(
    vendor_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get real-time monitoring status for a vendor"""
    try:
        from enhanced_features import RealTimeComplianceMonitor
        monitor = RealTimeComplianceMonitor(redis_client)
        result = await monitor.check_compliance_status(vendor_id)
        return result
    except Exception as e:
        logger.error("Failed to get monitoring status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get monitoring status")

@app.post("/analytics/predict-trends")
async def predict_compliance_trends(
    vendor_id: str,
    historical_data: List[Dict],
    current_user: str = Depends(get_current_user)
):
    """Predict compliance trends for the next 30 days"""
    try:
        from enhanced_features import PredictiveComplianceAnalytics
        analytics = PredictiveComplianceAnalytics()
        result = await analytics.predict_compliance_trends(vendor_id, historical_data)
        return result
    except Exception as e:
        logger.error("Failed to predict trends", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to predict trends")

@app.post("/analytics/forecast-risk")
async def forecast_risk_events(
    vendor_id: str,
    compliance_data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Forecast potential risk events"""
    try:
        from enhanced_features import PredictiveComplianceAnalytics
        analytics = PredictiveComplianceAnalytics()
        result = await analytics.forecast_risk_events(vendor_id, compliance_data)
        return result
    except Exception as e:
        logger.error("Failed to forecast risk", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to forecast risk")

@app.post("/analytics/detect-anomalies")
async def detect_compliance_anomalies(
    vendor_id: str,
    compliance_data: List[Dict],
    current_user: str = Depends(get_current_user)
):
    """Detect anomalies in compliance patterns"""
    try:
        from enhanced_features import PredictiveComplianceAnalytics
        analytics = PredictiveComplianceAnalytics()
        result = await analytics.detect_anomalies(vendor_id, compliance_data)
        return result
    except Exception as e:
        logger.error("Failed to detect anomalies", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")

@app.post("/workflows/start")
async def start_compliance_workflow(
    workflow_type: str,
    vendor_id: str,
    parameters: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Start an automated compliance workflow"""
    try:
        from enhanced_features import AutomatedComplianceWorkflow
        workflow = AutomatedComplianceWorkflow(redis_client)
        result = await workflow.start_workflow(workflow_type, vendor_id, parameters)
        return result
    except Exception as e:
        logger.error("Failed to start workflow", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start workflow")

@app.get("/workflows/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get workflow execution status"""
    try:
        from enhanced_features import AutomatedComplianceWorkflow
        workflow = AutomatedComplianceWorkflow(redis_client)
        result = await workflow.get_workflow_status(workflow_id)
        return result
    except Exception as e:
        logger.error("Failed to get workflow status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get workflow status")

@app.get("/workflows/list")
async def list_workflows(
    vendor_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List all workflows"""
    try:
        from enhanced_features import AutomatedComplianceWorkflow
        workflow = AutomatedComplianceWorkflow(redis_client)
        result = await workflow.list_workflows(vendor_id)
        return result
    except Exception as e:
        logger.error("Failed to list workflows", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list workflows")

# =============================================================================
# ENHANCED VENDOR INTEGRATION ENDPOINTS
# =============================================================================

@app.get("/vendors/compliance/{vendor_name}/{service}")
async def get_vendor_compliance(
    vendor_name: str,
    service: str,
    current_user: str = Depends(get_current_user)
):
    """Get compliance status for specific vendor service"""
    try:
        from enhanced_vendor_integrations import EnhancedVendorIntegrations
        vendor_integration = EnhancedVendorIntegrations()
        result = await vendor_integration.get_vendor_compliance_status(vendor_name, service)
        return result
    except Exception as e:
        logger.error("Failed to get vendor compliance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get vendor compliance")

@app.get("/regulatory/compliance/{regulatory_body}")
async def check_regulatory_compliance(
    regulatory_body: str,
    vendor_id: str,
    current_user: str = Depends(get_current_user)
):
    """Check compliance with specific regulatory body"""
    try:
        from enhanced_vendor_integrations import EnhancedRegulatoryIntegrations
        regulatory_integration = EnhancedRegulatoryIntegrations()
        result = await regulatory_integration.check_regulatory_compliance(vendor_id, regulatory_body)
        return result
    except Exception as e:
        logger.error("Failed to check regulatory compliance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to check regulatory compliance")

@app.post("/frameworks/map")
async def map_compliance_frameworks(
    vendor_frameworks: List[str],
    target_regulation: str,
    current_user: str = Depends(get_current_user)
):
    """Map vendor compliance frameworks to KSA regulatory requirements"""
    try:
        from enhanced_vendor_integrations import ComplianceFrameworkMapper
        mapper = ComplianceFrameworkMapper()
        result = mapper.map_compliance_frameworks(vendor_frameworks, target_regulation)
        return result
    except Exception as e:
        logger.error("Failed to map compliance frameworks", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to map compliance frameworks")
    )

# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def process_evaluation_result(result: EvaluationResult):
    """Process evaluation result in background"""
    try:
        # Store in database
        # Send notifications
        # Update analytics
        logger.info(f"Processed evaluation result {result.evaluation_id}")
    except Exception as e:
        logger.error(f"Failed to process evaluation result {result.evaluation_id}", error=str(e))

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(
        "Starting Compliance Engine Microservice",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        debug=DEBUG
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Compliance Engine Microservice")

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return {
        "detail": "Validation error",
        "errors": exc.errors()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return {
        "detail": "Internal server error"
    }

# Import Response for metrics endpoint
from fastapi.responses import Response
