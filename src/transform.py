"""Pure transformation functions, tested in CI and imported by notebooks.

We hold three rules for everything in this module, and together they are why a
GitHub-hosted runner can grade the pipeline's logic in under a minute:

1. No I/O. No network, no warehouse, no file reads. Arguments in, value out.
2. Deterministic. The same arguments always produce the same value.
3. Loud on bad input. If a function quietly returns something plausible for
   input it cannot handle, the defect surfaces in a Gold table three layers
   later, where it is somebody else's problem.

Your notebooks do the I/O and call these. We split it that way because it is
what makes the pipeline testable at all, and it is the layout the final project
requires.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

# The fiscal year runs 1 October to 30 September, so October starts a new year.
# We chose this to match the dim_date logic from the warehousing week. If your
# project uses a calendar fiscal year, change it here and the tests will tell
# you everywhere else it mattered.
FISCAL_YEAR_START_MONTH = 10


def clean_country_code(s: str) -> str:
    """Return a country code as two upper-case letters.

    Surrounding whitespace and case are the two ways a country code arrives
    dirty from a source system, and both give us silent duplicate keys: a
    group-by treats ``"us"``, ``"US "`` and ``"US"`` as three countries and
    splits one country's revenue across three rows. Nothing downstream errors,
    so we keep the cleaning in a tested function rather than in a notebook,
    where nothing would check it.

    Raises:
        TypeError: if ``s`` is not a string.
        ValueError: if the cleaned value is not exactly two letters.
    """
    if not isinstance(s, str):
        raise TypeError(f"country code must be a string, got {type(s).__name__}")

    cleaned = s.strip().upper()

    if len(cleaned) != 2 or not cleaned.isalpha():
        raise ValueError(f"expected a two-letter country code, got {s!r}")

    return cleaned


def extended_price(qty: int, unit_price: float, discount_rate: float = 0.0) -> float:
    """Return the discounted line total, rounded to two decimals.

    This is the measure every order-line fact table has in it. We apply the
    discount once, to the gross amount. Apply it a second time somewhere
    downstream and you have the classic revenue understatement, which a spot
    check does not find because the number still looks like money.

    Rounding is half-even, which is what :func:`round` does. If you need money
    to round half-up, you need :class:`decimal.Decimal`, and say so in a comment
    before you change it, because a rounding change moves every historical
    figure.

    Raises:
        ValueError: if ``qty`` or ``unit_price`` is negative, or if
            ``discount_rate`` falls outside the closed interval [0, 1].
    """
    if qty < 0:
        raise ValueError(f"quantity cannot be negative, got {qty}")
    if unit_price < 0:
        raise ValueError(f"unit price cannot be negative, got {unit_price}")
    if not 0.0 <= discount_rate <= 1.0:
        raise ValueError(f"discount rate must be between 0 and 1, got {discount_rate}")

    return round(qty * unit_price * (1.0 - discount_rate), 2)


def fiscal_quarter(d: date) -> str:
    """Return the fiscal year and quarter of ``d`` as ``"FY25-Q3"``.

    We label the fiscal year by the calendar year it ends in, so October 2024
    through September 2025 is all FY25. Every date in a warehouse gets this
    treatment exactly once, in a date dimension. Do it once and no report has
    to re-derive it and then disagree with another report.

    Raises:
        TypeError: if ``d`` is not a :class:`datetime.date`.
    """
    if not isinstance(d, date):
        raise TypeError(f"expected a datetime.date, got {type(d).__name__}")

    # We shift the calendar month so the fiscal year starts at index 0.
    months_into_fiscal_year = (d.month - FISCAL_YEAR_START_MONTH) % 12
    quarter = months_into_fiscal_year // 3 + 1

    fiscal_year = d.year + 1 if d.month >= FISCAL_YEAR_START_MONTH else d.year

    return f"FY{fiscal_year % 100:02d}-Q{quarter}"


def revenue_by_country_quarter(orders: pd.DataFrame) -> pd.DataFrame:
    """Return net revenue by cleaned country code and fiscal quarter.

    This is the shape of a Gold table: one row per country and fiscal quarter,
    with the revenue a report reads off it. We build it from the three functions
    above and nothing else, so a defect in any one of them changes a number in
    this table, and a test that pins those numbers catches it.

    ``orders`` needs the columns ``order_date``, ``country_code``, ``quantity``,
    ``unit_price`` and ``discount_rate``. We read it and never change it: the
    function returns a new frame with the columns ``country_code``,
    ``fiscal_quarter`` and ``net_revenue``, sorted by country and then quarter.
    A zero-quantity line stays in, and adds nothing to its group.

    Raises:
        KeyError: if a required column is missing.
        TypeError, ValueError: whatever the three functions raise for a bad row,
            because one bad row should stop the table rather than vanish from it.
    """
    lines = pd.DataFrame(
        {
            "country_code": [clean_country_code(c) for c in orders["country_code"]],
            "fiscal_quarter": [fiscal_quarter(d) for d in orders["order_date"]],
            "net_revenue": [
                extended_price(q, p, r)
                for q, p, r in zip(
                    orders["quantity"],
                    orders["unit_price"],
                    orders["discount_rate"],
                    strict=True,
                )
            ],
        }
    )

    gold = lines.groupby(["country_code", "fiscal_quarter"], as_index=False)["net_revenue"].sum()
    # Each line total is already rounded to cents. We round the sums again
    # because adding floats can leave noise in the last place: in Python,
    # 0.1 + 0.2 is 0.30000000000000004.
    gold["net_revenue"] = gold["net_revenue"].round(2)

    return gold.sort_values(["country_code", "fiscal_quarter"]).reset_index(drop=True)
