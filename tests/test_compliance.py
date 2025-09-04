import pytest
from unittest.mock import MagicMock, patch
from compliance import (
    evaluate_compliance,
    get_compliance_status,
    generate_compliance_report,
    get_vendor_mapping,
    ComplianceResult,
    ComplianceRequest
)

# Mock data and settings
MOCK_SETTINGS = {
    "COMPLIANCE_THRESHOLD": 80,
    "HIGH_PRIORITY_THRESHOLD": 90,
}

@pytest.fixture
def mock_settings():
    with patch('compliance.settings', MOCK_SETTINGS):
        yield

def test_get_compliance_status_compliant(mock_settings):
    """Test that a score above threshold is compliant."""
    score = 85
    status = get_compliance_status(score, "normal")
    assert status == "compliant"

def test_get_compliance_status_non_compliant(mock_settings):
    """Test that a score below threshold is non-compliant."""
    score = 70
    status = get_compliance_status(score, "normal")
    assert status == "non-compliant"

def test_get_compliance_status_high_priority_compliant(mock_settings):
    """Test high priority compliant status."""
    score = 95
    status = get_compliance_status(score, "high")
    assert status == "compliant"

def test_get_compliance_status_high_priority_non_compliant(mock_settings):
    """Test high priority non-compliant status."""
    score = 85
    status = get_compliance_status(score, "high")
    assert status == "non-compliant"

def test_get_vendor_mapping_found():
    """Test that a known vendor mapping is returned."""
    mapping = get_vendor_mapping("vendor1")
    assert mapping is not None
    assert mapping["vendor_id"] == "vendor1"

def test_get_vendor_mapping_not_found():
    """Test that a non-existent vendor mapping returns None."""
    mapping = get_vendor_mapping("unknown_vendor")
    assert mapping is None

@patch('compliance.get_vendor_mapping')
@patch('compliance.get_compliance_status')
def test_evaluate_compliance_success(mock_get_status, mock_get_mapping, mock_settings):
    """Test successful compliance evaluation."""
    mock_get_mapping.return_value = {"vendor_id": "vendor1", "rules": ["rule1", "rule2"]}
    mock_get_status.return_value = "compliant"

    request = ComplianceRequest(mapping="vendor1", priority="normal")
    result = evaluate_compliance(request)

    assert isinstance(result, ComplianceResult)
    assert result.mapping == "vendor1"
    assert result.status == "compliant"
    assert result.compliance_percentage >= 0
    assert result.compliance_percentage <= 100
    mock_get_mapping.assert_called_once_with("vendor1")
    mock_get_status.assert_called_once()

@patch('compliance.get_vendor_mapping')
def test_evaluate_compliance_mapping_not_found(mock_get_mapping, mock_settings):
    """Test compliance evaluation when mapping is not found."""
    mock_get_mapping.return_value = None
    request = ComplianceRequest(mapping="unknown", priority="normal")
    
    with pytest.raises(ValueError, match="Vendor mapping not found for unknown"):
        evaluate_compliance(request)

def test_generate_compliance_report():
    """Test report generation."""
    result = ComplianceResult(
        mapping="vendor1",
        status="compliant",
        evaluation_time=0.1,
        cached=False,
        compliance_percentage=95.5,
        details={"rules_passed": 19, "rules_failed": 1},
        request_id="req-123",
        priority="high"
    )
    report = generate_compliance_report(result)
    assert "Compliance Report" in report
    assert "Vendor: vendor1" in report
    assert "Status: compliant" in report
    assert "Score: 95.5%" in report

# To run these tests, use pytest from your terminal in the project root directory:
# pip install pytest unittest-mock
# pytest
