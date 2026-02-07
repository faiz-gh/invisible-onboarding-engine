from fastapi import FastAPI, HTTPException
from .models.schemas import RawJobDescription, OnboardingPackage
from .services.ai_service import AIService
from .services.pdf_service import PDFService
from .services.compliance import ComplianceEngine

app = FastAPI(title="Invisible Onboarding Engine")

# Initialize Services
ai_service = AIService()
pdf_service = PDFService()
compliance_engine = ComplianceEngine()

@app.post("/generate-onboarding", response_model=OnboardingPackage)
async def generate_onboarding_packet(input_data: RawJobDescription):
    print(f"📥 Received Input: {input_data.raw_text[:50]}...")

    # 1. AI Extraction (Gemini)
    candidate = ai_service.extract_candidate_data(input_data.raw_text)
    print(f"🤖 Extracted: {candidate.name} | {candidate.location_country}")

    # 2. Determine Jurisdiction
    jurisdiction = ai_service.determine_jurisdiction(candidate.location_country)
    
    # 3. Generate PDF (NEW)
    print("📄 Generating PDF...")
    pdf_path = pdf_service.generate_contract(candidate, jurisdiction)
    
    # 4. Compliance Logic (Simple)
    print("⚖️ Running Compliance Checks...")
    compliance_result = compliance_engine.analyze(candidate)
    
    # Extract just the messages for the simple response model
    # (In a real app, you'd send the full object, but for now we map to List[str])
    alert_messages = [alert['message'] for alert in compliance_result['alerts']]
    
    # 5. Return Response
    return OnboardingPackage(
        candidate=candidate,
        generated_files=[pdf_path],
        compliance_alerts=alert_messages,
        jurisdiction_detected=jurisdiction
    )

@app.get("/")
async def root():
    return {"message": "Invisible Onboarding Engine is Online"}