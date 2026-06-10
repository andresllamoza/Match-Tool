import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["PB_SESSION_DB"] = str(Path(tempfile.gettempdir()) / "pb_test_sessions.db")

from api.persistence import COOKIE_NAME, init_db, load_context  # noqa: E402
from api.server import app  # noqa: E402

init_db()
client = TestClient(app)


def test_customer_page_renders():
    r = client.get("/customer?fresh=1")
    assert r.status_code == 200
    assert "PensionBee" in r.text
    assert "htmx.org" in r.text
    assert COOKIE_NAME in r.cookies


def test_session_cookie_persists_across_refresh():
    r1 = client.get("/customer?fresh=1")
    jid = r1.cookies[COOKIE_NAME]
    client.post(
        "/htmx/journey/action",
        data={
            "journey_id": jid,
            "type": "provider_direct",
            "provider": "Fidelity Investments",
            "surface": "customer",
        },
    )
    ctx = load_context(jid)
    assert ctx is not None
    assert ctx.provider and "Fidelity" in ctx.provider

    r2 = client.get("/customer", cookies={COOKIE_NAME: jid})
    assert r2.status_code == 200
    assert "Welcome back" in r2.text
    assert "Fidelity" in r2.text


def test_htmx_action_returns_step_fragment():
    start = client.post("/api/journey/start").json()
    jid = start["context"]["journey_id"]
    client.post(
        f"/api/journey/{jid}/action",
        json={"type": "provider_direct", "provider": "Fidelity Investments"},
    )
    client.post(
        f"/api/journey/{jid}/action",
        json={"type": "access", "can_login": True},
    )
    client.post(
        f"/api/journey/{jid}/action",
        json={"type": "tax_type", "tax_type": "pre_tax"},
    )
    client.post(
        f"/api/journey/{jid}/action",
        json={"type": "channel", "channel": "online"},
    )
    r = client.post(
        "/htmx/journey/action",
        data={
            "journey_id": jid,
            "type": "step",
            "outcome": "done",
            "surface": "customer",
        },
    )
    assert r.status_code == 200
    assert 'id="journey-step-customer"' in r.text


def test_fbo_routing_card_on_payable_step():
    start = client.post("/api/journey/start").json()
    jid = start["context"]["journey_id"]
    for body in (
        {"type": "provider_direct", "provider": "Vanguard"},
        {"type": "access", "can_login": True},
        {"type": "tax_type", "tax_type": "pre_tax"},
        {"type": "channel", "channel": "online"},
    ):
        client.post(f"/api/journey/{jid}/action", json=body)

    r = client.post(
        "/htmx/journey/action",
        data={
            "journey_id": jid,
            "type": "step",
            "outcome": "done",
            "surface": "customer",
        },
    )
    html = r.text

    assert "PensionBee FBO" in html
    assert "Critical — check payable to" in html
    assert "data-copy=" in html


def test_sandbox_page_three_columns():
    r = client.get("/sandbox?fresh=1")
    assert r.status_code == 200
    assert "Customer flow" in r.text
    assert "Agent mirror" in r.text
    assert "Embed mode" in r.text
