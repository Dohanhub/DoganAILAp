#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Governance Framework
Comprehensive governance system for ownership, SLA management, and change classification
"""

import json
import yaml
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading

import structlog
from observability.metrics import observability

# Configure logging
logger = structlog.get_logger("governance")

# =============================================================================
# GOVERNANCE MODELS
# =============================================================================

class SLATier(Enum):
    """SLA tier definitions with resolution timeframes"""
    CRITICAL = "critical"      # 72-hour resolution
    IMPORTANT = "important"    # 14-day resolution
    OPTIONAL = "optional"      # Resolve by sprint end

class ChangeType(Enum):
    """Change classification types"""
    CONFIGURATION = "configuration"  # Configuration-only changes
    SECRET_ROTATION = "secret_rotation"  # Secret rotations
    ENDPOINT_MIGRATION = "endpoint_migration"  # Endpoint migrations
    DOCUMENTATION = "documentation"  # Documentation updates
    FEATURE_CHANGE = "feature_change"  # Feature modifications
    INFRASTRUCTURE = "infrastructure"  # Infrastructure changes
    SECURITY_PATCH = "security_patch"  # Security updates

class ComponentStatus(Enum):
    """Component status tracking"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Owner:
    """Component owner information"""
    email: str
    name: str
    team: str
    role: str
    backup_email: Optional[str] = None
    slack_handle: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SLADefinition:
    """SLA definition with resolution timeframes"""
    tier: SLATier
    resolution_hours: int
    escalation_hours: int
    business_hours_only: bool = False
    auto_escalate: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['tier'] = self.tier.value
        return data

@dataclass
class Component:
    """Governed component definition"""
    id: str
    name: str
    description: str
    owner: Owner
    sla_tier: SLATier
    risk_level: RiskLevel
    status: ComponentStatus
    tags: List[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['owner'] = self.owner.to_dict()
        data['sla_tier'] = self.sla_tier.value
        data['risk_level'] = self.risk_level.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.last_reviewed:
            data['last_reviewed'] = self.last_reviewed.isoformat()
        if self.next_review:
            data['next_review'] = self.next_review.isoformat()
        return data

@dataclass
class ChangeRecord:
    """Change tracking record"""
    id: str
    component_id: str
    change_type: ChangeType
    title: str
    description: str
    owner: str
    risk_assessment: RiskLevel
    approval_required: bool
    approved_by: Optional[str]
    implemented_at: Optional[datetime]
    rollback_plan: Optional[str]
    verification_steps: List[str]
    created_at: datetime
    status: str  # planned, approved, implemented, verified, rolled_back
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['change_type'] = self.change_type.value
        data['risk_assessment'] = self.risk_assessment.value
        data['created_at'] = self.created_at.isoformat()
        if self.implemented_at:
            data['implemented_at'] = self.implemented_at.isoformat()
        return data

@dataclass
class MaintenanceSchedule:
    """Maintenance schedule definition"""
    component_id: str
    schedule_type: str  # quarterly, monthly, weekly
    next_maintenance: datetime
    last_maintenance: Optional[datetime]
    maintenance_tasks: List[str]
    owner: str
    estimated_duration: int  # minutes
    requires_downtime: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['next_maintenance'] = self.next_maintenance.isoformat()
        if self.last_maintenance:
            data['last_maintenance'] = self.last_maintenance.isoformat()
        return data

# =============================================================================
# GOVERNANCE MANAGER
# =============================================================================

class GovernanceManager:
    """Central governance management system"""
    
    def __init__(self, config_path: str = "governance"):
        self.config_path = Path(config_path)
        self.components: Dict[str, Component] = {}
        self.change_records: Dict[str, ChangeRecord] = {}
        self.maintenance_schedules: Dict[str, MaintenanceSchedule] = {}
        self.sla_definitions: Dict[SLATier, SLADefinition] = {}
        self.lock = threading.RLock()
        self.logger = structlog.get_logger("governance_manager")
        
        self._initialize_sla_definitions()
        self._load_governance_data()
        self._create_default_components()
    
    def _initialize_sla_definitions(self):
        """Initialize SLA tier definitions"""
        self.sla_definitions = {
            SLATier.CRITICAL: SLADefinition(
                tier=SLATier.CRITICAL,
                resolution_hours=72,
                escalation_hours=24,
                business_hours_only=False,
                auto_escalate=True
            ),
            SLATier.IMPORTANT: SLADefinition(
                tier=SLATier.IMPORTANT,
                resolution_hours=14 * 24,  # 14 days
                escalation_hours=7 * 24,   # 7 days
                business_hours_only=True,
                auto_escalate=True
            ),
            SLATier.OPTIONAL: SLADefinition(
                tier=SLATier.OPTIONAL,
                resolution_hours=21 * 24,  # 3 weeks (sprint end)
                escalation_hours=14 * 24,  # 2 weeks
                business_hours_only=True,
                auto_escalate=False
            )
        }
    
    def _load_governance_data(self):
        """Load governance data from configuration files"""
        try:
            # Load components
            components_file = self.config_path / "components.yaml"
            if components_file.exists():
                with open(components_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for comp_data in data.get('components', []):
                        component = self._parse_component(comp_data)
                        self.components[component.id] = component
            
            # Load change records
            changes_file = self.config_path / "changes.json"
            if changes_file.exists():
                with open(changes_file, 'r') as f:
                    data = json.load(f)
                    for change_data in data.get('changes', []):
                        change = self._parse_change_record(change_data)
                        self.change_records[change.id] = change
            
            # Load maintenance schedules
            maintenance_file = self.config_path / "maintenance.yaml"
            if maintenance_file.exists():
                with open(maintenance_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for maint_data in data.get('schedules', []):
                        schedule = self._parse_maintenance_schedule(maint_data)
                        self.maintenance_schedules[schedule.component_id] = schedule
            
            self.logger.info(
                "Governance data loaded",
                components=len(self.components),
                changes=len(self.change_records),
                maintenance_schedules=len(self.maintenance_schedules)
            )
        
        except Exception as e:
            self.logger.error(
                "Failed to load governance data",
                error=str(e),
                exc_info=True
            )
    
    def _parse_component(self, data: Dict[str, Any]) -> Component:
        """Parse component from configuration data"""
        owner_data = data['owner']
        owner = Owner(
            email=owner_data['email'],
            name=owner_data['name'],
            team=owner_data['team'],
            role=owner_data['role'],
            backup_email=owner_data.get('backup_email'),
            slack_handle=owner_data.get('slack_handle')
        )
        
        return Component(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            owner=owner,
            sla_tier=SLATier(data['sla_tier']),
            risk_level=RiskLevel(data['risk_level']),
            status=ComponentStatus(data['status']),
            tags=data.get('tags', []),
            dependencies=data.get('dependencies', []),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            last_reviewed=(
                datetime.fromisoformat(data['last_reviewed'])
                if data.get('last_reviewed') else None
            ),
            next_review=(
                datetime.fromisoformat(data['next_review'])
                if data.get('next_review') else None
            ),
            metadata=data.get('metadata')
        )
    
    def _parse_change_record(self, data: Dict[str, Any]) -> ChangeRecord:
        """Parse change record from configuration data"""
        return ChangeRecord(
            id=data['id'],
            component_id=data['component_id'],
            change_type=ChangeType(data['change_type']),
            title=data['title'],
            description=data['description'],
            owner=data['owner'],
            risk_assessment=RiskLevel(data['risk_assessment']),
            approval_required=data['approval_required'],
            approved_by=data.get('approved_by'),
            implemented_at=(
                datetime.fromisoformat(data['implemented_at'])
                if data.get('implemented_at') else None
            ),
            rollback_plan=data.get('rollback_plan'),
            verification_steps=data.get('verification_steps', []),
            created_at=datetime.fromisoformat(data['created_at']),
            status=data['status'],
            metadata=data.get('metadata')
        )
    
    def _parse_maintenance_schedule(self, data: Dict[str, Any]) -> MaintenanceSchedule:
        """Parse maintenance schedule from configuration data"""
        return MaintenanceSchedule(
            component_id=data['component_id'],
            schedule_type=data['schedule_type'],
            next_maintenance=datetime.fromisoformat(data['next_maintenance']),
            last_maintenance=(
                datetime.fromisoformat(data['last_maintenance'])
                if data.get('last_maintenance') else None
            ),
            maintenance_tasks=data['maintenance_tasks'],
            owner=data['owner'],
            estimated_duration=data['estimated_duration'],
            requires_downtime=data.get('requires_downtime', False)
        )
    
    def _create_default_components(self):
        """Create default governance components"""
        if not self.components:
            default_components = [
                {
                    "id": "compliance_report_generator",
                    "name": "Compliance Report Generator",
                    "description": "Feature slice for generating compliance reports",
                    "owner": {
                        "email": "platform@dogan",
                        "name": "Platform Team",
                        "team": "Platform Engineering",
                        "role": "Feature Owner",
                        "slack_handle": "@platform-team"
                    },
                    "sla_tier": "critical",
                    "risk_level": "high",
                    "status": "active",
                    "tags": ["compliance", "reporting", "feature-slice"],
                    "dependencies": ["database", "redis", "api"]
                },
                {
                    "id": "database_configuration",
                    "name": "Database Configuration",
                    "description": "Primary database connection and configuration",
                    "owner": {
                        "email": "platform@dogan",
                        "name": "Platform Team",
                        "team": "Platform Engineering",
                        "role": "Infrastructure Owner",
                        "slack_handle": "@platform-team"
                    },
                    "sla_tier": "critical",
                    "risk_level": "critical",
                    "status": "active",
                    "tags": ["database", "infrastructure", "critical"],
                    "dependencies": []
                },
                {
                    "id": "feature_flags",
                    "name": "Feature Flag System",
                    "description": "Configuration-driven feature flag management",
                    "owner": {
                        "email": "platform@dogan",
                        "name": "Platform Team",
                        "team": "Platform Engineering",
                        "role": "System Owner",
                        "slack_handle": "@platform-team"
                    },
                    "sla_tier": "important",
                    "risk_level": "medium",
                    "status": "active",
                    "tags": ["feature-flags", "configuration", "rollout"],
                    "dependencies": ["api"]
                },
                {
                    "id": "observability_system",
                    "name": "Observability & Monitoring",
                    "description": "Metrics, logging, and monitoring infrastructure",
                    "owner": {
                        "email": "platform@dogan",
                        "name": "Platform Team",
                        "team": "Platform Engineering",
                        "role": "System Owner",
                        "slack_handle": "@platform-team"
                    },
                    "sla_tier": "important",
                    "risk_level": "medium",
                    "status": "active",
                    "tags": ["monitoring", "metrics", "logging"],
                    "dependencies": ["prometheus", "grafana"]
                }
            ]
            
            for comp_data in default_components:
                comp_data['created_at'] = datetime.now(timezone.utc).isoformat()
                comp_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                component = self._parse_component(comp_data)
                self.components[component.id] = component
            
            self._save_components()
    
    def _save_components(self):
        """Save components to configuration file"""
        try:
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            components_data = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "components": [comp.to_dict() for comp in self.components.values()]
            }
            
            with open(self.config_path / "components.yaml", 'w') as f:
                yaml.dump(components_data, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(
                "Components saved",
                count=len(self.components),
                path=str(self.config_path / "components.yaml")
            )
        
        except Exception as e:
            self.logger.error(
                "Failed to save components",
                error=str(e),
                exc_info=True
            )
    
    def register_component(self, component_data: Dict[str, Any]) -> bool:
        """Register a new component"""
        with self.lock:
            try:
                component_id = component_data['id']
                
                if component_id in self.components:
                    self.logger.error(
                        "Component already exists",
                        component_id=component_id
                    )
                    return False
                
                # Set timestamps
                now = datetime.now(timezone.utc)
                component_data['created_at'] = now.isoformat()
                component_data['updated_at'] = now.isoformat()
                
                # Calculate next review date
                sla_tier = SLATier(component_data['sla_tier'])
                if sla_tier == SLATier.CRITICAL:
                    next_review = now + timedelta(days=30)  # Monthly review
                elif sla_tier == SLATier.IMPORTANT:
                    next_review = now + timedelta(days=90)  # Quarterly review
                else:
                    next_review = now + timedelta(days=180)  # Semi-annual review
                
                component_data['next_review'] = next_review.isoformat()
                
                # Create component
                component = self._parse_component(component_data)
                self.components[component_id] = component
                
                # Save changes
                self._save_components()
                
                # Log audit event
                observability.audit_logger.log_event(
                    event_type="component_registered",
                    user="system",
                    resource=component_id,
                    action="register",
                    details=component.to_dict()
                )
                
                self.logger.info(
                    "Component registered",
                    component_id=component_id,
                    owner=component.owner.email,
                    sla_tier=component.sla_tier.value
                )
                
                return True
            
            except Exception as e:
                self.logger.error(
                    "Failed to register component",
                    error=str(e),
                    exc_info=True
                )
                return False
    
    def create_change_record(self, change_data: Dict[str, Any]) -> Optional[str]:
        """Create a new change record"""
        with self.lock:
            try:
                change_id = f"CHG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                change_record = ChangeRecord(
                    id=change_id,
                    component_id=change_data['component_id'],
                    change_type=ChangeType(change_data['change_type']),
                    title=change_data['title'],
                    description=change_data['description'],
                    owner=change_data['owner'],
                    risk_assessment=RiskLevel(change_data['risk_assessment']),
                    approval_required=change_data.get('approval_required', True),
                    approved_by=change_data.get('approved_by'),
                    implemented_at=None,
                    rollback_plan=change_data.get('rollback_plan'),
                    verification_steps=change_data.get('verification_steps', []),
                    created_at=datetime.now(timezone.utc),
                    status="planned",
                    metadata=change_data.get('metadata')
                )
                
                self.change_records[change_id] = change_record
                
                # Log audit event
                observability.audit_logger.log_event(
                    event_type="change_record_created",
                    user=change_record.owner,
                    resource=change_record.component_id,
                    action="create_change",
                    details=change_record.to_dict()
                )
                
                self.logger.info(
                    "Change record created",
                    change_id=change_id,
                    component_id=change_record.component_id,
                    change_type=change_record.change_type.value,
                    owner=change_record.owner
                )
                
                return change_id
            
            except Exception as e:
                self.logger.error(
                    "Failed to create change record",
                    error=str(e),
                    exc_info=True
                )
                return None
    
    def get_sla_status(self, component_id: str) -> Dict[str, Any]:
        """Get SLA status for a component"""
        if component_id not in self.components:
            return {"error": "Component not found"}
        
        component = self.components[component_id]
        sla_def = self.sla_definitions[component.sla_tier]
        
        now = datetime.now(timezone.utc)
        
        # Calculate time since last review
        time_since_review = None
        if component.last_reviewed:
            time_since_review = (now - component.last_reviewed).total_seconds() / 3600  # hours
        
        # Check if review is overdue
        review_overdue = False
        if component.next_review and now > component.next_review:
            review_overdue = True
        
        return {
            "component_id": component_id,
            "sla_tier": component.sla_tier.value,
            "resolution_hours": sla_def.resolution_hours,
            "escalation_hours": sla_def.escalation_hours,
            "last_reviewed": component.last_reviewed.isoformat() if component.last_reviewed else None,
            "next_review": component.next_review.isoformat() if component.next_review else None,
            "time_since_review_hours": time_since_review,
            "review_overdue": review_overdue,
            "owner": component.owner.email,
            "status": component.status.value
        }
    
    def get_ownership_report(self) -> Dict[str, Any]:
        """Generate ownership report"""
        with self.lock:
            owners = {}
            unowned_components = []
            
            for component in self.components.values():
                owner_email = component.owner.email
                
                if owner_email == "unknown" or not owner_email:
                    unowned_components.append(component.id)
                    continue
                
                if owner_email not in owners:
                    owners[owner_email] = {
                        "name": component.owner.name,
                        "team": component.owner.team,
                        "components": [],
                        "critical_count": 0,
                        "important_count": 0,
                        "optional_count": 0
                    }
                
                owners[owner_email]["components"].append({
                    "id": component.id,
                    "name": component.name,
                    "sla_tier": component.sla_tier.value,
                    "risk_level": component.risk_level.value,
                    "status": component.status.value
                })
                
                # Count by SLA tier
                if component.sla_tier == SLATier.CRITICAL:
                    owners[owner_email]["critical_count"] += 1
                elif component.sla_tier == SLATier.IMPORTANT:
                    owners[owner_email]["important_count"] += 1
                else:
                    owners[owner_email]["optional_count"] += 1
            
            return {
                "total_components": len(self.components),
                "total_owners": len(owners),
                "unowned_components": unowned_components,
                "unowned_count": len(unowned_components),
                "owners": owners,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    def get_maintenance_schedule(self) -> List[Dict[str, Any]]:
        """Get upcoming maintenance schedule"""
        with self.lock:
            now = datetime.now(timezone.utc)
            upcoming = []
            overdue = []
            
            for schedule in self.maintenance_schedules.values():
                schedule_dict = schedule.to_dict()
                
                # Add component information
                if schedule.component_id in self.components:
                    component = self.components[schedule.component_id]
                    schedule_dict['component_name'] = component.name
                    schedule_dict['owner_email'] = component.owner.email
                    schedule_dict['sla_tier'] = component.sla_tier.value
                
                # Check if overdue
                if schedule.next_maintenance < now:
                    overdue.append(schedule_dict)
                else:
                    upcoming.append(schedule_dict)
            
            # Sort by next maintenance date
            upcoming.sort(key=lambda x: x['next_maintenance'])
            overdue.sort(key=lambda x: x['next_maintenance'])
            
            return {
                "upcoming_maintenance": upcoming,
                "overdue_maintenance": overdue,
                "total_upcoming": len(upcoming),
                "total_overdue": len(overdue),
                "generated_at": now.isoformat()
            }
    
    def quarterly_cleanup(self) -> Dict[str, Any]:
        """Perform quarterly cleanup of deprecated components"""
        with self.lock:
            now = datetime.now(timezone.utc)
            cleanup_results = {
                "deprecated_components": [],
                "stale_changes": [],
                "overdue_reviews": [],
                "actions_taken": []
            }
            
            # Find deprecated components
            for component in self.components.values():
                if component.status == ComponentStatus.DEPRECATED:
                    # Check if deprecated for more than 90 days
                    if (now - component.updated_at).days > 90:
                        cleanup_results["deprecated_components"].append({
                            "id": component.id,
                            "name": component.name,
                            "deprecated_since": component.updated_at.isoformat(),
                            "owner": component.owner.email
                        })
            
            # Find stale change records
            for change in self.change_records.values():
                if change.status in ["planned", "approved"] and (now - change.created_at).days > 30:
                    cleanup_results["stale_changes"].append({
                        "id": change.id,
                        "title": change.title,
                        "created_at": change.created_at.isoformat(),
                        "owner": change.owner
                    })
            
            # Find overdue reviews
            for component in self.components.values():
                if component.next_review and now > component.next_review:
                    days_overdue = (now - component.next_review).days
                    cleanup_results["overdue_reviews"].append({
                        "id": component.id,
                        "name": component.name,
                        "days_overdue": days_overdue,
                        "owner": component.owner.email
                    })
            
            # Log cleanup audit event
            observability.audit_logger.log_event(
                event_type="quarterly_cleanup",
                user="system",
                resource="governance",
                action="cleanup",
                details=cleanup_results
            )
            
            self.logger.info(
                "Quarterly cleanup completed",
                deprecated_count=len(cleanup_results["deprecated_components"]),
                stale_changes=len(cleanup_results["stale_changes"]),
                overdue_reviews=len(cleanup_results["overdue_reviews"])
            )
            
            return cleanup_results

# =============================================================================
# GOVERNANCE CLI TOOLS
# =============================================================================

class GovernanceCLI:
    """Command-line interface for governance operations"""
    
    def __init__(self, governance_manager: GovernanceManager):
        self.governance = governance_manager
        self.logger = structlog.get_logger("governance_cli")
    
    def register_component_interactive(self):
        """Interactive component registration"""
        print("\n🏛️ Component Registration")
        print("=" * 40)
        
        component_data = {
            "id": input("Component ID: "),
            "name": input("Component Name: "),
            "description": input("Description: "),
            "owner": {
                "email": input("Owner Email: "),
                "name": input("Owner Name: "),
                "team": input("Team: "),
                "role": input("Role: "),
                "slack_handle": input("Slack Handle (optional): ") or None
            },
            "sla_tier": self._select_sla_tier(),
            "risk_level": self._select_risk_level(),
            "status": "active",
            "tags": input("Tags (comma-separated): ").split(",") if input("Tags (comma-separated): ") else [],
            "dependencies": input("Dependencies (comma-separated): ").split(",") if input("Dependencies (comma-separated): ") else []
        }
        
        if self.governance.register_component(component_data):
            print(f"✅ Component '{component_data['id']}' registered successfully")
        else:
            print(f"❌ Failed to register component '{component_data['id']}'")
    
    def _select_sla_tier(self) -> str:
        """Interactive SLA tier selection"""
        print("\nSLA Tiers:")
        print("1. Critical (72-hour resolution)")
        print("2. Important (14-day resolution)")
        print("3. Optional (Sprint end resolution)")
        
        while True:
            choice = input("Select SLA tier (1-3): ")
            if choice == "1":
                return "critical"
            elif choice == "2":
                return "important"
            elif choice == "3":
                return "optional"
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
    
    def _select_risk_level(self) -> str:
        """Interactive risk level selection"""
        print("\nRisk Levels:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        print("4. Critical")
        
        while True:
            choice = input("Select risk level (1-4): ")
            if choice == "1":
                return "low"
            elif choice == "2":
                return "medium"
            elif choice == "3":
                return "high"
            elif choice == "4":
                return "critical"
            else:
                print("Invalid choice. Please select 1, 2, 3, or 4.")
    
    def show_ownership_report(self):
        """Display ownership report"""
        report = self.governance.get_ownership_report()
        
        print("\n👥 OWNERSHIP REPORT")
        print("=" * 50)
        print(f"Total Components: {report['total_components']}")
        print(f"Total Owners: {report['total_owners']}")
        print(f"Unowned Components: {report['unowned_count']}")
        
        if report['unowned_components']:
            print("\n❌ Unowned Components:")
            for comp_id in report['unowned_components']:
                print(f"   - {comp_id}")
        
        print("\n📊 Ownership by Team:")
        for email, owner_info in report['owners'].items():
            print(f"\n👤 {owner_info['name']} ({email})")
            print(f"   Team: {owner_info['team']}")
            print(f"   Components: {len(owner_info['components'])}")
            print(f"   Critical: {owner_info['critical_count']}, Important: {owner_info['important_count']}, Optional: {owner_info['optional_count']}")
    
    def show_maintenance_schedule(self):
        """Display maintenance schedule"""
        schedule = self.governance.get_maintenance_schedule()
        
        print("\n🔧 MAINTENANCE SCHEDULE")
        print("=" * 50)
        
        if schedule['overdue_maintenance']:
            print(f"\n🚨 OVERDUE MAINTENANCE ({schedule['total_overdue']}):")
            for maint in schedule['overdue_maintenance']:
                print(f"   - {maint['component_id']}: {maint['next_maintenance']} (Owner: {maint.get('owner_email', 'unknown')})")
        
        if schedule['upcoming_maintenance']:
            print(f"\n📅 UPCOMING MAINTENANCE ({schedule['total_upcoming']}):")
            for maint in schedule['upcoming_maintenance'][:10]:  # Show next 10
                print(f"   - {maint['component_id']}: {maint['next_maintenance']} (Owner: {maint.get('owner_email', 'unknown')})")

# =============================================================================
# GLOBAL GOVERNANCE MANAGER
# =============================================================================

# Global governance manager instance
governance_manager = GovernanceManager()

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example usage
    
    # Show ownership report
    cli = GovernanceCLI(governance_manager)
    cli.show_ownership_report()
    
    # Show maintenance schedule
    cli.show_maintenance_schedule()
    
    # Create a change record
    change_data = {
        "component_id": "compliance_report_generator",
        "change_type": "feature_change",
        "title": "Add new report format support",
        "description": "Adding support for Excel and JSON report formats",
        "owner": "platform@dogan",
        "risk_assessment": "medium",
        "approval_required": True,
        "rollback_plan": "Disable new formats via feature flag",
        "verification_steps": [
            "Test report generation in all formats",
            "Verify file downloads work correctly",
            "Check performance impact"
        ]
    }
    
    change_id = governance_manager.create_change_record(change_data)
    print(f"\n📝 Change record created: {change_id}")
    
    # Get SLA status
    sla_status = governance_manager.get_sla_status("compliance_report_generator")
    print(f"\n📊 SLA Status: {sla_status}")
    
    # Perform quarterly cleanup
    cleanup_results = governance_manager.quarterly_cleanup()
    print(f"\n🧹 Quarterly cleanup results: {cleanup_results}")