"""
Elasticsearch manager for advanced search capabilities
Full-text search, analytics, and search optimization
"""

import os
import logging
import time
import threading
import json
from typing import Optional, Any, Dict, List, Union, Generator
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError, NotFoundError, TransportError
from elasticsearch_dsl import Search, Q, A
import structlog
from collections import defaultdict

from .settings import settings

logger = structlog.get_logger(__name__)

# =============================================================================
# ELASTICSEARCH MANAGER
# =============================================================================

class ElasticsearchManager:
    """Advanced Elasticsearch manager with search, indexing, and analytics"""
    
    def __init__(self):
        self.es_client: Optional[Elasticsearch] = None
        self._lock = threading.Lock()
        self._health_status = "unknown"
        self._last_health_check = None
        self._health_check_interval = 60  # seconds
        self._connection_errors = 0
        self._max_connection_errors = 5
        self._search_metrics = defaultdict(int)
        self._last_metrics_reset = datetime.now(timezone.utc)
        self._metrics_reset_interval = 3600  # 1 hour
        
        # Index configuration
        self._index_prefix = "doganai"
        self._compliance_index = f"{self._index_prefix}-compliance"
        self._audit_index = f"{self._index_prefix}-audit"
        self._documents_index = f"{self._index_prefix}-documents"
        self._users_index = f"{self._index_prefix}-users"
        
        # Search configuration
        self._default_size = 20
        self._max_size = 1000
        self._search_timeout = "30s"
        
    def initialize(self) -> bool:
        """Initialize Elasticsearch connection and indices"""
        try:
            with self._lock:
                if self.es_client is not None:
                    logger.info("Elasticsearch already initialized")
                    return True
                
                # Create Elasticsearch client
                self._create_client()
                
                # Test connection
                if not self._test_connection():
                    raise Exception("Failed to establish Elasticsearch connection")
                
                # Create indices
                if not self._create_indices():
                    raise Exception("Failed to create Elasticsearch indices")
                
                # Set up index mappings
                if not self._setup_index_mappings():
                    raise Exception("Failed to setup index mappings")
                
                logger.info(
                    "Elasticsearch initialized successfully",
                    host=settings.elasticsearch.host,
                    port=settings.elasticsearch.port,
                    indices=[self._compliance_index, self._audit_index, self._documents_index, self._users_index]
                )
                
                return True
                
        except Exception as e:
            logger.error(
                "Failed to initialize Elasticsearch",
                error=str(e),
                host=settings.elasticsearch.host,
                port=settings.elasticsearch.port,
                exc_info=True
            )
            return False
    
    def _create_client(self):
        """Create Elasticsearch client with advanced configuration"""
        hosts = [f"{settings.elasticsearch.host}:{settings.elasticsearch.port}"]
        
        # Build connection configuration
        connection_config = {
            "hosts": hosts,
            "timeout": 30,
            "max_retries": 3,
            "retry_on_timeout": True,
            "sniff_on_start": True,
            "sniff_on_connection_fail": True,
            "sniffer_timeout": 60,
            "http_compress": True,
            "verify_certs": settings.elasticsearch.verify_certs,
            "ssl_show_warn": False
        }
        
        # Add authentication if configured
        if settings.elasticsearch.username and settings.elasticsearch.password:
            connection_config["basic_auth"] = (
                settings.elasticsearch.username,
                settings.elasticsearch.password
            )
        
        # Add SSL configuration if enabled
        if settings.elasticsearch.use_ssl:
            connection_config["use_ssl"] = True
            if settings.elasticsearch.ca_certs:
                connection_config["ca_certs"] = settings.elasticsearch.ca_certs
        
        self.es_client = Elasticsearch(**connection_config)
    
    def _test_connection(self) -> bool:
        """Test Elasticsearch connection"""
        try:
            info = self.es_client.info()
            logger.info("Elasticsearch connection test successful", version=info.get("version", {}).get("number"))
            return True
        except Exception as e:
            logger.error("Elasticsearch connection test failed", error=str(e))
            return False
    
    def _create_indices(self) -> bool:
        """Create Elasticsearch indices"""
        try:
            indices = [self._compliance_index, self._audit_index, self._documents_index, self._users_index]
            
            for index in indices:
                if not self.es_client.indices.exists(index=index):
                    self.es_client.indices.create(
                        index=index,
                        body={
                            "settings": {
                                "number_of_shards": 1,
                                "number_of_replicas": 1,
                                "analysis": {
                                    "analyzer": {
                                        "compliance_analyzer": {
                                            "type": "custom",
                                            "tokenizer": "standard",
                                            "filter": ["lowercase", "stop", "snowball"]
                                        }
                                    }
                                }
                            }
                        }
                    )
                    logger.info(f"Created Elasticsearch index: {index}")
                else:
                    logger.info(f"Elasticsearch index already exists: {index}")
            
            return True
            
        except Exception as e:
            logger.error("Failed to create Elasticsearch indices", error=str(e))
            return False
    
    def _setup_index_mappings(self) -> bool:
        """Setup index mappings for better search"""
        try:
            # Compliance index mapping
            compliance_mapping = {
                "properties": {
                    "entity_id": {"type": "keyword"},
                    "compliance_type": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "compliance_analyzer"},
                    "description": {"type": "text", "analyzer": "compliance_analyzer"},
                    "details": {"type": "object"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
            
            # Audit index mapping
            audit_mapping = {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "action": {"type": "keyword"},
                    "resource_type": {"type": "keyword"},
                    "resource_id": {"type": "keyword"},
                    "changes": {"type": "object"},
                    "ip_address": {"type": "ip"},
                    "user_agent": {"type": "text"},
                    "timestamp": {"type": "date"}
                }
            }
            
            # Documents index mapping
            documents_mapping = {
                "properties": {
                    "title": {"type": "text", "analyzer": "compliance_analyzer"},
                    "content": {"type": "text", "analyzer": "compliance_analyzer"},
                    "document_type": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
            
            # Users index mapping
            users_mapping = {
                "properties": {
                    "username": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    "full_name": {"type": "text", "analyzer": "compliance_analyzer"},
                    "role": {"type": "keyword"},
                    "department": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "last_login": {"type": "date"}
                }
            }
            
            # Apply mappings
            mappings = {
                self._compliance_index: compliance_mapping,
                self._audit_index: audit_mapping,
                self._documents_index: documents_mapping,
                self._users_index: users_mapping
            }
            
            for index, mapping in mappings.items():
                try:
                    self.es_client.indices.put_mapping(
                        index=index,
                        body=mapping
                    )
                    logger.info(f"Applied mapping to index: {index}")
                except Exception as e:
                    logger.warning(f"Failed to apply mapping to {index}: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error("Failed to setup index mappings", error=str(e))
            return False
    
    # =============================================================================
    # INDEXING OPERATIONS
    # =============================================================================
    
    def index_compliance_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index compliance document"""
        try:
            # Add timestamp if not present
            if "created_at" not in document:
                document["created_at"] = datetime.now(timezone.utc).isoformat()
            
            if "updated_at" not in document:
                document["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.es_client.index(
                index=self._compliance_index,
                id=doc_id,
                body=document
            )
            
            if response["result"] in ["created", "updated"]:
                self._search_metrics['compliance_documents_indexed'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error("Failed to index compliance document", doc_id=doc_id, error=str(e))
            return False
    
    def index_audit_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index audit document"""
        try:
            # Add timestamp if not present
            if "timestamp" not in document:
                document["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            response = self.es_client.index(
                index=self._audit_index,
                id=doc_id,
                body=document
            )
            
            if response["result"] in ["created", "updated"]:
                self._search_metrics['audit_documents_indexed'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error("Failed to index audit document", doc_id=doc_id, error=str(e))
            return False
    
    def index_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index general document"""
        try:
            # Add timestamps if not present
            if "created_at" not in document:
                document["created_at"] = datetime.now(timezone.utc).isoformat()
            
            if "updated_at" not in document:
                document["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.es_client.index(
                index=self._documents_index,
                id=doc_id,
                body=document
            )
            
            if response["result"] in ["created", "updated"]:
                self._search_metrics['documents_indexed'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error("Failed to index document", doc_id=doc_id, error=str(e))
            return False
    
    def index_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Index user document"""
        try:
            # Add timestamps if not present
            if "created_at" not in user_data:
                user_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.es_client.index(
                index=self._users_index,
                id=user_id,
                body=user_data
            )
            
            if response["result"] in ["created", "updated"]:
                self._search_metrics['users_indexed'] += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error("Failed to index user", user_id=user_id, error=str(e))
            return False
    
    def bulk_index(self, documents: List[Dict[str, Any]], index_name: str) -> Dict[str, Any]:
        """Bulk index documents"""
        try:
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_id": doc.get("_id"),
                    "_source": {k: v for k, v in doc.items() if k != "_id"}
                }
                actions.append(action)
            
            success_count = 0
            error_count = 0
            
            for ok, result in helpers.streaming_bulk(
                self.es_client, 
                actions, 
                chunk_size=1000,
                request_timeout=60
            ):
                if ok:
                    success_count += 1
                else:
                    error_count += 1
            
            self._search_metrics['bulk_index_operations'] += 1
            
            return {
                "success_count": success_count,
                "error_count": error_count,
                "total_count": len(documents)
            }
            
        except Exception as e:
            logger.error("Bulk indexing failed", index_name=index_name, error=str(e))
            return {"error": str(e)}
    
    # =============================================================================
    # SEARCH OPERATIONS
    # =============================================================================
    
    def search_compliance(self, query: str, filters: Dict[str, Any] = None, 
                         size: int = None, from_: int = 0) -> Dict[str, Any]:
        """Search compliance documents"""
        try:
            s = Search(using=self.es_client, index=self._compliance_index)
            
            # Build query
            if query:
                q = Q("multi_match", query=query, fields=["title^2", "description", "details"])
                s = s.query(q)
            else:
                s = s.query("match_all")
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        s = s.filter("terms", **{field: value})
                    else:
                        s = s.filter("term", **{field: value})
            
            # Set size and from
            s = s[from_:from_ + (size or self._default_size)]
            
            # Execute search
            response = s.execute()
            
            self._search_metrics['compliance_searches'] += 1
            
            return {
                "total": response.hits.total.value,
                "hits": [
                    {
                        "id": hit.meta.id,
                        "score": hit.meta.score,
                        "source": hit.to_dict()
                    }
                    for hit in response.hits
                ],
                "aggregations": response.aggregations.to_dict() if response.aggregations else {}
            }
            
        except Exception as e:
            logger.error("Compliance search failed", query=query, error=str(e))
            return {"error": str(e)}
    
    def search_audit_trail(self, query: str = None, filters: Dict[str, Any] = None,
                          size: int = None, from_: int = 0) -> Dict[str, Any]:
        """Search audit trail"""
        try:
            s = Search(using=self.es_client, index=self._audit_index)
            
            # Build query
            if query:
                q = Q("multi_match", query=query, fields=["action", "resource_type", "changes"])
                s = s.query(q)
            else:
                s = s.query("match_all")
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        s = s.filter("terms", **{field: value})
                    else:
                        s = s.filter("term", **{field: value})
            
            # Sort by timestamp descending
            s = s.sort("-timestamp")
            
            # Set size and from
            s = s[from_:from_ + (size or self._default_size)]
            
            # Execute search
            response = s.execute()
            
            self._search_metrics['audit_searches'] += 1
            
            return {
                "total": response.hits.total.value,
                "hits": [
                    {
                        "id": hit.meta.id,
                        "score": hit.meta.score,
                        "source": hit.to_dict()
                    }
                    for hit in response.hits
                ]
            }
            
        except Exception as e:
            logger.error("Audit search failed", query=query, error=str(e))
            return {"error": str(e)}
    
    def search_documents(self, query: str, filters: Dict[str, Any] = None,
                        size: int = None, from_: int = 0) -> Dict[str, Any]:
        """Search documents"""
        try:
            s = Search(using=self.es_client, index=self._documents_index)
            
            # Build query
            q = Q("multi_match", query=query, fields=["title^2", "content", "tags"])
            s = s.query(q)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        s = s.filter("terms", **{field: value})
                    else:
                        s = s.filter("term", **{field: value})
            
            # Set size and from
            s = s[from_:from_ + (size or self._default_size)]
            
            # Execute search
            response = s.execute()
            
            self._search_metrics['document_searches'] += 1
            
            return {
                "total": response.hits.total.value,
                "hits": [
                    {
                        "id": hit.meta.id,
                        "score": hit.meta.score,
                        "source": hit.to_dict()
                    }
                    for hit in response.hits
                ]
            }
            
        except Exception as e:
            logger.error("Document search failed", query=query, error=str(e))
            return {"error": str(e)}
    
    def search_users(self, query: str, filters: Dict[str, Any] = None,
                    size: int = None, from_: int = 0) -> Dict[str, Any]:
        """Search users"""
        try:
            s = Search(using=self.es_client, index=self._users_index)
            
            # Build query
            if query:
                q = Q("multi_match", query=query, fields=["username", "full_name", "email"])
                s = s.query(q)
            else:
                s = s.query("match_all")
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        s = s.filter("terms", **{field: value})
                    else:
                        s = s.filter("term", **{field: value})
            
            # Set size and from
            s = s[from_:from_ + (size or self._default_size)]
            
            # Execute search
            response = s.execute()
            
            self._search_metrics['user_searches'] += 1
            
            return {
                "total": response.hits.total.value,
                "hits": [
                    {
                        "id": hit.meta.id,
                        "score": hit.meta.score,
                        "source": hit.to_dict()
                    }
                    for hit in response.hits
                ]
            }
            
        except Exception as e:
            logger.error("User search failed", query=query, error=str(e))
            return {"error": str(e)}
    
    # =============================================================================
    # ANALYTICS AND AGGREGATIONS
    # =============================================================================
    
    def get_compliance_analytics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get compliance analytics"""
        try:
            s = Search(using=self.es_client, index=self._compliance_index)
            
            # Date range filter
            if start_date and end_date:
                s = s.filter("range", created_at={"gte": start_date.isoformat(), "lte": end_date.isoformat()})
            
            # Status aggregation
            status_agg = A("terms", field="status")
            s.aggs.bucket("status_breakdown", status_agg)
            
            # Compliance type aggregation
            type_agg = A("terms", field="compliance_type")
            s.aggs.bucket("compliance_types", type_agg)
            
            # Date histogram
            date_agg = A("date_histogram", field="created_at", interval="1d")
            s.aggs.bucket("daily_trend", date_agg)
            
            response = s.execute()
            
            return {
                "status_breakdown": response.aggregations.status_breakdown.buckets,
                "compliance_types": response.aggregations.compliance_types.buckets,
                "daily_trend": response.aggregations.daily_trend.buckets
            }
            
        except Exception as e:
            logger.error("Failed to get compliance analytics", error=str(e))
            return {"error": str(e)}
    
    def get_audit_analytics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get audit analytics"""
        try:
            s = Search(using=self.es_client, index=self._audit_index)
            
            # Date range filter
            if start_date and end_date:
                s = s.filter("range", timestamp={"gte": start_date.isoformat(), "lte": end_date.isoformat()})
            
            # Action aggregation
            action_agg = A("terms", field="action")
            s.aggs.bucket("action_breakdown", action_agg)
            
            # User aggregation
            user_agg = A("terms", field="user_id", size=20)
            s.aggs.bucket("top_users", user_agg)
            
            # Resource type aggregation
            resource_agg = A("terms", field="resource_type")
            s.aggs.bucket("resource_types", resource_agg)
            
            response = s.execute()
            
            return {
                "action_breakdown": response.aggregations.action_breakdown.buckets,
                "top_users": response.aggregations.top_users.buckets,
                "resource_types": response.aggregations.resource_types.buckets
            }
            
        except Exception as e:
            logger.error("Failed to get audit analytics", error=str(e))
            return {"error": str(e)}
    
    # =============================================================================
    # MAINTENANCE OPERATIONS
    # =============================================================================
    
    def refresh_indices(self) -> bool:
        """Refresh all indices"""
        try:
            indices = [self._compliance_index, self._audit_index, self._documents_index, self._users_index]
            
            for index in indices:
                self.es_client.indices.refresh(index=index)
            
            logger.info("Elasticsearch indices refreshed successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to refresh indices", error=str(e))
            return False
    
    def optimize_indices(self) -> bool:
        """Optimize indices for better performance"""
        try:
            indices = [self._compliance_index, self._audit_index, self._documents_index, self._users_index]
            
            for index in indices:
                self.es_client.indices.forcemerge(index=index)
            
            logger.info("Elasticsearch indices optimized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to optimize indices", error=str(e))
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            indices = [self._compliance_index, self._audit_index, self._documents_index, self._users_index]
            
            stats = {}
            for index in indices:
                try:
                    index_stats = self.es_client.indices.stats(index=index)
                    stats[index] = {
                        "docs": index_stats["indices"][index]["total"]["docs"],
                        "store_size": index_stats["indices"][index]["total"]["store"]["size_in_bytes"],
                        "indexing": index_stats["indices"][index]["total"]["indexing"]
                    }
                except Exception as e:
                    stats[index] = {"error": str(e)}
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get index stats", error=str(e))
            return {"error": str(e)}
    
    # =============================================================================
    # HEALTH CHECKING
    # =============================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Perform Elasticsearch health check"""
        current_time = time.time()
        
        # Check if we need to perform health check
        if (self._last_health_check and 
            current_time - self._last_health_check < self._health_check_interval):
            return {
                "status": self._health_status,
                "last_check": self._last_health_check,
                "message": "Using cached health status"
            }
        
        try:
            # Get cluster health
            cluster_health = self.es_client.cluster.health()
            
            # Get index health
            index_health = {}
            indices = [self._compliance_index, self._audit_index, self._documents_index, self._users_index]
            
            for index in indices:
                try:
                    index_stats = self.es_client.indices.stats(index=index)
                    index_health[index] = {
                        "status": "green",
                        "docs": index_stats["indices"][index]["total"]["docs"]["count"]
                    }
                except Exception as e:
                    index_health[index] = {"status": "red", "error": str(e)}
            
            # Determine overall health
            if cluster_health["status"] == "green":
                self._health_status = "healthy"
                self._connection_errors = 0
                message = "Elasticsearch is healthy"
            else:
                self._health_status = "unhealthy"
                self._connection_errors += 1
                message = f"Elasticsearch cluster status: {cluster_health['status']}"
            
            # Get search metrics
            search_metrics = self._get_search_metrics()
            
            self._last_health_check = current_time
            
            return {
                "status": self._health_status,
                "last_check": current_time,
                "message": message,
                "connection_errors": self._connection_errors,
                "cluster_health": cluster_health,
                "index_health": index_health,
                "search_metrics": search_metrics
            }
            
        except Exception as e:
            self._health_status = "error"
            self._connection_errors += 1
            logger.error("Elasticsearch health check failed", error=str(e), exc_info=True)
            
            return {
                "status": "error",
                "last_check": current_time,
                "message": f"Health check error: {str(e)}",
                "connection_errors": self._connection_errors
            }
    
    def _get_search_metrics(self) -> Dict[str, Any]:
        """Get search metrics"""
        current_time = datetime.now(timezone.utc)
        
        # Reset metrics if interval has passed
        if (current_time - self._last_metrics_reset).total_seconds() > self._metrics_reset_interval:
            self._search_metrics.clear()
            self._last_metrics_reset = current_time
        
        return dict(self._search_metrics)
    
    # =============================================================================
    # CLEANUP
    # =============================================================================
    
    def close(self):
        """Close Elasticsearch connection"""
        try:
            with self._lock:
                if self.es_client:
                    self.es_client.close()
                    self.es_client = None
                logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error("Error closing Elasticsearch connection", error=str(e))

# =============================================================================
# GLOBAL ELASTICSEARCH MANAGER INSTANCE
# =============================================================================

_elasticsearch_manager: Optional[ElasticsearchManager] = None

def get_elasticsearch_manager() -> ElasticsearchManager:
    """Get the global Elasticsearch manager instance"""
    global _elasticsearch_manager
    if _elasticsearch_manager is None:
        _elasticsearch_manager = ElasticsearchManager()
    return _elasticsearch_manager

def initialize_elasticsearch() -> bool:
    """Initialize the global Elasticsearch connection"""
    return get_elasticsearch_manager().initialize()

def close_elasticsearch():
    """Close the global Elasticsearch connection"""
    global _elasticsearch_manager
    if _elasticsearch_manager:
        _elasticsearch_manager.close()
        _elasticsearch_manager = None

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'ElasticsearchManager',
    'get_elasticsearch_manager',
    'initialize_elasticsearch',
    'close_elasticsearch'
]
