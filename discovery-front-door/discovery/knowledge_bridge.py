from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from .models import NextStepResult


def _import_playbook_engine(playbook_root: Path):
    """Import rollover-playbook-engine even when sibling `engine` packages exist."""
    playbook_root = playbook_root.resolve()
    for name in list(sys.modules):
        if name != "engine" and not name.startswith("engine."):
            continue
        module_file = getattr(sys.modules[name], "__file__", "") or ""
        if module_file and str(playbook_root) not in module_file:
            del sys.modules[name]

    playbook_path = str(playbook_root)
    if playbook_path in sys.path:
        sys.path.remove(playbook_path)
    sys.path.insert(0, playbook_path)
    from engine import FunnelStage, RolloverEngine  # noqa: WPS433

    return FunnelStage, RolloverEngine


class KnowledgeBridge:
    """Reads the rollover playbook knowledge layer for next-step guidance."""

    def __init__(self, engine):
        self._engine = engine

    @classmethod
    def from_dir(cls, knowledge_dir: Path | None = None) -> KnowledgeBridge:
        repo_root = Path(__file__).resolve().parents[2]
        playbook_root = (knowledge_dir or repo_root) / "rollover-playbook-engine"
        if knowledge_dir and not playbook_root.exists():
            playbook_root = repo_root / "rollover-playbook-engine"
        FunnelStage, RolloverEngine = _import_playbook_engine(playbook_root)
        eng = RolloverEngine()
        bridge = cls(eng)
        bridge._FunnelStage = FunnelStage  # type: ignore[attr-defined]
        return bridge

    def next_step_for_provider(self, provider: str) -> Optional[NextStepResult]:
        if not provider:
            return None
        FunnelStage = self._FunnelStage  # noqa: N806
        try:
            resp = self._engine.recommend(provider, FunnelStage.PROVIDER_IDENTIFIED)
        except KeyError:
            return None
        return NextStepResult(
            action=resp.next_action.action,
            owner=resp.next_action.owner.value,
            source_status=resp.next_action.source_status.value,
            provenance_warning=resp.provenance_warning,
        )
