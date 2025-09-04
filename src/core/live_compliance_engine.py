#!/usr/bin/env python3
"""
Live Compliance Engine
Real-time policy validation with continuous monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
import aiohttp
import websockets
from pathlib import Path
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import schedule
import threading
import time

from .compliance_validator import RealComplianceValidator, ComplianceAssessment
from .ground_truth_system import GroundTruthSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EngineStatus(Enum):
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class LiveValidationEvent:
    """Real-time validation event"""
    event_id: str
    control_id: str
    framework: str
    organization_id: str
    validation_result: Dict[str, Any]
    timestamp: datetime
    severity: str
    action_required: bool

@dataclass
class EngineMetrics:
    """Live engine performance metrics"""
    validations_per_minute: float
    active_monitors: int
    policy_violations: int
    system_health: float
    uptime_seconds: int
    last_update: datetime

class LiveComplianceEngine:
    """Real-time compliance validation engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.status = EngineStatus.STARTING
        self.validator = RealComplianceValidator()
        self.ground_truth = GroundTruthSystem()
        self.active_monitors = {}
        self.validation_queue = asyncio.Queue()
        self.event_subscribers = []
        self.metrics = EngineMetrics(
            validations_per_minute=0.0,
            active_monitors=0,
            policy_violations=0,
            system_health=100.0,
            uptime_seconds=0,
            last_update=datetime.now(timezone.utc)
        )
        self.start_time = datetime.now(timezone.utc)
        self.redis_client = None
        
    async def initialize(self):
        """Initialize the live compliance engine"""
        try:
            logger.info("Initializing Live Compliance Engine...")
            
            # Initialize Redis connection
            redis_url = self.config.get('redis_url', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            # Load monitoring configurations
            await self._load_monitoring_configs()
            
            # Start background tasks
            asyncio.create_task(self._validation_processor())
            asyncio.create_task(self._metrics_updater())
            asyncio.create_task(self._policy_monitor())
            
            self.status = EngineStatus.RUNNING
            logger.info("Live Compliance Engine started successfully")
            
        except Exception as e:
            self.status = EngineStatus.ERROR
            logger.error(f"Failed to initialize engine: {e}")
            raise
    
    async def _load_monitoring_configs(self):
        """Load monitoring configurations for continuous validation"""
        config_path = Path("config/monitoring")
        if not config_path.exists():
            config_path.mkdir(parents=True, exist_ok=True)
            
        # Create default monitoring config if not exists
        default_config = {
            "continuous_monitoring": {
                "enabled": True,
                "interval_minutes": 5,
                "frameworks": ["NCA", "SAMA", "CITC", "CMA"]
            },
            "real_time_validation": {
                "enabled": True,
                "triggers": ["config_change", "policy_update", "security_event"]
            },
            "alert_thresholds": {
                "critical_violations": 1,
                "compliance_drop_percentage": 10,
                "response_time_seconds": 30
            }
        }
        
        config_file = config_path / "engine_config.yaml"
        if not config_file.exists():
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                
        # Load configuration
        with open(config_file, 'r') as f:
            self.monitoring_config = yaml.safe_load(f)
            
        logger.info("Monitoring configuration loaded")
    
    async def start_continuous_monitoring(self, organization_id: str, frameworks: List[str] = None):
        """Start continuous compliance monitoring"""
        frameworks = frameworks or ["NCA", "SAMA", "CITC", "CMA"]
        
        for framework in frameworks:
            monitor_id = f"{organization_id}_{framework}"
            
            if monitor_id not in self.active_monitors:
                monitor = {
                    "id": monitor_id,
                    "organization_id": organization_id,
                    "framework": framework,
                    "status": "active",
                    "last_validation": None,
                    "next_validation": datetime.now(timezone.utc),
                    "interval_minutes": self.monitoring_config.get("continuous_monitoring", {}).get("interval_minutes", 5)
                }
                
                self.active_monitors[monitor_id] = monitor
                logger.info(f"Started continuous monitoring: {monitor_id}")
        
        self.metrics.active_monitors = len(self.active_monitors)
    
    async def _policy_monitor(self):
        """Background task for continuous policy monitoring"""
        while self.status == EngineStatus.RUNNING:
            try:
                current_time = datetime.now(timezone.utc)
                
                for monitor_id, monitor in self.active_monitors.items():
                    if monitor["status"] == "active" and current_time >= monitor["next_validation"]:
                        # Queue validation
                        await self.validation_queue.put({
                            "type": "continuous_validation",
                            "monitor_id": monitor_id,
                            "organization_id": monitor["organization_id"],
                            "framework": monitor["framework"]
                        })
                        
                        # Update next validation time
                        monitor["next_validation"] = current_time + timedelta(minutes=monitor["interval_minutes"])
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Policy monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _validation_processor(self):
        """Background task to process validation queue"""
        validation_count = 0
        start_time = time.time()
        
        while self.status == EngineStatus.RUNNING:
            try:
                # Get validation task from queue
                task = await asyncio.wait_for(self.validation_queue.get(), timeout=1.0)
                
                if task["type"] == "continuous_validation":
                    await self._process_continuous_validation(task)
                elif task["type"] == "real_time_validation":
                    await self._process_real_time_validation(task)
                
                validation_count += 1
                
                # Update validation rate
                elapsed_time = time.time() - start_time
                if elapsed_time >= 60:  # Update every minute
                    self.metrics.validations_per_minute = validation_count / (elapsed_time / 60)
                    validation_count = 0
                    start_time = time.time()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Validation processor error: {e}")
                await asyncio.sleep(5)
    
    async def _process_continuous_validation(self, task: Dict[str, Any]):
        """Process continuous validation task"""
        try:
            organization_id = task["organization_id"]
            framework = task["framework"]
            monitor_id = task["monitor_id"]
            
            # Get system configuration (this would come from actual system inspection)
            system_config = await self._get_system_configuration(organization_id)
            
            # Perform compliance assessment
            assessment = await self.validator.assess_compliance(framework, organization_id, system_config)
            
            # Update monitor
            if monitor_id in self.active_monitors:
                self.active_monitors[monitor_id]["last_validation"] = datetime.now(timezone.utc)
            
            # Check for violations
            violations = [r for r in assessment.validation_results if r.status.value == "non_compliant"]
            if violations:
                self.metrics.policy_violations += len(violations)
                
                # Generate alerts for critical violations
                for violation in violations:
                    if violation.severity.value == "critical":
                        await self._generate_alert(violation, organization_id, framework)
            
            # Store results
            await self._store_validation_results(assessment)
            
            # Publish real-time event
            event = LiveValidationEvent(
                event_id=f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                control_id="continuous_monitoring",
                framework=framework,
                organization_id=organization_id,
                validation_result=asdict(assessment),
                timestamp=datetime.now(timezone.utc),
                severity="info" if not violations else "warning",
                action_required=len(violations) > 0
            )
            
            await self._publish_event(event)
            
            logger.info(f"Continuous validation completed: {framework} - {assessment.compliance_percentage:.1f}%")
            
        except Exception as e:
            logger.error(f"Continuous validation failed: {e}")
    
    async def _process_real_time_validation(self, task: Dict[str, Any]):
        """Process real-time validation triggered by events"""
        try:
            trigger = task.get("trigger")
            organization_id = task["organization_id"]
            framework = task.get("framework", "NCA")
            
            logger.info(f"Real-time validation triggered by: {trigger}")
            
            # Perform immediate validation
            system_config = await self._get_system_configuration(organization_id)
            assessment = await self.validator.assess_compliance(framework, organization_id, system_config)
            
            # Check for immediate action required
            critical_violations = [r for r in assessment.validation_results 
                                 if r.status.value == "non_compliant" and r.severity.value == "critical"]
            
            if critical_violations:
                for violation in critical_violations:
                    await self._generate_immediate_alert(violation, organization_id, framework, trigger)
            
            # Publish real-time event
            event = LiveValidationEvent(
                event_id=f"rt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                control_id=trigger,
                framework=framework,
                organization_id=organization_id,
                validation_result=asdict(assessment),
                timestamp=datetime.now(timezone.utc),
                severity="critical" if critical_violations else "info",
                action_required=len(critical_violations) > 0
            )
            
            await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Real-time validation failed: {e}")
    
    async def _get_system_configuration(self, organization_id: str) -> Dict[str, Any]:
        """Get current system configuration for validation"""
        # This would integrate with actual system inspection
        # For now, return a sample configuration
        return {
            "network": {
                "vpc_enabled": True,
                "subnets": ["public", "private", "database"],
                "security_groups": ["web-sg", "app-sg", "db-sg"],
                "firewall_rules": ["allow-https", "deny-all"]
            },
            "tls": {
                "version": "1.3",
                "certificates": True,
                "mutual_tls": True
            },
            "https_only": True,
            "storage": {
                "database_region": "saudi-arabia-central",
                "file_storage_region": "saudi-arabia-central",
                "backup_region": "saudi-arabia-central"
            }
        }
    
    async def _generate_alert(self, violation: Any, organization_id: str, framework: str):
        """Generate compliance violation alert"""
        alert = {
            "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "compliance_violation",
            "severity": violation.severity.value,
            "organization_id": organization_id,
            "framework": framework,
            "control_id": violation.control_id,
            "title": violation.title,
            "violations": violation.violations,
            "recommendations": violation.recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store alert
        if self.redis_client:
            await self.redis_client.lpush("compliance_alerts", json.dumps(alert))
            await self.redis_client.expire("compliance_alerts", 86400)  # 24 hours
        
        logger.warning(f"Compliance alert generated: {alert['alert_id']}")
    
    async def _generate_immediate_alert(self, violation: Any, organization_id: str, 
                                      framework: str, trigger: str):
        """Generate immediate alert for critical violations"""
        alert = {
            "alert_id": f"immediate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "immediate_action_required",
            "severity": "critical",
            "trigger": trigger,
            "organization_id": organization_id,
            "framework": framework,
            "control_id": violation.control_id,
            "title": violation.title,
            "violations": violation.violations,
            "recommendations": violation.recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store immediate alert
        if self.redis_client:
            await self.redis_client.lpush("immediate_alerts", json.dumps(alert))
            await self.redis_client.expire("immediate_alerts", 3600)  # 1 hour
        
        logger.critical(f"IMMEDIATE ACTION REQUIRED: {alert['alert_id']}")
    
    async def _store_validation_results(self, assessment: Any):
        """Store validation results for historical tracking"""
        result_data = {
            "assessment_id": assessment.assessment_id,
            "framework": assessment.framework,
            "organization_id": assessment.organization_id,
            "compliance_percentage": assessment.compliance_percentage,
            "overall_score": assessment.overall_score,
            "risk_level": assessment.risk_level,
            "timestamp": assessment.assessment_timestamp.isoformat()
        }
        
        if self.redis_client:
            # Store in Redis for quick access
            await self.redis_client.lpush("validation_history", json.dumps(result_data))
            await self.redis_client.ltrim("validation_history", 0, 999)  # Keep last 1000 results
    
    async def _publish_event(self, event: LiveValidationEvent):
        """Publish real-time event to subscribers"""
        event_data = asdict(event)
        event_data["timestamp"] = event.timestamp.isoformat()
        
        # Publish to Redis pub/sub
        if self.redis_client:
            await self.redis_client.publish("compliance_events", json.dumps(event_data))
        
        # Notify WebSocket subscribers
        for subscriber in self.event_subscribers:
            try:
                await subscriber(event_data)
            except Exception as e:
                logger.error(f"Failed to notify subscriber: {e}")
    
    async def _metrics_updater(self):
        """Background task to update engine metrics"""
        while self.status == EngineStatus.RUNNING:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Update uptime
                self.metrics.uptime_seconds = int((current_time - self.start_time).total_seconds())
                
                # Update system health based on various factors
                health_score = 100.0
                
                # Reduce health if too many violations
                if self.metrics.policy_violations > 10:
                    health_score -= min(self.metrics.policy_violations * 2, 50)
                
                # Reduce health if monitors are failing
                failed_monitors = sum(1 for m in self.active_monitors.values() 
                                    if m.get("status") == "failed")
                if failed_monitors > 0:
                    health_score -= failed_monitors * 10
                
                self.metrics.system_health = max(health_score, 0.0)
                self.metrics.last_update = current_time
                
                # Store metrics in Redis
                if self.redis_client:
                    await self.redis_client.set("engine_metrics", json.dumps(asdict(self.metrics), default=str))
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(60)
    
    async def trigger_real_time_validation(self, organization_id: str, trigger: str, 
                                         framework: str = "NCA"):
        """Trigger immediate real-time validation"""
        await self.validation_queue.put({
            "type": "real_time_validation",
            "organization_id": organization_id,
            "framework": framework,
            "trigger": trigger
        })
        
        logger.info(f"Real-time validation triggered: {trigger}")
    
    async def get_live_metrics(self) -> EngineMetrics:
        """Get current engine metrics"""
        return self.metrics
    
    async def get_active_monitors(self) -> Dict[str, Any]:
        """Get status of active monitors"""
        return self.active_monitors
    
    async def subscribe_to_events(self, callback: Callable):
        """Subscribe to real-time compliance events"""
        self.event_subscribers.append(callback)
    
    async def stop(self):
        """Stop the live compliance engine"""
        self.status = EngineStatus.STOPPED
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Live Compliance Engine stopped")

# Example usage
async def main():
    """Example usage of live compliance engine"""
    engine = LiveComplianceEngine({
        "redis_url": "redis://localhost:6379"
    })
    
    try:
        await engine.initialize()
        
        # Start monitoring for organization
        await engine.start_continuous_monitoring("org_001", ["NCA", "SAMA"])
        
        # Subscribe to events
        async def event_handler(event_data):
            print(f"Event received: {event_data['event_id']} - {event_data['severity']}")
        
        await engine.subscribe_to_events(event_handler)
        
        # Trigger a real-time validation
        await engine.trigger_real_time_validation("org_001", "config_change")
        
        # Run for a while to see continuous monitoring
        print("Live Compliance Engine running... (Press Ctrl+C to stop)")
        
        while True:
            metrics = await engine.get_live_metrics()
            monitors = await engine.get_active_monitors()
            
            print(f"\n=== LIVE ENGINE STATUS ===")
            print(f"Status: {engine.status.value}")
            print(f"Uptime: {metrics.uptime_seconds} seconds")
            print(f"System Health: {metrics.system_health:.1f}%")
            print(f"Active Monitors: {metrics.active_monitors}")
            print(f"Validations/min: {metrics.validations_per_minute:.1f}")
            print(f"Policy Violations: {metrics.policy_violations}")
            
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print("\nStopping Live Compliance Engine...")
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())
