#!/usr/bin/env python3
"""
Memory Profiling and Leak Detection System
Critical fix for memory usage optimization
"""

import psutil
import gc
import time
import logging
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import tracemalloc
import weakref
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """Memory snapshot data"""
    timestamp: datetime
    memory_usage: int
    memory_percent: float
    cpu_percent: float
    active_objects: int
    gc_objects: int
    top_allocations: List[tuple]

class MemoryProfiler:
    """Advanced memory profiling and leak detection"""
    
    def __init__(self, enable_tracemalloc: bool = True):
        self.enable_tracemalloc = enable_tracemalloc
        self.snapshots: List[MemorySnapshot] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.leak_threshold = 10 * 1024 * 1024  # 10MB
        self.cache_references = weakref.WeakSet()
        
        if self.enable_tracemalloc:
            tracemalloc.start(25)  # Keep 25 frames
    
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous memory monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Continuous monitoring loop"""
        while self.monitoring:
            try:
                self.take_snapshot()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Get top memory allocations if tracemalloc is enabled
        top_allocations = []
        if self.enable_tracemalloc and tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')[:10]
            top_allocations = [(stat.count, stat.size, stat.traceback.format()) 
                              for stat in top_stats]
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            memory_usage=memory_info.rss,
            memory_percent=process.memory_percent(),
            cpu_percent=process.cpu_percent(),
            active_objects=len(gc.get_objects()),
            gc_objects=len(gc.garbage),
            top_allocations=top_allocations
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def detect_memory_leaks(self) -> Dict[str, Any]:
        """Detect potential memory leaks"""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots"}
        
        recent_snapshots = self.snapshots[-10:]  # Last 10 snapshots
        memory_trend = [s.memory_usage for s in recent_snapshots]
        
        # Calculate memory growth rate
        if len(memory_trend) >= 2:
            growth_rate = (memory_trend[-1] - memory_trend[0]) / len(memory_trend)
        else:
            growth_rate = 0
        
        # Check for sustained memory growth
        sustained_growth = all(
            memory_trend[i] <= memory_trend[i+1] 
            for i in range(len(memory_trend)-1)
        )
        
        # Analyze cache references
        cache_objects = len(self.cache_references)
        
        leak_report = {
            "memory_growth_rate_mb_per_snapshot": growth_rate / (1024 * 1024),
            "sustained_memory_growth": sustained_growth,
            "potential_leak": growth_rate > self.leak_threshold,
            "cache_objects_count": cache_objects,
            "gc_garbage_count": recent_snapshots[-1].gc_objects,
            "recommendations": []
        }
        
        # Generate recommendations
        if leak_report["potential_leak"]:
            leak_report["recommendations"].append(
                "Memory leak detected - run garbage collection and check cache cleanup"
            )
        
        if recent_snapshots[-1].gc_objects > 100:
            leak_report["recommendations"].append(
                "High garbage collection objects - check for circular references"
            )
        
        if cache_objects > 1000:
            leak_report["recommendations"].append(
                "Large cache size - implement cache size limits and TTL"
            )
        
        return leak_report
    
    def optimize_memory(self):
        """Perform memory optimization"""
        logger.info("Starting memory optimization...")
        
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collected {collected} objects")
        
        # Clear cache references
        self.cache_references.clear()
        
        # Take optimization snapshot
        self.take_snapshot()
        
        logger.info("Memory optimization completed")
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory report"""
        if not self.snapshots:
            return {"error": "No memory data available"}
        
        latest = self.snapshots[-1]
        
        return {
            "current_memory_mb": latest.memory_usage / (1024 * 1024),
            "memory_percent": latest.memory_percent,
            "cpu_percent": latest.cpu_percent,
            "active_objects": latest.active_objects,
            "gc_objects": latest.gc_objects,
            "snapshots_count": len(self.snapshots),
            "top_allocations": latest.top_allocations[:5],
            "leak_analysis": self.detect_memory_leaks()
        }

class CacheMemoryOptimizer:
    """Cache-specific memory optimization"""
    
    def __init__(self, max_cache_size: int = 1000, ttl_seconds: int = 900):
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.cache_entries = {}
        self.access_times = {}
        self.profiler = MemoryProfiler()
    
    def add_cache_entry(self, key: str, value: Any):
        """Add entry to cache with memory optimization"""
        current_time = time.time()
        
        # Check cache size limit
        if len(self.cache_entries) >= self.max_cache_size:
            self._evict_oldest()
        
        self.cache_entries[key] = value
        self.access_times[key] = current_time
        
        # Track for memory profiling
        self.profiler.cache_references.add(value)
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache_entries[oldest_key]
        del self.access_times[oldest_key]
    
    def cleanup_expired(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, access_time in self.access_times.items()
            if current_time - access_time > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache_entries[key]
            del self.access_times[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get cache memory usage statistics"""
        return {
            "cache_size": len(self.cache_entries),
            "max_cache_size": self.max_cache_size,
            "memory_usage_mb": sys.getsizeof(self.cache_entries) / (1024 * 1024),
            "ttl_seconds": self.ttl_seconds
        }

def create_memory_monitor() -> MemoryProfiler:
    """Create and configure memory monitor"""
    profiler = MemoryProfiler(enable_tracemalloc=True)
    profiler.start_monitoring(interval=10.0)  # Monitor every 10 seconds
    return profiler

def optimize_system_memory():
    """System-wide memory optimization"""
    logger.info("Starting system memory optimization...")
    
    # Create profiler
    profiler = MemoryProfiler()
    
    # Take initial snapshot
    initial_snapshot = profiler.take_snapshot()
    logger.info(f"Initial memory usage: {initial_snapshot.memory_usage / (1024*1024):.2f} MB")
    
    # Perform optimization
    profiler.optimize_memory()
    
    # Take final snapshot
    final_snapshot = profiler.take_snapshot()
    logger.info(f"Final memory usage: {final_snapshot.memory_usage / (1024*1024):.2f} MB")
    
    # Calculate improvement
    improvement = initial_snapshot.memory_usage - final_snapshot.memory_usage
    logger.info(f"Memory freed: {improvement / (1024*1024):.2f} MB")
    
    return profiler.get_memory_report()

if __name__ == "__main__":
    # Run memory optimization
    report = optimize_system_memory()
    print("Memory Optimization Report:")
    print(report)
