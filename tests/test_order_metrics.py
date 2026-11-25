"""Tests for src.order_metrics, written by the same agent that wrote the code.

Planted for Week 9 practice, like the module they test.
"""

import pandas as pd

from src.order_metrics import average_order_value_by_country


def test_returns_a_series_named_average_order_value_when_given_orders(orders):
    result = average_order_value_by_country(orders)
    assert isinstance(result, pd.Series)
    assert result.name == "average_order_value"


def test_index_is_sorted_when_given_orders(orders):
    assert average_order_value_by_country(orders).index.is_monotonic_increasing


def test_every_country_code_is_two_upper_letters_when_given_orders(orders):
    result = average_order_value_by_country(orders)
    assert all(len(code) == 2 and code.isupper() for code in result.index)


def test_values_are_rounded_to_cents_when_given_orders(orders):
    result = average_order_value_by_country(orders)
    assert all(round(value, 2) == value for value in result)
