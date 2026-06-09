from discovery.models import BalanceRange, ValueReveal
from discovery.value import compute_value_reveal


def test_value_reveal_from_range():
    vr = compute_value_reveal(BalanceRange.R_50_100K)
    assert vr.match_low == 500
    assert vr.match_high == 1000
    assert vr.match_rate == 0.01


def test_value_reveal_has_no_balance_field():
    assert "balance" not in ValueReveal.model_fields


def test_disclaimer_present():
    vr = compute_value_reveal(BalanceRange.R_10_50K)
    assert "Illustrative" in vr.disclaimer
    assert "guaranteed" in vr.disclaimer.lower()


def test_custom_match_rate():
    vr = compute_value_reveal(BalanceRange.R_0_10K, match_rate=0.02)
    assert vr.match_low == 0
    assert vr.match_high == 200
