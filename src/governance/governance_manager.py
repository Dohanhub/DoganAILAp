#!/usr/bin/env python3
"""
Governance Manager
Manages service ownership, SLA tracking, change classification, and maintenance schedules
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.observability import logger

class SLATier(Enum):
    """SLA tier classifications"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ChangeType(Enum):
    """Change classification types"""
    EMERGENCY = "emergency"
    STANDARD = "standard"
    NORMAL = "normal"

class IncidentSeverity(Enum):
    """Incident severity levels"""
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"

@dataclass
class ServiceOwnership:
    """Service ownership information"""
    team: str
    email: str
    slack: Optional[str] = None
    manager: Optional[str] = None
    responsibility: Optional[str] = None

@dataclass
class SLATargets:
    """SLA targets and thresholds"""
    tier: SLATier
    availability_target: str
    response_time_target: str
    error_rate_target: str
    recovery_time_objective: str
    recovery_point_objective: str

@dataclass
class MaintenanceWindow:
    """Maintenance window definition"""
    day: str
    time: str
    duration: str
    activities: List[str]

@dataclass
class ServiceInfo:
    """Complete service information"""
    name: str
    description: str
    version: str
    environment: str
    ownership: ServiceOwnership
    sla_targets: SLATargets
    maintenance_windows: List[MaintenanceWindow]
    dependencies: Dict[str, List[str]]
    compliance_frameworks: List[str]

class GovernanceManager:
    """Manages service governance, ownership, and compliance"""
    
    def __init__(self, catalog_path: str = None):
        if catalog_path is None:
            catalog_path = Path(__file__).parent / "service_catalog.yml"
        
        self.catalog_path = Path(catalog_path)
        self.catalog_data = self._load_catalog()
        
    def _load_catalog(self) -> Dict[str, Any]:
        """Load service catalog from YAML file"""
        try:
            with open(self.catalog_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load service catalog: {e}")
            return {}
    
    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get complete service information"""
        services = self.catalog_data.get('services', {})
        if service_name not in services:
            return None
        
        service_data = services[service_name]
        
        # Parse ownership
        ownership_data = service_data.get('ownership', {}).get('primary_owner', {})
        ownership = ServiceOwnership(
            team=ownership_data.get('team', ''),
            email=ownership_data.get('email', ''),
            slack=ownership_data.get('slack'),
            manager=ownership_data.get('manager')
        )
        
        # Parse SLA targets
        sla_data = service_data.get('sla_tier', {})
        sla_targets = SLATargets(
            tier=SLATier(sla_data.get('tier', 'medium')),
            availability_target=sla_data.get('availability_target', '99.0%'),
            response_time_target=sla_data.get('response_time_target', '1s'),
            error_rate_target=sla_data.get('error_rate_target', '1%'),
            recovery_time_objective=sla_data.get('recovery_time_objective', '1 hour'),
            recovery_point_objective=sla_data.get('recovery_point_objective', '4 hours')
        )
        
        # Parse maintenance windows
        maintenance_data = service_data.get('maintenance_schedule', {}).get('regular_maintenance', {})
        maintenance_windows = []
        
        for period, window_data in maintenance_data.items():
            if isinstance(window_data, dict):
                window = MaintenanceWindow(
                    day=window_data.get('day', ''),
                    time=window_data.get('time', ''),
                    duration=window_data.get('duration', ''),
                    activities=window_data.get('activities', [])
                )
                maintenance_windows.append(window)
        
        return ServiceInfo(
            name=service_data.get('metadata', {}).get('name', service_name),
            description=service_data.get('metadata', {}).get('description', ''),
            version=service_data.get('metadata', {}).get('version', ''),
            environment=service_data.get('metadata', {}).get('environment', ''),
            ownership=ownership,
            sla_targets=sla_targets,
            maintenance_windows=maintenance_windows,
            dependencies=service_data.get('dependencies', {}),
            compliance_frameworks=service_data.get('compliance', {}).get('frameworks', [])
        )
    
    def get_service_owners(self, service_name: str) -> List[ServiceOwnership]:
        """Get all owners for a service"""
        services = self.catalog_data.get('services', {})
        if service_name not in services:
            return []
        
        service_data = services[service_name]
        ownership_data = service_data.get('ownership', {})
        
        owners = []
        
        # Primary owner
        primary = ownership_data.get('primary_owner', {})
        if primary:
            owners.append(ServiceOwnership(
                team=primary.get('team', ''),
                email=primary.get('email', ''),
                slack=primary.get('slack'),
                manager=primary.get('manager'),
                responsibility='primary'
            ))
        
        # Secondary owners
        for secondary in ownership_data.get('secondary_owners', []):
            owners.append(ServiceOwnership(
                team=secondary.get('team', ''),
                email=secondary.get('email', ''),
                slack=secondary.get('slack'),
                responsibility=secondary.get('responsibility', 'secondary')
            ))
        
        return owners
    
    def get_sla_requirements(self, service_name: str) -> Optional[SLATargets]:
        """Get SLA requirements for a service"""
        service_info = self.get_service_info(service_name)
        return service_info.sla_targets if service_info else None
    
    def get_change_classification(self, service_name: str, change_type: str) -> Dict[str, Any]:
        """Get change classification requirements"""
        services = self.catalog_data.get('services', {})
        if service_name not in services:
            return {}
        
        service_data = services[service_name]
        change_data = service_data.get('change_classification', {})
        change_types = change_data.get('change_types', {})
        
        return change_types.get(change_type, {})
    
    def get_maintenance_schedule(self, service_name: str) -> List[MaintenanceWindow]:
        """Get maintenance schedule for a service"""
        service_info = self.get_service_info(service_name)
        return service_info.maintenance_windows if service_info else []
    
    def get_next_maintenance_window(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get the next scheduled maintenance window"""
        windows = self.get_maintenance_schedule(service_name)
        if not windows:
            return None
        
        now = datetime.now()
        
        # Find next weekly maintenance (simplified logic)
        for window in windows:
            if 'sunday' in window.day.lower():
                # Calculate next Sunday
                days_ahead = 6 - now.weekday()  # Sunday is 6
                if days_ahead <= 0:
                    days_ahead += 7
                next_date = now + timedelta(days=days_ahead)
                
                return {
                    'date': next_date.strftime('%Y-%m-%d'),
                    'time': window.time,
                    'duration': window.duration,
                    'activities': window.activities
                }
        
        return None
    
    def get_incident_response_requirements(self, service_name: str, severity: IncidentSeverity) -> Dict[str, str]:
        """Get incident response requirements based on service and severity"""
        services = self.catalog_data.get('services', {})
        if service_name not in services:
            return {}
        
        service_data = services[service_name]
        incident_data = service_data.get('sla_tier', {}).get('incident_response', {})
        
        response_key = f"{severity.value}_response_time"
        return {
            'response_time': incident_data.get(response_key, '24 hours'),
            'escalation_policy': service_data.get('sla_tier', {}).get('escalation_policy', 'standard'),
            'on_call_required': service_data.get('sla_tier', {}).get('on_call_rotation', False)
        }
    
    def validate_service_compliance(self, service_name: str) -> Dict[str, Any]:
        """Validate service compliance with governance policies"""
        service_info = self.get_service_info(service_name)
        if not service_info:
            return {'valid': False, 'errors': ['Service not found']}
        
        errors = []
        warnings = []
        
        # Check ownership
        if not service_info.ownership.team:
            errors.append('Primary owner team not specified')
        if not service_info.ownership.email:
            errors.append('Primary owner email not specified')
        
        # Check SLA targets
        if service_info.sla_targets.tier == SLATier.CRITICAL:
            if '99.9' not in service_info.sla_targets.availability_target:
                warnings.append('Critical service should have 99.9% availability target')
        
        # Check maintenance windows
        if not service_info.maintenance_windows:
            warnings.append('No maintenance windows defined')
        
        # Check compliance frameworks
        if not service_info.compliance_frameworks:
            warnings.append('No compliance frameworks specified')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'compliance_score': max(0, 100 - len(errors) * 20 - len(warnings) * 5)
        }
    
    def generate_governance_report(self) -> Dict[str, Any]:
        """Generate comprehensive governance report"""
        services = self.catalog_data.get('services', {})
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_services': len(services),
            'services': {},
            'summary': {
                'sla_tiers': {},
                'compliance_scores': [],
                'ownership_coverage': 0,
                'maintenance_coverage': 0
            }
        }
        
        sla_tier_counts = {tier.value: 0 for tier in SLATier}
        total_compliance_score = 0
        services_with_owners = 0
        services_with_maintenance = 0
        
        for service_name in services:
            service_info = self.get_service_info(service_name)
            compliance = self.validate_service_compliance(service_name)
            
            if service_info:
                # Count SLA tiers
                sla_tier_counts[service_info.sla_targets.tier.value] += 1
                
                # Track compliance scores
                total_compliance_score += compliance['compliance_score']
                
                # Track ownership coverage
                if service_info.ownership.team and service_info.ownership.email:
                    services_with_owners += 1
                
                # Track maintenance coverage
                if service_info.maintenance_windows:
                    services_with_maintenance += 1
                
                report['services'][service_name] = {
                    'owner': service_info.ownership.team,
                    'sla_tier': service_info.sla_targets.tier.value,
                    'compliance_score': compliance['compliance_score'],
                    'errors': compliance['errors'],
                    'warnings': compliance['warnings']
                }
        
        # Calculate summary statistics
        report['summary']['sla_tiers'] = sla_tier_counts
        report['summary']['average_compliance_score'] = total_compliance_score / len(services) if services else 0
        report['summary']['ownership_coverage'] = (services_with_owners / len(services) * 100) if services else 0
        report['summary']['maintenance_coverage'] = (services_with_maintenance / len(services) * 100) if services else 0
        
        return report
    
    def get_services_by_owner(self, team: str) -> List[str]:
        """Get all services owned by a specific team"""
        services = self.catalog_data.get('services', {})
        owned_services = []
        
        for service_name in services:
            owners = self.get_service_owners(service_name)
            for owner in owners:
                if owner.team == team:
                    owned_services.append(service_name)
                    break
        
        return owned_services
    
    def get_services_by_sla_tier(self, tier: SLATier) -> List[str]:
        """Get all services with a specific SLA tier"""
        services = self.catalog_data.get('services', {})
        tier_services = []
        
        for service_name in services:
            service_info = self.get_service_info(service_name)
            if service_info and service_info.sla_targets.tier == tier:
                tier_services.append(service_name)
        
        return tier_services
    
    def update_service_ownership(self, service_name: str, new_owner: ServiceOwnership) -> bool:
        """Update service ownership information"""
        try:
            services = self.catalog_data.get('services', {})
            if service_name not in services:
                return False
            
            # Update primary owner
            services[service_name]['ownership']['primary_owner'] = {
                'team': new_owner.team,
                'email': new_owner.email,
                'slack': new_owner.slack,
                'manager': new_owner.manager
            }
            
            # Save updated catalog
            with open(self.catalog_path, 'w') as f:
                yaml.dump(self.catalog_data, f, default_flow_style=False)
            
            logger.info(f"Updated ownership for service {service_name} to team {new_owner.team}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update service ownership: {e}")
            return False

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Governance Manager CLI")
    parser.add_argument('command', choices=[
        'info', 'owners', 'sla', 'maintenance', 'compliance', 'report'
    ], help='Command to execute')
    parser.add_argument('--service', help='Service name')
    parser.add_argument('--team', help='Team name')
    parser.add_argument('--tier', help='SLA tier')
    parser.add_argument('--output', help='Output file for reports')
    
    args = parser.parse_args()
    
    manager = GovernanceManager()
    
    if args.command == 'info':
        if not args.service:
            print("Error: --service required for info command")
            sys.exit(1)
        
        service_info = manager.get_service_info(args.service)
        if service_info:
            print(json.dumps(asdict(service_info), indent=2, default=str))
        else:
            print(f"Service {args.service} not found")
    
    elif args.command == 'owners':
        if args.service:
            owners = manager.get_service_owners(args.service)
            print(json.dumps([asdict(owner) for owner in owners], indent=2))
        elif args.team:
            services = manager.get_services_by_owner(args.team)
            print(f"Services owned by {args.team}:")
            for service in services:
                print(f"  - {service}")
        else:
            print("Error: --service or --team required for owners command")
    
    elif args.command == 'sla':
        if args.service:
            sla = manager.get_sla_requirements(args.service)
            if sla:
                print(json.dumps(asdict(sla), indent=2, default=str))
            else:
                print(f"SLA requirements not found for {args.service}")
        elif args.tier:
            try:
                tier = SLATier(args.tier)
                services = manager.get_services_by_sla_tier(tier)
                print(f"Services with {args.tier} SLA tier:")
                for service in services:
                    print(f"  - {service}")
            except ValueError:
                print(f"Invalid SLA tier: {args.tier}")
        else:
            print("Error: --service or --tier required for sla command")
    
    elif args.command == 'maintenance':
        if not args.service:
            print("Error: --service required for maintenance command")
            sys.exit(1)
        
        next_window = manager.get_next_maintenance_window(args.service)
        if next_window:
            print(f"Next maintenance window for {args.service}:")
            print(json.dumps(next_window, indent=2))
        else:
            print(f"No maintenance windows found for {args.service}")
    
    elif args.command == 'compliance':
        if not args.service:
            print("Error: --service required for compliance command")
            sys.exit(1)
        
        compliance = manager.validate_service_compliance(args.service)
        print(json.dumps(compliance, indent=2))
    
    elif args.command == 'report':
        report = manager.generate_governance_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Governance report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()