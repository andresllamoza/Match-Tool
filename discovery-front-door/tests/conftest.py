import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(REPO_ROOT / "rollover-playbook-engine") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "rollover-playbook-engine"))
