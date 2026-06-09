from __future__ import annotations

from .customer_copy import customer_next_copy
from .knowledge_bridge import KnowledgeBridge
from .models import NextStepResult


def resolve_next_step(provider: str | None, bridge: KnowledgeBridge) -> NextStepResult | None:
    if not provider:
        return NextStepResult(
            action=customer_next_copy(customer_message=None, action=None),
            owner="beekeeper",
            source_status="verified",
        )
    return bridge.next_step_for_provider(provider)
