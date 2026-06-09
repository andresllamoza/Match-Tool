from __future__ import annotations

from .models import BALANCE_RANGE_BOUNDS, BalanceRange, ValueReveal

DEFAULT_MATCH_RATE = 0.01


def compute_value_reveal(
    balance_range: BalanceRange,
    match_rate: float = DEFAULT_MATCH_RATE,
) -> ValueReveal:
    low_bound, high_bound = BALANCE_RANGE_BOUNDS[balance_range]
    return ValueReveal(
        balance_range=balance_range,
        match_rate=match_rate,
        match_low=int(low_bound * match_rate),
        match_high=int(high_bound * match_rate),
    )
