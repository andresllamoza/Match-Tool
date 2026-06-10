"""API regression: every journey action a user/agent button can trigger."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.server import app

client = TestClient(app)


def _start(agent: bool = False) -> str:
    r = client.post(f"/api/journey/start?agent={agent}")
    assert r.status_code == 200
    return r.json()["context"]["journey_id"]


def _act(jid: str, body: dict, *, agent: bool = False):
    r = client.post(f"/api/journey/{jid}/action?agent={agent}", json=body)
    return r


def test_find_lookup_and_provider_picker_paths():
    jid = _start()
    r = _act(jid, {"type": "lookup", "employer": "Target"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "provider_identified"

    jid2 = _start()
    r2 = _act(jid2, {"type": "provider_direct", "provider": "Fidelity"})
    assert r2.status_code == 200
    assert r2.json()["screen"]["state"] == "provider_identified"


def test_access_channel_stuck_and_track_buttons():
    jid = _start()
    _act(jid, {"type": "provider_direct", "provider": "Fidelity"})
    r = _act(jid, {"type": "access", "can_login": True})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "access_recovered"

    r = _act(jid, {"type": "tax_type", "tax_type": "pre_tax"})
    assert r.status_code == 200

    r = _act(jid, {"type": "channel", "channel": "online"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "online_in_progress"

    while r.json()["screen"]["state"] == "online_in_progress":
        r = _act(jid, {"type": "step", "outcome": "done"})
        assert r.status_code == 200

    r = _act(jid, {"type": "confirm_in_flight"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "in_flight"

    r = _act(jid, {"type": "mark_complete"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "complete"


def test_stuck_resume_and_escalate_buttons():
    jid = _start()
    _act(jid, {"type": "provider_direct", "provider": "Voya"})
    _act(jid, {"type": "access", "can_login": True})
    _act(jid, {"type": "tax_type", "tax_type": "pre_tax"})
    _act(jid, {"type": "channel", "channel": "online"})
    r = _act(jid, {"type": "step", "outcome": "stuck"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "stuck"

    r = _act(jid, {"type": "resume"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "online_in_progress"

    r = _act(jid, {"type": "step", "outcome": "stuck"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "escalated"


def test_handoff_and_access_blocked_buttons():
    jid = _start()
    _act(jid, {"type": "lookup", "employer": "Uncovered Demo Corp"})
    r = _act(jid, {"type": "handoff", "reason": "provider_not_covered"})
    assert r.status_code == 200
    assert r.json()["screen"]["state"] == "escalated"

    jid2 = _start()
    _act(jid2, {"type": "provider_direct", "provider": "Fidelity"})
    r2 = _act(jid2, {"type": "access", "can_login": False})
    assert r2.status_code == 200
    assert r2.json()["screen"]["state"] == "access_blocked"

    r3 = _act(jid2, {"type": "access_recovered"})
    assert r3.status_code == 200
    assert r3.json()["screen"]["state"] == "access_recovered"


def test_agent_intel_on_lookup():
    jid = _start(agent=True)
    r = _act(jid, {"type": "lookup", "employer": "Walmart"}, agent=True)
    assert r.status_code == 200
    intel = r.json()["provider_intel"]
    assert intel.get("provider_status")
    assert "escalation_triggers" in intel
