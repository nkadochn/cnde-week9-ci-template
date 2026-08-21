"""Pure transformation functions, tested in CI and imported by notebooks.

Three rules hold for everything in this module, and they are the reason a
GitHub-hosted runner can grade the pipeline's logic in under a minute:

1. No I/O. No network, no warehouse, no file reads. Arguments in, value out.
2. Deterministic. The same arguments always produce the same value.
3. Loud on bad input. A function that quietly returns something plausible for
   input it cannot handle hides the defect in a Gold table three layers later.

Notebooks do the I/O and call these. That split is what makes the pipeline
testable at all, and it is the layout the final project requires.
"""

from __future__ import annotations

from datetime import date

# The fiscal year runs 1 October to 30 September, so October starts a new year.
# Chosen to match the dim_date logic from the warehousing week; if your project
# uses a calendar fiscal year, change this and the tests will tell you where.
FISCAL_YEAR_START_MONTH = 10


def clean_country_code(s: str) -> str:
    """Return a country code as two upper-case letters.

    Surrounding whitespace and case are the two ways a country code arrives
    dirty from a source system, and both produce silent duplicate keys: a
    group-by treats ``"us"``, ``"US "`` and ``"US"`` as three countries and
    splits one country's revenue across three rows. Nothing downstream errors,
    which is why this belongs in a tested function rather than in a notebook.

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

    The measure every order-line fact table carries. The discount is applied
    once, to the gross amount. Applying it a second time somewhere downstream
    is the classic revenue understatement, and it is invisible in a spot check
    because the number still looks like money.

    Rounding is half-even, which is what :func:`round` does. Money that must
    round half-up needs :class:`decimal.Decimal`; say so in a comment before
    you change it, because a rounding change moves every historical figure.

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

    The fiscal year is labelled by the calendar year it ends in, so October
    2024 through September 2025 is all FY25. Every date in a warehouse gets
    this treatment exactly once, in a date dimension, so that no report has to
    re-derive it and disagree with another report.

    Raises:
        TypeError: if ``d`` is not a :class:`datetime.date`.
    """
    if not isinstance(d, date):
        raise TypeError(f"expected a datetime.date, got {type(d).__name__}")

    # Shift the calendar month so that the fiscal year starts at index 0.
    months_into_fiscal_year = (d.month - FISCAL_YEAR_START_MONTH) % 12
    quarter = months_into_fiscal_year // 3 + 1

    fiscal_year = d.year + 1 if d.month >= FISCAL_YEAR_START_MONTH else d.year

    return f"FY{fiscal_year % 100:02d}-Q{quarter}"
