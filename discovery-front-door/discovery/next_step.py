from __future__ import annotations

from .knowledge_bridge import KnowledgeBridge
from .models import NextStepResult


def resolve_next_step(provider: str | None, bridge: KnowledgeBridge) -> NextStepResult | None:
    if not provider:
        return NextStepResult(
            action="Confirm your 401(k) recordkeeper before continuing.",
            owner="beekeeper",
            source_status="verified",
        )
    return bridge.next_step_for_provider(provider)
