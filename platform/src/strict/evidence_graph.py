"""
Doğan AI Strict™ Evidence Graph
Content-addressed, immutable evidence storage with cryptographic attestations
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import msgpack

class EvidenceType(Enum):
    """Types of evidence in the graph"""
    SCAN = "scan"
    CONFIG = "config"
    ARTIFACT = "artifact"
    APPROVAL = "approval"
    WAIVER = "waiver"
    VENDOR_ATTESTATION = "vendor_attestation"
    RUNTIME_EVENT = "runtime_event"
    AUDIT_LOG = "audit_log"

class EvidenceRelation(Enum):
    """Types of relationships between evidence"""
    PRODUCED_BY = "produced_by"
    VERIFIES = "verifies"
    SUPERSEDES = "supersedes"
    DEPENDS_ON = "depends_on"
    ATTESTS_TO = "attests_to"
    REVOKES = "revokes"

@dataclass
class Evidence:
    """Immutable evidence entry"""
    id: str
    type: EvidenceType
    content: Dict[str, Any]
    content_hash: str
    timestamp: int
    producer: str
    metadata: Dict[str, Any]
    signature: Optional[bytes] = None
    attestation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
            "producer": self.producer,
            "metadata": self.metadata,
            "attestation_id": self.attestation_id
        }
    
    @staticmethod
    def compute_hash(content: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of content"""
        content_bytes = msgpack.packb(content, use_bin_type=True)
        return hashlib.sha256(content_bytes).hexdigest()

class MerkleTree:
    """Merkle tree for tamper-evident logging"""
    
    def __init__(self):
        self.leaves = []
        self.root = None
        
    def add_leaf(self, data: bytes) -> int:
        """Add a leaf to the tree"""
        leaf_hash = hashlib.sha256(data).digest()
        index = len(self.leaves)
        self.leaves.append(leaf_hash)
        return index
    
    def compute_root(self) -> bytes:
        """Compute the Merkle root"""
        if not self.leaves:
            return b""
        
        if len(self.leaves) == 1:
            self.root = self.leaves[0]
            return self.root
        
        # Build tree level by level
        current_level = self.leaves.copy()
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                
                next_level.append(hashlib.sha256(combined).digest())
            
            current_level = next_level
        
        self.root = current_level[0]
        return self.root
    
    def get_proof(self, index: int) -> List[bytes]:
        """Get Merkle proof for a leaf"""
        if index >= len(self.leaves):
            raise ValueError("Index out of range")
        
        proof = []
        current_index = index
        current_level = self.leaves.copy()
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i == current_index or i + 1 == current_index:
                    # Add sibling to proof
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

class EvidenceGraph:
    """
    Content-addressed evidence graph with cryptographic guarantees
    Implements tamper-evident storage with Merkle trees
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.evidence_store = {}
        self.merkle_tree = MerkleTree()
        self.merkle_roots = []  # Chain of Merkle roots
        self.signing_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.signing_key.public_key()
        self.tombstones = {}  # For redacted evidence
        
    def add_evidence(self, 
                    evidence_type: EvidenceType,
                    content: Dict[str, Any],
                    producer: str,
                    metadata: Optional[Dict[str, Any]] = None) -> Evidence:
        """Add new evidence to the graph"""
        # Compute content hash
        content_hash = Evidence.compute_hash(content)
        
        # Check for duplicates
        if content_hash in self.evidence_store:
            return self.evidence_store[content_hash]
        
        # Create evidence entry
        evidence = Evidence(
            id=content_hash[:16],  # Use first 16 chars as ID
            type=evidence_type,
            content=content,
            content_hash=content_hash,
            timestamp=int(time.time()),
            producer=producer,
            metadata=metadata or {}
        )
        
        # Sign evidence
        evidence_bytes = msgpack.packb(evidence.to_dict(), use_bin_type=True)
        evidence.signature = self.signing_key.sign(evidence_bytes)
        
        # Add to Merkle tree
        merkle_index = self.merkle_tree.add_leaf(evidence_bytes)
        evidence.metadata["merkle_index"] = merkle_index
        
        # Store evidence
        self.evidence_store[content_hash] = evidence
        self.graph.add_node(content_hash, evidence=evidence)
        
        return evidence
    
    def add_relation(self,
                    from_evidence: str,
                    to_evidence: str,
                    relation: EvidenceRelation,
                    metadata: Optional[Dict[str, Any]] = None):
        """Add a relationship between evidence"""
        if from_evidence not in self.evidence_store:
            raise ValueError(f"Evidence {from_evidence} not found")
        if to_evidence not in self.evidence_store:
            raise ValueError(f"Evidence {to_evidence} not found")
        
        self.graph.add_edge(
            from_evidence,
            to_evidence,
            relation=relation,
            metadata=metadata or {},
            timestamp=int(time.time())
        )
    
    def get_evidence(self, content_hash: str) -> Optional[Evidence]:
        """Retrieve evidence by content hash"""
        return self.evidence_store.get(content_hash)
    
    def query_evidence(self,
                      evidence_type: Optional[EvidenceType] = None,
                      producer: Optional[str] = None,
                      since_timestamp: Optional[int] = None,
                      metadata_filter: Optional[Dict[str, Any]] = None) -> List[Evidence]:
        """Query evidence with filters"""
        results = []
        
        for evidence in self.evidence_store.values():
            # Apply filters
            if evidence_type and evidence.type != evidence_type:
                continue
            if producer and evidence.producer != producer:
                continue
            if since_timestamp and evidence.timestamp < since_timestamp:
                continue
            if metadata_filter:
                if not all(evidence.metadata.get(k) == v for k, v in metadata_filter.items()):
                    continue
            
            results.append(evidence)
        
        return sorted(results, key=lambda e: e.timestamp, reverse=True)
    
    def get_lineage(self, content_hash: str) -> Dict[str, Any]:
        """Get full lineage of evidence"""
        if content_hash not in self.evidence_store:
            raise ValueError(f"Evidence {content_hash} not found")
        
        # Get ancestors (what this evidence depends on)
        ancestors = list(nx.ancestors(self.graph, content_hash))
        
        # Get descendants (what depends on this evidence)
        descendants = list(nx.descendants(self.graph, content_hash))
        
        # Get immediate relationships
        predecessors = list(self.graph.predecessors(content_hash))
        successors = list(self.graph.successors(content_hash))
        
        return {
            "evidence": self.evidence_store[content_hash].to_dict(),
            "ancestors": [self.evidence_store[h].to_dict() for h in ancestors],
            "descendants": [self.evidence_store[h].to_dict() for h in descendants],
            "immediate_dependencies": predecessors,
            "immediate_dependents": successors
        }
    
    def verify_evidence(self, content_hash: str) -> Dict[str, Any]:
        """Verify evidence integrity and signature"""
        evidence = self.evidence_store.get(content_hash)
        if not evidence:
            return {"valid": False, "reason": "Evidence not found"}
        
        # Verify content hash
        computed_hash = Evidence.compute_hash(evidence.content)
        if computed_hash != evidence.content_hash:
            return {"valid": False, "reason": "Content hash mismatch"}
        
        # Verify signature
        if evidence.signature:
            evidence_bytes = msgpack.packb(evidence.to_dict(), use_bin_type=True)
            try:
                self.public_key.verify(evidence.signature, evidence_bytes)
            except:
                return {"valid": False, "reason": "Invalid signature"}
        
        # Verify Merkle inclusion
        if "merkle_index" in evidence.metadata:
            # Would verify against Merkle root here
            pass
        
        return {
            "valid": True,
            "content_hash": evidence.content_hash,
            "timestamp": evidence.timestamp,
            "producer": evidence.producer
        }
    
    def redact_evidence(self, content_hash: str, reason: str, authorized_by: str):
        """Redact evidence while maintaining audit trail"""
        if content_hash not in self.evidence_store:
            raise ValueError(f"Evidence {content_hash} not found")
        
        evidence = self.evidence_store[content_hash]
        
        # Create tombstone
        tombstone = {
            "original_hash": content_hash,
            "redacted_at": int(time.time()),
            "reason": reason,
            "authorized_by": authorized_by,
            "evidence_type": evidence.type.value,
            "original_producer": evidence.producer
        }
        
        # Add tombstone to graph
        tombstone_hash = Evidence.compute_hash(tombstone)
        self.tombstones[content_hash] = tombstone
        
        # Add redaction evidence
        self.add_evidence(
            evidence_type=EvidenceType.AUDIT_LOG,
            content={
                "action": "redaction",
                "target": content_hash,
                "tombstone": tombstone_hash,
                "reason": reason
            },
            producer="system",
            metadata={"authorized_by": authorized_by}
        )
        
        # Remove original content but keep metadata
        evidence.content = {"redacted": True}
        evidence.metadata["redacted"] = True
        evidence.metadata["tombstone"] = tombstone_hash
    
    def finalize_batch(self) -> Dict[str, Any]:
        """Finalize current batch and compute Merkle root"""
        if not self.merkle_tree.leaves:
            return {"status": "no_evidence_to_finalize"}
        
        # Compute Merkle root
        root = self.merkle_tree.compute_root()
        root_hex = root.hex()
        
        # Chain with previous root if exists
        if self.merkle_roots:
            previous_root = self.merkle_roots[-1]["root"]
            chained_data = previous_root.encode() + root
            chained_hash = hashlib.sha256(chained_data).hexdigest()
        else:
            chained_hash = root_hex
        
        # Store root with metadata
        root_entry = {
            "root": root_hex,
            "chained_hash": chained_hash,
            "timestamp": int(time.time()),
            "leaf_count": len(self.merkle_tree.leaves),
            "batch_number": len(self.merkle_roots)
        }
        
        self.merkle_roots.append(root_entry)
        
        # Reset tree for next batch
        self.merkle_tree = MerkleTree()
        
        return root_entry
    
    def export_graph(self) -> Dict[str, Any]:
        """Export the entire evidence graph"""
        nodes = []
        edges = []
        
        for node in self.graph.nodes():
            evidence = self.evidence_store[node]
            nodes.append(evidence.to_dict())
        
        for edge in self.graph.edges(data=True):
            edges.append({
                "from": edge[0],
                "to": edge[1],
                "relation": edge[2].get("relation").value if edge[2].get("relation") else None,
                "metadata": edge[2].get("metadata", {})
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "merkle_roots": self.merkle_roots,
            "tombstones": list(self.tombstones.values())
        }