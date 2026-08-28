# Notebooks

Empty on purpose. Your notebooks go here, and you import from `src/` rather than
defining transformation logic in a cell:

```python
from src.transform import clean_country_code, extended_price, fiscal_quarter
```

That import is why the tests are worth anything. Logic that lives in a cell is tested by
nobody, and a cell that has been edited since it last ran is no evidence that anything
works. When you do put the logic in `src/`, you get it checked on every push.

Notebooks do the reading and the writing: you mount the volume, read the source, call
the functions, and write the table. The runner never executes them, and you do not need
it to.
