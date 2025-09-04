"""
Quick Demo Script - See DoganAI Performance in Action!
Run this to see immediate results without dependencies
"""
import asyncio
import time
import json
import random
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import our performance modules
from improvements.performance import (
    TTLCache, HybridCache, CacheConfig, CacheStrategy,
    BatchProcessor, PerformanceMonitor
)


class QuickDemo:
    """Quick demonstration of DoganAI performance improvements"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
    def demo_cache_performance(self):
        """Demonstrate caching performance improvements"""
        print("?? CACHE PERFORMANCE DEMO")
        print("=" * 50)
        
        # Create caches
        cache = TTLCache(max_size=1000, ttl_seconds=3600, enable_compression=True)
        
        # Test data
        test_data = [
            {"compliance_mapping": f"MAP-BANK-{i}", "score": random.uniform(70, 95), "details": "x" * 100}
            for i in range(100)
        ]
        
        print("Testing cache vs no-cache performance...")
        
        # Simulate database query without cache
        def simulate_db_query(mapping_id: str) -> Dict[str, Any]:
            time.sleep(0.01)  # Simulate 10ms database query
            return {
                "mapping": mapping_id,
                "score": random.uniform(70, 95),
                "timestamp": datetime.now().isoformat(),
                "details": {"rules": 50, "passed": 45, "failed": 5}
            }
        
        # Test without cache
        start_time = time.time()
        uncached_results = []
        
        for i in range(50):
            mapping_id = f"MAP-BANK-{random.randint(1, 20)}"  # 20% cache hit potential
            result = simulate_db_query(mapping_id)
            uncached_results.append(result)
        
        uncached_time = time.time() - start_time
        
        # Test with cache
        start_time = time.time()
        cached_results = []
        
        for i in range(50):
            mapping_id = f"MAP-BANK-{random.randint(1, 20)}"
            
            # Try cache first
            cached_result = cache.get(mapping_id)
            if cached_result is None:
                # Cache miss - get from "database"
                cached_result = simulate_db_query(mapping_id)
                cache.set(mapping_id, cached_result)
            
            cached_results.append(cached_result)
        
        cached_time = time.time() - start_time
        
        # Show results
        cache_stats = cache.metrics.get_stats()
        improvement = ((uncached_time - cached_time) / uncached_time) * 100
        
        print(f"? Without Cache: {uncached_time:.3f} seconds")
        print(f"? With Cache: {cached_time:.3f} seconds")
        print(f"? Performance Improvement: {improvement:.1f}%")
        print(f"? Cache Hit Rate: {cache_stats['hit_rate']:.2%}")
        print(f"? Speed Increase: {uncached_time/cached_time:.1f}x faster")
        
        return {
            "uncached_time": uncached_time,
            "cached_time": cached_time,
            "improvement_percent": improvement,
            "cache_stats": cache_stats
        }
    
    async def demo_batch_processing(self):
        """Demonstrate batch processing performance"""
        print("\n?? BATCH PROCESSING DEMO")
        print("=" * 50)
        
        batch_processor = BatchProcessor(batch_size=10, max_wait_time=1.0)
        
        async def process_compliance_check(items: List[str]) -> List[Dict[str, Any]]:
            """Simulate batch compliance processing"""
            await asyncio.sleep(0.2)  # Simulate processing time
            return [
                {
                    "mapping": item,
                    "status": "compliant" if random.random() > 0.2 else "non-compliant",
                    "score": random.uniform(70, 95),
                    "processed_at": datetime.now().isoformat()
                }
                for item in items
            ]
        
        # Sequential processing
        print("Testing sequential vs batch processing...")
        
        mappings = [f"MAP-GOV-{i}" for i in range(25)]
        
        # Sequential
        start_time = time.time()
        sequential_results = []
        
        for mapping in mappings:
            result = await process_compliance_check([mapping])
            sequential_results.extend(result)
        
        sequential_time = time.time() - start_time
        
        # Batch processing
        start_time = time.time()
        batch_tasks = []
        
        for mapping in mappings:
            task = batch_processor.add_item(mapping, process_compliance_check)
            batch_tasks.append(task)
        
        batch_results = await asyncio.gather(*batch_tasks)
        batch_time = time.time() - start_time
        
        improvement = ((sequential_time - batch_time) / sequential_time) * 100
        
        print(f"? Sequential Processing: {sequential_time:.3f} seconds")
        print(f"? Batch Processing: {batch_time:.3f} seconds")
        print(f"? Performance Improvement: {improvement:.1f}%")
        print(f"? Speed Increase: {sequential_time/batch_time:.1f}x faster")
        print(f"? Items Processed: {len(batch_results)}")
        
        return {
            "sequential_time": sequential_time,
            "batch_time": batch_time,
            "improvement_percent": improvement,
            "items_processed": len(batch_results)
        }
    
    def demo_compression_efficiency(self):
        """Demonstrate compression efficiency"""
        print("\n??? COMPRESSION EFFICIENCY DEMO")
        print("=" * 50)
        
        # Create caches with and without compression
        uncompressed_cache = TTLCache(max_size=1000, enable_compression=False)
        compressed_cache = TTLCache(max_size=1000, enable_compression=True)
        
        # Create large test data
        large_compliance_data = {
            "policy_details": "This is a detailed compliance policy document. " * 100,
            "rules": [f"Rule {i}: Detailed compliance requirement description" for i in range(50)],
            "vendors": [
                {
                    "name": f"Vendor {i}",
                    "capabilities": ["Feature A", "Feature B", "Feature C"] * 10,
                    "compliance_matrix": [[random.randint(0, 1) for _ in range(20)] for _ in range(10)]
                }
                for i in range(10)
            ]
        }
        
        # Store in both caches
        for i in range(50):
            key = f"compliance_data_{i}"
            uncompressed_cache.set(key, large_compliance_data)
            compressed_cache.set(key, large_compliance_data)
        
        # Calculate memory usage (simplified)
        import sys
        uncompressed_size = sys.getsizeof(str(uncompressed_cache._cache))
        compressed_size = sys.getsizeof(str(compressed_cache._cache))
        
        compression_ratio = (uncompressed_size - compressed_size) / uncompressed_size * 100
        
        print(f"? Uncompressed Cache Size: ~{uncompressed_size//1024} KB")
        print(f"? Compressed Cache Size: ~{compressed_size//1024} KB")
        print(f"? Compression Savings: {compression_ratio:.1f}%")
        print(f"? Memory Efficiency: {uncompressed_size/compressed_size:.1f}x better")
        
        return {
            "uncompressed_size": uncompressed_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio
        }
    
    def demo_performance_monitoring(self):
        """Demonstrate performance monitoring"""
        print("\n?? PERFORMANCE MONITORING DEMO")
        print("=" * 50)
        
        @self.performance_monitor.monitor_function
        def compliance_evaluation(mapping: str, complexity: str = "normal") -> Dict[str, Any]:
            """Simulated compliance evaluation function"""
            if complexity == "simple":
                time.sleep(0.1)
            elif complexity == "normal":
                time.sleep(0.3)
            else:  # complex
                time.sleep(0.7)
            
            return {
                "mapping": mapping,
                "status": "evaluated",
                "score": random.uniform(70, 95),
                "complexity": complexity
            }
        
        # Run various evaluations
        print("Running monitored compliance evaluations...")
        
        evaluations = [
            ("MAP-SIMPLE-1", "simple"),
            ("MAP-NORMAL-1", "normal"),
            ("MAP-COMPLEX-1", "complex"),
            ("MAP-NORMAL-2", "normal"),
            ("MAP-SIMPLE-2", "simple"),
        ]
        
        for mapping, complexity in evaluations:
            result = compliance_evaluation(mapping, complexity)
            print(f"  ? Evaluated {mapping} ({complexity})")
        
        # Get performance report
        report = self.performance_monitor.get_performance_report()
        
        print(f"\n?? Performance Statistics:")
        func_stats = report["function_stats"]["compliance_evaluation"]
        print(f"? Total Calls: {func_stats['call_count']}")
        print(f"? Success Rate: {func_stats['success_count']/func_stats['call_count']:.2%}")
        print(f"? Average Time: {func_stats['avg_time']:.3f} seconds")
        print(f"? Min Time: {func_stats['min_time']:.3f} seconds")
        print(f"? Max Time: {func_stats['max_time']:.3f} seconds")
        
        return report
    
    def demo_real_world_scenario(self):
        """Demonstrate real-world compliance scenario"""
        print("\n?? REAL-WORLD SCENARIO DEMO")
        print("=" * 50)
        print("Scenario: Saudi Bank needs to evaluate 100 compliance mappings")
        
        # Setup
        cache = TTLCache(max_size=500, ttl_seconds=1800)  # 30 minute cache
        
        # Simulate compliance mappings
        mappings = [
            "MAP-SAMA-CoreBanking-IBM",
            "MAP-SAMA-RiskMgmt-Microsoft", 
            "MAP-NCA-DataSecurity-AWS",
            "MAP-SAMA-AuditTrail-Oracle",
            "MAP-NCA-IdentityMgmt-Azure"
        ] * 20  # 100 total evaluations
        
        def evaluate_compliance_mapping(mapping: str) -> Dict[str, Any]:
            """Simulate compliance evaluation"""
            time.sleep(0.05)  # 50ms evaluation time
            
            base_score = {
                "IBM": 92,
                "Microsoft": 89,
                "AWS": 87,
                "Oracle": 85,
                "Azure": 88
            }
            
            vendor = mapping.split('-')[-1]
            score = base_score.get(vendor, 80) + random.uniform(-5, 5)
            
            return {
                "mapping": mapping,
                "vendor": vendor,
                "compliance_score": round(score, 1),
                "status": "compliant" if score >= 85 else "needs_attention",
                "evaluated_at": datetime.now().isoformat(),
                "evaluation_time": 0.05
            }
        
        print("Running 100 compliance evaluations...")
        
        # Without cache
        start_time = time.time()
        results_no_cache = []
        
        for mapping in mappings:
            result = evaluate_compliance_mapping(mapping)
            results_no_cache.append(result)
        
        time_no_cache = time.time() - start_time
        
        # With cache
        start_time = time.time()
        results_with_cache = []
        
        for mapping in mappings:
            cached_result = cache.get(mapping)
            if cached_result is None:
                cached_result = evaluate_compliance_mapping(mapping)
                cache.set(mapping, cached_result)
            results_with_cache.append(cached_result)
        
        time_with_cache = time.time() - start_time
        
        # Analysis
        cache_stats = cache.metrics.get_stats()
        unique_mappings = len(set(mappings))
        cache_hits = int(cache_stats['hits'])
        time_saved = time_no_cache - time_with_cache
        
        print(f"\n?? RESULTS:")
        print(f"? Total Evaluations: {len(mappings)}")
        print(f"? Unique Mappings: {unique_mappings}")
        print(f"? Time without cache: {time_no_cache:.2f} seconds")
        print(f"? Time with cache: {time_with_cache:.2f} seconds")
        print(f"? Time saved: {time_saved:.2f} seconds ({time_saved/time_no_cache*100:.1f}%)")
        print(f"? Cache hits: {cache_hits}/{len(mappings)} ({cache_stats['hit_rate']:.2%})")
        print(f"? Performance improvement: {time_no_cache/time_with_cache:.1f}x faster")
        
        # Compliance summary
        compliant_count = sum(1 for r in results_with_cache if r['status'] == 'compliant')
        avg_score = sum(r['compliance_score'] for r in results_with_cache) / len(results_with_cache)
        
        print(f"\n??? COMPLIANCE SUMMARY:")
        print(f"? Compliant mappings: {compliant_count}/{len(mappings)} ({compliant_count/len(mappings)*100:.1f}%)")
        print(f"? Average compliance score: {avg_score:.1f}")
        print(f"? Time per evaluation: {time_with_cache/len(mappings)*1000:.1f}ms")
        
        return {
            "evaluations": len(mappings),
            "time_saved": time_saved,
            "performance_improvement": time_no_cache/time_with_cache,
            "cache_hit_rate": cache_stats['hit_rate'],
            "compliance_rate": compliant_count/len(mappings),
            "avg_score": avg_score
        }
    
    async def run_complete_demo(self):
        """Run complete demonstration"""
        print("?? DOGANAI COMPLIANCE KIT - PERFORMANCE DEMO")
        print("=" * 60)
        print("Demonstrating enterprise-grade performance improvements")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all demos
        cache_results = self.demo_cache_performance()
        batch_results = await self.demo_batch_processing()
        compression_results = self.demo_compression_efficiency()
        monitoring_results = self.demo_performance_monitoring()
        scenario_results = self.demo_real_world_scenario()
        
        total_time = time.time() - start_time
        
        # Summary
        print(f"\n?? DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"?? Total demo time: {total_time:.2f} seconds")
        print(f"?? Cache Performance: {cache_results['improvement_percent']:.1f}% faster")
        print(f"?? Batch Processing: {batch_results['improvement_percent']:.1f}% faster")
        print(f"??? Memory Savings: {compression_results['compression_ratio']:.1f}%")
        print(f"?? Real-world Scenario: {scenario_results['performance_improvement']:.1f}x faster")
        
        print(f"\n? YOUR DOGANAI COMPLIANCE KIT IS READY FOR:")
        print(f"   • Saudi banks with 1000+ compliance checks")
        print(f"   • Government agencies with complex regulations")
        print(f"   • Enterprise deployments requiring high performance")
        print(f"   • Mobile teams needing fast compliance validation")
        
        return {
            "cache_demo": cache_results,
            "batch_demo": batch_results,
            "compression_demo": compression_results,
            "monitoring_demo": monitoring_results,
            "scenario_demo": scenario_results,
            "total_demo_time": total_time
        }


def main():
    """Run the quick demo"""
    print("Starting DoganAI Performance Demo...")
    print("No external dependencies required!")
    print()
    
    demo = QuickDemo()
    
    try:
        # Run the demo
        results = asyncio.run(demo.run_complete_demo())
        
        # Save results
        with open("demo_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n?? Demo results saved to demo_results.json")
        print(f"\n?? Next Steps:")
        print(f"   1. Run: python improvements/enhanced_api.py")
        print(f"   2. Test: curl http://localhost:8000/health/enhanced")
        print(f"   3. Monitor: curl http://localhost:8000/metrics/performance")
        print(f"   4. Deploy: python improvements/deploy.py --check")
        
    except KeyboardInterrupt:
        print("\n?? Demo interrupted by user")
    except Exception as e:
        print(f"\n? Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()