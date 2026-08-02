# matterbridge-purpleair

Matterbridge DynamicPlatform plugin that turns the JSON from
`PurpleAirMatterDataLogger` into commissionable Matter Air Quality Sensor
endpoints.

## Requirements

- Node.js 20.19, 22.13, 24, or 26
- A globally installed Matterbridge 3.10 or newer, linked into this package for
  development
- A running PurpleAir Matter feed, normally
  `http://127.0.0.1:9855/matter/sensors`
- LAN IPv6 and mDNS connectivity for Matter commissioning

Normative behavior is specified in [Requirements.rst](Requirements.rst).

## Development

Run commands from this directory in WSL:

```bash
npm install --global --prefix "$HOME/.local" matterbridge@3.10.3
npm install
npm_config_prefix="$HOME/.local" npm run dev:link
npm run typecheck
npm test
npm run build
npm run lint
npm run format:check
```

Matterbridge must remain an unsaved link, not a package dependency. This
preserves the single matter.js instance required by Matterbridge.

Start the Python data source from the repository root:

```bash
python3.12.venv/bin/python -m purpleair_data_logger.PurpleAirMatterDataLogger \
  -paa_local_sensor_request_json_file \
  sample_json_config_files/sample_local_sensor_request_json_file.json \
  --matter-only
```

Install the local plugin and start Matterbridge:

```bash
"$HOME/.local/bin/matterbridge" --add .
"$HOME/.local/bin/matterbridge" --bridge
```

Matterbridge serves its frontend at `http://localhost:8283` by default. Use the
frontend or console commissioning code to add the bridge to a Matter fabric.

## Configuration

`feedUrl`
: Full URL of the all-sensors endpoint. Default:
  `http://127.0.0.1:9855/matter/sensors`.

`pollIntervalSeconds`
: Seconds between polls. Default: `60`.

`requestTimeoutSeconds`
: HTTP timeout in seconds. Default: `10`.

`whiteList` / `blackList`
: Matterbridge device filters populated from discovered sensor names and stable
  `purpleair-<sensor_index>` serial numbers.

`unregisterOnShutdown`
: Development option that removes endpoints at shutdown. Keep `false` in normal
  use to preserve endpoint identity.

The plugin retains registered endpoints and their last values across transient
HTTP or payload failures. Sensors are not removed merely because one response
omits them.