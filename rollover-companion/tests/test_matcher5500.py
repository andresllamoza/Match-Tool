"""Integration tests against the repo's real Form 5500 matcher when deps are present."""

from __future__ import annotations

import pytest

from adapters.matcher5500 import Local5500Adapter


@pytest.fixture
def real_matcher():
    ok, missing = Local5500Adapter.matcher_deps_available()
    if not ok:
        pytest.skip(f"matcher deps missing: {missing}")
    return Local5500Adapter.from_matcher()


def test_target_matches_alight_via_real_5500_matcher(real_matcher):
    for query in ("Target", "Target Corporation"):
        result = real_matcher.lookup(query)
        assert result.provider == "Alight Solutions"
        assert result.confidence == 1.0
        assert result.raw_confidence_label == "High"
        assert "TARGET" in (result.matched_employer_name or "").upper()
