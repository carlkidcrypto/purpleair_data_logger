"""Unit tests for .github/scripts/generate_release_notes.py in purpleair_data_logger."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Dynamically import generate_release_notes from .github/scripts/
_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "generate_release_notes.py"
spec = importlib.util.spec_from_file_location(
    "generate_release_notes", str(_SCRIPT_PATH)
)
gen_mod = importlib.util.module_from_spec(spec)
sys.modules["generate_release_notes"] = gen_mod
spec.loader.exec_module(gen_mod)

clean_title = gen_mod.clean_title
rewrite_to_natural_language = gen_mod.rewrite_to_natural_language
categorize_item = gen_mod.categorize_item
parse_semver = gen_mod.parse_semver
determine_base_tag = gen_mod.determine_base_tag
parse_existing_prs = gen_mod.parse_existing_prs
synthesize_summary = gen_mod.synthesize_summary
build_release_notes = gen_mod.build_release_notes


def test_clean_title():
    raw1 = "✨ Fix memory leak in CSV logger (#123) by @carlkidcrypto in https://github.com/carlkidcrypto/purpleair_data_logger/pull/123"
    assert clean_title(raw1) == "Fix memory leak in CSV logger"

    raw2 = "[docs] Update documentation for PSQL data logger #456"
    assert clean_title(raw2) == "[docs] Update documentation for PSQL data logger"


def test_rewrite_to_natural_language_prefixes_and_verbs():
    # Conventional commit prefixes stripped and verb conjugated
    assert (
        rewrite_to_natural_language("feat(psql): add batch insert option")
        == "Adds batch insert option"
    )
    assert (
        rewrite_to_natural_language("fix: resolve crash on missing sensor data")
        == "Resolves crash on missing sensor data"
    )
    assert (
        rewrite_to_natural_language("chore(deps): bump pg8000 from 1.30 to 1.31")
        == "Bumps pg8000 from 1.30 to 1.31"
    )
    assert (
        rewrite_to_natural_language("[coverage-autofix] improve branch coverage")
        == "Improves branch coverage"
    )

    # Past tense verbs conjugated to 3rd person singular present
    assert (
        rewrite_to_natural_language("Fixed connection handling in SQLite logger")
        == "Fixes connection handling in SQLite logger"
    )
    assert (
        rewrite_to_natural_language("Added support for Python 3.14")
        == "Adds support for Python 3.14"
    )
    assert (
        rewrite_to_natural_language("Updated dependencies in requirements.txt")
        == "Updates dependencies in requirements.txt"
    )

    # Prefix with noun gets inferred active verb
    assert (
        rewrite_to_natural_language("fix: memory leak in CSV writer")
        == "Fixes memory leak in CSV writer"
    )
    assert (
        rewrite_to_natural_language("feat: matter protocol support")
        == "Adds matter protocol support"
    )

    # Already third person present unchanged
    assert (
        rewrite_to_natural_language("Adds support for Loki push API")
        == "Adds support for Loki push API"
    )


def test_categorize_item():
    # Dependencies
    assert categorize_item("Bump pg8000 from 1.30 to 1.31", []) == "Dependencies"
    assert (
        categorize_item(
            "Update packages",
            ["requirements.txt"],
        )
        == "Dependencies"
    )

    # CI / Workflows (priority over docs)
    assert (
        categorize_item(
            "Update release workflow",
            [".github/workflows/auto_release_notes.md"],
        )
        == "CI / Workflows"
    )
    assert categorize_item("ci: improve test matrix", []) == "CI / Workflows"

    # Documentation
    assert (
        categorize_item("docs: update getting started guide", ["docs/index.rst"])
        == "Documentation"
    )
    assert categorize_item("Fix typo in readme", ["README.md"]) == "Documentation"

    # Tests
    assert (
        categorize_item(
            "Add test for CSV logger missing fields",
            ["tests/test_purpleair_data_logger.py"],
        )
        == "Tests"
    )
    assert (
        categorize_item(
            "test: verify behave scenarios", ["behave_tests/features/test.feature"]
        )
        == "Tests"
    )

    # Packaging
    assert (
        categorize_item("Update wheel configuration", ["setup.py", "setup.cfg"])
        == "Packaging"
    )

    # Core Library / Bug Fixes / Features
    assert (
        categorize_item(
            "Fix query string format",
            ["purpleair_data_logger/PurpleAirPSQLQueryStatements.py"],
        )
        == "Bug Fixes"
    )
    assert (
        categorize_item(
            "Add Matter data logger integration",
            ["purpleair_data_logger/PurpleAirMatterDataLogger.py"],
        )
        == "Features / Enhancements"
    )
    assert (
        categorize_item(
            "Refactor helper utilities",
            ["purpleair_data_logger/PurpleAirDataLoggerHelpers.py"],
        )
        == "Data Loggers / Core"
    )

    # Chores / Misc
    assert categorize_item("misc cleanups", ["LICENSE"]) == "Chores / Misc"


def test_parse_semver():
    assert parse_semver("v1.5.1") == (1, 5, 0, 1, "")
    assert parse_semver("v1.5.1a2") == (1, 5, 0, 0, "a2")
    assert parse_semver("0.0.8b1") == (0, 0, 8, 0, "b1")
    assert parse_semver("invalid-tag") is None


def test_determine_base_tag_priority_1_override():
    rel = {
        "tag_name": "v1.5.1",
        "prerelease": False,
        "body": "Some body\n<!-- BASE_TAG: v1.4.0-custom -->\nMore text",
    }
    base = determine_base_tag(rel, [], set())
    assert base == "v1.4.0-custom"


def test_determine_base_tag_priority_2_stable():
    releases = [
        {"tag_name": "v1.3.0", "prerelease": False},
        {"tag_name": "v1.4.0", "prerelease": False},
        {"tag_name": "v1.5.1a1", "prerelease": True},
        {"tag_name": "v1.5.1a2", "prerelease": True},
        {"tag_name": "v1.5.1", "prerelease": False},
    ]
    # For v1.5.1 (stable), the base must skip prereleases and pick v1.4.0
    base = determine_base_tag(releases[-1], releases, set())
    assert base == "v1.4.0"


def test_determine_base_tag_priority_3_prerelease():
    releases = [
        {"tag_name": "v1.4.0", "prerelease": False},
        {"tag_name": "v1.5.1a1", "prerelease": True},
        {"tag_name": "v1.5.1a2", "prerelease": True},
    ]
    # For v1.5.1a2 (prerelease), base picks the immediately preceding release
    base = determine_base_tag(releases[-1], releases, set())
    assert base == "v1.5.1a1"


def test_determine_base_tag_priority_4_semver_fallback():
    current_rel = {"tag_name": "v1.5.1", "prerelease": False, "body": ""}
    git_tags = {"v1.0.0", "v1.3.0", "v1.4.2", "v1.5.1", "v2.0.0"}
    base = determine_base_tag(current_rel, [current_rel], git_tags)
    assert base == "v1.4.2"


def test_parse_existing_prs():
    body = (
        "* Add Matter protocol logger by @carlkidcrypto in"
        " https://github.com/carlkidcrypto/purpleair_data_logger/pull/50\n* Fix leak by"
        " @contributor in https://github.com/carlkidcrypto/purpleair_data_logger/pull/51\n"
    )
    git_commits = {
        "hash1": {
            "title": "feat: add matter protocol logger (#50)",
            "files": ["purpleair_data_logger/PurpleAirMatterDataLogger.py"],
        },
        "hash2": {
            "title": "fix: fix leak (#51)",
            "files": ["purpleair_data_logger/PurpleAirCSVDataLogger.py"],
        },
    }
    prs, seen = parse_existing_prs(body, git_commits)
    assert seen == {"50", "51"}
    assert len(prs) == 2
    assert prs[0]["pr"] == "50"
    assert prs[0]["files"] == ["purpleair_data_logger/PurpleAirMatterDataLogger.py"]
    assert prs[1]["pr"] == "51"
    assert prs[1]["files"] == ["purpleair_data_logger/PurpleAirCSVDataLogger.py"]


def test_synthesize_summary():
    categories = {
        "Features / Enhancements": ["- Adds feature (#1)"],
        "Bug Fixes": ["- Fixes bug (#2)"],
        "Data Loggers / Core": [],
        "Tests": [],
        "Packaging": [],
        "CI / Workflows": [],
        "Documentation": [],
        "Dependencies": [],
        "Chores / Misc": [],
    }
    summary = synthesize_summary(categories, is_prerelease=False)
    assert (
        "release focuses on features and enhancements and bug fixes across the purpleair_data_logger package."
        in summary
    )

    summary_with_ctx = synthesize_summary(
        categories,
        is_prerelease=True,
        additional_context="Includes extra docs.",
    )
    assert "prerelease focuses on" in summary_with_ctx
    assert summary_with_ctx.endswith("Includes extra docs.")


def test_build_release_notes():
    release = {
        "tag_name": "v1.5.1",
        "prerelease": False,
        "body": (
            "* Add Matter protocol logger by @carlkidcrypto in"
            " https://github.com/carlkidcrypto/purpleair_data_logger/pull/50\n"
        ),
    }
    git_commits: dict[str, dict[str, Any]] = {
        "aaa111122223333444455556666777788889999": {
            "title": "Add Matter protocol logger (#50)",
            "files": ["purpleair_data_logger/PurpleAirMatterDataLogger.py"],
        },
        "bbb111122223333444455556666777788889999": {
            "title": "fix: query formatting in PSQL (#51)",
            "files": ["purpleair_data_logger/PurpleAirPSQLQueryStatements.py"],
        },
    }
    notes = build_release_notes(release, "v1.4.2", git_commits)

    assert "Compared to: v1.4.2" in notes
    assert "pip install purpleair_data_logger==1.5.1" in notes
    assert "https://pypi.org/project/purpleair_data_logger/1.5.1/" in notes
    assert "## Features / Enhancements" in notes
    assert "- Adds Matter protocol logger (#50)" in notes
    assert "## Bug Fixes" in notes
    assert "- Fixes query formatting in PSQL (#51)" in notes
    assert (
        "**Full Changelog**:"
        " https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.4.2...v1.5.1"
        in notes
    )


def test_build_release_notes_non_version_tag():
    release = {
        "tag_name": "custom_build",
        "prerelease": False,
        "body": "",
    }
    notes = build_release_notes(release, "repository root", {})
    # Should omit Install / Upgrade if not a valid version
    assert "## Install / Upgrade" not in notes
    assert "Compared to: repository root" in notes
    assert (
        "**Full Changelog**:"
        " https://github.com/carlkidcrypto/purpleair_data_logger/commits/custom_build"
        in notes
    )
