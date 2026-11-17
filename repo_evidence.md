# Repository evidence

This file is deliverable 4 of the final project. You upload it to Canvas on its own, next to the
repository zip, and you never commit it. We grade from what you upload and never open GitHub, so
every section below asks for text that you copy from your terminal or from a run's log and paste in.

Write it after your last push. Committing it would add a new top line to your log, and the green
run you paste would then no longer be on your final commit. To keep a `git add .` from picking it
up, copy this file out of your repository (for example to `~/repo_evidence.md`) and fill in the
copy.

The red run shows that your checks can fail and that you fixed what they found, which a green run
alone cannot show.

## Bring your clone up to date

The log below comes from your local clone. A pull request merged in the GitHub browser does not
reach your clone on its own, and a clone that is behind gives you an old log, which does not match
your green run. Run this first:

```bash
git switch main && git pull && git status -sb
```

Go on only when the status line does not say "behind".

## Your log

Run this in your up-to-date clone and paste what it prints. Its top line is your final commit.

```bash
git log --oneline -20
```

```text

```

## Your final green Actions run

Open the run in the **Actions** tab, then the job, then each step.

- **Commit id.** It has to match the top line of your log above. A green run on an older commit
  says nothing about the code you hand in.

  ```text

  ```

- **The last lines of the `ruff` step:**

  ```text

  ```

- **The last lines of the `pytest` step:**

  ```text

  ```

## One red run from your history

This run has to be failed by a test of one of your own quality rules on your own fixtures. The
Week 9 practice run (the `extended_price` break) does not count, and neither does a run failed by
any test that came with this template. The final-project brief on Canvas says what a missing red
run costs.

- **Commit id:**

  ```text

  ```

- **The name of the failing test and its error line.** For `pytest` both are in the `FAILED` line
  of the short test summary at the end of the step.

  ```text

  ```

- **What it caught, in one sentence:**



## Notes (optional)

Leave this empty unless a reader needs something in order to believe the sections above: a run that
is red for a reason you know about, a test you have skipped and why, a dependency you had to unpin.
