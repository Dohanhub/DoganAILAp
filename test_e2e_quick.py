#!/usr/bin/env python3
"""
Quick End-to-End Test for DoganAI Compliance Kit
Fast validation of core functionality without heavy dependencies
"""
import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
TEST_USER = {
    "username": "quicktest",
    "password": "Test123!",
    "email": "quicktest@doganai.com",
    "full_name": "Quick Test User",
    "role": "user"
}

class QuickE2ETest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.org_id = None
        self.results = []

    def log_result(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({"test": test_name, "success": success, "message": message})
        print(f"{status} {test_name}: {message}")

    def test_health(self):
        """Test system health"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=5)
            success = response.status_code == 200 and response.json().get("status") == "operational"
            self.log_result("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False

    def test_registration(self):
        """Test user registration"""
        try:
            response = self.session.post(f"{API_BASE}/register", json=TEST_USER, timeout=10)
            success = response.status_code in [200, 400]  # 400 if user exists
            message = response.json().get("message", response.json().get("detail", ""))
            self.log_result("User Registration", success, message)
            return success
        except Exception as e:
            self.log_result("User Registration", False, str(e))
            return False

    def test_login(self):
        """Test user login and token generation"""
        try:
            login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
            response = self.session.post(f"{API_BASE}/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                success = bool(self.auth_token)
                self.log_result("User Login", success, "Token received" if success else "No token")
                return success
            else:
                self.log_result("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("User Login", False, str(e))
            return False

    def test_protected_endpoint(self):
        """Test protected endpoint access"""
        try:
            response = self.session.get(f"{API_BASE}/api/auth/me", timeout=5)
            success = response.status_code == 200
            message = "Authenticated" if success else f"Status: {response.status_code}"
            self.log_result("Protected Endpoint", success, message)
            return success
        except Exception as e:
            self.log_result("Protected Endpoint", False, str(e))
            return False

    def test_organization_crud(self):
        """Test organization creation"""
        try:
            org_data = {
                "name": f"Test Org {int(time.time())}",
                "sector": "Technology",
                "city": "Riyadh",
                "size": "Medium"
            }
            response = self.session.post(f"{API_BASE}/api/organizations", json=org_data, timeout=10)
            
            if response.status_code == 200:
                self.org_id = response.json().get("id")
                success = bool(self.org_id)
                self.log_result("Organization Creation", success, f"ID: {self.org_id}")
                return success
            else:
                self.log_result("Organization Creation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Organization Creation", False, str(e))
            return False

    def test_frameworks(self):
        """Test framework listing"""
        try:
            response = self.session.get(f"{API_BASE}/api/frameworks", timeout=5)
            success = response.status_code == 200
            if success:
                frameworks = response.json()
                count = len(frameworks)
                saudi_count = len([f for f in frameworks if f.get("is_saudi")])
                message = f"{count} frameworks ({saudi_count} Saudi)"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_result("Framework Listing", success, message)
            return success
        except Exception as e:
            self.log_result("Framework Listing", False, str(e))
            return False

    def test_assessment_creation(self):
        """Test assessment creation"""
        if not self.org_id:
            self.log_result("Assessment Creation", False, "No organization ID")
            return False
        
        try:
            # Get first framework
            frameworks_response = self.session.get(f"{API_BASE}/api/frameworks", timeout=5)
            if frameworks_response.status_code != 200:
                self.log_result("Assessment Creation", False, "Cannot get frameworks")
                return False
            
            frameworks = frameworks_response.json()
            if not frameworks:
                self.log_result("Assessment Creation", False, "No frameworks available")
                return False
            
            assessment_data = {
                "organization_id": self.org_id,
                "framework_code": frameworks[0]["code"],
                "assessment_type": "automated"
            }
            
            response = self.session.post(f"{API_BASE}/api/assessments", json=assessment_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                score = data.get("score", 0)
                message = f"Score: {score}%"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_result("Assessment Creation", success, message)
            return success
        except Exception as e:
            self.log_result("Assessment Creation", False, str(e))
            return False

    def test_risk_management(self):
        """Test risk creation and calculation"""
        if not self.org_id:
            self.log_result("Risk Management", False, "No organization ID")
            return False
        
        try:
            risk_data = {
                "organization_id": self.org_id,
                "title": "Test Security Risk",
                "severity": "high",
                "likelihood": "medium",
                "category": "Security",
                "description": "E2E test risk"
            }
            
            response = self.session.post(f"{API_BASE}/api/risks", json=risk_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                risk_score = data.get("inherent_risk_score", 0)
                risk_level = data.get("risk_level", "Unknown")
                message = f"Score: {risk_score}, Level: {risk_level}"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_result("Risk Management", success, message)
            return success
        except Exception as e:
            self.log_result("Risk Management", False, str(e))
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        try:
            response = self.session.get(f"{API_BASE}/api/dashboard/stats", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                orgs = data.get("organizations", 0)
                assessments = data.get("assessments", 0)
                risks = data.get("open_risks", 0)
                message = f"Orgs: {orgs}, Assessments: {assessments}, Risks: {risks}"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_result("Dashboard Stats", success, message)
            return success
        except Exception as e:
            self.log_result("Dashboard Stats", False, str(e))
            return False

    def test_security_cors(self):
        """Test CORS security configuration"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=5)
            cors_header = response.headers.get("Access-Control-Allow-Origin", "")
            
            # Should not be wildcard (security fix validation)
            success = cors_header != "*"
            message = f"CORS Origin: {cors_header or 'Not set'}"
            
            self.log_result("CORS Security", success, message)
            return success
        except Exception as e:
            self.log_result("CORS Security", False, str(e))
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting DoganAI Compliance Kit E2E Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Core system tests
        if not self.test_health():
            print("❌ System not healthy, stopping tests")
            return False
        
        # Authentication flow
        self.test_registration()
        if not self.test_login():
            print("❌ Authentication failed, stopping tests")
            return False
        
        self.test_protected_endpoint()
        
        # Core functionality
        self.test_organization_crud()
        self.test_frameworks()
        self.test_assessment_creation()
        self.test_risk_management()
        self.test_dashboard_stats()
        
        # Security validation
        self.test_security_cors()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        duration = time.time() - start_time
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print(f"\n📈 Results: {passed}/{total} tests passed")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if passed == total:
            print("🎉 All tests passed! System is operational.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check system configuration.")
            return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("DoganAI Compliance Kit - Quick E2E Test")
        print("Usage: python test_e2e_quick.py")
        print("\nThis script tests core functionality:")
        print("- System health and availability")
        print("- User authentication flow")
        print("- Organization management")
        print("- Framework and assessment operations")
        print("- Risk management")
        print("- Dashboard statistics")
        print("- Security configurations")
        return
    
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = QuickE2ETest()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
