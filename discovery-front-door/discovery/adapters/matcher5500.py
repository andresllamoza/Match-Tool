from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from ..models import LookupResult
from ..synthetic_data import SYNTHETIC_EMPLOYERS


class Local5500Adapter:
    """5500 matcher adapter — synthetic or real `src.matcher.match`."""

    name = "matcher5500"

    def __init__(self, lookup_fn):
        self._lookup = lookup_fn

    @classmethod
    def from_synthetic(cls) -> Local5500Adapter:
        def _lookup(employer_name: str, years=None, state=None) -> LookupResult:
            key = employer_name.strip().lower()
            for row in SYNTHETIC_EMPLOYERS:
                if row["employer"].lower() == key or key in row.get("aliases", []):
                    matcher = row.get("matcher")
                    if matcher is None:
                        return LookupResult(source="matcher5500", provider=None, confidence=0.0)
                    conf = row.get("matcher_confidence", 0.9)
                    return LookupResult(
                        source="matcher5500",
                        provider=matcher,
                        confidence=conf,
                        matched_employer_name=row["employer"],
                        raw_confidence_label=row.get("matcher_label"),
                    )
            return LookupResult(source="matcher5500", provider=None, confidence=0.0)

        return cls(_lookup)

    @classmethod
    def matcher_deps_available(cls) -> tuple[bool, str | None]:
        try:
            import numpy  # noqa: F401
            import pandas  # noqa: F401
            import rapidfuzz  # noqa: F401
        except ImportError as exc:
            return False, exc.name
        return True, None

    @classmethod
    def from_matcher(cls, repo_root: Path | None = None) -> Local5500Adapter:
        ok, missing = cls.matcher_deps_available()
        if not ok:
            raise ModuleNotFoundError(
                f"Matcher dependency {missing!r} is not installed. "
                "Fix discovery-front-door/requirements.txt or use from_synthetic()."
            )

        root = repo_root or Path(__file__).resolve().parents[3]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        from src.matcher import match as matcher_match  # noqa: WPS433

        def _lookup(employer_name: str, years=None, state=None) -> LookupResult:
            results = matcher_match(employer_name, top_n=1)
            if not results:
                return LookupResult(source="matcher5500", provider=None, confidence=0.0)
            best = results[0]
            return LookupResult(
                source="matcher5500",
                provider=best.recordkeeper,
                confidence=best.confidence,
                matched_employer_name=best.matched_employer_name,
                raw_confidence_label=best.confidence_label,
            )

        return cls(_lookup)

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult:
        return self._lookup(employer_name, years, state)
