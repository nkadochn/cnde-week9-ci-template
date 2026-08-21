"""Shared pytest configuration and fixtures.

This file sits at the repository root for two reasons, and both matter when a
test suddenly stops being able to import anything.

Its presence here is what puts the repository root on ``sys.path``, so
``from src.transform import ...`` resolves without the package being installed.
Move this file into ``tests/`` and every import breaks with
``ModuleNotFoundError: No module named 'src'``.

And fixtures defined here are visible to every test file, so a second test
module needs no import to reach them.
"""

from pathlib import Path

import pandas as pd
import pytest

FIXTURE_CSV = Path(__file__).parent / "data" / "fixture_orders.csv"


@pytest.fixture(scope="session")
def orders() -> pd.DataFrame:
    """The 20-row order fixture, read exactly as it sits on disk.

    Nothing is cleaned on the way in. The whitespace and the mixed case in
    ``country_code`` are the point of the file, and a reader that stripped them
    would test the reader instead of the transformation.

    The path is resolved from this file rather than from the working directory,
    because a test run started from ``tests/`` would otherwise fail to find the
    data while passing everywhere else.
    """
    return pd.read_csv(FIXTURE_CSV, dtype={"country_code": str}, parse_dates=["order_date"])
