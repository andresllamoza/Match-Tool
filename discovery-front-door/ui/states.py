"""UI state machine + safe discovery runner (presentation only)."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from discovery.flow import DiscoveryFlow
from discovery.knowledge_bridge import KnowledgeBridge
from discovery.models import BalanceRange, ConfidenceTier, DiscoveryOutcome
from discovery.ports import ProviderLookupPort

logger = logging.getLogger(__name__)


class UiState(str, Enum):
    INPUT = "input"
    RESULT = "result"
    LOW_CONFIDENCE = "low_confidence"
    ERROR = "error"


def classify_ui_state(outcome: DiscoveryOutcome) -> UiState:
    disc = outcome.discovery
    if disc.confidence_tier == ConfidenceTier.LOW or not disc.resolved_provider:
        return UiState.LOW_CONFIDENCE
    return UiState.RESULT


def run_discovery_safe(
    flow: DiscoveryFlow,
    employer: str,
    balance_range: BalanceRange,
    *,
    state: Optional[str] = None,
) -> tuple[Optional[DiscoveryOutcome], Optional[str]]:
    """Run discovery; return (outcome, error_message). Never raises to the UI."""
    try:
        outcome = flow.run(
            employer.strip(),
            balance_range,
            state=state.strip() if state and state.strip() else None,
        )
        return outcome, None
    except Exception:
        logger.exception("Discovery flow failed for employer=%r", employer)
        return None, "unexpected"
