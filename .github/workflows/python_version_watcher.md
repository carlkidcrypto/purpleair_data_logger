---
name: Python Version Watcher

on:
  schedule:
    - cron: "0 9 1 * *"
  workflow_dispatch:
  skip-if-match:
    query: "is:pr is:open head:automation/python-version-watcher label:automated-pr"

permissions:
  actions: read
  contents: read

safe-outputs:
  create-pull-request:
    title-prefix: "[python-version]"
    labels:
      - automated-pr
    draft: true
    preserve-branch-name: true
    if-no-changes: ignore

timeout-minutes: 45

network: defaults

tools:
  edit:
  bash: true

engine:
  id: copilot
  model: auto
---

## Python Version Watcher and Auto-Sync

Monitor https://devguide.python.org/versions/ for changes to the set of actively supported Python
versions and automatically update the repository to stay in sync.

## Goals

- Detect which Python versions are currently supported (status = "bugfix", "security", or
  "prerelease") vs. end-of-life (status = "end-of-life").
- Update `setup.cfg` (`python_requires` range and `[tool:black]` `target-version` list) to reflect
  the current supported set.
- Update `.github/workflows/tests.yml` (`python-version` matrix list) to reflect the current
  supported set.
- Open a PR only when changes are actually needed.

## Steps

### 1. Fetch the Python versions page

```bash
curl -s --max-time 30 "https://devguide.python.org/versions/" -o /tmp/python_versions.html
```

If the fetch fails (non-zero exit, empty file, or the file contains fewer than 500 bytes — the
actual page is tens of kilobytes, so anything smaller indicates a truncated or error response),
log the failure and stop cleanly without modifying any files or opening a PR.

### 2. Parse supported versions

Extract the Python version table from the HTML. Parse each row of the table to find entries where
the status column contains one of: `bugfix`, `security`, or `prerelease`. These are the three
statuses that indicate an actively maintained release. Explicitly exclude all other statuses:
`end-of-life` (no longer maintained), `feature` (pre-release development branch not yet in
bugfix/security phase), and any unrecognized status strings.

Use the following Python snippet (or equivalent logic) to extract the data:

```python
import re

with open("/tmp/python_versions.html", "r", encoding="utf-8", errors="replace") as f:
    html = f.read()

# Find table rows; each row contains version number and status
# The devguide table uses <td> cells; version is typically like "3.12", status like "bugfix"
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)

SUPPORTED_STATUSES = {"bugfix", "security", "prerelease"}
supported = []

for row in rows:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL | re.IGNORECASE)
    if len(cells) < 2:
        continue
    # Strip HTML tags from cell text
    def strip_tags(s):
        return re.sub(r"<[^>]+>", "", s).strip()
    version_text = strip_tags(cells[0])
    # Version must look like "3.X"
    if not re.match(r"^3\.\d+$", version_text):
        continue
    # Status is typically in the second or third cell; use word-boundary regex to avoid
    # false positives (e.g., "insecurity" matching "security", or "prebugfix" matching "bugfix")
    all_cell_text = " ".join(strip_tags(c).lower() for c in cells)
    matched_status = next(
        (s for s in SUPPORTED_STATUSES if re.search(r"\b" + re.escape(s) + r"\b", all_cell_text)),
        None,
    )
    if matched_status:
        supported.append(version_text)

supported = sorted(supported, key=lambda v: tuple(int(x) for x in v.split(".")))
print("Supported versions:", supported)
```

If no supported versions are found (empty list), something went wrong with parsing — log the error
and stop without modifying any files.

### 3. Compare with current repo state

Read `setup.cfg` to find the current `python_requires` range and the `target-version` list under
`[tool:black]`. Read `.github/workflows/tests.yml` to find the current `python-version` matrix
list.

Extract the set of versions currently tracked in the repo. Compare it to the supported set obtained
in step 2.

- **Versions to add**: in the supported set but not currently tracked.
- **Versions to remove**: currently tracked but not in the supported set (i.e., end-of-life).

If both sets are empty (no additions and no removals), log "No Python version changes needed." and
stop cleanly without modifying any files or opening a PR.

### 4. Update `setup.cfg`

Compute the new values:

- **`python_requires`**: `>=<min_version>,<3.<max_minor + 1>` where `min_version` is the lowest
  version in the supported set and `max_minor` is the highest minor version number in the supported
  set (e.g., if highest supported is `3.14`, the upper bound is `3.15`).
- **`target-version`**: a Python list of strings in `['pyXY', ...]` format, one entry per
  supported version (e.g., `3.10` → `'py310'`), sorted ascending.

Edit `setup.cfg` in-place:

1. Replace the `python_requires = ...` line with the new computed value.
2. Replace the `target-version = [...]` line (under `[tool:black]`) with the new computed list.

### 5. Update `.github/workflows/tests.yml`

Edit `.github/workflows/tests.yml` in-place:

- Find the `python-version:` matrix line that looks like:
  `python-version: ['3.10', '3.11', ...]`
- Replace it with the new list of supported versions in the same format, sorted ascending:
  `python-version: ['X.Y', ...]`

### 6. Format Python files with Black

After editing `setup.cfg` and the workflow file, run Black on the Python source to keep formatting
consistent:

```bash
python3 -m pip install --quiet black
python3 -m black purpleair_data_logger/ --line-length 100
```

### 7. Open a pull request

Create or update a PR with the following details:

- **Branch**: `automation/python-version-watcher`
- **Base**: `main`
- **Title**: `[python-version] Sync supported Python versions <YYYY-MM-DD>` (use today's UTC date)
- **Commit message**: `chore: sync supported Python versions <YYYY-MM-DD>`

PR body must include:

- Date the Python versions page was fetched (UTC).
- List of Python versions **added** (newly supported).
- List of Python versions **removed** (now end-of-life).
- Files changed: `setup.cfg`, `.github/workflows/tests.yml`.
- The new `python_requires` value.
- The new `target-version` list.
- The new `python-version` matrix.
- A link to https://devguide.python.org/versions/ for reference.

## Constraints

- Only modify `setup.cfg` and `.github/workflows/tests.yml`.
- Do not open a PR if no changes are needed.
- If the Python versions page is unreachable or returns an error, stop without modifying any files.
- If parsing yields an empty or implausible supported version list (fewer than 3 versions), stop
  and log the issue without modifying files. Python typically maintains at least 3 supported
  versions simultaneously, so fewer than 3 results strongly suggests a parsing failure.
- Keep all Python code Black-formatted with line length 100.
