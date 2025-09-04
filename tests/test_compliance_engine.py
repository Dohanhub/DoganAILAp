"""
Comprehensive compliance engine tests for DoganAI Compliance Kit
Target: 65% coverage for compliance engine functionality
"""
import pytest
import yaml
import tempfile
import os
import sys
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')

from src.core.compliance import ComplianceEngine


@pytest.fixture
def compliance_engine():
    """Compliance engine fixture"""
    return ComplianceEngine()


@pytest.fixture
def sample_mapping_data():
    """Sample mapping YAML data"""
    return {
        "metadata": {
            "name": "citc_mapping",
            "version": "1.0",
            "policy_ref": "CITC-2024",
            "sector": "telecommunications"
        },
        "controls": [
            {
                "id": "CITC-001",
                "title": "Data Protection",
                "description": "Ensure data protection compliance",
                "requirements": ["encryption", "access_control"]
            },
            {
                "id": "CITC-002", 
                "title": "Network Security",
                "description": "Network security requirements",
                "requirements": ["firewall", "monitoring"]
            }
        ]
    }


@pytest.fixture
def sample_policy_data():
    """Sample policy YAML data"""
    return {
        "metadata": {
            "name": "CITC",
            "version": "2024.1",
            "authority": "Communications and Information Technology Commission"
        },
        "framework": {
            "categories": [
                {
                    "id": "data_protection",
                    "name": "Data Protection",
                    "controls": ["CITC-001"]
                },
                {
                    "id": "network_security", 
                    "name": "Network Security",
                    "controls": ["CITC-002"]
                }
            ]
        }
    }


@pytest.fixture
def sample_vendor_data():
    """Sample vendor YAML data"""
    return {
        "metadata": {
            "name": "IBM Watson",
            "type": "AI Platform",
            "region": "KSA"
        },
        "capabilities": [
            {
                "id": "data_encryption",
                "name": "Data Encryption",
                "compliance_controls": ["CITC-001"]
            },
            {
                "id": "network_monitoring",
                "name": "Network Monitoring", 
                "compliance_controls": ["CITC-002"]
            }
        ]
    }


class TestComplianceEngineInit:
    """Test compliance engine initialization"""
    
    def test_init_creates_directories(self):
        """Test that initialization sets up directory paths"""
        engine = ComplianceEngine()
        assert hasattr(engine, 'mappings_dir')
        assert hasattr(engine, 'policies_dir')
        assert hasattr(engine, 'vendors_dir')
        assert hasattr(engine, 'settings')
    
    def test_init_sets_correct_paths(self):
        """Test that directory paths are set correctly"""
        engine = ComplianceEngine()
        assert engine.mappings_dir == Path('mappings')
        assert engine.policies_dir == Path('policies')
        assert engine.vendors_dir == Path('vendors')


class TestGetAvailableMappings:
    """Test getting available mappings"""
    
    @pytest.mark.asyncio
    async def test_get_mappings_success(self, compliance_engine):
        """Test successful mappings retrieval"""
        with patch.object(compliance_engine.mappings_dir, 'exists', return_value=True), \
             patch.object(compliance_engine.mappings_dir, 'glob') as mock_glob:
            
            # Mock YAML files
            mock_files = [
                Mock(is_file=lambda: True, stem='citc_mapping'),
                Mock(is_file=lambda: True, stem='sama_mapping'),
                Mock(is_file=lambda: True, stem='moh_mapping')
            ]
            mock_glob.return_value = mock_files
            
            result = await compliance_engine.get_available_mappings()
            
            assert len(result) == 3
            assert 'citc_mapping' in result
            assert 'sama_mapping' in result
            assert 'moh_mapping' in result
            assert result == sorted(result)  # Should be sorted
    
    @pytest.mark.asyncio
    async def test_get_mappings_directory_not_exists(self, compliance_engine):
        """Test mappings retrieval when directory doesn't exist"""
        with patch.object(compliance_engine.mappings_dir, 'exists', return_value=False):
            result = await compliance_engine.get_available_mappings()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_mappings_exception_handling(self, compliance_engine):
        """Test exception handling in mappings retrieval"""
        with patch.object(compliance_engine.mappings_dir, 'exists', side_effect=Exception("Permission denied")):
            result = await compliance_engine.get_available_mappings()
            assert result == []


class TestGetAvailablePolicies:
    """Test getting available policies"""
    
    @pytest.mark.asyncio
    async def test_get_policies_success(self, compliance_engine):
        """Test successful policies retrieval"""
        with patch.object(compliance_engine.policies_dir, 'exists', return_value=True), \
             patch.object(compliance_engine.policies_dir, 'glob') as mock_glob:
            
            mock_files = [
                Mock(is_file=lambda: True, stem='CITC'),
                Mock(is_file=lambda: True, stem='SAMA'),
                Mock(is_file=lambda: True, stem='MOH')
            ]
            mock_glob.return_value = mock_files
            
            result = await compliance_engine.get_available_policies()
            
            assert len(result) == 3
            assert 'CITC' in result
            assert 'SAMA' in result
            assert 'MOH' in result
    
    @pytest.mark.asyncio
    async def test_get_policies_directory_not_exists(self, compliance_engine):
        """Test policies retrieval when directory doesn't exist"""
        with patch.object(compliance_engine.policies_dir, 'exists', return_value=False):
            result = await compliance_engine.get_available_policies()
            assert result == []


class TestGetAvailableVendors:
    """Test getting available vendors"""
    
    @pytest.mark.asyncio
    async def test_get_vendors_success(self, compliance_engine):
        """Test successful vendors retrieval"""
        with patch.object(compliance_engine.vendors_dir, 'exists', return_value=True), \
             patch.object(compliance_engine.vendors_dir, 'glob') as mock_glob:
            
            mock_files = [
                Mock(is_file=lambda: True, stem='IBM'),
                Mock(is_file=lambda: True, stem='Microsoft'),
                Mock(is_file=lambda: True, stem='AWS')
            ]
            mock_glob.return_value = mock_files
            
            result = await compliance_engine.get_available_vendors()
            
            assert len(result) == 3
            assert 'IBM' in result
            assert 'Microsoft' in result
            assert 'AWS' in result


class TestLoadMapping:
    """Test loading mapping files"""
    
    @pytest.mark.asyncio
    async def test_load_mapping_success(self, compliance_engine, sample_mapping_data):
        """Test successful mapping loading"""
        yaml_content = yaml.dump(sample_mapping_data)
        
        with patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch.object(Path, 'exists', return_value=True):
            
            result = await compliance_engine.load_mapping('citc_mapping')
            
            assert result is not None
            assert result['metadata']['name'] == 'citc_mapping'
            assert len(result['controls']) == 2
    
    @pytest.mark.asyncio
    async def test_load_mapping_file_not_found(self, compliance_engine):
        """Test loading non-existent mapping"""
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                await compliance_engine.load_mapping('nonexistent_mapping')
    
    @pytest.mark.asyncio
    async def test_load_mapping_invalid_yaml(self, compliance_engine):
        """Test loading mapping with invalid YAML"""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)), \
             patch.object(Path, 'exists', return_value=True):
            
            with pytest.raises(yaml.YAMLError):
                await compliance_engine.load_mapping('invalid_mapping')


class TestEvaluateMapping:
    """Test mapping evaluation"""
    
    @pytest.mark.asyncio
    async def test_evaluate_mapping_success(self, compliance_engine, sample_mapping_data):
        """Test successful mapping evaluation"""
        yaml_content = yaml.dump(sample_mapping_data)
        
        with patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(compliance_engine, '_evaluate_controls') as mock_evaluate:
            
            mock_evaluate.return_value = {
                "total_controls": 2,
                "covered_controls": 2,
                "coverage_percentage": 100.0,
                "control_results": [
                    {"id": "CITC-001", "status": "compliant", "score": 95},
                    {"id": "CITC-002", "status": "compliant", "score": 90}
                ]
            }
            
            result = await compliance_engine.evaluate_mapping('citc_mapping')
            
            assert result is not None
            assert result['status'] == 'compliant'
            assert result['mapping_name'] == 'citc_mapping'
            assert result['policy_ref'] == 'CITC-2024'
            assert result['sector'] == 'telecommunications'
            assert result['summary']['coverage_percentage'] == 100.0
    
    @pytest.mark.asyncio
    async def test_evaluate_mapping_with_cache(self, compliance_engine):
        """Test mapping evaluation with caching"""
        cached_result = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "cached": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        with patch.object(compliance_engine, 'get_cached_result', return_value=cached_result):
            result = await compliance_engine.evaluate_mapping('citc_mapping', force_refresh=False)
            assert result['cached'] == True
    
    @pytest.mark.asyncio
    async def test_evaluate_mapping_force_refresh(self, compliance_engine, sample_mapping_data):
        """Test mapping evaluation with force refresh"""
        yaml_content = yaml.dump(sample_mapping_data)
        
        with patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(compliance_engine, '_evaluate_controls') as mock_evaluate, \
             patch.object(compliance_engine, 'get_cached_result', return_value={"cached": True}):
            
            mock_evaluate.return_value = {
                "total_controls": 2,
                "covered_controls": 1,
                "coverage_percentage": 50.0,
                "control_results": []
            }
            
            result = await compliance_engine.evaluate_mapping('citc_mapping', force_refresh=True)
            
            # Should not use cache when force_refresh=True
            assert 'cached' not in result or not result.get('cached')


class TestControlEvaluation:
    """Test control evaluation logic"""
    
    def test_evaluate_controls_success(self, compliance_engine):
        """Test successful control evaluation"""
        controls = [
            {
                "id": "CITC-001",
                "title": "Data Protection",
                "requirements": ["encryption", "access_control"]
            },
            {
                "id": "CITC-002",
                "title": "Network Security", 
                "requirements": ["firewall", "monitoring"]
            }
        ]
        
        with patch.object(compliance_engine, '_evaluate_single_control') as mock_eval:
            mock_eval.side_effect = [
                {"status": "compliant", "score": 95, "details": {}},
                {"status": "non_compliant", "score": 60, "details": {}}
            ]
            
            result = compliance_engine._evaluate_controls(controls)
            
            assert result['total_controls'] == 2
            assert result['covered_controls'] == 1  # Only one compliant
            assert result['coverage_percentage'] == 50.0
            assert len(result['control_results']) == 2
    
    def test_evaluate_single_control_compliant(self, compliance_engine):
        """Test single control evaluation - compliant"""
        control = {
            "id": "CITC-001",
            "title": "Data Protection",
            "requirements": ["encryption", "access_control"]
        }
        
        with patch.object(compliance_engine, '_check_requirements') as mock_check:
            mock_check.return_value = {"score": 95, "passed": 2, "failed": 0}
            
            result = compliance_engine._evaluate_single_control(control)
            
            assert result['status'] == 'compliant'
            assert result['score'] == 95
    
    def test_evaluate_single_control_non_compliant(self, compliance_engine):
        """Test single control evaluation - non-compliant"""
        control = {
            "id": "CITC-002",
            "title": "Network Security",
            "requirements": ["firewall", "monitoring"]
        }
        
        with patch.object(compliance_engine, '_check_requirements') as mock_check:
            mock_check.return_value = {"score": 60, "passed": 1, "failed": 1}
            
            result = compliance_engine._evaluate_single_control(control)
            
            assert result['status'] == 'non_compliant'
            assert result['score'] == 60


class TestCaching:
    """Test caching functionality"""
    
    @pytest.mark.asyncio
    async def test_get_cached_result_exists(self, compliance_engine):
        """Test getting existing cached result"""
        mock_cache_entry = Mock()
        mock_cache_entry.result_data = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "cached": True
        }
        mock_cache_entry.created_at = datetime.now(timezone.utc)
        
        with patch('src.core.compliance.get_db_service') as mock_db:
            mock_session = Mock()
            mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_cache_entry
            
            result = await compliance_engine.get_cached_result('citc_mapping')
            
            assert result is not None
            assert result['cached'] == True
    
    @pytest.mark.asyncio
    async def test_get_cached_result_not_exists(self, compliance_engine):
        """Test getting non-existent cached result"""
        with patch('src.core.compliance.get_db_service') as mock_db:
            mock_session = Mock()
            mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = await compliance_engine.get_cached_result('nonexistent_mapping')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_result_success(self, compliance_engine):
        """Test successful result caching"""
        result_data = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "score": 95.5
        }
        
        with patch('src.core.compliance.get_db_service') as mock_db:
            mock_session = Mock()
            mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
            
            await compliance_engine._cache_result('citc_mapping', result_data)
            
            # Verify session operations were called
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


class TestAuditLogging:
    """Test audit logging functionality"""
    
    @pytest.mark.asyncio
    async def test_create_audit_log_success(self, compliance_engine):
        """Test successful audit log creation"""
        evaluation_data = {
            "status": "compliant",
            "mapping_name": "citc_mapping",
            "summary": {"score": 95.5}
        }
        
        with patch('src.core.compliance.get_db_service') as mock_db:
            mock_session = Mock()
            mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
            
            await compliance_engine._create_audit_log(
                mapping_name='citc_mapping',
                policy_ref='CITC-2024',
                status='compliant',
                evaluation_data=evaluation_data
            )
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_calculate_hash(self, compliance_engine):
        """Test hash calculation"""
        data = {"test": "data", "number": 123}
        hash1 = compliance_engine._calculate_hash(data)
        hash2 = compliance_engine._calculate_hash(data)
        
        assert hash1 == hash2  # Same data should produce same hash
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string
    
    def test_calculate_hash_different_data(self, compliance_engine):
        """Test hash calculation with different data"""
        data1 = {"test": "data1"}
        data2 = {"test": "data2"}
        
        hash1 = compliance_engine._calculate_hash(data1)
        hash2 = compliance_engine._calculate_hash(data2)
        
        assert hash1 != hash2  # Different data should produce different hashes
    
    def test_determine_status_compliant(self, compliance_engine):
        """Test status determination - compliant"""
        summary = {"coverage_percentage": 85.0}
        status = compliance_engine._determine_status(summary)
        assert status == "compliant"
    
    def test_determine_status_non_compliant(self, compliance_engine):
        """Test status determination - non-compliant"""
        summary = {"coverage_percentage": 65.0}
        status = compliance_engine._determine_status(summary)
        assert status == "non_compliant"
    
    def test_determine_status_partial(self, compliance_engine):
        """Test status determination - partial compliance"""
        summary = {"coverage_percentage": 75.0}
        status = compliance_engine._determine_status(summary)
        assert status == "partial_compliant"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_evaluate_mapping_database_error(self, compliance_engine):
        """Test mapping evaluation with database error"""
        with patch('src.core.compliance.get_db_service', side_effect=Exception("Database connection failed")):
            with pytest.raises(Exception):
                await compliance_engine.evaluate_mapping('citc_mapping')
    
    @pytest.mark.asyncio
    async def test_load_mapping_permission_error(self, compliance_engine):
        """Test loading mapping with permission error"""
        with patch('builtins.open', side_effect=PermissionError("Access denied")), \
             patch.object(Path, 'exists', return_value=True):
            
            with pytest.raises(PermissionError):
                await compliance_engine.load_mapping('citc_mapping')


class TestIntegration:
    """Integration tests for compliance engine"""
    
    @pytest.mark.asyncio
    async def test_full_evaluation_workflow(self, compliance_engine, sample_mapping_data):
        """Test complete evaluation workflow"""
        yaml_content = yaml.dump(sample_mapping_data)
        
        with patch('builtins.open', mock_open(read_data=yaml_content)), \
             patch.object(Path, 'exists', return_value=True), \
             patch('src.core.compliance.get_db_service') as mock_db:
            
            mock_session = Mock()
            mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None  # No cache
            
            # Mock control evaluation
            with patch.object(compliance_engine, '_check_requirements') as mock_check:
                mock_check.return_value = {"score": 90, "passed": 2, "failed": 0}
                
                result = await compliance_engine.evaluate_mapping('citc_mapping')
                
                assert result['status'] == 'compliant'
                assert result['mapping_name'] == 'citc_mapping'
                assert 'timestamp' in result
                
                # Verify caching and audit logging occurred
                assert mock_session.add.call_count >= 2  # Cache + audit log
                assert mock_session.commit.call_count >= 2
