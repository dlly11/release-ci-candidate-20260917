#include "CppUTest/TestHarness.h"

#include "release_candidate/package_b.h"
#include "release_candidate/package_b_version.h"

TEST_GROUP(PackageBFarewell){};

TEST(PackageBFarewell, CreatesFarewell) {
    char output[64] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_OK,
                release_candidate_package_b_farewell("Ada", output, sizeof(output)));
    STRCMP_EQUAL("Goodbye, Ada!", output);
}

TEST_GROUP(PackageBVersion){};

TEST(PackageBVersion, MatchesRepositoryVersion) {
    STRCMP_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION, RELEASE_CANDIDATE_PACKAGE_B_VERSION);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MAJOR,
                RELEASE_CANDIDATE_PACKAGE_B_VERSION_MAJOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MINOR,
                RELEASE_CANDIDATE_PACKAGE_B_VERSION_MINOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_PATCH,
                RELEASE_CANDIDATE_PACKAGE_B_VERSION_PATCH);
}
