# Course CI Template

### ADSP 31011 Cloud-Native Data Engineering · Nick Kadochnikov

A working repository with a working pipeline in it. Push to it and a GitHub Actions
runner checks out your code, installs the pinned dependencies, lints, and runs the
tests. Open a pull request and you get the same check reporting on the pull request
before anyone reads the diff.

We use this template twice. In Week 9 you create a repository from it and spend the
session breaking and extending the pipeline. Then your final-project repository is this
same template with your own pipeline grown inside it, so the layout below is the layout
the final project requires.

## What is in here

```
.github/workflows/ci.yml   the pipeline: checkout, Python, install, lint, test
src/transform.py           four pure functions, imported by notebooks and by tests
tests/test_transform.py    pytest, driven by the fixture and by parametrized cases
conftest.py                the fixture loader, and what makes `src` importable
data/fixture_orders.csv    20 rows, authored here on purpose
notebooks/                 where your notebooks go
requirements.txt           pinned versions, because CI must be reproducible
ruff.toml                  the lint rules, chosen rather than inherited
```

## The four functions, and why these four

`src/transform.py` has `clean_country_code`, `extended_price` and `fiscal_quarter` in
it, and a fourth function built from those three. The first three are small
deliberately, and each one is a defect you have already met in this course:

- **`clean_country_code`** strips whitespace and folds case. Skip it and a group-by
  reports `us`, `US ` and `US` as three countries. Nothing errors.
- **`extended_price`** applies a discount once. Apply it twice and you will understate
  revenue by a plausible-looking amount that survives a spot check.
- **`fiscal_quarter`** turns a date into `FY25-Q3`. Derive it in three notebooks
  instead of once and two reports will disagree about which quarter a sale fell in.

The fourth, **`revenue_by_country_quarter`**, takes the orders as a DataFrame and
returns a Gold-shaped table: net revenue by cleaned country code and fiscal quarter. It
calls the other three and nothing else, so a defect in any one of them moves a number in
that table. Two tests pin the table built from the fixture to exact values, and they are
the tests that see a wrong amount which still looks like money.

All four are pure: arguments in, value out, no network, no warehouse, no file reads.
That is the property that lets a runner check them in seconds. You do the reading and
the writing in your notebooks, and they call these.

## Run it the way CI runs it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
ruff check src tests
pytest -q
```

The first line makes a virtual environment inside the repository and switches to it.
Cloud Shell and most Linux systems refuse a `pip install` into the system Python, and
`.gitignore` already keeps `.venv/` out of your commits. The other three commands are
the same three the workflow runs. When CI is red and your machine is green, the
difference is almost always an uncommitted file or an unpinned dependency.

## The fixture is the data, and that is the rule

`data/fixture_orders.csv` has twenty rows in it, written by hand. We did put the mess
in on purpose: whitespace around country codes, mixed case, a zero-quantity line, and
dates that cross both a calendar year and a fiscal year.

**CI never reads from the network.** No bucket, no warehouse, no credentials. A test
suite that downloads its input fails whenever the service it downloads from is down or
slow, and once a pipeline fails a few times for reasons outside your code, nobody looks
at it any more. For the final project you write your own small fixtures the same way,
one per source, and you plant the anomalies you want caught in them. Real trip data
never enters the repository.

## How the final project extends this

Keep the layout and grow into it.

| Here | In the final project |
|---|---|
| `src/transform.py` | your conforming, typing and quality-rule functions, still pure |
| `tests/test_transform.py` | tests over those functions, one file per module as it grows |
| `data/fixture_orders.csv` | a small fixture per service, with the anomalies planted |
| `notebooks/` | the Bronze, Silver and Gold notebooks, importing from `src/` |
| `ci.yml` | the same job, unchanged, running against more code |

Three things separate a repository that has CI from one where CI is doing work: the
layout above, tests that exercise your own quality rules rather than asserting `True`,
and a green run on the commit you do hand over.

`repo_evidence.md` in this repository is the form for the evidence you upload to Canvas
with your final project: your log and the output of your runs, pasted as text. Fill in a
copy of it after your last push and never commit it; the form says why. What counts, and
what the CI component is worth, is in the final-project brief on Canvas.

## Before you write your first line

Rename nothing yet. Push once, watch the run go green, and read the log from top to
bottom. It tells you exactly what a runner does with your code: which machine, which
Python, which packages, which commands, in order.
