"""Chain matchers: instant synthetic → bundled index → full DOL cache (local only)."""

from __future__ import annotations

from typing import Optional

from engine.models import LookupResult


class Hybrid5500Adapter:
    name = "matcher5500"

    def __init__(self, adapters: list):
        self._adapters = adapters

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult:
        best = LookupResult(source=self.name, provider=None, confidence=0.0)
        for adapter in self._adapters:
            result = adapter.lookup(employer_name, years=years, state=state)
            if result.provider and result.confidence >= 0.85:
                return result
            if result.provider and result.confidence > best.confidence:
                best = result
        return best
