cmake_minimum_required(VERSION 3.16)
project(purpleair_data_logger_csharp VERSION 2026.11.3 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(MSVC)
  add_compile_options(/MP)
endif()

add_subdirectory(../.. purpleair_data_logger_core)

add_library(purpleair_data_logger_pinvoke SHARED
  "${CMAKE_CURRENT_SOURCE_DIR}/generated/csharp/purpleair_data_logger_csharp_wrap.cxx"
)
set_target_properties(purpleair_data_logger_pinvoke PROPERTIES OUTPUT_NAME "purpleair_data_logger_csharp")
target_include_directories(purpleair_data_logger_pinvoke PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/../../include"
)
target_link_libraries(purpleair_data_logger_pinvoke PRIVATE purpleair_data_logger)
