import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ..models.schemas import CandidateProfile

# Load environment variables
load_dotenv()

# Mock data for fallback
MOCK_RESPONSE = {
    "name": "Alex Smith",
    "role": "Senior DevOps Engineer",
    "email": "alex.smith@example.com",
    "salary": 25000,
    "currency": "AED",
    "start_date": "2023-11-01",
    "location_country": "UAE",
    "citizenship": "UK",
    "equity_grant": True
}

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            print("⚠️ WARNING: GOOGLE_API_KEY not found. Running in MOCK MODE.")
            self.client = None
        else:
            # Initialize the new Client
            self.client = genai.Client(api_key=self.api_key)

    def extract_candidate_data(self, raw_text: str) -> CandidateProfile:
        """
        Extracts structured data from unstructured text using Gemini.
        """
        if not self.client:
            return CandidateProfile(**MOCK_RESPONSE)

        try:
            # The prompt remains similar, but we can be more direct
            prompt = f"""
            Extract the following details from the text below into a JSON object.
            
            Required Keys:
            - name (string, use "Unknown" if missing)
            - role (string, use "TBD" if missing)
            - email (string, or null if missing)
            - salary (number, or 0 if missing)
            - currency (string, default "USD")
            - start_date (string YYYY-MM-DD, or null if missing)
            - location_country (string, default "Unknown")
            
            - citizenship (string, COUNTRY NAME ONLY. e.g., return "UAE" not "UAE citizen", return "Germany" not "German")
            
            - equity_grant (boolean)

            Text to analyze: "{raw_text}"
            """

            # New SDK Call Structure
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"  # Native JSON support!
                )
            )
            
            # The new SDK guarantees JSON string output with this config
            data = json.loads(response.text)
            
            return CandidateProfile(**data)

        except Exception as e:
            print(f"Gemini Extraction Failed: {e}")
            return CandidateProfile(**MOCK_RESPONSE)

    def determine_jurisdiction(self, country: str) -> str:
        """
        Determines the legal framework based on location.
        """
        if not country:
            return "General International Contractor Agreement"
            
        country = country.lower()
        
        # UAE Logic
        if any(x in country for x in ["uae", "dubai", "united arab emirates", "abudhabi", "difc"]):
            return "DIFC Employment Law (UAE)"
            
        # UK Logic (Added 'united kingdom')
        elif any(x in country for x in ["uk", "britain", "united kingdom", "england", "london"]):
            return "Employment Rights Act 1996 (UK)"
            
        # Germany Logic
        elif any(x in country for x in ["germany", "deutschland", "berlin", "munich"]):
            return "German Civil Code (BGB)"
            
        else:
            return "General International Contractor Agreement"