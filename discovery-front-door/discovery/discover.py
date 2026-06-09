from __future__ import annotations

from .models import ConfidenceTier, DiscoveryResult, LookupResult
from .ports import ProviderLookupPort


def _tier(confidence: float, label: str | None = None) -> ConfidenceTier:
    if label and label.lower() == "low":
        return ConfidenceTier.LOW
    if confidence >= 0.85:
        return ConfidenceTier.HIGH
    if confidence >= 0.60:
        return ConfidenceTier.MEDIUM
    return ConfidenceTier.LOW


def _disambiguation_question(employer_query: str) -> str:
    return (
        f"To narrow down '{employer_query}', which US state did you work in "
        "when you participated in this 401(k)?"
    )


def discover_employer(
    employer_query: str,
    matcher: ProviderLookupPort,
    advizorpro: ProviderLookupPort,
    *,
    years: list[int] | None = None,
    state: str | None = None,
) -> DiscoveryResult:
    matcher_result = matcher.lookup(employer_query, years=years, state=state)
    adv_result = advizorpro.lookup(employer_query, years=years, state=state)

    primary = matcher_result
    tier = _tier(primary.confidence, primary.raw_confidence_label)
    provider = primary.provider
    question = None

    if tier == ConfidenceTier.LOW or not provider:
        question = _disambiguation_question(employer_query)
        if not provider and adv_result.provider and adv_result.confidence >= 0.85:
            provider = adv_result.provider
            tier = ConfidenceTier.MEDIUM

    return DiscoveryResult(
        employer_query=employer_query,
        resolved_provider=provider,
        confidence_tier=tier,
        disambiguation_question=question if tier == ConfidenceTier.LOW else None,
        matcher_result=matcher_result,
        advizorpro_result=adv_result,
    )
