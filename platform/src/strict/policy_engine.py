"""
Doğan AI Strict™ Policy Engine
WASM-based deterministic policy evaluation with sub-50ms p95 latency
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import wasmtime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import redis
import msgpack

class PolicyDecision(Enum):
    """Policy evaluation decisions"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    REQUIRE_ATTESTATION = "require_attestation"

@dataclass
class EvidenceReference:
    """Reference to evidence in the graph"""
    hash: str
    type: str
    timestamp: int
    attestation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PolicyResult:
    """Result of policy evaluation"""
    decision: PolicyDecision
    reasons: List[str]
    evidence_refs: List[EvidenceReference]
    policy_hash: str
    evaluation_time_ms: float
    deterministic_hash: str
    
    def to_dict(self) -> Dict:
        return {
            "decision": self.decision.value,
            "reasons": self.reasons,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
            "policy_hash": self.policy_hash,
            "evaluation_time_ms": self.evaluation_time_ms,
            "deterministic_hash": self.deterministic_hash
        }

class AdlyDSLCompiler:
    """Compiles Adly-DSL to WASM for deterministic execution"""
    
    def __init__(self):
        self.wasm_store = wasmtime.Store()
        self.wasm_engine = wasmtime.Engine()
        self.compiled_policies = {}
        
    def compile_policy(self, policy_dsl: str) -> bytes:
        """
        Compile Adly-DSL to WASM module
        Returns WASM bytecode for deterministic execution
        """
        # Parse DSL
        policy_hash = hashlib.sha256(policy_dsl.encode()).hexdigest()
        
        # Generate WASM (simplified - in production use a real compiler)
        # This is a placeholder for the actual DSL->IR->WASM compilation
        wat_code = f"""
        (module
          (func $evaluate (param i32 i32) (result i32)
            ;; Policy logic compiled from DSL
            ;; Returns 1 for allow, 0 for deny
            local.get 0
            i32.const 1
            i32.eq
          )
          (export "evaluate" (func $evaluate))
        )
        """
        
        # Compile WAT to WASM
        wasm_module = wasmtime.Module(self.wasm_engine, wat_code)
        wasm_bytes = wasm_module.serialize()
        
        self.compiled_policies[policy_hash] = wasm_module
        return wasm_bytes

class PolicyEngine:
    """
    High-performance policy engine with WASM runtime
    Targets p95 < 50ms evaluation time
    """
    
    def __init__(self, cache_host: str = "localhost", cache_port: int = 6379):
        self.compiler = AdlyDSLCompiler()
        self.cache = redis.Redis(host=cache_host, port=cache_port, decode_responses=False)
        self.wasm_store = wasmtime.Store()
        self.loaded_policies = {}
        self.signing_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.signing_key.public_key()
        
    def load_policy(self, policy_id: str, policy_dsl: str) -> str:
        """Load and compile policy to WASM"""
        start_time = time.perf_counter()
        
        # Check cache first
        policy_hash = hashlib.sha256(policy_dsl.encode()).hexdigest()
        cached_wasm = self.cache.get(f"policy:wasm:{policy_hash}")
        
        if cached_wasm:
            wasm_bytes = cached_wasm
        else:
            # Compile to WASM
            wasm_bytes = self.compiler.compile_policy(policy_dsl)
            # Cache compiled WASM
            self.cache.setex(f"policy:wasm:{policy_hash}", 3600, wasm_bytes)
        
        # Load into runtime
        wasm_module = wasmtime.Module.deserialize(self.wasm_store.engine, wasm_bytes)
        instance = wasmtime.Instance(self.wasm_store, wasm_module, [])
        
        self.loaded_policies[policy_id] = {
            "instance": instance,
            "hash": policy_hash,
            "dsl": policy_dsl
        }
        
        load_time = (time.perf_counter() - start_time) * 1000
        print(f"Policy {policy_id} loaded in {load_time:.2f}ms")
        
        return policy_hash
    
    def evaluate(self, 
                policy_id: str, 
                context: Dict[str, Any],
                evidence: List[EvidenceReference]) -> PolicyResult:
        """
        Evaluate policy against context with evidence
        Deterministic execution with performance guarantee
        """
        start_time = time.perf_counter()
        
        if policy_id not in self.loaded_policies:
            raise ValueError(f"Policy {policy_id} not loaded")
        
        policy = self.loaded_policies[policy_id]
        
        # Serialize context for deterministic hashing
        context_bytes = msgpack.packb(context, use_bin_type=True)
        context_hash = hashlib.sha256(context_bytes).hexdigest()
        
        # Check result cache for determinism
        cache_key = f"eval:{policy['hash']}:{context_hash}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            # Deserialize cached result
            result_data = msgpack.unpackb(cached_result, raw=False)
            evaluation_time = (time.perf_counter() - start_time) * 1000
            
            return PolicyResult(
                decision=PolicyDecision(result_data["decision"]),
                reasons=result_data["reasons"],
                evidence_refs=[EvidenceReference(**ref) for ref in result_data["evidence_refs"]],
                policy_hash=policy["hash"],
                evaluation_time_ms=evaluation_time,
                deterministic_hash=result_data["deterministic_hash"]
            )
        
        # Execute WASM policy (simplified - real implementation would pass context)
        wasm_instance = policy["instance"]
        evaluate_func = wasm_instance.exports(self.wasm_store)["evaluate"]
        
        # Convert context to WASM-compatible format
        # In production, this would properly serialize and pass context
        result_code = evaluate_func(self.wasm_store, 1, 0)
        
        # Determine decision based on result
        if result_code == 1:
            decision = PolicyDecision.ALLOW
            reasons = ["Policy conditions met"]
        elif result_code == 0:
            decision = PolicyDecision.DENY
            reasons = ["Policy conditions not met"]
        else:
            decision = PolicyDecision.REQUIRE_ATTESTATION
            reasons = ["Additional attestation required"]
        
        # Create deterministic hash of result
        result_data = {
            "decision": decision.value,
            "reasons": reasons,
            "evidence_refs": [ref.to_dict() for ref in evidence],
            "policy_hash": policy["hash"],
            "context_hash": context_hash
        }
        
        deterministic_hash = hashlib.sha256(
            msgpack.packb(result_data, use_bin_type=True)
        ).hexdigest()
        
        evaluation_time = (time.perf_counter() - start_time) * 1000
        
        result = PolicyResult(
            decision=decision,
            reasons=reasons,
            evidence_refs=evidence,
            policy_hash=policy["hash"],
            evaluation_time_ms=evaluation_time,
            deterministic_hash=deterministic_hash
        )
        
        # Cache result for determinism
        cache_data = {
            "decision": result.decision.value,
            "reasons": result.reasons,
            "evidence_refs": [ref.to_dict() for ref in result.evidence_refs],
            "deterministic_hash": result.deterministic_hash
        }
        
        self.cache.setex(
            cache_key, 
            300,  # 5 minute TTL
            msgpack.packb(cache_data, use_bin_type=True)
        )
        
        # Log performance metrics
        if evaluation_time > 50:
            print(f"WARNING: Policy evaluation took {evaluation_time:.2f}ms (target: <50ms)")
        
        return result
    
    def sign_result(self, result: PolicyResult) -> bytes:
        """Sign policy result with Ed25519"""
        result_bytes = msgpack.packb(result.to_dict(), use_bin_type=True)
        signature = self.signing_key.sign(result_bytes)
        return signature
    
    def verify_signature(self, result: PolicyResult, signature: bytes) -> bool:
        """Verify Ed25519 signature of policy result"""
        result_bytes = msgpack.packb(result.to_dict(), use_bin_type=True)
        try:
            self.public_key.verify(signature, result_bytes)
            return True
        except:
            return False

class PolicyRepository:
    """Repository for managing policies with versioning"""
    
    def __init__(self, engine: PolicyEngine):
        self.engine = engine
        self.policies = {}
        self.policy_versions = {}
        
    def add_policy(self, policy_id: str, policy_dsl: str, version: str = "1.0.0"):
        """Add a new policy or version"""
        if policy_id not in self.policy_versions:
            self.policy_versions[policy_id] = []
        
        policy_hash = self.engine.load_policy(f"{policy_id}:{version}", policy_dsl)
        
        self.policies[f"{policy_id}:{version}"] = {
            "dsl": policy_dsl,
            "hash": policy_hash,
            "version": version,
            "created_at": time.time()
        }
        
        self.policy_versions[policy_id].append(version)
        return policy_hash
    
    def get_policy(self, policy_id: str, version: Optional[str] = None) -> Dict:
        """Get policy by ID and optional version"""
        if version:
            key = f"{policy_id}:{version}"
        else:
            # Get latest version
            if policy_id not in self.policy_versions:
                raise ValueError(f"Policy {policy_id} not found")
            latest_version = sorted(self.policy_versions[policy_id])[-1]
            key = f"{policy_id}:{latest_version}"
        
        return self.policies.get(key)

# Saudi-specific compliance policies
SAUDI_COMPLIANCE_POLICIES = {
    "nca_data_residency": """
        rule DataMustRemainInSaudi when data.classification in ["critical", "sensitive"] {
            require data.storage.region == "saudi-arabia"
            require data.processing.region == "saudi-arabia"
            require data.backup.region == "saudi-arabia"
        }
    """,
    
    "sama_encryption": """
        rule FinancialDataEncryption when data.type == "financial" {
            require data.encryption.algorithm in ["AES-256", "RSA-4096"]
            require data.encryption.key_management == "hsm"
            require data.encryption.key_rotation_days <= 90
        }
    """,
    
    "pdpl_consent": """
        rule PersonalDataConsent when data.contains_pii == true {
            require data.consent.obtained == true
            require data.consent.purpose != null
            require data.consent.retention_days <= 365
            require data.consent.withdrawal_enabled == true
        }
    """,
    
    "waiver_timeboxed": """
        rule WaiverMustExpire when waiver.active == true {
            require waiver.expires_at != null
            require now() < waiver.expires_at
            require waiver.dual_approval == true
            require waiver.max_duration_days <= 30
        }
    """
}