#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/demo/recordkeeper_exec_demo.mp4"
ART="/opt/cursor/artifacts/recordkeeper_exec_demo.mp4"

# Record primary monitor; trim to ~4:30 max
ffmpeg -y -f x11grab -video_size 1280x900 -framerate 24 -i :1.0+0,0 \
  -t 240 \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  "$OUT" &
FFPID=$!
sleep 2

python3 "$ROOT/scripts/record_exec_demo.py"

sleep 2
kill -INT "$FFPID" 2>/dev/null || true
wait "$FFPID" 2>/dev/null || true

cp -f "$OUT" "$ART"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT"
