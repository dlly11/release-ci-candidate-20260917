#include "release_candidate/package_b.h"

release_candidate_status release_candidate_package_b_farewell(const char *name, char *output,
                                                              size_t output_capacity) {
    return release_candidate_core_format_message("Goodbye", name, output, output_capacity);
}
