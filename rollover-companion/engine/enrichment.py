from __future__ import annotations

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
        requires_tax_selection=_needs_tax_selection(ctx),
        tax_options=_tax_options(knowledge) if _needs_tax_selection(ctx) else [],
    )

    if ctx.employer_query and ctx.provider and ctx.state == JourneyState.PROVIDER_IDENTIFIED:
        enrichment.lookup = LookupContext(
            employer_query=ctx.employer_query,
            matched_provider=ctx.provider,
        )

    if ctx.provider:
        pb = knowledge.get(ctx.provider)
        enrichment.mechanism = pb.mechanism.value
        enrichment.check_destination = pb.check_destination
        enrichment.forward_step_required = pb.forward_step_required

        if screen.state in {
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
            JourneyState.FORMS_IN_PROGRESS,
        }:
            enrichment.channel_context = _channel_context(ctx, pb, general.mailing_address)

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


def _channel_context(ctx: JourneyContext, playbook, mailing_address: str) -> ChannelContext:
    cs = playbook.call_script
    if ctx.channel == JourneyChannel.PHONE:
        step_text = cs.steps[ctx.step_index].text if ctx.step_index < len(cs.steps) else ""
        return ChannelContext(
            channel="phone",
            say_this=step_text,
            phone=cs.phone,
            intro=cs.intro if ctx.step_index == 0 else None,
            check_payable=cs.check_payable,
            mailing_address=cs.mailing_address,
            rep_questions=[
                RepQuestionView(question=q.question, answer=q.answer) for q in cs.rep_questions
            ],
            step_label=f"Step {ctx.step_index + 1}",
        )
    if ctx.channel == JourneyChannel.FORMS:
        field = playbook.form_guidance.fields[ctx.step_index]
        return ChannelContext(
            channel="forms",
            say_this=field.instruction,
            form_field_label=field.label,
            check_payable=general_payable(playbook, mailing_address),
            mailing_address=mailing_address,
            rep_questions=[],
            step_label=field.label,
        )
    step = playbook.steps[ctx.step_index]
    return ChannelContext(
        channel="online",
        say_this=step.text,
        mailing_address=mailing_address,
        check_payable=general_payable(playbook, mailing_address),
        rep_questions=[],
        step_label=f"Step {ctx.step_index + 1}",
    )


def general_payable(playbook, mailing_address: str) -> str:
    if playbook.call_script.check_payable:
        return playbook.call_script.check_payable
    return f"Payable to PensionBee — mail to {mailing_address}"
