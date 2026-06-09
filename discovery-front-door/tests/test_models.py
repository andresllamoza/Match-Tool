from discovery.models import BalanceRange, BALANCE_RANGE_BOUNDS


def test_all_balance_ranges_have_bounds():
    for br in BalanceRange:
        assert br in BALANCE_RANGE_BOUNDS
        low, high = BALANCE_RANGE_BOUNDS[br]
        assert low < high
