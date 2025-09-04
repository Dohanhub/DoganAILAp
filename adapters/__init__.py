"""
External Module Adapters for DoganAI Compliance Kit
Advanced integration with open-source compliance frameworks
"""

from .openscap_adapter import OpenSCAPAdapter
from .sqlmodel_adapter import SQLModelAdapter
from .hydra_adapter import HydraConfigAdapter
from .compliance_framework_adapter import ComplianceFrameworkAdapter

__all__ = [
    'OpenSCAPAdapter',
    'SQLModelAdapter', 
    'HydraConfigAdapter',
    'ComplianceFrameworkAdapter'
]
