# Release Scripts

This directory contains release-maintenance scripts for PurpleAir Data Logger(s).

## `release.sh`

`release.sh` updates the package version in tracked source and current user-facing documentation. It does not create a commit, tag, GitHub release, or PyPI upload. Those steps remain explicit so the release can be reviewed before publishing.

### Requirements

Run it from a Git checkout with:

- Bash
- Git
- Perl
- `sed`

The script locates the repository root with `git rev-parse`, so it may be started from any directory inside the checkout.

### Usage

Preview the files that will change:

```bash
bash scripts/release.sh --dry-run 1.5.0 1.5.0a2
```

Apply the stable release bump:

```bash
bash scripts/release.sh 1.5.0 1.5.0a2
```

When the old version is omitted, it is read from `setup.cfg`:

```bash
bash scripts/release.sh 1.5.0
```

The script accepts stable versions such as `1.5.0` and prereleases such as `1.5.0a2`, `1.5.0b1`, and `1.5.0rc1`. The new version is supplied without a leading `v`; existing `v` prefixes in documentation are preserved.

### Files and validation

The script searches tracked text files for both the plain and `v`-prefixed old version, updates the matching active files, and requires the old version to be present in:

- `setup.cfg`
- `sphinx_docs_build/source/conf.py`

It deliberately excludes:

- `CHANGELOG.md`, which records release history
- Generated HTML under `docs/html/` and `docs/html_v*/`
- Sphinx doctrees under `docs/doctrees/`
- `build/`
- The local `python3.12.venv/`
- Generated workflow lock files under `.github/workflows/`

After an actual bump, it checks that no old-version references remain in the active tracked scope. If the requested version is already current, it exits without changes.

### Release checklist

For the `1.5.0a2` to `1.5.0` release:

1. Run `bash scripts/release.sh --dry-run 1.5.0 1.5.0a2` and review the selected files.
2. Run `bash scripts/release.sh 1.5.0 1.5.0a2`.
3. Update `CHANGELOG.md` with the stable release notes and date.
4. Run the test suite from `tests/`.
5. Build and verify the Sphinx documentation.
6. Review the complete diff and commit the release preparation changes.
7. Create and push the release tag, for example `v1.5.0`.
8. Publish the GitHub release and verify the PyPI and GitHub Pages workflows.
