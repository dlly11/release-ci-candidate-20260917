#include "release_candidate/core.h"

const char *release_candidate_test_unknown_status_string(void);

/* C permits this value; converting 99 to this enum in C++ would be undefined. */
const char *release_candidate_test_unknown_status_string(void) {
    return release_candidate_core_status_string((release_candidate_status)99);
}
