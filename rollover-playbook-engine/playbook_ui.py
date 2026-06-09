"""Presentation helpers for the Streamlit playbook explorer (testable without Streamlit)."""

from __future__ import annotations

from engine.knowledge import KnowledgeBase
from engine.models import FunnelStage, Owner, RecommendationResponse, SourceStatus

STAGE_LABELS = {
    FunnelStage.PROVIDER_IDENTIFIED: "Provider identified",
    FunnelStage.ROLLOVER_INITIATED: "Rollover initiated",
    FunnelStage.IN_FLIGHT: "In flight",
    FunnelStage.COMPLETED: "Completed",
}

OWNER_LABELS = {
    Owner.USER: "User",
    Owner.BEEKEEPER: "BeeKeeper",
    Owner.SYSTEM: "System",
}


def flag_options_for_provider(kb: KnowledgeBase, provider: str) -> list[tuple[str, str]]:
    """Return (flag, label) pairs for multiselect — global flags plus provider-specific."""
    options: list[tuple[str, str]] = []
    for entry in kb.available_flags(provider):
        prefix = "Global" if entry["scope"] == "global" else entry["provider"]
        kind = "escalation" if entry["kind"] == "escalation" else "failure"
        label = f"[{prefix} · {kind}] {entry['flag']}"
        options.append((entry["flag"], label))
    return options


def owner_badge(owner: Owner) -> str:
    return OWNER_LABELS.get(owner, owner.value)


def source_badge(status: SourceStatus) -> str:
    return "Verified" if status == SourceStatus.VERIFIED else "Reconstructed"


def summary_lines(resp: RecommendationResponse) -> list[str]:
    lines = [
        f"**Mechanism:** {resp.mechanism.value.replace('_', ' ')}",
        f"**Check destination:** {resp.check_destination}",
        f"**Forward step required:** {'Yes' if resp.forward_step_required else 'No'}",
        f"**Preferred path:** {resp.preferred_path}",
    ]
    if resp.sla_gap:
        lines.append(f"**SLA:** not quantified — {resp.sla_note}")
    elif resp.sla_days is not None:
        lines.append(f"**SLA:** {resp.sla_days} days")
    return lines
