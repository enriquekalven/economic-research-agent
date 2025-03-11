install:
	pip install .

test:
	pytest tests/unit && pytest tests/integration

playground:
	uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload &
	streamlit run frontend/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

backend:
	uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

ui:
	streamlit run streamlit/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

lint:
	codespell
	ruff check . --diff
	ruff format . --check --diff
	mypy .
