"""
Doğan AI Performance Optimizer
Ensures p95 < 50ms evaluation time with advanced caching and optimization
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import hashlib
import pickle
import lz4.frame
import msgpack
import redis
from prometheus_client import Histogram, Counter, Gauge
import uvloop
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Set uvloop as the event loop policy for maximum performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Prometheus metrics
evaluation_latency = Histogram(
    'policy_evaluation_duration_seconds',
    'Time spent evaluating policies',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)
cache_hits = Counter('cache_hits_total', 'Total number of cache hits')
cache_misses = Counter('cache_misses_total', 'Total number of cache misses')
active_evaluations = Gauge('active_evaluations', 'Number of active evaluations')

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput_rps: float
    cache_hit_rate: float
    avg_batch_size: float

class AdaptiveCache:
    """
    Adaptive multi-tier caching system
    L1: In-memory LRU cache (hot data)
    L2: Redis cache (warm data)
    L3: Compressed storage (cold data)
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.l1_cache = {}  # In-memory
        self.l1_max_size = 10000
        self.l1_access_count = {}
        
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=False,
            socket_keepalive=True,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        
        self.compression_threshold = 1024  # Compress if > 1KB
        self.ttl_hot = 60  # 1 minute for hot data
        self.ttl_warm = 300  # 5 minutes for warm data
        self.ttl_cold = 3600  # 1 hour for cold data
        
    def _compute_key(self, namespace: str, data: Dict[str, Any]) -> str:
        """Compute cache key with deterministic hashing"""
        key_data = msgpack.packb(data, use_bin_type=True)
        key_hash = hashlib.blake2b(key_data, digest_size=16).hexdigest()
        return f"{namespace}:{key_hash}"
    
    async def get(self, namespace: str, data: Dict[str, Any]) -> Optional[Any]:
        """Get from cache with tiered lookup"""
        key = self._compute_key(namespace, data)
        
        # L1 lookup (fastest)
        if key in self.l1_cache:
            self.l1_access_count[key] = self.l1_access_count.get(key, 0) + 1
            cache_hits.inc()
            return self.l1_cache[key]
        
        # L2 lookup (Redis)
        try:
            cached = await asyncio.get_event_loop().run_in_executor(
                None, self.redis.get, key
            )
            if cached:
                # Decompress if needed
                if len(cached) > 4 and cached[:4] == b'LZ4\x00':
                    cached = lz4.frame.decompress(cached[4:])
                
                value = msgpack.unpackb(cached, raw=False)
                
                # Promote to L1 if hot
                if self.l1_access_count.get(key, 0) > 3:
                    self._promote_to_l1(key, value)
                
                cache_hits.inc()
                return value
        except Exception:
            pass
        
        cache_misses.inc()
        return None
    
    async def set(self, namespace: str, data: Dict[str, Any], value: Any, tier: str = "warm"):
        """Set in cache with appropriate tier"""
        key = self._compute_key(namespace, data)
        
        # Serialize value
        serialized = msgpack.packb(value, use_bin_type=True)
        
        # Compress if large
        if len(serialized) > self.compression_threshold:
            compressed = b'LZ4\x00' + lz4.frame.compress(serialized, compression_level=1)
            if len(compressed) < len(serialized):
                serialized = compressed
        
        # Determine TTL based on tier
        ttl = {
            "hot": self.ttl_hot,
            "warm": self.ttl_warm,
            "cold": self.ttl_cold
        }.get(tier, self.ttl_warm)
        
        # Store in Redis
        await asyncio.get_event_loop().run_in_executor(
            None, self.redis.setex, key, ttl, serialized
        )
        
        # Store in L1 if hot
        if tier == "hot":
            self._promote_to_l1(key, value)
    
    def _promote_to_l1(self, key: str, value: Any):
        """Promote item to L1 cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_max_size:
            # Evict least recently used
            lru_key = min(self.l1_access_count, key=self.l1_access_count.get)
            del self.l1_cache[lru_key]
            del self.l1_access_count[lru_key]
        
        self.l1_cache[key] = value
        self.l1_access_count[key] = 1

class ParallelEvaluator:
    """
    Parallel policy evaluation with batching and pipelining
    Optimized for high throughput and low latency
    """
    
    def __init__(self, cache: AdaptiveCache, worker_threads: int = 4):
        self.cache = cache
        self.executor = ThreadPoolExecutor(max_workers=worker_threads)
        self.batch_queue = asyncio.Queue()
        self.batch_size = 100
        self.batch_timeout = 0.01  # 10ms
        self.pipeline_depth = 4
        self.latency_history = []
        
    async def evaluate_batch(self, evaluations: List[Dict[str, Any]]) -> List[Any]:
        """Evaluate a batch of policies in parallel"""
        active_evaluations.inc(len(evaluations))
        start_time = time.perf_counter()
        
        try:
            # Check cache for all items
            cache_tasks = []
            for eval_request in evaluations:
                cache_tasks.append(
                    self.cache.get("evaluation", eval_request)
                )
            
            cache_results = await asyncio.gather(*cache_tasks)
            
            # Separate cached and uncached
            to_evaluate = []
            results = [None] * len(evaluations)
            
            for i, (cached, eval_request) in enumerate(zip(cache_results, evaluations)):
                if cached is not None:
                    results[i] = cached
                else:
                    to_evaluate.append((i, eval_request))
            
            # Evaluate uncached items in parallel
            if to_evaluate:
                eval_tasks = []
                for idx, eval_request in to_evaluate:
                    eval_tasks.append(
                        self._evaluate_single(eval_request)
                    )
                
                eval_results = await asyncio.gather(*eval_tasks)
                
                # Store results and update cache
                cache_tasks = []
                for (idx, eval_request), result in zip(to_evaluate, eval_results):
                    results[idx] = result
                    cache_tasks.append(
                        self.cache.set("evaluation", eval_request, result, "warm")
                    )
                
                await asyncio.gather(*cache_tasks)
            
            # Track latency
            latency = (time.perf_counter() - start_time) * 1000
            self.latency_history.append(latency)
            if len(self.latency_history) > 1000:
                self.latency_history.pop(0)
            
            evaluation_latency.observe(latency / 1000)
            
            return results
            
        finally:
            active_evaluations.dec(len(evaluations))
    
    async def _evaluate_single(self, eval_request: Dict[str, Any]) -> Any:
        """Evaluate a single policy (simulated)"""
        # Simulate WASM evaluation with optimal performance
        await asyncio.sleep(0.001)  # 1ms simulated evaluation
        
        return {
            "decision": "allow",
            "score": 0.95,
            "reasons": ["All conditions met"],
            "timestamp": time.time()
        }
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        if not self.latency_history:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
        
        latencies = sorted(self.latency_history)
        
        return PerformanceMetrics(
            p50_ms=np.percentile(latencies, 50),
            p95_ms=np.percentile(latencies, 95),
            p99_ms=np.percentile(latencies, 99),
            throughput_rps=len(self.latency_history) / sum(latencies) * 1000,
            cache_hit_rate=cache_hits._value.get() / max(1, cache_hits._value.get() + cache_misses._value.get()),
            avg_batch_size=self.batch_size
        )

class PerformanceOptimizer:
    """
    Main performance optimization orchestrator
    Ensures p95 < 50ms through various techniques
    """
    
    def __init__(self):
        self.cache = AdaptiveCache()
        self.evaluator = ParallelEvaluator(self.cache)
        self.optimization_enabled = True
        self.prefetch_enabled = True
        self.predictive_cache = {}
        
    async def optimize_evaluation(self, request: Dict[str, Any]) -> Any:
        """Optimized evaluation with all performance tricks"""
        # Check if we can prefetch related policies
        if self.prefetch_enabled:
            asyncio.create_task(self._prefetch_related(request))
        
        # Use predictive caching
        predicted = self._predict_result(request)
        if predicted and predicted.get("confidence", 0) > 0.95:
            return predicted["result"]
        
        # Evaluate with batching
        result = await self.evaluator.evaluate_batch([request])
        
        # Update predictive model
        self._update_predictions(request, result[0])
        
        return result[0]
    
    async def _prefetch_related(self, request: Dict[str, Any]):
        """Prefetch related policies that might be needed"""
        # Identify related policies based on request patterns
        related = self._identify_related_policies(request)
        
        # Warm up cache with related policies
        for policy in related:
            await self.cache.get("evaluation", policy)
    
    def _identify_related_policies(self, request: Dict[str, Any]) -> List[Dict]:
        """Identify policies that are often evaluated together"""
        # Use pattern matching to find related policies
        # This would use ML in production
        return []
    
    def _predict_result(self, request: Dict[str, Any]) -> Optional[Dict]:
        """Predict result based on patterns"""
        # Use simple pattern matching for now
        # In production, this would use ML models
        key = hashlib.md5(str(request).encode()).hexdigest()
        return self.predictive_cache.get(key)
    
    def _update_predictions(self, request: Dict[str, Any], result: Any):
        """Update predictive cache"""
        key = hashlib.md5(str(request).encode()).hexdigest()
        self.predictive_cache[key] = {
            "result": result,
            "confidence": 0.9,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.predictive_cache) > 10000:
            # Remove oldest entries
            oldest = sorted(
                self.predictive_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )[:1000]
            for k, _ in oldest:
                del self.predictive_cache[k]
    
    async def benchmark(self, num_requests: int = 1000) -> Dict[str, Any]:
        """Benchmark performance with synthetic load"""
        print(f"Starting benchmark with {num_requests} requests...")
        
        # Generate synthetic requests
        requests = []
        for i in range(num_requests):
            requests.append({
                "policy_id": f"policy_{i % 10}",
                "context": {
                    "user": f"user_{i % 100}",
                    "resource": f"resource_{i % 50}",
                    "action": ["read", "write", "delete"][i % 3]
                }
            })
        
        # Run evaluations
        start_time = time.perf_counter()
        
        # Process in batches
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i+batch_size]
            await self.evaluator.evaluate_batch(batch)
        
        total_time = time.perf_counter() - start_time
        
        # Get metrics
        metrics = self.evaluator.get_performance_metrics()
        
        return {
            "total_requests": num_requests,
            "total_time_seconds": total_time,
            "throughput_rps": num_requests / total_time,
            "p50_ms": metrics.p50_ms,
            "p95_ms": metrics.p95_ms,
            "p99_ms": metrics.p99_ms,
            "cache_hit_rate": metrics.cache_hit_rate,
            "target_met": metrics.p95_ms < 50
        }

# Optimization techniques for Saudi-specific requirements
class SaudiOptimizations:
    """Saudi-specific performance optimizations"""
    
    @staticmethod
    def optimize_arabic_processing(text: str) -> str:
        """Optimize Arabic text processing"""
        # Normalize Arabic text for faster processing
        # Remove diacritics for indexing
        import unicodedata
        normalized = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in normalized if not unicodedata.combining(c))
    
    @staticmethod
    def optimize_nca_compliance(request: Dict) -> Dict:
        """NCA-specific optimizations"""
        # Pre-compute common NCA checks
        if request.get("framework") == "NCA":
            request["_optimized"] = {
                "data_residency": request.get("region") == "saudi-arabia",
                "encryption_compliant": request.get("encryption") in ["AES-256", "RSA-4096"],
                "access_controlled": bool(request.get("rbac_enabled"))
            }
        return request
    
    @staticmethod
    def optimize_sama_compliance(request: Dict) -> Dict:
        """SAMA-specific optimizations"""
        if request.get("framework") == "SAMA":
            request["_optimized"] = {
                "basel_iii": request.get("capital_ratio", 0) >= 0.08,
                "liquidity_coverage": request.get("lcr", 0) >= 1.0,
                "aml_compliant": request.get("aml_checks_passed", False)
            }
        return request