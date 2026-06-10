"""Boot JourneyEngine for the Streamlit sandbox (synthetic lookups — no DOL cache)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.journey import JourneyEngine  # noqa: E402
from engine.knowledge import KnowledgeBase  # noqa: E402
from engine.lookup import LookupService  # noqa: E402


def _build_engine() -> JourneyEngine:
    from adapters.advizorpro import AdvizorProAdapter
    from adapters.matcher5500 import Local5500Adapter

    knowledge = KnowledgeBase.from_dir(ROOT / "rollover-knowledge-layer")
    matcher = Local5500Adapter.from_synthetic()
    lookup = LookupService(knowledge, matcher, AdvizorProAdapter())
    return JourneyEngine(knowledge=knowledge, lookup_service=lookup)


@st.cache_resource
def get_engine() -> JourneyEngine:
    return _build_engine()


def list_providers() -> list[str]:
    return get_engine().knowledge.list_providers()
