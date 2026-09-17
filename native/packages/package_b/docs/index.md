# Native package B

The native package B library creates farewells through the core formatter. Consumers include
`<release_candidate/package_b.h>` for behaviour, `<release_candidate/package_b_version.h>` for version macros, and link
to `release_candidate::package_b`.

```cmake
target_link_libraries(my_target PRIVATE release_candidate::package_b)
```

## Native package B examples

```c
#include <release_candidate/package_b.h>

#include <stdio.h>

int main(void) {
    char message[64] = {0};
    release_candidate_status status = release_candidate_package_b_farewell("Ada", message, sizeof(message));

    if (status != RELEASE_CANDIDATE_STATUS_OK) {
        return 1;
    }

    (void)puts(message);
    return 0;
}
```

Read the configured package version at compile time:

```c
#include <release_candidate/package_b_version.h>

const char *package_b_version = RELEASE_CANDIDATE_PACKAGE_B_VERSION;
```

Within this repository, save the example as `example.c` and compile it directly with:

```bash
cc -std=c17 -Inative/packages/core/include -Inative/packages/package_b/include \
  native/packages/core/src/core.c native/packages/package_b/src/package_b.c \
  example.c -o package-b-example
./package-b-example
```

## Native package B API

```{doxygenfunction} release_candidate_package_b_farewell
:project: native
```

### Version macros

```{doxygendefine} RELEASE_CANDIDATE_PACKAGE_B_VERSION
:project: native
```

```{doxygendefine} RELEASE_CANDIDATE_PACKAGE_B_VERSION_MAJOR
:project: native
```

```{doxygendefine} RELEASE_CANDIDATE_PACKAGE_B_VERSION_MINOR
:project: native
```

```{doxygendefine} RELEASE_CANDIDATE_PACKAGE_B_VERSION_PATCH
:project: native
```
