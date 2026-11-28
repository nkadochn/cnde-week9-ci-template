# Instructions for coding agents

Many coding agents look for a file with this name and read it before they change
anything, and an agent that does not can be pointed at it. The person who owns
the repository reads it too, because these rules are theirs.

- **Never edit `tests/test_gold_signoff.py` or anything in `data/`.** Those files
  hold numbers a person worked out by hand from the fixture. When a test there
  fails, the code is wrong: change the code, or stop and say what you found.
- **Write tests for every behavior you add**, in `tests/`, next to the code they
  test. A test states each behavior a second time, and CI checks the two
  statements against each other on every push.
- **Keep everything in `src/` pure**: arguments in, value out, no network, no file
  reads, no warehouse.
- **Do not make a check pass by weakening it.** Do not raise the CRAP threshold in
  `.github/workflows/ci.yml`, remove a rule from `ruff.toml`, or skip a test.
- **Run the checks before you report that you are done**, the same commands CI
  runs, listed in `README.md`.
