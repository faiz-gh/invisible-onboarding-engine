import os
from fpdf import FPDF
from datetime import datetime

class PDFService:
    def __init__(self):
        # Ensure output directory exists
        self.output_dir = "data"
        self.template_dir = "backend/templates"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)

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

    def generate_contract(self, candidate_data, jurisdiction: str) -> str:
        """
        Dynamically loads the correct template, fills it, and generates a PDF.
        """
        # 1. Determine which template to use
        template_file = self._select_template_file(jurisdiction)
        raw_text = self._load_template(template_file)

        # 2. Prepare Data for Formatting
        # We handle missing data safely using .get or defaults from Pydantic
        fmt_data = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "timestamp": int(datetime.now().timestamp()),
            "name": candidate_data.name,
            "role": candidate_data.role,
            "citizenship": candidate_data.citizenship or "Not Specified",
            "start_date": candidate_data.start_date or "TBD",
            "currency": candidate_data.currency or "USD",
            "salary": candidate_data.salary or 0.0
        }

        # 3. Fill the Template (Simple String Formatting)
        # Note: If a key is missing in fmt_data, this might error, so we catch it.
        try:
            filled_text = raw_text.format(**fmt_data)
        except KeyError as e:
            print(f"⚠️ Template formatting error: Missing key {e}")
            filled_text = raw_text # Fallback to raw text if fill fails

        # 4. Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "DERIV", ln=True, align="C")
        pdf.ln(5)

        # Sub-header
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Generated via Invisible Onboarding Engine | {jurisdiction}", ln=True, align="C")
        pdf.line(10, 30, 200, 30) # Draw a line
        pdf.ln(10)

        # Body Content
        pdf.set_font("Arial", size=11)
        
        # We split by lines to handle Markdown-like headers purely visually
        for line in filled_text.split('\n'):
            line = line.strip()
            if not line:
                pdf.ln(2) # Small gap for empty lines
                continue
                
            if line.startswith("# "): # H1
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, line.replace("# ", "").upper(), ln=True)
                pdf.set_font("Arial", size=11)
            elif line.startswith("## "): # H2
                pdf.ln(4)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, line.replace("## ", ""), ln=True)
                pdf.set_font("Arial", size=11)
            elif line.startswith("**"): # Simple bolding hack (entire line)
                pdf.set_font("Arial", "B", 11)
                pdf.multi_cell(0, 6, line.replace("**", ""))
                pdf.set_font("Arial", size=11)
            else:
                pdf.multi_cell(0, 6, line)

        # 5. Handle Equity Grant (If Applicable)
        if candidate_data.equity_grant:
            pdf.add_page()
            equity_text = self._load_template("equity_grant.md")
            try:
                filled_equity = equity_text.format(**fmt_data)
            except:
                filled_equity = equity_text
            
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "ADDENDUM: EQUITY GRANT", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 6, filled_equity)

        # 6. Save
        filename = f"Contract_{candidate_data.name.replace(' ', '_')}_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(self.output_dir, filename)
        pdf.output(file_path)
        
        return file_path