"""
Regulatory Integration API
Real-time integration with trusted government sources and automated updates
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
from pydantic import BaseModel
import redis.asyncio as redis
from .regulatory_data_monitor import RegulatoryDataMonitor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Regulatory Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
monitor = RegulatoryDataMonitor()
redis_client = None

# Pydantic models
class RegulatorUpdate(BaseModel):
    regulator_id: str
    name: str
    type: str
    last_check: datetime
    status: str
    changes_count: int

class RegulationUpdate(BaseModel):
    id: str
    regulator_id: str
    title: str
    type: str
    effective_date: datetime
    status: str
    sectors: List[str]
    source_url: str

class AuditFirmUpdate(BaseModel):
    id: str
    name: str
    socpa_license: str
    staff_count: int
    offices: List[str]
    specializations: List[str]
    last_updated: datetime

class MonitoringStatus(BaseModel):
    total_regulators: int
    total_regulations: int
    total_audit_firms: int
    last_update: datetime
    active_monitors: int
    failed_checks: int

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize connections and start monitoring"""
    global redis_client
    
    # Initialize Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Start regulatory monitoring in background
    asyncio.create_task(monitor.start_monitoring())
    
    logger.info("Regulatory Integration API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections"""
    await monitor.close()
    if redis_client:
        await redis_client.close()
    logger.info("Regulatory Integration API shutdown")

# API Endpoints

@app.get("/api/v1/regulators", response_model=List[RegulatorUpdate])
async def get_all_regulators():
    """Get all monitored regulators with their status"""
    try:
        status = monitor.get_monitoring_status()
        regulators = []
        
        for source_key, source_data in status["sources"].items():
            regulator = RegulatorUpdate(
                regulator_id=source_key,
                name=monitor.trusted_sources[source_key]["name"],
                type="government_regulator",
                last_check=datetime.fromisoformat(source_data["last_check"]),
                status=source_data["status"],
                changes_count=source_data["recent_changes"]
            )
            regulators.append(regulator)
        
        return regulators
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regulators: {str(e)}")

@app.get("/api/v1/regulators/{regulator_id}/updates", response_model=List[RegulationUpdate])
async def get_regulator_updates(regulator_id: str, limit: int = 50):
    """Get latest updates from specific regulator"""
    try:
        updates = monitor.get_latest_updates(regulator_id, limit)
        
        regulations = []
        for update in updates:
            regulation = RegulationUpdate(
                id=update["id"],
                regulator_id=update["regulator_id"],
                title=update["title"],
                type=update["type"],
                effective_date=datetime.fromisoformat(update["effective_date"]),
                status=update["status"],
                sectors=json.loads(update["sectors"]) if update["sectors"] else [],
                source_url=update["source_url"]
            )
            regulations.append(regulation)
        
        return regulations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching updates: {str(e)}")

@app.get("/api/v1/regulations/latest", response_model=List[RegulationUpdate])
async def get_latest_regulations(limit: int = 100):
    """Get latest regulations from all sources"""
    try:
        updates = monitor.get_latest_updates(limit=limit)
        
        regulations = []
        for update in updates:
            regulation = RegulationUpdate(
                id=update["id"],
                regulator_id=update["regulator_id"],
                title=update["title"],
                type=update["type"],
                effective_date=datetime.fromisoformat(update["effective_date"]),
                status=update["status"],
                sectors=json.loads(update["sectors"]) if update["sectors"] else [],
                source_url=update["source_url"]
            )
            regulations.append(regulation)
        
        return regulations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regulations: {str(e)}")

@app.get("/api/v1/monitoring/status", response_model=MonitoringStatus)
async def get_monitoring_status():
    """Get overall monitoring system status"""
    try:
        status = monitor.get_monitoring_status()
        
        # Count failed checks in last 24 hours
        failed_checks = sum(
            1 for source_data in status["sources"].values()
            if source_data["status"] == "error"
        )
        
        monitoring_status = MonitoringStatus(
            total_regulators=status["totals"]["regulators"],
            total_regulations=status["totals"]["regulations"],
            total_audit_firms=status["totals"]["audit_firms"],
            last_update=datetime.fromisoformat(status["last_updated"]),
            active_monitors=len(status["sources"]),
            failed_checks=failed_checks
        )
        
        return monitoring_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching status: {str(e)}")

@app.post("/api/v1/monitoring/force-update")
async def force_update_all(background_tasks: BackgroundTasks):
    """Force update all regulatory sources"""
    try:
        background_tasks.add_task(monitor.force_update_all)
        return {"message": "Force update initiated", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating update: {str(e)}")

@app.post("/api/v1/monitoring/force-update/{regulator_id}")
async def force_update_regulator(regulator_id: str, background_tasks: BackgroundTasks):
    """Force update specific regulator"""
    try:
        if regulator_id not in monitor.trusted_sources:
            raise HTTPException(status_code=404, detail="Regulator not found")
        
        background_tasks.add_task(monitor._monitor_source, regulator_id)
        return {
            "message": f"Force update initiated for {regulator_id}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating regulator: {str(e)}")

@app.get("/api/v1/audit-firms", response_model=List[AuditFirmUpdate])
async def get_audit_firms():
    """Get all registered audit firms"""
    try:
        # This would query the audit firms from the database
        # For now, return empty list as placeholder
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching audit firms: {str(e)}")

@app.get("/api/v1/regulations/search")
async def search_regulations(
    query: str,
    regulator_id: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = 50
):
    """Search regulations by query, regulator, or sector"""
    try:
        # Implement search functionality
        # This would search through the regulations database
        return {"message": "Search functionality to be implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching regulations: {str(e)}")

@app.get("/api/v1/compliance/deadlines")
async def get_compliance_deadlines(days_ahead: int = 30):
    """Get upcoming compliance deadlines"""
    try:
        # Query regulations with compliance deadlines in the next N days
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        # This would query the database for regulations with deadlines
        return {"message": "Deadline tracking to be implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching deadlines: {str(e)}")

@app.get("/api/v1/integration/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        status = monitor.get_monitoring_status()
        
        # Check Redis connection
        redis_status = "connected" if redis_client else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "redis": redis_status,
            "monitors_active": len(status["sources"]),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/regulatory-updates")
async def websocket_regulatory_updates(websocket):
    """WebSocket endpoint for real-time regulatory updates"""
    await websocket.accept()
    
    try:
        while True:
            # Check for new updates every 30 seconds
            await asyncio.sleep(30)
            
            # Get latest updates
            updates = monitor.get_latest_updates(limit=10)
            
            if updates:
                await websocket.send_json({
                    "type": "regulatory_updates",
                    "data": updates,
                    "timestamp": datetime.now().isoformat()
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Integration endpoints for compliance engine
@app.post("/api/v1/integration/sync-compliance-rules")
async def sync_compliance_rules(background_tasks: BackgroundTasks):
    """Sync latest regulatory updates with compliance engine"""
    try:
        # This would integrate with the existing compliance engine
        # to update rules based on new regulations
        background_tasks.add_task(_sync_with_compliance_engine)
        
        return {
            "message": "Compliance rules sync initiated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing rules: {str(e)}")

async def _sync_with_compliance_engine():
    """Background task to sync with compliance engine"""
    try:
        # Get latest regulatory updates
        updates = monitor.get_latest_updates(limit=100)
        
        # Process each update and update compliance rules
        for update in updates:
            # This would call the compliance_validator.py
            # and live_compliance_engine.py to update rules
            logger.info(f"Processing regulatory update: {update['title']}")
        
        logger.info("Compliance rules sync completed")
    except Exception as e:
        logger.error(f"Compliance sync error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
