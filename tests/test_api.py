import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from backend.main import app

# Initialize TestClient
client = TestClient(app)

# We need to mock the services inside main.py
# Using patch.object on the instances created in main.py is tricky because they are global.
# Easier to mock the methods using pytest-mock or patch context in the test.

@pytest.fixture
def mock_services(mocker):
    # Mock the methods on the global instances in main
    # Mock with real Pydantic objects to satisfy response_model validation
    from backend.models.schemas import CandidateProfile
    mock_candidate = CandidateProfile(
        name="Test", location_country="UAE", job_family="General", 
        citizenship="UAE", role="Tester", salary=1000, currency="USD"
    )
    mocker.patch("backend.main.ai_service.extract_candidate_data", return_value=mock_candidate)
    mocker.patch("backend.main.ai_service.determine_jurisdiction", return_value="DIFC Law")
    mocker.patch("backend.main.pdf_service.generate_contract", return_value={
        "path": "dummy.pdf",
        "original_text": "template",
        "final_text": "filled"
    })
    mocker.patch("backend.main.compliance_engine.analyze", return_value={"alerts": [], "projected_dates": {}})

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Invisible Onboarding Engine is Online"}

def test_generate_onboarding(mock_services):
    payload = {"raw_text": "Hire someone"}
    response = client.post("/generate-onboarding", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["jurisdiction_detected"] == "DIFC Law"
    assert "dummy.pdf" in data["generated_files"]

def test_ask_policy(mocker):
    mocker.patch("backend.main.ai_service.answer_policy_question", return_value="You can work remotely.")
    
    response = client.post("/ask-policy", json={"question": "Remote work?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "You can work remotely."
