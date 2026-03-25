#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
# --- Economic Research Agent (ERA) Dockerfile ---
# Built for High-Performance ADK 2.0 / Vertex AI Reasoning Engines.

FROM python:3.12-slim-bookworm AS builder

# 1. Environment & Path Logic
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 2. Sync Dependencies (Using UV for speed/safety)
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    pip install --break-system-packages uv && \
    uv sync --frozen --no-dev

# 3. Execution Phase
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# 4. Expose FastAPI Server (for local testing/Cloud Run)
EXPOSE 8000

# 5. Optimized Entrypoint (Standard ADK 2.0 Uvicorn Pattern)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
