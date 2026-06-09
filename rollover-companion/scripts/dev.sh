#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -q -r requirements.txt

SESSION_NAME="rollover-companion-dev"
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_NAME" 2>/dev/null || \
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_NAME" -c "$ROOT" -- "${SHELL:-bash}" -l

tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  "cd $ROOT && python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload" C-m

tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  "cd $ROOT/web && npm run dev -- -p 3000 -H 0.0.0.0" C-m

echo "API:  http://localhost:8000"
echo "Web:  http://localhost:3000"
echo "Agent: http://localhost:3000/agent"
