import pytest
from unittest.mock import MagicMock, patch
from backend.services.ai_service import AIService

@pytest.fixture
def ai_service():
    # Patch the Client init so we don't try to connect to real Ollama
    with patch("backend.services.ai_service.Client") as mock_client:
        service = AIService()
        service.client = MagicMock()
        yield service

def test_jurisdiction_mapping(ai_service):
    assert ai_service.determine_jurisdiction("Dubai") == "DIFC Employment Law (UAE)"
    assert ai_service.determine_jurisdiction("London") == "Employment Rights Act 1996 (UK)"
    assert ai_service.determine_jurisdiction("Berlin") == "German Civil Code (BGB)"
    assert ai_service.determine_jurisdiction("Unknown Place") == "General International Contractor Agreement"

def test_extract_candidate_valid_json(ai_service):
    # Mock the chat response
    mock_response = MagicMock()
    mock_response.message.content = '{"name": "John Doe", "role": "Dev", "job_family": "Engineering", "salary": 5000}'
    ai_service.client.chat.return_value = mock_response

    result = ai_service.extract_candidate_data("Hire John Doe")
    assert result.name == "John Doe"
    assert result.role == "Dev"
    assert result.job_family == "Engineering"
    assert result.salary == 5000.0

def test_extract_candidate_fallback_on_error(ai_service):
    # Simulate an exception from the client
    ai_service.client.chat.side_effect = Exception("Ollama Down")

    result = ai_service.extract_candidate_data("Hire someone")
    # Should return MOCK_RESPONSE
    assert result.name == "Alex Smith"
    assert result.role == "Senior DevOps Engineer"
