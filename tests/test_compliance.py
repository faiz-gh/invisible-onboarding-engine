import pytest
from datetime import datetime, timedelta
from backend.services.compliance import ComplianceEngine
from backend.models.schemas import CandidateProfile

@pytest.fixture
def compliance_engine():
    return ComplianceEngine()

def test_visa_required(compliance_engine):
    candidate = CandidateProfile(
        citizenship="United Kingdom",
        location_country="United Arab Emirates"
    )
    alerts = compliance_engine.check_visa_requirements(candidate)
    assert any(a['type'] == 'WORKFLOW_TRIGGER' for a in alerts)
    assert "Visa Sponsorship Required" in alerts[0]['message']

def test_local_hire_no_visa(compliance_engine):
    candidate = CandidateProfile(
        citizenship="United Arab Emirates",
        location_country="United Arab Emirates"
    )
    alerts = compliance_engine.check_visa_requirements(candidate)
    assert len(alerts) == 0

def test_minimum_wage_fail(compliance_engine):
    # UAE Min Wage is 5000
    candidate = CandidateProfile(
        salary=4000,
        currency="AED",
        location_country="United Arab Emirates"
    )
    alerts = compliance_engine.check_wage_compliance(candidate)
    assert any(a['type'] == 'COMPLIANCE_RISK' for a in alerts)
    assert "Low Salary Warning" in alerts[0]['message']

def test_minimum_wage_pass(compliance_engine):
    candidate = CandidateProfile(
        salary=6000,
        currency="AED",
        location_country="United Arab Emirates"
    )
    alerts = compliance_engine.check_wage_compliance(candidate)
    assert len(alerts) == 0

def test_start_date_in_past(compliance_engine):
    past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    candidate = CandidateProfile(
        start_date=past_date,
        location_country="United Arab Emirates",
        citizenship="United Kingdom"
    )
    alerts = compliance_engine.check_visa_requirements(candidate)
    assert any("Invalid Start Date" in a['message'] for a in alerts)
