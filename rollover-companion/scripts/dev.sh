#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
WEB_DIR="$REPO_ROOT/web"

python3 -m pip install -q -r "$ROOT/requirements.txt"

SESSION_NAME="rollover-companion-dev"
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_NAME" 2>/dev/null || \
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_NAME" -c "$ROOT" -- "${SHELL:-bash}" -l

tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  "cd $ROOT && python3 -m uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload" C-m

tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  "cd $WEB_DIR && API_URL=http://127.0.0.1:8000 npm run dev -- -p 3000" C-m

echo "API:  http://127.0.0.1:8000"
echo "Web:  http://localhost:3000/app"
echo "Agent: http://localhost:3000/agent"
echo "Discovery handoff: http://localhost:3000/customer?employer=Target"
