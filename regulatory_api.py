
from fastapi import FastAPI
import sqlite3
import json
from datetime import datetime

# Create regulatory API extension
regulatory_app = FastAPI(title="Regulatory Monitor Extension")

@regulatory_app.get("/api/v1/regulators")
async def get_regulators():
    """Get all regulators"""
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regulators")
        columns = [desc[0] for desc in cursor.description]
        regulators = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return {"regulators": regulators, "count": len(regulators)}
    except Exception as e:
        return {"error": str(e)}

@regulatory_app.get("/api/v1/monitoring/status")
async def get_monitoring_status():
    """Get monitoring status"""
    try:
        conn = sqlite3.connect('regulatory_monitor.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM regulators")
        reg_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "active",
            "total_regulators": reg_count,
            "last_update": datetime.now().isoformat(),
            "monitoring_active": True
        }
    except Exception as e:
        return {"error": str(e)}

@regulatory_app.get("/regulatory/health")
async def regulatory_health():
    """Regulatory system health check"""
    return {
        "status": "healthy",
        "service": "Regulatory Monitor",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(regulatory_app, host="0.0.0.0", port=8002)
