# Example Package B

Example farewell service depending only on `release-candidate-core`.

```python
from release_candidate_package_b import FarewellService

assert FarewellService().farewell("Ada").text == "Goodbye, Ada!"
```

See the [component documentation](https://dlly11.github.io/release-ci-candidate-20260917/python/packages/package_b/docs/index.html) for examples and API details.
