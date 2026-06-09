"""Build lookup services wired to the DOL 5500 matcher + rollover playbook."""

from __future__ import annotations

import os
from pathlib import Path

from adapters.advizorpro import AdvizorProAdapter
from adapters.matcher5500 import Local5500Adapter
from engine.events import EventLogger
from engine.knowledge import KnowledgeBase
from engine.lookup import LookupService

REPO_ROOT = Path(__file__).resolve().parents[2]


def build_matcher_adapter(repo_root: Path | None = None) -> Local5500Adapter:
    """Return synthetic or real 5500 matcher adapter (USE_SYNTHETIC=1 forces fixtures)."""
    if os.environ.get("USE_SYNTHETIC") == "1":
        return Local5500Adapter.from_synthetic()

    root = repo_root or REPO_ROOT
    matcher_ready, _ = Local5500Adapter.matcher_deps_available()
    if matcher_ready:
        return Local5500Adapter.from_matcher(root)
    return Local5500Adapter.from_synthetic()


def build_lookup_service(
    knowledge: KnowledgeBase | None = None,
    event_logger: EventLogger | None = None,
    *,
    repo_root: Path | None = None,
) -> LookupService:
    """LookupService: DOL 5500 matcher → playbook provider resolution."""
    kb = knowledge or KnowledgeBase.from_dir()
    return LookupService(
        kb,
        build_matcher_adapter(repo_root),
        AdvizorProAdapter(),
        event_logger or EventLogger(),
    )


def build_journey_engine(
    knowledge: KnowledgeBase | None = None,
    event_logger: EventLogger | None = None,
    *,
    repo_root: Path | None = None,
):
    from engine.journey import JourneyEngine

    kb = knowledge or KnowledgeBase.from_dir()
    return JourneyEngine(
        kb,
        build_lookup_service(kb, event_logger, repo_root=repo_root),
        event_logger,
    )
