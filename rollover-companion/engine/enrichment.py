from __future__ import annotations

from .customer_copy import SYNTHETIC_CUSTOMER_NAME, format_check_payable
from .knowledge import KnowledgeBase
from .models import (
    ChannelContext,
    JourneyChannel,
    JourneyContext,
    JourneyScreen,
    JourneyState,
    LookupContext,
    RepQuestionView,
    ScreenEnrichment,
    TrackContext,
)


def build_enrichment(
    knowledge: KnowledgeBase,
    ctx: JourneyContext,
    screen: JourneyScreen,
) -> ScreenEnrichment:
    general = knowledge.general_guide
    enrichment = ScreenEnrichment(
        mailing_address=general.mailing_address,
        destination_name=general.destination_name,
        customer_display_name=SYNTHETIC_CUSTOMER_NAME,
        general_path=knowledge.is_general_path(ctx),
        requires_tax_selection=_needs_tax_selection(ctx),
        tax_options=_tax_options(knowledge) if _needs_tax_selection(ctx) else [],
    )

    recordkeeper = ctx.provider or ctx.uncovered_provider
    if ctx.employer_query and recordkeeper and ctx.state in {
        JourneyState.PROVIDER_IDENTIFIED,
        JourneyState.PROVIDER_NOT_COVERED,
    }:
        enrichment.lookup = LookupContext(
            employer_query=ctx.employer_query,
            matched_provider=recordkeeper,
        )

    if recordkeeper:
        pb = knowledge.playbook_for(ctx)
        enrichment.mechanism = pb.mechanism.value
        enrichment.check_destination = pb.check_destination
        enrichment.forward_step_required = pb.forward_step_required

        if screen.state in {
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
            JourneyState.FORMS_IN_PROGRESS,
        }:
            enrichment.channel_context = _channel_context(
                ctx, pb, general, knowledge.is_general_path(ctx)
            )

        if screen.phase.value == "track" or screen.state in {
            JourneyState.INITIATED,
            JourneyState.IN_FLIGHT,
        }:
            tg = general.track_guidance
            enrichment.track = TrackContext(
                typical_timeline=pb.sla_note or general.typical_processing_time,
                check_destination=pb.check_destination,
                follow_up_days=tg.follow_up_days,
                nothing_arrived_message=tg.nothing_arrived_message,
                mechanism_note=pb.preferred_path,
            )

    return enrichment


def _needs_tax_selection(ctx: JourneyContext) -> bool:
    return ctx.state == JourneyState.ACCESS_RECOVERED and not ctx.tax_fund_type


def _tax_options(knowledge: KnowledgeBase) -> list[dict[str, str]]:
    tr = knowledge.general_guide.tax_routing_customer
    return [
        {"id": "pre_tax", "label": "Pre-tax", "hint": tr.pre_tax},
        {"id": "roth", "label": "Roth", "hint": tr.roth},
        {"id": "both", "label": "Both pre-tax and Roth", "hint": tr.both},
        {"id": "pre_tax_to_roth", "label": "Pre-tax into a Roth IRA", "hint": tr.conversion_warning},
    ]


def _general_hints(general, step_text: str) -> tuple[list[str], list[str]]:
    lower = step_text.lower()
    portal_hints = (
        general.portal_menu_aliases
        if any(w in lower for w in ("withdrawal", "rollover", "distribution", "transfer"))
        else []
    )
    destination_hints = (
        general.destination_dropdown_aliases
        if any(w in lower for w in ("other", "pensionbee", "not listed", "provider"))
        else []
    )
    return portal_hints, destination_hints


def _channel_context(
    ctx: JourneyContext,
    playbook,
    general,
    is_general_path: bool,
) -> ChannelContext:
    mailing_address = general.mailing_address
    customer_name = SYNTHETIC_CUSTOMER_NAME
    payable = general_payable(playbook, mailing_address, customer_name)
    cs = playbook.call_script
    if ctx.channel == JourneyChannel.PHONE:
        step_text = cs.steps[ctx.step_index].text if ctx.step_index < len(cs.steps) else ""
        portal_hints, destination_hints = (
            _general_hints(general, step_text) if is_general_path else ([], [])
        )
        return ChannelContext(
            channel="phone",
            say_this=step_text,
            phone=cs.phone,
            intro=cs.intro if ctx.step_index == 0 else None,
            check_payable=_resolved_payable(cs.check_payable, customer_name),
            mailing_address=cs.mailing_address,
            rep_questions=[
                RepQuestionView(question=q.question, answer=q.answer) for q in cs.rep_questions
            ],
            step_label=f"Step {ctx.step_index + 1}",
            portal_menu_hints=portal_hints,
            destination_hints=destination_hints,
        )
    if ctx.channel == JourneyChannel.FORMS:
        field = playbook.form_guidance.fields[ctx.step_index]
        return ChannelContext(
            channel="forms",
            say_this=field.instruction,
            form_field_label=field.label,
            check_payable=payable,
            mailing_address=mailing_address,
            rep_questions=[],
            step_label=field.label,
        )
    step = playbook.steps[ctx.step_index]
    portal_hints, destination_hints = (
        _general_hints(general, step.text) if is_general_path else ([], [])
    )
    return ChannelContext(
        channel="online",
        say_this=step.text,
        mailing_address=mailing_address,
        check_payable=payable,
        rep_questions=[],
        step_label=f"Step {ctx.step_index + 1}",
        portal_menu_hints=portal_hints,
        destination_hints=destination_hints,
    )


def general_payable(
    playbook,
    mailing_address: str,
    customer_name: str = SYNTHETIC_CUSTOMER_NAME,
) -> str:
    if playbook.call_script.check_payable:
        return format_check_payable(playbook.call_script.check_payable, customer_name)
    return f"Payable to PensionBee — mail to {mailing_address}"


def _resolved_payable(raw: str | None, customer_name: str) -> str | None:
    if not raw:
        return None
    return format_check_payable(raw, customer_name)
