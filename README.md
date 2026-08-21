# Course CI Template

### ADSP 31011 Cloud-Native Data Engineering · Nick Kadochnikov

A working repository with a working pipeline. Push to it and a GitHub Actions runner
checks out your code, installs the pinned dependencies, lints, and runs the tests. Open
a pull request and the same check reports on the pull request before anyone reads the
diff.

Two things use this template. In Week 9 you create a repository from it and spend the
session breaking and extending the pipeline. Your final-project repository is the same
template with your own pipeline grown inside it, so the layout below is the layout the
final project is graded against.

## What is in here

```
.github/workflows/ci.yml   the pipeline: checkout, Python, install, lint, test
src/transform.py           three pure functions, imported by notebooks and by tests
tests/test_transform.py    pytest, driven by the fixture and by parametrized cases
conftest.py                the fixture loader, and what makes `src` importable
data/fixture_orders.csv    20 rows, authored here on purpose
notebooks/                 where your notebooks go
requirements.txt           pinned versions, because CI must be reproducible
ruff.toml                  the lint rules, chosen rather than inherited
```

## The three functions, and why these three

`src/transform.py` holds `clean_country_code`, `extended_price` and `fiscal_quarter`.
They are small deliberately, and each one is a defect you have already met in this
course:

- **`clean_country_code`** strips whitespace and folds case. Skip it and a group-by
  reports `us`, `US ` and `US` as three countries. Nothing errors.
- **`extended_price`** applies a discount once. Apply it twice and revenue is
  understated by a plausible-looking amount that survives a spot check.
- **`fiscal_quarter`** turns a date into `FY25-Q3`. Derive it in three notebooks
  instead of once and two reports will disagree about which quarter a sale fell in.

All three are pure: arguments in, value out, no network, no warehouse, no file reads.
That is the property that lets a runner check them in seconds. Your notebooks do the
reading and writing and call these.

## Run it the way CI runs it

```bash
pip install -r requirements.txt
ruff check src tests
pytest -q
```

Three commands, and they are the same three the workflow runs. When CI is red and your
machine is green, the difference is almost always an uncommitted file or an unpinned
dependency.

## The fixture is the data, and that is the rule

`data/fixture_orders.csv` has twenty rows, written by hand. It carries the mess on
purpose: whitespace around country codes, mixed case, a zero-quantity line, and dates
that cross both a calendar year and a fiscal year.

**CI never reads from the network.** No bucket, no warehouse, no credentials. A test
suite that downloads its input fails when someone else's service has a bad morning, and
a pipeline that only goes red for real reasons is the only kind anyone keeps looking at.
For the final project you author your own small fixtures the same way, one per source,
with the anomalies you want caught planted in them. Real trip data never enters the
repository.

## How the final project extends this

Keep the layout and grow into it.

| Here | In the final project |
|---|---|
| `src/transform.py` | your conforming, typing and quality-rule functions, still pure |
| `tests/test_transform.py` | tests over those functions, one file per module as it grows |
| `data/fixture_orders.csv` | a small fixture per service, with the anomalies planted |
| `notebooks/` | the Bronze, Silver and Gold notebooks, importing from `src/` |
| `ci.yml` | the same job, unchanged, running against more code |

Three things make the difference between a repository that has CI and one where CI is
doing work: the layout above, tests that exercise your own quality rules rather than
asserting `True`, and a green run on the commit you hand over.

`repo_evidence.md` in this repository is where the run links go. Fill it in as you work
rather than at the end. What counts for the course, and what the CI component is worth,
is in the Week 9 material on Canvas.

## Before you write your first line

Rename nothing yet. Push once, watch the run go green, and read the log from top to
bottom. It tells you exactly what a runner does with your code: which machine, which
Python, which packages, which commands, in order.
