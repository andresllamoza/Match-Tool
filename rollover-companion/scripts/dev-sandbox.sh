#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pip install -q -r requirements.txt
echo "→ streamlit sandbox (3 surfaces)"
exec streamlit run sandbox/app.py --server.port 8502
