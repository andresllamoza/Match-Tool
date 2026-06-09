import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.server import app  # noqa: E402

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_journey_lifecycle():
    start = client.post("/api/journey/start").json()
    jid = start["context"]["journey_id"]
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "provider_direct", "provider": "Fidelity"},
    ).json()
    assert r["screen"]["state"] == "provider_identified"
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "access", "can_login": True},
    ).json()
    assert r["screen"]["state"] == "access_recovered"
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "tax_type", "tax_type": "pre_tax"},
    ).json()
    assert r["context"]["tax_fund_type"] == "pre_tax"
    assert "enrichment" in r


def test_assistant_endpoint():
    start = client.post("/api/journey/start").json()
    jid = start["context"]["journey_id"]
    client.post(
        f"/api/journey/{jid}/action",
        json={"type": "provider_direct", "provider": "Vanguard"},
    )
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "ask", "question": "what is the weather"},
    ).json()
    assert r["assistant"]["in_scope"] is False


def test_funnel_endpoint():
    assert "by_state" in client.get("/api/funnel").json()


def test_provider_not_covered_handoff():
    start = client.post("/api/journey/start").json()
    jid = start["context"]["journey_id"]
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "lookup", "employer": "Walmart"},
    ).json()
    assert r["screen"]["state"] == "provider_not_covered"
    assert r["context"]["uncovered_provider"] == "Merrill Lynch"
    r = client.post(
        f"/api/journey/{jid}/action",
        json={"type": "handoff", "reason": "provider_not_covered"},
    ).json()
    assert r["screen"]["state"] == "escalated"
