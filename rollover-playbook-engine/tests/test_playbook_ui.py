from engine import FunnelStage, RolloverEngine
from engine.knowledge import KnowledgeBase
from playbook_ui import flag_options_for_provider, owner_badge, summary_lines


def test_available_flags_includes_global_and_provider():
    kb = KnowledgeBase.from_dir()
    fidelity_flags = {f["flag"] for f in kb.available_flags("Fidelity")}
    assert "pre_tax_to_roth" in fidelity_flags
    assert "avenue3_unavailable" in fidelity_flags

    empower_flags = {f["flag"] for f in kb.available_flags("Empower")}
    assert "notary_required" in empower_flags


def test_flag_options_for_provider():
    kb = KnowledgeBase.from_dir()
    opts = flag_options_for_provider(kb, "Voya")
    flags = [f for f, _ in opts]
    assert "phone_verify_required" in flags
    assert "pre_tax_to_roth" in flags


def test_summary_lines_surfaces_sla_gap():
    eng = RolloverEngine()
    resp = eng.recommend("Vanguard", FunnelStage.PROVIDER_IDENTIFIED)
    text = " ".join(summary_lines(resp))
    assert "not quantified" in text.lower()


def test_owner_badge():
    from engine.models import Owner

    assert owner_badge(Owner.BEEKEEPER) == "BeeKeeper"
