"""Tests for src.transform.

We name every test ``test_<behavior>_when_<condition>``, so when one fails the
CI log states what broke and nobody has to open this file to find out. That is
what we get for the extra typing: the log line becomes the bug report.
"""

import datetime as dt

import pytest

from src.transform import (
    clean_country_code,
    extended_price,
    fiscal_quarter,
    revenue_by_country_quarter,
)


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
        # We are guarding against a group-by that splits one country into
        # three rows. No downstream error message ever mentions it.
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
        # 7 * 89.95 * 0.95 = 598.16749999... and money has two decimals.
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
        # These two dates are one day apart and sit in different fiscal years.
        assert fiscal_quarter(dt.date(2025, 9, 30)) == "FY25-Q4"
        assert fiscal_quarter(dt.date(2025, 10, 1)) == "FY26-Q1"

    def test_keeps_the_year_when_december_becomes_january(self):
        # Here the calendar year rolls over and the fiscal year does not.
        assert fiscal_quarter(dt.date(2024, 12, 31)) == "FY25-Q1"
        assert fiscal_quarter(dt.date(2025, 1, 1)) == "FY25-Q2"

    def test_accepts_a_datetime_when_given_one(self):
        assert fiscal_quarter(dt.datetime(2025, 5, 20, 14, 30)) == "FY25-Q3"

    @pytest.mark.parametrize("value", ["2025-05-20", 20250520, None])
    def test_raises_when_input_is_not_a_date(self, value):
        with pytest.raises(TypeError):
            fiscal_quarter(value)


class TestAgainstTheFixture:
    """The same functions, driven by data/fixture_orders.csv.

    The unit cases above prove each function in isolation. These prove the
    fixture is still the shape the pipeline assumes, which is how we find out
    that a source file changed under us. The last two pin the Gold table built
    from the fixture to exact values, worked out line by line from its twenty rows.
    """

    def test_every_country_code_cleans_when_the_fixture_is_read(self, orders):
        cleaned = [clean_country_code(c) for c in orders["country_code"]]
        assert len(cleaned) == 20
        assert all(len(c) == 2 and c.isupper() for c in cleaned)

    def test_the_fixture_is_dirty_when_read_without_cleaning(self, orders):
        # If this fails, somebody tidied the fixture, and the cleaning tests
        # above are no longer exercising anything.
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
        # This test checks a direction and nothing more, so a wrong amount
        # that is still below the gross passes it. The two Gold tests at the
        # end of this class pin exact amounts.

    def test_two_fiscal_years_are_covered_when_dates_are_bucketed(self, orders):
        quarters = {fiscal_quarter(d.date()) for d in orders["order_date"]}
        assert {"FY25-Q1", "FY25-Q2", "FY25-Q3", "FY25-Q4"} <= quarters
        assert any(q.startswith("FY26") for q in quarters)

    def test_one_line_has_no_quantity_when_the_fixture_is_read(self, orders):
        # We put the zero-quantity line in on purpose. If your pipeline
        # divides by quantity anywhere, we want a row that makes it fail here
        # rather than in production.
        assert (orders["quantity"] == 0).sum() == 1

    def test_gold_has_one_row_per_country_and_quarter_when_the_fixture_is_aggregated(
        self, orders
    ):
        gold = revenue_by_country_quarter(orders)
        assert list(gold.columns) == ["country_code", "fiscal_quarter", "net_revenue"]
        assert len(gold) == 16
        assert gold["country_code"].nunique() == 10
        assert not gold.duplicated(["country_code", "fiscal_quarter"]).any()

    def test_gold_net_revenue_is_exact_when_the_fixture_is_aggregated(self, orders):
        gold = revenue_by_country_quarter(orders).set_index(["country_code", "fiscal_quarter"])
        # The total first, then two cells, so a wrong amount fails here even
        # if errors elsewhere in the table happen to cancel out in the total.
        # GB FY25-Q3 is 2 x 999.99, plus 15 x 7.80 less 25 percent.
        total = round(float(gold["net_revenue"].sum()), 2)
        assert total == 8989.21
        assert gold.loc[("US", "FY25-Q1"), "net_revenue"] == 148.55
        assert gold.loc[("GB", "FY25-Q3"), "net_revenue"] == 2087.73
