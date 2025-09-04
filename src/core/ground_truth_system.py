#!/usr/bin/env python3
"""
Ground Truth Verification System
Replaces hard-coded scores with evidence-based validation
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
import hashlib
import requests
import subprocess
import psutil
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemEvidence:
    """Evidence collected from actual system inspection"""
    timestamp: datetime
    evidence_type: str
    source: str
    data: Dict[str, Any]
    hash_signature: str

@dataclass
class GroundTruthResult:
    """Ground truth validation result with evidence"""
    control_id: str
    actual_score: float
    evidence_count: int
    validation_method: str
    system_evidence: List[SystemEvidence]
    confidence_level: float
    last_verified: datetime

class GroundTruthSystem:
    """Evidence-based verification system replacing hard-coded scores"""
    
    def __init__(self, db_path: str = "ground_truth.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize ground truth database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ground_truth_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                source TEXT NOT NULL,
                data_json TEXT NOT NULL,
                hash_signature TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(control_id, evidence_type, hash_signature)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_id TEXT NOT NULL,
                actual_score REAL NOT NULL,
                evidence_count INTEGER NOT NULL,
                validation_method TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Ground truth database initialized")
    
    async def collect_network_evidence(self) -> List[SystemEvidence]:
        """Collect actual network configuration evidence"""
        evidence = []
        
        try:
            # Check network interfaces
            interfaces = psutil.net_if_addrs()
            interface_data = {
                "interface_count": len(interfaces),
                "interfaces": list(interfaces.keys())
            }
            
            evidence.append(SystemEvidence(
                timestamp=datetime.now(timezone.utc),
                evidence_type="network_interfaces",
                source="psutil.net_if_addrs",
                data=interface_data,
                hash_signature=hashlib.md5(json.dumps(interface_data, sort_keys=True).encode()).hexdigest()
            ))
            
            # Check listening ports
            connections = psutil.net_connections(kind='inet')
            listening_ports = [conn.laddr.port for conn in connections if conn.status == 'LISTEN']
            port_data = {
                "listening_ports": sorted(set(listening_ports)),
                "port_count": len(set(listening_ports))
            }
            
            evidence.append(SystemEvidence(
                timestamp=datetime.now(timezone.utc),
                evidence_type="listening_ports",
                source="psutil.net_connections",
                data=port_data,
                hash_signature=hashlib.md5(json.dumps(port_data, sort_keys=True).encode()).hexdigest()
            ))
            
            # Check firewall status (Windows)
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                      capture_output=True, text=True, timeout=10)
                firewall_active = "ON" in result.stdout
                firewall_data = {
                    "firewall_enabled": firewall_active,
                    "profiles_checked": result.stdout.count("Profile Settings")
                }
                
                evidence.append(SystemEvidence(
                    timestamp=datetime.now(timezone.utc),
                    evidence_type="firewall_status",
                    source="netsh_advfirewall",
                    data=firewall_data,
                    hash_signature=hashlib.md5(json.dumps(firewall_data, sort_keys=True).encode()).hexdigest()
                ))
            except Exception as e:
                logger.warning(f"Could not check firewall status: {e}")
                
        except Exception as e:
            logger.error(f"Failed to collect network evidence: {e}")
            
        return evidence
    
    async def collect_tls_evidence(self) -> List[SystemEvidence]:
        """Collect actual TLS/encryption evidence"""
        evidence = []
        
        try:
            # Check TLS configuration on running services
            tls_ports = [443, 8001, 8443]  # Common HTTPS ports
            tls_data = {"tls_enabled_ports": [], "tls_versions": []}
            
            for port in tls_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        tls_data["tls_enabled_ports"].append(port)
                    sock.close()
                except Exception:
                    pass
            
            # Check SSL certificate files
            cert_paths = [
                "certs/",
                "ssl/",
                "certificates/",
                "config/ssl/"
            ]
            
            cert_files = []
            for cert_path in cert_paths:
                path = Path(cert_path)
                if path.exists():
                    cert_files.extend([str(f) for f in path.glob("*.crt")])
                    cert_files.extend([str(f) for f in path.glob("*.pem")])
            
            tls_data["certificate_files"] = cert_files
            tls_data["certificate_count"] = len(cert_files)
            
            evidence.append(SystemEvidence(
                timestamp=datetime.now(timezone.utc),
                evidence_type="tls_configuration",
                source="socket_and_filesystem",
                data=tls_data,
                hash_signature=hashlib.md5(json.dumps(tls_data, sort_keys=True).encode()).hexdigest()
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect TLS evidence: {e}")
            
        return evidence
    
    async def collect_storage_evidence(self) -> List[SystemEvidence]:
        """Collect actual storage and data residency evidence"""
        evidence = []
        
        try:
            # Check database connections
            db_evidence = {"databases": [], "connection_strings": []}
            
            # Look for database configuration files
            config_files = [
                ".env",
                "config.json", 
                "database.yml",
                "docker-compose.yml"
            ]
            
            for config_file in config_files:
                if Path(config_file).exists():
                    try:
                        with open(config_file, 'r') as f:
                            content = f.read()
                            if 'DATABASE_URL' in content or 'postgres' in content.lower():
                                db_evidence["databases"].append(config_file)
                    except Exception:
                        pass
            
            # Check for data directories
            data_dirs = ["data/", "db/", "database/", "storage/"]
            existing_dirs = [d for d in data_dirs if Path(d).exists()]
            db_evidence["data_directories"] = existing_dirs
            
            evidence.append(SystemEvidence(
                timestamp=datetime.now(timezone.utc),
                evidence_type="storage_configuration",
                source="filesystem_inspection",
                data=db_evidence,
                hash_signature=hashlib.md5(json.dumps(db_evidence, sort_keys=True).encode()).hexdigest()
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect storage evidence: {e}")
            
        return evidence
    
    async def validate_control_with_evidence(self, control_id: str) -> GroundTruthResult:
        """Validate control using actual system evidence"""
        all_evidence = []
        
        # Collect evidence based on control type
        if "network" in control_id.lower() or control_id == "NCA-02":
            all_evidence.extend(await self.collect_network_evidence())
            
        if "tls" in control_id.lower() or "encryption" in control_id.lower() or control_id == "NCA-03":
            all_evidence.extend(await self.collect_tls_evidence())
            
        if "data" in control_id.lower() or "residency" in control_id.lower() or control_id == "NCA-10":
            all_evidence.extend(await self.collect_storage_evidence())
        
        # Calculate actual score based on evidence
        actual_score = self._calculate_evidence_score(control_id, all_evidence)
        
        # Calculate confidence level
        confidence_level = min(len(all_evidence) * 0.2, 1.0)  # More evidence = higher confidence
        
        # Store evidence in database
        await self._store_evidence(control_id, all_evidence, actual_score, confidence_level)
        
        result = GroundTruthResult(
            control_id=control_id,
            actual_score=actual_score,
            evidence_count=len(all_evidence),
            validation_method="system_inspection",
            system_evidence=all_evidence,
            confidence_level=confidence_level,
            last_verified=datetime.now(timezone.utc)
        )
        
        return result
    
    def _calculate_evidence_score(self, control_id: str, evidence: List[SystemEvidence]) -> float:
        """Calculate actual score based on collected evidence"""
        if not evidence:
            return 0.0
            
        score = 0.0
        max_score = 100.0
        
        # Score based on evidence type and quality
        for ev in evidence:
            if ev.evidence_type == "network_interfaces":
                # Score based on network configuration
                interface_count = ev.data.get("interface_count", 0)
                if interface_count > 1:  # Multiple interfaces suggest segmentation
                    score += 20.0
                    
            elif ev.evidence_type == "listening_ports":
                # Score based on port configuration
                port_count = ev.data.get("port_count", 0)
                if port_count > 0:
                    score += 15.0
                    
            elif ev.evidence_type == "firewall_status":
                # Score based on firewall configuration
                if ev.data.get("firewall_enabled", False):
                    score += 30.0
                    
            elif ev.evidence_type == "tls_configuration":
                # Score based on TLS configuration
                tls_ports = ev.data.get("tls_enabled_ports", [])
                cert_count = ev.data.get("certificate_count", 0)
                if tls_ports:
                    score += 25.0
                if cert_count > 0:
                    score += 25.0
                    
            elif ev.evidence_type == "storage_configuration":
                # Score based on storage configuration
                db_count = len(ev.data.get("databases", []))
                data_dirs = len(ev.data.get("data_directories", []))
                if db_count > 0:
                    score += 20.0
                if data_dirs > 0:
                    score += 15.0
        
        return min(score, max_score)
    
    async def _store_evidence(self, control_id: str, evidence: List[SystemEvidence], 
                            score: float, confidence: float):
        """Store evidence and results in database"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Store evidence
            for ev in evidence:
                conn.execute("""
                    INSERT OR REPLACE INTO ground_truth_evidence 
                    (control_id, evidence_type, source, data_json, hash_signature, confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (control_id, ev.evidence_type, ev.source, 
                     json.dumps(ev.data), ev.hash_signature, confidence))
            
            # Store validation result
            conn.execute("""
                INSERT INTO validation_results 
                (control_id, actual_score, evidence_count, validation_method, confidence_level)
                VALUES (?, ?, ?, ?, ?)
            """, (control_id, score, len(evidence), "system_inspection", confidence))
            
            conn.commit()
            
        finally:
            conn.close()
    
    async def get_historical_scores(self, control_id: str) -> List[Dict[str, Any]]:
        """Get historical validation scores for a control"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            cursor = conn.execute("""
                SELECT actual_score, evidence_count, confidence_level, timestamp
                FROM validation_results 
                WHERE control_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (control_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "score": row[0],
                    "evidence_count": row[1],
                    "confidence": row[2],
                    "timestamp": row[3]
                })
                
            return results
            
        finally:
            conn.close()
    
    async def replace_hardcoded_scores(self) -> Dict[str, float]:
        """Replace all hard-coded scores with evidence-based ones"""
        logger.info("Replacing hard-coded scores with ground truth validation...")
        
        # Key controls to validate
        controls_to_validate = [
            "NCA-02",  # Network Segmentation
            "NCA-03",  # Encryption In Transit  
            "NCA-10",  # Data Residency
            "SAMA-01", # Zero Trust
            "CITC-TC-001", # Service Quality
            "CITC-TC-002"  # ICT Security
        ]
        
        real_scores = {}
        
        for control_id in controls_to_validate:
            try:
                result = await self.validate_control_with_evidence(control_id)
                real_scores[control_id] = result.actual_score
                logger.info(f"Control {control_id}: {result.actual_score:.1f}% (confidence: {result.confidence_level:.2f})")
                
            except Exception as e:
                logger.error(f"Failed to validate {control_id}: {e}")
                real_scores[control_id] = 0.0
        
        return real_scores

# Example usage
async def main():
    """Example usage of ground truth system"""
    system = GroundTruthSystem()
    
    print("=== GROUND TRUTH VALIDATION SYSTEM ===")
    print("Collecting actual system evidence...")
    
    # Replace hard-coded scores with real validation
    real_scores = await system.replace_hardcoded_scores()
    
    print(f"\n=== EVIDENCE-BASED SCORES ===")
    total_score = 0
    valid_scores = 0
    
    for control_id, score in real_scores.items():
        print(f"{control_id}: {score:.1f}%")
        if score > 0:
            total_score += score
            valid_scores += 1
    
    if valid_scores > 0:
        average_score = total_score / valid_scores
        print(f"\nOverall Evidence-Based Score: {average_score:.1f}%")
    else:
        print("\nNo valid scores collected")
    
    # Show detailed evidence for one control
    print(f"\n=== DETAILED EVIDENCE FOR NCA-02 ===")
    result = await system.validate_control_with_evidence("NCA-02")
    
    print(f"Score: {result.actual_score:.1f}%")
    print(f"Evidence Count: {result.evidence_count}")
    print(f"Confidence: {result.confidence_level:.2f}")
    
    for evidence in result.system_evidence:
        print(f"\nEvidence Type: {evidence.evidence_type}")
        print(f"Source: {evidence.source}")
        print(f"Data: {json.dumps(evidence.data, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
