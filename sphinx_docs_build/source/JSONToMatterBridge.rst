JSON to Matter bridge
=====================

Overview
--------

``PurpleAirMatterDataLogger`` publishes current PurpleAir readings as
Matter-shaped JSON. Google Home and Home Assistant cannot commission that HTTP
API directly because it does not implement Matter discovery, commissioning,
secure sessions, fabrics, or subscriptions.

A ``matterbridge-purpleair`` plugin provides the missing protocol boundary.
The plugin reads the logger's JSON API and registers each PurpleAir sensor as a
bridged Matter Air Quality Sensor. Matterbridge then provides the commissionable
Matter bridge, QR code, network discovery, security, and fabric storage.

The plugin is developed in the repository's ``matterbridge-purpleair``
directory. It is currently a local development package and is not published to
npm.

Architecture
------------

::

   PurpleAir sensors
           |
           v
   PurpleAirMatterDataLogger
   http://127.0.0.1:9855/matter/sensors
           |
           v
   matterbridge-purpleair plugin
   JSON parsing, endpoint identity, cluster updates
           |
           v
   Matterbridge / matter.js
   mDNS, commissioning, secure sessions, fabrics
           |
           +-------------------+
           |                   |
           v                   v
      Google Home        Home Assistant

Matterbridge is the Matter device in this design. The Python logger remains the
sensor-data source and does not become a Matter transport implementation.
``python-matter-server`` is a Matter controller and is not a replacement for the
bridge shown above.

Plugin responsibilities
-----------------------

The companion plugin:

* Accepts the logger base URL and polling interval as configuration.
* Reads ``GET /matter/sensors`` when it starts and on every polling cycle.
* Validates the top-level ``sensors`` list and each ``sensor_index`` and
  ``device`` object before applying updates.
* Assigns one stable bridged endpoint to each unique ``sensor_index``.
* Persists the ``sensor_index`` to endpoint mapping across restarts.
* Adds newly discovered sensors without changing existing endpoint identities.
* Retains the last-known-good Matter attributes when the HTTP request or one
  sensor payload fails.
* Updates Matter attributes only after a complete sensor payload has been
  validated.
* Reports connection and payload errors without terminating the bridge.
* Removes or disables a sensor only through explicit configuration, not because
  it is absent from one response.

The ``device.endpoint`` value in the JSON payload is descriptive and is ``1``
for each converted sensor. A bridge must not reuse that value for every child.
Matterbridge must allocate a distinct and stable endpoint for each PurpleAir
``sensor_index``.

Matter data mapping
-------------------

The current HTTP payload has this shape::

   {
     "sensors": [
       {
         "sensor_index": 123456,
         "device": {
           "device_type": {"id": 45, "label": "Air Quality Sensor"},
           "sensor_name": "Example sensor",
           "clusters": {
             "air_quality_measurement": {"attributes": {}},
             "temperature_measurement": {"attributes": {}},
             "humidity_measurement": {"attributes": {}},
             "pressure_measurement": {"attributes": {}}
           }
         }
       }
     ],
     "count": 1
   }

The plugin must map the JSON values into Matterbridge cluster APIs. It must not
publish the entire JSON object as if every JSON property were a standard Matter
attribute.

.. list-table:: Required mapping
   :header-rows: 1
   :widths: 34 30 36

   * - JSON source
     - Matter representation
     - Notes
   * - ``device.device_type.id``
     - Air Quality Sensor ``0x002C``
     - The legacy converter currently emits decimal ``45``. The plugin uses
       Matterbridge's canonical Matter 1.6 device definition instead.
   * - ``air_quality_measurement.attributes.airQuality``
     - Air Quality cluster
     - Use the Matter enumeration value supplied by the converter.
   * - PM1, PM2.5, and PM10 density values
     - Corresponding concentration measurement clusters
     - Use distinct standard clusters rather than custom Air Quality attributes.
   * - VOC density
     - Total VOC concentration measurement cluster
     - Omit the cluster when the source value is unavailable.
   * - ``temperature_measurement.attributes.measuredValue``
     - Temperature Measurement cluster
     - The JSON value is in hundredths of a degree Celsius.
   * - ``humidity_measurement.attributes.measuredValue``
     - Relative Humidity Measurement cluster
     - The JSON value is in hundredths of a percent.
   * - ``pressure_measurement.attributes.measuredValue``
     - Pressure Measurement cluster
     - Pass the converted integer using the units expected by matter.js.
   * - ``device.sensor_name``
     - Bridged Basic Information
     - Use as the user-visible product or node label.
   * - ``device.firmware_version`` and ``device.hardware_model``
     - Bridged Basic Information
     - Publish only where the Matterbridge API supports the fields.

The plugin should use matter.js or Matterbridge types for range checking and
attribute encoding. It should not duplicate Matter unit conversion rules with
untyped JSON manipulation.

Companion project
-----------------

The companion is maintained in a subdirectory at the repository root::

   matterbridge-purpleair/
     package.json
     Requirements.rst
     tsconfig.json
     src/
       module.ts
       purpleair-client.ts
       purpleair-endpoint.ts
     vitest/

The implementation follows the official Matterbridge plugin template and uses
TypeScript, Vitest, oxlint, and oxfmt. See
``matterbridge-purpleair/Requirements.rst`` for its normative requirements.
Its main configuration fields are:

``feedUrl``
  Full PurpleAir Matter feed URL. Default:
  ``http://127.0.0.1:9855/matter/sensors``.

``pollIntervalSeconds``
   JSON polling interval. It should not be shorter than the Python logger's
   polling interval. Default: ``60``.

``requestTimeoutSeconds``
   HTTP request timeout. Default: ``10``.

``whiteList`` and ``blackList``
  Matterbridge device filters populated from discovered sensor names and
  stable serial numbers.

Running the data source
-----------------------

When Matterbridge runs on the same host, keep the safer loopback binding::

   python3 -m purpleair_data_logger.PurpleAirMatterDataLogger \
       -paa_local_sensor_request_json_file \
       ./sample_json_config_files/sample_local_sensor_request_json_file.json \
       --matter-only

The plugin can then use ``http://127.0.0.1:9855/matter/sensors``. If Matterbridge runs on a
separate trusted host, bind the logger to a LAN interface::

   python3 -m purpleair_data_logger.PurpleAirMatterDataLogger \
       -paa_local_sensor_request_json_file \
       ./sample_json_config_files/sample_local_sensor_request_json_file.json \
       --http-host 0.0.0.0 \
       --matter-only

The HTTP API has no authentication or TLS. Restrict port ``9855`` to the bridge
host with a firewall and do not expose it to the internet.

Installing and pairing
----------------------

The local development flow from ``matterbridge-purpleair`` is::

  npm install --global --prefix "$HOME/.local" matterbridge@3.10.3
   npm install
  npm_config_prefix="$HOME/.local" npm link matterbridge --no-save
   npm run build
   npm test
  "$HOME/.local/bin/matterbridge" --add .
  "$HOME/.local/bin/matterbridge" --bridge

Matterbridge provides its frontend on port ``8283`` by default and displays the
bridge QR code in the frontend and console.

Matterbridge is linked rather than declared as a package dependency. This is a
Matterbridge requirement that prevents a plugin from loading a second,
incompatible matter.js instance.

To pair with Home Assistant:

#. Install and configure Home Assistant's Matter integration.
#. In the Home Assistant companion app, choose **Settings > Matter > Add
   device**.
#. Scan the Matterbridge QR code or enter its numeric commissioning code.
#. Verify that every allowed PurpleAir sensor appears as a sensor device.

To pair with Google Home:

#. Ensure a compatible Google Matter hub is present in the home.
#. In Google Home, choose **Add > Device > Matter-enabled device**.
#. Scan the Matterbridge QR code.
#. Verify that each bridged PurpleAir Air Quality Sensor appears.

Matter supports multiple fabrics. After pairing the bridge with one ecosystem,
open a new commissioning window from that ecosystem or from Matterbridge and
use the generated sharing code to add the bridge to the second ecosystem.

Network requirements
--------------------

Matter commissioning and operation require local IPv6 and working mDNS
multicast between Matterbridge and the controllers. The internet connection does
not need IPv6, but the LAN does. Avoid firewall, VLAN, container, or virtual
machine settings that block IPv6 or multicast traffic.

This repository commonly runs under WSL. The Python HTTP service can run there,
but Matterbridge must run in an environment whose mDNS and IPv6 traffic reaches
the physical LAN. Native Linux, a correctly configured host-network container,
or a supported native Windows Matterbridge installation is generally easier to
diagnose than default WSL NAT networking.

Compatibility and certification
-------------------------------

Google Home lists the Matter Air Quality Sensor device type and Matter bridges
as supported. Controller user interfaces may still expose only a subset of the
available clusters or attributes. Home Assistant generally exposes a broader
set of sensor entities, but behavior depends on its current Matter Server and
Matter specification support.

Development and personal testing can use Matterbridge's development
commissioning credentials. A distributed commercial product requires the
applicable Connectivity Standards Alliance certification, device attestation,
and ecosystem integration testing. A working development QR code is not proof
of Matter certification.

Acceptance criteria
-------------------

The first usable plugin release should demonstrate all of the following:

* Matterbridge starts while the Python logger is serving two or more sensors.
* One stable Matter endpoint is created per ``sensor_index``.
* Temperature, humidity, pressure, air quality, and available concentration
  measurements update after subsequent JSON polls.
* A transient logger outage leaves the last-known-good values available.
* Restarting Matterbridge does not change endpoint identities.
* The bridge commissions successfully into Home Assistant.
* The same bridge can be added to Google Home through a second fabric.
* Neither controller requires direct access to port ``9855``.

References
----------

* `Matterbridge <https://github.com/Luligu/matterbridge>`_
* `Matterbridge plugin template <https://github.com/Luligu/matterbridge-plugin-template>`_
* `Google Home supported Matter devices <https://developers.home.google.com/matter/supported-devices>`_
* `Home Assistant Matter integration <https://www.home-assistant.io/integrations/matter/>`_
* :doc:`PurpleAirMatterDataLogger`
