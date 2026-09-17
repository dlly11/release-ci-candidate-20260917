#include "CppUTest/TestHarness.h"

#include "release_candidate/core.h"
#include "release_candidate/core_version.h"

extern "C" const char *release_candidate_test_unknown_status_string(void);

TEST_GROUP(CoreFormatMessage){};

TEST(CoreFormatMessage, FormatsMessage) {
    char output[64] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_OK,
                release_candidate_core_format_message("Hello", "Ada", output, sizeof(output)));
    STRCMP_EQUAL("Hello, Ada!", output);
}

TEST(CoreFormatMessage, ReportsSmallOutputBuffer) {
    char output[4] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_BUFFER_TOO_SMALL,
                release_candidate_core_format_message("Hello", "Ada", output, sizeof(output)));
}

TEST(CoreFormatMessage, AcceptsExactFit) {
    char output[sizeof("Hello, Ada!")] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_OK,
                release_candidate_core_format_message("Hello", "Ada", output, sizeof(output)));
    STRCMP_EQUAL("Hello, Ada!", output);
}

TEST(CoreFormatMessage, TerminatesOutputOneByteShort) {
    char output[sizeof("Hello, Ada!") - 1U] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_BUFFER_TOO_SMALL,
                release_candidate_core_format_message("Hello", "Ada", output, sizeof(output)));
    STRCMP_EQUAL("Hello, Ada", output);
}

TEST(CoreFormatMessage, TerminatesSingleByteOutput) {
    char output[1] = {'x'};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_BUFFER_TOO_SMALL,
                release_candidate_core_format_message("Hello", "Ada", output, sizeof(output)));
    STRCMP_EQUAL("", output);
}

TEST(CoreFormatMessage, LeavesOutputUntouchedAfterValidationFailure) {
    char output[] = "unchanged";

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", "", output, sizeof(output)));
    STRCMP_EQUAL("unchanged", output);
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", "Ada", output, 0U));
    STRCMP_EQUAL("unchanged", output);
}

TEST(CoreFormatMessage, RejectsInvalidArguments) {
    char output[64] = {0};

    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message(nullptr, "Ada", output, sizeof(output)));
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", nullptr, output, sizeof(output)));
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", "Ada", nullptr, sizeof(output)));
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", "Ada", output, 0U));
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("", "Ada", output, sizeof(output)));
    LONGS_EQUAL(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT,
                release_candidate_core_format_message("Hello", "", output, sizeof(output)));
}

TEST_GROUP(CoreStatusString){};

TEST(CoreStatusString, DescribesEveryStatus) {
    STRCMP_EQUAL("ok", release_candidate_core_status_string(RELEASE_CANDIDATE_STATUS_OK));
    STRCMP_EQUAL("invalid argument",
                 release_candidate_core_status_string(RELEASE_CANDIDATE_STATUS_INVALID_ARGUMENT));
    STRCMP_EQUAL("buffer too small",
                 release_candidate_core_status_string(RELEASE_CANDIDATE_STATUS_BUFFER_TOO_SMALL));
    STRCMP_EQUAL("format error",
                 release_candidate_core_status_string(RELEASE_CANDIDATE_STATUS_FORMAT_ERROR));
    STRCMP_EQUAL("unknown status", release_candidate_test_unknown_status_string());
}

TEST_GROUP(CoreVersion){};

TEST(CoreVersion, MatchesRepositoryVersion) {
    STRCMP_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION, RELEASE_CANDIDATE_CORE_VERSION);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MAJOR, RELEASE_CANDIDATE_CORE_VERSION_MAJOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_MINOR, RELEASE_CANDIDATE_CORE_VERSION_MINOR);
    LONGS_EQUAL(RELEASE_CANDIDATE_EXPECTED_VERSION_PATCH, RELEASE_CANDIDATE_CORE_VERSION_PATCH);
}
