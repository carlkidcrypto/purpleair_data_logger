"""Unit tests for scripts/fetch_codecov_report.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "fetch_codecov_report.py"
_SPEC = importlib.util.spec_from_file_location(
    "fetch_codecov_report", str(_SCRIPT_PATH)
)
assert _SPEC is not None and _SPEC.loader is not None
codecov_mod = importlib.util.module_from_spec(_SPEC)
sys.modules["fetch_codecov_report"] = codecov_mod
_SPEC.loader.exec_module(codecov_mod)


class TestFetchCodecovReport(unittest.TestCase):
    """Test cases for fetch_codecov_report."""

    def test_constants_and_summarize_report(self) -> None:
        self.assertEqual(codecov_mod.MAX_LOOKBACK, 30)
        self.assertEqual(codecov_mod.compress_lines([1, 2, 3, 5]), "1-3, 5")
        summary = "\n".join(
            codecov_mod.summarize_report(
                {
                    "totals": {
                        "coverage": 95.5,
                        "lines": 200,
                        "hits": 191,
                        "misses": 9,
                    },
                    "files": [],
                },
                "Overall",
            )
        )
        self.assertIn("95.5%", summary)
        self.assertIn("hits=191", summary)

    def test_main_missing_repository_env(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch("sys.argv", ["fetch_codecov_report.py"]):
                rc = codecov_mod.main()
        self.assertEqual(rc, 0)

    def test_fetch_scope_uses_lookback_commit(self) -> None:
        calls: list[str] = []

        def fake_api_get(url: str, token: str):
            calls.append(url)
            if "sha=abc1234" in url:
                return {
                    "totals": {"lines": 100, "hits": 90, "misses": 10},
                    "files": [
                        {
                            "name": "a.py",
                            "totals": {"lines": 100, "coverage": 90},
                            "line_coverage": [[1, 1]],
                        }
                    ],
                }
            return {"totals": {"lines": 0}, "files": []}

        with mock.patch.object(codecov_mod, "api_get", side_effect=fake_api_get):
            report, used_sha, err = codecov_mod.fetch_scope(
                "https://api.codecov.io/api/v2/github/owner/repos/pkg",
                "tok",
                "main",
                {"component_id": "python_code"},
                [{"commitid": "headsha"}, {"commitid": "abc1234"}],
            )

        self.assertIsNone(err)
        self.assertEqual(used_sha["commitid"], "abc1234")
        self.assertEqual(report["totals"]["lines"], 100)
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
