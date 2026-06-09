from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BalanceRange(str, Enum):
    R_0_10K = "0_10k"
    R_10_50K = "10_50k"
    R_50_100K = "50_100k"
    R_100_250K = "100_250k"
    R_250K_PLUS = "250k_plus"


BALANCE_RANGE_BOUNDS: dict[BalanceRange, tuple[int, int]] = {
    BalanceRange.R_0_10K: (0, 10_000),
    BalanceRange.R_10_50K: (10_000, 50_000),
    BalanceRange.R_50_100K: (50_000, 100_000),
    BalanceRange.R_100_250K: (100_000, 250_000),
    BalanceRange.R_250K_PLUS: (250_000, 500_000),
}


class ConfidenceTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LookupResult(BaseModel):
    source: str
    provider: Optional[str] = None
    confidence: float = 0.0
    matched_employer_name: Optional[str] = None
    raw_confidence_label: Optional[str] = None


class DiscoveryResult(BaseModel):
    employer_query: str
    resolved_provider: Optional[str] = None
    confidence_tier: ConfidenceTier
    disambiguation_question: Optional[str] = None
    matcher_result: LookupResult
    advizorpro_result: LookupResult


class ValueReveal(BaseModel):
    """Illustrative match from a self-reported balance range — no exact balance."""

    balance_range: BalanceRange
    match_rate: float
    match_low: int
    match_high: int
    disclaimer: str = (
        "Illustrative promotional match based on your selected balance range. "
        "Not guaranteed."
    )


class NextStepResult(BaseModel):
    action: str
    owner: str
    source_status: str
    provenance_warning: Optional[str] = None


class ComparisonEvent(BaseModel):
    employer_query: str
    matcher_provider: Optional[str]
    advizorpro_provider: Optional[str]
    agreement: bool


class DiscoveryOutcome(BaseModel):
    discovery: DiscoveryResult
    value_reveal: Optional[ValueReveal] = None
    next_step: Optional[NextStepResult] = None


class AddTransferResult(BaseModel):
    employer_query: str
    account_type: str
    provider: Optional[str]
    confidence_tier: ConfidenceTier
    next_step: Optional[NextStepResult] = None
    disambiguation_question: Optional[str] = None
