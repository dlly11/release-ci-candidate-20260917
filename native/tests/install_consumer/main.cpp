#include "release_candidate/core.h"
#include "release_candidate/core_version.h"
#include "release_candidate/package_a.h"
#include "release_candidate/package_a_cli_version.h"
#include "release_candidate/package_a_version.h"
#include "release_candidate/package_b.h"
#include "release_candidate/package_b_version.h"

#include <cstring>

int main() {
    char greeting[64] = {0};
    char farewell[64] = {0};

    if (release_candidate_package_a_greeting("Ada", greeting, sizeof(greeting)) !=
            RELEASE_CANDIDATE_STATUS_OK ||
        release_candidate_package_b_farewell("Ada", farewell, sizeof(farewell)) !=
            RELEASE_CANDIDATE_STATUS_OK) {
        return 1;
    }
    if (std::strcmp(greeting, "Hello, Ada!") != 0 || std::strcmp(farewell, "Goodbye, Ada!") != 0) {
        return 2;
    }
    if (std::strcmp(RELEASE_CANDIDATE_CORE_VERSION, RELEASE_CANDIDATE_PACKAGE_A_VERSION) != 0 ||
        std::strcmp(RELEASE_CANDIDATE_CORE_VERSION, RELEASE_CANDIDATE_PACKAGE_B_VERSION) != 0 ||
        std::strcmp(RELEASE_CANDIDATE_CORE_VERSION, RELEASE_CANDIDATE_PACKAGE_A_CLI_VERSION) != 0) {
        return 3;
    }
    return 0;
}
