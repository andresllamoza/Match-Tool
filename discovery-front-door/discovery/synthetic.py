from __future__ import annotations

from pathlib import Path

from .adapters.advizorpro import AdvizorProAdapter
from .adapters.matcher5500 import Local5500Adapter
from .synthetic_data import SYNTHETIC_EMPLOYERS

__all__ = ["SYNTHETIC_EMPLOYERS", "build_adapters"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def build_adapters(repo_root: Path | None = None):
    """
    Build AdvizorPro + 5500 matcher adapters for playbook flows.

    Uses the real DOL matcher when deps are installed and USE_SYNTHETIC is not set.
    """
    import os

    root = repo_root or REPO_ROOT
    if os.environ.get("USE_SYNTHETIC") == "1":
        return AdvizorProAdapter(), Local5500Adapter.from_synthetic()

    matcher_ready, _ = Local5500Adapter.matcher_deps_available()
    if matcher_ready:
        try:
            return AdvizorProAdapter(), Local5500Adapter.from_matcher(root)
        except (ModuleNotFoundError, ImportError):
            pass
    return AdvizorProAdapter(), Local5500Adapter.from_synthetic()
