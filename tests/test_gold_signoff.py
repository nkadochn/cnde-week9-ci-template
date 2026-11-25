"""The numbers a person signs off on. Owned by a human; agents do not edit it.

Every expected value in this file was worked out by hand from the twenty rows
of data/fixture_orders.csv, before anybody ran the code. That is the rule that
makes the file worth having. The tests in the other files may be written by
whoever wrote the code, a coding agent included, and a test written from the
code can share the code's misunderstanding of the task. A number worked out
from the data and the business rule cannot.

So when one of these goes red, change the code, not the number. Change a
number only when the business rule changed, and say so in the pull request.
"""

from src.transform import revenue_by_country_quarter


def test_gold_has_one_row_per_country_and_quarter_when_the_fixture_is_aggregated(orders):
    gold = revenue_by_country_quarter(orders)
    assert list(gold.columns) == ["country_code", "fiscal_quarter", "net_revenue"]
    assert len(gold) == 16
    assert gold["country_code"].nunique() == 10
    assert not gold.duplicated(["country_code", "fiscal_quarter"]).any()


def test_gold_net_revenue_is_exact_when_the_fixture_is_aggregated(orders):
    gold = revenue_by_country_quarter(orders).set_index(["country_code", "fiscal_quarter"])
    # The total first, then two cells, so a wrong amount fails here even
    # if errors elsewhere in the table happen to cancel out in the total.
    # GB FY25-Q3 is 2 x 999.99, plus 15 x 7.80 less 25 percent.
    total = round(float(gold["net_revenue"].sum()), 2)
    assert total == 8989.21
    assert gold.loc[("US", "FY25-Q1"), "net_revenue"] == 148.55
    assert gold.loc[("GB", "FY25-Q3"), "net_revenue"] == 2087.73
