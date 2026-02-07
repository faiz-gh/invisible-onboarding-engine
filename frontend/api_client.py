import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def generate_onboarding_packet(raw_text):
    """
    Sends the raw job description to the backend AI.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/generate-onboarding",
            json={"raw_text": raw_text}
        )
        response.raise_for_status() # Raise error for 400/500 codes
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Backend is offline. Is FastAPI running?"}
    except Exception as e:
        return {"error": f"Request Failed: {e}"}

def ask_policy_question(question):
    """
    New: Sends employee questions to the HR Policy Bot.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/ask-policy",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"answer": f"⚠️ Error connecting to HR Brain: {e}"}

def get_file_content(file_path):
    """
    Helper to read the generated PDF for display.
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    return None