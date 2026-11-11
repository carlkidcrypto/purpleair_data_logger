"""Tests for desktop launcher shortcuts and locale manager."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from purpleair_data_logger.gui.launcher import (
    get_icon_path,
    install_desktop_launcher,
)
from purpleair_data_logger.gui.locale_manager import (
    DEFAULT_LOCALE_PATH,
    LocaleManager,
)


def test_launcher_meipass_and_platform_shortcuts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_meipass = tmp_path / "meipass"
    fake_static = fake_meipass / "purpleair_data_logger" / "gui" / "static"
    fake_static.mkdir(parents=True, exist_ok=True)
    (fake_static / "app_icon.png").write_bytes(b"PNG_DATA")

    monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)
    unknown_icon = get_icon_path("nonexistent_kind")
    assert unknown_icon.name == "app_icon.png"

    monkeypatch.setattr(sys, "platform", "win32")
    win_out = tmp_path / "win_out"
    path_win = install_desktop_launcher(win_out)
    assert path_win.suffix == ".bat"

    monkeypatch.setattr(sys, "platform", "linux")
    linux_out = tmp_path / "linux_out"
    path_linux = install_desktop_launcher(linux_out)
    assert path_linux.suffix == ".desktop"


def test_locale_manager_complete_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_meipass = tmp_path / "meipass_loc"
    fake_loc_dir = fake_meipass / "purpleair_data_logger" / "gui"
    fake_loc_dir.mkdir(parents=True, exist_ok=True)
    fake_loc_file = fake_loc_dir / "locale.json"
    fake_loc_file.write_text('{"key": {"en": "val"}}', encoding="utf-8")
    monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)

    mgr = LocaleManager(locale="en", locale_file=tmp_path / "missing.json")
    assert mgr.locale_file == DEFAULT_LOCALE_PATH

    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not valid json", encoding="utf-8")
    mgr_corrupt = LocaleManager(locale="en", locale_file=corrupt)
    assert "buttons.start_logger" in mgr_corrupt._catalog

    monkeypatch.setattr(
        "purpleair_data_logger.gui.locale_manager.DEFAULT_LOCALE_PATH",
        tmp_path / "empty.json",
    )
    mgr_empty = LocaleManager(locale="en", locale_file=corrupt)
    assert mgr_empty._catalog == {}

    test_catalog = {
        "scalar_key": "Direct String Value",
        "normal_key": {
            "en": "English Normal",
            "es": "Spanish Normal",
        },
        "nested": {
            "sub": {
                "en": "English Sub {name}",
                "es": "Spanish Sub {name}",
            },
            "leaf_str": "Direct nested leaf",
        },
        "only_en": {"en": "Only English"},
        "flat_str": "Plain string for flat",
    }
    custom_loc = tmp_path / "catalog_test.json"
    custom_loc.write_text(json.dumps(test_catalog), encoding="utf-8")

    mgr_test = LocaleManager(locale="es", locale_file=custom_loc)
    assert "en" in mgr_test.supported_locales()
    assert "es" in mgr_test.supported_locales()

    mgr_test.set_locale("es")
    assert mgr_test.locale == "es"

    assert mgr_test.t("nested.missing.path") == "nested.missing.path"
    assert mgr_test.t("missing_key", default="fallback_val") == "fallback_val"
    assert mgr_test.t("scalar_key") == "Direct String Value"
    assert mgr_test.t("nested.sub", name="World") == "Spanish Sub World"
    assert mgr_test.t("only_en") == "Only English"
    assert mgr_test.t("nested.leaf_str") == "Direct nested leaf"
    assert mgr_test.t("nested.sub", bad_kwarg="x") == "Spanish Sub {name}"

    d_es = mgr_test.get_locale_dict("es")
    assert d_es["only_en"] == "Only English"
    assert d_es["flat_str"] == "Plain string for flat"
