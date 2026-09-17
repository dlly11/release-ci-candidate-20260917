add_library(release_candidate_package_a STATIC src/package_a.c)
add_library(release_candidate::package_a ALIAS release_candidate_package_a)

target_include_directories(
  release_candidate_package_a
  PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
monorepo_add_version_header(
  release_candidate_package_a
  "${CMAKE_CURRENT_SOURCE_DIR}/include/release_candidate/package_a_version.h.in"
  "release_candidate/package_a_version.h"
  PUBLIC
)
target_link_libraries(release_candidate_package_a PUBLIC release_candidate::core)
set_target_properties(release_candidate_package_a PROPERTIES EXPORT_NAME package_a)
monorepo_set_project_options(release_candidate_package_a)

install(
  TARGETS release_candidate_package_a
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
  add_executable(release_candidate_package_a_tests tests/test_package_a.cpp)
  target_link_libraries(release_candidate_package_a_tests PRIVATE release_candidate::package_a release_candidate_cpputest_main)
  monorepo_set_cpp_test_options(release_candidate_package_a_tests)
  monorepo_set_version_test_definitions(release_candidate_package_a_tests)
  add_test(NAME c.package_a COMMAND release_candidate_package_a_tests)
  set_tests_properties(c.package_a PROPERTIES TIMEOUT 60)
endif()
