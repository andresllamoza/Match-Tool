"""Employer search state must update on the first submit — no URL or stale value fights."""

from app import (
    EMPLOYER_SEARCH_INPUT_KEY,
    SEARCH_BUILD_ID,
    apply_lookup_submission,
    has_legacy_employer_url_param,
    migrate_stale_search_session,
)


def test_first_submit_sets_confirmed_lookup():
    state: dict[str, object] = {}
    result = apply_lookup_submission(True, "  Disney  ", state)
    assert result == "Disney"
    assert state["confirmed_lookup"] == "Disney"
    assert state[EMPLOYER_SEARCH_INPUT_KEY] == "Disney"


def test_second_submit_replaces_previous_employer():
    state: dict[str, object] = {
        "confirmed_lookup": "Target",
        EMPLOYER_SEARCH_INPUT_KEY: "Target",
    }
    result = apply_lookup_submission(True, "Amazon", state)
    assert result == "Amazon"
    assert state["confirmed_lookup"] == "Amazon"
    assert state[EMPLOYER_SEARCH_INPUT_KEY] == "Amazon"


def test_no_submit_keeps_previous_lookup():
    state: dict[str, object] = {
        "confirmed_lookup": "Target",
        EMPLOYER_SEARCH_INPUT_KEY: "Target",
    }
    result = apply_lookup_submission(False, "Disney", state)
    assert result == "Target"
    assert state["confirmed_lookup"] == "Target"


def test_empty_submit_is_ignored():
    state: dict[str, object] = {"confirmed_lookup": "Target", EMPLOYER_SEARCH_INPUT_KEY: "Target"}
    result = apply_lookup_submission(True, "   ", state)
    assert result == "Target"
    assert state["confirmed_lookup"] == "Target"


def test_migrate_stale_search_session_clears_legacy_keys():
    state: dict[str, object] = {
        "_synced_param_lookup": ("param", "Target"),
        "_url_employer_seeded": True,
        "_pending_search_query": "Target",
        "confirmed_lookup": "Target",
    }

    class FakeSessionState(dict):
        def pop(self, key, default=None):
            return super().pop(key, default)

    fake_state = FakeSessionState(state)
    import app as app_module

    original = app_module.st.session_state
    app_module.st.session_state = fake_state
    try:
        migrate_stale_search_session()
        assert fake_state["_search_session_migrated"] == SEARCH_BUILD_ID
        assert "_synced_param_lookup" not in fake_state
        assert "_url_employer_seeded" not in fake_state
        assert "_pending_search_query" not in fake_state
        assert fake_state["confirmed_lookup"] == "Target"
    finally:
        app_module.st.session_state = original


def test_legacy_url_param_detection():
    assert has_legacy_employer_url_param({"selected_employer": "Target"})
    assert has_legacy_employer_url_param({"selected_employer": ["Target"]})
    assert not has_legacy_employer_url_param({"selected_employer": ""})
    assert not has_legacy_employer_url_param({})


def test_submit_clears_feedback_flags():
    state: dict[str, object] = {
        "confirmed_lookup": "Target",
        EMPLOYER_SEARCH_INPUT_KEY: "Target",
        "last_logged_lookup_signature": ("Target",),
        "show_provider_feedback": True,
        "provider_feedback_submitted": True,
    }
    apply_lookup_submission(True, "Disney", state)
    assert "last_logged_lookup_signature" not in state
    assert "show_provider_feedback" not in state
    assert "provider_feedback_submitted" not in state
