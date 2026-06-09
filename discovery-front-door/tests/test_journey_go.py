"""Regression: _go must not rerun on failure (errors would vanish)."""

from journey.render import _go


def test_go_does_not_set_rerun_on_error(monkeypatch):
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
  _go({"type": "lookup", "employer": "X"})
  assert jr.st.session_state.ui_error == "lookup failed"
  assert calls["rerun"] == 0
