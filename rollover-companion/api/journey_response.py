"""Journey response wrapping shared by JSON and HTML routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from api.sessions import get_engine
from engine.enrichment import build_enrichment
from engine.models import (
    JourneyContext,
    JourneyScreen,
    JourneyState,
    ScreenEnrichment,
)


class JourneyResponse(BaseModel):
    context: JourneyContext
    screen: JourneyScreen
    step_index: int = 0
    total_steps: int = 0
    enrichment: ScreenEnrichment = Field(default_factory=ScreenEnrichment)
    provider_intel: dict[str, Any] = Field(default_factory=dict)


def _enrich_intel(ctx: JourneyContext, screen: JourneyScreen) -> dict[str, Any]:
    engine = get_engine()
    intel: dict[str, Any] = {
        "provider_status": (
            "RECONSTRUCTED"
            if screen.has_reconstructed_content
            else ("PENDING" if ctx.state == JourneyState.PROVIDER_UNKNOWN else "VERIFIED")
        ),
        "agent_action_script": screen.next_beekeeper_script,
        "escalation_triggers": [],
        "failure_modes": [],
        "knowledge_rules": [],
    }
    if not ctx.provider and not ctx.uncovered_provider:
        return intel

    pb = engine.knowledge.playbook_for(ctx)
    intel.update(
        {
            "mechanism": pb.mechanism.value,
            "check_destination": pb.check_destination,
            "forward_step_required": pb.forward_step_required,
            "portal": pb.portal,
            "flags_available": [],
            "general_path": engine.knowledge.is_general_path(ctx),
            "rep_questions": [q.model_dump() for q in pb.call_script.rep_questions],
            "call_phone": pb.call_script.phone,
            "call_intro": pb.call_script.intro,
            "escalation_triggers": [t.flag for t in pb.escalation_triggers],
            "failure_modes": [f.flag for f in pb.failure_modes],
        }
    )
    rules: list[dict[str, str]] = []
    if pb.call_script.phone:
        rules.append(
            {
                "title": f"{pb.provider} Phone Script Fallback",
                "body": pb.call_script.intro or f"Call {pb.call_script.phone}",
            }
        )
    for trigger in pb.escalation_triggers:
        rules.append({"title": trigger.flag, "body": trigger.action})
    for failure in pb.failure_modes:
        rules.append({"title": failure.flag, "body": failure.routing_action})
    if pb.access_recovery.lockout_fallback.phone:
        rules.append(
            {
                "title": f"{pb.provider} Access Recovery",
                "body": pb.access_recovery.lockout_fallback.what_to_say,
            }
        )
    if "notary" in " ".join(pb.edge_cases).lower():
        rules.append(
            {
                "title": f"{pb.provider} Notary Details",
                "body": " ; ".join(pb.edge_cases),
            }
        )
    intel["knowledge_rules"] = rules
    return intel


def _step_totals(ctx: JourneyContext) -> tuple[int, int]:
    if not ctx.provider and not ctx.uncovered_provider:
        return ctx.step_index, 0
    pb = get_engine().knowledge.playbook_for(ctx)
    if ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        return ctx.step_index, len(pb.steps)
    if ctx.state == JourneyState.PHONE_IN_PROGRESS:
        return ctx.step_index, len(pb.call_script.steps)
    if ctx.state == JourneyState.FORMS_IN_PROGRESS:
        return ctx.step_index, len(pb.form_guidance.fields)
    return ctx.step_index, 0


def wrap_journey(
    ctx: JourneyContext,
    screen: JourneyScreen,
    *,
    include_intel: bool = False,
) -> JourneyResponse:
    engine = get_engine()
    step_index, total_steps = _step_totals(ctx)
    return JourneyResponse(
        context=ctx,
        screen=screen,
        step_index=step_index,
        total_steps=total_steps,
        enrichment=build_enrichment(engine.knowledge, ctx, screen),
        provider_intel=_enrich_intel(ctx, screen) if include_intel else {},
    )
