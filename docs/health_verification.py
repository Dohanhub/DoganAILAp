#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Comprehensive Health Verification
Systematic health checks for all services post-boot
"""

import requests
import json
import time
from datetime import datetime
import sys
from urllib.parse import urljoin

class HealthVerifier:
    def __init__(self):
        self.services = {
            'compliance_engine': {
                'base_url': 'http://localhost:8000',
                'endpoints': ['/health', '/healthz', '/ready', '/readyz', '/', '/docs']
            },
            'workflow_app': {
                'base_url': 'http://localhost:8001',
                'endpoints': ['/health', '/', '/api/demo-data']
            },
            'benchmarks': {
                'base_url': 'http://localhost:8002',
                'endpoints': ['/health', '/healthz', '/ready']
            },
            'ai_ml': {
                'base_url': 'http://localhost:8003',
                'endpoints': ['/health', '/healthz', '/ready']
            },
            'integrations': {
                'base_url': 'http://localhost:8004',
                'endpoints': ['/health', '/healthz', '/ready']
            },
            'auth': {
                'base_url': 'http://localhost:8005',
                'endpoints': ['/health', '/healthz', '/ready']
            },
            'ai_agent': {
                'base_url': 'http://localhost:8006',
                'endpoints': ['/health', '/healthz', '/ready']
            },
            'autonomous_testing': {
                'base_url': 'http://localhost:8007',
                'endpoints': ['/health', '/healthz', '/ready']
            }
        }
        
        self.results = {}
        self.overall_status = True
    
    def check_endpoint(self, service_name, base_url, endpoint, timeout=5):
        """Check a single endpoint"""
        url = urljoin(base_url, endpoint)
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            status = {
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'accessible': True,
                'healthy': response.status_code < 400,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': len(response.content)
            }
            
            # Try to parse JSON response
            try:
                if 'application/json' in response.headers.get('content-type', ''):
                    json_data = response.json()
                    status['json_response'] = json_data
                    
                    # Check for common health indicators
                    if isinstance(json_data, dict):
                        if 'status' in json_data:
                            status['service_status'] = json_data['status']
                        if 'healthy' in json_data:
                            status['service_healthy'] = json_data['healthy']
                        if 'version' in json_data:
                            status['service_version'] = json_data['version']
                else:
                    status['text_response'] = response.text[:200]  # First 200 chars
            except json.JSONDecodeError:
                status['text_response'] = response.text[:200]
            
            return status
            
        except requests.exceptions.ConnectionError:
            return {
                'url': url,
                'accessible': False,
                'healthy': False,
                'error': 'Connection refused - service not running'
            }
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'accessible': False,
                'healthy': False,
                'error': f'Timeout after {timeout}s'
            }
        except Exception as e:
            return {
                'url': url,
                'accessible': False,
                'healthy': False,
                'error': str(e)
            }
    
    def check_service(self, service_name, config):
        """Check all endpoints for a service"""
        print(f"\n🔍 Checking {service_name}...")
        
        service_results = {
            'service_name': service_name,
            'base_url': config['base_url'],
            'endpoints': {},
            'overall_healthy': True,
            'accessible_endpoints': 0,
            'healthy_endpoints': 0,
            'total_endpoints': len(config['endpoints'])
        }
        
        for endpoint in config['endpoints']:
            print(f"  Testing {endpoint}...", end=" ")
            
            result = self.check_endpoint(service_name, config['base_url'], endpoint)
            service_results['endpoints'][endpoint] = result
            
            if result['accessible']:
                service_results['accessible_endpoints'] += 1
                if result['healthy']:
                    service_results['healthy_endpoints'] += 1
                    print(f"✅ {result['status_code']} ({result.get('response_time_ms', 0)}ms)")
                else:
                    print(f"⚠️ {result['status_code']} ({result.get('response_time_ms', 0)}ms)")
                    service_results['overall_healthy'] = False
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")
                service_results['overall_healthy'] = False
        
        # Service summary
        if service_results['overall_healthy'] and service_results['accessible_endpoints'] > 0:
            print(f"  ✅ {service_name}: HEALTHY ({service_results['healthy_endpoints']}/{service_results['total_endpoints']} endpoints)")
        elif service_results['accessible_endpoints'] > 0:
            print(f"  ⚠️ {service_name}: DEGRADED ({service_results['healthy_endpoints']}/{service_results['total_endpoints']} endpoints)")
        else:
            print(f"  ❌ {service_name}: DOWN (0/{service_results['total_endpoints']} endpoints)")
            self.overall_status = False
        
        return service_results
    
    def run_comprehensive_check(self):
        """Run comprehensive health checks for all services"""
        print("🚀 DoganAI Compliance Kit - Comprehensive Health Verification")
        print("=" * 65)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for service_name, config in self.services.items():
            self.results[service_name] = self.check_service(service_name, config)
        
        self.generate_summary_report()
        return self.overall_status
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 65)
        print("📊 HEALTH VERIFICATION SUMMARY REPORT")
        print("=" * 65)
        
        # Overall status
        if self.overall_status:
            print("\n🎉 OVERALL STATUS: HEALTHY")
        else:
            print("\n⚠️ OVERALL STATUS: ISSUES DETECTED")
        
        # Service breakdown
        print("\n📋 SERVICE STATUS BREAKDOWN:")
        
        healthy_services = 0
        degraded_services = 0
        down_services = 0
        
        for service_name, result in self.results.items():
            if result['overall_healthy'] and result['accessible_endpoints'] > 0:
                status_icon = "✅"
                status_text = "HEALTHY"
                healthy_services += 1
            elif result['accessible_endpoints'] > 0:
                status_icon = "⚠️"
                status_text = "DEGRADED"
                degraded_services += 1
            else:
                status_icon = "❌"
                status_text = "DOWN"
                down_services += 1
            
            print(f"{status_icon} {service_name:20} {status_text:10} ({result['healthy_endpoints']}/{result['total_endpoints']} endpoints)")
        
        # Statistics
        total_services = len(self.results)
        print(f"\n📈 STATISTICS:")
        print(f"  • Total Services: {total_services}")
        print(f"  • Healthy: {healthy_services} ({healthy_services/total_services*100:.1f}%)")
        print(f"  • Degraded: {degraded_services} ({degraded_services/total_services*100:.1f}%)")
        print(f"  • Down: {down_services} ({down_services/total_services*100:.1f}%)")
        
        # Critical issues
        critical_issues = []
        for service_name, result in self.results.items():
            if not result['overall_healthy']:
                if result['accessible_endpoints'] == 0:
                    critical_issues.append(f"{service_name}: Service completely inaccessible")
                else:
                    failed_endpoints = []
                    for endpoint, endpoint_result in result['endpoints'].items():
                        if not endpoint_result.get('healthy', False):
                            failed_endpoints.append(endpoint)
                    if failed_endpoints:
                        critical_issues.append(f"{service_name}: Failed endpoints: {', '.join(failed_endpoints)}")
        
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  • {issue}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if down_services > 0:
            print("  1. Start missing services:")
            for service_name, result in self.results.items():
                if result['accessible_endpoints'] == 0:
                    print(f"     - {service_name}: Check if service is running on {result['base_url']}")
        
        if degraded_services > 0:
            print("  2. Fix degraded services:")
            for service_name, result in self.results.items():
                if result['accessible_endpoints'] > 0 and not result['overall_healthy']:
                    print(f"     - {service_name}: Check logs for errors")
        
        print("  3. Validate environment configuration (.env files)")
        print("  4. Check database connectivity and migrations")
        print("  5. Verify Docker containers are running (if using Docker)")
        
        # Next steps based on user's requirements
        print("\n🎯 IMMEDIATE NEXT STEPS (as per user requirements):")
        
        if 'compliance_engine' in self.results:
            ce_result = self.results['compliance_engine']
            if not ce_result['overall_healthy']:
                print("  1. 🔧 STABILIZE COMPLIANCE ENGINE:")
                print("     - Execute DB migrations")
                print("     - Launch background workers/queues")
                print("     - Verify feature flags: ENABLE_PII_REDACTION=true, DATA_RESIDENCY=KSA")
                print("     - Re-validate /readyz endpoint")
        
        print("  2. 🔍 VALIDATE ENVIRONMENT CONFIGURATION:")
        print("     - Confirm .env points to correct hosts/ports")
        print("     - Use localhost:PORT for host→Docker connections")
        print("     - Use service names for service→service communication within Docker")
        
        print("  3. 🐳 IMPLEMENT DOCKER HEALTHCHECKS:")
        print("     - Add healthcheck configuration in compose file targeting /readyz")
        print("     - Configure appropriate retries and start_period")
        
        print("  4. 📊 DASHBOARD VERIFICATION:")
        print("     - Validate widget endpoints display seeded metrics correctly")
        print("     - Test: 15 Tests, 87% Compliance, 3 Policies, 12 AI Insights")
        
        # Clean slate option
        if down_services > total_services * 0.5:  # More than 50% down
            print("\n🔄 CLEAN SLATE OPTION (if issues persist):")
            print("  • Docker: docker compose down -v && docker compose build --no-cache && docker compose up -d")
            print("  • PM2: Rebuild and restart services")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def save_detailed_report(self, filename="health_report.json"):
        """Save detailed results to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self.overall_status,
            'services': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {filename}")

def main():
    """Main function"""
    verifier = HealthVerifier()
    
    try:
        success = verifier.run_comprehensive_check()
        
        # Save detailed report
        verifier.save_detailed_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Health check failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()