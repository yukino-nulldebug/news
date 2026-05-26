from __future__ import annotations

import pytest

from src.market.calculator import calculate_change, calculate_market_changes
from src.utils.exceptions import MarketCalculationError


def test_calculate_change_returns_change_and_rate():
    assert calculate_change(105.0, 100.0) == (5.0, 5.0)


def test_calculate_change_rounds_to_two_digits():
    assert calculate_change(101.234, 100.0) == (1.23, 1.23)


def test_calculate_change_returns_none_when_previous_close_is_zero():
    assert calculate_change(100.0, 0.0) == (None, None)


def test_calculate_change_raises_when_value_is_not_number():
    with pytest.raises(MarketCalculationError):
        calculate_change("100.0", 99.0)


def test_calculate_market_changes_adds_change_fields(sample_market_items):
    calculated = calculate_market_changes(sample_market_items)

    assert calculated[0]["change"] == 5.0
    assert calculated[0]["change_rate"] == 5.0
    assert "change" not in sample_market_items[0]


def test_calculate_market_changes_raises_when_required_key_is_missing(sample_market_items):
    del sample_market_items[0]["previous_close"]

    with pytest.raises(MarketCalculationError):
        calculate_market_changes(sample_market_items)
