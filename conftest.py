"""Shared pytest configuration and fixtures.

We keep this file at the repository root for two reasons, and both of them
matter on the day a test suddenly stops being able to import anything.

Having it here is what puts the repository root on ``sys.path``, so
``from src.transform import ...`` resolves without you installing the package.
Move this file into ``tests/`` and every import breaks with
``ModuleNotFoundError: No module named 'src'``.

And a fixture defined here is visible to every test file, so when you add a
second test module it can use them without importing anything.
"""

from pathlib import Path

import pandas as pd
import pytest

FIXTURE_CSV = Path(__file__).parent / "data" / "fixture_orders.csv"


@pytest.fixture(scope="session")
def orders() -> pd.DataFrame:
    """The 20-row order fixture, read exactly as it sits on disk.

    We clean nothing on the way in. The whitespace and the mixed case in
    ``country_code`` are why the file exists, and a reader that stripped them
    would be testing the reader instead of the transformation.

    We resolve the path from this file rather than from the working directory.
    Otherwise a test run started from inside ``tests/`` fails to find the data
    while passing everywhere else.
    """
    return pd.read_csv(FIXTURE_CSV, dtype={"country_code": str}, parse_dates=["order_date"])
