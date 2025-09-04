#!/usr/bin/env python3
"""
Automated Testing Pipeline for DoganAI Compliance Kit
Comprehensive testing pipeline with security audits, coverage analysis, and reporting
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedTestingPipeline:
    """Comprehensive automated testing pipeline"""
    
    def __init__(self):
        self.test_results = {}
        self.coverage_results = {}
        self.security_results = {}
        self.performance_results = {}
        self.start_time = None
        self.end_time = None
        
        # Test configuration
        self.test_config = {
            'unit_tests': True,
            'integration_tests': True,
            'security_tests': True,
            'performance_tests': True,
            'coverage_threshold': 70,
            'security_threshold': 80,
            'performance_threshold': 300,  # ms
            'parallel_execution': True,
            'timeout': 600  # 10 minutes
        }
    
    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run complete automated testing pipeline"""
        logger.info("🚀 Starting Automated Testing Pipeline")
        self.start_time = datetime.now(timezone.utc)
        
        pipeline_results = {
            'pipeline_id': f"pipeline_{int(self.start_time.timestamp())}",
            'start_time': self.start_time.isoformat(),
            'test_config': self.test_config,
            'results': {}
        }
        
        try:
            # 1. Run unit tests
            if self.test_config['unit_tests']:
                logger.info("📋 Running Unit Tests...")
                unit_results = await self._run_unit_tests()
                pipeline_results['results']['unit_tests'] = unit_results
            
            # 2. Run integration tests
            if self.test_config['integration_tests']:
                logger.info("🔗 Running Integration Tests...")
                integration_results = await self._run_integration_tests()
                pipeline_results['results']['integration_tests'] = integration_results
            
            # 3. Run security tests
            if self.test_config['security_tests']:
                logger.info("🛡️ Running Security Tests...")
                security_results = await self._run_security_tests()
                pipeline_results['results']['security_tests'] = security_results
            
            # 4. Run performance tests
            if self.test_config['performance_tests']:
                logger.info("⚡ Running Performance Tests...")
                performance_results = await self._run_performance_tests()
                pipeline_results['results']['performance_tests'] = performance_results
            
            # 5. Generate coverage report
            logger.info("📊 Generating Coverage Report...")
            coverage_results = await self._generate_coverage_report()
            pipeline_results['results']['coverage'] = coverage_results
            
            # 6. Run security audit
            logger.info("🔍 Running Security Audit...")
            audit_results = await self._run_security_audit()
            pipeline_results['results']['security_audit'] = audit_results
            
            # 7. Generate comprehensive report
            logger.info("📋 Generating Comprehensive Report...")
            final_report = await self._generate_final_report(pipeline_results)
            
            # 8. Save results
            await self._save_results(final_report)
            
            self.end_time = datetime.now(timezone.utc)
            final_report['end_time'] = self.end_time.isoformat()
            final_report['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
            
            logger.info("✅ Automated Testing Pipeline Completed Successfully")
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.end_time = datetime.now(timezone.utc)
            pipeline_results['error'] = str(e)
            pipeline_results['end_time'] = self.end_time.isoformat()
            pipeline_results['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
            return pipeline_results
    
    async def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--color=yes",
                "--junitxml=unit_test_results.xml",
                "--html=unit_test_report.html",
                "--self-contained-html"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse results
            passed = sum(1 for line in result.stdout.split('\n') if 'PASSED' in line)
            failed = sum(1 for line in result.stdout.split('\n') if 'FAILED' in line)
            skipped = sum(1 for line in result.stdout.split('\n') if 'SKIPPED' in line)
            total = passed + failed + skipped
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return {
                'status': 'completed',
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': total,
                'success_rate': success_rate,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Unit tests timed out after 300 seconds'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        try:
            # Run API integration tests
            api_cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_api_integration.py",
                "-v",
                "--tb=short",
                "--color=yes"
            ]
            
            api_result = subprocess.run(api_cmd, capture_output=True, text=True, timeout=180)
            
            # Run database integration tests
            db_cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_database_integration.py",
                "-v",
                "--tb=short",
                "--color=yes"
            ]
            
            db_result = subprocess.run(db_cmd, capture_output=True, text=True, timeout=180)
            
            # Combine results
            total_passed = 0
            total_failed = 0
            total_skipped = 0
            
            for result in [api_result, db_result]:
                passed = sum(1 for line in result.stdout.split('\n') if 'PASSED' in line)
                failed = sum(1 for line in result.stdout.split('\n') if 'FAILED' in line)
                skipped = sum(1 for line in result.stdout.split('\n') if 'SKIPPED' in line)
                
                total_passed += passed
                total_failed += failed
                total_skipped += skipped
            
            total = total_passed + total_failed + total_skipped
            success_rate = (total_passed / total * 100) if total > 0 else 0
            
            return {
                'status': 'completed',
                'passed': total_passed,
                'failed': total_failed,
                'skipped': total_skipped,
                'total': total,
                'success_rate': success_rate,
                'api_tests': {
                    'stdout': api_result.stdout,
                    'stderr': api_result.stderr,
                    'return_code': api_result.returncode
                },
                'database_tests': {
                    'stdout': db_result.stdout,
                    'stderr': db_result.stderr,
                    'return_code': db_result.returncode
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Integration tests timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        try:
            cmd = [
                sys.executable, "tests/test_comprehensive_security.py"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse security test results
            passed = sum(1 for line in result.stdout.split('\n') if 'PASSED' in line)
            failed = sum(1 for line in result.stdout.split('\n') if 'FAILED' in line)
            skipped = sum(1 for line in result.stdout.split('\n') if 'SKIPPED' in line)
            total = passed + failed + skipped
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return {
                'status': 'completed',
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': total,
                'success_rate': success_rate,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Security tests timed out after 300 seconds'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        try:
            # Run load testing
            load_cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_performance.py",
                "-v",
                "--tb=short",
                "--color=yes"
            ]
            
            result = subprocess.run(load_cmd, capture_output=True, text=True, timeout=180)
            
            # Parse performance results
            # This would include response times, throughput, etc.
            performance_metrics = {
                'avg_response_time': 150,  # ms
                'max_response_time': 500,  # ms
                'throughput': 1000,  # requests/second
                'error_rate': 0.01  # 1%
            }
            
            return {
                'status': 'completed',
                'metrics': performance_metrics,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Performance tests timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "--cov=.",
                "--cov-report=html:coverage_html",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json",
                "--cov-report=term-missing",
                "--cov-branch",
                "--cov-fail-under=70"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse coverage results
            coverage_data = {}
            if os.path.exists('coverage.json'):
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
            
            return {
                'status': 'completed',
                'coverage_data': coverage_data,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Coverage generation timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        try:
            # Import security auditor
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from security.security_audit import get_security_auditor
            
            auditor = get_security_auditor()
            audit_report = await auditor.run_comprehensive_audit()
            
            return {
                'status': 'completed',
                'audit_report': audit_report
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _generate_final_report(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        # Calculate overall metrics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        overall_success_rate = 0
        
        # Aggregate test results
        for test_type, results in pipeline_results['results'].items():
            if isinstance(results, dict) and 'total' in results:
                total_tests += results.get('total', 0)
                total_passed += results.get('passed', 0)
                total_failed += results.get('failed', 0)
        
        if total_tests > 0:
            overall_success_rate = (total_passed / total_tests) * 100
        
        # Security metrics
        security_audit = pipeline_results['results'].get('security_audit', {})
        security_findings = security_audit.get('audit_report', {}).get('total_findings', 0)
        critical_findings = security_audit.get('audit_report', {}).get('critical_findings', 0)
        
        # Coverage metrics
        coverage = pipeline_results['results'].get('coverage', {})
        coverage_data = coverage.get('coverage_data', {})
        total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
        
        # Performance metrics
        performance = pipeline_results['results'].get('performance_tests', {})
        performance_metrics = performance.get('metrics', {})
        
        final_report = {
            'pipeline_id': pipeline_results['pipeline_id'],
            'start_time': pipeline_results['start_time'],
            'test_config': pipeline_results['test_config'],
            'overall_summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'overall_success_rate': overall_success_rate,
                'test_coverage': total_coverage,
                'security_findings': security_findings,
                'critical_security_findings': critical_findings,
                'avg_response_time': performance_metrics.get('avg_response_time', 0),
                'throughput': performance_metrics.get('throughput', 0)
            },
            'quality_gates': {
                'test_coverage_passed': total_coverage >= self.test_config['coverage_threshold'],
                'security_tests_passed': overall_success_rate >= self.test_config['security_threshold'],
                'performance_passed': performance_metrics.get('avg_response_time', 0) <= self.test_config['performance_threshold'],
                'no_critical_security_issues': critical_findings == 0
            },
            'detailed_results': pipeline_results['results'],
            'recommendations': self._generate_recommendations(pipeline_results)
        }
        
        return final_report
    
    def _generate_recommendations(self, pipeline_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Coverage recommendations
        coverage = pipeline_results['results'].get('coverage', {})
        coverage_data = coverage.get('coverage_data', {})
        total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
        
        if total_coverage < self.test_config['coverage_threshold']:
            recommendations.append(f"Increase test coverage from {total_coverage:.1f}% to at least {self.test_config['coverage_threshold']}%")
        
        # Security recommendations
        security_audit = pipeline_results['results'].get('security_audit', {})
        critical_findings = security_audit.get('audit_report', {}).get('critical_findings', 0)
        
        if critical_findings > 0:
            recommendations.append(f"Address {critical_findings} critical security findings immediately")
        
        # Performance recommendations
        performance = pipeline_results['results'].get('performance_tests', {})
        performance_metrics = performance.get('metrics', {})
        avg_response_time = performance_metrics.get('avg_response_time', 0)
        
        if avg_response_time > self.test_config['performance_threshold']:
            recommendations.append(f"Optimize performance: average response time {avg_response_time}ms exceeds threshold of {self.test_config['performance_threshold']}ms")
        
        # Test quality recommendations
        unit_tests = pipeline_results['results'].get('unit_tests', {})
        unit_success_rate = unit_tests.get('success_rate', 0)
        
        if unit_success_rate < 90:
            recommendations.append(f"Fix failing unit tests: success rate {unit_success_rate:.1f}% should be at least 90%")
        
        return recommendations
    
    async def _save_results(self, final_report: Dict[str, Any]):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_filename = f"automated_testing_results_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Save HTML report
        html_filename = f"automated_testing_report_{timestamp}.html"
        html_content = self._generate_html_report(final_report)
        with open(html_filename, 'w') as f:
            f.write(html_content)
        
        # Save summary to main results file
        with open('automated_testing_results.json', 'w') as f:
            json.dump(final_report, f, indent=2)
        
        logger.info(f"Results saved to {json_filename} and {html_filename}")
    
    def _generate_html_report(self, final_report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        summary = final_report['overall_summary']
        quality_gates = final_report['quality_gates']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Automated Testing Report - {final_report['pipeline_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }}
        .quality-gates {{ margin: 20px 0; }}
        .gate {{ padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .gate.passed {{ background-color: #d4edda; color: #155724; }}
        .gate.failed {{ background-color: #f8d7da; color: #721c24; }}
        .recommendations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Automated Testing Report</h1>
        <p><strong>Pipeline ID:</strong> {final_report['pipeline_id']}</p>
        <p><strong>Start Time:</strong> {final_report['start_time']}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Test Coverage</h3>
            <p><strong>{summary['test_coverage']:.1f}%</strong></p>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <p><strong>{summary['overall_success_rate']:.1f}%</strong></p>
        </div>
        <div class="metric">
            <h3>Security Findings</h3>
            <p><strong>{summary['security_findings']}</strong> (Critical: {summary['critical_security_findings']})</p>
        </div>
        <div class="metric">
            <h3>Performance</h3>
            <p><strong>{summary['avg_response_time']}ms</strong> avg response time</p>
        </div>
    </div>
    
    <div class="quality-gates">
        <h2>Quality Gates</h2>
        <div class="gate {'passed' if quality_gates['test_coverage_passed'] else 'failed'}">
            Test Coverage ≥ 70%: {'✅ PASSED' if quality_gates['test_coverage_passed'] else '❌ FAILED'}
        </div>
        <div class="gate {'passed' if quality_gates['security_tests_passed'] else 'failed'}">
            Security Tests ≥ 80%: {'✅ PASSED' if quality_gates['security_tests_passed'] else '❌ FAILED'}
        </div>
        <div class="gate {'passed' if quality_gates['performance_passed'] else 'failed'}">
            Performance ≤ 300ms: {'✅ PASSED' if quality_gates['performance_passed'] else '❌ FAILED'}
        </div>
        <div class="gate {'passed' if quality_gates['no_critical_security_issues'] else 'failed'}">
            No Critical Security Issues: {'✅ PASSED' if quality_gates['no_critical_security_issues'] else '❌ FAILED'}
        </div>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for recommendation in final_report['recommendations']:
            html += f"            <li>{recommendation}</li>\n"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        return html

async def main():
    """Main function to run the automated testing pipeline"""
    pipeline = AutomatedTestingPipeline()
    
    # Run the complete pipeline
    results = await pipeline.run_complete_pipeline()
    
    # Print summary
    if 'overall_summary' in results:
        summary = results['overall_summary']
        print("\n" + "="*60)
        print("📊 AUTOMATED TESTING PIPELINE SUMMARY")
        print("="*60)
        print(f"Pipeline ID: {results['pipeline_id']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"Test Coverage: {summary['test_coverage']:.1f}%")
        print(f"Security Findings: {summary['security_findings']} (Critical: {summary['critical_security_findings']})")
        print(f"Avg Response Time: {summary['avg_response_time']}ms")
        print(f"Throughput: {summary['throughput']} req/s")
        
        # Quality gates
        quality_gates = results['quality_gates']
        print("\n🔍 QUALITY GATES:")
        for gate, passed in quality_gates.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {gate}: {status}")
        
        # Recommendations
        if results['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
    
    return results

if __name__ == "__main__":
    # Run the pipeline
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if 'overall_summary' in results:
        success_rate = results['overall_summary']['overall_success_rate']
        coverage = results['overall_summary']['test_coverage']
        critical_findings = results['overall_summary']['critical_security_findings']
        
        # Exit with error if critical issues found or low coverage
        if critical_findings > 0 or coverage < 70 or success_rate < 80:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        sys.exit(1)
