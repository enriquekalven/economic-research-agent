install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; source ~/.bashrc; }
	uv sync --dev --extra streamlit --extra jupyter --frozen

test:
	uv run pytest tests/unit && uv run pytest tests/integration

playground:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload &
	uv run streamlit run frontend/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

ui:
	uv run streamlit run streamlit/streamlit_app.py --browser.serverAddress=localhost --server.enableCORS=false --server.enableXsrfProtection=false

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
