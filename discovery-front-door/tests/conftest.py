import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
# Append so repo-root `app.py` is not shadowed when running the full suite.
for path in (ROOT, REPO_ROOT / "rollover-playbook-engine"):
    if str(path) not in sys.path:
        sys.path.append(str(path))
