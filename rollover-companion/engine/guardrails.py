from __future__ import annotations

from .knowledge import KnowledgeBase
from .models import (
    FunnelStage,
    NextAction,
    Owner,
    ProviderPlaybook,
    SourceStatus,
    TriggeredAction,
)


def collect_triggered_actions(
    knowledge: KnowledgeBase,
    playbook: ProviderPlaybook,
    flags: dict[str, bool],
) -> tuple[list[TriggeredAction], list[TriggeredAction]]:
    active_escalations: list[TriggeredAction] = []
    active_failures: list[TriggeredAction] = []

    for esc in knowledge.global_rules.global_escalations:
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

    for fail in knowledge.global_rules.global_failure_modes:
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

    return active_escalations, active_failures


def resolve_next_action(
    playbook: ProviderPlaybook,
    funnel_stage: FunnelStage,
    active_escalations: list[TriggeredAction],
    active_failures: list[TriggeredAction],
) -> NextAction:
    if active_escalations:
        top = active_escalations[0]
        return NextAction(action=top.action, owner=top.owner, source_status=top.source_status)
    if active_failures:
        top = active_failures[0]
        return NextAction(action=top.action, owner=top.owner, source_status=top.source_status)
    return playbook.next_actions[funnel_stage]


def check_tax_routing_escalation(flags: dict[str, bool]) -> bool:
    return bool(flags.get("pre_tax_to_roth"))
