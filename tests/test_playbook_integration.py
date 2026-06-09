"""5500 matcher ↔ rollover playbook integration tests."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_ROOT = REPO_ROOT / "discovery-front-door"
COMPANION_ROOT = REPO_ROOT / "rollover-companion"
PLAYBOOK_ROOT = REPO_ROOT / "rollover-playbook-engine"


class PlaybookIntegrationTest(unittest.TestCase):
    def test_provider_hint_feeds_knowledge_bridge(self):
        if str(DISCOVERY_ROOT) not in sys.path:
            sys.path.insert(0, str(DISCOVERY_ROOT))

        from discovery.knowledge_bridge import KnowledgeBridge
        from src.provider_equiv import normalize_for_playbook

        bridge = KnowledgeBridge.from_dir(REPO_ROOT / "discovery-front-door")
        dol_label = "Fidelity Workplace Services, LLC"
        provider = normalize_for_playbook(dol_label)
        step = bridge.next_step_for_provider(provider)
        self.assertIsNotNone(step)
        self.assertIn("Fidelity", step.action)

    def test_discovery_build_adapters_synthetic(self):
        if str(DISCOVERY_ROOT) not in sys.path:
            sys.path.insert(0, str(DISCOVERY_ROOT))

        from discovery.synthetic import build_adapters

        prev = os.environ.get("USE_SYNTHETIC")
        os.environ["USE_SYNTHETIC"] = "1"
        try:
            adv, matcher = build_adapters(REPO_ROOT)
            result = matcher.lookup("Amazon.com Services LLC")
            self.assertEqual(result.provider, "Fidelity")
            self.assertIsNotNone(adv)
        finally:
            if prev is None:
                os.environ.pop("USE_SYNTHETIC", None)
            else:
                os.environ["USE_SYNTHETIC"] = prev

    def test_companion_factory_synthetic(self):
        if str(COMPANION_ROOT) not in sys.path:
            sys.path.insert(0, str(COMPANION_ROOT))

        from adapters.factory import build_lookup_service
        from engine.knowledge import KnowledgeBase
        from engine.models import ConfidenceTier

        prev = os.environ.get("USE_SYNTHETIC")
        os.environ["USE_SYNTHETIC"] = "1"
        try:
            knowledge = KnowledgeBase.from_dir()
            service = build_lookup_service(knowledge)
            outcome = service.lookup("Nike Inc")
            self.assertEqual(outcome.resolved_provider, "Fidelity")
            self.assertEqual(outcome.confidence_tier, ConfidenceTier.HIGH)
        finally:
            if prev is None:
                os.environ.pop("USE_SYNTHETIC", None)
            else:
                os.environ["USE_SYNTHETIC"] = prev


if __name__ == "__main__":
    unittest.main()
