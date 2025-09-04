#!/usr/bin/env python3
"""
Real Compliance Validation Engine
Evidence-based compliance checking with actual policy validation
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import re
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    VALIDATION_ERROR = "validation_error"

class ValidationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ValidationResult:
    control_id: str
    title: str
    status: ComplianceStatus
    severity: ValidationSeverity
    score: float
    evidence: List[str]
    violations: List[str]
    recommendations: List[str]
    validation_timestamp: datetime
    validation_method: str

@dataclass
class ComplianceAssessment:
    framework: str
    organization_id: str
    assessment_id: str
    total_controls: int
    compliant_controls: int
    non_compliant_controls: int
    overall_score: float
    compliance_percentage: float
    risk_level: str
    validation_results: List[ValidationResult]
    assessment_timestamp: datetime
    assessor: str

class RealComplianceValidator:
    """Evidence-based compliance validation engine"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/policies"
        self.policies = {}
        self.validation_cache = {}
        self.audit_log = []
        self._load_policies()
        
    def _load_policies(self):
        """Load all policy files from config directory"""
        try:
            policy_dir = Path(self.config_path)
            if not policy_dir.exists():
                logger.error(f"Policy directory not found: {policy_dir}")
                return
                
            for policy_file in policy_dir.glob("*.yaml"):
                try:
                    with open(policy_file, 'r', encoding='utf-8') as f:
                        policy_data = yaml.safe_load(f)
                        regulator = policy_data.get('regulator')
                        if regulator:
                            self.policies[regulator] = policy_data
                            logger.info(f"Loaded policy: {regulator}")
                except Exception as e:
                    logger.error(f"Failed to load policy {policy_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
    
    async def validate_nca_controls(self, system_config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate NCA Essential Cybersecurity Controls"""
        results = []
        nca_policy = self.policies.get('NCA', {})
        controls = nca_policy.get('controls', [])
        
        for control in controls:
            control_id = control.get('id')
            title = control.get('title_en', 'Unknown Control')
            requirement = control.get('requirement_en', '')
            
            # Real validation logic based on control requirements
            validation_result = await self._validate_control(control_id, title, requirement, system_config)
            results.append(validation_result)
            
        return results
    
    async def _validate_control(self, control_id: str, title: str, requirement: str, 
                               system_config: Dict[str, Any]) -> ValidationResult:
        """Perform actual validation of a specific control"""
        evidence = []
        violations = []
        recommendations = []
        score = 0.0
        status = ComplianceStatus.NON_COMPLIANT
        
        try:
            # NCA-02: Network Segmentation
            if control_id == "NCA-02":
                score, evidence, violations = await self._validate_network_segmentation(system_config)
                
            # NCA-03: Encryption In Transit
            elif control_id == "NCA-03":
                score, evidence, violations = await self._validate_encryption_transit(system_config)
                
            # NCA-10: Data Residency
            elif control_id == "NCA-10":
                score, evidence, violations = await self._validate_data_residency(system_config)
                
            # Default validation for other controls
            else:
                score, evidence, violations = await self._default_validation(control_id, system_config)
            
            # Determine compliance status based on score
            if score >= 90:
                status = ComplianceStatus.COMPLIANT
            elif score >= 70:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
                
            # Generate recommendations based on violations
            if violations:
                recommendations = self._generate_recommendations(control_id, violations)
                
        except Exception as e:
            logger.error(f"Validation error for {control_id}: {e}")
            status = ComplianceStatus.VALIDATION_ERROR
            violations.append(f"Validation failed: {str(e)}")
        
        return ValidationResult(
            control_id=control_id,
            title=title,
            status=status,
            severity=ValidationSeverity.HIGH,
            score=score,
            evidence=evidence,
            violations=violations,
            recommendations=recommendations,
            validation_timestamp=datetime.now(timezone.utc),
            validation_method="automated_technical_validation"
        )
    
    async def _validate_network_segmentation(self, config: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate network segmentation implementation"""
        evidence = []
        violations = []
        score = 0.0
        
        # Check for network configuration
        network_config = config.get('network', {})
        
        # Validate VPC/VNET segmentation
        if network_config.get('vpc_enabled'):
            evidence.append("VPC/Virtual Network configured")
            score += 25
        else:
            violations.append("No VPC/Virtual Network segmentation found")
            
        # Validate subnet segmentation
        subnets = network_config.get('subnets', [])
        if len(subnets) >= 3:  # Public, Private, Database subnets
            evidence.append(f"Multiple subnets configured: {len(subnets)}")
            score += 25
        else:
            violations.append("Insufficient subnet segmentation")
            
        # Validate security groups/NSGs
        security_groups = network_config.get('security_groups', [])
        if security_groups:
            evidence.append(f"Security groups configured: {len(security_groups)}")
            score += 25
        else:
            violations.append("No security groups configured")
            
        # Validate firewall rules
        firewall_rules = network_config.get('firewall_rules', [])
        if firewall_rules:
            evidence.append(f"Firewall rules configured: {len(firewall_rules)}")
            score += 25
        else:
            violations.append("No firewall rules configured")
            
        return score, evidence, violations
    
    async def _validate_encryption_transit(self, config: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate encryption in transit implementation"""
        evidence = []
        violations = []
        score = 0.0
        
        # Check TLS configuration
        tls_config = config.get('tls', {})
        
        # Validate TLS version
        tls_version = tls_config.get('version')
        if tls_version and float(tls_version) >= 1.2:
            evidence.append(f"TLS {tls_version} configured")
            score += 30
        else:
            violations.append("TLS 1.2+ not configured")
            
        # Validate certificate configuration
        if tls_config.get('certificates'):
            evidence.append("SSL certificates configured")
            score += 20
        else:
            violations.append("No SSL certificates configured")
            
        # Validate mTLS for internal services
        if tls_config.get('mutual_tls'):
            evidence.append("Mutual TLS configured for internal services")
            score += 30
        else:
            violations.append("Mutual TLS not configured for internal services")
            
        # Validate HTTPS enforcement
        if config.get('https_only', False):
            evidence.append("HTTPS-only enforcement enabled")
            score += 20
        else:
            violations.append("HTTPS-only enforcement not enabled")
            
        return score, evidence, violations
    
    async def _validate_data_residency(self, config: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate data residency in KSA"""
        evidence = []
        violations = []
        score = 0.0
        
        # Check data storage configuration
        storage_config = config.get('storage', {})
        
        # Validate database location
        db_region = storage_config.get('database_region')
        if db_region and 'saudi' in db_region.lower():
            evidence.append(f"Database in Saudi region: {db_region}")
            score += 40
        else:
            violations.append("Database not confirmed in Saudi Arabia")
            
        # Validate file storage location
        file_region = storage_config.get('file_storage_region')
        if file_region and 'saudi' in file_region.lower():
            evidence.append(f"File storage in Saudi region: {file_region}")
            score += 30
        else:
            violations.append("File storage not confirmed in Saudi Arabia")
            
        # Validate backup location
        backup_region = storage_config.get('backup_region')
        if backup_region and 'saudi' in backup_region.lower():
            evidence.append(f"Backups in Saudi region: {backup_region}")
            score += 30
        else:
            violations.append("Backups not confirmed in Saudi Arabia")
            
        return score, evidence, violations
    
    async def _default_validation(self, control_id: str, config: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Default validation for controls without specific implementation"""
        evidence = ["Control exists in policy framework"]
        violations = ["Automated validation not yet implemented for this control"]
        score = 50.0  # Partial score for having the control defined
        return score, evidence, violations
    
    def _generate_recommendations(self, control_id: str, violations: List[str]) -> List[str]:
        """Generate actionable recommendations based on violations"""
        recommendations = []
        
        for violation in violations:
            if "network segmentation" in violation.lower():
                recommendations.append("Implement VPC with separate subnets for different tiers")
                recommendations.append("Configure security groups with least privilege access")
                
            elif "tls" in violation.lower() or "encryption" in violation.lower():
                recommendations.append("Upgrade to TLS 1.2 or higher")
                recommendations.append("Implement mutual TLS for internal service communication")
                
            elif "saudi" in violation.lower() or "residency" in violation.lower():
                recommendations.append("Migrate data storage to Saudi Arabia regions")
                recommendations.append("Ensure all backups are stored within KSA")
                
        return recommendations
    
    async def assess_compliance(self, framework: str, organization_id: str, 
                              system_config: Dict[str, Any]) -> ComplianceAssessment:
        """Perform comprehensive compliance assessment"""
        assessment_id = f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Validate based on framework
        if framework.upper() == "NCA":
            validation_results = await self.validate_nca_controls(system_config)
        else:
            raise ValueError(f"Framework {framework} not supported yet")
        
        # Calculate overall metrics
        total_controls = len(validation_results)
        compliant_controls = sum(1 for r in validation_results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant_controls = sum(1 for r in validation_results if r.status == ComplianceStatus.NON_COMPLIANT)
        
        # Calculate overall score
        if total_controls > 0:
            overall_score = sum(r.score for r in validation_results) / total_controls
            compliance_percentage = (compliant_controls / total_controls) * 100
        else:
            overall_score = 0.0
            compliance_percentage = 0.0
        
        # Determine risk level
        if compliance_percentage >= 90:
            risk_level = "LOW"
        elif compliance_percentage >= 70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        assessment = ComplianceAssessment(
            framework=framework,
            organization_id=organization_id,
            assessment_id=assessment_id,
            total_controls=total_controls,
            compliant_controls=compliant_controls,
            non_compliant_controls=non_compliant_controls,
            overall_score=overall_score,
            compliance_percentage=compliance_percentage,
            risk_level=risk_level,
            validation_results=validation_results,
            assessment_timestamp=datetime.now(timezone.utc),
            assessor="automated_compliance_engine"
        )
        
        # Log assessment to audit trail
        await self._log_assessment(assessment)
        
        return assessment
    
    async def _log_assessment(self, assessment: ComplianceAssessment):
        """Log assessment to audit trail"""
        audit_entry = {
            "timestamp": assessment.assessment_timestamp.isoformat(),
            "assessment_id": assessment.assessment_id,
            "framework": assessment.framework,
            "organization_id": assessment.organization_id,
            "compliance_percentage": assessment.compliance_percentage,
            "risk_level": assessment.risk_level,
            "total_controls": assessment.total_controls,
            "compliant_controls": assessment.compliant_controls,
            "assessor": assessment.assessor
        }
        
        self.audit_log.append(audit_entry)
        
        # Save to file for persistence
        audit_file = f"audit_logs/compliance_assessment_{assessment.assessment_id}.json"
        Path("audit_logs").mkdir(exist_ok=True)
        
        with open(audit_file, 'w') as f:
            json.dump(audit_entry, f, indent=2)
            
        logger.info(f"Assessment logged: {assessment.assessment_id}")

# Example usage and testing
async def main():
    """Example usage of the real compliance validator"""
    validator = RealComplianceValidator()
    
    # Example system configuration
    system_config = {
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
    
    # Perform compliance assessment
    assessment = await validator.assess_compliance("NCA", "org_001", system_config)
    
    print(f"\n=== COMPLIANCE ASSESSMENT RESULTS ===")
    print(f"Framework: {assessment.framework}")
    print(f"Assessment ID: {assessment.assessment_id}")
    print(f"Overall Score: {assessment.overall_score:.2f}")
    print(f"Compliance Percentage: {assessment.compliance_percentage:.1f}%")
    print(f"Risk Level: {assessment.risk_level}")
    print(f"Compliant Controls: {assessment.compliant_controls}/{assessment.total_controls}")
    
    print(f"\n=== DETAILED RESULTS ===")
    for result in assessment.validation_results:
        print(f"\n{result.control_id}: {result.title}")
        print(f"  Status: {result.status.value}")
        print(f"  Score: {result.score:.1f}")
        print(f"  Evidence: {', '.join(result.evidence)}")
        if result.violations:
            print(f"  Violations: {', '.join(result.violations)}")
        if result.recommendations:
            print(f"  Recommendations: {', '.join(result.recommendations)}")

if __name__ == "__main__":
    asyncio.run(main())
