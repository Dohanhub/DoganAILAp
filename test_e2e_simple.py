#!/usr/bin/env python3
"""
Simple End-to-End Test for DoganAI Compliance Kit
Uses only standard library - no external dependencies
"""
import urllib.request
import urllib.parse
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode(), json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.reason}
    except Exception as e:
        return 0, {"error": str(e)}

def test_health():
    """Test system health"""
    print("🔍 Testing system health...")
    status, data = make_request(f"{API_BASE}/health")
    
    if status == 200 and data.get("status") == "operational":
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {status} - {data}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    status, data = make_request(f"{API_BASE}/")
    
    if status == 200 and "Dogan AI" in data.get("platform", ""):
        print("✅ Root endpoint working")
        print(f"   Platform: {data.get('platform')}")
        print(f"   Version: {data.get('version')}")
        return True
    else:
        print(f"❌ Root endpoint failed: {status}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    print("🔍 Testing metrics...")
    status, data = make_request(f"{API_BASE}/metrics")
    
    if status == 200 and "metrics" in data:
        print("✅ Metrics endpoint working")
        metrics = data["metrics"]
        print(f"   Organizations: {metrics.get('total_orgs', 0)}")
        print(f"   Assessments: {metrics.get('total_assessments', 0)}")
        return True
    else:
        print(f"❌ Metrics failed: {status}")
        return False

def test_frameworks():
    """Test frameworks endpoint"""
    print("🔍 Testing frameworks...")
    status, data = make_request(f"{API_BASE}/api/frameworks")
    
    if status == 200 and isinstance(data, list):
        print("✅ Frameworks endpoint working")
        saudi_frameworks = [f for f in data if f.get("is_saudi")]
        print(f"   Total frameworks: {len(data)}")
        print(f"   Saudi frameworks: {len(saudi_frameworks)}")
        return True
    else:
        print(f"❌ Frameworks failed: {status}")
        return False

def test_organizations():
    """Test organizations endpoint"""
    print("🔍 Testing organizations...")
    status, data = make_request(f"{API_BASE}/api/organizations")
    
    if status == 200 and isinstance(data, list):
        print("✅ Organizations endpoint working")
        print(f"   Total organizations: {len(data)}")
        return True
    else:
        print(f"❌ Organizations failed: {status}")
        return False

def test_dashboard_stats():
    """Test dashboard stats"""
    print("🔍 Testing dashboard stats...")
    status, data = make_request(f"{API_BASE}/api/dashboard/stats")
    
    if status == 200:
        print("✅ Dashboard stats working")
        print(f"   Organizations: {data.get('organizations', 0)}")
        print(f"   Assessments: {data.get('assessments', 0)}")
        print(f"   Open risks: {data.get('open_risks', 0)}")
        return True
    else:
        print(f"❌ Dashboard stats failed: {status}")
        return False

def test_security_headers():
    """Test security headers"""
    print("🔍 Testing security configuration...")
    
    req = urllib.request.Request(f"{API_BASE}/health")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            cors_header = response.headers.get("Access-Control-Allow-Origin", "")
            
            if cors_header != "*":
                print("✅ CORS security properly configured")
                print(f"   CORS Origin: {cors_header or 'Not set'}")
                return True
            else:
                print("❌ CORS wildcard detected (security risk)")
                return False
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

def run_quick_tests():
    """Run quick validation tests"""
    print("🚀 DoganAI Compliance Kit - Quick E2E Test")
    print("=" * 50)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {API_BASE}")
    print()
    
    start_time = time.time()
    tests = [
        test_health,
        test_root_endpoint,
        test_metrics,
        test_frameworks,
        test_organizations,
        test_dashboard_stats,
        test_security_headers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    duration = time.time() - start_time
    
    print("=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"📈 Results: {passed}/{total} tests passed")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    
    if passed == total:
        print("🎉 All tests passed! System is operational.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed.")
        print("💡 Ensure the backend server is running on port 8000")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)
