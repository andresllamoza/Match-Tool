FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir \
    pydantic PyYAML fastapi "uvicorn[standard]" jinja2 pandas numpy rapidfuzz httpx

COPY api/ api/
COPY engine/ engine/
COPY adapters/ adapters/
COPY rollover-knowledge-layer/ rollover-knowledge-layer/
COPY data/employer_rk_index.csv data/employer_rk_index.csv

RUN mkdir -p data

ENV PB_COOKIE_SECURE=true
ENV PB_SESSION_DB=/app/data/pb_sessions.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-8000}/api/health" || exit 1

CMD uvicorn api.server:app --host 0.0.0.0 --port ${PORT:-8000}
