"""Order metrics, written the way a coding agent writes them.

This module and tests/test_order_metrics.py are planted for Week 9 practice.
They play the part of code a coding agent produced from the request below, in
one pass, with its own tests, and that nobody has read line by line. Lint is
clean and every test the agent wrote passes.

The request the agent was given:

    Add average_order_value_by_country(orders). It returns the average net
    order value per cleaned country code, as a Series indexed by country and
    rounded to cents. Net value is extended_price of the line. A line with
    quantity 0 is a cancelled order: it is not an order, so it does not count.
"""

from __future__ import annotations

import pandas as pd

from src.transform import clean_country_code, extended_price


def average_order_value_by_country(orders: pd.DataFrame) -> pd.Series:
    """Return the average net order value per cleaned country code.

    ``orders`` needs the columns ``country_code``, ``quantity``,
    ``unit_price`` and ``discount_rate``, with one row per order. The result
    is indexed by country code, sorted, and rounded to two decimals.
    """
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row in orders.itertuples(index=False):
        country = clean_country_code(row.country_code)
        net = extended_price(row.quantity, row.unit_price, row.discount_rate)
        totals[country] = totals.get(country, 0.0) + net
        counts[country] = counts.get(country, 0) + 1

    averages = {country: round(totals[country] / counts[country], 2) for country in totals}
    return pd.Series(averages, name="average_order_value").sort_index()
