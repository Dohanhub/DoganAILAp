"""
DEMO/EXAMPLE ONLY – NOT FOR PRODUCTION
This example backend is not used by the main application.
Prefer app/main.py and the Helm chart for deployments.

Modern FastAPI Backend for Compliance Platform
Clean architecture with latest technologies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from datetime import datetime
import random

# Create FastAPI app
app = FastAPI(
    title="Dogan AI Compliance API",
    description="Modern Compliance Platform Backend",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models using dictionaries (no Pydantic dependencies)
def create_compliance_data():
    """Generate compliance data"""
    return {
        "frameworks": {
            "NCA": {"score": 92, "controls": 245, "status": "compliant"},
            "SAMA": {"score": 88, "controls": 180, "status": "compliant"},
            "PDPL": {"score": 85, "controls": 120, "status": "partial"},
            "ISO27001": {"score": 90, "controls": 114, "status": "compliant"},
            "NIST": {"score": 87, "controls": 108, "status": "compliant"}
        },
        "overall_score": 87,
        "risk_level": "low",
        "open_issues": 8,
        "last_updated": datetime.now().isoformat()
    }

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dogan AI Compliance Platform API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "cache": "operational"
        }
    }

@app.get("/api/compliance")
async def get_compliance_status():
    """Get current compliance status"""
    return create_compliance_data()

@app.get("/api/frameworks")
async def list_frameworks():
    """List available compliance frameworks"""
    frameworks = [
        {
            "id": "nca",
            "name": "NCA - National Cybersecurity Authority",
            "description": "Saudi Arabia's cybersecurity framework",
            "controls": 245,
            "categories": 5
        },
        {
            "id": "sama",
            "name": "SAMA - Saudi Arabian Monetary Authority",
            "description": "Financial services compliance framework",
            "controls": 180,
            "categories": 4
        },
        {
            "id": "pdpl",
            "name": "PDPL - Personal Data Protection Law",
            "description": "Saudi data protection regulations",
            "controls": 120,
            "categories": 6
        },
        {
            "id": "iso27001",
            "name": "ISO 27001",
            "description": "International security standard",
            "controls": 114,
            "categories": 14
        },
        {
            "id": "nist",
            "name": "NIST Cybersecurity Framework",
            "description": "US cybersecurity framework",
            "controls": 108,
            "categories": 5
        }
    ]
    return {"frameworks": frameworks, "count": len(frameworks)}

@app.get("/api/assessments")
async def get_assessments():
    """Get recent assessments"""
    assessments = []
    for i in range(5):
        assessments.append({
            "id": f"assess-{i+1}",
            "date": f"2024-12-{15-i*2:02d}",
            "framework": random.choice(["NCA", "SAMA", "PDPL"]),
            "score": random.randint(75, 95),
            "status": "completed",
            "findings": random.randint(3, 15)
        })
    return {"assessments": assessments, "total": len(assessments)}

@app.get("/api/controls/{framework_id}")
async def get_framework_controls(framework_id: str):
    """Get controls for a specific framework"""
    controls = []
    for i in range(10):
        controls.append({
            "id": f"{framework_id.upper()}-{i+1}",
            "name": f"Control {i+1}",
            "description": f"Security control for {framework_id}",
            "status": random.choice(["compliant", "partial", "non-compliant"]),
            "score": random.randint(60, 100),
            "priority": random.choice(["critical", "high", "medium", "low"])
        })
    return {"framework": framework_id, "controls": controls, "count": len(controls)}

@app.post("/api/assessment/run")
async def run_assessment(framework: str = "NCA"):
    """Run a new compliance assessment"""
    # Simulate assessment
    results = {
        "id": f"assess-{datetime.now().timestamp()}",
        "framework": framework,
        "start_time": datetime.now().isoformat(),
        "status": "in_progress",
        "message": "Assessment started successfully"
    }
    
    # Simulate completion after a moment
    results.update({
        "status": "completed",
        "end_time": datetime.now().isoformat(),
        "score": random.randint(75, 95),
        "findings": random.randint(3, 15),
        "recommendations": [
            "Improve access control policies",
            "Update incident response procedures",
            "Enhance data encryption methods"
        ]
    })
    
    return results

@app.get("/api/metrics")
async def get_metrics():
    """Get platform metrics"""
    return {
        "users": {"total": 150, "active": 89, "new_this_month": 12},
        "assessments": {"total": 1250, "this_month": 45, "average_score": 86},
        "controls": {"total": 867, "compliant": 750, "non_compliant": 117},
        "issues": {"open": 23, "resolved_this_month": 67, "average_resolution_days": 3.5}
    }

@app.get("/api/risks")
async def get_risks():
    """Get current risk analysis"""
    risks = {
        "critical": 2,
        "high": 6,
        "medium": 15,
        "low": 45,
        "top_risks": [
            {"name": "Unpatched vulnerabilities", "level": "critical", "affected_controls": 8},
            {"name": "Weak access controls", "level": "high", "affected_controls": 5},
            {"name": "Missing encryption", "level": "high", "affected_controls": 3}
        ]
    }
    return risks

@app.get("/api/reports/generate")
async def generate_report(report_type: str = "executive"):
    """Generate compliance report"""
    return {
        "report_id": f"report-{datetime.now().timestamp()}",
        "type": report_type,
        "generated_at": datetime.now().isoformat(),
        "format": "pdf",
        "status": "ready",
        "download_url": f"/api/reports/download/sample-{report_type}.pdf"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
