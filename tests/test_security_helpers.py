"""Unit tests for SonarQube security helpers (S5145, S8706, S8707)."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    load_json_config_file,
    sanitize_log_value,
    validate_sqlite_database_path,
)


class TestSecurityHelpers(unittest.TestCase):
    """Verify log sanitization, JSON config path safety, and SQLite path safety."""

    def test_sanitize_log_value_strips_newlines_and_controls(self):
        self.assertEqual(sanitize_log_value("127.0.0.1"), "127.0.0.1")
        self.assertEqual(
            sanitize_log_value("host\r\ninjected\x00line\x1f"),
            "host injected line ",
        )
        self.assertEqual(sanitize_log_value(12345), "12345")

    def test_load_json_config_file_valid_absolute_and_relative(self):
        payload = {"sensor_indexes": [12345]}
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg = Path(tmp_dir) / "config.json"
            cfg.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(load_json_config_file(str(cfg)), payload)

            old_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                self.assertEqual(load_json_config_file("config.json"), payload)
            finally:
                os.chdir(old_cwd)

    def test_load_json_config_file_rejects_traversal_and_invalid_inputs(self):
        for bad_path in ["", None, "bad\x00.json", "../secret.json", "a/../b.json"]:
            with self.assertRaises(ValueError):
                load_json_config_file(bad_path)

    def test_load_json_config_file_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outer_dir:
            secret = Path(outer_dir) / "secret.json"
            secret.write_text('{"k": "v"}', encoding="utf-8")
            work_dir = Path(outer_dir) / "work"
            work_dir.mkdir()
            link = work_dir / "escape.json"
            link.symlink_to(secret)

            old_cwd = os.getcwd()
            try:
                os.chdir(work_dir)
                with self.assertRaises(ValueError):
                    load_json_config_file("escape.json")
            finally:
                os.chdir(old_cwd)

    def test_validate_sqlite_database_path_valid_and_invalid(self):
        self.assertEqual(validate_sqlite_database_path(":memory:"), ":memory:")
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_abs = str(Path(tmp_dir) / "sensors.db")
            self.assertEqual(
                validate_sqlite_database_path(db_abs),
                str(Path(db_abs).resolve()),
            )
            old_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                self.assertEqual(
                    validate_sqlite_database_path("sensors.db"),
                    str((Path(tmp_dir) / "sensors.db").resolve()),
                )
            finally:
                os.chdir(old_cwd)

        for bad_db in [
            "",
            None,
            "db\x00.sqlite",
            "file:sensors.db?mode=ro",
            "FILE:sensors.db",
            "sensors.db?cache=shared",
            "../escape.db",
        ]:
            with self.assertRaises(ValueError):
                validate_sqlite_database_path(bad_db)


if __name__ == "__main__":
    unittest.main()
