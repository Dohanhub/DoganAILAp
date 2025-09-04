#!/usr/bin/env python3
"""
Portable Server Manager for DoganAI Compliance Kit
Manages the embedded Python/Node.js servers for the portable version.
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

class PortableServerManager:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.config = self._load_config()
        self.processes = {}
        self.running = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        config_path = self.app_dir / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration if config.json not found."""
        return {
            "runtime": {
                "python": {"path": "runtime/python"},
                "node": {"path": "runtime/node"}
            },
            "components": {
                "backend": {"port": 8000},
                "frontend": {"port": 3000}
            }
        }
    
    def setup_environment(self):
        """Setup environment variables and paths."""
        print("🔧 Setting up environment...")
        
        # Set paths
        python_dir = self.app_dir / self.config["runtime"]["python"]["path"]
        node_dir = self.app_dir / self.config["runtime"]["node"]["path"]
        
        # Update PATH
        current_path = os.environ.get("PATH", "")
        new_path = f"{python_dir};{node_dir};{current_path}"
        os.environ["PATH"] = new_path
        
        # Set application environment
        os.environ["DATABASE_URL"] = f"sqlite:///{self.app_dir}/data/compliance.db"
        os.environ["SECRET_KEY"] = "portable-doganai-secret-key-2024"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"
        os.environ["ENVIRONMENT"] = "portable"
        os.environ["DEBUG"] = "false"
        
        print("  ✅ Environment configured")
    
    def initialize_database(self):
        """Initialize SQLite database if needed."""
        print("🗄️ Initializing database...")
        
        db_path = self.app_dir / "data" / "compliance.db"
        db_path.parent.mkdir(exist_ok=True)
        
        if not db_path.exists():
            # Create empty database
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            
            # Basic schema for portable version
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sector TEXT,
                    country TEXT DEFAULT 'SA',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS compliance_frameworks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    regulator TEXT NOT NULL,
                    version TEXT,
                    country TEXT DEFAULT 'SA',
                    is_active BOOLEAN DEFAULT TRUE
                );
                
                -- Insert default admin user (password: admin123)
                INSERT OR IGNORE INTO users (email, username, password_hash, is_admin) 
                VALUES ('admin@doganai.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/Qe2', TRUE);
                
                -- Insert Saudi regulatory frameworks
                INSERT OR IGNORE INTO compliance_frameworks (name, regulator, version) VALUES
                ('CITC Cybersecurity Framework', 'CITC', '2.0'),
                ('CMA Market Conduct Regulations', 'CMA', '2023'),
                ('MHRSD Labor Law Compliance', 'MHRSD', '2024'),
                ('MOI Data Protection Standards', 'MOI', '1.0'),
                ('SAMA Banking Regulations', 'SAMA', '2023');
            ''')
            
            conn.close()
            print("  ✅ Database initialized with default data")
        else:
            print("  ✅ Database already exists")
    
    def start_backend(self):
        """Start the FastAPI backend server."""
        print("🐍 Starting backend server...")
        
        python_exe = self.app_dir / self.config["runtime"]["python"]["path"] / "python.exe"
        backend_dir = self.app_dir / "backend"
        
        if not python_exe.exists():
            # Fallback to system Python
            python_exe = "python"
        
        cmd = [
            str(python_exe), "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(self.config["components"]["backend"]["port"]),
            "--reload", "false"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.processes['backend'] = process
            print(f"  ✅ Backend started on port {self.config['components']['backend']['port']}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server."""
        print("🌐 Starting frontend server...")
        
        frontend_dir = self.app_dir / "frontend"
        if not frontend_dir.exists():
            print("  ⚠️ Frontend not found, serving static files via backend")
            return True
        
        # Simple static file server using Python
        python_exe = self.app_dir / self.config["runtime"]["python"]["path"] / "python.exe"
        if not python_exe.exists():
            python_exe = "python"
        
        cmd = [
            str(python_exe), "-m", "http.server",
            str(self.config["components"]["frontend"]["port"]),
            "--directory", str(frontend_dir)
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.processes['frontend'] = process
            print(f"  ✅ Frontend started on port {self.config['components']['frontend']['port']}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
            return False
    
    def wait_for_services(self, timeout: int = 30):
        """Wait for services to be ready."""
        print("⏳ Waiting for services to start...")
        
        import urllib.request
        import urllib.error
        
        backend_url = f"http://localhost:{self.config['components']['backend']['port']}/health"
        frontend_url = f"http://localhost:{self.config['components']['frontend']['port']}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check backend
                urllib.request.urlopen(backend_url, timeout=1)
                backend_ready = True
            except:
                backend_ready = False
            
            try:
                # Check frontend
                urllib.request.urlopen(frontend_url, timeout=1)
                frontend_ready = True
            except:
                frontend_ready = False
            
            if backend_ready and frontend_ready:
                print("  ✅ All services ready")
                return True
            
            time.sleep(1)
        
        print("  ⚠️ Services may not be fully ready")
        return False
    
    def open_browser(self):
        """Open the application in the default browser."""
        print("🌐 Opening browser...")
        
        url = f"http://localhost:{self.config['components']['frontend']['port']}"
        try:
            webbrowser.open(url)
            print(f"  ✅ Browser opened: {url}")
        except Exception as e:
            print(f"  ⚠️ Could not open browser: {e}")
            print(f"  📱 Please open manually: {url}")
    
    def stop_services(self):
        """Stop all running services."""
        print("🛑 Stopping services...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  ⚠️ {name} force killed")
            except Exception as e:
                print(f"  ❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        self.running = False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n🛑 Shutdown signal received...")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Main run method."""
        print("🚀 DoganAI Compliance Kit - Portable Edition")
        print("=" * 50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            self.setup_environment()
            self.initialize_database()
            
            # Start services
            backend_started = self.start_backend()
            frontend_started = self.start_frontend()
            
            if not (backend_started or frontend_started):
                print("❌ Failed to start any services")
                return False
            
            self.running = True
            
            # Wait for services and open browser
            if self.wait_for_services():
                self.open_browser()
            
            print("\n✅ DoganAI Compliance Kit is running!")
            print(f"📊 Dashboard: http://localhost:{self.config['components']['frontend']['port']}")
            print(f"🔧 API Docs:  http://localhost:{self.config['components']['backend']['port']}/docs")
            print("\nPress Ctrl+C to stop the application...")
            
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️ {name} process stopped unexpectedly")
                        del self.processes[name]
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.stop_services()
        
        return True

if __name__ == "__main__":
    manager = PortableServerManager()
    manager.run()
