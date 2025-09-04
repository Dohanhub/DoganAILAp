from typing import Dict, List
import os, yaml, hashlib, logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent

class ComplianceError(Exception):
    """Base exception for compliance-related errors"""
    pass

class PolicyNotFoundError(ComplianceError):
    """Raised when a policy file is not found"""
    pass

class VendorNotFoundError(ComplianceError):
    """Raised when a vendor file is not found"""
    pass

class MappingNotFoundError(ComplianceError):
    """Raised when a mapping file is not found"""
    pass

class InvalidDataError(ComplianceError):
    """Raised when YAML data is invalid or corrupted"""
    pass

def _read_yaml(path: Path) -> dict:
    """Read and validate YAML file"""
    try:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        if data is None:
            raise InvalidDataError(f"Empty or invalid YAML file: {path}")
            
        return data
    except yaml.YAMLError as e:
        raise InvalidDataError(f"Invalid YAML syntax in {path}: {str(e)}")
    except Exception as e:
        raise ComplianceError(f"Error reading {path}: {str(e)}")

def load_policy(regulator: str, version: str) -> dict:
    """Load and validate policy file"""
    path = BASE / "policies" / f"{regulator}.yaml"
    try:
        data = _read_yaml(path)
        if data.get('regulator') != regulator or data.get('version') != version:
            raise InvalidDataError(
                f"Policy mismatch: expected {regulator}@{version}, "
                f"got {data.get('regulator')}@{data.get('version')}"
            )
        return data
    except FileNotFoundError:
        raise PolicyNotFoundError(f"Policy not found: {regulator}@{version}")

def load_vendor(filename: str) -> dict:
    """Load and validate vendor file"""
    path = BASE / "vendors" / filename
    try:
        data = _read_yaml(path)
        # Validate required vendor fields
        required_fields = ['vendor', 'solution']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Vendor file {filename} missing required field: {field}")
        return data
    except FileNotFoundError:
        raise VendorNotFoundError(f"Vendor file not found: {filename}")

def load_mapping(name: str) -> dict:
    """Load and validate mapping file"""
    path = BASE / "mappings" / f"{name}.yaml"
    try:
        data = _read_yaml(path)
        # Validate required mapping fields
        required_fields = ['policy_ref', 'vendors']
        for field in required_fields:
            if field not in data:
                raise InvalidDataError(f"Mapping {name} missing required field: {field}")
        return data
    except FileNotFoundError:
        raise MappingNotFoundError(f"Mapping not found: {name}")

def evaluate(mapping_name: str) -> dict:
    """Evaluate compliance mapping with enhanced error handling"""
    try:
        logger.info(f"Starting evaluation for mapping: {mapping_name}")
        
        # Load mapping
        m = load_mapping(mapping_name)
        policy_ref = m['policy_ref']  # e.g., NCA@1.0.0
        
        if '@' not in policy_ref:
            raise InvalidDataError(f"Invalid policy reference format: {policy_ref}. Expected format: regulator@version")
        
        regulator, version = policy_ref.split("@", 1)
        
        # Load policy
        policy = load_policy(regulator, version)
        required = [c['id'] for c in policy.get('controls', [])]
        
        if not required:
            logger.warning(f"No controls found in policy {policy_ref}")
        
        # Process vendors
        provided = set()
        vendor_details = []
        
        for vf in m['vendors']:
            try:
                v = load_vendor(vf)
                vendor_details.append(v)
                for cap in v.get('capabilities', []):
                    if 'control_id' in cap:
                        provided.add(cap['control_id'])
                    else:
                        logger.warning(f"Capability in {vf} missing control_id")
            except VendorNotFoundError as e:
                logger.error(f"Failed to load vendor {vf}: {str(e)}")
                # Continue processing other vendors
                continue
        
        # Calculate compliance
        missing = [cid for cid in required if cid not in provided]
        
        if not missing:
            status = "COMPLIANT"
        elif len(missing) < len(required):
            status = "PARTIAL"
        else:
            status = "GAPS"
        
        # Build result
        payload = {
            "mapping": mapping_name,
            "policy": policy_ref,
            "status": status,
            "required": required,
            "provided": sorted(list(provided)),
            "missing": missing,
            "vendors": [
                {
                    "vendor": vd.get("vendor", "Unknown"),
                    "solution": vd.get("solution", "Unknown")
                } for vd in vendor_details
            ]
        }
        
        # Add metadata
        payload["hash"] = hashlib.sha256(str(payload).encode()).hexdigest()
        
        logger.info(f"Evaluation completed for {mapping_name}: {status}")
        return payload
        
    except (PolicyNotFoundError, VendorNotFoundError, MappingNotFoundError, InvalidDataError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {str(e)}", exc_info=True)
        raise ComplianceError(f"Evaluation failed: {str(e)}")

def get_available_mappings() -> List[str]:
    """Get list of available mapping files"""
    try:
        mappings_dir = BASE / "mappings"
        if not mappings_dir.exists():
            return []
        return [f.stem for f in mappings_dir.glob("*.yaml")]
    except Exception as e:
        logger.error(f"Error listing mappings: {str(e)}")
        return []
