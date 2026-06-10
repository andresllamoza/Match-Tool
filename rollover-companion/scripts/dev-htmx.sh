#!/usr/bin/env bash
# Pure Python dev server — FastAPI + HTMX + Tailwind CDN (no Node.js).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pip install -q -r requirements.txt
echo "→ http://127.0.0.1:8000/customer"
echo "→ http://127.0.0.1:8000/sandbox"
exec python3 -m uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload
