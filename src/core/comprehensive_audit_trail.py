#!/usr/bin/env python3
"""
Comprehensive Audit Trail System
Complete logging and tracking of all compliance assessments and activities
"""

import asyncio
import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import threading
from contextlib import asynccontextmanager
import aiofiles
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    COMPLIANCE_ASSESSMENT = "compliance_assessment"
    POLICY_VALIDATION = "policy_validation"
    CONTROL_CHECK = "control_check"
    VIOLATION_DETECTED = "violation_detected"
    REMEDIATION_ACTION = "remediation_action"
    USER_ACCESS = "user_access"
    SYSTEM_CHANGE = "system_change"
    DATA_ACCESS = "data_access"
    ALERT_GENERATED = "alert_generated"
    REPORT_GENERATED = "report_generated"

class AuditSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AuditEvent:
    """Complete audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    organization_id: str
    session_id: Optional[str]
    source_ip: Optional[str]
    user_agent: Optional[str]
    severity: AuditSeverity
    framework: Optional[str]
    control_id: Optional[str]
    action: str
    description: str
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    evidence_hash: Optional[str]
    compliance_impact: Optional[str]
    regulatory_reference: Optional[str]

@dataclass
class AuditQuery:
    """Audit trail query parameters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    severity: Optional[AuditSeverity] = None
    framework: Optional[str] = None
    control_id: Optional[str] = None
    limit: int = 100
    offset: int = 0

class ComprehensiveAuditTrail:
    """Complete audit trail system with tamper-proof logging"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = self.config.get('audit_db_path', 'audit_trail.db')
        self.log_directory = Path(self.config.get('log_directory', 'audit_logs'))
        self.redis_client = None
        self.event_buffer = []
        self.buffer_lock = threading.Lock()
        self._init_storage()
        
    def _init_storage(self):
        """Initialize audit storage systems"""
        # Create log directory
        self.log_directory.mkdir(exist_ok=True)
        
        # Initialize SQLite database
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                user_id TEXT,
                organization_id TEXT NOT NULL,
                session_id TEXT,
                source_ip TEXT,
                user_agent TEXT,
                severity TEXT NOT NULL,
                framework TEXT,
                control_id TEXT,
                action TEXT NOT NULL,
                description TEXT NOT NULL,
                before_state_json TEXT,
                after_state_json TEXT,
                metadata_json TEXT NOT NULL,
                evidence_hash TEXT,
                compliance_impact TEXT,
                regulatory_reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(timestamp),
                INDEX(event_type),
                INDEX(organization_id),
                INDEX(user_id),
                INDEX(framework),
                INDEX(control_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_integrity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                hash_chain TEXT NOT NULL,
                previous_hash TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(event_id) REFERENCES audit_events(event_id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id TEXT NOT NULL,
                framework TEXT NOT NULL,
                compliance_percentage REAL NOT NULL,
                risk_level TEXT NOT NULL,
                assessment_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                INDEX(organization_id, framework),
                INDEX(timestamp)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Audit trail database initialized")
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection for real-time audit streaming"""
        try:
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection for audit streaming established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
    
    async def log_compliance_assessment(self, assessment: Any, user_id: str = None, 
                                      session_context: Dict[str, Any] = None) -> str:
        """Log complete compliance assessment with full audit trail"""
        session_context = session_context or {}
        
        # Main assessment event
        assessment_event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.COMPLIANCE_ASSESSMENT,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            organization_id=assessment.organization_id,
            session_id=session_context.get('session_id'),
            source_ip=session_context.get('source_ip'),
            user_agent=session_context.get('user_agent'),
            severity=AuditSeverity.INFO,
            framework=assessment.framework,
            control_id=None,
            action="compliance_assessment_completed",
            description=f"Compliance assessment completed for {assessment.framework}",
            before_state=None,
            after_state={
                "compliance_percentage": assessment.compliance_percentage,
                "overall_score": assessment.overall_score,
                "risk_level": assessment.risk_level,
                "total_controls": assessment.total_controls,
                "compliant_controls": assessment.compliant_controls
            },
            metadata={
                "assessment_id": assessment.assessment_id,
                "assessor": assessment.assessor,
                "validation_results_count": len(assessment.validation_results)
            },
            evidence_hash=self._calculate_evidence_hash(assessment),
            compliance_impact="assessment_completed",
            regulatory_reference=f"{assessment.framework}_compliance_framework"
        )
        
        await self._store_audit_event(assessment_event)
        
        # Log individual control validations
        for result in assessment.validation_results:
            control_event = AuditEvent(
                event_id=str(uuid.uuid4()),
                event_type=AuditEventType.CONTROL_CHECK,
                timestamp=result.validation_timestamp,
                user_id=user_id,
                organization_id=assessment.organization_id,
                session_id=session_context.get('session_id'),
                source_ip=session_context.get('source_ip'),
                user_agent=session_context.get('user_agent'),
                severity=AuditSeverity.HIGH if result.status.value == "non_compliant" else AuditSeverity.INFO,
                framework=assessment.framework,
                control_id=result.control_id,
                action=f"control_validation_{result.status.value}",
                description=f"Control {result.control_id} validated: {result.title}",
                before_state=None,
                after_state={
                    "status": result.status.value,
                    "score": result.score,
                    "evidence_count": len(result.evidence),
                    "violations_count": len(result.violations)
                },
                metadata={
                    "validation_method": result.validation_method,
                    "evidence": result.evidence,
                    "violations": result.violations,
                    "recommendations": result.recommendations
                },
                evidence_hash=self._calculate_control_hash(result),
                compliance_impact=result.status.value,
                regulatory_reference=f"{assessment.framework}_{result.control_id}"
            )
            
            await self._store_audit_event(control_event)
            
            # Log violations as separate events
            if result.violations:
                violation_event = AuditEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=AuditEventType.VIOLATION_DETECTED,
                    timestamp=datetime.now(timezone.utc),
                    user_id=user_id,
                    organization_id=assessment.organization_id,
                    session_id=session_context.get('session_id'),
                    source_ip=session_context.get('source_ip'),
                    user_agent=session_context.get('user_agent'),
                    severity=AuditSeverity.CRITICAL if result.severity.value == "critical" else AuditSeverity.HIGH,
                    framework=assessment.framework,
                    control_id=result.control_id,
                    action="compliance_violation_detected",
                    description=f"Compliance violations detected in {result.control_id}",
                    before_state=None,
                    after_state={
                        "violation_count": len(result.violations),
                        "violations": result.violations,
                        "severity": result.severity.value
                    },
                    metadata={
                        "control_title": result.title,
                        "recommendations": result.recommendations,
                        "validation_method": result.validation_method
                    },
                    evidence_hash=self._calculate_violation_hash(result.violations),
                    compliance_impact="violation_detected",
                    regulatory_reference=f"{assessment.framework}_{result.control_id}_violation"
                )
                
                await self._store_audit_event(violation_event)
        
        # Update compliance timeline
        await self._update_compliance_timeline(assessment)
        
        return assessment_event.event_id
    
    async def log_user_access(self, user_id: str, action: str, resource: str,
                            session_context: Dict[str, Any] = None) -> str:
        """Log user access events"""
        session_context = session_context or {}
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.USER_ACCESS,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            organization_id=session_context.get('organization_id', 'unknown'),
            session_id=session_context.get('session_id'),
            source_ip=session_context.get('source_ip'),
            user_agent=session_context.get('user_agent'),
            severity=AuditSeverity.INFO,
            framework=None,
            control_id=None,
            action=action,
            description=f"User {user_id} performed {action} on {resource}",
            before_state=None,
            after_state={"resource": resource, "access_granted": True},
            metadata={
                "resource": resource,
                "access_method": session_context.get('access_method', 'web')
            },
            evidence_hash=None,
            compliance_impact="user_activity",
            regulatory_reference=None
        )
        
        await self._store_audit_event(event)
        return event.event_id
    
    async def log_system_change(self, change_type: str, component: str, 
                              before_state: Dict[str, Any], after_state: Dict[str, Any],
                              user_id: str = None, session_context: Dict[str, Any] = None) -> str:
        """Log system configuration changes"""
        session_context = session_context or {}
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.SYSTEM_CHANGE,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            organization_id=session_context.get('organization_id', 'system'),
            session_id=session_context.get('session_id'),
            source_ip=session_context.get('source_ip'),
            user_agent=session_context.get('user_agent'),
            severity=AuditSeverity.MEDIUM,
            framework=None,
            control_id=None,
            action=f"system_change_{change_type}",
            description=f"System change: {change_type} in {component}",
            before_state=before_state,
            after_state=after_state,
            metadata={
                "component": component,
                "change_type": change_type
            },
            evidence_hash=self._calculate_change_hash(before_state, after_state),
            compliance_impact="system_configuration_change",
            regulatory_reference=None
        )
        
        await self._store_audit_event(event)
        return event.event_id
    
    async def log_alert_generation(self, alert_data: Dict[str, Any], 
                                 user_id: str = None) -> str:
        """Log compliance alert generation"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.ALERT_GENERATED,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            organization_id=alert_data.get('organization_id', 'unknown'),
            session_id=None,
            source_ip=None,
            user_agent=None,
            severity=AuditSeverity.HIGH if alert_data.get('severity') == 'critical' else AuditSeverity.MEDIUM,
            framework=alert_data.get('framework'),
            control_id=alert_data.get('control_id'),
            action="compliance_alert_generated",
            description=f"Compliance alert generated: {alert_data.get('title', 'Unknown')}",
            before_state=None,
            after_state=alert_data,
            metadata={
                "alert_type": alert_data.get('type'),
                "trigger": alert_data.get('trigger')
            },
            evidence_hash=self._calculate_alert_hash(alert_data),
            compliance_impact="alert_generated",
            regulatory_reference=f"{alert_data.get('framework')}_{alert_data.get('control_id')}"
        )
        
        await self._store_audit_event(event)
        return event.event_id
    
    async def _store_audit_event(self, event: AuditEvent):
        """Store audit event with integrity verification"""
        # Calculate integrity hash chain
        previous_hash = await self._get_last_hash()
        event_data = asdict(event)
        event_json = json.dumps(event_data, sort_keys=True, default=str)
        current_hash = hashlib.sha256(f"{previous_hash}{event_json}".encode()).hexdigest()
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        try:
            # Insert audit event
            conn.execute("""
                INSERT INTO audit_events (
                    event_id, event_type, timestamp, user_id, organization_id,
                    session_id, source_ip, user_agent, severity, framework,
                    control_id, action, description, before_state_json,
                    after_state_json, metadata_json, evidence_hash,
                    compliance_impact, regulatory_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.event_type.value, event.timestamp.isoformat(),
                event.user_id, event.organization_id, event.session_id,
                event.source_ip, event.user_agent, event.severity.value,
                event.framework, event.control_id, event.action, event.description,
                json.dumps(event.before_state) if event.before_state else None,
                json.dumps(event.after_state) if event.after_state else None,
                json.dumps(event.metadata), event.evidence_hash,
                event.compliance_impact, event.regulatory_reference
            ))
            
            # Insert integrity record
            conn.execute("""
                INSERT INTO audit_integrity (event_id, hash_chain, previous_hash)
                VALUES (?, ?, ?)
            """, (event.event_id, current_hash, previous_hash))
            
            conn.commit()
            
        finally:
            conn.close()
        
        # Write to log file
        await self._write_log_file(event)
        
        # Stream to Redis if available
        if self.redis_client:
            await self.redis_client.lpush("audit_stream", json.dumps(event_data, default=str))
            await self.redis_client.ltrim("audit_stream", 0, 9999)  # Keep last 10k events
        
        logger.info(f"Audit event stored: {event.event_id}")
    
    async def _write_log_file(self, event: AuditEvent):
        """Write audit event to daily log file"""
        log_date = event.timestamp.strftime("%Y-%m-%d")
        log_file = self.log_directory / f"audit_{log_date}.jsonl"
        
        event_data = asdict(event)
        event_line = json.dumps(event_data, default=str) + "\n"
        
        async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
            await f.write(event_line)
    
    async def _get_last_hash(self) -> str:
        """Get the last hash in the integrity chain"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT hash_chain FROM audit_integrity 
                ORDER BY timestamp DESC LIMIT 1
            """)
            result = cursor.fetchone()
            return result[0] if result else "genesis"
        finally:
            conn.close()
    
    async def _update_compliance_timeline(self, assessment: Any):
        """Update compliance timeline for trend analysis"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO compliance_timeline (
                    organization_id, framework, compliance_percentage,
                    risk_level, assessment_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                assessment.organization_id, assessment.framework,
                assessment.compliance_percentage, assessment.risk_level,
                assessment.assessment_id, assessment.assessment_timestamp.isoformat()
            ))
            conn.commit()
        finally:
            conn.close()
    
    def _calculate_evidence_hash(self, assessment: Any) -> str:
        """Calculate hash of assessment evidence"""
        evidence_data = {
            "assessment_id": assessment.assessment_id,
            "compliance_percentage": assessment.compliance_percentage,
            "total_controls": assessment.total_controls,
            "compliant_controls": assessment.compliant_controls
        }
        return hashlib.sha256(json.dumps(evidence_data, sort_keys=True).encode()).hexdigest()
    
    def _calculate_control_hash(self, result: Any) -> str:
        """Calculate hash of control validation result"""
        control_data = {
            "control_id": result.control_id,
            "status": result.status.value,
            "score": result.score,
            "evidence": result.evidence,
            "violations": result.violations
        }
        return hashlib.sha256(json.dumps(control_data, sort_keys=True).encode()).hexdigest()
    
    def _calculate_violation_hash(self, violations: List[str]) -> str:
        """Calculate hash of violations"""
        return hashlib.sha256(json.dumps(sorted(violations)).encode()).hexdigest()
    
    def _calculate_change_hash(self, before: Dict[str, Any], after: Dict[str, Any]) -> str:
        """Calculate hash of system changes"""
        change_data = {"before": before, "after": after}
        return hashlib.sha256(json.dumps(change_data, sort_keys=True).encode()).hexdigest()
    
    def _calculate_alert_hash(self, alert_data: Dict[str, Any]) -> str:
        """Calculate hash of alert data"""
        return hashlib.sha256(json.dumps(alert_data, sort_keys=True).encode()).hexdigest()
    
    async def query_audit_trail(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """Query audit trail with filters"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Build query
            where_clauses = []
            params = []
            
            if query.start_date:
                where_clauses.append("timestamp >= ?")
                params.append(query.start_date.isoformat())
            
            if query.end_date:
                where_clauses.append("timestamp <= ?")
                params.append(query.end_date.isoformat())
            
            if query.event_types:
                placeholders = ",".join("?" * len(query.event_types))
                where_clauses.append(f"event_type IN ({placeholders})")
                params.extend([et.value for et in query.event_types])
            
            if query.user_id:
                where_clauses.append("user_id = ?")
                params.append(query.user_id)
            
            if query.organization_id:
                where_clauses.append("organization_id = ?")
                params.append(query.organization_id)
            
            if query.severity:
                where_clauses.append("severity = ?")
                params.append(query.severity.value)
            
            if query.framework:
                where_clauses.append("framework = ?")
                params.append(query.framework)
            
            if query.control_id:
                where_clauses.append("control_id = ?")
                params.append(query.control_id)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            sql = f"""
                SELECT * FROM audit_events 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """
            params.extend([query.limit, query.offset])
            
            cursor = conn.execute(sql, params)
            columns = [description[0] for description in cursor.description]
            
            results = []
            for row in cursor.fetchall():
                event_dict = dict(zip(columns, row))
                
                # Parse JSON fields
                if event_dict['before_state_json']:
                    event_dict['before_state'] = json.loads(event_dict['before_state_json'])
                if event_dict['after_state_json']:
                    event_dict['after_state'] = json.loads(event_dict['after_state_json'])
                if event_dict['metadata_json']:
                    event_dict['metadata'] = json.loads(event_dict['metadata_json'])
                
                results.append(event_dict)
            
            return results
            
        finally:
            conn.close()
    
    async def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify audit trail integrity"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get all integrity records
            cursor = conn.execute("""
                SELECT ai.event_id, ai.hash_chain, ai.previous_hash, ae.timestamp
                FROM audit_integrity ai
                JOIN audit_events ae ON ai.event_id = ae.event_id
                ORDER BY ae.timestamp
            """)
            
            integrity_records = cursor.fetchall()
            
            verification_results = {
                "total_events": len(integrity_records),
                "verified_events": 0,
                "integrity_violations": [],
                "verification_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            previous_hash = "genesis"
            
            for record in integrity_records:
                event_id, hash_chain, stored_previous_hash, timestamp = record
                
                if stored_previous_hash == previous_hash:
                    verification_results["verified_events"] += 1
                else:
                    verification_results["integrity_violations"].append({
                        "event_id": event_id,
                        "timestamp": timestamp,
                        "expected_previous_hash": previous_hash,
                        "stored_previous_hash": stored_previous_hash
                    })
                
                previous_hash = hash_chain
            
            verification_results["integrity_percentage"] = (
                verification_results["verified_events"] / verification_results["total_events"] * 100
                if verification_results["total_events"] > 0 else 100
            )
            
            return verification_results
            
        finally:
            conn.close()
    
    async def get_compliance_timeline(self, organization_id: str, 
                                   framework: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get compliance timeline for trend analysis"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            where_clause = "organization_id = ? AND timestamp >= ?"
            params = [organization_id, start_date.isoformat()]
            
            if framework:
                where_clause += " AND framework = ?"
                params.append(framework)
            
            cursor = conn.execute(f"""
                SELECT * FROM compliance_timeline
                WHERE {where_clause}
                ORDER BY timestamp
            """, params)
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            conn.close()

# Example usage
async def main():
    """Example usage of comprehensive audit trail"""
    audit = ComprehensiveAuditTrail()
    await audit.initialize_redis()
    
    # Example: Log user access
    session_context = {
        "session_id": "sess_123",
        "source_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "organization_id": "org_001"
    }
    
    access_event_id = await audit.log_user_access(
        "user_001", "dashboard_access", "compliance_dashboard", session_context
    )
    print(f"User access logged: {access_event_id}")
    
    # Example: Log system change
    before_state = {"tls_version": "1.2", "encryption": "enabled"}
    after_state = {"tls_version": "1.3", "encryption": "enabled"}
    
    change_event_id = await audit.log_system_change(
        "tls_upgrade", "web_server", before_state, after_state, "admin_001", session_context
    )
    print(f"System change logged: {change_event_id}")
    
    # Query audit trail
    query = AuditQuery(
        start_date=datetime.now(timezone.utc) - timedelta(hours=1),
        organization_id="org_001",
        limit=10
    )
    
    events = await audit.query_audit_trail(query)
    print(f"\nFound {len(events)} audit events:")
    
    for event in events:
        print(f"- {event['timestamp']}: {event['action']} by {event['user_id']}")
    
    # Verify integrity
    integrity = await audit.verify_audit_integrity()
    print(f"\nAudit Integrity: {integrity['integrity_percentage']:.1f}%")
    print(f"Verified Events: {integrity['verified_events']}/{integrity['total_events']}")

if __name__ == "__main__":
    asyncio.run(main())
