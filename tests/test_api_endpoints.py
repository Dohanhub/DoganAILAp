"""
Comprehensive API endpoint tests for DoganAI Compliance Kit
Target: 65% coverage for API endpoints
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock environment variables before importing
os.environ.setdefault('API_KEY', 'test-api-key')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')

from src.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_compliance_engine():
    """Mock compliance engine fixture"""
    with patch('src.main.compliance_engine') as mock:
        yield mock


@pytest.fixture
def mock_db_service():
    """Mock database service fixture"""
    with patch('src.main.get_db_service') as mock:
        yield mock


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint_success(self, client):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @patch('src.main.get_health_checker')
    def test_health_check_success(self, mock_health_checker, client):
        """Test successful health check"""
        mock_checker = Mock()
        mock_checker.run_all_checks.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00",
            "checks": {"database": "ok", "redis": "ok"},
            "summary": {"total": 2, "passed": 2}
        }
        mock_health_checker.return_value = mock_checker
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert "summary" in data
    
    @patch('src.main.get_health_checker')
    def test_health_check_failure(self, mock_health_checker, client):
        """Test health check failure"""
        mock_health_checker.side_effect = Exception("Health check failed")
        
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "message" in data


class TestMappingsEndpoint:
    """Test mappings endpoint"""
    
    def test_list_mappings_success(self, client, mock_compliance_engine):
        """Test successful mappings listing"""
        mock_compliance_engine.get_available_mappings.return_value = [
            "citc_mapping", "sama_mapping", "moh_mapping"
        ]
        
        response = client.get("/mappings")
        assert response.status_code == 200
        data = response.json()
        assert "mappings" in data
        assert "count" in data
        assert data["count"] == 3
        assert "citc_mapping" in data["mappings"]
    
    def test_list_mappings_failure(self, client, mock_compliance_engine):
        """Test mappings listing failure"""
        mock_compliance_engine.get_available_mappings.side_effect = Exception("Database error")
        
        response = client.get("/mappings")
        assert response.status_code == 500


class TestEvaluationEndpoint:
    """Test compliance evaluation endpoints"""
    
    def test_evaluate_compliance_success(self, client, mock_compliance_engine):
        """Test successful compliance evaluation"""
        mock_result = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "policy_ref": "CITC-2024",
            "sector": "telecommunications",
            "summary": {"score": 95.5, "controls": 20},
            "details": {"passed": 19, "failed": 1},
            "timestamp": "2024-01-01T00:00:00Z"
        }
        mock_compliance_engine.evaluate_mapping.return_value = mock_result
        
        request_data = {
            "mapping_name": "citc_mapping",
            "force_refresh": False
        }
        
        response = client.post("/evaluate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "compliant"
        assert data["mapping_name"] == "citc_mapping"
        assert data["summary"]["score"] == 95.5
    
    def test_evaluate_compliance_not_found(self, client, mock_compliance_engine):
        """Test evaluation with non-existent mapping"""
        mock_compliance_engine.evaluate_mapping.side_effect = FileNotFoundError("Mapping not found")
        
        request_data = {
            "mapping_name": "nonexistent_mapping",
            "force_refresh": False
        }
        
        response = client.post("/evaluate", json=request_data)
        assert response.status_code == 404
    
    def test_evaluate_compliance_server_error(self, client, mock_compliance_engine):
        """Test evaluation server error"""
        mock_compliance_engine.evaluate_mapping.side_effect = Exception("Internal error")
        
        request_data = {
            "mapping_name": "citc_mapping",
            "force_refresh": False
        }
        
        response = client.post("/evaluate", json=request_data)
        assert response.status_code == 500
    
    def test_get_evaluation_result_success(self, client, mock_compliance_engine):
        """Test getting cached evaluation result"""
        mock_result = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "cached": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        mock_compliance_engine.get_cached_result.return_value = mock_result
        
        response = client.get("/evaluate/citc_mapping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "compliant"
        assert data["cached"] == True
    
    def test_get_evaluation_result_not_found(self, client, mock_compliance_engine):
        """Test getting non-existent cached result"""
        mock_compliance_engine.get_cached_result.return_value = None
        
        response = client.get("/evaluate/nonexistent_mapping")
        assert response.status_code == 404


class TestPoliciesEndpoint:
    """Test policies endpoint"""
    
    def test_list_policies_success(self, client, mock_compliance_engine):
        """Test successful policies listing"""
        mock_compliance_engine.get_available_policies.return_value = [
            "CITC", "SAMA", "MOH", "NCA"
        ]
        
        response = client.get("/policies")
        assert response.status_code == 200
        data = response.json()
        assert "policies" in data
        assert "count" in data
        assert data["count"] == 4
        assert "CITC" in data["policies"]
    
    def test_list_policies_failure(self, client, mock_compliance_engine):
        """Test policies listing failure"""
        mock_compliance_engine.get_available_policies.side_effect = Exception("Error")
        
        response = client.get("/policies")
        assert response.status_code == 500


class TestVendorsEndpoint:
    """Test vendors endpoint"""
    
    def test_list_vendors_success(self, client, mock_compliance_engine):
        """Test successful vendors listing"""
        mock_compliance_engine.get_available_vendors.return_value = [
            "IBM", "Microsoft", "AWS", "Lenovo"
        ]
        
        response = client.get("/vendors")
        assert response.status_code == 200
        data = response.json()
        assert "vendors" in data
        assert "count" in data
        assert data["count"] == 4
        assert "IBM" in data["vendors"]
    
    def test_list_vendors_failure(self, client, mock_compliance_engine):
        """Test vendors listing failure"""
        mock_compliance_engine.get_available_vendors.side_effect = Exception("Error")
        
        response = client.get("/vendors")
        assert response.status_code == 500


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    @patch('src.main.metrics_collector')
    def test_get_metrics_success(self, mock_metrics_collector, client):
        """Test successful metrics collection"""
        mock_metrics_collector.collect_system_metrics.return_value = None
        
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data
        mock_metrics_collector.collect_system_metrics.assert_called_once()
    
    @patch('src.main.metrics_collector')
    def test_get_metrics_failure(self, mock_metrics_collector, client):
        """Test metrics collection failure"""
        mock_metrics_collector.collect_system_metrics.side_effect = Exception("Metrics error")
        
        response = client.get("/metrics")
        assert response.status_code == 500


class TestObservabilityEndpoints:
    """Test observability endpoints"""
    
    @patch('src.main.get_observability_status')
    @patch('src.main.observability')
    def test_observability_status_success(self, mock_observability, mock_get_status, client):
        """Test observability status endpoint"""
        mock_get_status.return_value = {"enabled": True, "components": ["metrics", "tracing"]}
        mock_observability.get_metrics_summary.return_value = {"timestamp": "2024-01-01T00:00:00Z"}
        
        response = client.get("/observability/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "observability" in data
    
    @patch('src.main.observability')
    def test_observability_metrics_success(self, mock_observability, client):
        """Test observability metrics endpoint"""
        mock_observability.get_metrics_summary.return_value = {
            "requests_total": 100,
            "errors_total": 5,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        response = client.get("/observability/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data


class TestFeatureFlagsEndpoints:
    """Test feature flags endpoints"""
    
    @patch('src.main.flag_manager')
    def test_list_feature_flags_success(self, mock_flag_manager, client):
        """Test listing feature flags"""
        mock_flag_manager.list_flags.return_value = [
            {"name": "new_ui", "enabled": True},
            {"name": "advanced_analytics", "enabled": False}
        ]
        
        response = client.get("/feature-flags")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] == 2
        assert "flags" in data
    
    @patch('src.main.flag_manager')
    def test_feature_flags_status_success(self, mock_flag_manager, client):
        """Test feature flags status"""
        mock_flag_manager.get_flag_status.return_value = {
            "total_flags": 10,
            "enabled_flags": 7,
            "disabled_flags": 3
        }
        
        response = client.get("/feature-flags/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "feature_flags" in data
    
    @patch('src.main.flag_manager')
    def test_evaluate_feature_flag_success(self, mock_flag_manager, client):
        """Test feature flag evaluation"""
        mock_result = Mock()
        mock_result.flag_name = "new_ui"
        mock_result.enabled = True
        mock_result.reason = "user_segment_match"
        mock_result.user_segment.value = "production"
        mock_result.rollout_percentage = 100
        mock_result.evaluation_time = datetime.now()
        
        mock_flag_manager.evaluate.return_value = mock_result
        
        response = client.post("/feature-flags/new_ui/evaluate?user_id=test_user")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["flag_name"] == "new_ui"
        assert data["enabled"] == True


class TestAuditEndpoint:
    """Test audit logs endpoint"""
    
    def test_get_audit_logs_success(self, client, mock_db_service):
        """Test successful audit logs retrieval"""
        # Mock database session and query
        mock_session = Mock()
        mock_db_service.return_value.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock audit log objects
        mock_log = Mock()
        mock_log.id = 1
        mock_log.timestamp = datetime.now()
        mock_log.mapping_name = "citc_mapping"
        mock_log.policy_ref = "CITC-2024"
        mock_log.status = "compliant"
        mock_log.result_hash = "abc123"
        mock_log.user_id = "test_user"
        mock_log.session_id = "session_123"
        mock_log.evaluation_data = {
            "summary": {
                "total_controls": 20,
                "covered_controls": 19,
                "coverage_percentage": 95.0
            }
        }
        
        # Mock query chain
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_log]
        
        mock_session.query.return_value = mock_query
        
        response = client.get("/audit?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "count" in data
        assert "total" in data
        assert data["count"] == 1
        assert data["total"] == 1
    
    def test_get_audit_logs_failure(self, client, mock_db_service):
        """Test audit logs retrieval failure"""
        mock_db_service.side_effect = Exception("Database error")
        
        response = client.get("/audit")
        assert response.status_code == 500


class TestRequestValidation:
    """Test request validation"""
    
    def test_evaluate_invalid_request(self, client):
        """Test evaluation with invalid request data"""
        invalid_data = {
            "invalid_field": "value"
        }
        
        response = client.post("/evaluate", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_audit_logs_invalid_params(self, client):
        """Test audit logs with invalid parameters"""
        response = client.get("/audit?limit=-1")
        assert response.status_code == 422  # Validation error
        
        response = client.get("/audit?limit=2000")  # Exceeds max limit
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_404_endpoint(self, client):
        """Test non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test wrong HTTP method"""
        response = client.delete("/health")
        assert response.status_code == 405
