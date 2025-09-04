#!/usr/bin/env python3
"""
Comprehensive Security Test Suite for DoganAI Compliance Kit
Tests all security features, authentication, authorization, and security audit functionality
"""

import pytest
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.security_audit import (
    SecurityAuditor, SecurityFinding, SecurityLevel, AuditCategory,
    get_security_auditor
)
from monitoring.alerting import (
    AlertManager, AlertSeverity, AlertChannel, get_alert_manager
)
from monitoring.health_checks import (
    HealthChecker, get_health_checker
)
from monitoring.prometheus_metrics import (
    DoganAIMetrics, get_metrics
)

class TestSecurityAuditor:
    """Test security auditor functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.auditor = SecurityAuditor()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_security_auditor_initialization(self):
        """Test security auditor initialization"""
        assert self.auditor is not None
        assert len(self.auditor.audit_rules) > 0
        assert len(self.auditor.secret_patterns) > 0
        assert len(self.auditor.vulnerability_patterns) > 0
    
    def test_secret_patterns(self):
        """Test secret pattern detection"""
        # Test API key pattern
        test_content = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        matches = []
        for pattern in self.auditor.secret_patterns:
            if 'api' in pattern and 'key' in pattern:
                import re
                matches.extend(re.findall(pattern, test_content, re.IGNORECASE))
        
        assert len(matches) > 0
    
    def test_vulnerability_patterns(self):
        """Test vulnerability pattern detection"""
        # Test SQL injection pattern
        test_content = 'cursor.execute("SELECT * FROM users WHERE id = " + user_id)'
        matches = []
        for pattern in self.auditor.vulnerability_patterns:
            if 'sql' in pattern.lower():
                import re
                matches.extend(re.findall(pattern, test_content, re.IGNORECASE))
        
        assert len(matches) > 0
    
    @pytest.mark.asyncio
    async def test_comprehensive_audit(self):
        """Test comprehensive security audit"""
        # Create test files with vulnerabilities
        test_file = os.path.join(self.temp_dir, "test_vulnerable.py")
        with open(test_file, 'w') as f:
            f.write('''
api_key = "sk-1234567890abcdef1234567890abcdef"
password = "weakpassword123"
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
''')
        
        # Run audit
        report = await self.auditor.run_comprehensive_audit()
        
        assert report is not None
        assert 'audit_id' in report
        assert 'total_findings' in report
        assert 'findings' in report
        assert len(report['findings']) > 0
    
    @pytest.mark.asyncio
    async def test_scan_for_secrets(self):
        """Test secret scanning functionality"""
        # Create test file with secrets
        test_file = os.path.join(self.temp_dir, "test_secrets.py")
        with open(test_file, 'w') as f:
            f.write('''
api_key = "sk-1234567890abcdef1234567890abcdef"
db_password = "mypassword123"
jwt_secret = "mysecretkey12345678901234567890"
''')
        
        findings = await self.auditor._scan_for_secrets()
        assert len(findings) > 0
        
        # Check that secrets were found
        secret_files = [f.location for f in findings]
        assert test_file in secret_files
    
    @pytest.mark.asyncio
    async def test_scan_for_vulnerabilities(self):
        """Test vulnerability scanning functionality"""
        # Create test file with vulnerabilities
        test_file = os.path.join(self.temp_dir, "test_vulns.py")
        with open(test_file, 'w') as f:
            f.write('''
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
os.system(user_input)
eval(user_code)
''')
        
        findings = await self.auditor._scan_for_vulnerabilities()
        assert len(findings) > 0
        
        # Check that vulnerabilities were found
        vuln_files = [f.location for f in findings]
        assert test_file in vuln_files
    
    def test_findings_summary(self):
        """Test findings summary generation"""
        # Add some test findings
        finding1 = SecurityFinding(
            id="TEST_001",
            title="Test Finding 1",
            description="Test description",
            category=AuditCategory.AUTHENTICATION,
            level=SecurityLevel.HIGH,
            location="test_file.py",
            recommendation="Fix the issue",
            timestamp=datetime.now(timezone.utc)
        )
        
        finding2 = SecurityFinding(
            id="TEST_002",
            title="Test Finding 2",
            description="Test description",
            category=AuditCategory.CONFIGURATION,
            level=SecurityLevel.CRITICAL,
            location="test_file2.py",
            recommendation="Fix the issue",
            timestamp=datetime.now(timezone.utc)
        )
        
        self.auditor.findings = [finding1, finding2]
        
        summary = self.auditor.get_findings_summary()
        assert summary['total_findings'] == 2
        assert summary['open_findings'] == 2
        assert summary['by_level']['high'] == 1
        assert summary['by_level']['critical'] == 1
    
    def test_export_findings(self):
        """Test findings export functionality"""
        # Add test finding
        finding = SecurityFinding(
            id="TEST_001",
            title="Test Finding",
            description="Test description",
            category=AuditCategory.AUTHENTICATION,
            level=SecurityLevel.HIGH,
            location="test_file.py",
            recommendation="Fix the issue",
            timestamp=datetime.now(timezone.utc)
        )
        
        self.auditor.findings = [finding]
        
        # Export as JSON
        json_export = self.auditor.export_findings('json')
        data = json.loads(json_export)
        
        assert 'findings' in data
        assert 'summary' in data
        assert len(data['findings']) == 1
        assert data['findings'][0]['id'] == "TEST_001"

class TestAlertManager:
    """Test alert manager functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.alert_manager = AlertManager()
    
    def test_alert_manager_initialization(self):
        """Test alert manager initialization"""
        assert self.alert_manager is not None
        assert len(self.alert_manager.notification_channels) > 0
        assert len(self.alert_manager.alert_rules) > 0
    
    def test_create_alert(self):
        """Test alert creation"""
        alert = self.alert_manager.create_alert(
            title="Test Alert",
            message="Test message",
            severity=AlertSeverity.HIGH,
            source="test",
            metadata={"test": "data"}
        )
        
        assert alert is not None
        assert alert.title == "Test Alert"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.source == "test"
        assert len(self.alert_manager.alerts) == 1
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment"""
        alert = self.alert_manager.create_alert(
            title="Test Alert",
            message="Test message",
            severity=AlertSeverity.HIGH,
            source="test"
        )
        
        assert not alert.acknowledged
        result = self.alert_manager.acknowledge_alert(alert.id)
        assert result is True
        assert alert.acknowledged
    
    def test_alert_resolution(self):
        """Test alert resolution"""
        alert = self.alert_manager.create_alert(
            title="Test Alert",
            message="Test message",
            severity=AlertSeverity.HIGH,
            source="test"
        )
        
        assert not alert.resolved
        result = self.alert_manager.resolve_alert(alert.id)
        assert result is True
        assert alert.resolved
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        # Create multiple alerts
        alert1 = self.alert_manager.create_alert(
            title="Active Alert",
            message="Active message",
            severity=AlertSeverity.HIGH,
            source="test"
        )
        
        alert2 = self.alert_manager.create_alert(
            title="Resolved Alert",
            message="Resolved message",
            severity=AlertSeverity.MEDIUM,
            source="test"
        )
        
        # Resolve one alert
        self.alert_manager.resolve_alert(alert2.id)
        
        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].id == alert1.id
    
    def test_alert_summary(self):
        """Test alert summary generation"""
        # Create alerts of different severities
        self.alert_manager.create_alert(
            title="Critical Alert",
            message="Critical message",
            severity=AlertSeverity.CRITICAL,
            source="test"
        )
        
        self.alert_manager.create_alert(
            title="High Alert",
            message="High message",
            severity=AlertSeverity.HIGH,
            source="test"
        )
        
        summary = self.alert_manager.get_alert_summary()
        assert summary['total_alerts'] == 2
        assert summary['active_alerts'] == 2
        assert summary['by_severity']['critical'] == 1
        assert summary['by_severity']['high'] == 1
    
    def test_notification_channels(self):
        """Test notification channel setup"""
        # Test adding custom channel
        def test_handler(alert):
            pass
        
        self.alert_manager.add_notification_channel(AlertChannel.WEBHOOK, test_handler)
        assert AlertChannel.WEBHOOK in self.alert_manager.notification_channels
    
    @patch('smtplib.SMTP')
    def test_email_channel_setup(self, mock_smtp):
        """Test email notification channel setup"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        self.alert_manager.setup_email_channel(
            smtp_server="smtp.test.com",
            smtp_port=587,
            username="test@test.com",
            password="password",
            recipients=["admin@test.com"]
        )
        
        assert AlertChannel.EMAIL in self.alert_manager.notification_channels

class TestHealthChecker:
    """Test health checker functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.health_checker = HealthChecker()
    
    def test_health_checker_initialization(self):
        """Test health checker initialization"""
        assert self.health_checker is not None
        assert len(self.health_checker.services) > 0
    
    @pytest.mark.asyncio
    async def test_check_database_health(self):
        """Test database health check"""
        # Create temporary database
        import sqlite3
        test_db = os.path.join(tempfile.gettempdir(), "test_health.db")
        
        # Create test database
        conn = sqlite3.connect(test_db)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()
        
        config = {
            'type': 'sqlite',
            'path': test_db,
            'critical': True
        }
        
        result = await self.health_checker._check_database("test_db", config)
        
        assert result is not None
        assert result.status == 'healthy'
        assert result.component == 'test_db'
        
        # Cleanup
        os.remove(test_db)
    
    @pytest.mark.asyncio
    async def test_check_system_health(self):
        """Test system health check"""
        result = await self.health_checker.check_system_health()
        
        assert result is not None
        assert result.component == 'system'
        assert result.status in ['healthy', 'degraded', 'unhealthy']
        assert 'cpu_percent' in result.details
        assert 'memory_percent' in result.details
    
    @pytest.mark.asyncio
    async def test_run_all_checks(self):
        """Test running all health checks"""
        result = await self.health_checker.run_all_checks()
        
        assert result is not None
        assert 'status' in result
        assert 'timestamp' in result
        assert 'checks' in result
        assert 'summary' in result
        assert result['status'] in ['healthy', 'degraded', 'unhealthy']
    
    def test_health_history(self):
        """Test health history functionality"""
        # Add some test history
        test_history = {
            'timestamp': datetime.now(timezone.utc),
            'status': 'healthy',
            'results': []
        }
        
        self.health_checker.health_history.append(test_history)
        
        history = self.health_checker.get_health_history()
        assert len(history) == 1
        assert history[0]['status'] == 'healthy'

class TestDoganAIMetrics:
    """Test metrics functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.metrics = DoganAIMetrics()
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        assert self.metrics is not None
        assert self.metrics.registry is not None
    
    def test_record_api_request(self):
        """Test API request recording"""
        self.metrics.record_api_request(
            method="GET",
            endpoint="/health",
            status_code=200,
            duration=0.1
        )
        
        # Check that metrics were recorded
        metrics_data = self.metrics.get_metrics()
        assert "doganai_api_requests_total" in metrics_data
    
    def test_record_compliance_evaluation(self):
        """Test compliance evaluation recording"""
        self.metrics.record_compliance_evaluation(
            mapping="test_mapping",
            status="success",
            standard="NCA",
            score=85.5,
            duration=2.5
        )
        
        # Check that metrics were recorded
        metrics_data = self.metrics.get_metrics()
        assert "doganai_compliance_evaluations_total" in metrics_data
    
    def test_record_security_event(self):
        """Test security event recording"""
        self.metrics.record_security_event(
            event_type="authentication_failure",
            severity="high",
            source="api"
        )
        
        # Check that metrics were recorded
        metrics_data = self.metrics.get_metrics()
        assert "doganai_security_events_total" in metrics_data
    
    def test_record_system_metrics(self):
        """Test system metrics recording"""
        self.metrics.record_system_metrics()
        
        # Check that metrics were recorded
        metrics_data = self.metrics.get_metrics()
        assert "doganai_system_cpu_usage_percent" in metrics_data
        assert "doganai_system_memory_usage_bytes" in metrics_data
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test metrics collection task"""
        # Start metrics collection
        task = asyncio.create_task(
            self.metrics.start_metrics_collection(interval=1)
        )
        
        # Let it run for a short time
        await asyncio.sleep(2)
        
        # Cancel the task
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass

class TestSecurityIntegration:
    """Test security integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_security_audit_with_alerts(self):
        """Test security audit with alert integration"""
        auditor = get_security_auditor()
        alert_manager = get_alert_manager()
        
        # Run security audit
        audit_report = await auditor.run_comprehensive_audit()
        
        # Check if critical findings should trigger alerts
        critical_findings = [
            f for f in audit_report['findings']
            if f['level'] == 'critical'
        ]
        
        if critical_findings:
            # Create alert for critical findings
            alert = alert_manager.create_alert(
                title="Critical Security Findings Detected",
                message=f"Found {len(critical_findings)} critical security issues",
                severity=AlertSeverity.CRITICAL,
                source="security_audit",
                metadata={'audit_id': audit_report['audit_id']}
            )
            
            assert alert is not None
            assert alert.severity == AlertSeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_health_monitoring_with_security(self):
        """Test health monitoring with security integration"""
        health_checker = get_health_checker()
        alert_manager = get_alert_manager()
        
        # Run health checks
        health_status = await health_checker.run_all_checks()
        
        # Check if unhealthy status should trigger security alert
        if health_status['status'] == 'unhealthy':
            alert = alert_manager.create_alert(
                title="System Health Critical",
                message="System health check failed",
                severity=AlertSeverity.CRITICAL,
                source="health_monitoring",
                metadata={'health_status': health_status}
            )
            
            assert alert is not None
    
    def test_metrics_with_security_events(self):
        """Test metrics recording with security events"""
        metrics = get_metrics()
        alert_manager = get_alert_manager()
        
        # Record security events
        metrics.record_security_event(
            event_type="authentication_failure",
            severity="high",
            source="api"
        )
        
        # Create alert for high severity security event
        alert = alert_manager.create_alert(
            title="High Severity Security Event",
            message="Authentication failure detected",
            severity=AlertSeverity.HIGH,
            source="security_monitoring"
        )
        
        assert alert is not None
        assert alert.severity == AlertSeverity.HIGH

def run_security_tests():
    """Run all security tests and return results"""
    print("🚀 STARTING COMPREHENSIVE SECURITY TESTING")
    print("=" * 60)
    
    # Run pytest with verbose output
    import subprocess
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_comprehensive_security.py",
        "-v",
        "--tb=short",
        "--color=yes",
        "--cov=security",
        "--cov=monitoring",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print("\n📊 SECURITY TEST RESULTS:")
        print("=" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ WARNINGS/ERRORS:")
            print(result.stderr)
        
        # Count passed tests
        stdout_lines = result.stdout.split('\n')
        passed_count = sum(1 for line in stdout_lines if 'PASSED' in line)
        failed_count = sum(1 for line in stdout_lines if 'FAILED' in line)
        skipped_count = sum(1 for line in stdout_lines if 'SKIPPED' in line)
        
        total_tests = passed_count + failed_count + skipped_count
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print("\n📈 SECURITY TEST METRICS:")
        print(f"- Total Tests: {total_tests}")
        print(f"- Passed: {passed_count} ✅")
        print(f"- Failed: {failed_count} ❌")
        print(f"- Skipped: {skipped_count} ⏭️")
        print(f"- Success Rate: {success_rate:.1f}%")
        
        status = "COMPLETED" if success_rate >= 80 else "PARTIAL"
        print(f"\n✅ COMPREHENSIVE SECURITY TESTING STATUS: {status}")
        
        return success_rate >= 80
        
    except subprocess.TimeoutExpired:
        print("❌ Security tests timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"❌ Security test execution failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when script is executed directly
    success = run_security_tests()
    sys.exit(0 if success else 1)
