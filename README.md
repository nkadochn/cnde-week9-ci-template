# Course CI Template

### ADSP 31011 Cloud-Native Data Engineering · Nick Kadochnikov

A working repository with a working pipeline in it. Push to it and a GitHub Actions
runner checks out your code, installs the pinned dependencies, lints, runs the tests
under coverage, and scores every function for change risk. Open a pull request and you
get the same checks reporting on the pull request before anyone reads the diff.

In Week 9 you create a repository from this template and spend the session breaking,
measuring and signing off on the pipeline. The layout below is also a good one to keep
when you grow a pipeline of your own inside it.

## What is in here

```
.github/workflows/ci.yml     the pipeline: checkout, Python, install, lint, test, CRAP gate
src/transform.py             four pure functions, imported by notebooks and by tests
src/order_metrics.py         one more function, planted as code a coding agent wrote
tests/test_transform.py      pytest over transform.py, unit cases and fixture checks
tests/test_order_metrics.py  the tests the same agent wrote for its own function
tests/test_gold_signoff.py   the exact numbers a person owns and signs off on
conftest.py                  the fixture loader, and what makes `src` importable
data/fixture_orders.csv      20 rows, authored here on purpose
tools/crap.py                the CRAP score: complexity and coverage in one number
notebooks/                   where your notebooks go
AGENTS.md                    the rules a coding agent follows in this repository
pyproject.toml               settings for coverage and mutmut
requirements.txt             exact versions of the packages we chose
ruff.toml                    the lint rules, chosen rather than inherited
```

## The functions, and why these

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
that table.

`src/order_metrics.py` is different on purpose. It plays the part of code a coding
agent wrote from a one-paragraph request, with its own tests, and nobody has read it.
The Week 9 practice asks how much its tests prove.

All of them are pure: arguments in, value out, no network, no warehouse, no file reads.
That is the property that lets a runner check them in seconds. You do the reading and
the writing in your notebooks, and they call these.

## Run it the way CI runs it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
ruff check src tests tools
coverage run -m pytest -q
coverage json -q && python tools/crap.py --max 12
```

The first line makes a virtual environment inside the repository and switches to it.
Cloud Shell and most Linux systems refuse a `pip install` into the system Python, and
`.gitignore` already keeps `.venv/` out of your commits. The last three lines are the
three checks the workflow runs. When CI is red and your machine is green, the
difference is almost always an uncommitted file or an unpinned dependency.

Mutation testing runs locally, because it reruns the test suite once for every small
change it makes to the code:

```bash
mutmut run
mutmut results
```

## Three kinds of test, and who owns each

- **Unit tests** in `tests/test_transform.py` and `tests/test_order_metrics.py` say
  what each function does a second time. Whoever writes the code writes these,
  and a coding agent can write them as well as a person can.
- **Fixture checks** confirm that `data/fixture_orders.csv` is still the shape the
  pipeline assumes, mess included.
- **Sign-off tests** in `tests/test_gold_signoff.py` hold numbers worked out by hand
  from the fixture and the business rule, before anybody ran the code. A test written
  from the code can share the code's misunderstanding of the task. A number worked
  out from the data cannot. You own this file, and `AGENTS.md` tells an agent never to
  edit it.

## The fixture is the data, and that is the rule

`data/fixture_orders.csv` has twenty rows in it, written by hand, with the mess planted
on purpose: whitespace around country codes, mixed case, a zero-quantity line, and
dates that cross both a calendar year and a fiscal year.

**The tests never read data from the network.** No bucket, no warehouse, no
credentials. The runner does download the pinned packages from PyPI when it installs
them, and that is the only download in the job. A test suite that downloads its input
fails whenever the service it downloads from is down or slow, and once a pipeline
fails a few times for reasons outside your code, nobody looks at it any more. When you
test a pipeline of your own, write its small fixtures the same way, one per source,
and plant the anomalies you want caught in them. Real data never enters the
repository.

## Growing your own pipeline in it

Keep the layout and grow into it.

| Here | In a pipeline of your own |
|---|---|
| `src/transform.py` | your conforming, typing and quality-rule functions, still pure |
| `tests/test_transform.py` | unit tests over those functions, one file per module as it grows |
| `tests/test_gold_signoff.py` | the numbers your stakeholders quote, worked out by hand |
| `data/fixture_orders.csv` | a small fixture per source, with the anomalies planted |
| `notebooks/` | the notebooks that read and write the data, importing from `src/` |
| `ci.yml` | the same job, unchanged, running against more code |

## Before you write your first line

Rename nothing yet. Push once, watch the run go green, and read the log from top to
bottom. It tells you exactly what a runner does with your code: which machine, which
Python, which packages, which commands, in order.
