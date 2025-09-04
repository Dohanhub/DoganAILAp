#!/usr/bin/env python3
"""
Performance Monitoring and Caching System
Implements performance monitoring, caching layer, and optimization features
"""

import sqlite3
import json
import time
import threading
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import wraps
import pickle

class PerformanceCache:
    """In-memory caching system with TTL and performance tracking"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.access_stats = {}
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if datetime.now() > entry['expires']:
                    del self.cache[key]
                    return None
                
                # Update access stats
                self._update_access_stats(key, 'hit')
                return entry['value']
            
            self._update_access_stats(key, 'miss')
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl
            
            expires = datetime.now() + timedelta(seconds=ttl)
            self.cache[key] = {
                'value': value,
                'expires': expires,
                'created': datetime.now()
            }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.access_stats.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total_hits = sum(stats['hits'] for stats in self.access_stats.values())
            total_misses = sum(stats['misses'] for stats in self.access_stats.values())
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_entries': len(self.cache),
                'total_requests': total_requests,
                'cache_hits': total_hits,
                'cache_misses': total_misses,
                'hit_rate_percent': round(hit_rate, 2),
                'memory_usage_keys': len(self.cache)
            }
    
    def _update_access_stats(self, key: str, access_type: str):
        """Update access statistics"""
        if key not in self.access_stats:
            self.access_stats[key] = {'hits': 0, 'misses': 0}
        
        if access_type == 'hit':
            self.access_stats[key]['hits'] += 1
        elif access_type == 'miss':
            self.access_stats[key]['misses'] += 1

class PerformanceMonitor:
    """Performance monitoring and optimization system"""
    
    def __init__(self):
        self.cache = PerformanceCache()
        self.query_stats = {}
        self.performance_history = []
        self.monitoring_active = False
        
    def cached_query(self, ttl: int = 300):
        """Decorator for caching database queries"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = self._create_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache first
                result = self.cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache the result
                self.cache.set(cache_key, result, ttl)
                
                # Track performance
                self._track_query_performance(func.__name__, execution_time)
                
                return result
            return wrapper
        return decorator
    
    def _create_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a unique cache key from function name and arguments"""
        key_data = {
            'function': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _track_query_performance(self, func_name: str, execution_time: float):
        """Track query performance statistics"""
        if func_name not in self.query_stats:
            self.query_stats[func_name] = {
                'total_calls': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'recent_times': []
            }
        
        stats = self.query_stats[func_name]
        stats['total_calls'] += 1
        stats['total_time'] += execution_time
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        
        # Keep last 100 execution times
        stats['recent_times'].append(execution_time)
        if len(stats['recent_times']) > 100:
            stats['recent_times'] = stats['recent_times'][-100:]
    
    def get_compliance_evaluations_cached(self, mapping_pattern: str = None) -> List[Dict]:
        """Cached version of compliance evaluations query"""
        
        @self.cached_query(ttl=600)  # 10 minutes cache
        def _get_evaluations(pattern):
            conn = sqlite3.connect('doganai_compliance.db')
            cursor = conn.cursor()
            
            if pattern:
                            cursor.execute('''
                SELECT mapping, vendor_id, compliance_percentage, missing_items, 
                       last_evaluation, evaluation_details
                FROM evaluation_results 
                WHERE mapping LIKE ?
                ORDER BY compliance_percentage DESC
            ''', (f'{pattern}%',))
        else:
            cursor.execute('''
                SELECT mapping, vendor_id, compliance_percentage, missing_items,
                       last_evaluation, evaluation_details
                FROM evaluation_results 
                ORDER BY compliance_percentage DESC
            ''')
        
        columns = ['mapping', 'vendor_id', 'compliance_percentage', 'missing_items',
                  'last_evaluation', 'evaluation_details']
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        
        return _get_evaluations(mapping_pattern)
    
    def get_policies_cached(self, authority: str = None) -> List[Dict]:
        """Cached version of policies query"""
        
        @self.cached_query(ttl=1800)  # 30 minutes cache (policies change less frequently)
        def _get_policies(auth):
            conn = sqlite3.connect('doganai_compliance.db')
            cursor = conn.cursor()
            
            if auth:
                cursor.execute('''
                    SELECT id, authority, version, description, is_active
                    FROM policies 
                    WHERE authority = ? AND is_active = 1
                ''', (auth,))
            else:
                cursor.execute('''
                    SELECT id, authority, version, description, is_active
                    FROM policies 
                    WHERE is_active = 1
                    ORDER BY authority
                ''')
            
            columns = ['id', 'authority', 'version', 'description', 'is_active']
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        
        return _get_policies(authority)
    
    def get_vendor_compliance_summary_cached(self) -> Dict:
        """Cached vendor compliance summary with performance optimization"""
        
        @self.cached_query(ttl=300)  # 5 minutes cache
        def _get_vendor_summary():
            conn = sqlite3.connect('doganai_compliance.db')
            cursor = conn.cursor()
            
            # Optimized query using indexes
            cursor.execute('''
                SELECT 
                    vendor_id,
                    COUNT(*) as total_evaluations,
                    AVG(compliance_percentage) as avg_compliance,
                    MAX(compliance_percentage) as max_compliance,
                    MIN(compliance_percentage) as min_compliance
                FROM evaluation_results
                GROUP BY vendor_id
                ORDER BY avg_compliance DESC
            ''')
            
            results = {}
            for row in cursor.fetchall():
                vendor_id, total, avg_comp, max_comp, min_comp = row
                results[vendor_id] = {
                    'total_evaluations': total,
                    'average_compliance': round(avg_comp, 2),
                    'max_compliance': max_comp,
                    'min_compliance': min_comp
                }
            
            conn.close()
            return results
        
        return _get_vendor_summary()
    
    def run_performance_analysis(self) -> Dict:
        """Run comprehensive performance analysis"""
        
        print("⚡ PERFORMANCE MONITORING & ANALYSIS")
        print("="*40)
        print(f"Analysis Time: {datetime.now().isoformat()}")
        print()
        
        analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'cache_performance': {},
            'query_performance': {},
            'database_optimization': {},
            'system_performance': {},
            'recommendations': []
        }
        
        # 1. Cache Performance Analysis
        print("💾 CACHE PERFORMANCE")
        print("="*20)
        cache_performance = self._analyze_cache_performance()
        analysis_report['cache_performance'] = cache_performance
        
        # 2. Query Performance Analysis
        print(f"\n🔍 QUERY PERFORMANCE")
        print("="*20)
        query_performance = self._analyze_query_performance()
        analysis_report['query_performance'] = query_performance
        
        # 3. Database Optimization Analysis
        print(f"\n🗄️ DATABASE OPTIMIZATION")
        print("="*25)
        db_optimization = self._analyze_database_optimization()
        analysis_report['database_optimization'] = db_optimization
        
        # 4. System Performance Tests
        print(f"\n🚀 SYSTEM PERFORMANCE TESTS")
        print("="*30)
        system_performance = self._run_system_performance_tests()
        analysis_report['system_performance'] = system_performance
        
        # 5. Generate Recommendations
        recommendations = self._generate_performance_recommendations(analysis_report)
        analysis_report['recommendations'] = recommendations
        
        # Save performance report
        with open('performance_analysis_report.json', 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\n🎯 PERFORMANCE SUMMARY")
        print("="*25)
        print(f"   Cache Hit Rate: {cache_performance.get('hit_rate_percent', 0)}%")
        print(f"   Average Query Time: {query_performance.get('average_query_time', 0):.3f}s")
        print(f"   Recommendations: {len(recommendations)}")
        print(f"   Report saved: performance_analysis_report.json")
        
        return analysis_report
    
    def _analyze_cache_performance(self) -> Dict:
        """Analyze cache performance"""
        
        cache_stats = self.cache.get_stats()
        
        print(f"   Cache Entries: {cache_stats['total_entries']}")
        print(f"   Hit Rate: {cache_stats['hit_rate_percent']}%")
        print(f"   Total Requests: {cache_stats['total_requests']}")
        
        # Determine cache performance status
        hit_rate = cache_stats['hit_rate_percent']
        if hit_rate >= 80:
            status = 'Excellent'
        elif hit_rate >= 60:
            status = 'Good'
        elif hit_rate >= 40:
            status = 'Fair'
        else:
            status = 'Poor'
        
        cache_stats['performance_status'] = status
        print(f"   Status: {status}")
        
        return cache_stats
    
    def _analyze_query_performance(self) -> Dict:
        """Analyze query performance statistics"""
        
        if not self.query_stats:
            print("   No query statistics available")
            return {'message': 'No query statistics available'}
        
        total_calls = sum(stats['total_calls'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        avg_time = total_time / total_calls if total_calls > 0 else 0
        
        # Find slowest queries
        slowest_queries = []
        for func_name, stats in self.query_stats.items():
            avg_func_time = stats['total_time'] / stats['total_calls']
            slowest_queries.append({
                'function': func_name,
                'avg_time': round(avg_func_time, 4),
                'max_time': round(stats['max_time'], 4),
                'total_calls': stats['total_calls']
            })
        
        slowest_queries.sort(key=lambda x: x['avg_time'], reverse=True)
        
        print(f"   Total Query Calls: {total_calls}")
        print(f"   Average Query Time: {avg_time:.3f}s")
        print(f"   Slowest Query: {slowest_queries[0]['function'] if slowest_queries else 'N/A'}")
        
        return {
            'total_calls': total_calls,
            'average_query_time': round(avg_time, 4),
            'slowest_queries': slowest_queries[:5],  # Top 5 slowest
            'query_functions': len(self.query_stats)
        }
    
    def _analyze_database_optimization(self) -> Dict:
        """Analyze database optimization status"""
        
        try:
            conn = sqlite3.connect('doganai_compliance.db')
            cursor = conn.cursor()
            
            # Check index usage
            cursor.execute("PRAGMA index_list(evaluation_results)")
            eval_indexes = len(cursor.fetchall())
            
            cursor.execute("PRAGMA index_list(policies)")
            policy_indexes = len(cursor.fetchall())
            
            # Check table sizes
            cursor.execute("SELECT COUNT(*) FROM evaluation_results")
            eval_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM policies")
            policy_count = cursor.fetchone()[0]
            
            # Test query performance with EXPLAIN QUERY PLAN
            cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM evaluation_results WHERE vendor_id = 'IBM-WATSON-2024'")
            plan = cursor.fetchall()
            uses_index = any('USING INDEX' in str(row) for row in plan)
            
            conn.close()
            
            optimization_status = {
                'evaluation_indexes': eval_indexes,
                'policy_indexes': policy_indexes,
                'evaluation_records': eval_count,
                'policy_records': policy_count,
                'index_utilization': uses_index
            }
            
            print(f"   Evaluation Indexes: {eval_indexes}")
            print(f"   Policy Indexes: {policy_indexes}")
            print(f"   Index Utilization: {'✅' if uses_index else '❌'}")
            
            return optimization_status
            
        except Exception as e:
            print(f"   Database analysis error: {e}")
            return {'error': str(e)}
    
    def _run_system_performance_tests(self) -> Dict:
        """Run system performance tests"""
        
        tests = []
        
        # Test 1: Database query speed
        start_time = time.time()
        evaluations = self.get_compliance_evaluations_cached()
        db_query_time = time.time() - start_time
        
        tests.append({
            'name': 'Database Query Speed',
            'execution_time': round(db_query_time, 4),
            'result_count': len(evaluations),
            'status': 'Fast' if db_query_time < 1.0 else 'Slow'
        })
        
        # Test 2: Cache performance
        start_time = time.time()
        cached_evaluations = self.get_compliance_evaluations_cached()  # Should be cached
        cache_query_time = time.time() - start_time
        
        tests.append({
            'name': 'Cache Query Speed',
            'execution_time': round(cache_query_time, 4),
            'result_count': len(cached_evaluations),
            'status': 'Fast' if cache_query_time < 0.1 else 'Slow'
        })
        
        # Test 3: Vendor summary performance
        start_time = time.time()
        vendor_summary = self.get_vendor_compliance_summary_cached()
        summary_query_time = time.time() - start_time
        
        tests.append({
            'name': 'Vendor Summary Speed',
            'execution_time': round(summary_query_time, 4),
            'result_count': len(vendor_summary),
            'status': 'Fast' if summary_query_time < 2.0 else 'Slow'
        })
        
        for test in tests:
            status_icon = '✅' if test['status'] == 'Fast' else '⚠️'
            print(f"   {status_icon} {test['name']}: {test['execution_time']}s ({test['result_count']} results)")
        
        return {
            'tests': tests,
            'total_tests': len(tests),
            'fast_tests': len([t for t in tests if t['status'] == 'Fast']),
            'slow_tests': len([t for t in tests if t['status'] == 'Slow'])
        }
    
    def _generate_performance_recommendations(self, analysis: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Cache recommendations
        cache_hit_rate = analysis['cache_performance'].get('hit_rate_percent', 0)
        if cache_hit_rate < 50:
            recommendations.append("Increase cache TTL for frequently accessed data")
        if cache_hit_rate == 0:
            recommendations.append("Implement caching for database queries")
        
        # Query performance recommendations
        query_perf = analysis['query_performance']
        if query_perf.get('average_query_time', 0) > 1.0:
            recommendations.append("Optimize slow database queries with better indexing")
        
        # Database optimization recommendations
        db_opt = analysis['database_optimization']
        if not db_opt.get('index_utilization', True):
            recommendations.append("Review and optimize database index usage")
        
        # System performance recommendations
        sys_perf = analysis['system_performance']
        slow_tests = sys_perf.get('slow_tests', 0)
        if slow_tests > 0:
            recommendations.append("Optimize slow system performance tests")
        
        # General recommendations
        recommendations.extend([
            "Implement connection pooling for database connections",
            "Add monitoring for query execution times",
            "Consider implementing Redis for distributed caching",
            "Set up automated performance regression testing"
        ])
        
        print(f"\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        return recommendations

def main():
    """Main performance monitoring function"""
    
    monitor = PerformanceMonitor()
    
    # Run some test queries to generate statistics
    print("🔄 Running performance tests...")
    
    # Test cached queries
    evaluations = monitor.get_compliance_evaluations_cached()
    policies = monitor.get_policies_cached()
    vendor_summary = monitor.get_vendor_compliance_summary_cached()
    
    # Test cache hits
    evaluations_cached = monitor.get_compliance_evaluations_cached()  # Should be cached
    
    print(f"   Loaded {len(evaluations)} evaluations")
    print(f"   Loaded {len(policies)} policies")
    print(f"   Loaded {len(vendor_summary)} vendor summaries")
    
    # Run comprehensive analysis
    analysis_report = monitor.run_performance_analysis()
    
    return analysis_report

if __name__ == "__main__":
    main()
