
'\nCompliance evaluation engine\n'
import yaml
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from core.database import get_db_service
from models import ComplianceCache, AuditLog
from src.core.settings import Settings
logger = logging.getLogger(__name__)

class ComplianceEngine():
    'Main compliance evaluation engine'

    def __init__(self):
        self.settings = Settings()
        self.mappings_dir = Path('mappings')
        self.policies_dir = Path('policies')
        self.vendors_dir = Path('vendors')

    async def get_available_mappings(self) -> List[str]:
        'Get list of available mapping files'
        try:
            if (not self.mappings_dir.exists()):
                logger.warning(f'Mappings directory not found: {self.mappings_dir}')
                return []
            mappings = []
            for file_path in self.mappings_dir.glob('*.yaml'):
                if file_path.is_file():
                    mappings.append(file_path.stem)
            return sorted(mappings)
        except Exception as e:
            logger.error(f'Failed to list mappings: {e}')
            return []

    async def get_available_policies(self) -> List[str]:
        'Get list of available policy files'
        try:
            if (not self.policies_dir.exists()):
                return []
            policies = []
            for file_path in self.policies_dir.glob('*.yaml'):
                if file_path.is_file():
                    policies.append(file_path.stem)
            return sorted(policies)
        except Exception as e:
            logger.error(f'Failed to list policies: {e}')
            return []

    async def get_available_vendors(self) -> List[str]:
        'Get list of available vendor files'
        try:
            if (not self.vendors_dir.exists()):
                return []
            vendors = []
            for file_path in self.vendors_dir.glob('*.yaml'):
                if file_path.is_file():
                    vendors.append(file_path.stem)
            return sorted(vendors)
        except Exception as e:
            logger.error(f'Failed to list vendors: {e}')
            return []

    async def evaluate_mapping(self, mapping_name: str, force_refresh: bool=False) -> Dict[(str, Any)]:
        'Evaluate compliance for a mapping'
        try:
            logger.info(f'Starting evaluation for mapping: {mapping_name}')
            mapping_path = (self.mappings_dir / f'{mapping_name}.yaml')
            if (not mapping_path.exists()):
                raise FileNotFoundError(f'Mapping file not found: {mapping_path}')
            with open(mapping_path, 'r', encoding='utf-8') as f:
                mapping_data = yaml.safe_load(f)
            if (not force_refresh):
                cached_result = (await self.get_cached_result(mapping_name))
                if cached_result:
                    logger.info(f'Returning cached result for {mapping_name}')
                    return cached_result
            policy_ref = mapping_data.get('policy_ref', '')
            policy_data = (await self._load_policy(policy_ref))
            vendor_files = mapping_data.get('vendors', [])
            vendor_data = (await self._load_vendors(vendor_files))
            evaluation_result = (await self._perform_evaluation(mapping_data, policy_data, vendor_data))
            (await self._cache_result(mapping_name, evaluation_result))
            (await self._log_audit(mapping_name, evaluation_result))
            logger.info(f'Evaluation completed for {mapping_name}')
            return evaluation_result
        except Exception as e:
            logger.error(f'Evaluation failed for {mapping_name}: {e}')
            raise

    async def get_cached_result(self, mapping_name: str) -> Optional[Dict[(str, Any)]]:
        'Get cached evaluation result'
        try:
            db_service = get_db_service()
            with db_service.get_session() as session:
                cached = session.query(ComplianceCache).filter((ComplianceCache.mapping_name == mapping_name), (ComplianceCache.is_valid == True)).first()
                if cached:
                    return cached.evaluation_data
        except Exception as e:
            logger.error(f'Failed to get cached result: {e}')
        return None

    async def _load_policy(self, policy_ref: str) -> Dict[(str, Any)]:
        'Load policy file'
        try:
            policy_path = (self.policies_dir / f'{policy_ref}.yaml')
            if (not policy_path.exists()):
                logger.warning(f'Policy file not found: {policy_path}')
                return {'controls': []}
            with open(policy_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f'Failed to load policy {policy_ref}: {e}')
            return {'controls': []}

    async def _load_vendors(self, vendor_files: List[str]) -> List[Dict[(str, Any)]]:
        'Load vendor files'
        vendors = []
        for vendor_file in vendor_files:
            try:
                vendor_path = (self.vendors_dir / vendor_file)
                if (not vendor_path.exists()):
                    logger.warning(f'Vendor file not found: {vendor_path}')
                    continue
                with open(vendor_path, 'r', encoding='utf-8') as f:
                    vendor_data = yaml.safe_load(f)
                    vendors.append(vendor_data)
            except Exception as e:
                logger.error(f'Failed to load vendor {vendor_file}: {e}')
        return vendors

    async def _perform_evaluation(self, mapping_data: Dict[(str, Any)], policy_data: Dict[(str, Any)], vendor_data: List[Dict[(str, Any)]]) -> Dict[(str, Any)]:
        'Perform the actual compliance evaluation'
        policy_controls = policy_data.get('controls', [])
        required_controls = {control['id']: control for control in policy_controls}
        provided_capabilities = {}
        for vendor in vendor_data:
            capabilities = vendor.get('capabilities', [])
            for capability in capabilities:
                control_id = capability.get('control_id')
                if control_id:
                    provided_capabilities[control_id] = capability
        missing_controls = []
        covered_controls = []
        for (control_id, control) in required_controls.items():
            if (control_id in provided_capabilities):
                covered_controls.append({'control_id': control_id, 'title': control.get('title', ''), 'vendor_capability': provided_capabilities[control_id]})
            else:
                missing_controls.append({'control_id': control_id, 'title': control.get('title', ''), 'description': control.get('description', '')})
        total_controls = len(required_controls)
        covered_count = len(covered_controls)
        missing_count = len(missing_controls)
        coverage_percentage = (((covered_count / total_controls) * 100) if (total_controls > 0) else 0)
        if (coverage_percentage >= 90):
            status = 'COMPLIANT'
        elif (coverage_percentage >= 70):
            status = 'GAPS'
        else:
            status = 'NON_COMPLIANT'
        return {'status': status, 'mapping_name': mapping_data.get('mapping', mapping_data.get('name', 'Unknown')), 'policy_ref': mapping_data.get('policy_ref', ''), 'sector': mapping_data.get('sector', 'Unknown'), 'timestamp': datetime.now(timezone.utc).isoformat(), 'summary': {'total_controls': total_controls, 'covered_controls': covered_count, 'missing_controls': missing_count, 'coverage_percentage': round(coverage_percentage, 2)}, 'details': {'required': list(required_controls.values()), 'provided': covered_controls, 'missing': missing_controls}}

    async def _cache_result(self, mapping_name: str, result: Dict[(str, Any)]):
        'Cache evaluation result'
        try:
            db_service = get_db_service()
            result_str = str(sorted(result.items()))
            result_hash = hashlib.sha256(result_str.encode()).hexdigest()
            with db_service.get_session() as session:
                session.query(ComplianceCache).filter((ComplianceCache.mapping_name == mapping_name)).delete()
                cache_entry = ComplianceCache(mapping_name=mapping_name, policy_ref=result.get('policy_ref', ''), result_hash=result_hash, evaluation_data=result)
                session.add(cache_entry)
        except Exception as e:
            logger.error(f'Failed to cache result: {e}')

    async def _log_audit(self, mapping_name: str, result: Dict[(str, Any)]):
        'Log audit entry'
        try:
            if (not self.settings.enable_audit_logging):
                return
            db_service = get_db_service()
            result_str = str(sorted(result.items()))
            result_hash = hashlib.sha256(result_str.encode()).hexdigest()
            with db_service.get_session() as session:
                audit_entry = AuditLog(mapping_name=mapping_name, policy_ref=result.get('policy_ref', ''), status=result.get('status', 'UNKNOWN'), result_hash=result_hash, evaluation_data=result, user_id=None, session_id=None)
                session.add(audit_entry)
        except Exception as e:
            logger.error(f'Failed to log audit: {e}')

# Standalone functions for external use
def get_available_mappings() -> List[str]:
    """Get list of available mapping files (standalone function)"""
    try:
        mappings_dir = Path('mappings')
        if not mappings_dir.exists():
            logger.warning(f'Mappings directory not found: {mappings_dir}')
            return []
        mappings = []
        for file_path in mappings_dir.glob('*.yaml'):
            if file_path.is_file():
                mappings.append(file_path.stem)
        return sorted(mappings)
    except Exception as e:
        logger.error(f'Failed to list mappings: {e}')
        return []
