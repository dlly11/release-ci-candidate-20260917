add_library(release_candidate_core STATIC src/core.c)
add_library(release_candidate::core ALIAS release_candidate_core)

target_include_directories(
  release_candidate_core
  PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
monorepo_add_version_header(
  release_candidate_core
  "${CMAKE_CURRENT_SOURCE_DIR}/include/release_candidate/core_version.h.in"
  "release_candidate/core_version.h"
  PUBLIC
)
set_target_properties(release_candidate_core PROPERTIES EXPORT_NAME core)
monorepo_set_project_options(release_candidate_core)

install(
  TARGETS release_candidate_core
  EXPORT ReleaseCandidateTargets
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
install(
  DIRECTORY include/
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
  FILES_MATCHING
  PATTERN "*.h"
)

if(BUILD_TESTING)
  add_library(release_candidate_core_c_test_helpers OBJECT tests/unknown_status.c)
  target_link_libraries(release_candidate_core_c_test_helpers PRIVATE release_candidate::core)
  monorepo_set_project_options(release_candidate_core_c_test_helpers)

  add_executable(release_candidate_core_tests tests/test_core.cpp)
  target_link_libraries(release_candidate_core_tests PRIVATE release_candidate::core release_candidate_cpputest_main release_candidate_core_c_test_helpers)
  monorepo_set_cpp_test_options(release_candidate_core_tests)
  monorepo_set_version_test_definitions(release_candidate_core_tests)
  add_test(NAME c.core COMMAND release_candidate_core_tests)
  set_tests_properties(c.core PROPERTIES TIMEOUT 60)
endif()
