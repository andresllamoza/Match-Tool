from __future__ import annotations

from pathlib import Path
from typing import Optional

from .knowledge import KnowledgeBase
from .models import (
    FunnelStage,
    NextAction,
    Owner,
    RecommendationResponse,
    SourceStatus,
    TriggeredAction,
)
from .invocation_log import log_invocation


class RolloverEngine:
    def __init__(self, knowledge: KnowledgeBase | None = None):
        self.knowledge = knowledge or KnowledgeBase.from_dir()

    def recommend(
        self,
        provider: str,
        funnel_stage: FunnelStage,
        flags: Optional[dict[str, bool]] = None,
    ) -> RecommendationResponse:
        flags = flags or {}
        playbook = self.knowledge.get(provider)
        global_rules = self.knowledge.global_rules

        active_escalations: list[TriggeredAction] = []
        active_failures: list[TriggeredAction] = []

        for esc in global_rules.global_escalations:
            if flags.get(esc.flag):
                active_escalations.append(
                    TriggeredAction(
                        id=esc.id,
                        flag=esc.flag,
                        action=esc.action,
                        owner=esc.owner,
                        source_status=esc.source_status,
                        scope="global",
                    )
                )
        for esc in playbook.escalation_triggers:
            if flags.get(esc.flag):
                active_escalations.append(
                    TriggeredAction(
                        id=esc.id,
                        flag=esc.flag,
                        action=esc.action,
                        owner=esc.owner,
                        source_status=esc.source_status,
                        scope="provider",
                    )
                )

        for fail in global_rules.global_failure_modes:
            if flags.get(fail.flag):
                active_failures.append(
                    TriggeredAction(
                        id=fail.id,
                        flag=fail.flag,
                        action=fail.routing_action,
                        owner=fail.owner,
                        source_status=fail.source_status,
                        scope="global",
                    )
                )
        for fail in playbook.failure_modes:
            if flags.get(fail.flag):
                active_failures.append(
                    TriggeredAction(
                        id=fail.id,
                        flag=fail.flag,
                        action=fail.routing_action,
                        owner=fail.owner,
                        source_status=fail.source_status,
                        scope="provider",
                    )
                )

        if active_escalations:
            top = active_escalations[0]
            next_action = NextAction(
                action=top.action,
                owner=top.owner,
                source_status=top.source_status,
            )
        elif active_failures:
            top = active_failures[0]
            next_action = NextAction(
                action=top.action,
                owner=top.owner,
                source_status=top.source_status,
            )
        else:
            next_action = playbook.next_actions[funnel_stage]

        has_reconstructed = any(
            s.source_status == SourceStatus.RECONSTRUCTED for s in playbook.steps
        ) or next_action.source_status == SourceStatus.RECONSTRUCTED

        provenance_warning = None
        if has_reconstructed:
            provenance_warning = (
                "Some portal step wording is reconstructed — spot-check against the live Scribe."
            )

        response = RecommendationResponse(
            provider=playbook.provider,
            funnel_stage=funnel_stage,
            next_action=next_action,
            preferred_path=playbook.preferred_path,
            mechanism=playbook.mechanism,
            check_destination=playbook.check_destination,
            forward_step_required=playbook.forward_step_required,
            tax_routing_note=playbook.tax_routing_note,
            sla_days=playbook.sla_days,
            sla_note=playbook.sla_note,
            sla_gap=playbook.sla_days is None,
            steps=playbook.steps,
            edge_cases=playbook.edge_cases,
            active_escalations=active_escalations,
            active_failure_modes=active_failures,
            has_reconstructed_content=has_reconstructed,
            provenance_warning=provenance_warning,
        )

        path_taken = "escalation" if active_escalations else ("failure" if active_failures else "stage")
        log_invocation(
            provider=playbook.provider,
            funnel_stage=funnel_stage.value,
            path_taken=path_taken,
            outcome=next_action.action,
        )
        return response
