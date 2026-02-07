.PHONY: backend frontend setup activate help

help:
	@echo "Available commands:"
	@echo "  make activate  - Activate the Python environment"
	@echo "  make setup     - Create environment and install requirements"
	@echo "  make backend   - Run backend server with uvicorn"
	@echo "  make frontend  - Run frontend server with streamlit"

setup:
	python3 -m venv . && source bin/activate && pip install -r requirements.txt

activate:
	source bin/activate

backend:
	uvicorn backend.main:app --reload

frontend:
	streamlit run frontend/app.py

test:
	pytest tests/ -v