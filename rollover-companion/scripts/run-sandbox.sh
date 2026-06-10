#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pip install -q -r requirements.txt
echo "→ http://127.0.0.1:8501  (Customer / BeeKeeper / Funnel)"
exec streamlit run sandbox/app.py --server.port 8501
