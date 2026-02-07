from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models.schemas import CandidateProfile

class ComplianceEngine:
    def __init__(self):
        # 1. Knowledge Base: Canonical Names -> Rules
        self.minimum_wages = {
            "germany": {"amount": 40000, "currency": "EUR"},
            "united kingdom": {"amount": 25000, "currency": "GBP"},
            "united arab emirates": {"amount": 5000, "currency": "AED"}
        }
        
        self.visa_processing_times = {
            "united arab emirates": 21,
            "germany": 60,
            "united kingdom": 45
        }

        # 2. The Normalization Map
        # Maps common variations to a single Canonical Name (lowercase)
        self.country_aliases = {
            # UAE Variations
            "uae": "united arab emirates",
            "dubai": "united arab emirates",
            "abudhabi": "united arab emirates",
            "u.a.e.": "united arab emirates",
            "abu dhabi": "united arab emirates",
            
            # UK Variations
            "uk": "united kingdom",
            "britain": "united kingdom",
            "great britain": "united kingdom",
            "london": "united kingdom",
            "england": "united kingdom",
            
            # Germany Variations
            "de": "germany",
            "deutschland": "germany",
            "berlin": "germany",
            "munich": "germany"
        }

    def _normalize_country(self, name: Optional[str]) -> str:
        """
        Converts 'UAE', 'Dubai', 'U.A.E.' -> 'united arab emirates'
        """
        if not name:
            return "unknown"
        
        cleaned = name.lower().strip()
        return self.country_aliases.get(cleaned, cleaned)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None

    def check_visa_requirements(self, candidate: CandidateProfile) -> List[Dict]:
        alerts = []
        
        # 1. Normalize Inputs
        citizenship_norm = self._normalize_country(candidate.citizenship)
        location_norm = self._normalize_country(candidate.location_country)

        # 2. Comparison Logic
        if citizenship_norm == "unknown" or location_norm == "unknown":
            return alerts
            
        # If they match, NO Visa is needed
        if citizenship_norm == location_norm:
            return [] # Local Hire

        # 3. Visa Required Logic
        alerts.append({
            "type": "WORKFLOW_TRIGGER",
            "severity": "HIGH",
            "message": f"🛂 Visa Sponsorship Required: {candidate.citizenship} citizen hiring in {candidate.location_country}.",
        })

        # 4. Start Date Risk Analysis
        start_date = self._parse_date(candidate.start_date)
        if start_date:
            days_until_start = (start_date - datetime.now()).days
            
            # Use normalized key for lookup
            needed_days = self.visa_processing_times.get(location_norm, 30)

            # LOGIC FIX: Handle Past vs. Future Dates
            if days_until_start < 0:
                alerts.append({
                    "type": "DATA_ERROR",
                    "severity": "HIGH",
                    "message": f"⚠️ Invalid Start Date: The date {candidate.start_date} is in the past. Please check the year."
                })
            elif days_until_start < needed_days:
                sugg_date = (datetime.now() + timedelta(days=needed_days + 7)).strftime('%Y-%m-%d')
                alerts.append({
                    "type": "COMPLIANCE_RISK",
                    "severity": "CRITICAL",
                    "message": f"⚠️ Start Date Risk: {days_until_start} days is too short for {candidate.location_country} visa (avg {needed_days} days). Suggested Start: {sugg_date}"
                })

        return alerts

    def check_wage_compliance(self, candidate: CandidateProfile) -> List[Dict]:
        alerts = []
        if not candidate.salary:
            return alerts

        # Normalize location to find the rule
        location_norm = self._normalize_country(candidate.location_country)
        rule = self.minimum_wages.get(location_norm)
        
        if rule:
            # Check Amount
            if candidate.salary < rule["amount"]:
                alerts.append({
                    "type": "COMPLIANCE_RISK",
                    "severity": "HIGH",
                    "message": f"📉 Low Salary Warning: {candidate.salary} is below the {location_norm.title()} minimum of {rule['amount']}."
                })

        return alerts

    def analyze(self, candidate: CandidateProfile) -> Dict:
        """
        Main entry point. Runs all checks and returns a summary.
        """
        all_alerts = []
        all_alerts.extend(self.check_visa_requirements(candidate))
        all_alerts.extend(self.check_wage_compliance(candidate))
        
        # Calculate Key Dates
        start_date = self._parse_date(candidate.start_date)
        key_dates = {}
        if start_date:
            key_dates["probation_end"] = (start_date + timedelta(days=180)).strftime("%Y-%m-%d")
        
        return {
            "alerts": all_alerts,
            "projected_dates": key_dates
        }