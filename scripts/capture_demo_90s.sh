#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/demo/recordkeeper_demo_90s.mp4"
ART="/opt/cursor/artifacts/recordkeeper_demo_90s.mp4"
TMP="${OUT%.mp4}_raw.mp4"

# Warm caches + paint cream UI twice before recording (avoids gray first frame)
python3 "$ROOT/scripts/record_demo_90s.py" --warmup-only 2>/dev/null || true
sleep 1
python3 "$ROOT/scripts/record_demo_90s.py" --warmup-only 2>/dev/null || true
sleep 1

python3 - <<'PY'
import subprocess
import sys
from pathlib import Path

root = Path("/workspace")
out = root / "demo/recordkeeper_demo_90s.mp4"
art = Path("/opt/cursor/artifacts/recordkeeper_demo_90s.mp4")

rec = subprocess.run(
    [sys.executable, str(root / "scripts/record_demo_90s.py"), "--with-recording", str(out)],
    check=False,
)
if rec.returncode != 0:
    sys.exit(rec.returncode)

import shutil
shutil.copy2(out, art)

import json
import subprocess as sp
dur = float(
    sp.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(out),
        ],
        text=True,
    ).strip()
)
print(f"Duration: {dur}s")
if dur > 90.5:
    print("WARN: over 90s — tighten RESULT_HOLD_MS in record_demo_90s.py")
    sys.exit(1)
print("OK: within 90s")
PY
