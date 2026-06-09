from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .events import EventLogger
from .knowledge import KnowledgeBase
from .models import ConfidenceTier, LookupResult


class LookupAdapter(Protocol):
    name: str

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult: ...


def _confidence_tier(
    matcher: LookupResult,
    advizor: LookupResult,
    agreement: bool,
) -> ConfidenceTier:
    if matcher.provider and advizor.provider and agreement:
        return ConfidenceTier.HIGH
    if matcher.provider and matcher.confidence >= 0.85:
        return ConfidenceTier.HIGH
    if advizor.provider and advizor.confidence >= 0.85:
        return ConfidenceTier.HIGH
    if matcher.provider or advizor.provider:
        return ConfidenceTier.MEDIUM
    return ConfidenceTier.LOW


def _pick_provider(matcher: LookupResult, advizor: LookupResult) -> str | None:
    if matcher.provider and advizor.provider:
        if matcher.provider == advizor.provider:
            return matcher.provider
        return matcher.provider
    return matcher.provider or advizor.provider


@dataclass
class LookupOutcome:
    employer_query: str
    resolved_provider: str | None
    confidence_tier: ConfidenceTier
    disambiguation_question: str | None
    disambiguation_options: list[str]
    matcher_result: LookupResult
    advizorpro_result: LookupResult
    agreement: bool
    uncovered_provider: str | None = None


class LookupService:
    def __init__(
        self,
        knowledge: KnowledgeBase,
        matcher: LookupAdapter,
        advizorpro: LookupAdapter,
        event_logger: EventLogger | None = None,
    ):
        self.knowledge = knowledge
        self.matcher = matcher
        self.advizorpro = advizorpro
        self.event_logger = event_logger or EventLogger()

    def lookup(self, employer_name: str) -> LookupOutcome:
        matcher_result = self.matcher.lookup(employer_name)
        advizor_result = self.advizorpro.lookup(employer_name)
        agreement = (
            matcher_result.provider is not None
            and advizor_result.provider is not None
            and matcher_result.provider == advizor_result.provider
        )
        tier = _confidence_tier(matcher_result, advizor_result, agreement)
        resolved = _pick_provider(matcher_result, advizor_result)

        self.event_logger.log_comparison(
            input_query=employer_name,
            matcher_result=matcher_result.provider,
            advizorpro_result=advizor_result.provider,
            agreement=agreement,
            confidence_tier=tier,
        )

        disambiguation_question: str | None = None
        disambiguation_options: list[str] = []
        disagree = (
            matcher_result.provider
            and advizor_result.provider
            and matcher_result.provider != advizor_result.provider
        )

        if tier == ConfidenceTier.LOW:
            disambiguation_question = (
                "Do you mean your former employer, or the financial company "
                "that holds the 401(k) (like Fidelity or Vanguard)?"
            )
            disambiguation_options = ["Former employer", "The 401(k) provider"]
        elif disagree:
            disambiguation_question = (
                "We found two possible recordkeepers. Which sounds right for your old 401(k)?"
            )
            disambiguation_options = sorted({matcher_result.provider, advizor_result.provider})
            resolved = None
            tier = ConfidenceTier.MEDIUM

        uncovered: str | None = None
        if resolved:
            try:
                self.knowledge.resolve_provider(resolved)
            except KeyError:
                uncovered = resolved
                resolved = None
                tier = ConfidenceTier.HIGH
                disambiguation_question = None
                disambiguation_options = []

        return LookupOutcome(
            employer_query=employer_name,
            resolved_provider=resolved if tier != ConfidenceTier.LOW else None,
            confidence_tier=tier,
            disambiguation_question=disambiguation_question,
            disambiguation_options=disambiguation_options,
            matcher_result=matcher_result,
            advizorpro_result=advizor_result,
            agreement=agreement,
            uncovered_provider=uncovered,
        )

    def resolve_provider_direct(self, provider_name: str) -> str:
        return self.knowledge.resolve_provider(provider_name)
