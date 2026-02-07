import os
from fpdf import FPDF
from datetime import datetime
import time

class PDFService:
    def __init__(self):
        # Ensure output directory exists
        self.output_dir = "data"
        self.template_dir = "backend/templates"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)

        # CLEANUP: Run immediately on startup
        self._cleanup_old_files()

    def _load_template(self, filename: str) -> str:
        """Reads a markdown file from the templates directory."""
        path = os.path.join(self.template_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: Template {filename} not found."

    def _select_template_file(self, jurisdiction: str) -> str:
        """
        Maps AI detected jurisdiction to a physical file.
        Handles: "United Arab Emirates", "UAE", "Dubai", "DIFC", etc.
        """
        if not jurisdiction:
            return "contractor_agreement.md"

        # 1. Normalize
        j_lower = jurisdiction.lower().strip()

        # 2. MATCHING LOGIC
        
        # UAE / Dubai Logic
        if any(x in j_lower for x in ["united arab emirates", "uae", "dubai", "abudhabi", "difc"]):
            return "uae_labor.md"
        
        # UK Logic
        elif any(x in j_lower for x in ["united kingdom", "uk", "britain", "england", "london"]):
            return "uk_employment.md"
        
        # Germany Logic
        elif any(x in j_lower for x in ["germany", "deutschland", "berlin", "munich"]):
            return "german_employment.md"
        
        # Fallback
        else:
            print(f"⚠️ Jurisdiction '{jurisdiction}' not recognized. Using Default.")
            return "contractor_agreement.md"
    
    def _sanitize_text(self, text: str) -> str:
        """
        Aggressively converts text to Latin-1 compatible format.
        """
        # 1. Manual replacements for common "smart" characters
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '-',  # Dashes
            '\u2026': '...',               # Ellipsis
            '\u00A0': ' ',                 # Non-breaking space
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
            
        # 2. NUCLEAR OPTION: Encode to Latin-1, ignoring errors.
        # This guarantees no crash, even if it skips a weird emoji.
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def _get_dynamic_clauses(self, job_family: str) -> str:
        """
        Selects extra clauses based on Job Family.
        """
        clauses = []
        clause_dir = os.path.join(self.template_dir, "clauses")
        
        # 1. Engineering Clause
        if job_family == "Engineering":
            path = os.path.join(clause_dir, "ip_assignment.md")
            if os.path.exists(path):
                with open(path, "r") as f: clauses.append(f.read())

        # 2. Sales Clause
        elif job_family == "Sales":
            path = os.path.join(clause_dir, "sales_commission.md")
            if os.path.exists(path):
                with open(path, "r") as f: clauses.append(f.read())

        # 3. Executive Clause
        elif job_family == "Executive":
            path = os.path.join(clause_dir, "executive_severance.md")
            if os.path.exists(path):
                with open(path, "r") as f: clauses.append(f.read())
        
        return "\n\n".join(clauses)
    
    def _cleanup_old_files(self, age_minutes: int = 10):
        """
        Deletes PDF files older than 'age_minutes' to save space and privacy.
        """
        try:
            now = time.time()
            cutoff = now - (age_minutes * 60)
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                
                # Check if it's a PDF and older than cutoff
                if filename.endswith(".pdf") and os.path.isfile(file_path):
                    file_creation_time = os.path.getctime(file_path)
                    if file_creation_time < cutoff:
                        os.remove(file_path)
                        print(f"🗑️ Cleaned up old file: {filename}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

    def generate_contract(self, candidate_data, jurisdiction: str) -> dict:
        # Every time we generate a new file, we check for old ones.
        self._cleanup_old_files(age_minutes=10)

        # 1. Load Original
        template_file = self._select_template_file(jurisdiction)
        raw_text = self._load_template(template_file)

        # 2. Fetch Dynamic Clauses (The Logic Layer)
        dynamic_text = self._get_dynamic_clauses(candidate_data.job_family)

        # 3. Fill Data
        fmt_data = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "timestamp": int(datetime.now().timestamp()),
            "name": self._sanitize_text(candidate_data.name), # Sanitize Name!
            "role": self._sanitize_text(candidate_data.role), # Sanitize Role!
            "citizenship": self._sanitize_text(candidate_data.citizenship or "Not Specified"),
            "start_date": candidate_data.start_date or "TBD",
            "currency": candidate_data.currency or "USD",
            "salary": candidate_data.salary or 0.0,
            "dynamic_clauses": dynamic_text
        }

        try:
            filled_text = raw_text.format(**fmt_data)
        except Exception:
            filled_text = raw_text

        # 4. Sanitize the WHOLE body before PDF generation
        safe_body_text = self._sanitize_text(filled_text)

        # 5. Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Header (Sanitized just in case)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "DERIV", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "I", 10)
        # Sanitize Jurisdiction too
        safe_jurisdiction = self._sanitize_text(jurisdiction)
        pdf.cell(0, 10, f"Generated via Invisible Onboarding Engine | {safe_jurisdiction}", ln=True, align="C")
        pdf.line(10, 30, 200, 30)
        pdf.ln(10)

        # Body
        pdf.set_font("Arial", size=11)
        
        # Use SAFE text
        for line in safe_body_text.split('\n'):
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue
                
            if line.startswith("# "):
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, line.replace("# ", "").upper(), ln=True)
                pdf.set_font("Arial", size=11)
            elif line.startswith("## "):
                pdf.ln(4)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, line.replace("## ", ""), ln=True)
                pdf.set_font("Arial", size=11)
            else:
                pdf.multi_cell(0, 6, line)

        # 6. Save
        filename = f"Contract_{candidate_data.name.replace(' ', '_')}_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(self.output_dir, filename)
        pdf.output(file_path)
        
        return {
            "path": file_path,
            "original_text": raw_text,
            "final_text": filled_text # Return pretty text to UI
        }