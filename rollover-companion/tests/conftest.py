from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.advizorpro import AdvizorProAdapter  # noqa: E402
from adapters.matcher5500 import Local5500Adapter  # noqa: E402
from engine.events import EventLogger  # noqa: E402
from engine.journey import JourneyEngine  # noqa: E402
from engine.knowledge import KnowledgeBase  # noqa: E402
from engine.lookup import LookupService  # noqa: E402


@pytest.fixture
def tmp_logs(tmp_path):
    return EventLogger(
        journey_path=tmp_path / "journey.jsonl",
        comparison_path=tmp_path / "comparison.jsonl",
    )


@pytest.fixture
def knowledge():
    return KnowledgeBase.from_dir()


@pytest.fixture
def lookup_service(knowledge, tmp_logs):
    return LookupService(
        knowledge,
        Local5500Adapter.from_synthetic(),
        AdvizorProAdapter(),
        tmp_logs,
    )


@pytest.fixture
def engine(knowledge, lookup_service, tmp_logs):
    return JourneyEngine(knowledge, lookup_service, tmp_logs)
