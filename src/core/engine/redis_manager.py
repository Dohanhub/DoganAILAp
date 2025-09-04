"""
Redis connection and cache management for DoganAI Compliance Kit
Advanced caching, session management, and performance optimization
"""

import os
import logging
import time
import threading
import json
import pickle
from typing import Optional, Any, Dict, List, Union, Generator
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError
import structlog
from collections import defaultdict

from .settings import settings

logger = structlog.get_logger(__name__)

# =============================================================================
# REDIS CONNECTION MANAGER
# =============================================================================

class RedisManager:
    """Advanced Redis connection manager with caching, sessions, and monitoring"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_cluster: Optional[redis.RedisCluster] = None
        self._lock = threading.Lock()
        self._health_status = "unknown"
        self._last_health_check = None
        self._health_check_interval = 30  # seconds
        self._connection_errors = 0
        self._max_connection_errors = 5
        self._cache_metrics = defaultdict(int)
        self._last_metrics_reset = datetime.now(timezone.utc)
        self._metrics_reset_interval = 3600  # 1 hour
        
        # Cache configuration
        self._default_ttl = 3600  # 1 hour
        self._session_ttl = 1800  # 30 minutes
        self._lock_ttl = 300  # 5 minutes
        
        # Connection configuration
        self._connect_timeout = 5
        self._read_timeout = 10
        self._write_timeout = 10
        self._retry_on_timeout = True
        self._retry_on_error = True
        self._max_retries = 3
        
    def initialize(self) -> bool:
        """Initialize Redis connection with advanced configuration"""
        try:
            with self._lock:
                if self.redis_client is not None:
                    logger.info("Redis already initialized")
                    return True
                
                # Determine Redis configuration
                if settings.redis.use_cluster:
                    self._initialize_cluster()
                else:
                    self._initialize_single()
                
                # Test connection
                if not self._test_connection():
                    raise Exception("Failed to establish Redis connection")
                
                # Set up connection event handlers
                self._setup_connection_events()
                
                logger.info(
                    "Redis initialized successfully",
                    host=settings.redis.host,
                    port=settings.redis.port,
                    database=settings.redis.database,
                    use_cluster=settings.redis.use_cluster
                )
                
                return True
                
        except Exception as e:
            logger.error(
                "Failed to initialize Redis",
                error=str(e),
                host=settings.redis.host,
                port=settings.redis.port,
                exc_info=True
            )
            return False
    
    def _initialize_single(self):
        """Initialize single Redis instance"""
        self.redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.database,
            password=settings.redis.password,
            decode_responses=True,
            socket_connect_timeout=self._connect_timeout,
            socket_timeout=self._read_timeout,
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=self._retry_on_timeout,
            retry_on_error=self._retry_on_error,
            retry=self._max_retries,
            health_check_interval=30,
            max_connections=20,
            connection_pool_class=redis.ConnectionPool
        )
    
    def _initialize_cluster(self):
        """Initialize Redis cluster"""
        startup_nodes = [
            {"host": node["host"], "port": node["port"]} 
            for node in settings.redis.cluster_nodes
        ]
        
        self.redis_cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            socket_connect_timeout=self._connect_timeout,
            socket_timeout=self._read_timeout,
            socket_keepalive=True,
            retry_on_timeout=self._retry_on_timeout,
            retry_on_error=self._retry_on_error,
            retry=self._max_retries,
            max_connections=20
        )
    
    def _test_connection(self) -> bool:
        """Test Redis connection with timeout"""
        try:
            client = self._get_client()
            client.ping()
            return True
        except Exception as e:
            logger.error("Redis connection test failed", error=str(e))
            return False
    
    def _setup_connection_events(self):
        """Set up Redis connection event handlers"""
        # Monitor connection events
        def on_connect(connection):
            logger.info("Redis connection established")
            self._cache_metrics['connections_established'] += 1
        
        def on_disconnect(connection):
            logger.warning("Redis connection disconnected")
            self._cache_metrics['connections_disconnected'] += 1
        
        # Add event handlers if supported
        if hasattr(self.redis_client, 'connection_pool'):
            pool = self.redis_client.connection_pool
            if hasattr(pool, 'on_connect'):
                pool.on_connect = on_connect
            if hasattr(pool, 'on_disconnect'):
                pool.on_disconnect = on_disconnect
    
    def _get_client(self) -> redis.Redis:
        """Get Redis client (single or cluster)"""
        if settings.redis.use_cluster and self.redis_cluster:
            return self.redis_cluster
        elif self.redis_client:
            return self.redis_client
        else:
            raise RuntimeError("Redis not initialized")
    
    # =============================================================================
    # CACHING OPERATIONS
    # =============================================================================
    
    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value with TTL"""
        try:
            client = self._get_client()
            serialized_value = self._serialize_value(value)
            ttl = ttl or self._default_ttl
            
            result = client.setex(key, ttl, serialized_value)
            self._cache_metrics['cache_sets'] += 1
            return bool(result)
            
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            self._cache_metrics['cache_errors'] += 1
            return False
    
    def get_cache(self, key: str, default: Any = None) -> Any:
        """Get cache value with deserialization"""
        try:
            client = self._get_client()
            value = client.get(key)
            
            if value is None:
                self._cache_metrics['cache_misses'] += 1
                return default
            
            self._cache_metrics['cache_hits'] += 1
            return self._deserialize_value(value)
            
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            self._cache_metrics['cache_errors'] += 1
            return default
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache key"""
        try:
            client = self._get_client()
            result = client.delete(key)
            self._cache_metrics['cache_deletes'] += 1
            return bool(result)
            
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            self._cache_metrics['cache_errors'] += 1
            return False
    
    def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache keys matching pattern"""
        try:
            client = self._get_client()
            keys = client.keys(pattern)
            
            if keys:
                deleted = client.delete(*keys)
                self._cache_metrics['cache_pattern_deletes'] += 1
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error("Cache pattern clear failed", pattern=pattern, error=str(e))
            self._cache_metrics['cache_errors'] += 1
            return 0
    
    def get_cache_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for cache key"""
        try:
            client = self._get_client()
            return client.ttl(key)
        except Exception as e:
            logger.error("Cache TTL check failed", key=key, error=str(e))
            return None
    
    # =============================================================================
    # SESSION MANAGEMENT
    # =============================================================================
    
    def set_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Set session data with TTL"""
        key = f"session:{session_id}"
        return self.set_cache(key, data, self._session_ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"session:{session_id}"
        return self.get_cache(key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        key = f"session:{session_id}"
        return self.delete_cache(key)
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session TTL"""
        try:
            client = self._get_client()
            key = f"session:{session_id}"
            return bool(client.expire(key, self._session_ttl))
        except Exception as e:
            logger.error("Session extension failed", session_id=session_id, error=str(e))
            return False
    
    # =============================================================================
    # DISTRIBUTED LOCKING
    # =============================================================================
    
    @contextmanager
    def distributed_lock(self, lock_name: str, timeout: Optional[int] = None) -> Generator[bool, None, None]:
        """Distributed lock context manager"""
        lock_key = f"lock:{lock_name}"
        timeout = timeout or self._lock_ttl
        acquired = False
        
        try:
            client = self._get_client()
            acquired = client.set(lock_key, "1", ex=timeout, nx=True)
            
            if acquired:
                self._cache_metrics['locks_acquired'] += 1
                yield True
            else:
                self._cache_metrics['locks_failed'] += 1
                yield False
                
        except Exception as e:
            logger.error("Distributed lock failed", lock_name=lock_name, error=str(e))
            yield False
        finally:
            if acquired:
                try:
                    client.delete(lock_key)
                    self._cache_metrics['locks_released'] += 1
                except Exception as e:
                    logger.error("Lock release failed", lock_name=lock_name, error=str(e))
    
    # =============================================================================
    # PUBLISH/SUBSCRIBE
    # =============================================================================
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            client = self._get_client()
            serialized_message = self._serialize_value(message)
            subscribers = client.publish(channel, serialized_message)
            self._cache_metrics['messages_published'] += 1
            return subscribers
            
        except Exception as e:
            logger.error("Publish failed", channel=channel, error=str(e))
            self._cache_metrics['pubsub_errors'] += 1
            return 0
    
    def subscribe(self, channel: str, callback) -> bool:
        """Subscribe to channel with callback"""
        try:
            client = self._get_client()
            pubsub = client.pubsub()
            pubsub.subscribe(channel)
            
            def message_handler(message):
                if message['type'] == 'message':
                    data = self._deserialize_value(message['data'])
                    callback(data)
            
            pubsub.listen(message_handler)
            self._cache_metrics['subscriptions_created'] += 1
            return True
            
        except Exception as e:
            logger.error("Subscribe failed", channel=channel, error=str(e))
            self._cache_metrics['pubsub_errors'] += 1
            return False
    
    # =============================================================================
    # SERIALIZATION
    # =============================================================================
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        elif isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        else:
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            # Try JSON first
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            try:
                # Try pickle
                return pickle.loads(bytes.fromhex(value))
            except (ValueError, pickle.UnpicklingError):
                # Return as string
                return value
    
    # =============================================================================
    # HEALTH CHECKING
    # =============================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Perform Redis health check"""
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
            client = self._get_client()
            
            # Test basic operations
            client.ping()
            client.set("health_check", "ok", ex=60)
            result = client.get("health_check")
            client.delete("health_check")
            
            if result == "ok":
                self._health_status = "healthy"
                self._connection_errors = 0
                message = "Redis is healthy"
            else:
                self._health_status = "unhealthy"
                self._connection_errors += 1
                message = f"Redis health check failed ({self._connection_errors} consecutive failures)"
            
            # Get Redis info
            info = client.info()
            
            # Get cache metrics
            cache_metrics = self._get_cache_metrics()
            
            self._last_health_check = current_time
            
            return {
                "status": self._health_status,
                "last_check": current_time,
                "message": message,
                "connection_errors": self._connection_errors,
                "redis_info": {
                    "version": info.get("redis_version"),
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses")
                },
                "cache_metrics": cache_metrics
            }
            
        except Exception as e:
            self._health_status = "error"
            self._connection_errors += 1
            logger.error("Redis health check failed", error=str(e), exc_info=True)
            
            return {
                "status": "error",
                "last_check": current_time,
                "message": f"Health check error: {str(e)}",
                "connection_errors": self._connection_errors
            }
    
    def _get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache metrics"""
        current_time = datetime.now(timezone.utc)
        
        # Reset metrics if interval has passed
        if (current_time - self._last_metrics_reset).total_seconds() > self._metrics_reset_interval:
            self._cache_metrics.clear()
            self._last_metrics_reset = current_time
        
        return dict(self._cache_metrics)
    
    # =============================================================================
    # CLEANUP
    # =============================================================================
    
    def close(self):
        """Close Redis connections"""
        try:
            with self._lock:
                if self.redis_client:
                    self.redis_client.close()
                    self.redis_client = None
                if self.redis_cluster:
                    self.redis_cluster.close()
                    self.redis_cluster = None
                logger.info("Redis connections closed")
        except Exception as e:
            logger.error("Error closing Redis connections", error=str(e))

# =============================================================================
# GLOBAL REDIS MANAGER INSTANCE
# =============================================================================

_redis_manager: Optional[RedisManager] = None

def get_redis_manager() -> RedisManager:
    """Get the global Redis manager instance"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisManager()
    return _redis_manager

def initialize_redis() -> bool:
    """Initialize the global Redis connection"""
    return get_redis_manager().initialize()

def close_redis():
    """Close the global Redis connection"""
    global _redis_manager
    if _redis_manager:
        _redis_manager.close()
        _redis_manager = None

# =============================================================================
# CACHE DECORATORS
# =============================================================================

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Cache decorator for functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            redis_manager = get_redis_manager()
            cached_result = redis_manager.get_cache(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_manager.set_cache(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    'RedisManager',
    'get_redis_manager',
    'initialize_redis',
    'close_redis',
    'cached'
]
