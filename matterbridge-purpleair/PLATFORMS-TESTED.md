# Platforms tested

This document tracks Matter controller platforms tested with
`matterbridge-purpleair`. A successful result applies only to the environment
tested and does not guarantee compatibility with every platform version or
network configuration.

## Status definitions

- **Worked**: Commissioning and basic use completed successfully.
- **In progress**: Testing started, but end-to-end operation is not yet
  confirmed.
- **Not tested**: No result has been recorded.

## Compatibility matrix

| Platform            | Status      | Notes                                                                                                                  |
| ------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| Google Home         | Worked      | Commissioning succeeded. Detailed environment and entity behavior will be documented later.                            |
| Home Assistant      | In progress | Matterbridge commissioning reached an Android Local Fabric, but the Home Assistant handoff has not yet been confirmed. |
| Apple Home          | Not tested  |                                                                                                                        |
| Amazon Alexa        | Not tested  |                                                                                                                        |
| Samsung SmartThings | Not tested  |                                                                                                                        |

## Details to record

When adding a test result, include when available:

- Controller application and version
- Controller or hub hardware
- Mobile operating system and version
- Matterbridge and plugin versions
- Network topology
- Commissioning result
- PurpleAir endpoints and attributes exposed by the controller
- Known limitations or required workarounds
