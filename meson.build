project(
  'purpleair_data_logger',
  ['c', 'cpp'],
  version: '2026.11.3a0',
  license: 'MIT',
  default_options: [
    'c_std=c11',
    'cpp_std=c++17',
    'warning_level=2',
  ],
  meson_version: '>=0.63.0',
)

cpp = meson.get_compiler('cpp')
fs = import('fs')
py_prog = find_program('python3', 'python', required: true)
threads_dep = dependency('threads')

# Ensure embedded SQLite3 amalgamation is provisioned
run_command(py_prog, 'tools/prepare_sqlite3_amalgamation.py', check: true)

inc_dirs = [include_directories('include')]
extra_deps = [threads_dep]
cpp_args = []
core_sources = files(
  'src/version.cpp',
  'src/json_utils.cpp',
  'src/datatypes.cpp',
  'src/config.cpp',
  'src/purpleair_poller.cpp',
  'src/csv_sink.cpp',
  'src/jsonl_sink.cpp',
  'src/sqlite_sink.cpp',
  'src/psql_sink.cpp',
  'src/prometheus_sink.cpp',
  'src/sink_inspector.cpp',
  'src/data_logger.cpp',
  'src/cli_runner.cpp',
)

# SQLite3 dependency (embedded amalgamation preferred)
if fs.is_file('third_party/sqlite3/sqlite3.c')
  sqlite_lib = static_library(
    'sqlite3_embedded',
    'third_party/sqlite3/sqlite3.c',
    include_directories: include_directories('third_party/sqlite3'),
    c_args: [
      '-DSQLITE_THREADSAFE=1',
      '-DSQLITE_ENABLE_FTS5=1',
      '-DSQLITE_ENABLE_JSON1=1',
      '-DSQLITE_OMIT_LOAD_EXTENSION=1',
    ],
    pic: true,
  )
  sqlite_dep = declare_dependency(
    link_with: sqlite_lib,
    include_directories: include_directories('third_party/sqlite3'),
  )
  extra_deps += sqlite_dep
  cpp_args += ['-DPURPLEAIR_DL_HAVE_SQLITE3=1', '-DPURPLEAIR_DL_EMBEDDED_SQLITE3=1']
else
  sqlite_dep = dependency('sqlite3', required: get_option('with_sqlite3'))
  if sqlite_dep.found()
    extra_deps += sqlite_dep
    cpp_args += '-DPURPLEAIR_DL_HAVE_SQLITE3=1'
  endif
endif

# Optional PostgreSQL libpq dependency
libpq_dep = dependency('libpq', required: get_option('with_libpq'))
if libpq_dep.found()
  extra_deps += libpq_dep
  cpp_args += '-DPURPLEAIR_DL_HAVE_LIBPQ=1'
endif

# Optional purpleair_api C++17 layer integration
purpleair_api_src_opt = get_option('purpleair_api_src_dir')
purpleair_api_candidates = []
if purpleair_api_src_opt != ''
  purpleair_api_candidates += purpleair_api_src_opt
endif
purpleair_api_candidates += ['third_party/purpleair_api', '../purpleair_api']

purpleair_api_root = ''
foreach cand : purpleair_api_candidates
  if purpleair_api_root == '' and fs.is_dir(cand / 'swig/include') and fs.is_file(cand / 'swig/src/PurpleAirAPI.cpp')
    purpleair_api_root = cand
  endif
endforeach

if get_option('with_purpleair_api').allowed() and purpleair_api_root != ''
  libcurl_dep = dependency('libcurl', required: get_option('with_purpleair_api'))
  if libcurl_dep.found()
    extra_deps += libcurl_dep
    inc_dirs += include_directories(purpleair_api_root / 'swig/include')
    core_sources += files(
      purpleair_api_root / 'swig/src/PurpleAirAPI.cpp',
      purpleair_api_root / 'swig/src/PurpleAirAPIHelpers.cpp',
      purpleair_api_root / 'swig/src/PurpleAirReadAPI.cpp',
      purpleair_api_root / 'swig/src/PurpleAirWriteAPI.cpp',
      purpleair_api_root / 'swig/src/PurpleAirLocalAPI.cpp',
    )
    cpp_args += '-DPURPLEAIR_DL_HAVE_PURPLEAIR_API=1'
  endif
endif

if host_machine.system() == 'windows'
  ws2_dep = cpp.find_library('ws2_32', required: true)
  extra_deps += ws2_dep
endif

purpleair_dl_lib = static_library(
  'purpleair_data_logger',
  core_sources,
  include_directories: inc_dirs,
  dependencies: extra_deps,
  cpp_args: cpp_args,
  pic: true,
  install: false,
)

purpleair_dl_dep = declare_dependency(
  link_with: purpleair_dl_lib,
  include_directories: inc_dirs,
  dependencies: extra_deps,
  compile_args: cpp_args,
)

if get_option('build_cli')
  executable(
    'purpleair-data-logger',
    'src/main.cpp',
    dependencies: [purpleair_dl_dep],
    install: true,
  )
endif

if get_option('build_tests')
  gtest_dep = dependency('gtest', main: false, required: false)
  if gtest_dep.found()
    test_exe = executable(
      'purpleair_data_logger_tests',
      files(
        'cpp_tests/test_main.cpp',
        'cpp_tests/test_json_utils.cpp',
        'cpp_tests/test_config_and_datatypes.cpp',
        'cpp_tests/test_queue_and_sinks.cpp',
        'cpp_tests/test_sink_inspector.cpp',
        'cpp_tests/test_purpleair_poller.cpp',
        'cpp_tests/test_data_logger_and_cli.cpp',
        'cpp_tests/test_main_binary.cpp',
      ),
      dependencies: [purpleair_dl_dep, gtest_dep],
      build_by_default: true,
    )
    test('purpleair_data_logger_cpp_tests', test_exe, timeout: 120)
  endif
endif
