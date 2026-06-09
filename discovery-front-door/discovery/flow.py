from __future__ import annotations

from typing import Optional

from .comparison import comparison_from_discovery, log_comparison
from .discover import discover_employer
from .knowledge_bridge import KnowledgeBridge
from .models import BalanceRange, DiscoveryOutcome
from .next_step import resolve_next_step
from .ports import ProviderLookupPort
from .value import compute_value_reveal


class DiscoveryFlow:
    def __init__(
        self,
        advizorpro: ProviderLookupPort,
        matcher: ProviderLookupPort,
        knowledge: KnowledgeBridge,
    ):
        self.advizorpro = advizorpro
        self.matcher = matcher
        self.knowledge = knowledge

    def run(
        self,
        employer_name: str,
        balance_range: Optional[BalanceRange] = None,
        *,
        years: list[int] | None = None,
        state: str | None = None,
        match_rate: float = 0.01,
    ) -> DiscoveryOutcome:
        discovery = discover_employer(
            employer_name,
            self.matcher,
            self.advizorpro,
            years=years,
            state=state,
        )
        log_comparison(comparison_from_discovery(discovery))

        value = compute_value_reveal(balance_range, match_rate) if balance_range else None
        next_step = resolve_next_step(discovery.resolved_provider, self.knowledge)

        return DiscoveryOutcome(
            discovery=discovery,
            value_reveal=value,
            next_step=next_step,
        )
