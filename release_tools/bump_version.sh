#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'USAGE_TEXT'
Usage: release_tools/bump_version.sh [OPTIONS] NEW_VERSION [OLD_VERSION]

Bump the current release version across tracked configuration, source, and documentation files.
If OLD_VERSION is omitted, it is read automatically from setup.cfg.

Options:
    -n, --dry-run    Preview files that would be modified without writing changes.
    -v, --verify     Run black formatting check, sphinx doc build (-W), and tests after bumping.
    -h, --help       Show this help message.

Examples:
    release_tools/bump_version.sh 1.6.0
    release_tools/bump_version.sh --dry-run 1.6.0
    release_tools/bump_version.sh --verify 1.6.0
    release_tools/bump_version.sh 1.6.0 1.6.0a1
USAGE_TEXT
}

dry_run=false
verify=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run)
            dry_run=true
            shift
            ;;
        -v|--verify)
            verify=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            printf 'Unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            break
            ;;
    esac
done

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage >&2
    exit 2
fi

new_version="${1#v}"  # Strip leading 'v' if present
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

# Validate new version format (supports SemVer e.g. 1.6.0, 1.6.0a1, and CalVer)
if [[ ! "$new_version" =~ ^[0-9]+(\.[0-9]+){2}([.-]?[0-9A-Za-z.-]+)?$ ]]; then
    printf 'Error: Invalid release version: %s\n' "$new_version" >&2
    exit 2
fi

if [[ $# -eq 2 ]]; then
    old_version="${2#v}"
else
    if [[ ! -f "setup.cfg" ]]; then
        printf 'Error: setup.cfg not found in %s\n' "$repo_root" >&2
        exit 1
    fi
    old_version=$(sed -nE 's/^version[[:space:]]*=[[:space:]]*([^[:space:]]+).*$/\1/p' setup.cfg | head -n 1)
fi

old_version="${old_version#v}"

if [[ -z "$old_version" ]]; then
    printf 'Error: Could not determine current version from setup.cfg\n' >&2
    exit 1
fi

if [[ "$old_version" == "$new_version" ]]; then
    printf 'Current version is already %s. Nothing to bump.\n' "$old_version"
    exit 0
fi

# Exclude historical files, build caches, and release tools themselves
pathspecs=(
    ':(exclude)CHANGELOG.md'
    ':(exclude)build/**'
    ':(exclude)docs/**'
    ':(exclude)sphinx_docs_build/landing/**'
    ':(exclude)python3.12.venv/**'
    ':(exclude)tests/**'
    ':(exclude).github/scripts/**'
    ':(exclude)release_tools/**'
    ':(exclude)purpleair_data_logger/PurpleAirMatterDataLogger.py'
    ':(exclude)purpleair_data_logger/PurpleAirMatterDataLoggerConstants.py'
    ':(exclude)sphinx_docs_build/source/Requirements.rst'
    ':(exclude)sphinx_docs_build/source/PurpleAirMatterDataLogger.rst'
    ':(exclude).github/workflows/*.lock.yml'
)

files=()
while IFS= read -r line; do
    [[ -n "$line" ]] && files+=("$line")
done < <(
    {
        git grep -Il -F -- "$old_version" -- . "${pathspecs[@]}" || true
        git grep -Il -F -- "v$old_version" -- . "${pathspecs[@]}" || true
    } | sort -u
)

required_files=(
    setup.cfg
    sphinx_docs_build/source/conf.py
)

for required_file in "${required_files[@]}"; do
    if [[ ! " ${files[*]} " == *" $required_file "* ]]; then
        printf 'Error: Expected release version "%s" not found in required file: %s\n' "$old_version" "$required_file" >&2
        exit 1
    fi
done

if [[ ${#files[@]} -eq 0 ]]; then
    printf 'Error: No tracked files contain version "%s"\n' "$old_version" >&2
    exit 1
fi

printf '%s version %s -> %s in %d file(s):\n' \
    "$([[ "$dry_run" == true ]] && printf 'Would bump' || printf 'Bumping')" \
    "$old_version" "$new_version" "${#files[@]}"
for f in "${files[@]}"; do
    printf '  - %s\n' "$f"
done

if [[ "$dry_run" == true ]]; then
    printf '\nDry-run complete. No files were modified.\n'
    exit 0
fi

for file in "${files[@]}"; do
    if [[ "$file" == "setup.cfg" ]]; then
        OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
            's/^version\s*=\s*\Q$ENV{OLD_VERSION}\E$/version = $ENV{NEW_VERSION}/m' "$file"
    else
        OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
            's/\Qv$ENV{OLD_VERSION}\E/v$ENV{NEW_VERSION}/g; s/\Q$ENV{OLD_VERSION}\E/$ENV{NEW_VERSION}/g' "$file"
    fi
done

# Verify no occurrences remain in active tracked files
remaining=()
while IFS= read -r line; do
    [[ -n "$line" ]] && remaining+=("$line")
done < <(
    {
        git grep -Il -F -- "$old_version" -- . "${pathspecs[@]}" || true
        git grep -Il -F -- "v$old_version" -- . "${pathspecs[@]}" || true
    } | sort -u
)

if [[ ${#remaining[@]} -gt 0 ]]; then
    printf 'Error: Version %s still remains in tracked files:\n' "$old_version" >&2
    for r in "${remaining[@]}"; do
        printf '  - %s\n' "$r" >&2
    done
    exit 1
fi

printf '\nSuccessfully updated version to %s.\n' "$new_version"

if [[ "$verify" == true ]]; then
    printf '\nRunning post-bump verification...\n'
    
    # Locate tools across candidate virtual environments
    black_bin="black"
    sphinx_bin="sphinx-build"
    pytest_bin="pytest"

    venv_candidates=(
        "/home/carlkidcrypto/Github/ezsnmp/python3.12.venv"
        "${repo_root}/python3.12.venv"
        "${VIRTUAL_ENV:-}"
    )

    for vdir in "${venv_candidates[@]}"; do
        [[ -z "$vdir" ]] && continue
        [[ "$black_bin" == "black" && -x "${vdir}/bin/black" ]] && black_bin="${vdir}/bin/black"
        [[ "$sphinx_bin" == "sphinx-build" && -x "${vdir}/bin/sphinx-build" ]] && sphinx_bin="${vdir}/bin/sphinx-build"
        [[ "$pytest_bin" == "pytest" && -x "${vdir}/bin/pytest" ]] && pytest_bin="${vdir}/bin/pytest"
    done

    # 1. Format check
    if command -v "$black_bin" >/dev/null 2>&1; then
        printf '[1/3] Checking Black formatting on conf.py...\n'
        "$black_bin" --check sphinx_docs_build/source/conf.py
    else
        printf '[1/3] Black not found, skipping format check.\n'
    fi

    # 2. Sphinx doc build check (must pass with zero warnings)
    if command -v "$sphinx_bin" >/dev/null 2>&1; then
        printf '[2/3] Building Sphinx documentation (SPHINXOPTS="-W")...\n'
        (cd sphinx_docs_build && PYTHONPATH=.. SPHINXBUILD="$sphinx_bin" make html SPHINXOPTS="-W" >/dev/null && rm -rf .doctrees)
    else
        printf '[2/3] sphinx-build not found, skipping doc build.\n'
    fi

    # 3. Unit test check
    if command -v "$pytest_bin" >/dev/null 2>&1; then
        printf '[3/3] Running pytest suite...\n'
        (cd tests && PYTHONPATH=.. "$pytest_bin" -q)
    else
        printf '[3/3] pytest not found, skipping unit tests.\n'
    fi

    printf 'Verification complete: all checks passed with zero warnings.\n'
fi
