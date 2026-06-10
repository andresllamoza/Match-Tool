#!/usr/bin/env bash
# PensionBee rollover product demo — discovery handoff + full guided companion.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"

echo "==> Installing engine deps (if needed)…"
pip install -q -r "$ROOT/rollover-companion/requirements.txt"

echo "==> Starting API on :$API_PORT"
cd "$ROOT/rollover-companion"
python3 -m uvicorn api.server:app --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Starting Next.js on :$WEB_PORT (rollover companion UI)"
cd "$ROOT/web"
if [[ ! -d node_modules ]]; then npm install; fi
API_URL="http://127.0.0.1:$API_PORT" npm run dev -- --port "$WEB_PORT" &
WEB_PID=$!
trap 'kill "$API_PID" "$WEB_PID" 2>/dev/null || true' EXIT

sleep 3
echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  FULL PRODUCT (guided rollover — use this)                  │"
echo "│  http://localhost:$WEB_PORT/customer                          │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│  DISCOVERY ONLY (employer lookup + \$ match — then handoff)   │"
echo "│  USE_SYNTHETIC=1 streamlit run discovery-front-door/app.py  │"
echo "│  Set ROLLOVER_COMPANION_URL=http://localhost:$WEB_PORT/customer │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
wait
