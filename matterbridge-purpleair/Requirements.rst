matterbridge-purpleair requirements
===================================

Scope
-----

These requirements define the behavior of the ``matterbridge-purpleair``
companion plugin. ``SHALL`` and ``SHALL NOT`` are normative.

Runtime and configuration
-------------------------

MBPA-001
   The plugin SHALL implement a Matterbridge ``DynamicPlatform``.

MBPA-002
   The plugin SHALL require Matterbridge 3.10.0 or newer and a Node.js version
   supported by that Matterbridge release.

MBPA-003
   The plugin SHALL accept an HTTP or HTTPS ``feedUrl`` whose default is
   ``http://127.0.0.1:9855/matter/sensors``.

MBPA-004
   The plugin SHALL accept positive integer polling and request-timeout values.

MBPA-005
   The plugin SHALL expose its settings through a Matterbridge configuration
   file and JSON schema.

MBPA-006
   The package SHALL NOT declare Matterbridge or ``@matter`` packages as
   dependencies, development dependencies, or peer dependencies. Development
   SHALL use ``npm link matterbridge --no-save`` so runtime and plugin code
   share one matter.js instance without modifying ``package.json``.

Feed handling
-------------

MBPA-010
   The plugin SHALL request the feed once at startup and periodically
   thereafter.

MBPA-011
   The plugin SHALL reject a non-object response or a response without a
   ``sensors`` array.

MBPA-012
   The plugin SHALL validate each sensor independently so that one malformed
   sensor does not suppress valid sensors in the same response.

MBPA-013
   A sensor SHALL have a unique, non-negative, safely representable integer
   ``sensor_index``.

MBPA-014
   The Air Quality value SHALL be an integer in the Matter enumeration range
   zero through six.

MBPA-015
   The plugin SHALL prefer the feed's unscaled ``_raw`` concentration values
   and SHALL divide the legacy density attributes by 100 only as a fallback.

MBPA-016
   The plugin SHALL abort an HTTP request after the configured timeout and
   SHALL report non-success HTTP responses.

Matter endpoint behavior
------------------------

MBPA-020
   The plugin SHALL expose one Matter Air Quality Sensor endpoint for each
   accepted ``sensor_index`` using Matterbridge's canonical device definition.

MBPA-021
   The stable endpoint ID and serial number SHALL be
   ``purpleair-<sensor_index>`` and SHALL NOT depend on sensor order or the
   feed's descriptive ``device.endpoint`` value.

MBPA-022
   The plugin SHALL expose Air Quality, Temperature Measurement, Relative
   Humidity Measurement, Pressure Measurement, PM1, PM2.5, and PM10 clusters.

MBPA-023
   The plugin SHALL expose Total VOC concentration when the source supplies a
   VOC value.

MBPA-024
   Subsequent readings for a known sensor SHALL update the registered endpoint
   in place instead of replacing its identity.

MBPA-025
   Matterbridge SHALL allocate and persist numeric endpoint assignments from
   the plugin's stable endpoint IDs.

MBPA-026
   When a source sensor name is a MAC address, the plugin SHALL expose its
   device name as ``purple-air-<last-three-MAC-octets>`` using lowercase,
   hyphen-separated octets. The plugin SHALL preserve source sensor names that
   are not MAC addresses.

Resilience and lifecycle
------------------------

MBPA-030
   Polls SHALL NOT overlap.

MBPA-031
   An HTTP, JSON, or individual sensor error SHALL leave previously published
   Matter attributes unchanged.

MBPA-032
   The plugin SHALL NOT remove a registered sensor solely because a later feed
   response omits it.

MBPA-033
   The plugin SHALL stop its polling timer during shutdown.

MBPA-034
   The plugin SHALL unregister devices during shutdown only when
   ``unregisterOnShutdown`` is explicitly enabled.

Verification
------------

MBPA-040
   The package SHALL provide automated tests for feed normalization, malformed
   sensor isolation, stable identity, Matter cluster composition, and in-place
   attribute updates.

MBPA-041
   The package SHALL pass TypeScript type checking, production build, unit
   tests, linting, and formatting checks before release.