"""Sandbox guardrails: SQLite write-through + FBO payee invariants."""

from __future__ import annotations

from engine.enrichment import build_enrichment
from engine.models import JourneyChannel, JourneyState
from sandbox.persistence import SessionStore


def _store(tmp_path):
    return SessionStore(tmp_path / "rollover_sessions.db")


def test_every_transition_survives_hard_refresh(engine, tmp_path):
    store = _store(tmp_path)
    ctx = engine.start()
    store.save(ctx)

    engine.set_provider_direct(ctx, "Empower")
    store.save(ctx)
    engine.submit_access(ctx, can_login=True)
    store.save(ctx)
    engine.submit_tax_type(ctx, "pre_tax")
    store.save(ctx)
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    store.save(ctx)

    restored = store.load(ctx.journey_id)
    assert restored is not None
    assert restored.state == JourneyState.PHONE_IN_PROGRESS
    assert restored.provider == ctx.provider
    assert restored.tax_fund_type == "pre_tax"
    assert restored.channel == JourneyChannel.PHONE

    engine.advance_step(restored, "done")
    store.save(restored)
    again = store.load(ctx.journey_id)
    assert again.step_index == restored.step_index


def _phone_enrichment(engine, provider):
    ctx = engine.start()
    engine.set_provider_direct(ctx, provider)
    engine.submit_access(ctx, can_login=True)
    ctx.customer_first_name, ctx.customer_last_name = "Avery", "Quinn"
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    return build_enrichment(engine.knowledge, ctx, engine.render(ctx))


ALL_PROVIDERS = [
    "Fidelity",
    "Empower",
    "Vanguard",
    "Voya",
    "Alight Solutions",
    "Merrill Lynch",
    "Principal",
]


def test_payee_is_always_fbo_never_participant(engine):
    from engine.customer_copy import is_fbo_payable_line

    for provider in ALL_PROVIDERS:
        enr = _phone_enrichment(engine, provider)
        payable = (enr.channel_context and enr.channel_context.check_payable) or ""
        assert payable == "PensionBee FBO Avery Quinn", provider
        assert is_fbo_payable_line(payable), provider
        assert "participant" not in payable.lower(), provider


def test_mailing_destination_varies_by_mechanism(engine):
    empower = _phone_enrichment(engine, "Empower")
    assert "address on file" in (empower.channel_context.mailing_address or "").lower()
    for provider in ("Voya", "Vanguard"):
        enr = _phone_enrichment(engine, provider)
        assert "PO Box 72" in (enr.channel_context.mailing_address or ""), provider


def test_resume_list_is_newest_first(engine, tmp_path):
    store = _store(tmp_path)
    a = engine.start()
    store.save(a)
    b = engine.start()
    store.save(b)
    rows = store.recent()
    assert rows[0]["journey_id"] == b.journey_id
    assert {r["journey_id"] for r in rows} >= {a.journey_id, b.journey_id}
