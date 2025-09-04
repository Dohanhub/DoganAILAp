"""
FastAPI backend for DoganAI KSA Compliance Platform
"""
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.core.database import initialize_database, get_db_service
from src.core.settings import Settings
from src.api.health import get_health_checker
from src.utils.monitoring import metrics_collector
from src.core.compliance import ComplianceEngine
from src.models.schemas import AuditLog
from src.core.observability_init import initialize_observability, shutdown_observability, get_observability_status
from src.services.observability import observability, logger as obs_logger
from src.services.feature_flags import flag_manager, EvaluationContext, UserSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Dogan AI 'Shahin KSA' Platform...")
    
    # Initialize observability system first
    try:
        if initialize_observability(settings):
            obs_logger.info("Observability system initialized successfully")
        else:
            logger.warning("Observability system initialization failed, continuing without full observability")
    except Exception as e:
        logger.error(f"Observability initialization failed: {e}")
        # Continue without observability rather than failing completely
    
    # Initialize database
    try:
        initialize_database()
        logger.info("Database initialized successfully")
        obs_logger.info("Database initialization completed", component="database")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        obs_logger.error("Database initialization failed", error=str(e), component="database")
        raise
    
    # Start metrics collection
    try:
        metrics_collector.collect_system_metrics()
        logger.info("Metrics collection started")
        obs_logger.info("Metrics collection started", component="metrics")
    except Exception as e:
        logger.warning(f"Metrics collection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    obs_logger.info("Application shutdown initiated")
    
    # Shutdown observability system
    try:
        shutdown_observability()
        logger.info("Observability system shutdown completed")
    except Exception as e:
        logger.error(f"Error during observability shutdown: {e}")
    
    obs_logger.info("Application shutdown completed")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Dogan AI 'Shahin KSA' - Compliance & Operations Platform API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins or ["http://localhost:5000", "http://localhost:8501"],
    allow_credentials=settings.api.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class EvaluationRequest(BaseModel):
    mapping_name: str
    force_refresh: bool = False

class EvaluationResponse(BaseModel):
    status: str
    mapping_name: str
    policy_ref: str
    sector: str
    summary: Dict[str, Any]
    details: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    checks: Dict[str, Any]
    summary: Dict[str, Any]

# Initialize compliance engine
compliance_engine = ComplianceEngine()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dogan AI 'Shahin KSA' - Compliance Platform API",
        "version": settings.app_version,
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    try:
        health_checker = get_health_checker()
        result = health_checker.run_all_checks()
        return result
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": settings.get_current_time().isoformat()
            }
        )

@app.get("/mappings")
async def list_mappings():
    """List available compliance mappings"""
    try:
        mappings = await compliance_engine.get_available_mappings()
        return {
            "mappings": mappings,
            "count": len(mappings)
        }
    except Exception as e:
        logger.error(f"Failed to list mappings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_compliance(request: EvaluationRequest):
    """Evaluate compliance for a specific mapping"""
    try:
        logger.info(f"Evaluating compliance for mapping: {request.mapping_name}")
        
        result = await compliance_engine.evaluate_mapping(
            request.mapping_name,
            force_refresh=request.force_refresh
        )
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Mapping not found: {e}")
        raise HTTPException(status_code=404, detail=f"Mapping not found: {request.mapping_name}")
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate/{mapping_name}")
async def get_evaluation_result(mapping_name: str):
    """Get cached evaluation result"""
    try:
        result = await compliance_engine.get_cached_result(mapping_name)
        if not result:
            raise HTTPException(status_code=404, detail="No cached result found")
        return result
    except Exception as e:
        logger.error(f"Failed to get evaluation result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/policies")
async def list_policies():
    """List available policies"""
    try:
        policies = await compliance_engine.get_available_policies()
        return {
            "policies": policies,
            "count": len(policies)
        }
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors")
async def list_vendors():
    """List available vendors"""
    try:
        vendors = await compliance_engine.get_available_vendors()
        return {
            "vendors": vendors,
            "count": len(vendors)
        }
    except Exception as e:
        logger.error(f"Failed to list vendors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    try:
        # Collect current system metrics
        metrics_collector.collect_system_metrics()
        
        return {
            "message": "Metrics collected - use /health for detailed metrics",
            "timestamp": settings.get_current_time().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/observability/status")
async def get_observability_status_endpoint():
    """Get observability system status"""
    try:
        status = get_observability_status()
        obs_logger.info("Observability status requested", status=status)
        return {
            "status": "success",
            "observability": status,
            "timestamp": observability.get_metrics_summary().get("timestamp", "unknown")
        }
    except Exception as e:
        obs_logger.error("Failed to get observability status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/observability/metrics")
async def get_observability_metrics():
    """Get detailed observability metrics"""
    try:
        metrics_summary = observability.get_metrics_summary()
        obs_logger.info("Observability metrics requested")
        return {
            "status": "success",
            "metrics": metrics_summary,
            "prometheus_endpoint": f"http://localhost:{settings.observability.metrics_port}/metrics" if settings.observability.enable_metrics else None
        }
    except Exception as e:
        obs_logger.error("Failed to get observability metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feature-flags")
async def list_feature_flags(tags: Optional[str] = Query(None)):
    """List all feature flags with optional tag filtering"""
    try:
        tag_list = tags.split(",") if tags else None
        flags = flag_manager.list_flags(tags=tag_list)
        obs_logger.info("Feature flags listed", count=len(flags), tags=tag_list)
        return {
            "status": "success",
            "flags": flags,
            "count": len(flags)
        }
    except Exception as e:
        obs_logger.error("Failed to list feature flags", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feature-flags/status")
async def get_feature_flags_status():
    """Get feature flags system status"""
    try:
        status = flag_manager.get_flag_status()
        obs_logger.info("Feature flags status requested")
        return {
            "status": "success",
            "feature_flags": status
        }
    except Exception as e:
        obs_logger.error("Failed to get feature flags status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feature-flags/{flag_name}/evaluate")
async def evaluate_feature_flag(
    flag_name: str,
    user_id: Optional[str] = Query(None),
    user_segment: str = Query("production"),
    environment: str = Query(None)
):
    """Evaluate a specific feature flag for a user"""
    try:
        # Use environment from settings if not provided
        eval_environment = environment or settings.environment
        
        # Parse user segment
        try:
            segment = UserSegment(user_segment.lower())
        except ValueError:
            segment = UserSegment.PRODUCTION
        
        # Create evaluation context
        context = EvaluationContext(
            user_id=user_id,
            user_segment=segment,
            environment=eval_environment
        )
        
        # Evaluate flag
        result = flag_manager.evaluate(flag_name, context)
        
        obs_logger.info(
            "Feature flag evaluated",
            flag_name=flag_name,
            enabled=result.enabled,
            user_segment=user_segment,
            reason=result.reason
        )
        
        return {
            "status": "success",
            "flag_name": result.flag_name,
            "enabled": result.enabled,
            "reason": result.reason,
            "user_segment": result.user_segment.value,
            "rollout_percentage": result.rollout_percentage,
            "evaluation_time": result.evaluation_time.isoformat()
        }
        
    except Exception as e:
        obs_logger.error(
            "Failed to evaluate feature flag",
            flag_name=flag_name,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get audit logs"""
    try:
        db_service = get_db_service()
        
        with db_service.get_session() as session:
            # Query audit logs using ORM
            logs_query = session.query(AuditLog).order_by(AuditLog.timestamp.desc())
            total_count = logs_query.count()
            logs = logs_query.offset(offset).limit(limit).all()
            
        return {
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "mapping_name": log.mapping_name,
                    "policy_ref": log.policy_ref,
                    "status": log.status,
                    "result_hash": log.result_hash,
                    "user_id": log.user_id,
                    "session_id": log.session_id,
                    "evaluation_summary": {
                        "total_controls": log.evaluation_data.get("summary", {}).get("total_controls", 0),
                        "covered_controls": log.evaluation_data.get("summary", {}).get("covered_controls", 0),
                        "coverage_percentage": log.evaluation_data.get("summary", {}).get("coverage_percentage", 0)
                    }
                }
                for log in logs
            ],
            "count": len(logs),
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(logs)) < total_count
        }
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main entry point for the DoganAI Compliance Kit server"""
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )

if __name__ == "__main__":
    main()
