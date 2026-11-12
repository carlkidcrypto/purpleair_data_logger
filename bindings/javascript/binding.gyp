{
  "targets": [
    {
      "target_name": "purpleair_data_logger",
      "sources": [
        "generated/javascript/purpleair_data_logger_javascript_wrap.cxx",
        "../../src/version.cpp",
        "../../src/json_utils.cpp",
        "../../src/datatypes.cpp",
        "../../src/config.cpp",
        "../../src/purpleair_poller.cpp",
        "../../src/csv_sink.cpp",
        "../../src/jsonl_sink.cpp",
        "../../src/sqlite_sink.cpp",
        "../../src/psql_sink.cpp",
        "../../src/prometheus_sink.cpp",
        "../../src/sink_inspector.cpp",
        "../../src/data_logger.cpp",
        "../../src/cli_runner.cpp",
        "../../third_party/sqlite3/sqlite3.c"
      ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")",
        "../../include",
        "../../third_party/sqlite3"
      ],
      "defines": [
        "PURPLEAIR_DL_HAVE_SQLITE3=1",
        "PURPLEAIR_DL_EMBEDDED_SQLITE3=1",
        "PURPLEAIR_DL_HAVE_LIBPQ=0",
        "SQLITE_THREADSAFE=1",
        "SQLITE_ENABLE_FTS5=1",
        "SQLITE_ENABLE_JSON1=1",
        "SQLITE_OMIT_LOAD_EXTENSION=1"
      ],
      "cflags!": ["-fno-exceptions"],
      "cflags_cc!": ["-fno-exceptions"],
      "cflags_cc": ["-std=c++17"],
      "conditions": [
        ["OS=='linux'", {
          "ldflags": ["-Wl,-rpath,'$$ORIGIN/libs'"]
        }],
        ["OS=='mac'", {
          "xcode_settings": {
            "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
            "CLANG_CXX_LANGUAGE_STANDARD": "c++17",
            "LD_RUNPATH_SEARCH_PATHS": ["@loader_path/.dylibs"]
          }
        }],
        ["OS=='win'", {
          "libraries": ["ws2_32.lib"],
          "msvs_settings": {
            "VCCLCompilerTool": {
              "ExceptionHandling": 1,
              "AdditionalOptions": ["/std:c++17"]
            }
          }
        }]
      ]
    }
  ]
}
