# Python package A

`release-candidate-package-a` provides `GreetingService`. It depends on `release-candidate-core` and does not depend
on package B or either application.

```python
from release_candidate_package_a import GreetingService
```

## Python package A examples

### Default greeting

```python
from release_candidate_package_a import GreetingService

message = GreetingService().greet("Ada")
assert message.text == "Hello, Ada!"
assert message.source == "package_a"
```

### Custom prefix

```python
from release_candidate_package_a import GreetingService

message = GreetingService(prefix="Welcome").greet("Grace Hopper")
assert message.text == "Welcome, Grace Hopper!"
```

## Python package A API

```{automodule} release_candidate_package_a.service
:members:
:show-inheritance:
```
