from pydantic import BaseModel, Field
from typing import Optional, List

# 1. Input: What the HR Manager pastes
class RawJobDescription(BaseModel):
    raw_text: str = Field(..., description="The raw email or notes")

# 2. Structured Data: RELAXED VALIDATION
class CandidateProfile(BaseModel):
    name: str = Field("Unknown Candidate", description="Candidate Name")
    role: str = Field("TBD", description="Job Role")
    job_family: str = Field("General", description="Normalized Category: 'Sales', 'Engineering', 'Executive', or 'General'")
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
    original_template_text: str = Field("", description="Raw markdown before filling")
    final_contract_text: str = Field("", description="Final filled text used for PDF")

# 4. Policy Question for 'Ask HR' Tab
class PolicyQuestion(BaseModel):
    """
    Model for the HR Chatbot input.
    Defined here so Python knows what 'PolicyQuestion' is before the endpoint uses it.
    """
    question: str