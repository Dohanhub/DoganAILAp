#!/usr/bin/env python3
"""
DoganAI Compliance Kit - 60-Second Auto-Update Startup Script
Integrates with existing system for seamless operation
"""

import asyncio
import sys
import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
import signal
import subprocess
import threading

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_update_validation_60s import AutoUpdateEngine

class AutoUpdateIntegrator:
    """Integrates 60-second auto-update with existing DoganAI system"""
    
    def __init__(self):
        self.auto_update_engine = None
        self.integration_status = {
            "status": "initializing",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "cycles_completed": 0,
            "last_cycle_time": None,
            "errors": []
        }
        self.running = False
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging for integration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - AUTO_UPDATE_INTEGRATION - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('auto_update_integration.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_integration(self):
        """Start integrated auto-update system"""
        self.logger.info("🚀 DoganAI Compliance Kit - Auto-Update Integration Starting")
        self.logger.info("=" * 70)
        self.logger.info("📊 Regulatory Sources: NCA, SAMA, MOH, CITC, CMA")
        self.logger.info("🔧 Vendor Sources: IBM Watson, Microsoft Azure, AWS Comprehend")
        self.logger.info("🏛️ Government Sources: MOI, SDAIA")
        self.logger.info("⏰ Update Frequency: Every 60 seconds")
        self.logger.info("🔄 Non-blocking operations enabled")
        self.logger.info("=" * 70)
        
        self.running = True
        self.integration_status["status"] = "running"
        
        try:
            # Initialize auto-update engine
            self.auto_update_engine = AutoUpdateEngine()
            
            # Check existing system compatibility
            await self._check_system_compatibility()
            
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitor_integration())
            
            # Start auto-update engine
            engine_task = asyncio.create_task(self.auto_update_engine.start())
            
            # Wait for tasks
            await asyncio.gather(monitor_task, engine_task, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"❌ Integration failed: {e}")
            self.integration_status["errors"].append(str(e))
            self.integration_status["status"] = "failed"
        finally:
            await self._cleanup()
    
    async def _check_system_compatibility(self):
        """Check compatibility with existing DoganAI system"""
        self.logger.info("🔍 Checking system compatibility...")
        
        # Check if existing databases are accessible
        db_files = [
            "doganai_compliance.db",
            "doganai_compliance_production_demo.db", 
            "doganai_compliance_demo.db"
        ]
        
        accessible_dbs = []
        for db_file in db_files:
            if os.path.exists(db_file):
                accessible_dbs.append(db_file)
                self.logger.info(f"✅ Found database: {db_file}")
        
        if not accessible_dbs:
            self.logger.warning("⚠️ No existing databases found - will create new ones")
        
        # Check if existing services are running
        existing_services = await self._check_existing_services()
        
        if existing_services:
            self.logger.info(f"🔗 Detected {len(existing_services)} existing services")
            for service in existing_services:
                self.logger.info(f"   - {service}")
        
        # Check environment variables for API keys
        api_keys = {
            "NCA_API_KEY": os.getenv("NCA_API_KEY"),
            "SAMA_API_KEY": os.getenv("SAMA_API_KEY"), 
            "MOH_API_KEY": os.getenv("MOH_API_KEY"),
            "CITC_API_KEY": os.getenv("CITC_API_KEY"),
            "CMA_API_KEY": os.getenv("CMA_API_KEY"),
            "IBM_WATSON_API_KEY": os.getenv("IBM_WATSON_API_KEY"),
            "AZURE_API_KEY": os.getenv("AZURE_API_KEY"),
            "AWS_ACCESS_KEY": os.getenv("AWS_ACCESS_KEY")
        }
        
        configured_keys = sum(1 for key in api_keys.values() if key)
        self.logger.info(f"🔑 API Keys configured: {configured_keys}/{len(api_keys)}")
        
        if configured_keys == 0:
            self.logger.warning("⚠️ No API keys configured - using fallback data sources")
        
        self.logger.info("✅ System compatibility check completed")
    
    async def _check_existing_services(self):
        """Check for existing DoganAI services"""
        existing_services = []
        
        # Check for common DoganAI processes
        service_patterns = [
            "app.py",
            "main.py", 
            "continuous_database_upload_system.py",
            "hourly_data_maintenance.py"
        ]
        
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        for pattern in service_patterns:
                            if pattern in cmdline_str and 'DoganAI' in cmdline_str:
                                existing_services.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            self.logger.warning("⚠️ psutil not available - cannot check existing services")
        
        return existing_services
    
    async def _monitor_integration(self):
        """Monitor integration status and performance"""
        self.logger.info("📊 Starting integration monitoring...")
        
        cycle_count = 0
        last_report_time = time.time()
        
        while self.running:
            try:
                # Update cycle count
                cycle_count += 1
                self.integration_status["cycles_completed"] = cycle_count
                self.integration_status["last_cycle_time"] = datetime.now(timezone.utc).isoformat()
                
                # Get engine status
                if self.auto_update_engine:
                    engine_status = self.auto_update_engine.get_status()
                    
                    # Report status every 5 minutes
                    if time.time() - last_report_time >= 300:  # 5 minutes
                        self._report_integration_status(engine_status)
                        last_report_time = time.time()
                
                # Wait for next monitoring cycle (every 30 seconds)
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"📊 Monitoring error: {e}")
                self.integration_status["errors"].append(str(e))
                await asyncio.sleep(60)
    
    def _report_integration_status(self, engine_status):
        """Report comprehensive integration status"""
        self.logger.info("📊 === INTEGRATION STATUS REPORT ===")
        self.logger.info(f"🕐 Uptime: {engine_status.get('uptime_hours', 0):.1f} hours")
        self.logger.info(f"🔄 Cycles Completed: {self.integration_status['cycles_completed']}")
        self.logger.info(f"📊 Total Sources: {engine_status.get('total_sources', 0)}")
        
        # Update statistics
        update_stats = engine_status.get('update_stats', {})
        total_updates = update_stats.get('total_updates', 0)
        successful_updates = update_stats.get('successful_updates', 0)
        
        if total_updates > 0:
            success_rate = (successful_updates / total_updates) * 100
            self.logger.info(f"✅ Success Rate: {success_rate:.1f}%")
            self.logger.info(f"📈 Total Updates: {total_updates}")
        
        # Validation status
        validation_summary = engine_status.get('validation_summary', {})
        health_status = validation_summary.get('health_status', 'unknown')
        self.logger.info(f"🏥 Health Status: {health_status.upper()}")
        
        # Error reporting
        if self.integration_status['errors']:
            self.logger.warning(f"⚠️ Total Errors: {len(self.integration_status['errors'])}")
        
        self.logger.info("=" * 40)
    
    async def _cleanup(self):
        """Cleanup resources"""
        self.logger.info("🧹 Cleaning up integration resources...")
        self.running = False
        
        if self.auto_update_engine:
            await self.auto_update_engine.stop()
        
        # Save final integration status
        self._save_integration_status()
        
        self.logger.info("✅ Integration cleanup completed")
    
    def _save_integration_status(self):
        """Save integration status to file"""
        try:
            self.integration_status["end_time"] = datetime.now(timezone.utc).isoformat()
            self.integration_status["status"] = "stopped"
            
            with open("auto_update_integration_status.json", "w") as f:
                json.dump(self.integration_status, f, indent=2)
            
            self.logger.info("💾 Integration status saved")
            
        except Exception as e:
            self.logger.error(f"💾 Failed to save integration status: {e}")

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                 DoganAI Compliance Kit                                  ║
║           60-Second Auto-Update & Validation System                     ║
║                                                                          ║
║  🏛️ Regulatory Sources: NCA, SAMA, MOH, CITC, CMA                      ║
║  🔧 Vendor Sources: IBM Watson, Microsoft Azure, AWS                    ║
║  🏛️ Government Sources: MOI, SDAIA                                      ║
║  ⏰ Update Frequency: Every 60 seconds                                  ║
║  🔄 Non-blocking operations                                              ║
║  🛡️ Real-time validation                                                 ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def main():
    """Main entry point"""
    print_banner()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start integrator
    integrator = AutoUpdateIntegrator()
    
    try:
        await integrator.start_integration()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        logging.error(f"System error: {e}")

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
