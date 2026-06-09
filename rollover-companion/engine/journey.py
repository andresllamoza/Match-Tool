from __future__ import annotations

import uuid
from typing import Callable, Optional

from .events import EventLogger
from .guardrails import collect_triggered_actions, resolve_next_action
from .knowledge import KnowledgeBase
from .lookup import LookupService
from .models import (
    ConfidenceTier,
    FunnelStage,
    GuidanceItem,
    JourneyChannel,
    JourneyContext,
    JourneyPhase,
    JourneyScreen,
    JourneyState,
    Owner,
    SourceStatus,
    Step,
)


class InvalidTransitionError(ValueError):
    pass


TRANSITIONS: dict[tuple[JourneyState, str], JourneyState] = {
    (JourneyState.PROVIDER_UNKNOWN, "lookup_high_confidence"): JourneyState.PROVIDER_IDENTIFIED,
    (JourneyState.PROVIDER_UNKNOWN, "lookup_low_confidence"): JourneyState.PROVIDER_UNKNOWN,
    (JourneyState.PROVIDER_UNKNOWN, "provider_direct"): JourneyState.PROVIDER_IDENTIFIED,
    (JourneyState.PROVIDER_UNKNOWN, "disambiguate"): JourneyState.PROVIDER_IDENTIFIED,
    (JourneyState.PROVIDER_IDENTIFIED, "can_access_yes"): JourneyState.ACCESS_RECOVERED,
    (JourneyState.PROVIDER_IDENTIFIED, "can_access_no"): JourneyState.ACCESS_BLOCKED,
    (JourneyState.ACCESS_BLOCKED, "access_recovered"): JourneyState.ACCESS_RECOVERED,
    (JourneyState.ACCESS_BLOCKED, "escalate"): JourneyState.ESCALATED,
    (JourneyState.ACCESS_RECOVERED, "choose_online"): JourneyState.ONLINE_IN_PROGRESS,
    (JourneyState.ACCESS_RECOVERED, "choose_phone"): JourneyState.PHONE_IN_PROGRESS,
    (JourneyState.ACCESS_RECOVERED, "choose_forms"): JourneyState.FORMS_IN_PROGRESS,
    (JourneyState.ONLINE_IN_PROGRESS, "step_done"): JourneyState.ONLINE_IN_PROGRESS,
    (JourneyState.ONLINE_IN_PROGRESS, "all_steps_done"): JourneyState.INITIATED,
    (JourneyState.ONLINE_IN_PROGRESS, "step_stuck"): JourneyState.STUCK,
    (JourneyState.PHONE_IN_PROGRESS, "step_done"): JourneyState.PHONE_IN_PROGRESS,
    (JourneyState.PHONE_IN_PROGRESS, "all_steps_done"): JourneyState.INITIATED,
    (JourneyState.PHONE_IN_PROGRESS, "step_stuck"): JourneyState.STUCK,
    (JourneyState.FORMS_IN_PROGRESS, "step_done"): JourneyState.FORMS_IN_PROGRESS,
    (JourneyState.FORMS_IN_PROGRESS, "all_steps_done"): JourneyState.INITIATED,
    (JourneyState.FORMS_IN_PROGRESS, "step_stuck"): JourneyState.STUCK,
    (JourneyState.STUCK, "escalate"): JourneyState.ESCALATED,
    (JourneyState.STUCK, "resume_online"): JourneyState.ONLINE_IN_PROGRESS,
    (JourneyState.STUCK, "resume_phone"): JourneyState.PHONE_IN_PROGRESS,
    (JourneyState.STUCK, "resume_forms"): JourneyState.FORMS_IN_PROGRESS,
    (JourneyState.INITIATED, "confirm_in_flight"): JourneyState.IN_FLIGHT,
    (JourneyState.IN_FLIGHT, "mark_complete"): JourneyState.COMPLETE,
    (JourneyState.PROVIDER_IDENTIFIED, "escalate"): JourneyState.ESCALATED,
    (JourneyState.ACCESS_RECOVERED, "escalate"): JourneyState.ESCALATED,
    (JourneyState.ONLINE_IN_PROGRESS, "escalate"): JourneyState.ESCALATED,
    (JourneyState.PHONE_IN_PROGRESS, "escalate"): JourneyState.ESCALATED,
    (JourneyState.FORMS_IN_PROGRESS, "escalate"): JourneyState.ESCALATED,
    (JourneyState.IN_FLIGHT, "escalate"): JourneyState.ESCALATED,
}


def _phase_for_state(state: JourneyState) -> JourneyPhase:
    if state == JourneyState.PROVIDER_UNKNOWN:
        return JourneyPhase.FIND
    if state in {JourneyState.PROVIDER_IDENTIFIED, JourneyState.ACCESS_BLOCKED, JourneyState.ACCESS_RECOVERED}:
        return JourneyPhase.ACCESS
    if state in {
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
        JourneyState.FORMS_IN_PROGRESS,
        JourneyState.INITIATED,
        JourneyState.STUCK,
    }:
        return JourneyPhase.ROLLOVER
    return JourneyPhase.TRACK


def _step_to_guidance(step: Step) -> GuidanceItem:
    return GuidanceItem(
        text=step.text,
        owner=step.owner,
        source_status=step.source_status,
        reconstructed=step.source_status == SourceStatus.RECONSTRUCTED,
    )


class JourneyEngine:
    def __init__(
        self,
        knowledge: KnowledgeBase | None = None,
        lookup_service: LookupService | None = None,
        event_logger: EventLogger | None = None,
    ):
        self.knowledge = knowledge or KnowledgeBase.from_dir()
        self.event_logger = event_logger or EventLogger()
        if lookup_service is None:
            from adapters.advizorpro import AdvizorProAdapter
            from adapters.matcher5500 import Local5500Adapter

            lookup_service = LookupService(
                self.knowledge,
                Local5500Adapter.from_synthetic(),
                AdvizorProAdapter(),
                self.event_logger,
            )
        self.lookup_service = lookup_service

    def start(self) -> JourneyContext:
        return JourneyContext(journey_id=str(uuid.uuid4()))

    def _transition(
        self,
        ctx: JourneyContext,
        action: str,
        outcome: str,
        metadata: dict | None = None,
    ) -> JourneyContext:
        key = (ctx.state, action)
        if key not in TRANSITIONS:
            raise InvalidTransitionError(f"Invalid transition: {ctx.state.value} + {action}")
        new_state = TRANSITIONS[key]
        ctx.state = new_state
        self.event_logger.log_journey(
            state=new_state,
            provider=ctx.provider,
            channel=ctx.channel,
            action=action,
            outcome=outcome,
            metadata=metadata or {},
            journey_id=ctx.journey_id,
        )
        return ctx

    def lookup_employer(self, ctx: JourneyContext, employer_name: str) -> JourneyScreen:
        outcome = self.lookup_service.lookup(employer_name)
        ctx.employer_query = employer_name
        ctx.disambiguation_question = outcome.disambiguation_question
        ctx.disambiguation_options = outcome.disambiguation_options

        if outcome.disambiguation_question and not outcome.resolved_provider:
            self._transition(ctx, "lookup_low_confidence", "disambiguation_required")
        elif outcome.confidence_tier == ConfidenceTier.LOW:
            self._transition(ctx, "lookup_low_confidence", "disambiguation_required")
        else:
            ctx.provider = outcome.resolved_provider
            self._transition(ctx, "lookup_high_confidence", outcome.resolved_provider or "unknown")

        return self.render(ctx)

    def set_provider_direct(self, ctx: JourneyContext, provider_name: str) -> JourneyScreen:
        ctx.provider = self.lookup_service.resolve_provider_direct(provider_name)
        ctx.disambiguation_question = None
        ctx.disambiguation_options = []
        self._transition(ctx, "provider_direct", ctx.provider)
        return self.render(ctx)

    def disambiguate(self, ctx: JourneyContext, answer: str) -> JourneyScreen:
        answer_lower = answer.strip().lower()
        if answer_lower in {"former employer", "employer"}:
            ctx.disambiguation_question = "What was your former employer's name?"
            ctx.disambiguation_options = []
            return self.render(ctx)

        for provider in self.knowledge.list_providers():
            if provider.lower() in answer_lower or answer_lower == provider.lower():
                ctx.provider = provider
                break
        else:
            try:
                ctx.provider = self.lookup_service.resolve_provider_direct(answer)
            except KeyError:
                ctx.disambiguation_question = "Which company manages your old 401(k)?"
                ctx.disambiguation_options = self.knowledge.list_providers()
                return self.render(ctx)

        ctx.disambiguation_question = None
        ctx.disambiguation_options = []
        self._transition(ctx, "disambiguate", ctx.provider or answer)
        return self.render(ctx)

    def submit_access(self, ctx: JourneyContext, can_login: bool) -> JourneyScreen:
        action = "can_access_yes" if can_login else "can_access_no"
        self._transition(ctx, action, "access_check")
        return self.render(ctx)

    def submit_access_recovered(self, ctx: JourneyContext) -> JourneyScreen:
        if ctx.state != JourneyState.ACCESS_BLOCKED:
            raise InvalidTransitionError("access_recovered only valid from access_blocked")
        self._transition(ctx, "access_recovered", "credentials_restored")
        return self.render(ctx)

    def choose_channel(self, ctx: JourneyContext, channel: JourneyChannel) -> JourneyScreen:
        ctx.channel = channel
        ctx.step_index = 0
        action_map = {
            JourneyChannel.ONLINE: "choose_online",
            JourneyChannel.PHONE: "choose_phone",
            JourneyChannel.FORMS: "choose_forms",
        }
        self._transition(ctx, action_map[channel], channel.value)
        return self.render(ctx)

    def advance_step(self, ctx: JourneyContext, outcome: str) -> JourneyScreen:
        if outcome == "stuck":
            prev_channel = ctx.channel
            self._transition(ctx, "step_stuck", "user_stuck")
            ctx.channel = prev_channel
            return self.render(ctx)

        if ctx.state not in {
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
            JourneyState.FORMS_IN_PROGRESS,
        }:
            raise InvalidTransitionError(f"advance_step invalid in {ctx.state.value}")

        playbook = self.knowledge.get(ctx.provider)  # type: ignore[arg-type]
        total = self._total_steps(ctx, playbook)
        ctx.step_index += 1
        if ctx.step_index >= total:
            self._transition(ctx, "all_steps_done", "channel_complete")
        else:
            self._transition(ctx, "step_done", f"step_{ctx.step_index}")
        return self.render(ctx)

    def confirm_in_flight(self, ctx: JourneyContext) -> JourneyScreen:
        self._transition(ctx, "confirm_in_flight", "tracking_started")
        return self.render(ctx)

    def mark_complete(self, ctx: JourneyContext) -> JourneyScreen:
        self._transition(ctx, "mark_complete", "funds_received")
        return self.render(ctx)

    def escalate(self, ctx: JourneyContext, reason: str) -> JourneyScreen:
        ctx.flags["escalated"] = True
        self._transition(ctx, "escalate", reason)
        return self.render(ctx)

    def set_flag(self, ctx: JourneyContext, flag: str, value: bool = True) -> JourneyScreen:
        ctx.flags[flag] = value
        if flag == "pre_tax_to_roth" and value:
            return self.escalate(ctx, "pre_tax_to_roth_conversion")
        return self.render(ctx)

    def resume_from_stuck(self, ctx: JourneyContext) -> JourneyScreen:
        if ctx.state != JourneyState.STUCK:
            raise InvalidTransitionError("resume only valid from stuck")
        channel = ctx.channel or JourneyChannel.ONLINE
        action_map = {
            JourneyChannel.ONLINE: "resume_online",
            JourneyChannel.PHONE: "resume_phone",
            JourneyChannel.FORMS: "resume_forms",
        }
        self._transition(ctx, action_map[channel], "user_resumed")
        return self.render(ctx)

    def _total_steps(self, ctx: JourneyContext, playbook) -> int:
        if ctx.channel == JourneyChannel.ONLINE:
            return len(playbook.steps)
        if ctx.channel == JourneyChannel.PHONE:
            return len(playbook.call_script.steps)
        return len(playbook.form_guidance.fields)

    def render(self, ctx: JourneyContext) -> JourneyScreen:
        phase = _phase_for_state(ctx.state)
        guidance: list[GuidanceItem] = []
        edge_cases: list[str] = []
        headline = ""
        body = ""
        primary = ""
        secondary: list[str] = []
        agent_notes: list[str] = []
        beekeeper_script: str | None = None
        sla_note: str | None = None
        active_escalations = []
        provenance_warning: str | None = None
        has_reconstructed = False
        confidence: ConfidenceTier | None = None

        if ctx.state == JourneyState.PROVIDER_UNKNOWN:
            headline = "Let's find your old 401(k)"
            body = self.knowledge.general_guide.employer_vs_provider_note
            primary = "Search by employer or provider"
            secondary = ["I know my 401(k) provider"]
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=phase,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                disambiguation_question=ctx.disambiguation_question,
                disambiguation_options=ctx.disambiguation_options,
            )

        playbook = self.knowledge.get(ctx.provider) if ctx.provider else None
        if playbook:
            edge_cases = list(playbook.edge_cases)
            sla_note = playbook.sla_note or self.knowledge.general_guide.typical_processing_time
            active_escalations, active_failures = collect_triggered_actions(
                self.knowledge, playbook, ctx.flags
            )
            if active_escalations or active_failures:
                top = (active_escalations or active_failures)[0]
                beekeeper_script = top.action
                agent_notes.append(f"Escalation/failure active: {top.flag}")

        if ctx.state == JourneyState.PROVIDER_IDENTIFIED and playbook:
            headline = f"Can you log in to {playbook.portal or playbook.provider}?"
            body = playbook.preferred_path
            primary = "Yes, I can log in"
            secondary = ["No — I need help getting access"]
            for ec in edge_cases:
                agent_notes.append(f"Edge case to surface: {ec}")
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.ACCESS,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                sla_note=sla_note,
                disambiguation_question=ctx.disambiguation_question,
                disambiguation_options=ctx.disambiguation_options,
            )

        if ctx.state == JourneyState.ACCESS_BLOCKED and playbook:
            ar = playbook.access_recovery
            headline = f"Let's get you into {ar.portal_name}"
            body = "You'll need: " + ", ".join(ar.info_needed)
            guidance = [_step_to_guidance(s) for s in ar.reset_steps + ar.first_time_setup_steps]
            guidance.append(
                GuidanceItem(
                    text=f"Locked out? Call {ar.lockout_fallback.phone} and say: {ar.lockout_fallback.what_to_say}",
                    owner=ar.lockout_fallback.owner,
                    source_status=ar.lockout_fallback.source_status,
                    reconstructed=ar.lockout_fallback.source_status == SourceStatus.RECONSTRUCTED,
                )
            )
            primary = "I'm in now"
            secondary = ["Still locked out — get a BeeKeeper"]
            has_reconstructed = any(g.reconstructed for g in guidance)
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.ACCESS,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                guidance=guidance,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                has_reconstructed_content=has_reconstructed,
                provenance_warning=(
                    "Some portal steps are reconstructed — double-check this screen."
                    if has_reconstructed
                    else None
                ),
                sla_note=sla_note,
            )

        if ctx.state == JourneyState.ACCESS_RECOVERED and playbook:
            headline = "How would you like to do your rollover?"
            body = playbook.check_destination
            primary = "Online portal"
            secondary = ["Phone", "Paper forms"]
            for ec in edge_cases:
                agent_notes.append(f"Pre-empt: {ec}")
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.ROLLOVER,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                sla_note=sla_note,
            )

        if ctx.state in {
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
            JourneyState.FORMS_IN_PROGRESS,
        } and playbook:
            if ctx.channel == JourneyChannel.ONLINE:
                steps = playbook.steps
                headline = f"Step {ctx.step_index + 1} of {len(steps)}"
                body = steps[ctx.step_index].text
                guidance = [_step_to_guidance(steps[ctx.step_index])]
            elif ctx.channel == JourneyChannel.PHONE:
                cs = playbook.call_script
                steps = cs.steps
                headline = f"Call script — step {ctx.step_index + 1} of {len(steps)}"
                step_text = steps[ctx.step_index].text
                if ctx.step_index == 0:
                    body = f"Call {cs.phone}. {cs.intro}\n\n{step_text}"
                    agent_notes.append(f"Phone: {cs.phone} — {cs.intro}")
                else:
                    body = step_text
                guidance = [_step_to_guidance(steps[ctx.step_index])]
            else:
                fields = playbook.form_guidance.fields
                headline = f"Form field: {fields[ctx.step_index].label}"
                body = fields[ctx.step_index].instruction
                guidance = [
                    GuidanceItem(
                        text=fields[ctx.step_index].instruction,
                        owner=Owner.USER,
                        source_status=fields[ctx.step_index].source_status,
                        reconstructed=fields[ctx.step_index].source_status == SourceStatus.RECONSTRUCTED,
                    )
                ]
            primary = "Done"
            secondary = ["I'm stuck"]
            has_reconstructed = any(g.reconstructed for g in guidance)
            if has_reconstructed:
                provenance_warning = "Double-check this screen — step wording is reconstructed."
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.ROLLOVER,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                guidance=guidance,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                has_reconstructed_content=has_reconstructed,
                provenance_warning=provenance_warning,
                sla_note=sla_note,
            )

        if ctx.state == JourneyState.INITIATED and playbook:
            esc, fail = collect_triggered_actions(self.knowledge, playbook, ctx.flags)
            na = resolve_next_action(playbook, FunnelStage.ROLLOVER_INITIATED, esc, fail)
            headline = "Rollover initiated"
            body = na.action
            primary = "Track my rollover"
            beekeeper_script = na.action if na.owner == Owner.BEEKEEPER else None
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.TRACK,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                next_beekeeper_script=beekeeper_script,
                sla_note=sla_note,
            )

        if ctx.state == JourneyState.IN_FLIGHT and playbook:
            esc, fail = collect_triggered_actions(self.knowledge, playbook, ctx.flags)
            na = resolve_next_action(playbook, FunnelStage.IN_FLIGHT, esc, fail)
            headline = "Your rollover is in progress"
            body = na.action
            primary = "Mark as complete"
            secondary = ["Nothing arrived yet — get help"]
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.TRACK,
                provider=ctx.provider,
                channel=ctx.channel,
                headline=headline,
                body=body,
                primary_action=primary,
                secondary_actions=secondary,
                edge_cases=edge_cases,
                agent_notes=agent_notes,
                sla_note=sla_note,
            )

        if ctx.state == JourneyState.COMPLETE:
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.TRACK,
                provider=ctx.provider,
                channel=ctx.channel,
                headline="Rollover complete",
                body="Funds are in your PensionBee IRA.",
                primary_action="Done",
            )

        if ctx.state == JourneyState.STUCK:
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=JourneyPhase.ROLLOVER,
                provider=ctx.provider,
                channel=ctx.channel,
                headline="Let's get you unstuck",
                body="A BeeKeeper can walk through this step with you.",
                primary_action="Talk to a BeeKeeper",
                secondary_actions=["Try again"],
                next_beekeeper_script="Route to BeeKeeper for live portal walkthrough.",
            )

        if ctx.state == JourneyState.ESCALATED:
            return JourneyScreen(
                journey_id=ctx.journey_id,
                state=ctx.state,
                phase=phase,
                provider=ctx.provider,
                channel=ctx.channel,
                headline="A BeeKeeper will help",
                body=beekeeper_script or "We've flagged this for a BeeKeeper.",
                primary_action="Continue with BeeKeeper",
                next_beekeeper_script=beekeeper_script,
            )

        return JourneyScreen(
            journey_id=ctx.journey_id,
            state=ctx.state,
            phase=phase,
            provider=ctx.provider,
            channel=ctx.channel,
            headline="Rollover Companion",
            body="",
            primary_action="Continue",
        )


def valid_transitions() -> list[tuple[JourneyState, str, JourneyState]]:
    return [(src, action, dst) for (src, action), dst in TRANSITIONS.items()]
