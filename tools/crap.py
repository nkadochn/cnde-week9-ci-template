"""Print the CRAP score of every function in src/, and fail above a threshold.

CRAP is a 2007 metric by Alberto Savoia and Bob Evans, first called Change Risk
Analysis and Prediction and later renamed Change Risk Anti-Patterns. For one
function with cyclomatic complexity ``comp`` and test coverage ``cov`` (a
fraction from 0 to 1):

    CRAP = comp**2 * (1 - cov)**3 + comp

A fully covered function scores its complexity and nothing more. An untested
one scores ``comp**2 + comp``, so complexity is cheap when tests cover it and
expensive when they do not.

We read complexity from radon and coverage from the ``coverage.json`` that
``coverage json`` writes. Run it after the tests:

    coverage run -m pytest -q
    coverage json -q
    python tools/crap.py --max 12
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from radon.complexity import cc_visit


def crap(comp: int, cov: float) -> float:
    return comp**2 * (1.0 - cov) ** 3 + comp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max", type=float, default=12.0, help="highest CRAP allowed")
    parser.add_argument("--coverage", default="coverage.json", help="path to coverage json")
    args = parser.parse_args()

    files = json.loads(Path(args.coverage).read_text())["files"]
    rows = []
    for path in sorted(Path("src").glob("*.py")):
        functions = files.get(path.as_posix(), {}).get("functions", {})
        blocks = cc_visit(path.read_text())
        # A class block lists its methods; we score the methods, not the class.
        blocks = [m for b in blocks for m in getattr(b, "methods", [b])]
        for block in blocks:
            name = f"{block.classname}.{block.name}" if block.classname else block.name
            covered = functions.get(name, {}).get("summary", {}).get("percent_covered", 0.0)
            score = crap(block.complexity, covered / 100.0)
            rows.append((score, block.complexity, covered, f"{path.as_posix()}::{name}"))

    print(f"{'CRAP':>6} {'complexity':>10} {'coverage':>9}  function")
    for score, comp, covered, name in sorted(rows, reverse=True):
        print(f"{score:6.1f} {comp:10d} {covered:8.0f}%  {name}")

    worst = max((row[0] for row in rows), default=0.0)
    if worst > args.max:
        print(f"FAIL: highest CRAP is {worst:.1f}, above the threshold of {args.max:g}")
        return 1
    print(f"OK: highest CRAP is {worst:.1f}, at or below the threshold of {args.max:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
