from __future__ import annotations

from typing import Optional, Protocol

from engine.models import LookupResult

from .synthetic_data import SYNTHETIC_EMPLOYERS


class LookupAdapter(Protocol):
    name: str

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult: ...


class AdvizorProAdapter:
    """Stub paid-DB adapter — swap `lookup` body for the real API."""

    name = "advizorpro"

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult:
        key = employer_name.strip().lower()
        for row in SYNTHETIC_EMPLOYERS:
            if row["employer"].lower() == key or key in row.get("aliases", []):
                adv = row.get("advizorpro")
                if adv is None:
                    return LookupResult(source=self.name, provider=None, confidence=0.0)
                return LookupResult(
                    source=self.name,
                    provider=adv,
                    confidence=0.99,
                    matched_employer_name=row["employer"],
                )
        return LookupResult(source=self.name, provider=None, confidence=0.0)
