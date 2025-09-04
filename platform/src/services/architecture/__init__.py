"""
Doğan AI Platform - Modular Service Architecture
Cluster-Ready Service-Oriented Design
"""

from .core import ServiceRegistry, ServiceOrchestrator
from .compliance_service import ComplianceService
from .vendor_service import VendorIntegrationService
from .regulatory_service import RegulatoryService
from .customer_service import CustomerService
from .analytics_service import AnalyticsService

__all__ = [
    'ServiceRegistry',
    'ServiceOrchestrator',
    'ComplianceService',
    'VendorIntegrationService',
    'RegulatoryService',
    'CustomerService',
    'AnalyticsService'
]