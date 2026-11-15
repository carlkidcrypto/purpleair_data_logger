"""Unit tests for .github/scripts/update_landing_versions.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from packaging.version import Version

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "update_landing_versions.py"
_SPEC = importlib.util.spec_from_file_location(
    "update_landing_versions", str(_SCRIPT_PATH)
)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["update_landing_versions"] = _MOD
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_MOD)

parse_version = _MOD.parse_version
update_landing_version_list = _MOD.update_landing_version_list
main = _MOD.main


class TestUpdateLandingVersions(unittest.TestCase):
    """Tests for Sphinx landing page version normalization and prerelease retirement."""

    def test_parse_version_valid_and_invalid(self) -> None:
        self.assertEqual(parse_version("html_v2026.11.3a0"), Version("2026.11.3a0"))
        self.assertEqual(parse_version("html_V1.6.0"), Version("1.6.0"))
        self.assertEqual(parse_version("html_vnotaversion"), Version("0.0.0"))

    def test_update_landing_version_list_retires_prereleases_and_normalizes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            for name in (
                "html",
                "html_V1.6.0",
                "html_v1.6.0a0",
                "html_v1.6.0a1",
                "html_v2026.11.3a0",
                "html_v1.5.0",
            ):
                (docs_dir / name).mkdir()

            index_rst = root / "index.rst"
            index_rst.write_text(
                "Header\n\n.. VERSION_LIST_START\n\n* old\n\n.. VERSION_LIST_END\n\nFooter\n",
                encoding="utf-8",
            )

            active = update_landing_version_list(docs_dir, index_rst)

            self.assertEqual(
                active, ["html_v2026.11.3a0", "html_v1.6.0", "html_v1.5.0"]
            )
            entries = set(os.listdir(docs_dir))
            self.assertNotIn("html_V1.6.0", entries)
            self.assertIn("html_v1.6.0", entries)
            self.assertNotIn("html_v1.6.0a0", entries)
            self.assertNotIn("html_v1.6.0a1", entries)
            self.assertIn("html_v2026.11.3a0", entries)

            rendered = index_rst.read_text(encoding="utf-8")
            self.assertIn("* `Latest Version <./html/index.html>`_", rendered)
            self.assertIn(
                "* `v2026.11.3a0 <./html_v2026.11.3a0/index.html>`_", rendered
            )
            self.assertIn("* `v1.6.0 <./html_v1.6.0/index.html>`_", rendered)
            self.assertIn("* `v1.5.0 <./html_v1.5.0/index.html>`_", rendered)
            self.assertNotIn("v1.6.0a0", rendered)

    def test_main_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "html_v1.0.0").mkdir()

            valid_rst = root / "valid.rst"
            valid_rst.write_text(
                ".. VERSION_LIST_START\n.. VERSION_LIST_END\n",
                encoding="utf-8",
            )
            self.assertEqual(
                main(["--docs-dir", str(docs_dir), "--index-rst", str(valid_rst)]), 0
            )

            missing_sentinels_rst = root / "invalid.rst"
            missing_sentinels_rst.write_text("No sentinels here\n", encoding="utf-8")
            self.assertEqual(
                main(
                    [
                        "--docs-dir",
                        str(docs_dir),
                        "--index-rst",
                        str(missing_sentinels_rst),
                    ]
                ),
                1,
            )


if __name__ == "__main__":
    unittest.main()
