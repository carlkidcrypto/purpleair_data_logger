PurpleAirMatterDataLogger module
================================

Overview
--------

``PurpleAirMatterDataLogger`` converts PurpleAir sensor readings to JSON shaped
like a Matter 1.5.1 Air Quality Sensor device type (``0x002D``). The conversion
is provided by ``purpleair_api.PurpleAirMatterConverter``. This logger does not
implement Matter transport, discovery, commissioning, fabrics, or certification.

Continuous HTTP service
-----------------------

The command-line interface polls configured sensors, retains the latest
successful reading for each sensor, and serves the converted devices over HTTP.
The default bind address is ``127.0.0.1:9855``.

Cloud sensors require a PurpleAir Read API key and a configuration containing
``sensor_indexes``::

   python3 -m purpleair_data_logger.PurpleAirMatterDataLogger \
       -paa_read_key YOUR_READ_KEY \
       -paa_multiple_sensor_request_json_file \
       ./sample_json_config_files/sample_matter_request_json_file.json \
       --matter-only

Local-network sensors use a configuration containing ``sensor_ip_list`` and do
not require a cloud API key::

   python3 -m purpleair_data_logger.PurpleAirMatterDataLogger \
       -paa_local_sensor_request_json_file \
       ./sample_json_config_files/sample_local_sensor_request_json_file.json \
       --matter-only

Only one JSON configuration file may be supplied. The logger clamps polling
intervals below 60 seconds to 60 seconds. An individual cloud polling failure is
isolated so other configured sensors continue updating, and the HTTP API retains
the failed sensor's last-known-good value.

One-shot conversion
-------------------

Call :meth:`PurpleAirMatterDataLogger.run_once` to convert cloud sensor readings
without starting the HTTP server or polling loop::

   from purpleair_data_logger.PurpleAirMatterDataLogger import (
       PurpleAirMatterDataLogger,
   )

   matter_logger = PurpleAirMatterDataLogger(
       PurpleAirApiReadKey="YOUR_READ_KEY",
   )
   devices = matter_logger.run_once([123456])

Configuration
-------------

Continuous cloud mode recognizes these fields:

``sensor_indexes``
   Required list of integer PurpleAir sensor indexes.

``sensor_names``
   Optional object mapping sensor indexes to display-name overrides. JSON object
   keys are strings and are converted to integers while loading.

``read_keys``
   Optional object mapping private sensor indexes to sensor Read keys.

``poll_interval_seconds``
   Poll delay. Values below 60 are clamped to 60.

``http_host`` and ``http_port``
   HTTP bind address and port. Defaults are ``127.0.0.1`` and ``9855``.

``matter_only``
   Describes the Matter-only service mode. The current class has no raw-data
   persistence sink, so this option does not change persistence behavior.

Continuous local mode requires ``sensor_ip_list`` and accepts the same polling
and HTTP fields. Group configuration is not supported because ``group_id`` is
not resolved into sensor indexes. The standard single-sensor sample uses
``sensor_index`` rather than the required ``sensor_indexes`` list and therefore
cannot be used unchanged.

HTTP API
--------

``GET /`` or ``GET /health``
   Returns ``{"status": "ok", "sensor_count": N}``.

``GET /matter/sensors``
   Returns all current devices and their sensor indexes, plus a ``count``.

``GET /matter/sensor/<sensor_index>``
   Returns one device. A non-integer index returns 400 and an unavailable index
   returns 404. Query parameters do not affect route matching.

Security
--------

The HTTP service does not provide authentication or TLS. Keep the default
loopback bind unless another trusted network layer protects access. Binding to
``0.0.0.0`` exposes the service to reachable networks.

Python API
----------

.. automodule:: PurpleAirMatterDataLogger
   :members:
   :undoc-members:
   :show-inheritance: