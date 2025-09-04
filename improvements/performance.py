"""
Enhanced Performance and Caching Improvements
"""
import asyncio
import time
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from functools import wraps, lru_cache
from dataclasses import dataclass
from enum import Enum
import threading
import weakref
import gzip
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncpg
import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool
import logging


class CacheStrategy(str, Enum):
    """Cache strategies"""
    LRU = "lru"
    TTL = "ttl"
    LFU = "lfu"
    REDIS = "redis"
    HYBRID = "hybrid"


@dataclass
class CacheConfig:
    """Cache configuration"""
    strategy: CacheStrategy = CacheStrategy.HYBRID
    max_size: int = 10000
    ttl_seconds: int = 3600
    redis_url: Optional[str] = None
    compression_enabled: bool = True
    compression_threshold: int = 1024  # bytes
    enable_metrics: bool = True


class CacheMetrics:
    """Cache performance metrics"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_size = 0
        self.avg_access_time = 0.0
        self._lock = threading.Lock()
    
    def record_hit(self, access_time: float):
        with self._lock:
            self.hits += 1
            self._update_avg_time(access_time)
    
    def record_miss(self, access_time: float):
        with self._lock:
            self.misses += 1
            self._update_avg_time(access_time)
    
    def record_eviction(self):
        with self._lock:
            self.evictions += 1
    
    def _update_avg_time(self, access_time: float):
        total_requests = self.hits + self.misses
        if total_requests > 1:
            self.avg_access_time = (
                (self.avg_access_time * (total_requests - 1) + access_time) / 
                total_requests
            )
        else:
            self.avg_access_time = access_time
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "evictions": self.evictions,
            "total_size": self.total_size,
            "avg_access_time_ms": self.avg_access_time * 1000
        }


class TTLCache:
    """TTL-based cache with compression"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600, enable_compression: bool = True):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_compression = enable_compression
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
        self.metrics = CacheMetrics()
    
    def _is_expired(self, timestamp: float) -> bool:
        return time.time() - timestamp > self.ttl_seconds
    
    def _compress_value(self, value: Any) -> bytes:
        """Compress value if beneficial"""
        serialized = pickle.dumps(value)
        if self.enable_compression and len(serialized) > 1024:
            return gzip.compress(serialized)
        return serialized
    
    def _decompress_value(self, data: bytes) -> Any:
        """Decompress value"""
        try:
            return pickle.loads(gzip.decompress(data))
        except gzip.BadGzipFile:
            return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                
                if self._is_expired(timestamp):
                    del self._cache[key]
                    del self._access_times[key]
                    self.metrics.record_miss(time.time() - start_time)
                    return None
                
                self._access_times[key] = time.time()
                self.metrics.record_hit(time.time() - start_time)
                
                if isinstance(value, bytes):
                    return self._decompress_value(value)
                return value
            
            self.metrics.record_miss(time.time() - start_time)
            return None
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            # Evict expired entries
            self._evict_expired()
            
            # Evict LRU if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            # Store value (compressed if beneficial)
            if self.enable_compression:
                stored_value = self._compress_value(value)
            else:
                stored_value = value
            
            self._cache[key] = (stored_value, time.time())
            self._access_times[key] = time.time()
            
            self.metrics.total_size = len(self._cache)
    
    def _evict_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self._cache[key]
            del self._access_times[key]
            self.metrics.record_eviction()
    
    def _evict_lru(self):
        """Remove least recently used entry"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[lru_key]
        del self._access_times[lru_key]
        self.metrics.record_eviction()
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self.metrics.total_size = 0


class HybridCache:
    """Hybrid cache combining local and Redis"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.local_cache = TTLCache(
            max_size=config.max_size // 2,  # Split capacity
            ttl_seconds=config.ttl_seconds,
            enable_compression=config.compression_enabled
        )
        self.redis_client: Optional[redis.Redis] = None
        self.metrics = CacheMetrics()
        
        if config.redis_url:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=False
            )
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        
        # Try local cache first
        value = self.local_cache.get(key)
        if value is not None:
            self.metrics.record_hit(time.time() - start_time)
            return value
        
        # Try Redis cache
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    value = pickle.loads(redis_value)
                    # Populate local cache
                    self.local_cache.set(key, value)
                    self.metrics.record_hit(time.time() - start_time)
                    return value
            except Exception as e:
                logging.error(f"Redis get error: {e}")
        
        self.metrics.record_miss(time.time() - start_time)
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        # Set in local cache
        self.local_cache.set(key, value)
        
        # Set in Redis cache
        if self.redis_client:
            try:
                serialized_value = pickle.dumps(value)
                self.redis_client.set(
                    key, 
                    serialized_value, 
                    ex=ttl or self.config.ttl_seconds
                )
            except Exception as e:
                logging.error(f"Redis set error: {e}")
    
    def delete(self, key: str) -> None:
        # Remove from local cache
        with self.local_cache._lock:
            if key in self.local_cache._cache:
                del self.local_cache._cache[key]
                del self.local_cache._access_times[key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logging.error(f"Redis delete error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        local_stats = self.local_cache.metrics.get_stats()
        global_stats = self.metrics.get_stats()
        
        return {
            "local_cache": local_stats,
            "global_cache": global_stats,
            "redis_connected": self.redis_client is not None
        }


class QueryOptimizer:
    """Database query optimization"""
    
    def __init__(self, cache: HybridCache):
        self.cache = cache
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def _get_query_key(self, query: str, params: Tuple = ()) -> str:
        """Generate cache key for query"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        params_hash = hashlib.md5(str(params).encode()).hexdigest()
        return f"query:{query_hash}:{params_hash}"
    
    async def execute_cached_query(
        self, 
        session: AsyncSession,
        query: str,
        params: Tuple = (),
        ttl: int = 3600
    ) -> Any:
        """Execute query with caching"""
        cache_key = self._get_query_key(query, params)
        
        # Try cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            self._record_query_stat(query, "cache_hit")
            return cached_result
        
        # Execute query
        start_time = time.time()
        try:
            result = await session.execute(query, params)
            execution_time = time.time() - start_time
            
            # Cache result
            await self.cache.set(cache_key, result, ttl)
            
            self._record_query_stat(query, "database_hit", execution_time)
            return result
            
        except Exception as e:
            self._record_query_stat(query, "error")
            raise
    
    def _record_query_stat(self, query: str, event_type: str, execution_time: float = 0):
        """Record query statistics"""
        with self._lock:
            query_key = hashlib.md5(query.encode()).hexdigest()[:8]
            
            if query_key not in self.query_stats:
                self.query_stats[query_key] = {
                    "cache_hits": 0,
                    "database_hits": 0,
                    "errors": 0,
                    "total_execution_time": 0,
                    "avg_execution_time": 0
                }
            
            stats = self.query_stats[query_key]
            
            if event_type == "cache_hit":
                stats["cache_hits"] += 1
            elif event_type == "database_hit":
                stats["database_hits"] += 1
                stats["total_execution_time"] += execution_time
                total_db_hits = stats["database_hits"]
                stats["avg_execution_time"] = stats["total_execution_time"] / total_db_hits
            elif event_type == "error":
                stats["errors"] += 1


class AsyncConnectionPool:
    """Enhanced async connection pool"""
    
    def __init__(
        self,
        database_url: str,
        min_size: int = 5,
        max_size: int = 20,
        max_queries: int = 50000,
        max_inactive_connection_lifetime: float = 300.0
    ):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.max_queries = max_queries
        self.max_inactive_connection_lifetime = max_inactive_connection_lifetime
        self.pool: Optional[asyncpg.Pool] = None
        self._pool_lock = asyncio.Lock()
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self.pool is None:
            async with self._pool_lock:
                if self.pool is None:
                    self.pool = await asyncpg.create_pool(
                        self.database_url,
                        min_size=self.min_size,
                        max_size=self.max_size,
                        max_queries=self.max_queries,
                        max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
                        command_timeout=60
                    )
        return self.pool
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query with connection pooling"""
        pool = await self.get_pool()
        
        async with pool.acquire() as connection:
            result = await connection.fetch(query, *args)
            return [dict(row) for row in result]
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()


class BatchProcessor:
    """Batch processing for improved performance"""
    
    def __init__(self, batch_size: int = 100, max_wait_time: float = 5.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_items: List[Any] = []
        self.batch_futures: List[asyncio.Future] = []
        self._lock = asyncio.Lock()
        self._timer_task: Optional[asyncio.Task] = None
    
    async def add_item(self, item: Any, processor_func: Callable) -> Any:
        """Add item to batch for processing"""
        future = asyncio.Future()
        
        async with self._lock:
            self.pending_items.append(item)
            self.batch_futures.append(future)
            
            # Start timer if this is the first item
            if len(self.pending_items) == 1:
                self._timer_task = asyncio.create_task(
                    self._wait_and_process(processor_func)
                )
            
            # Process immediately if batch is full
            if len(self.pending_items) >= self.batch_size:
                if self._timer_task:
                    self._timer_task.cancel()
                await self._process_batch(processor_func)
        
        return await future
    
    async def _wait_and_process(self, processor_func: Callable):
        """Wait for max time then process batch"""
        try:
            await asyncio.sleep(self.max_wait_time)
            async with self._lock:
                if self.pending_items:
                    await self._process_batch(processor_func)
        except asyncio.CancelledError:
            pass  # Batch was processed early
    
    async def _process_batch(self, processor_func: Callable):
        """Process current batch"""
        if not self.pending_items:
            return
        
        items = self.pending_items.copy()
        futures = self.batch_futures.copy()
        
        self.pending_items.clear()
        self.batch_futures.clear()
        
        try:
            # Process batch
            results = await processor_func(items)
            
            # Resolve futures
            for future, result in zip(futures, results):
                if not future.done():
                    future.set_result(result)
                    
        except Exception as e:
            # Reject all futures
            for future in futures:
                if not future.done():
                    future.set_exception(e)


def cache_with_ttl(ttl_seconds: int = 3600, cache_instance: Optional[HybridCache] = None):
    """Decorator for caching function results with TTL"""
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or HybridCache(CacheConfig())
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl_seconds)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceMonitor:
    """Performance monitoring and profiling"""
    
    def __init__(self):
        self.function_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def monitor_function(self, func: Callable) -> Callable:
        """Decorator to monitor function performance"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                memory_delta = self._get_memory_usage() - start_memory
                
                self._record_stats(func.__name__, execution_time, memory_delta, True)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self._record_stats(func.__name__, execution_time, 0, False)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _record_stats(self, func_name: str, execution_time: float, memory_delta: float, success: bool):
        """Record function execution statistics"""
        with self._lock:
            if func_name not in self.function_stats:
                self.function_stats[func_name] = {
                    "call_count": 0,
                    "success_count": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "total_memory_delta": 0.0,
                    "avg_memory_delta": 0.0
                }
            
            stats = self.function_stats[func_name]
            stats["call_count"] += 1
            
            if success:
                stats["success_count"] += 1
            
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["call_count"]
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)
            
            stats["total_memory_delta"] += memory_delta
            stats["avg_memory_delta"] = stats["total_memory_delta"] / stats["call_count"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        with self._lock:
            return {
                "function_stats": self.function_stats.copy(),
                "summary": {
                    "total_functions": len(self.function_stats),
                    "total_calls": sum(stats["call_count"] for stats in self.function_stats.values()),
                    "avg_success_rate": sum(
                        stats["success_count"] / stats["call_count"] 
                        for stats in self.function_stats.values()
                    ) / len(self.function_stats) if self.function_stats else 0
                }
            }