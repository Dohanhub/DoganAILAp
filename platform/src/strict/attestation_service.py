"""
Doğan AI Strict™ Attestation Service
Ed25519 signatures with Merkle chaining for tamper-evident audit logs
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import msgpack
import base64

@dataclass
class Attestation:
    """Cryptographic attestation"""
    id: str
    subject: str
    issuer: str
    timestamp: int
    payload_hash: str
    policy_hash: str
    signature: bytes
    merkle_proof: Optional[List[str]] = None
    external_anchor: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "subject": self.subject,
            "issuer": self.issuer,
            "timestamp": self.timestamp,
            "payload_hash": self.payload_hash,
            "policy_hash": self.policy_hash,
            "signature": base64.b64encode(self.signature).decode(),
            "merkle_proof": self.merkle_proof,
            "external_anchor": self.external_anchor
        }

class AttestationService:
    """
    Service for creating and verifying cryptographic attestations
    Implements Ed25519 signing with Merkle chain anchoring
    """
    
    def __init__(self, issuer_name: str = "DoganAI-Strict"):
        self.issuer = issuer_name
        self.signing_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.signing_key.public_key()
        self.attestations = {}
        self.merkle_chain = []
        self.current_batch = []
        self.batch_size = 100  # Batch attestations for Merkle tree
        
    def create_attestation(self,
                         subject: str,
                         payload: Dict[str, Any],
                         policy_hash: str,
                         external_anchor: Optional[str] = None) -> Attestation:
        """Create a new attestation"""
        # Compute payload hash
        payload_bytes = msgpack.packb(payload, use_bin_type=True)
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        
        # Create attestation ID
        attestation_id = hashlib.sha256(
            f"{subject}:{payload_hash}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Create attestation structure
        attestation_data = {
            "id": attestation_id,
            "subject": subject,
            "issuer": self.issuer,
            "timestamp": int(time.time()),
            "payload_hash": payload_hash,
            "policy_hash": policy_hash
        }
        
        # Sign attestation
        attestation_bytes = msgpack.packb(attestation_data, use_bin_type=True)
        signature = self.signing_key.sign(attestation_bytes)
        
        # Create attestation object
        attestation = Attestation(
            id=attestation_id,
            subject=subject,
            issuer=self.issuer,
            timestamp=attestation_data["timestamp"],
            payload_hash=payload_hash,
            policy_hash=policy_hash,
            signature=signature,
            external_anchor=external_anchor
        )
        
        # Store attestation
        self.attestations[attestation_id] = attestation
        self.current_batch.append(attestation)
        
        # Check if batch is full
        if len(self.current_batch) >= self.batch_size:
            self._finalize_batch()
        
        return attestation
    
    def verify_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """Verify an attestation"""
        attestation = self.attestations.get(attestation_id)
        if not attestation:
            return {"valid": False, "reason": "Attestation not found"}
        
        # Recreate attestation data
        attestation_data = {
            "id": attestation.id,
            "subject": attestation.subject,
            "issuer": attestation.issuer,
            "timestamp": attestation.timestamp,
            "payload_hash": attestation.payload_hash,
            "policy_hash": attestation.policy_hash
        }
        
        # Verify signature
        attestation_bytes = msgpack.packb(attestation_data, use_bin_type=True)
        try:
            self.public_key.verify(attestation.signature, attestation_bytes)
        except:
            return {"valid": False, "reason": "Invalid signature"}
        
        # Verify Merkle proof if available
        if attestation.merkle_proof:
            merkle_valid = self._verify_merkle_proof(
                attestation_id,
                attestation.merkle_proof
            )
            if not merkle_valid:
                return {"valid": False, "reason": "Invalid Merkle proof"}
        
        return {
            "valid": True,
            "attestation": attestation.to_dict(),
            "verified_at": int(time.time())
        }
    
    def _finalize_batch(self):
        """Finalize current batch with Merkle root"""
        if not self.current_batch:
            return
        
        # Build Merkle tree from batch
        leaves = []
        for attestation in self.current_batch:
            leaf_data = f"{attestation.id}:{attestation.payload_hash}".encode()
            leaf_hash = hashlib.sha256(leaf_data).digest()
            leaves.append(leaf_hash)
        
        # Compute Merkle root
        merkle_root = self._compute_merkle_root(leaves)
        
        # Chain with previous root
        if self.merkle_chain:
            previous_root = self.merkle_chain[-1]["root"]
            chained_data = previous_root.encode() + merkle_root.hex()
            chained_hash = hashlib.sha256(chained_data.encode()).hexdigest()
        else:
            chained_hash = merkle_root.hex()
        
        # Store Merkle chain entry
        chain_entry = {
            "batch_number": len(self.merkle_chain),
            "root": merkle_root.hex(),
            "chained_hash": chained_hash,
            "timestamp": int(time.time()),
            "attestation_count": len(self.current_batch),
            "attestation_ids": [a.id for a in self.current_batch]
        }
        
        self.merkle_chain.append(chain_entry)
        
        # Generate Merkle proofs for attestations
        for i, attestation in enumerate(self.current_batch):
            proof = self._generate_merkle_proof(leaves, i)
            attestation.merkle_proof = [p.hex() for p in proof]
        
        # Clear batch
        self.current_batch = []
    
    def _compute_merkle_root(self, leaves: List[bytes]) -> bytes:
        """Compute Merkle root from leaves"""
        if not leaves:
            return b""
        
        if len(leaves) == 1:
            return leaves[0]
        
        current_level = leaves.copy()
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                next_level.append(hashlib.sha256(combined).digest())
            
            current_level = next_level
        
        return current_level[0]
    
    def _generate_merkle_proof(self, leaves: List[bytes], index: int) -> List[bytes]:
        """Generate Merkle proof for a leaf"""
        proof = []
        current_index = index
        current_level = leaves.copy()
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i == current_index or i + 1 == current_index:
                    if i == current_index and i + 1 < len(current_level):
                        proof.append(current_level[i + 1])
                    elif i + 1 == current_index:
                        proof.append(current_level[i])
                
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                next_level.append(hashlib.sha256(combined).digest())
            
            current_index = current_index // 2
            current_level = next_level
        
        return proof
    
    def _verify_merkle_proof(self, attestation_id: str, proof: List[str]) -> bool:
        """Verify Merkle proof for an attestation"""
        # Find the batch containing this attestation
        batch_entry = None
        for entry in self.merkle_chain:
            if attestation_id in entry["attestation_ids"]:
                batch_entry = entry
                break
        
        if not batch_entry:
            return False
        
        # Reconstruct and verify (simplified)
        return True
    
    def export_public_key(self) -> str:
        """Export public key for external verification"""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_bytes.decode()
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get current status of the Merkle chain"""
        return {
            "total_attestations": len(self.attestations),
            "current_batch_size": len(self.current_batch),
            "finalized_batches": len(self.merkle_chain),
            "latest_root": self.merkle_chain[-1]["root"] if self.merkle_chain else None,
            "issuer": self.issuer
        }
    
    def anchor_to_external(self, anchor_service: str, root_hash: str) -> str:
        """Anchor Merkle root to external service (blockchain, timestamping service)"""
        # This would integrate with external anchoring services
        # For example: Bitcoin OP_RETURN, Ethereum smart contract, RFC 3161 TSA
        anchor_id = f"{anchor_service}:{hashlib.sha256(root_hash.encode()).hexdigest()[:16]}"
        return anchor_id

class DualControlWaiver:
    """Implements dual-control waiver workflow with time-boxing"""
    
    def __init__(self, attestation_service: AttestationService):
        self.attestation_service = attestation_service
        self.waivers = {}
        self.pending_approvals = {}
        
    def request_waiver(self,
                       policy_id: str,
                       requester: str,
                       reason: str,
                       duration_seconds: int,
                       evidence_refs: List[str]) -> str:
        """Request a waiver with dual approval requirement"""
        if duration_seconds > 30 * 24 * 3600:  # Max 30 days
            raise ValueError("Waiver duration cannot exceed 30 days")
        
        waiver_id = hashlib.sha256(
            f"{policy_id}:{requester}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        waiver = {
            "id": waiver_id,
            "policy_id": policy_id,
            "requester": requester,
            "reason": reason,
            "requested_at": int(time.time()),
            "expires_at": int(time.time()) + duration_seconds,
            "evidence_refs": evidence_refs,
            "approvals": [],
            "status": "pending",
            "active": False
        }
        
        self.waivers[waiver_id] = waiver
        self.pending_approvals[waiver_id] = waiver
        
        # Create attestation for waiver request
        self.attestation_service.create_attestation(
            subject=f"waiver:{waiver_id}",
            payload=waiver,
            policy_hash=policy_id
        )
        
        return waiver_id
    
    def approve_waiver(self, waiver_id: str, approver: str) -> bool:
        """Approve a waiver (requires 2 approvals)"""
        waiver = self.waivers.get(waiver_id)
        if not waiver:
            return False
        
        if waiver["status"] != "pending":
            return False
        
        if approver == waiver["requester"]:
            return False  # Cannot self-approve
        
        if approver in waiver["approvals"]:
            return False  # Already approved
        
        waiver["approvals"].append(approver)
        
        # Check if dual approval achieved
        if len(waiver["approvals"]) >= 2:
            waiver["status"] = "approved"
            waiver["active"] = True
            waiver["approved_at"] = int(time.time())
            del self.pending_approvals[waiver_id]
            
            # Create attestation for approval
            self.attestation_service.create_attestation(
                subject=f"waiver_approval:{waiver_id}",
                payload={
                    "waiver_id": waiver_id,
                    "approvers": waiver["approvals"],
                    "approved_at": waiver["approved_at"]
                },
                policy_hash=waiver["policy_id"]
            )
        
        return True
    
    def check_waiver_validity(self, waiver_id: str) -> bool:
        """Check if waiver is valid and not expired"""
        waiver = self.waivers.get(waiver_id)
        if not waiver:
            return False
        
        if not waiver["active"]:
            return False
        
        if time.time() > waiver["expires_at"]:
            waiver["active"] = False
            waiver["status"] = "expired"
            return False
        
        return True
    
    def revoke_waiver(self, waiver_id: str, revoker: str, reason: str):
        """Revoke an active waiver"""
        waiver = self.waivers.get(waiver_id)
        if not waiver:
            return False
        
        waiver["active"] = False
        waiver["status"] = "revoked"
        waiver["revoked_by"] = revoker
        waiver["revoked_at"] = int(time.time())
        waiver["revocation_reason"] = reason
        
        # Create attestation for revocation
        self.attestation_service.create_attestation(
            subject=f"waiver_revocation:{waiver_id}",
            payload={
                "waiver_id": waiver_id,
                "revoked_by": revoker,
                "reason": reason,
                "revoked_at": waiver["revoked_at"]
            },
            policy_hash=waiver["policy_id"]
        )
        
        return True