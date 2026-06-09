from __future__ import annotations

from .discover import _disambiguation_question, _tier
from .knowledge_bridge import KnowledgeBridge
from .models import AddTransferResult, ConfidenceTier
from .next_step import resolve_next_step
from .ports import ProviderLookupPort

ACCOUNT_TYPE_401K = "401(k)"


def run_add_transfer(
    employer_name: str,
    account_type: str,
    lookup: ProviderLookupPort,
    knowledge: KnowledgeBridge,
) -> AddTransferResult:
    if account_type != ACCOUNT_TYPE_401K:
        return AddTransferResult(
            employer_query=employer_name,
            account_type=account_type,
            provider=None,
            confidence_tier=ConfidenceTier.LOW,
            next_step=None,
            disambiguation_question="Only 401(k) transfers are supported in this flow.",
        )

    result = lookup.lookup(employer_name)
    tier = _tier(result.confidence, result.raw_confidence_label)
    question = None
    provider = result.provider

    if tier == ConfidenceTier.LOW or not provider:
        question = _disambiguation_question(employer_name)

    next_step = resolve_next_step(provider, knowledge) if provider else None

    return AddTransferResult(
        employer_query=employer_name,
        account_type=account_type,
        provider=provider,
        confidence_tier=tier,
        next_step=next_step,
        disambiguation_question=question if tier == ConfidenceTier.LOW else None,
    )
