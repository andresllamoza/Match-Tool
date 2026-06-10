from __future__ import annotations

from .knowledge import KnowledgeBase
from .models import JourneyContext

_PLACEHOLDER = "[your name]"


def resolve_check_payable(knowledge: KnowledgeBase, ctx: JourneyContext) -> str:
    """Single source of truth for check payable lines (FBO template + participant name)."""
    template = knowledge.general_guide.track_guidance.check_payable_template
    name = (ctx.participant_name or "").strip() or "your name"
    if _PLACEHOLDER in template:
        return template.replace(_PLACEHOLDER, name)
    return template
