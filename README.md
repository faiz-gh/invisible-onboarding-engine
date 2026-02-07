# Invisible Onboarding Engine

The **Invisible Onboarding Engine** is an AI-powered automation tool designed to streamline the employee onboarding process. Built for the Deriv AI Hackathon, it leverages LLMs to parse natural language job descriptions, generate compliant employment contracts, and answer HR policy questions instantly.

## 🚀 Features

### 1. 📄 Intelligent Contract Generation
*   **Natural Language Processing**: Simply paste an email or job description (e.g., "Hire Alex Smith as Senior DevOps Engineer in Dubai for 25k AED").
*   **Data Extraction**: Automatically extracts candidate details (Name, Role, Salary, Location, Citizenship) using AI.
*   **Jurisdiction Detection**: Identifies the correct legal jurisdiction based on the candidate's location.
*   **Dynamic PDF Creation**: Generates a ready-to-sign PDF contract tailored to the specific role and location.

### 2. 🛡️ Compliance & Risk Analysis
*   **Automated Risk Flags**: Scans for potential compliance issues such as visa requirements or salary thresholds.
*   **Diff View**: Provides an interactive side-by-side comparison of the original template vs. the final generated contract, highlighting AI-filled sections.

### 3. 💬 Ask HR Assistant (RAG)
*   **Policy Q&A**: A built-in chatbot that answers questions about company policies (e.g., "Can I work remotely from Bali?") by consulting the Employee Handbook.
*   **Retrieval-Augmented Generation (RAG)**: Ensures answers are accurate and grounded in your specific documents.

## 🛠️ Tech Stack

*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance API for handling AI logic and PDF generation.
*   **Frontend**: [Streamlit](https://streamlit.io/) - Interactive and user-friendly web interface.
*   **AI/LLM**: [Ollama](https://ollama.com/) - Local LLM integration for privacy and speed.
*   **PDF Generation**: `fpdf` - Programmatic PDF creation.
*   **Utilities**: `pydantic` for data validation, `python-dotenv` for configuration.

## 📦 Installation & Setup

### Prerequisites
*   Python 3.8+
*   `make` (optional, for convenience)
*   **Ollama** installed and running locally (or configured remote instance).

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/invisible-onboarding-engine.git
    cd invisible-onboarding-engine
    ```

2.  **Set up the environment:**
    We provide a `Makefile` to simplify setup.
    ```bash
    make setup
    # This creates a virtual environment and installs requirements from requirements.txt
    ```
    *Alternatively, manually:*
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory if needed (e.g., for API keys or custom config).

## 🏃‍♂️ Usage

You need to run both the backend API and the frontend UI.

### 1. Start the Backend
Open a terminal and run:
```bash
make backend
# Or: uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend
Open a **new** terminal, activate the environment, and run:
```bash
make frontend
# Or: streamlit run frontend/app.py
```
The UI will open in your browser at `http://localhost:8501`.

## 📂 Project Structure

```
├── backend/
│   ├── main.py             # FastAPI entry point
│   ├── models/             # Pydantic schemas
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic (AI, PDF, Compliance)
│   └── templates/          # Contract templates
├── frontend/
│   ├── app.py              # Streamlit application
│   └── components/         # UI components
├── data/                   # Data storage for RAG/Docs
├── requirements.txt        # Python dependencies
└── Makefile                # Command shortcuts
```
