from pydantic import BaseModel, Field
from typing import Optional, List

# 1. Input: What the HR Manager pastes
class RawJobDescription(BaseModel):
    raw_text: str = Field(..., description="The raw email or notes")

# 2. Structured Data: RELAXED VALIDATION
class CandidateProfile(BaseModel):
    name: str = Field("Unknown Candidate", description="Candidate Name")
    role: str = Field("TBD", description="Job Role")
    email: Optional[str] = Field(None, description="Candidate Email (Optional)")
    salary: Optional[float] = Field(0.0, description="Salary amount")
    currency: Optional[str] = Field("USD", description="Currency")
    start_date: Optional[str] = Field(None, description="Start Date YYYY-MM-DD")
    location_country: str = Field("Unknown", description="Country")
    citizenship: Optional[str] = Field(None, description="Citizenship")
    equity_grant: bool = Field(False, description="Stock options included?")

# 3. Output
class OnboardingPackage(BaseModel):
    candidate: CandidateProfile
    generated_files: List[str]
    compliance_alerts: List[str]
    jurisdiction_detected: str