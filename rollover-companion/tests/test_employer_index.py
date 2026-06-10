"""Bundled employer index — fast lookups without DOL master cache."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.employer_index import EmployerIndexAdapter

REPO = Path(__file__).resolve().parents[2]
INDEX = REPO / "data" / "employer_rk_index.csv"


@pytest.fixture
def index():
    if not INDEX.is_file():
        pytest.skip("employer_rk_index.csv not built")
    return EmployerIndexAdapter.from_csv(INDEX)


def test_google_instant(index: EmployerIndexAdapter):
    result = index.lookup("google")
    assert result.provider == "Vanguard"
    assert result.confidence >= 0.85


def test_target_maps_alight(index: EmployerIndexAdapter):
    result = index.lookup("Target")
    assert result.provider == "Alight Solutions"


def test_google_lookup_under_one_second(index: EmployerIndexAdapter):
    import time

    index.lookup("warmup")
    t0 = time.time()
    result = index.lookup("google")
    assert time.time() - t0 < 1.0
    assert result.provider == "Vanguard"
