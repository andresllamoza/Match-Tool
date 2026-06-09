from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from .customer_copy import customer_next_copy
from .models import NextStepResult


class KnowledgeBridge:
    """Reads the rollover companion knowledge layer for customer-facing next steps."""

    def __init__(self, engine):
        self._engine = engine

    @classmethod
    def from_dir(cls, knowledge_dir: Path | None = None) -> KnowledgeBridge:
        repo_root = Path(__file__).resolve().parents[2]
        companion_root = repo_root / "rollover-companion"
        if not companion_root.exists():
            companion_root = repo_root / "rollover-playbook-engine"
        if str(companion_root) not in sys.path:
            sys.path.insert(0, str(companion_root))
        from engine.knowledge import KnowledgeBase  # noqa: WPS433
        from engine.models import FunnelStage  # noqa: WPS433

        kb = KnowledgeBase.from_dir(
            companion_root / "rollover-knowledge-layer"
            if (companion_root / "rollover-knowledge-layer").exists()
            else None
        )
        bridge = cls(kb)
        bridge._FunnelStage = FunnelStage  # type: ignore[attr-defined]
        return bridge

    def next_step_for_provider(self, provider: str) -> Optional[NextStepResult]:
        if not provider:
            return None
        FunnelStage = self._FunnelStage  # noqa: N806
        try:
            playbook = self._engine.get(provider)
        except KeyError:
            return None
        na = playbook.next_actions[FunnelStage.PROVIDER_IDENTIFIED]
        return NextStepResult(
            action=customer_next_copy(
                customer_message=getattr(na, "customer_message", None),
                action=na.action,
            ),
            owner=na.owner.value,
            source_status=na.source_status.value,
            provenance_warning=None,
        )
