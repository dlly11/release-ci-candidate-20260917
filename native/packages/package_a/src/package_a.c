#include "release_candidate/package_a.h"

release_candidate_status release_candidate_package_a_greeting(const char *name, char *output,
                                                              size_t output_capacity) {
    return release_candidate_core_format_message("Hello", name, output, output_capacity);
}
