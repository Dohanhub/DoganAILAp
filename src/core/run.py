#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Application Entry Point
Optimized entry point for FastAPI application with uvicorn
"""

import uvicorn
import os
from main import app  # Import the FastAPI app from main.py

# Expose the app instance for uvicorn
# This allows running: uvicorn run:app --reload --host 0.0.0.0 --port 8000
__all__ = ["app"]

def main():
    """Main entry point for the application"""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting DoganAI Compliance Kit on {host}:{port}")
    print(f"Reload mode: {reload}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        "run:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
