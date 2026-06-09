from engine import FunnelStage, RolloverEngine
from engine.knowledge import KnowledgeBase


def test_general_guide_loaded():
    kb = KnowledgeBase.from_dir()
    g = kb.general_guide
    assert g.destination_name == "PensionBee"
    assert "PO Box 72" in g.mailing_address
    assert len(g.general_steps) >= 7


def test_fin_escalations_merged():
    kb = KnowledgeBase.from_dir()
    flags = {e.flag for e in kb.global_rules.global_escalations}
    assert "account_number_request" in flags
    assert "portal_navigation_stuck" in flags
    assert "pre_tax_to_roth" in flags


def test_vanguard_no_provenance_warning():
    eng = RolloverEngine()
    resp = eng.recommend("Vanguard", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.provenance_warning is None
    assert resp.general_guide is not None
    assert len(resp.general_steps) > 0


def test_sla_uses_general_timeline():
    eng = RolloverEngine()
    resp = eng.recommend("Vanguard", FunnelStage.PROVIDER_IDENTIFIED)
    assert "2" in (resp.sla_note or "") or "week" in (resp.sla_note or "").lower()
