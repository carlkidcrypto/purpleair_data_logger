Software requirements
=====================

Purpose and conventions
-----------------------

This document defines the externally observable requirements for the PurpleAir
data logger modules. Each requirement has a stable identifier for use in tests,
issues, and change reviews. ``Shall`` indicates required behavior. CLI option
names and JSON field names are case-sensitive.

Shared data logger requirements
-------------------------------

**[GEN-001]** The software shall support Python 3.11 through Python 3.15.

**[GEN-002]** Each executable data logger module shall support invocation with
``python -m purpleair_data_logger.<ModuleName>``.

**[GEN-003]** Each executable data logger module shall provide ``-h`` and
``--help`` options that print usage information without starting a polling loop.

**[GEN-004]** The package initializer ``purpleair_data_logger/__init__.py`` shall
remain free of executable-module imports so module invocation does not emit a
duplicate-module ``RuntimeWarning``.

**[GEN-005]** The common CLI parser shall provide these optional string options:

* ``-paa_read_key`` for the PurpleAir cloud Read API key.
* ``-paa_write_key`` for the PurpleAir cloud Write API key.
* ``-paa_single_sensor_request_json_file`` for a single-sensor configuration.
* ``-paa_multiple_sensor_request_json_file`` for a multiple-sensor
	configuration.
* ``-paa_group_sensor_request_json_file`` for a group configuration.
* ``-paa_local_sensor_request_json_file`` for a local-network configuration.

**[GEN-006]** A cloud request shall initialize the PurpleAir API client with the
provided Read and Write API keys.

**[GEN-007]** A supported local-network request shall initialize the PurpleAir
API client with the IPv4 addresses in ``sensor_ip_list`` and shall not require a
cloud API key.

**[GEN-008]** Storage logger modules shall normalize every sensor record to the
complete accepted PurpleAir field set before passing the record to the output
sink, using default values for fields absent from the response.

**[GEN-009]** Storage logger modules shall poll continuously until interrupted
or until an unrecoverable error terminates the process.

Configuration requirements
--------------------------

**[CFG-001]** A storage logger invocation shall provide exactly one of the four
common JSON configuration options.

**[CFG-002]** A storage logger shall raise ``PurpleAirDataLoggerError`` when no
configuration option is provided or when more than one configuration option is
provided.

**[CFG-003]** A single-sensor configuration shall contain
``poll_interval_seconds``, ``sensor_index``, ``read_key``, and ``fields``.

**[CFG-004]** A multiple-sensor configuration shall contain
``poll_interval_seconds`` and the PurpleAir multiple-sensor request fields
``fields``, ``location_type``, ``read_keys``, ``show_only``,
``modified_since``, ``max_age``, ``nwlng``, ``nwlat``, ``selng``, and ``selat``.

**[CFG-005]** A group configuration shall contain
``poll_interval_seconds``, ``sensor_group_name``, ``add_sensors_to_group``,
``sensor_index_list``, and all request fields listed in **[CFG-004]**.

**[CFG-006]** When ``add_sensors_to_group`` is true, the group logger shall add
each sensor in ``sensor_index_list`` to the selected group and shall tolerate a
sensor that is already a member of that group.

**[CFG-007]** A local-network configuration shall contain ``sensor_ip_list`` as
a list of IPv4-address strings and ``poll_interval_seconds`` as the polling
delay in seconds.

**[CFG-008]** Cloud single-, multiple-, and group-sensor polling intervals shall
be at least 60 seconds; a lower value shall raise
``PurpleAirDataLoggerError``.

**[CFG-009]** Each completed storage polling cycle shall wait for the configured
polling interval before beginning the next cycle.

Current implementation constraints
----------------------------------

This section is informative rather than normative. The common parser presents
``-paa_local_sensor_request_json_file`` to every logger. The CSV, Loki, and
Matter CLIs initialize their PurpleAir API clients from ``sensor_ip_list`` and
support that mode. The SQLite, PostgreSQL, and Prometheus CLIs do not currently
pass ``sensor_ip_list`` to their API clients, so local-network operation is not
supported by those three module CLIs.

CSV data logger requirements
----------------------------

**[CSV-001]** ``PurpleAirCSVDataLogger`` shall require the CLI option
``-save_file_path``.

**[CSV-002]** The CSV logger shall support single-sensor, multiple-sensor,
group-sensor, and local-network configurations.

**[CSV-003]** For local-network operation, the CSV CLI shall read
``sensor_ip_list`` before constructing ``PurpleAirCSVDataLogger``.

**[CSV-004]** The CSV logger shall create ``-save_file_path`` when the directory
does not exist.

**[CSV-005]** The CSV logger shall maintain separate files for station and
status, environmental, miscellaneous, PM1.0, PM2.5, PM2.5 pseudo-average,
PM10.0, particle-count, and ThingSpeak field groups.

**[CSV-006]** The CSV logger shall append sensor records to the field-group
files and shall flush and close every file after each stored record.

**[CSV-007]** The CSV logger shall write one header row per field-group file for
each logger process before writing its first sensor record.

**[CSV-008]** A CSV ``UnicodeEncodeError`` shall increment the logger's data
error counter and shall report the failure without preventing the file streams
from being closed.

SQLite data logger requirements
-------------------------------

**[SQLITE-001]** ``PurpleAirSQLiteDataLogger`` shall require the CLI option
``-db_name`` containing the path and file name of the SQLite database.

**[SQLITE-002]** The SQLite CLI shall support cloud single-sensor,
multiple-sensor, and group-sensor configurations.

**[SQLITE-003]** The SQLite logger shall create its field-group tables when they
do not already exist.

**[SQLITE-004]** The SQLite logger shall store each normalized sensor record in
the station and status, environmental, miscellaneous, PM1.0, PM2.5, PM2.5
pseudo-average, PM10.0, particle-count, and ThingSpeak tables.

**[SQLITE-005]** The SQLite logger shall commit the database transaction after
storing a sensor record in all field-group tables.

PostgreSQL data logger requirements
-----------------------------------

**[PSQL-001]** ``PurpleAirPSQLDataLogger`` shall require ``-db_usr`` and ``-db``
CLI options.

**[PSQL-002]** The PostgreSQL CLI shall accept ``-db_host`` with a default of
``localhost``, ``-db_port`` with a default of ``5432``, and optional ``-db_pwd``.

**[PSQL-003]** The PostgreSQL CLI shall support cloud single-sensor,
multiple-sensor, and group-sensor configurations.

**[PSQL-004]** The PostgreSQL logger shall connect with ``pg8000`` using the
provided user, host, database, port, and password values.

**[PSQL-005]** On initialization, the PostgreSQL logger shall create missing
field-group tables, convert them to TimescaleDB hypertables, configure
compression policies, configure continuous aggregates, and prepare insertion
statements.

**[PSQL-006]** The PostgreSQL logger shall store each normalized sensor record
in all field-group tables and commit the transaction after the record is stored.

**[PSQL-007]** Unix epoch values written to PostgreSQL timestamp columns shall be
converted to UTC timestamps; ``None`` timestamp values shall remain ``None``.

**[PSQL-008]** The optional ``-db_drop_all_tables`` flag shall display a
destructive-operation warning and require interactive confirmation before
dropping tables.

**[PSQL-009]** When table deletion is confirmed with ``yes``, the PostgreSQL
logger shall run the drop statements, commit the transaction, and exit without
starting the polling loop.

**[PSQL-010]** When table deletion is declined with ``no``, the PostgreSQL logger
shall exit without dropping tables or starting the polling loop.

Loki data logger requirements
-----------------------------

**[LOKI-001]** ``PurpleAirLokiDataLogger`` shall require the CLI option
``-loki_url``.

**[LOKI-002]** The Loki CLI shall accept optional ``-loki_usr`` and ``-loki_pwd``
options for HTTP Basic authentication.

**[LOKI-003]** The Loki logger shall support single-sensor, multiple-sensor,
group-sensor, and local-network configurations.

**[LOKI-004]** For local-network operation, the Loki CLI shall read
``sensor_ip_list`` before constructing ``PurpleAirLokiDataLogger``.

**[LOKI-005]** The Loki logger shall send data to
``<loki_url>/loki/api/v1/push`` and shall avoid adding a duplicate slash when the
base URL ends in ``/``.

**[LOKI-006]** The Loki logger shall use a 10-second HTTP request timeout.

**[LOKI-007]** The Loki logger shall use Basic authentication only when both a
username and password are provided.

**[LOKI-008]** Each sensor record shall produce separate Loki streams for the
nine PurpleAir field groups, labeled with ``sensor_index`` and ``data_group``.

**[LOKI-009]** Loki event timestamps shall be represented as decimal-string Unix
timestamps in nanoseconds.

**[LOKI-010]** A Loki push failure shall increment the data error counter and
report the failure without terminating the polling loop.

Prometheus data logger requirements
-----------------------------------

**[PROM-001]** ``PurpleAirPrometheusDataLogger`` shall accept the optional
integer CLI option ``-prometheus_port`` and shall default it to ``9760``.

**[PROM-002]** The Prometheus CLI shall support cloud single-sensor,
multiple-sensor, and group-sensor configurations.

**[PROM-003]** The Prometheus logger shall start an HTTP metrics server on the
configured port during logger initialization.

**[PROM-004]** The Prometheus logger shall expose supported numeric PurpleAir
fields as Gauges labeled by ``sensor_index``.

**[PROM-005]** The Prometheus logger shall convert numeric values to floating
point before assigning Gauge values.

**[PROM-006]** A missing or non-numeric PurpleAir value shall be represented as
``NaN`` rather than terminating metric collection.

**[PROM-007]** The Python API shall permit a caller-provided
``CollectorRegistry`` and shall default to the global Prometheus registry.

Matter data logger requirements
-------------------------------

**[MAT-001]** ``PurpleAirMatterDataLogger`` shall provide a module CLI through
``main`` and an ``if __name__ == "__main__"`` guard.

**[MAT-002]** The Matter CLI shall accept optional ``--http-host`` and
``--http-port`` options with defaults of ``127.0.0.1`` and ``9855``.

**[MAT-003]** The Matter CLI shall accept ``--matter-only`` as a Boolean flag.

**[MAT-004]** The Matter CLI shall accept ``-save_file_path`` for compatibility,
shall warn when it is supplied, and shall not write Matter output to that path.

**[MAT-005]** Continuous cloud operation shall require a non-empty
``sensor_indexes`` list supplied by the selected JSON configuration or by the
Python constructor.

**[MAT-006]** Continuous local operation shall require a non-empty
``sensor_ip_list`` and shall initialize the PurpleAir API client with those
addresses before polling.

**[MAT-007]** The Matter logger shall reject more than one JSON configuration
file in a single invocation.

**[MAT-008]** The Matter logger shall reject continuous operation when neither
``sensor_indexes`` nor ``sensor_ip_list`` is available.

**[MAT-009]** Matter polling intervals below 60 seconds shall be clamped to 60
seconds.

**[MAT-010]** Cloud configuration shall support optional ``sensor_names`` and
``read_keys`` objects keyed by sensor index, and JSON string keys shall be
converted to integer keys before lookup.

**[MAT-011]** The Matter logger shall convert successful PurpleAir readings to
Matter 1.5.1 Air Quality Sensor-shaped JSON using device type ``0x002D``.

**[MAT-012]** The Matter logger shall expose Air Quality, Temperature,
Relative Humidity, and Pressure measurement clusters when the corresponding
readings are available.

**[MAT-013]** ``run_once`` shall return a dictionary keyed by sensor index and
shall not start an HTTP server or continuous polling loop.

**[MAT-014]** Continuous mode shall start the HTTP server before entering the
polling loop.

**[MAT-015]** ``GET /`` and ``GET /health`` shall return HTTP 200 with service
status and the current converted-sensor count.

**[MAT-016]** ``GET /matter/sensors`` shall return HTTP 200 with every current
sensor index, its converted device, and a total count.

**[MAT-017]** ``GET /matter/sensor/<sensor_index>`` shall return HTTP 200 for an
available integer sensor index, HTTP 400 for a non-integer index, and HTTP 404
for an unavailable index.

**[MAT-018]** Unknown HTTP paths shall return HTTP 404, and query parameters
shall not alter route matching.

**[MAT-019]** HTTP responses shall use JSON UTF-8 content type and shall include
``Cache-Control: no-store``.

**[MAT-020]** HTTP ``HEAD`` requests shall return HTTP 204.

**[MAT-021]** Access to the shared Matter device dictionary shall be protected
by a shared lock, and updates shall preserve the dictionary object referenced by
the HTTP server.

**[MAT-022]** A failed sensor poll shall not remove that sensor's last-known-good
reading from the HTTP API.

**[MAT-023]** An individual cloud sensor polling or conversion exception shall
be logged and isolated so polling can continue for other sensors.

**[MAT-024]** The Matter HTTP server shall permit socket-address reuse for quick
service restarts.

**[MAT-025]** The Matter HTTP API shall be documented as unauthenticated and
unencrypted, and the default host shall remain loopback-only.

**[MAT-026]** The Matter logger shall be described as producing Matter-shaped
JSON and shall not be described as implementing Matter transport, discovery,
commissioning, fabrics, or certification.

**[MAT-027]** Sensor polling shall retry failed requests up to a configurable
number of retries (default 3) using exponential backoff before marking a
request failed.

**[MAT-028]** When a sensor request fails, the Matter logger shall serve cached
readings marked with status ``stale`` during an offline grace period (default 600
seconds).

**[MAT-029]** When a sensor exceeds the offline grace period without successful
responses, the Matter logger shall report status ``offline`` with ``airQuality``
cluster attributes set to 0 (``kUnknown``).

**[MAT-030]** When a previously failed sensor successfully responds to a poll,
the Matter logger shall restore status ``online`` and update the ``_last_seen``
timestamp.

**[MAT-031]** HTTP endpoints ``/matter/sensors`` and
``/matter/sensor/<sensor_index>`` shall expose ``_status`` and ``_last_seen``
metadata alongside device records.

**[MAT-032]** Offline or unreachable sensor events shall be logged at WARNING
level instead of ERROR level to avoid log spam for routine transient network
outages.

Continuous integration and deployment requirements
--------------------------------------------------

**[CICD-001]** Every GitHub Actions workflow shall configure a workflow-level concurrency group
named after the workflow file name (excluding the ``.yml`` extension).

**[CICD-002]** Every GitHub Actions workflow concurrency configuration shall set
``cancel-in-progress: true`` so that only one run of each workflow executes at a time.

**[CICD-003]** When new commits are pushed to an open pull request, any obsolete in-progress
workflow runs for that workflow shall be cancelled immediately.

**[CICD-004]** When new commits are pushed to the ``main`` branch, any obsolete in-progress
workflow runs for that workflow shall be cancelled immediately.

**[CICD-005]** The documentation build system shall execute in a dedicated Python 3.14 runner
environment (supporting dependencies requiring Python >=3.13, such as Sphinx 9.2+) for continuous
documentation and versioned release builds.

**[CICD-006]** Distribution packaging actions (``build-distribution``) shall execute under Python
3.14 to compile and validate sdist and wheel artifacts.

**[CICD-007]** CI workflow validation tooling (including workflow syntax validation via
``verify_syntax.yml``) shall configure and execute in a dedicated Python 3.14 runner environment.

**[CICD-008]** The package versioning and release automation shall follow SemVer-compliant
Calendar Versioning (CalSemVer) using ``YYYY.M.D`` for stable releases and ``YYYY.M.DaN`` for
pre-releases, omitting leading zeroes in date components to guarantee compatibility with PEP 440
and SemVer 2.0.0.

**[CICD-009]** Automated test workflows (``tests.yml``) shall generate Cobertura XML and coverage
reports across matrix runners and upload them to Codecov (``codecov/codecov-action``) using
repository secret ``CODECOV_TOKEN``, tagged with dedicated flag ``python`` and tracked via
component ``python_code``.

C++17 core engine & ``purpleair_api`` base layer requirements
-------------------------------------------------------------

**[CPP-001]** The high-performance core telemetry engine, RFC-8259 JSON configuration parser and
validator, bounded queue, storage sinks, and CLI dispatcher shall be implemented in portable
**ISO C++17** under ``include/purpleair_data_logger/`` and ``src/``.

**[CPP-002]** ``purpleair_data_logger`` shall integrate directly with the ``purpleair_api`` C++17
base layer (``PurpleAirAPI::PurpleAirAPI``, ``PurpleAirAPI::PurpleAirReadAPI``,
``PurpleAirAPI::PurpleAirWriteAPI``, ``PurpleAirAPI::PurpleAirLocalAPI``,
``PurpleAirAPI::PurpleAirAPIHelpers``, and ``PurpleAirAPI::PurpleAirAPIError``) to execute live
cloud single-sensor, multiple-sensor, sensor-history, group-sensor, and local-network HTTP/JSON
telemetry requests.

**[CPP-003]** ``PurpleAirPoller`` shall parse ``purpleair_api`` JSON responses into normalized,
typed ``Sample`` records preserving sensor index, field name (``oid``), value type, raw string
payload, and typed scalar value (``Int64``, ``Float64``, ``Str``, or ``Null``), capturing transport
or API exceptions as structured error ``Sample`` records without crashing polling worker threads.

**[CPP-004]** ``StubPurpleAirPoller`` shall provide deterministic synthetic PurpleAir air-quality
and environmental telemetry (including ``pm2.5_atm``, ``pm2.5_cf_1``, ``pm1.0_atm``, ``pm10.0_atm``,
``temperature``, ``humidity``, ``pressure``, ``voc``, ``rssi``, and ``uptime``) when ``mode`` is set
to ``"stub"`` for offline testing, demos, and CI validation.

**[CPP-005]** ``DataLogger`` shall decouple multi-sensor polling worker threads from sink
persistence using a thread-safe ``BoundedQueue<Batch>`` enforcing bounded memory under
back-pressure and draining queued batches prior to shutdown.

**[CPP-006]** The C++17 engine shall provide five native storage sinks: ``SqliteSink`` (embedded
SQLite3 WAL mode with normalized ``series`` and ``samples`` tables), ``CsvSink`` (per-target
RFC-4180 CSV), ``JsonlSink`` (per-target newline-delimited JSON), ``PsqlSink`` (PostgreSQL and
optional TimescaleDB hypertables via ``libpq``), and ``PrometheusSink`` (embedded HTTP ``/metrics``
endpoint supporting ephemeral port ``0`` binding).

**[CPP-007]** ``inspect_configured_sinks`` shall query recent stored telemetry rows across SQLite3,
JSONL, and CSV sinks with optional sensor target and metric filters.

Multi-language SWIG 4.x & self-contained packaging requirements
---------------------------------------------------------------

**[SWIG-001]** Modular SWIG 4.x interface files in ``interface/`` (``purpleair_data_logger.i``,
``exceptions.i``, ``datatypes.i``, ``config.i``, ``data_logger.i``) and
``tools/generate_swig_bindings.py`` shall generate and package bindings exclusively for the 4
supported target languages: ``python``, ``javascript`` (Node.js N-API), ``csharp`` (.NET 8+
P/Invoke), and ``go`` (cgo).

**[SWIG-002]** In Python bindings, blocking C++ operations (``run``, ``run_once``, ``stop``,
``probe``, ``request_json``, ``set_json``, ``CliRunner::run``, ``CliRunner::execute``) shall release
Python's GIL via ``%thread``.

**[PKG-001]** ``tools/prepare_sqlite3_amalgamation.py`` shall provision a SHA-256-verified SQLite3 C
amalgamation (``third_party/sqlite3/sqlite3.c`` and ``sqlite3.h``) compiled directly into the
native library, and ``tools/prepare_purpleair_api_source.py`` shall locate or provision the
``purpleair_api`` C++17 source tree (``third_party/purpleair_api`` or sibling checkout).

**[PKG-002]** ``tools/package_desktop_app.py`` shall package standalone desktop distributions named
``PurpleAirDataLogger`` across Linux (``.deb``, ``.rpm``, ``.tar.gz``), macOS
(``PurpleAirDataLogger.app``, ``PurpleAirDataLogger-macOS-<arch>.dmg``), and Windows
(``PurpleAirDataLogger-Windows-x64.exe``, ``PurpleAirDataLogger-Windows-x64-Setup.exe``).

Unified CLI & cross-platform Studio GUI requirements
----------------------------------------------------

**[UCLI-001]** The ``purpleair-data-logger`` CLI shall provide ``run``, ``validate``, ``probe``,
``request``, ``set``, ``inspect``, ``init-config``, ``gui``, ``schema``, ``version``, and ``help``
subcommands with ``--json`` machine-readable output support, while preserving all existing
``python -m purpleair_data_logger.<ModuleName>`` entry points.

**[GUI-001]** Both Cross-Platform Graphical User Interfaces — Native Desktop Studio
(``tkinter.ttk``) and Browser Web Studio (``http.server.ThreadingHTTPServer`` + HTML5/SVG) — shall
act strictly as frontends driving the ``purpleair-data-logger`` CLI via ``CliSubprocessBridge``,
featuring live telemetry charting, ad-hoc sensor diagnostics, sink data inspection, JSON
configuration editing, a live CLI Command Audit Trail, ``LocaleManager`` internationalization
(``purpleair_data_logger/gui/locale.json``), and custom branding icon assets.


