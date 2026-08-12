---
name: Matter Data Logger Standards Watcher
description: Monitor Matter standards releases and propose synchronized Matter data logger, test, and documentation updates.
on:
  schedule:
    - cron: "0 9 1 * *"
  workflow_dispatch:
  skip-if-match:
    query: "is:pr is:open head:automation/matter-data-logger-standards-watcher label:automated-pr"

permissions:
  actions: read
  contents: read
  copilot-requests: write

safe-outputs:
  create-pull-request:
    title-prefix: "[matter-data-logger]"
    labels:
      - automated-pr
    draft: true
    preserve-branch-name: true
    if-no-changes: ignore
    allowed-files:
      - purpleair_data_logger/PurpleAirMatterDataLogger.py
      - purpleair_data_logger/PurpleAirMatterDataLoggerConstants.py
      - tests/test_purpleair_matter_data_logger.py
      - README.md
      - docs/**
      - sphinx_docs_build/source/**

# Matter standards research should have enough time for authoritative source checks and tests.
timeout-minutes: 45

network:
  allowed:
    - csa-iot.org
    - www.csa-iot.org
    - github
    - python

tools:
  edit:
  bash: true

model: claude-sonnet-5
engine:
  id: copilot
---

## Matter Data Logger Standards Watcher

Monitor the Connectivity Standards Alliance Matter specifications and keep this repository's
PurpleAir Matter data logger synchronized with published standards that affect its exposed device
JSON and HTTP interface. The repository currently documents Matter 1.5.1 as its baseline.

The data logger delegates sensor-to-Matter conversion to `purpleair_api.PurpleAirMatterConverter`.
This watcher owns the data logger's integration, HTTP representation, tests, and documentation. If
a required converter change belongs in `purpleair_api`, describe that compatibility requirement in
the PR and do not implement unrelated API changes in this repository.

## Authoritative sources

- CSA specifications index: https://csa-iot.org/developer-resource/specifications/
- Matter specification documents and release notes linked from that index
- The Matter device library and cluster definitions in the published specification
- https://github.com/project-chip/matter.js as a secondary implementation reference only; never
  treat it as authoritative when it conflicts with the CSA specification
- The published `purpleair_api` package or repository only for confirming the converter interface,
  never as authority for the Matter standard itself

Do not infer a standards change from an unavailable page, a search-result snippet, or an
implementation library alone. If the CSA source cannot be fetched or the apparent change cannot be
verified against an authoritative Matter document, call `noop` without editing files or opening a
PR.

## Review scope

Inspect the current Matter version, device type IDs, cluster IDs, attribute IDs, enum values,
measurement units, scaling and encoding rules, required and optional cluster mappings, and source
references in:

- `purpleair_data_logger/PurpleAirMatterDataLogger.py`
- `purpleair_data_logger/PurpleAirMatterDataLoggerConstants.py`
- `tests/test_purpleair_matter_data_logger.py`
- `README.md`
- `docs/**` and `sphinx_docs_build/source/**`

Also verify that the logger's documented `purpleair_api` minimum version and the converter call
contract remain compatible. Do not change `tests/requirements.txt`; its `purpleair_api` pin is
maintained independently by Dependabot.

## Required steps

1. Fetch the CSA specifications index and identify the newest published Matter release or errata
   relevant to this data logger. Record the document title, version, publication date, and stable
   URL. Do not treat a draft or preview as current unless the source explicitly marks it published.
2. Compare the authoritative device-library and cluster definitions with the logger's emitted
   structures and documentation. Check identifiers, names, enum values, required or optional
   status, units, numeric ranges, scaling, encoding, and deprecations. Separate standards changes
   from documentation-only wording changes.
3. If no verified, actionable Matter change affects this logger, call `noop` with a concise
   explanation and the source checked. Do not edit files.
4. If a verified change exists, update the implementation and focused tests together. Preserve the
   public Python API and HTTP routes unless the standard requires a change. Do not add speculative,
   vendor-specific, or bridge-specific behavior.
5. Update affected user-facing documentation and references, including the documented Matter
   version and stable source links. Do not edit generated HTML or doctree artifacts under
   `docs/html/**` or `docs/doctrees/**`.
6. Run the focused Matter data logger tests first, then the relevant repository test command. If a
   failure is unrelated and pre-existing, report it in the PR body and do not make unrelated fixes.
7. Review the diff for accidental changes, stale Matter version references, inconsistent IDs or
   units, and documentation that claims support beyond what implementation and tests cover.
8. Create one draft pull request on branch `automation/matter-data-logger-standards-watcher`
   against `main` using the configured safe output. Include the authoritative source, old and new
   Matter versions, exact specification sections, each code/test/doc change, validation commands
   and results, and any remaining `purpleair_api` compatibility concern.

## Constraints

- Only modify files allowed by `safe-outputs.create-pull-request.allowed-files`.
- Do not modify generated documentation under `docs/html/**` or `docs/doctrees/**`.
- Do not remove existing mappings solely because a secondary implementation omits them.
- Do not modify `purpleair_api`, `tests/requirements.txt`, unrelated data logger behavior,
  dependencies, formatting, or release metadata.
- Keep the patch small and internally consistent: one standards update per PR.
- If the source is unavailable, ambiguous, or unchanged, use `noop` and leave the repository
  untouched.

## Safe output

Use `create-pull-request` only after a verified implementation or documentation change and
successful validation. Use `noop` when no verified change is needed, when the source cannot be
validated, or when an existing open watcher PR covers the same release.
