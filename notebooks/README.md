# Notebooks

Empty on purpose. Notebooks go here, and they import from `src/` rather than defining
transformation logic in a cell:

```python
from src.transform import clean_country_code, extended_price, fiscal_quarter
```

That import is why the tests are worth anything. Logic that lives in a cell is tested
by nobody, and a cell that has been edited since it last ran is not evidence of
anything. Logic in `src/` is checked on every push.

Notebooks do the reading and the writing: mount the volume, read the source, call the
functions, write the table. The runner never executes them, and it does not need to.
