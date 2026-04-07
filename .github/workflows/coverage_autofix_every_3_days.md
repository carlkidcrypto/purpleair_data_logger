---
name: Coverage Autofix Every 3 Days
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-every-3-days label:automated-pr'
permissions:
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[coverage-autofix] "
    labels: [automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
  add-labels:
    target: "*"
    allowed: [coverage, tests, python]
    max: 3
timeout-minutes: 45
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, python]
tools:
  edit:
  bash: true
---

# Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for Python tests, then propose and
implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk.
- Prefer tests first when improving coverage.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-every-3-days`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Prepare Python dependencies and run tests with coverage:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r tests/requirements.txt`
   - `python -m pip install coverage requests_mock purpleair_api`
   - `cd tests && coverage run -m unittest`
   - `coverage xml -o coverage.xml`
   - `coverage report`
   - Read coverage from `coverage.xml` when available.

2. Evaluate coverage results:
   - Parse `coverage.xml` to determine overall line and branch coverage percentages.
   - Identify specific uncovered lines or branches in `purpleair_data_logger/*.py`.
   - Note any test failures or errors encountered during the run.

3. Determine if action is needed:
   - If Python coverage is below 90%, or tests reveal clear reliability gaps,
     create targeted fixes.
   - If current coverage looks healthy and no concrete improvement is justified,
     do not change code.

## Fix Strategy

- Prioritize:
  - Adding missing test coverage for uncovered branches/paths in
    `purpleair_data_logger/*.py`.
  - Fixing brittle or flaky tests in `tests/`.
  - Small correctness fixes discovered while writing tests.
- Test files live in `tests/` (unittest style) and `behave_tests/` (BDD style).
- Add new tests to `tests/test_purpleair_data_logger.py` or
  `tests/test_purpleair_data_logger_helpers.py` as appropriate.
- Use `requests_mock` for mocking HTTP calls to the PurpleAir API.
- Do not modify `behave_tests/` unless the fix is specifically for a behaviour
  described there.
- Avoid broad refactors or unrelated formatting churn.
- Keep commits coherent and reviewable.

## Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:

- Branch: `automation/coverage-autofix-every-3-days`
- Base: `main`
- Title style: `[coverage-autofix] <short summary>`
- PR body must include:
  - Python coverage before/after (if measurable)
  - Summary of tests added/updated
  - Any limitations or follow-up recommendations

After creating the PR, attempt a best-effort follow-up label step:

- Add supplemental labels to the created PR when possible: `coverage`, `tests`,
  `python`.
- Treat this as non-critical metadata enrichment. If supplemental labeling fails,
  do not treat the run as a primary failure and do not abandon the created PR.

If no changes are required, report that coverage checks passed without actionable
improvements.
