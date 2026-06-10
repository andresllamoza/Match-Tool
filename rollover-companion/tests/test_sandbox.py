"""Streamlit sandbox — persistence + mechanism-aware routing (no browser)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["PB_SESSION_DB"] = str(Path(tempfile.gettempdir()) / "pb_sandbox_test.db")

from api.journey_dispatch import dispatch_action  # noqa: E402
from api.persistence import init_db, load_context, save_context  # noqa: E402
from engine.customer_copy import is_fbo_payable_line  # noqa: E402
from engine.enrichment import build_enrichment  # noqa: E402
from sandbox.boot import get_engine  # noqa: E402

init_db()


def _advance_to_phone(ctx, provider: str):
    engine = get_engine()
    dispatch_action(ctx, {"type": "provider_direct", "provider": provider})
    dispatch_action(ctx, {"type": "access", "can_login": True})
    ctx.customer_first_name = "Avery"
    ctx.customer_last_name = "Quinn"
    save_context(ctx)
    dispatch_action(ctx, {"type": "tax_type", "tax_type": "pre_tax"})
    dispatch_action(ctx, {"type": "channel", "channel": "phone"})
    return engine.render(ctx), build_enrichment(engine.knowledge, ctx, engine.render(ctx))


def test_sqlite_rehydrate_after_ram_purge():
    """Simulate Streamlit rerun: only URL jid + SQLite survive."""
    engine = get_engine()
    ctx = engine.start()
    dispatch_action(ctx, {"type": "provider_direct", "provider": "Voya"})
    jid = ctx.journey_id
    save_context(ctx)

    restored = load_context(jid)
    assert restored is not None
    assert restored.journey_id == jid
    assert restored.provider == "Voya"

    dispatch_action(restored, {"type": "access", "can_login": True})
    save_context(restored)
    again = load_context(jid)
    assert again.state.value == "access_recovered"


def test_voya_phone_fbo_routing_with_dynamic_name():
    engine = get_engine()
    ctx = engine.start()
    screen, enrichment = _advance_to_phone(ctx, "Voya")
    payable = enrichment.channel_context.check_payable if enrichment.channel_context else ""
    assert payable == "PensionBee FBO Avery Quinn"
    assert is_fbo_payable_line(payable)
    mail = enrichment.channel_context.mailing_address if enrichment.channel_context else ""
    assert "PO Box 72" in mail
    assert screen.state.value == "phone_in_progress"


def test_empower_participant_payee_not_fbo():
    engine = get_engine()
    ctx = engine.start()
    _, enrichment = _advance_to_phone(ctx, "Empower")
    payable = enrichment.channel_context.check_payable if enrichment.channel_context else ""
    assert payable
    assert not is_fbo_payable_line(payable)
    assert "participant" in payable.lower() or "Participant" in payable


def test_sandbox_modules_import():
    from sandbox import state  # noqa: F401
    from sandbox.ui import channel  # noqa: F401

    assert channel.routing_security_card("PensionBee FBO Test", "PO Box 72")
    assert "Critical" in channel.routing_security_card("PensionBee FBO Test", "PO Box 72")
