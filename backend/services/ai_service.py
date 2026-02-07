import json
import os
import re
from datetime import date
from ollama import Client
from ..models.schemas import CandidateProfile

# Mock data for fallback
MOCK_RESPONSE = {
    "name": "Alex Smith",
    "role": "Senior DevOps Engineer",
    "job_family": "Engineering",
    "email": "alex.smith@example.com",
    "salary": 25000,
    "currency": "AED",
    "start_date": "2023-11-01",
    "location_country": "UAE",
    "citizenship": "UK",
    "equity_grant": True
}

def get_windows_host_ip():
    """
    Auto-detects the Windows Host IP from inside WSL.
    """
    try:
        # Method 1: Check /etc/resolv.conf for the nameserver (usually the host)
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if "nameserver" in line:
                    ip = line.split()[1]
                    return ip
    except Exception:
        pass
    
    # Fallback: standard localhost (if not in WSL)
    return "127.0.0.1"

class AIService:
    def __init__(self):
        # 1. AUTO-DISCOVER THE HOST
        self.windows_ip = get_windows_host_ip()
        self.host_url = f"http://{self.windows_ip}:11434"
        
        print(f"🔍 Discovered Windows IP: {self.windows_ip}")
        print(f"🦙 Connecting to Ollama at: {self.host_url}")
        
        self.model = "ministral-3" # Ensure you have pulled this model!
        
        # 2. Initialize Client
        try:
            self.client = Client(host=self.host_url)
        except Exception as e:
            print(f"⚠️ Failed to initialize Client: {e}")
            self.client = None

    def extract_candidate_data(self, raw_text: str) -> CandidateProfile:
        today_str = date.today().strftime("%Y-%m-%d")

        prompt = f"""
        Current Date: {today_str} (Use this to resolve relative dates like "next month")
        
        You are an expert HR Data Extractor. Your goal is to extract structured data from the text below.
        
        CRITICAL INSTRUCTION - "job_family":
        Analyze the "role" and classify it into EXACTLY ONE of these categories:
        - "Sales" (if role involves Sales, BD, Account Exec)
        - "Engineering" (if role involves Dev, QA, Product, Data)
        - "Executive" (if role is C-level, VP, Director)
        - "General" (everything else)

        CRITICAL INSTRUCTION - "citizenship" & "location_country":
        Return the COUNTRY NAME ONLY. 
        - Example: "UAE" (not "UAE citizen")
        - Example: "Germany" (not "German")

        Required JSON Structure:
        {{
            "name": string (use "Unknown" if missing),
            "role": string (use "TBD" if missing),
            "job_family": string,
            "email": string or null,
            "salary": number (0 if missing),
            "currency": string (default "USD"),
            "start_date": string (YYYY-MM-DD) or null,
            "location_country": string (default "Unknown"),
            "citizenship": string or null,
            "equity_grant": boolean
        }}

        Text to analyze: "{raw_text}"
        
        Return ONLY the JSON object. Do not include any explanation or markdown formatting like ```json.
        """

        try:
            # 3. USE CLIENT CHAT
            response = self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': 'You are a JSON extractor.'},
                    {'role': 'user', 'content': prompt}
                ],
            )
            
            # Clean Output
            content = response.message.content.strip()
            # Remove markdown blocks if present
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            data = json.loads(content)
            return CandidateProfile(**data)

        except Exception as e:
            print(f"❌ Ollama Extraction Failed: {e}")
            print(f"   Target Host was: {self.host_url}")
            return CandidateProfile(**MOCK_RESPONSE)

    def determine_jurisdiction(self, country: str) -> str:
        """
        Robust Jurisdiction Matcher.
        Handles full names ("United Arab Emirates") and codes ("UAE").
        """
        if not country: 
            return "General International Contractor Agreement"
            
        country = country.lower().strip()
        
        # 1. UAE Logic (Added 'united arab emirates' and 'emirates')
        uae_keywords = ["uae", "dubai", "difc", "united arab emirates", "emirates", "abu dhabi"]
        if any(x in country for x in uae_keywords):
            return "DIFC Employment Law (UAE)"
            
        # 2. UK Logic (Added 'united kingdom')
        uk_keywords = ["uk", "britain", "london", "united kingdom", "england", "scotland"]
        if any(x in country for x in uk_keywords):
            return "Employment Rights Act 1996 (UK)"
            
        # 3. Germany Logic (Added 'deutschland')
        de_keywords = ["germany", "berlin", "deutschland", "munich", "frankfurt"]
        if any(x in country for x in de_keywords):
            return "German Civil Code (BGB)"
            
        # Fallback
        return "General International Contractor Agreement"

    def answer_policy_question(self, question: str) -> str:
        """
        Phase 2: Conversational HR Assistant
        """
        try:
            # Check if handbook exists
            path = os.path.join("data", "handbook.txt")
            if os.path.exists(path):
                with open(path, "r") as f:
                    policy_text = f.read()
            else:
                policy_text = "No handbook found."

            # OPTIMIZED PROMPT
            prompt = f"""
            You are the Deriv HR AI. Answer the employee's question based strictly on the policy text below.
            
            RULES:
            1. Be extremely concise. Maximum 2 sentences.
            2. Go straight to the answer. Do not say "Based on the handbook..." or "Hello".
            3. If the answer involves money, bold the amount (e.g., *$50*)."
            
            POLICY TEXT:
            {policy_text}
            
            QUESTION: {question}
            """

            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return response.message.content

        except Exception as e:
            return f"Sorry, I couldn't process that. Error: {e}"