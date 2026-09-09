#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/release.sh [--dry-run] NEW_VERSION [OLD_VERSION]

Bump the release version in tracked source and current documentation files.
If OLD_VERSION is omitted, it is read from setup.cfg.
EOF
}

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
    dry_run=true
    shift
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage >&2
    exit 2
fi

new_version=$1
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

if [[ ! "$new_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([abrc][0-9]+)?$ ]]; then
    printf 'Invalid release version: %s\n' "$new_version" >&2
    exit 2
fi

if [[ $# -eq 2 ]]; then
    old_version=${2#v}
else
    old_version=$(sed -nE 's/^version[[:space:]]*=[[:space:]]*([^[:space:]]+).*$/\1/p' setup.cfg | head -n 1)
fi

old_version=${old_version#v}
if [[ -z "$old_version" ]]; then
    printf 'Could not determine the current version from setup.cfg\n' >&2
    exit 1
fi

if [[ ! "$old_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([abrc][0-9]+)?$ ]]; then
    printf 'Invalid current release version: %s\n' "$old_version" >&2
    exit 1
fi

if [[ "$old_version" == "$new_version" ]]; then
    printf 'New version is the same as the current version: %s\n' "$old_version"
    exit 0
fi

pathspecs=(
    ':(exclude)CHANGELOG.md'
    ':(exclude)build/**'
    ':(exclude)docs/html/**'
    ':(exclude)docs/html_v*/**'
    ':(exclude)docs/doctrees/**'
    ':(exclude)python3.12.venv/**'
    ':(exclude)tests/requirements.txt'
    ':(exclude).github/workflows/*.lock.yml'
)

version_files=()
while IFS= read -r file; do
    version_files+=("$file")
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
    if [[ ! " ${version_files[*]} " == *" $required_file "* ]]; then
        printf 'Expected release version %s in %s\n' "$old_version" "$required_file" >&2
        exit 1
    fi
done

if [[ ${#version_files[@]} -eq 0 ]]; then
    printf 'No tracked release files contain version %s\n' "$old_version" >&2
    exit 1
fi

printf '%s version %s -> %s in %d file(s):\n' \
    "$([[ "$dry_run" == true ]] && printf 'Would bump' || printf 'Bumping')" \
    "$old_version" "$new_version" "${#version_files[@]}"
printf '  %s\n' "${version_files[@]}"

if [[ "$dry_run" == true ]]; then
    exit 0
fi

OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
    's/\Qv$ENV{OLD_VERSION}\E/v$ENV{NEW_VERSION}/g; s/\Q$ENV{OLD_VERSION}\E/$ENV{NEW_VERSION}/g' \
    "${version_files[@]}"

remaining=()
while IFS= read -r file; do
    remaining+=("$file")
done < <(
    {
        git grep -Il -F -- "$old_version" -- . "${pathspecs[@]}" || true
        git grep -Il -F -- "v$old_version" -- . "${pathspecs[@]}" || true
    } | sort -u
)

if [[ ${#remaining[@]} -gt 0 ]]; then
    printf 'Version %s remains in active tracked files:\n' "$old_version" >&2
    printf '  %s\n' "${remaining[@]}" >&2
    exit 1
fi

printf 'Release version updated to %s.\n' "$new_version"
