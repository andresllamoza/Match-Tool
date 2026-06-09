"""Keep the repo root first on sys.path so `import app` resolves to the 5500 matcher."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))
