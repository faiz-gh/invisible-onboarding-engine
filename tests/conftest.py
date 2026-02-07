import pytest
import sys
import os
from unittest.mock import MagicMock

# Add project root to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.schemas import CandidateProfile

@pytest.fixture
def mock_candidate():
    return CandidateProfile(
        name="Test User",
        role="Software Engineer",
        job_family="Engineering",
        salary=50000,
        currency="USD",
        start_date="2025-01-01",
        location_country="United Arab Emirates",
        citizenship="United Arab Emirates",
        equity_grant=False
    )
