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
    release_tools/bump_version.sh 2026.11.3
    release_tools/bump_version.sh --dry-run 2026.11.3
    release_tools/bump_version.sh --verify 2026.11.3
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

# Validate new version format (supports CalSemVer e.g. 2026.11.3, 2026.11.3a0, or SemVer)
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

to_semver() {
    local v="$1"
    if [[ "$v" =~ ^([0-9]+\.[0-9]+\.[0-9]+)a([0-9]+)$ ]]; then
        printf '%s-alpha.%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    elif [[ "$v" =~ ^([0-9]+\.[0-9]+\.[0-9]+)b([0-9]+)$ ]]; then
        printf '%s-beta.%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    elif [[ "$v" =~ ^([0-9]+\.[0-9]+\.[0-9]+)rc([0-9]+)$ ]]; then
        printf '%s-rc.%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    elif [[ "$v" =~ ^([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+)$ ]]; then
        printf '%s-%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    else
        printf '%s' "$v"
    fi
}

to_base_version() {
    local v="$1"
    if [[ "$v" =~ ^([0-9]+\.[0-9]+\.[0-9]+) ]]; then
        printf '%s' "${BASH_REMATCH[1]}"
    else
        printf '%s' "$v"
    fi
}

old_semver_npm=$(to_semver "$old_version")
new_semver_npm=$(to_semver "$new_version")
old_base=$(to_base_version "$old_version")
new_base=$(to_base_version "$new_version")

# Exclude historical files, build caches, external specs, and release tools themselves
pathspecs=(
    ':(exclude)CHANGELOG.md'
    ':(exclude)build/**'
    ':(exclude)docs/**'
    ':(exclude)sphinx_docs_build/landing/**'
    ':(exclude)python3.12.venv/**'
    ':(exclude)third_party/**'
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
        git grep -Il -F -- "$old_semver_npm" -- . "${pathspecs[@]}" || true
        git grep -Il -F -- "v$old_semver_npm" -- . "${pathspecs[@]}" || true
    } | sort -u
)

required_files=(
    setup.cfg
    pyproject.toml
    purpleair_data_logger/__init__.py
    CMakeLists.txt
    src/version.cpp
    meson.build
    bindings/javascript/package.json
    bindings/csharp/PurpleAirDataLogger.csproj
    sphinx_docs_build/source/conf.py
)

for required_file in "${required_files[@]}"; do
    if [[ ! " ${files[*]} " == *" $required_file "* ]]; then
        printf 'Error: Expected release version "%s" not found in required file: %s\n' "$old_version" "$required_file" >&2
        exit 1
    fi
done

printf '%s version %s -> %s (npm/SemVer %s -> %s) in %d file(s):\n' \
    "$([[ "$dry_run" == true ]] && printf 'Would bump' || printf 'Bumping')" \
    "$old_version" "$new_version" "$old_semver_npm" "$new_semver_npm" "${#files[@]}"
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
    elif [[ "$file" == "pyproject.toml" ]]; then
        OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
            's/^version\s*=\s*"\Q$ENV{OLD_VERSION}\E"$/version = "$ENV{NEW_VERSION}"/m' "$file"
    elif [[ "$file" == "bindings/javascript/package.json" || "$file" == "bindings/javascript/package-lock.json" ]]; then
        OLD_VER="$old_semver_npm" NEW_VER="$new_semver_npm" perl -0pi -e \
            's/"version":\s*"\Q$ENV{OLD_VER}\E"/"version": "$ENV{NEW_VER}"/g' "$file"
    elif [[ "$file" == "bindings/csharp/PurpleAirDataLogger.csproj" ]]; then
        if [[ "$new_version" =~ (a|b|rc) ]]; then
            TARGET_CS_VER="$new_semver_npm"
        else
            TARGET_CS_VER="$new_version"
        fi
        perl -0pi -e 's/<Version>.*?<\/Version>/<Version>'"$TARGET_CS_VER"'<\/Version>/g' "$file"
    elif [[ "$file" == "CMakeLists.txt" || "$file" == "bindings/csharp/CMakeLists.txt" ]]; then
        OLD_BASE="$old_base" NEW_BASE="$new_base" OLD_VER="$old_version" NEW_VER="$new_version" perl -0pi -e \
            's/VERSION\s+\Q$ENV{OLD_BASE}\E/VERSION $ENV{NEW_BASE}/g; s/set\(PURPLEAIR_DL_VERSION_STRING\s+"\Q$ENV{OLD_VER}\E"\)/set(PURPLEAIR_DL_VERSION_STRING "$ENV{NEW_VER}")/g' "$file"
    elif [[ "$file" == "sphinx_docs_build/source/conf.py" ]]; then
        OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
            's/release\s*=\s*"v\Q$ENV{OLD_VERSION}\E"/release = "v$ENV{NEW_VERSION}"/g' "$file"
    else
        OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
            's/\Qv$ENV{OLD_VERSION}\E/v$ENV{NEW_VERSION}/g; s/\Q$ENV{OLD_VERSION}\E/$ENV{NEW_VERSION}/g' "$file"
    fi
done

printf '\nSuccessfully updated version to %s.\n' "$new_version"
