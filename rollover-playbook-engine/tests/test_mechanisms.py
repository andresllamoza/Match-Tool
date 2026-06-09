from engine import FunnelStage, RolloverEngine
from engine.models import Mechanism


def test_fidelity_two_hop_acat():
    eng = RolloverEngine()
    resp = eng.recommend("Fidelity", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.mechanism == Mechanism.TWO_HOP_ACAT
    assert "ACAT" in resp.check_destination or "No check" in resp.check_destination


def test_empower_check_to_participant():
    eng = RolloverEngine()
    resp = eng.recommend("Empower", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.mechanism == Mechanism.CHECK_TO_PARTICIPANT
    assert resp.forward_step_required is True


def test_vanguard_check_to_provider():
    eng = RolloverEngine()
    resp = eng.recommend("Vanguard", FunnelStage.PROVIDER_IDENTIFIED)
    assert resp.mechanism == Mechanism.CHECK_TO_PROVIDER
    assert resp.forward_step_required is False


def test_fidelity_avenue3_unavailable_fallback():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Fidelity",
        FunnelStage.PROVIDER_IDENTIFIED,
        flags={"avenue3_unavailable": True},
    )
    assert resp.active_failure_modes[0].flag == "avenue3_unavailable"
    assert "phone" in resp.next_action.action.lower() or "participant" in resp.next_action.action.lower()


def test_automation_credential_global_failure():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Vanguard",
        FunnelStage.PROVIDER_IDENTIFIED,
        flags={"automation_credential_fail": True},
    )
    assert resp.active_failure_modes[0].scope == "global"
    assert "BeeKeeper" in resp.next_action.action or resp.next_action.owner.value == "beekeeper"


def test_empower_check_confusion_failure():
    eng = RolloverEngine()
    resp = eng.recommend(
        "Empower",
        FunnelStage.ROLLOVER_INITIATED,
        flags={"check_to_user_confusion": True},
    )
    assert "envelope" in resp.next_action.action.lower() or "forward" in resp.next_action.action.lower()
