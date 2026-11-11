"""Locale and internationalization manager for purpleair_data_logger GUIs.

Loads `locale.json` where strings are defined in the format:
`{"LOCALE_KEY_NAME": {"en": "...", "es": "...", ...}}`
for effortless per-key translation and multi-language deployment across desktop and web.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_LOCALE_PATH = Path(__file__).resolve().parent / "locale.json"
if not DEFAULT_LOCALE_PATH.is_file() and getattr(
    sys, "_MEIPASS", None
):  # pragma: no cover
    _cand = Path(sys._MEIPASS) / "purpleair_data_logger" / "gui" / "locale.json"
    if _cand.is_file():
        DEFAULT_LOCALE_PATH = _cand


class LocaleManager:
    """Manages string resolution, language selection, and fallback for GUIs.

    Supports the key-centric format:
    `{"LOCALE_KEY_NAME": {"en": "...", "es": "...", ...}}`
    """

    def __init__(
        self,
        locale: str = "en",
        locale_file: str | Path | None = None,
    ) -> None:
        self.locale = (locale or "en").strip().lower()
        self.locale_file = (
            Path(locale_file).resolve() if locale_file else DEFAULT_LOCALE_PATH
        )
        self._catalog: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Load or reload locale definitions from JSON file."""
        if not self.locale_file.is_file():
            self.locale_file = DEFAULT_LOCALE_PATH

        try:
            self._catalog = json.loads(self.locale_file.read_text(encoding="utf-8"))
        except Exception:
            if (
                self.locale_file != DEFAULT_LOCALE_PATH
                and DEFAULT_LOCALE_PATH.is_file()
            ):
                self._catalog = json.loads(
                    DEFAULT_LOCALE_PATH.read_text(encoding="utf-8")
                )
            else:
                self._catalog = {}

    def supported_locales(self) -> list[str]:
        """Return list of supported locale codes in the loaded catalog."""
        langs: set[str] = {"en"}
        for entry in self._catalog.values():
            if isinstance(entry, dict):
                langs.update(
                    k.strip().lower() for k in entry.keys() if isinstance(k, str)
                )
        return sorted(langs)

    def set_locale(self, locale: str) -> None:
        """Switch active locale (e.g. 'en', 'es')."""
        if locale:
            self.locale = locale.strip().lower()

    def t(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        """Translate a key into the active locale with keyword formatting."""
        entry = self._catalog.get(key)
        val: Any | None = None

        if isinstance(entry, dict):
            val = entry.get(self.locale)
            if val is None and self.locale != "en":
                val = entry.get("en")
        elif entry is not None and not isinstance(entry, dict):
            val = entry

        if val is None and "." in key:
            parts = key.split(".")
            curr: Any = self._catalog
            for p in parts:
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
                else:
                    curr = None
                    break
            if isinstance(curr, dict):
                val = curr.get(self.locale) or curr.get("en")
            elif isinstance(curr, str):
                val = curr

        if val is None:
            val = default if default is not None else key

        if isinstance(val, str) and kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return str(val) if val is not None else ""

    def get_locale_dict(self, locale: str | None = None) -> dict[str, str]:
        """Return flat dictionary mapping each key to its string for the requested locale."""
        loc = (locale or self.locale).strip().lower()
        res: dict[str, str] = {}
        for key, entry in self._catalog.items():
            if isinstance(entry, dict):
                v = entry.get(loc)
                if v is None:
                    v = entry.get("en")
                if v is not None:
                    res[key] = str(v)
            elif isinstance(entry, str):
                res[key] = entry
        return res


def get_default_locale_manager() -> LocaleManager:
    """Return a default LocaleManager instance configured for English."""
    return LocaleManager(locale="en")
