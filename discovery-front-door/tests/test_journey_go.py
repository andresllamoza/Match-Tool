"""Regression: _go persists errors in session and always reruns."""

from journey.render import _go


def test_go_reruns_and_persists_error(monkeypatch):
    calls = {"rerun": 0}

    monkeypatch.setattr("journey.render.apply_action", lambda _a: "lookup failed")
    monkeypatch.setattr("journey.render.st.rerun", lambda: calls.__setitem__("rerun", calls["rerun"] + 1))

    class SS(dict):
        def __getattr__(self, k):
            return self.get(k)

        def __setattr__(self, k, v):
            self[k] = v

        def pop(self, k, default=None):
            return dict.pop(self, k, default)

    import journey.render as jr

    jr.st.session_state = SS()
    _go({"type": "lookup", "employer": "Target"})
    assert jr.st.session_state.ui_error == "lookup failed"
    assert calls["rerun"] == 1


def test_go_clears_error_on_success(monkeypatch):
    calls = {"rerun": 0}

    class View:
        pass

    monkeypatch.setattr("journey.render.apply_action", lambda _a: View())
    monkeypatch.setattr("journey.render.st.rerun", lambda: calls.__setitem__("rerun", calls["rerun"] + 1))

    class SS(dict):
        def __getattr__(self, k):
            return self.get(k)

        def __setattr__(self, k, v):
            self[k] = v

        def pop(self, k, default=None):
            return dict.pop(self, k, default)

    import journey.render as jr

    jr.st.session_state = SS(ui_error="old")
    _go({"type": "lookup", "employer": "Target"})
    assert "ui_error" not in jr.st.session_state
    assert calls["rerun"] == 1
