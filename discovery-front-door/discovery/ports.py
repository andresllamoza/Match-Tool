from __future__ import annotations

from typing import Optional, Protocol

from .models import LookupResult


class ProviderLookupPort(Protocol):
    name: str

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult: ...
