#include "CppUTest/TestHarness.h"

#include "release_candidate/package_a.h"
#include "release_candidate/package_a_version.h"

TEST_GROUP(PackageAGreeting){};

TEST(PackageAGreeting, CreatesGreeting) {
    char output[64] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_OK,
                release_candidate_package_a_greeting("Ada", output, sizeof(output)));
    STRCMP_EQUAL("Hello, Ada!", output);
}

TEST_GROUP(PackageAVersion){};

TEST(PackageAVersion, MatchesRepositoryVersion) {
    STRCMP_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION, RELEASE_CANDIDATE_PACKAGE_A_VERSION);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MAJOR,
                RELEASE_CANDIDATE_PACKAGE_A_VERSION_MAJOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MINOR,
                RELEASE_CANDIDATE_PACKAGE_A_VERSION_MINOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_PATCH,
                RELEASE_CANDIDATE_PACKAGE_A_VERSION_PATCH);
}
