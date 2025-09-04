from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, List, Optional
import os
import json
import requests
from datetime import datetime, timedelta
import uuid
from dashboard_data import dashboard_service
from template_engine import template_engine
from config_manager import config_manager

app = FastAPI(title="DoganAI Compliance Kit - Enterprise Platform", description="KSA Regulatory Compliance Platform with AI/ML Integration")

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page with language support."""
    # Get language from query parameter, default to English
    language = request.query_params.get("lang", "en")
    
    # Generate HTML dynamically from configuration
    html_content = template_engine.generate_dashboard_html(language)
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "UI Service", "version": "1.0.0"}

@app.get("/config")
def config():
    """Return current config."""
    return {"version": "1.0.0", "ui": "configuration-driven", "status": "active"}

@app.get("/dashboard")
def dashboard():
    """Return dashboard data."""
    return {"summary": "Configuration-driven dashboard is active"}

@app.post("/api/compliance-test")
async def run_compliance_test(request: Request):
    """Run compliance test via API."""
    try:
        data = await request.json()
        # Here you would integrate with the compliance engine
        return {
            "status": "success",
            "test_id": str(uuid.uuid4()),
            "compliance_score": 87,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ai-analysis")
async def run_ai_analysis(request: Request):
    """Run AI analysis via API."""
    try:
        data = await request.json()
        # Here you would integrate with the AI/ML service
        return {
            "status": "success",
            "analysis_id": str(uuid.uuid4()),
            "insights": ["AI insight 1", "AI insight 2"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dashboard Data Endpoints
@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview data."""
    return await dashboard_service.get_dashboard_overview()

@app.get("/api/dashboard/activity")
async def get_recent_activity(limit: int = 10):
    """Get recent activity data."""
    return await dashboard_service.get_recent_activity(limit)

@app.get("/api/dashboard/compliance")
async def get_compliance_summary():
    """Get compliance summary data."""
    return await dashboard_service.get_compliance_summary()

@app.get("/api/dashboard/vendors")
async def get_vendor_status():
    """Get vendor status data."""
    return await dashboard_service.get_vendor_status()

@app.get("/api/dashboard/health")
async def get_system_health():
    """Get system health data."""
    return await dashboard_service.get_system_health()

@app.get("/api/dashboard/all")
async def get_all_dashboard_data():
    """Get all dashboard data."""
    return dashboard_service.get_all_dashboard_data()

# Configuration endpoints
@app.get("/api/config/dashboard")
async def get_dashboard_config():
    """Get dashboard configuration."""
    return config_manager.get_config("dashboard_config.json")

@app.get("/api/config/languages")
async def get_supported_languages():
    """Get supported languages."""
    return {
        "languages": config_manager.get_supported_languages(),
        "default": config_manager.get_config("dashboard_config.json", "default_language"),
        "rtl_languages": config_manager.get_config("dashboard_config.json", "rtl_languages")
    }

@app.post("/api/config/reload")
async def reload_configuration():
    """Reload all configuration files."""
    config_manager.reload_all()
    return {"status": "success", "message": "Configuration reloaded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)

