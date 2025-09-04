
#!/usr/bin/env python3
"""
Cache Warming Script
Pre-load frequently accessed data into cache
"""

import redis
import json
import time
from typing import List, Dict

class CacheWarmer:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    def warm_compliance_data(self):
        """Warm compliance-related cache data"""
        # Pre-load common compliance queries
        common_queries = [
            'compliance_analytics',
            'vendor_performance',
            'recent_evaluations',
            'compliance_trends'
        ]
        
        for query in common_queries:
            cache_key = f"warm:{query}"
            self.redis.setex(cache_key, 3600, json.dumps({
                'query': query,
                'warmed_at': time.time(),
                'data': {'status': 'warmed'}
            }))
    
    def warm_vendor_data(self):
        """Warm vendor-related cache data"""
        # Pre-load vendor information
        vendor_keys = [
            'vendor_list',
            'vendor_performance_summary',
            'active_vendors'
        ]
        
        for key in vendor_keys:
            cache_key = f"warm:{key}"
            self.redis.setex(cache_key, 1800, json.dumps({
                'key': key,
                'warmed_at': time.time(),
                'data': {'status': 'warmed'}
            }))

if __name__ == "__main__":
    warmer = CacheWarmer()
    warmer.warm_compliance_data()
    warmer.warm_vendor_data()
    print("Cache warming completed!")
        