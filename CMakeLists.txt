cmake_minimum_required(VERSION 3.16)
project(purpleair_data_logger VERSION 2026.11.3 LANGUAGES C CXX)
set(PURPLEAIR_DL_VERSION_STRING "2026.11.3a0")

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(MSVC)
  add_compile_options(/MP)
endif()

option(PURPLEAIR_DL_WITH_SQLITE3 "Enable SQLite3 storage sink" ON)
option(PURPLEAIR_DL_WITH_LIBPQ "Enable PostgreSQL/TimescaleDB storage sink" OFF)
option(PURPLEAIR_DL_WITH_PURPLEAIR_API "Compile with live purpleair_api C++17 layer" ON)
option(PURPLEAIR_DL_BUILD_CLI "Build purpleair-data-logger CLI executable" ON)
option(PURPLEAIR_DL_BUILD_TESTS "Build C++ unit tests" ON)

find_package(Threads REQUIRED)
find_package(Python3 COMPONENTS Interpreter REQUIRED)

if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3/sqlite3.c")
  execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/prepare_sqlite3_amalgamation.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    RESULT_VARIABLE _sqlite_prep_rc
  )
endif()

set(PURPLEAIR_DL_SOURCES
  src/version.cpp
  src/json_utils.cpp
  src/datatypes.cpp
  src/config.cpp
  src/purpleair_poller.cpp
  src/csv_sink.cpp
  src/jsonl_sink.cpp
  src/sqlite_sink.cpp
  src/psql_sink.cpp
  src/prometheus_sink.cpp
  src/sink_inspector.cpp
  src/data_logger.cpp
  src/cli_runner.cpp
)

if(PURPLEAIR_DL_WITH_SQLITE3 AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3/sqlite3.c")
  list(APPEND PURPLEAIR_DL_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3/sqlite3.c")
  set_source_files_properties(
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3/sqlite3.c"
    PROPERTIES COMPILE_DEFINITIONS "SQLITE_THREADSAFE=1;SQLITE_ENABLE_FTS5=1;SQLITE_ENABLE_JSON1=1;SQLITE_OMIT_LOAD_EXTENSION=1"
  )
endif()

add_library(purpleair_data_logger ${PURPLEAIR_DL_SOURCES})
target_include_directories(purpleair_data_logger PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(purpleair_data_logger PUBLIC Threads::Threads)

if(WIN32)
  target_link_libraries(purpleair_data_logger PUBLIC ws2_32)
endif()

if(PURPLEAIR_DL_WITH_SQLITE3)
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3/sqlite3.c")
    target_include_directories(purpleair_data_logger PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite3")
    target_compile_definitions(purpleair_data_logger PUBLIC PURPLEAIR_DL_HAVE_SQLITE3=1 PURPLEAIR_DL_EMBEDDED_SQLITE3=1)
  else()
    find_package(SQLite3 REQUIRED)
    target_link_libraries(purpleair_data_logger PUBLIC SQLite::SQLite3)
    target_compile_definitions(purpleair_data_logger PUBLIC PURPLEAIR_DL_HAVE_SQLITE3=1)
  endif()
endif()

if(PURPLEAIR_DL_WITH_LIBPQ)
  find_package(PostgreSQL REQUIRED)
  target_link_libraries(purpleair_data_logger PUBLIC PostgreSQL::PostgreSQL)
  target_compile_definitions(purpleair_data_logger PUBLIC PURPLEAIR_DL_HAVE_LIBPQ=1)
endif()

if(PURPLEAIR_DL_WITH_PURPLEAIR_API)
  set(_PA_CANDIDATES
    "${PURPLEAIR_API_SRC_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/purpleair_api"
    "${CMAKE_CURRENT_SOURCE_DIR}/../purpleair_api"
  )
  set(_PA_FOUND "")
  foreach(_cand IN LISTS _PA_CANDIDATES)
    if(_cand AND EXISTS "${_cand}/swig/src/PurpleAirAPI.cpp")
      set(_PA_FOUND "${_cand}")
      break()
    endif()
  endforeach()

  find_package(CURL QUIET)
  if(_PA_FOUND AND CURL_FOUND)
    target_sources(purpleair_data_logger PRIVATE
      "${_PA_FOUND}/swig/src/PurpleAirAPI.cpp"
      "${_PA_FOUND}/swig/src/PurpleAirAPIHelpers.cpp"
      "${_PA_FOUND}/swig/src/PurpleAirReadAPI.cpp"
      "${_PA_FOUND}/swig/src/PurpleAirWriteAPI.cpp"
      "${_PA_FOUND}/swig/src/PurpleAirLocalAPI.cpp"
    )
    target_include_directories(purpleair_data_logger PRIVATE
      "${_PA_FOUND}/swig/include"
      ${CURL_INCLUDE_DIRS}
    )
    target_link_libraries(purpleair_data_logger PUBLIC ${CURL_LIBRARIES})
    target_compile_definitions(purpleair_data_logger PUBLIC PURPLEAIR_DL_HAVE_PURPLEAIR_API=1)
  endif()
endif()

if(PURPLEAIR_DL_BUILD_CLI)
  add_executable(purpleair-data-logger src/main.cpp)
  target_link_libraries(purpleair-data-logger PRIVATE purpleair_data_logger)
endif()

if(PURPLEAIR_DL_BUILD_TESTS)
  find_package(GTest QUIET)
  if(GTest_FOUND)
    enable_testing()
    add_executable(purpleair_data_logger_tests cpp_tests/test_main.cpp)
    target_link_libraries(purpleair_data_logger_tests PRIVATE purpleair_data_logger GTest::gtest)
    add_test(NAME purpleair_data_logger_tests COMMAND purpleair_data_logger_tests)
  endif()
endif()
