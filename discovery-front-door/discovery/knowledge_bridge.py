from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from .models import NextStepResult


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
        if str(playbook_root) not in sys.path:
            sys.path.insert(0, str(playbook_root))
        from engine import FunnelStage, RolloverEngine  # noqa: WPS433

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
