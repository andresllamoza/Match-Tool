"""Shared wiring between the DOL 5500 matcher and rollover playbook flows."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def use_synthetic_data() -> bool:
    return os.environ.get("USE_SYNTHETIC") == "1"


def ensure_repo_on_path(repo_root: Path | None = None) -> Path:
    root = (repo_root or REPO_ROOT).resolve()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def matcher_deps_available() -> tuple[bool, str | None]:
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
        import rapidfuzz  # noqa: F401
    except ImportError as exc:
        return False, exc.name
    return True, None


def should_use_real_matcher(repo_root: Path | None = None) -> bool:
    if use_synthetic_data():
        return False
    ok, _ = matcher_deps_available()
    if not ok:
        return False
    ensure_repo_on_path(repo_root)
    try:
        from src.matcher import match  # noqa: F401, WPS433
    except ImportError:
        return False
    return True
