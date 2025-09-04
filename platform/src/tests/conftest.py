"""
Test configuration and fixtures for DoganAI-Compliance-Kit
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
import json

from src.core.models import Base
from src.core.database import EnhancedDatabaseManager
from src.core.settings import Settings

@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture(scope="session")
def test_database():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    
    db_service = EnhancedDatabaseManager()
    db_service.engine = engine
    db_service.session_factory = session_factory
    
    return db_service

@pytest.fixture
def test_settings():
    """Test settings configuration"""
    return Settings(
        app_name="Test KSA Compliance API",
        app_version="0.1.0-test",
        debug=True,
        api_url="http://localhost:8000",
        cors_origins=["http://localhost:8501"],
        pg_host="localhost",
        pg_port=5432,
        pg_db="test_ksa",
        pg_user="test_user",
        pg_password="test_password"
    )

@pytest.fixture
def sample_policy(temp_dir):
    """Create sample policy file"""
    policy_dir = temp_dir / "policies"
    policy_dir.mkdir(exist_ok=True)
    
    policy_data = {
        "regulator": "NCA",
        "version": "1.0.0",
        "name": "Test Cybersecurity Controls",
        "controls": [
            {"id": "NCA-001", "name": "Access Control", "category": "Identity"},
            {"id": "NCA-002", "name": "Data Encryption", "category": "Protection"},
            {"id": "NCA-003", "name": "Incident Response", "category": "Response"}
        ]
    }
    
    policy_file = policy_dir / "NCA.yaml"
    with open(policy_file, 'w', encoding='utf-8') as f:
        yaml.dump(policy_data, f)
    
    return policy_file

@pytest.fixture
def sample_vendor(temp_dir):
    """Create sample vendor file"""
    vendor_dir = temp_dir / "vendors"
    vendor_dir.mkdir(exist_ok=True)
    
    vendor_data = {
        "vendor": "Test Security Corp",
        "solution": "CyberShield Pro",
        "version": "2.1.0",
        "capabilities": [
            {"control_id": "NCA-001", "implementation": "Full"},
            {"control_id": "NCA-002", "implementation": "Partial"}
        ]
    }
    
    vendor_file = vendor_dir / "test-vendor.yaml"
    with open(vendor_file, 'w', encoding='utf-8') as f:
        yaml.dump(vendor_data, f)
    
    return vendor_file

@pytest.fixture
def sample_mapping(temp_dir, sample_policy, sample_vendor):
    """Create sample mapping file"""
    mapping_dir = temp_dir / "mappings"
    mapping_dir.mkdir(exist_ok=True)
    
    mapping_data = {
        "name": "Test Government Mapping",
        "policy_ref": "NCA@1.0.0",
        "sector": "Government",
        "vendors": ["test-vendor.yaml"]
    }
    
    mapping_file = mapping_dir / "MAP-GOV-Test.yaml"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        yaml.dump(mapping_data, f)
    
    return mapping_file

@pytest.fixture
def sample_benchmarks(temp_dir):
    """Create sample benchmarks file"""
    benchmark_dir = temp_dir / "benchmarks"
    benchmark_dir.mkdir(exist_ok=True)
    
    benchmark_data = {
        "Government": {
            "months": ["Jan", "Feb", "Mar"],
            "SLA_met_pct": [95.2, 96.1, 94.8]
        },
        "Banking": {
            "months": ["Jan", "Feb", "Mar"],
            "SLA_met_pct": [98.1, 97.9, 98.5]
        }
    }
    
    benchmark_file = benchmark_dir / "sector_kpis_2024_2025.json"
    with open(benchmark_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_data, f)
    
    return benchmark_file

@pytest.fixture
def mock_compliance_environment(temp_dir, sample_policy, sample_vendor, sample_mapping, sample_benchmarks):
    """Set up complete test environment"""
    with patch('engine.compliance.BASE', temp_dir):
        yield temp_dir

@pytest.fixture
def api_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from engine.api import app
    
    return TestClient(app)

class MockRequest:
    """Mock request for testing"""
    def __init__(self, method="GET", url="/", headers=None):
        self.method = method
        self.url = Mock()
        self.url.path = url
        self.headers = headers or {}

@pytest.fixture
def mock_request():
    """Mock request fixture"""
    return MockRequest