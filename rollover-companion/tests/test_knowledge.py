import pytest

from engine.knowledge import KnowledgeBase
from engine.models import Mechanism, SourceStatus


@pytest.fixture
def kb() -> KnowledgeBase:
    return KnowledgeBase.from_dir()


def test_loads_all_providers(kb: KnowledgeBase):
    assert set(kb.list_providers()) == {"Empower", "Fidelity", "Vanguard", "Voya"}


def test_alias_resolution(kb: KnowledgeBase):
    assert kb.resolve_provider("NetBenefits") == "Fidelity"
    assert kb.resolve_provider("Great-West") == "Empower"


def test_mechanism_invariants(kb: KnowledgeBase):
    empower = kb.get("Empower")
    assert empower.mechanism == Mechanism.CHECK_TO_PARTICIPANT
    assert empower.forward_step_required is True


def test_access_recovery_loaded(kb: KnowledgeBase):
    fidelity = kb.get("Fidelity")
    assert fidelity.access_recovery.portal_name == "NetBenefits"
    assert fidelity.access_recovery.lockout_fallback.phone


def test_call_script_loaded(kb: KnowledgeBase):
    vanguard = kb.get("Vanguard")
    assert vanguard.call_script.phone
    assert len(vanguard.call_script.rep_questions) >= 1


def test_form_guidance_loaded(kb: KnowledgeBase):
    voya = kb.get("Voya")
    assert len(voya.form_guidance.fields) >= 2


def test_global_tax_escalation(kb: KnowledgeBase):
    assert any(e.flag == "pre_tax_to_roth" for e in kb.global_rules.global_escalations)


def test_every_provider_has_complete_journey_assets(kb: KnowledgeBase):
    for name in kb.list_providers():
        pb = kb.get(name)
        assert pb.access_recovery.reset_steps
        assert pb.call_script.steps
        assert pb.form_guidance.fields
        assert pb.sla_note
        assert len(pb.steps) >= 1
