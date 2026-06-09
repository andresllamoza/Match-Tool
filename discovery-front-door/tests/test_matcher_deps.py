from discovery.adapters.matcher5500 import Local5500Adapter


def test_matcher_deps_available():
    ok, missing = Local5500Adapter.matcher_deps_available()
    assert ok is True
    assert missing is None
