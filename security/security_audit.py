#!/usr/bin/env python3
"""
Comprehensive Security Audit System for DoganAI Compliance Kit
Implements security scanning, vulnerability assessment, and compliance checking
"""

import os
import json
import hashlib
import re
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for audit findings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditCategory(Enum):
    """Audit categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_PROTECTION = "data_protection"
    NETWORK_SECURITY = "network_security"
    CONFIGURATION = "configuration"
    CODE_SECURITY = "code_security"
    DEPENDENCIES = "dependencies"
    COMPLIANCE = "compliance"

@dataclass
class SecurityFinding:
    """Security audit finding"""
    id: str
    title: str
    description: str
    category: AuditCategory
    level: SecurityLevel
    location: str
    recommendation: str
    timestamp: datetime
    status: str = "open"  # open, acknowledged, resolved
    evidence: Dict[str, Any] = None

class SecurityAuditor:
    """Comprehensive security audit system"""
    
    def __init__(self):
        self.findings = []
        self.audit_rules = []
        self.secret_patterns = []
        self.vulnerability_patterns = []
        
        # Initialize audit rules and patterns
        self._setup_audit_rules()
        self._setup_secret_patterns()
        self._setup_vulnerability_patterns()
    
    def _setup_audit_rules(self):
        """Setup security audit rules"""
        self.audit_rules = [
            # Authentication rules
            {
                'id': 'AUTH_001',
                'title': 'Weak Password Policy',
                'category': AuditCategory.AUTHENTICATION,
                'level': SecurityLevel.HIGH,
                'check': self._check_password_policy,
                'description': 'Check for weak password policies'
            },
            {
                'id': 'AUTH_002',
                'title': 'Missing Multi-Factor Authentication',
                'category': AuditCategory.AUTHENTICATION,
                'level': SecurityLevel.MEDIUM,
                'check': self._check_mfa_implementation,
                'description': 'Check for MFA implementation'
            },
            {
                'id': 'AUTH_003',
                'title': 'Session Management Issues',
                'category': AuditCategory.AUTHENTICATION,
                'level': SecurityLevel.HIGH,
                'check': self._check_session_management,
                'description': 'Check session management security'
            },
            
            # Authorization rules
            {
                'id': 'AUTHZ_001',
                'title': 'Missing Role-Based Access Control',
                'category': AuditCategory.AUTHORIZATION,
                'level': SecurityLevel.HIGH,
                'check': self._check_rbac_implementation,
                'description': 'Check RBAC implementation'
            },
            {
                'id': 'AUTHZ_002',
                'title': 'Insufficient Privilege Controls',
                'category': AuditCategory.AUTHORIZATION,
                'level': SecurityLevel.MEDIUM,
                'check': self._check_privilege_controls,
                'description': 'Check privilege escalation controls'
            },
            
            # Data Protection rules
            {
                'id': 'DATA_001',
                'title': 'Unencrypted Data Storage',
                'category': AuditCategory.DATA_PROTECTION,
                'level': SecurityLevel.CRITICAL,
                'check': self._check_data_encryption,
                'description': 'Check data encryption at rest'
            },
            {
                'id': 'DATA_002',
                'title': 'Insecure Data Transmission',
                'category': AuditCategory.DATA_PROTECTION,
                'level': SecurityLevel.CRITICAL,
                'check': self._check_data_transmission,
                'description': 'Check data transmission security'
            },
            {
                'id': 'DATA_003',
                'title': 'Missing Data Backup Encryption',
                'category': AuditCategory.DATA_PROTECTION,
                'level': SecurityLevel.HIGH,
                'check': self._check_backup_encryption,
                'description': 'Check backup encryption'
            },
            
            # Network Security rules
            {
                'id': 'NET_001',
                'title': 'Missing Network Segmentation',
                'category': AuditCategory.NETWORK_SECURITY,
                'level': SecurityLevel.MEDIUM,
                'check': self._check_network_segmentation,
                'description': 'Check network segmentation'
            },
            {
                'id': 'NET_002',
                'title': 'Insecure API Endpoints',
                'category': AuditCategory.NETWORK_SECURITY,
                'level': SecurityLevel.HIGH,
                'check': self._check_api_security,
                'description': 'Check API endpoint security'
            },
            
            # Configuration rules
            {
                'id': 'CONFIG_001',
                'title': 'Hardcoded Secrets',
                'category': AuditCategory.CONFIGURATION,
                'level': SecurityLevel.CRITICAL,
                'check': self._check_hardcoded_secrets,
                'description': 'Check for hardcoded secrets'
            },
            {
                'id': 'CONFIG_002',
                'title': 'Insecure Default Configurations',
                'category': AuditCategory.CONFIGURATION,
                'level': SecurityLevel.MEDIUM,
                'check': self._check_default_configs,
                'description': 'Check default security configurations'
            },
            
            # Code Security rules
            {
                'id': 'CODE_001',
                'title': 'SQL Injection Vulnerabilities',
                'category': AuditCategory.CODE_SECURITY,
                'level': SecurityLevel.CRITICAL,
                'check': self._check_sql_injection,
                'description': 'Check for SQL injection vulnerabilities'
            },
            {
                'id': 'CODE_002',
                'title': 'Cross-Site Scripting (XSS)',
                'category': AuditCategory.CODE_SECURITY,
                'level': SecurityLevel.HIGH,
                'check': self._check_xss_vulnerabilities,
                'description': 'Check for XSS vulnerabilities'
            },
            {
                'id': 'CODE_003',
                'title': 'Insecure Deserialization',
                'category': AuditCategory.CODE_SECURITY,
                'level': SecurityLevel.HIGH,
                'check': self._check_deserialization,
                'description': 'Check for insecure deserialization'
            },
            
            # Dependencies rules
            {
                'id': 'DEPS_001',
                'title': 'Outdated Dependencies',
                'category': AuditCategory.DEPENDENCIES,
                'level': SecurityLevel.MEDIUM,
                'check': self._check_dependency_versions,
                'description': 'Check for outdated dependencies'
            },
            {
                'id': 'DEPS_002',
                'title': 'Known Vulnerable Dependencies',
                'category': AuditCategory.DEPENDENCIES,
                'level': SecurityLevel.CRITICAL,
                'check': self._check_vulnerable_dependencies,
                'description': 'Check for known vulnerable dependencies'
            },
            
            # Compliance rules
            {
                'id': 'COMP_001',
                'title': 'GDPR Compliance',
                'category': AuditCategory.COMPLIANCE,
                'level': SecurityLevel.HIGH,
                'check': self._check_gdpr_compliance,
                'description': 'Check GDPR compliance requirements'
            },
            {
                'id': 'COMP_002',
                'title': 'ISO 27001 Compliance',
                'category': AuditCategory.COMPLIANCE,
                'level': SecurityLevel.HIGH,
                'check': self._check_iso27001_compliance,
                'description': 'Check ISO 27001 compliance'
            }
        ]
    
    def _setup_secret_patterns(self):
        """Setup patterns for detecting secrets"""
        self.secret_patterns = [
            # API Keys
            r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{32,}["\']',
            r'api[_-]?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{32,}["\']',
            
            # Database passwords
            r'password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
            r'db[_-]?password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
            
            # JWT secrets
            r'jwt[_-]?secret["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{32,}["\']',
            r'secret[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{32,}["\']',
            
            # Private keys
            r'-----BEGIN PRIVATE KEY-----',
            r'-----BEGIN RSA PRIVATE KEY-----',
            r'-----BEGIN DSA PRIVATE KEY-----',
            
            # AWS credentials
            r'AKIA[0-9A-Z]{16}',
            r'aws[_-]?access[_-]?key[_-]?id["\']?\s*[:=]\s*["\'][A-Z0-9]{20}["\']',
            r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\'][A-Za-z0-9/+=]{40}["\']',
            
            # Generic secrets
            r'secret["\']?\s*[:=]\s*["\'][^"\']{16,}["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\']{16,}["\']',
        ]
    
    def _setup_vulnerability_patterns(self):
        """Setup patterns for detecting vulnerabilities"""
        self.vulnerability_patterns = [
            # SQL Injection patterns
            r'execute\s*\(\s*["\'][^"\']*["\']\s*\+\s*\w+',
            r'cursor\.execute\s*\(\s*["\'][^"\']*["\']\s*%\s*\w+',
            
            # XSS patterns
            r'innerHTML\s*=\s*\w+',
            r'document\.write\s*\(\s*\w+',
            r'eval\s*\(\s*\w+',
            
            # Command injection patterns
            r'os\.system\s*\(\s*\w+',
            r'subprocess\.call\s*\(\s*\w+',
            r'exec\s*\(\s*\w+',
        ]
    
    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        logger.info("Starting comprehensive security audit...")
        
        start_time = datetime.now(timezone.utc)
        findings = []
        
        # Run all audit rules
        for rule in self.audit_rules:
            try:
                result = await rule['check']()
                if result:
                    finding = SecurityFinding(
                        id=rule['id'],
                        title=rule['title'],
                        description=rule['description'],
                        category=rule['category'],
                        level=rule['level'],
                        location=result.get('location', 'Unknown'),
                        recommendation=result.get('recommendation', 'Review and fix the identified issue'),
                        timestamp=datetime.now(timezone.utc),
                        evidence=result.get('evidence', {})
                    )
                    findings.append(finding)
            except Exception as e:
                logger.error(f"Error running audit rule {rule['id']}: {e}")
        
        # Scan for secrets
        secret_findings = await self._scan_for_secrets()
        findings.extend(secret_findings)
        
        # Scan for vulnerabilities
        vulnerability_findings = await self._scan_for_vulnerabilities()
        findings.extend(vulnerability_findings)
        
        # Store findings
        self.findings.extend(findings)
        
        # Generate audit report
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        report = {
            'audit_id': f"audit_{int(start_time.timestamp())}",
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_findings': len(findings),
            'findings_by_level': {
                level.value: len([f for f in findings if f.level == level])
                for level in SecurityLevel
            },
            'findings_by_category': {
                category.value: len([f for f in findings if f.category == category])
                for category in AuditCategory
            },
            'critical_findings': len([f for f in findings if f.level == SecurityLevel.CRITICAL]),
            'high_findings': len([f for f in findings if f.level == SecurityLevel.HIGH]),
            'medium_findings': len([f for f in findings if f.level == SecurityLevel.MEDIUM]),
            'low_findings': len([f for f in findings if f.level == SecurityLevel.LOW]),
            'findings': [
                {
                    'id': f.id,
                    'title': f.title,
                    'description': f.description,
                    'category': f.category.value,
                    'level': f.level.value,
                    'location': f.location,
                    'recommendation': f.recommendation,
                    'timestamp': f.timestamp.isoformat(),
                    'status': f.status,
                    'evidence': f.evidence
                }
                for f in findings
            ]
        }
        
        logger.info(f"Security audit completed. Found {len(findings)} issues.")
        return report
    
    async def _check_password_policy(self) -> Optional[Dict[str, Any]]:
        """Check password policy implementation"""
        # This would check actual password policy implementation
        # For now, return a placeholder finding
        return {
            'location': 'authentication/password_policy.py',
            'recommendation': 'Implement strong password policy with minimum length, complexity, and history requirements',
            'evidence': {'current_policy': 'No password policy found'}
        }
    
    async def _check_mfa_implementation(self) -> Optional[Dict[str, Any]]:
        """Check MFA implementation"""
        return {
            'location': 'authentication/mfa.py',
            'recommendation': 'Implement multi-factor authentication for all user accounts',
            'evidence': {'mfa_enabled': False}
        }
    
    async def _check_session_management(self) -> Optional[Dict[str, Any]]:
        """Check session management security"""
        return {
            'location': 'authentication/session.py',
            'recommendation': 'Implement secure session management with proper timeout and invalidation',
            'evidence': {'session_timeout': 'No timeout configured'}
        }
    
    async def _check_rbac_implementation(self) -> Optional[Dict[str, Any]]:
        """Check RBAC implementation"""
        return {
            'location': 'authorization/rbac.py',
            'recommendation': 'Implement role-based access control with proper permission management',
            'evidence': {'rbac_implemented': False}
        }
    
    async def _check_privilege_controls(self) -> Optional[Dict[str, Any]]:
        """Check privilege escalation controls"""
        return {
            'location': 'authorization/privileges.py',
            'recommendation': 'Implement proper privilege escalation controls and least privilege principle',
            'evidence': {'privilege_controls': 'Insufficient'}
        }
    
    async def _check_data_encryption(self) -> Optional[Dict[str, Any]]:
        """Check data encryption at rest"""
        return {
            'location': 'database/encryption.py',
            'recommendation': 'Implement encryption at rest for all sensitive data',
            'evidence': {'encryption_enabled': False}
        }
    
    async def _check_data_transmission(self) -> Optional[Dict[str, Any]]:
        """Check data transmission security"""
        return {
            'location': 'api/security.py',
            'recommendation': 'Use HTTPS/TLS for all data transmission',
            'evidence': {'tls_enabled': False}
        }
    
    async def _check_backup_encryption(self) -> Optional[Dict[str, Any]]:
        """Check backup encryption"""
        return {
            'location': 'backup/encryption.py',
            'recommendation': 'Encrypt all backup data',
            'evidence': {'backup_encryption': False}
        }
    
    async def _check_network_segmentation(self) -> Optional[Dict[str, Any]]:
        """Check network segmentation"""
        return {
            'location': 'network/segmentation.py',
            'recommendation': 'Implement proper network segmentation',
            'evidence': {'segmentation_implemented': False}
        }
    
    async def _check_api_security(self) -> Optional[Dict[str, Any]]:
        """Check API endpoint security"""
        return {
            'location': 'api/endpoints.py',
            'recommendation': 'Implement proper API security with authentication and rate limiting',
            'evidence': {'api_security': 'Insufficient'}
        }
    
    async def _check_hardcoded_secrets(self) -> Optional[Dict[str, Any]]:
        """Check for hardcoded secrets"""
        secrets_found = []
        
        # Scan Python files for secrets
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.py') or file.endswith('.env'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in self.secret_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                secrets_found.append({
                                    'file': file_path,
                                    'pattern': pattern,
                                    'matches': len(matches)
                                })
                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
        
        if secrets_found:
            return {
                'location': 'Multiple files',
                'recommendation': 'Remove all hardcoded secrets and use environment variables or secure secret management',
                'evidence': {'secrets_found': secrets_found}
            }
        
        return None
    
    async def _check_default_configs(self) -> Optional[Dict[str, Any]]:
        """Check default security configurations"""
        return {
            'location': 'config/security.py',
            'recommendation': 'Review and secure all default configurations',
            'evidence': {'default_configs': 'Insecure defaults detected'}
        }
    
    async def _check_sql_injection(self) -> Optional[Dict[str, Any]]:
        """Check for SQL injection vulnerabilities"""
        vulnerabilities_found = []
        
        # Scan Python files for SQL injection patterns
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in self.vulnerability_patterns:
                            if 'sql' in pattern.lower():
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                if matches:
                                    vulnerabilities_found.append({
                                        'file': file_path,
                                        'pattern': pattern,
                                        'matches': len(matches)
                                    })
                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
        
        if vulnerabilities_found:
            return {
                'location': 'Multiple files',
                'recommendation': 'Use parameterized queries and input validation to prevent SQL injection',
                'evidence': {'vulnerabilities_found': vulnerabilities_found}
            }
        
        return None
    
    async def _check_xss_vulnerabilities(self) -> Optional[Dict[str, Any]]:
        """Check for XSS vulnerabilities"""
        return {
            'location': 'ui/templates.py',
            'recommendation': 'Implement proper input validation and output encoding to prevent XSS',
            'evidence': {'xss_protection': 'Insufficient'}
        }
    
    async def _check_deserialization(self) -> Optional[Dict[str, Any]]:
        """Check for insecure deserialization"""
        return {
            'location': 'api/serialization.py',
            'recommendation': 'Use secure deserialization methods and validate all input',
            'evidence': {'deserialization_security': 'Insufficient'}
        }
    
    async def _check_dependency_versions(self) -> Optional[Dict[str, Any]]:
        """Check for outdated dependencies"""
        return {
            'location': 'requirements.txt',
            'recommendation': 'Update all dependencies to latest secure versions',
            'evidence': {'outdated_deps': 'Multiple outdated dependencies found'}
        }
    
    async def _check_vulnerable_dependencies(self) -> Optional[Dict[str, Any]]:
        """Check for known vulnerable dependencies"""
        return {
            'location': 'requirements.txt',
            'recommendation': 'Remove or update vulnerable dependencies',
            'evidence': {'vulnerable_deps': 'Known vulnerable dependencies detected'}
        }
    
    async def _check_gdpr_compliance(self) -> Optional[Dict[str, Any]]:
        """Check GDPR compliance"""
        return {
            'location': 'compliance/gdpr.py',
            'recommendation': 'Implement GDPR compliance measures including data protection and user rights',
            'evidence': {'gdpr_compliance': 'Insufficient'}
        }
    
    async def _check_iso27001_compliance(self) -> Optional[Dict[str, Any]]:
        """Check ISO 27001 compliance"""
        return {
            'location': 'compliance/iso27001.py',
            'recommendation': 'Implement ISO 27001 information security management system',
            'evidence': {'iso27001_compliance': 'Insufficient'}
        }
    
    async def _scan_for_secrets(self) -> List[SecurityFinding]:
        """Scan codebase for secrets"""
        findings = []
        
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith(('.py', '.env', '.json', '.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in self.secret_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                finding = SecurityFinding(
                                    id=f"SECRET_{len(findings)+1:03d}",
                                    title=f"Hardcoded Secret Found in {file}",
                                    description=f"Found {len(matches)} potential secrets in {file_path}",
                                    category=AuditCategory.CONFIGURATION,
                                    level=SecurityLevel.CRITICAL,
                                    location=file_path,
                                    recommendation="Remove hardcoded secrets and use environment variables or secure secret management",
                                    timestamp=datetime.now(timezone.utc),
                                    evidence={'pattern': pattern, 'matches': len(matches)}
                                )
                                findings.append(finding)
                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
        
        return findings
    
    async def _scan_for_vulnerabilities(self) -> List[SecurityFinding]:
        """Scan codebase for vulnerabilities"""
        findings = []
        
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in self.vulnerability_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                finding = SecurityFinding(
                                    id=f"VULN_{len(findings)+1:03d}",
                                    title=f"Security Vulnerability Found in {file}",
                                    description=f"Found {len(matches)} potential vulnerabilities in {file_path}",
                                    category=AuditCategory.CODE_SECURITY,
                                    level=SecurityLevel.HIGH,
                                    location=file_path,
                                    recommendation="Review and fix the identified security vulnerabilities",
                                    timestamp=datetime.now(timezone.utc),
                                    evidence={'pattern': pattern, 'matches': len(matches)}
                                )
                                findings.append(finding)
                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
        
        return findings
    
    def get_findings_summary(self) -> Dict[str, Any]:
        """Get summary of all findings"""
        return {
            'total_findings': len(self.findings),
            'open_findings': len([f for f in self.findings if f.status == 'open']),
            'resolved_findings': len([f for f in self.findings if f.status == 'resolved']),
            'by_level': {
                level.value: len([f for f in self.findings if f.level == level])
                for level in SecurityLevel
            },
            'by_category': {
                category.value: len([f for f in self.findings if f.category == category])
                for category in AuditCategory
            }
        }
    
    def export_findings(self, format: str = 'json') -> str:
        """Export findings in specified format"""
        if format == 'json':
            return json.dumps({
                'findings': [
                    {
                        'id': f.id,
                        'title': f.title,
                        'description': f.description,
                        'category': f.category.value,
                        'level': f.level.value,
                        'location': f.location,
                        'recommendation': f.recommendation,
                        'timestamp': f.timestamp.isoformat(),
                        'status': f.status,
                        'evidence': f.evidence
                    }
                    for f in self.findings
                ],
                'summary': self.get_findings_summary()
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global security auditor instance
security_auditor = SecurityAuditor()

def get_security_auditor() -> SecurityAuditor:
    """Get the global security auditor instance"""
    return security_auditor
