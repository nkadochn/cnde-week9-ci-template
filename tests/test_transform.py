"""Tests for src.transform.

Test names read ``test_<behavior>_when_<condition>``, so a failure in the CI log
states what broke without anyone opening the file. That is the whole return on
the naming convention: the log line is the bug report.
"""

import datetime as dt

import pytest

from src.transform import clean_country_code, extended_price, fiscal_quarter


class TestCleanCountryCode:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("US", "US"),
            ("us", "US"),
            (" US ", "US"),
            ("\tde\n", "DE"),
            ("  fr", "FR"),
            ("jp  ", "JP"),
        ],
    )
    def test_returns_two_upper_letters_when_input_is_dirty(self, raw, expected):
        assert clean_country_code(raw) == expected

    def test_collapses_to_one_key_when_the_same_country_arrives_three_ways(self):
        # The failure this guards against is a group-by splitting one country
        # into three rows, which no downstream error message ever mentions.
        assert len({clean_country_code(v) for v in ("us", "US ", " US")}) == 1

    @pytest.mark.parametrize("raw", ["", "   ", "\t\n"])
    def test_raises_when_input_is_blank(self, raw):
        with pytest.raises(ValueError):
            clean_country_code(raw)

    @pytest.mark.parametrize("raw", ["USA", "U", "U1", "12", "U S"])
    def test_raises_when_input_is_not_two_letters(self, raw):
        with pytest.raises(ValueError):
            clean_country_code(raw)

    @pytest.mark.parametrize("raw", [None, 42, ["US"]])
    def test_raises_type_error_when_input_is_not_a_string(self, raw):
        with pytest.raises(TypeError):
            clean_country_code(raw)


class TestExtendedPrice:
    @pytest.mark.parametrize(
        ("qty", "unit_price", "rate", "expected"),
        [
            (10, 100.00, 0.10, 900.00),
            (5, 19.99, 0.00, 99.95),
            (1, 1499.00, 0.20, 1199.20),
            (20, 2.25, 0.50, 22.50),
            (3, 10.00, 1.00, 0.00),
        ],
    )
    def test_applies_the_discount_once_when_rate_is_given(
        self, qty, unit_price, rate, expected
    ):
        assert extended_price(qty, unit_price, rate) == pytest.approx(expected)

    def test_returns_zero_when_quantity_is_zero(self):
        assert extended_price(0, 15.00, 0.25) == 0.0

    def test_returns_gross_when_rate_is_omitted(self):
        assert extended_price(4, 25.00) == pytest.approx(100.00)

    def test_rounds_to_two_decimals_when_the_product_has_more(self):
        # 7 * 89.95 * 0.95 = 598.16749999... and money carries two decimals.
        assert extended_price(7, 89.95, 0.05) == 598.17

    @pytest.mark.parametrize("rate", [-0.01, 1.01, 2.0])
    def test_raises_when_rate_is_outside_zero_to_one(self, rate):
        with pytest.raises(ValueError):
            extended_price(5, 10.00, rate)

    @pytest.mark.parametrize(("qty", "unit_price"), [(-1, 10.00), (5, -10.00)])
    def test_raises_when_an_amount_is_negative(self, qty, unit_price):
        with pytest.raises(ValueError):
            extended_price(qty, unit_price)


class TestFiscalQuarter:
    @pytest.mark.parametrize(
        ("day", "expected"),
        [
            (dt.date(2024, 10, 1), "FY25-Q1"),
            (dt.date(2024, 12, 31), "FY25-Q1"),
            (dt.date(2025, 1, 1), "FY25-Q2"),
            (dt.date(2025, 3, 31), "FY25-Q2"),
            (dt.date(2025, 4, 1), "FY25-Q3"),
            (dt.date(2025, 6, 30), "FY25-Q3"),
            (dt.date(2025, 7, 1), "FY25-Q4"),
            (dt.date(2025, 9, 30), "FY25-Q4"),
            (dt.date(2025, 10, 1), "FY26-Q1"),
        ],
    )
    def test_maps_the_date_when_it_sits_on_a_quarter_boundary(self, day, expected):
        assert fiscal_quarter(day) == expected

    def test_rolls_the_year_when_september_becomes_october(self):
        # The two dates are one day apart and belong to different fiscal years.
        assert fiscal_quarter(dt.date(2025, 9, 30)) == "FY25-Q4"
        assert fiscal_quarter(dt.date(2025, 10, 1)) == "FY26-Q1"

    def test_keeps_the_year_when_december_becomes_january(self):
        # The calendar year rolls here and the fiscal year does not.
        assert fiscal_quarter(dt.date(2024, 12, 31)) == "FY25-Q1"
        assert fiscal_quarter(dt.date(2025, 1, 1)) == "FY25-Q2"

    def test_accepts_a_datetime_when_given_one(self):
        assert fiscal_quarter(dt.datetime(2025, 5, 20, 14, 30)) == "FY25-Q3"

    @pytest.mark.parametrize("value", ["2025-05-20", 20250520, None])
    def test_raises_when_input_is_not_a_date(self, value):
        with pytest.raises(TypeError):
            fiscal_quarter(value)


class TestAgainstTheFixture:
    """The same three functions, driven by data/fixture_orders.csv.

    Unit cases above prove each function in isolation. These prove the fixture
    is the shape the pipeline assumes, which is the check that catches a source
    file changing under you.
    """

    def test_every_country_code_cleans_when_the_fixture_is_read(self, orders):
        cleaned = [clean_country_code(c) for c in orders["country_code"]]
        assert len(cleaned) == 20
        assert all(len(c) == 2 and c.isupper() for c in cleaned)

    def test_the_fixture_is_dirty_when_read_without_cleaning(self, orders):
        # If this fails, someone tidied the fixture and the cleaning tests above
        # are no longer exercising anything.
        raw = list(orders["country_code"])
        assert any(c != c.strip() for c in raw), "no whitespace left to strip"
        assert any(c != c.upper() for c in raw), "no lower case left to fold"

    def test_ten_countries_appear_when_codes_are_cleaned(self, orders):
        assert len({clean_country_code(c) for c in orders["country_code"]}) == 10

    def test_no_line_exceeds_its_gross_when_priced(self, orders):
        for row in orders.itertuples():
            gross = extended_price(row.quantity, row.unit_price, 0.0)
            net = extended_price(row.quantity, row.unit_price, row.discount_rate)
            assert 0.0 <= net <= gross

    def test_the_discounted_total_is_lower_when_discounts_exist(self, orders):
        gross = sum(extended_price(r.quantity, r.unit_price, 0.0) for r in orders.itertuples())
        net = sum(
            extended_price(r.quantity, r.unit_price, r.discount_rate)
            for r in orders.itertuples()
        )
        assert net < gross
        # A double-applied discount would still satisfy net < gross, which is why
        # the parametrized cases above carry the exact expected amounts.

    def test_two_fiscal_years_are_covered_when_dates_are_bucketed(self, orders):
        quarters = {fiscal_quarter(d.date()) for d in orders["order_date"]}
        assert {"FY25-Q1", "FY25-Q2", "FY25-Q3", "FY25-Q4"} <= quarters
        assert any(q.startswith("FY26") for q in quarters)

    def test_one_line_has_no_quantity_when_the_fixture_is_read(self, orders):
        # The zero-quantity line is deliberate: a pipeline that divides by
        # quantity anywhere needs a row that makes it fail here rather than in
        # production.
        assert (orders["quantity"] == 0).sum() == 1
