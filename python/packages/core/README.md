# Example Core

Shared Python domain values and validation used by the example packages.

```python
from release_candidate_core import normalize_name

assert normalize_name("  Ada   Lovelace  ") == "Ada Lovelace"
```

See the [component documentation](https://dlly11.github.io/release-ci-candidate-20260917/python/packages/core/docs/index.html) for examples and API details.
