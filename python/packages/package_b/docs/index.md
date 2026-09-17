# Python package B

`release-candidate-package-b` provides `FarewellService`. It depends on `release-candidate-core` and remains
independent of package A and both applications.

```python
from release_candidate_package_b import FarewellService
```

## Python package B examples

### Default farewell

```python
from release_candidate_package_b import FarewellService

message = FarewellService().farewell("Ada")
assert message.text == "Goodbye, Ada!"
assert message.source == "package_b"
```

### Custom prefix

```python
from release_candidate_package_b import FarewellService

message = FarewellService(prefix="Until next time").farewell("Grace")
assert message.text == "Until next time, Grace!"
```

## Python package B API

```{automodule} release_candidate_package_b.service
:members:
:show-inheritance:
```
