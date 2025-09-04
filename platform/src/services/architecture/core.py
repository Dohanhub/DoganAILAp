"""
Core Service Architecture Components
Enables cluster deployment and service orchestration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import json
from datetime import datetime
from enum import Enum

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"

class ServiceType(Enum):
    """Types of services in the ecosystem"""
    COMPLIANCE = "compliance"
    VENDOR = "vendor"
    REGULATORY = "regulatory"
    CUSTOMER = "customer"
    ANALYTICS = "analytics"
    GATEWAY = "gateway"
    ORCHESTRATOR = "orchestrator"

@dataclass
class ServiceMetadata:
    """Service identification and metadata"""
    name: str
    type: ServiceType
    version: str
    instance_id: str
    cluster_node: str
    capabilities: List[str]
    dependencies: List[str]
    api_endpoints: Dict[str, str]
    sla_targets: Dict[str, float]

class BaseService(ABC):
    """
    Base class for all modular services
    Each service can run independently or in a cluster
    """
    
    def __init__(self, metadata: ServiceMetadata):
        self.metadata = metadata
        self.status = ServiceStatus.STARTING
        self.health_metrics = {}
        self.connections = {}
        self.message_queue = asyncio.Queue()
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize service with health checks"""
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming service request"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform service health check"""
        pass
    
    async def start(self):
        """Start the service"""
        try:
            success = await self.initialize()
            if success:
                self.status = ServiceStatus.HEALTHY
                return True
        except Exception as e:
            self.status = ServiceStatus.UNHEALTHY
            raise e
    
    async def stop(self):
        """Gracefully stop the service"""
        self.status = ServiceStatus.STOPPING
        await self._cleanup()
        self.status = ServiceStatus.UNHEALTHY
    
    async def _cleanup(self):
        """Clean up resources"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            "service": self.metadata.name,
            "status": self.status.value,
            "health": self.health_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

class ServiceRegistry:
    """
    Central registry for all services in the cluster
    Enables service discovery and load balancing
    """
    
    def __init__(self):
        self.services: Dict[str, List[BaseService]] = {}
        self.service_map: Dict[str, ServiceMetadata] = {}
        self.load_balancer_config = {}
        
    def register(self, service: BaseService) -> bool:
        """Register a service in the cluster"""
        service_type = service.metadata.type.value
        
        if service_type not in self.services:
            self.services[service_type] = []
            
        self.services[service_type].append(service)
        self.service_map[service.metadata.instance_id] = service.metadata
        return True
    
    def discover(self, service_type: ServiceType) -> List[BaseService]:
        """Discover available services of a specific type"""
        return self.services.get(service_type.value, [])
    
    def get_healthy_services(self, service_type: ServiceType) -> List[BaseService]:
        """Get only healthy services for load balancing"""
        services = self.discover(service_type)
        return [s for s in services if s.status == ServiceStatus.HEALTHY]
    
    def get_service_by_id(self, instance_id: str) -> Optional[BaseService]:
        """Get specific service instance"""
        for service_list in self.services.values():
            for service in service_list:
                if service.metadata.instance_id == instance_id:
                    return service
        return None

class ServiceOrchestrator:
    """
    Orchestrates communication between services
    Handles routing, load balancing, and failover
    """
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.routing_rules = {}
        self.circuit_breakers = {}
        self.request_count = 0
        
    async def route_request(self, 
                          service_type: ServiceType, 
                          request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate service with load balancing"""
        services = self.registry.get_healthy_services(service_type)
        
        if not services:
            raise Exception(f"No healthy {service_type.value} services available")
        
        # Round-robin load balancing
        service = services[self.request_count % len(services)]
        self.request_count += 1
        
        try:
            response = await service.process_request(request)
            return response
        except Exception as e:
            # Failover to next available service
            for backup_service in services:
                if backup_service != service:
                    try:
                        return await backup_service.process_request(request)
                    except:
                        continue
            raise e
    
    async def orchestrate_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Orchestrate complex multi-service workflows"""
        results = []
        context = {}
        
        for step in workflow:
            service_type = ServiceType(step['service'])
            request = step.get('request', {})
            request['context'] = context
            
            result = await self.route_request(service_type, request)
            results.append(result)
            
            # Update context for next step
            if 'output_key' in step:
                context[step['output_key']] = result
        
        return {
            "workflow_results": results,
            "final_context": context
        }
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster health and status"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "total_requests": self.request_count
        }
        
        for service_type, services in self.registry.services.items():
            status["services"][service_type] = {
                "total": len(services),
                "healthy": len([s for s in services if s.status == ServiceStatus.HEALTHY]),
                "degraded": len([s for s in services if s.status == ServiceStatus.DEGRADED]),
                "unhealthy": len([s for s in services if s.status == ServiceStatus.UNHEALTHY])
            }
        
        return status

class MessageBroker:
    """
    Inter-service communication broker
    Enables async messaging between services
    """
    
    def __init__(self):
        self.topics: Dict[str, List[asyncio.Queue]] = {}
        self.subscribers: Dict[str, List[BaseService]] = {}
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish message to a topic"""
        if topic not in self.topics:
            self.topics[topic] = []
        
        for queue in self.topics[topic]:
            await queue.put(message)
    
    def subscribe(self, service: BaseService, topic: str):
        """Subscribe service to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
            self.topics[topic] = []
        
        self.subscribers[topic].append(service)
        queue = asyncio.Queue()
        self.topics[topic].append(queue)
        return queue
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all services"""
        for topic in self.topics:
            await self.publish(topic, message)