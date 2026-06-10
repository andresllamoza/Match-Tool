from __future__ import annotations

from .customer_copy import customer_full_name
from .knowledge import KnowledgeBase
from .models import JourneyContext

_PLACEHOLDER = "[your name]"


def resolve_check_payable(knowledge: KnowledgeBase, ctx: JourneyContext) -> str:
    """Single source of truth for check payable lines (FBO template + participant name)."""
    template = knowledge.general_guide.track_guidance.check_payable_template
    name = (ctx.participant_name or "").strip()
    if not name:
        if ctx.customer_first_name or ctx.customer_last_name:
            name = customer_full_name(ctx.customer_first_name, ctx.customer_last_name)
        else:
            name = "your name"
    if _PLACEHOLDER in template:
        return template.replace(_PLACEHOLDER, name)
    return template
