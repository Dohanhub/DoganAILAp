"""
DoganAI Compliance Kit - Unified Application Entry Point
Fast-tracked, production-ready compliance management platform

This unified application combines:
- FastAPI backend for REST API services  
- Advanced React frontend for interactive dashboard
- Real PostgreSQL database integration
- Comprehensive security and monitoring
- Saudi regulatory framework compliance
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional
from threading import Thread
import uvicorn

# Add src to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedApplication:
    """Unified application manager for FastAPI + React Frontend"""
    
    def __init__(self):
        self.api_port = int(os.getenv("API_PORT", 8000))
        self.ui_port = int(os.getenv("UI_PORT", 3001))
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.host = os.getenv("HOST", "0.0.0.0")
        self.api_process: Optional[subprocess.Popen] = None
        self.ui_process: Optional[subprocess.Popen] = None
        
    def create_api_app(self):
        """Create and configure FastAPI application"""
        try:
            from src.core.app import create_app
            app = create_app()
            logger.info("FastAPI application created successfully")
            return app
        except ImportError as e:
            logger.error(f"Failed to import FastAPI app: {e}")
            return self._create_fallback_api()
    
    def _create_fallback_api(self):
        """Create basic FastAPI application as fallback"""
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from datetime import datetime
        
        app = FastAPI(
            title="DoganAI Compliance Kit API",
            description="Saudi Arabia Regulatory Compliance Platform",
            version="1.0.0",
            docs_url="/docs" if self.environment != "production" else None
        )
        
        # CORS configuration for React frontend
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[f"http://localhost:{self.ui_port}", f"http://127.0.0.1:{self.ui_port}"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "DoganAI Compliance Kit",
                "version": "1.0.0",
                "environment": self.environment,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.get("/")
        async def root():
            return {
                "message": "DoganAI Compliance Kit API",
                "description": "Saudi Arabia Regulatory Compliance Platform",
                "version": "1.0.0",
                "docs": f"http://localhost:{self.api_port}/docs" if self.environment != "production" else "Disabled in production",
                "frontend": f"http://localhost:{self.ui_port}",
                "health": "/health"
            }
        
        return app
    
    def start_api_server(self):
        """Start FastAPI server"""
        def run_api():
            try:
                app = self.create_api_app()
                uvicorn.run(
                    app,
                    host=self.host,
                    port=self.api_port,
                    log_level="info",
                    access_log=True
                )
            except Exception as e:
                logger.error(f"Failed to start API server: {e}")
        
        api_thread = Thread(target=run_api, daemon=True)
        api_thread.start()
        logger.info(f"FastAPI server starting on {self.host}:{self.api_port}")
        return api_thread
    
    def start_frontend_server(self):
        """Start React frontend development server"""
        frontend_dir = Path(__file__).parent / "frontend"
        
        if not frontend_dir.exists():
            logger.error("Frontend directory not found")
            return None
            
        try:
            # Check if npm is available
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            
            # Install dependencies if node_modules doesn't exist
            node_modules = frontend_dir / "node_modules"
            if not node_modules.exists():
                logger.info("Installing frontend dependencies...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            # Start development server
            logger.info(f"Starting React frontend on port {self.ui_port}")
            self.ui_process = subprocess.Popen(
                ["npm", "run", "start"],
                cwd=frontend_dir,
                env={**os.environ, "PORT": str(self.ui_port)}
            )
            
            return self.ui_process
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start frontend server: {e}")
            return None
        except FileNotFoundError:
            logger.error("npm not found. Please install Node.js and npm")
            return None
    
    def check_frontend_available(self) -> bool:
        """Check if frontend directory and package.json exist"""
        frontend_dir = Path(__file__).parent / "frontend"
        package_json = frontend_dir / "package.json"
        return frontend_dir.exists() and package_json.exists()
    
    def run(self):
        """Run the complete application"""
        logger.info("Starting DoganAI Compliance Kit in unified mode")
        
        # Start API server
        api_thread = self.start_api_server()
        
        # Start frontend if available
        if self.check_frontend_available():
            ui_process = self.start_frontend_server()
            if ui_process:
                logger.info(f"Application started successfully!")
                logger.info(f"API: http://localhost:{self.api_port}")
                logger.info(f"Frontend: http://localhost:{self.ui_port}")
                logger.info(f"API Docs: http://localhost:{self.api_port}/docs")
                
                try:
                    # Wait for frontend process
                    ui_process.wait()
                except KeyboardInterrupt:
                    logger.info("Shutting down application...")
                    ui_process.terminate()
            else:
                logger.warning("Frontend failed to start, API only mode")
                self._wait_for_api()
        else:
            logger.warning("Frontend not available, running API only")
            self._wait_for_api()
    
    def _wait_for_api(self):
        """Wait for API server (when no frontend)"""
        logger.info(f"API server running on http://localhost:{self.api_port}")
        logger.info(f"API documentation available at http://localhost:{self.api_port}/docs")
        try:
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Application shutdown requested")

def main():
    """Main application entry point"""
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="DoganAI Compliance Kit")
    parser.add_argument("--api-only", action="store_true", help="Run API server only")
    parser.add_argument("--frontend-only", action="store_true", help="Run frontend only")
    parser.add_argument("--api-port", type=int, default=8000, help="API server port")
    parser.add_argument("--ui-port", type=int, default=3001, help="Frontend server port")
    args = parser.parse_args()
    
    # Set environment variables from args
    if args.api_port:
        os.environ["API_PORT"] = str(args.api_port)
    if args.ui_port:
        os.environ["UI_PORT"] = str(args.ui_port)
    
    app = UnifiedApplication()
    
    if args.api_only:
        logger.info("Running in API-only mode")
        app.start_api_server()
        app._wait_for_api()
    elif args.frontend_only:
        logger.info("Running in frontend-only mode")
        if app.check_frontend_available():
            ui_process = app.start_frontend_server()
            if ui_process:
                try:
                    ui_process.wait()
                except KeyboardInterrupt:
                    ui_process.terminate()
        else:
            logger.error("Frontend not available")
    else:
        # Run both
        app.run()

if __name__ == "__main__":
    main()