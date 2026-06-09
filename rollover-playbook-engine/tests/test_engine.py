from engine import FunnelStage, RolloverEngine
from engine.models import Owner, SourceStatus


def test_fidelity_provider_identified_default():
    eng = RolloverEngine()
    resp = eng.recommend("Fidelity", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.provider == "Fidelity"
    assert resp.next_action.owner == Owner.USER
    assert "Express rollover" in resp.next_action.action
    assert resp.forward_step_required is False


def test_empower_notary_escalation_preempts():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Empower",
        FunnelStage.PROVIDER_IDENTIFIED,
        flags={"notary_required": True},
    )
    assert resp.active_escalations
    assert resp.active_escalations[0].flag == "notary_required"
    assert resp.next_action.owner == Owner.BEEKEEPER
    assert "notary" in resp.next_action.action.lower()


def test_voya_phone_verify_failure_mode():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Voya",
        FunnelStage.ROLLOVER_INITIATED,
        flags={"phone_verify_required": True},
    )
    assert resp.active_failure_modes
    assert resp.active_failure_modes[0].flag == "phone_verify_required"
    assert "call Voya" in resp.next_action.action


def test_global_pre_tax_to_roth_escalation():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Vanguard",
        FunnelStage.PROVIDER_IDENTIFIED,
        flags={"pre_tax_to_roth": True},
    )
    assert resp.active_escalations[0].scope == "global"
    assert resp.next_action.owner == Owner.BEEKEEPER


def test_sla_gap_surfaced():
    eng = RolloverEngine()
    resp = eng.recommend("Vanguard", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.sla_gap is True
    assert resp.sla_note is not None


def test_provenance_flagged_for_reconstructed():
    eng = RolloverEngine()
    resp = eng.recommend("Fidelity", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.has_reconstructed_content is True
    assert resp.provenance_warning is not None


def test_completed_stage_system_owned():
    eng = RolloverEngine()
    resp = eng.recommend("Fidelity", FunnelStage.COMPLETED)
    assert resp.next_action.owner == Owner.SYSTEM
