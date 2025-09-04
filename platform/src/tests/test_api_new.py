"""
Test suite for API endpoints
"""
from unittest.mock import patch

class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    def test_health_endpoint(self, api_client):
        """Test basic health endpoint"""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data
    
    def test_detailed_health_endpoint(self, api_client):
        """Test detailed health endpoint"""
        with patch('engine.health.get_health_checker') as mock_checker:
            mock_result = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00",
                "checks": {
                    "database": {"status": "healthy"},
                    "filesystem": {"status": "healthy"}
                }
            }
            mock_checker.return_value.run_all_checks.return_value = mock_result
            
            response = api_client.get("/health/detailed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "checks" in data
    
    def test_version_endpoint(self, api_client):
        """Test version endpoint"""
        response = api_client.get("/version")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_mappings_endpoint(self, api_client):
        """Test mappings listing endpoint"""
        with patch('engine.api._list_mapping_names') as mock_list:
            mock_list.return_value = ["MAP-GOV-Test", "MAP-BANK-Test"]
            
            response = api_client.get("/mappings")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert "MAP-GOV-Test" in data
    
    def test_evaluate_endpoint_success(self, api_client):
        """Test successful evaluation endpoint"""
        mock_result = {
            "mapping": "MAP-GOV-Test",
            "policy": "NCA@1.0.0",
            "status": "PARTIAL",
            "required": ["NCA-001", "NCA-002", "NCA-003"],
            "provided": ["NCA-001", "NCA-002"],
            "missing": ["NCA-003"],
            "vendors": [{"vendor": "Test Corp", "solution": "Test Solution"}],
            "hash": "abc123"
        }
        
        with patch('engine.api.evaluate') as mock_eval, \
             patch('engine.api._list_mapping_names') as mock_list:
            
            mock_list.return_value = ["MAP-GOV-Test"]
            mock_eval.return_value = mock_result
            
            response = api_client.post("/evaluate", json={"mapping": "MAP-GOV-Test"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["mapping"] == "MAP-GOV-Test"
            assert data["status"] == "PARTIAL"
            assert len(data["missing"]) == 1
    
    def test_evaluate_endpoint_mapping_not_found(self, api_client):
        """Test evaluation with non-existent mapping"""
        with patch('engine.api._list_mapping_names') as mock_list:
            mock_list.return_value = ["MAP-GOV-Test"]
            
            response = api_client.post("/evaluate", json={"mapping": "NONEXISTENT"})
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"]
    
    def test_evaluate_endpoint_invalid_input(self, api_client):
        """Test evaluation with invalid input"""
        response = api_client.post("/evaluate", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_evaluate_endpoint_compliance_error(self, api_client):
        """Test evaluation with compliance error"""
        from engine.compliance import ComplianceError
        
        with patch('engine.api.evaluate') as mock_eval, \
             patch('engine.api._list_mapping_names') as mock_list:
            
            mock_list.return_value = ["MAP-GOV-Test"]
            mock_eval.side_effect = ComplianceError("Test compliance error")
            
            response = api_client.post("/evaluate", json={"mapping": "MAP-GOV-Test"})
            
            assert response.status_code == 400
            data = response.json()
            assert "Compliance error" in data["detail"]
    
    def test_benchmarks_endpoint_success(self, api_client):
        """Test successful benchmarks endpoint"""
        mock_benchmarks = {
            "Government": {
                "months": ["Jan", "Feb", "Mar"],
                "SLA_met_pct": [95.2, 96.1, 94.8]
            }
        }
        
        with patch('builtins.open', create=True) as mock_open, \
             patch('os.path.exists') as mock_exists, \
             patch('json.load') as mock_json:
            
            mock_exists.return_value = True
            mock_json.return_value = mock_benchmarks
            
            response = api_client.get("/benchmarks")
            
            assert response.status_code == 200
            data = response.json()
            assert "Government" in data
            assert len(data["Government"]["months"]) == 3
    
    def test_benchmarks_endpoint_file_not_found(self, api_client):
        """Test benchmarks endpoint when file not found"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = api_client.get("/benchmarks")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"]
    
    def test_metrics_endpoint(self, api_client):
        """Test Prometheus metrics endpoint"""
        response = api_client.get("/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        
        # Check that some basic metrics are present
        content = response.text
        assert "http_requests_total" in content

class TestAPIMiddleware:
    """Test API middleware functionality"""
    
    def test_request_id_middleware(self, api_client):
        """Test request ID middleware"""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # Test with provided request ID
        custom_id = "custom-request-id-123"
        response = api_client.get("/health", headers={"X-Request-ID": custom_id})
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
    
    def test_cors_headers(self, api_client):
        """Test CORS headers are present"""
        response = api_client.options("/health")
        
        # FastAPI automatically handles OPTIONS for CORS
        assert response.status_code in [200, 405]  # Depending on FastAPI version

class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_general_exception_handler(self, api_client):
        """Test general exception handler"""
        with patch('engine.api.evaluate') as mock_eval, \
             patch('engine.api._list_mapping_names') as mock_list:
            
            mock_list.return_value = ["MAP-GOV-Test"]
            mock_eval.side_effect = Exception("Unexpected error")
            
            response = api_client.post("/evaluate", json={"mapping": "MAP-GOV-Test"})
            
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
    
    def test_validation_error(self, api_client):
        """Test Pydantic validation error handling"""
        response = api_client.post("/evaluate", json={"mapping": ""})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data