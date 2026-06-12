from pathlib import Path

import pytest

from engine.knowledge import KnowledgeBase
from engine.models import Mechanism


@pytest.fixture
def kb() -> KnowledgeBase:
    return KnowledgeBase.from_dir()


def test_loads_all_providers(kb: KnowledgeBase):
    assert set(kb.list_providers()) == {
        "Alight Solutions",
        "Empower",
        "Fidelity",
        "Merrill Lynch",
        "Principal",
        "Vanguard",
        "Voya",
    }


def test_alias_resolution(kb: KnowledgeBase):
    assert kb.resolve_provider("NetBenefits") == "Fidelity"
    assert kb.resolve_provider("Great-West") == "Empower"
    assert kb.resolve_provider("ING") == "Voya"
    assert kb.resolve_provider("Alight") == "Alight Solutions"
    assert kb.resolve_provider("Merrill") == "Merrill Lynch"


def test_unknown_provider_raises(kb: KnowledgeBase):
    with pytest.raises(KeyError, match="Unknown provider"):
        kb.get("Schwab")


def test_mechanism_invariants(kb: KnowledgeBase):
    empower = kb.get("Empower")
    assert empower.mechanism == Mechanism.CHECK_TO_PARTICIPANT
    assert empower.forward_step_required is True

    vanguard = kb.get("Vanguard")
    assert vanguard.mechanism == Mechanism.CHECK_TO_PROVIDER
    assert vanguard.forward_step_required is False


def test_global_rules_loaded(kb: KnowledgeBase):
    rules = kb.global_rules
    assert "pre-tax" in rules.tax_routing.pre_tax.lower() or "Pre-tax" in rules.tax_routing.pre_tax
    assert any(e.flag == "pre_tax_to_roth" for e in rules.global_escalations)


def test_all_stages_have_next_actions(kb: KnowledgeBase):
    for name in kb.list_providers():
        playbook = kb.get(name)
        assert len(playbook.next_actions) == 4
