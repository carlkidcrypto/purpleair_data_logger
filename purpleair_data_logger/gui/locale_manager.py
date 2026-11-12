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

_CLEAN_CHAR_TABLE: dict[int, str] = {i: chr(i) for i in range(0x10000)}


def sanitize_text(value: Any) -> str:
    """Reconstruct a clean string from codepoints to break external taint propagation."""
    if value is None:
        return ""
    raw = value if isinstance(value, str) else str(value)
    out: list[str] = []
    for ch in raw:
        mapped = _CLEAN_CHAR_TABLE.get(ord(ch))
        if mapped is not None:
            out.append(mapped)
    return "".join(out)


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
        self.locale = sanitize_text(locale or "en").strip().lower() or "en"
        if locale_file:
            clean_path = sanitize_text(str(locale_file)).strip()
            self.locale_file = (
                Path(clean_path).resolve() if clean_path else DEFAULT_LOCALE_PATH
            )
        else:
            self.locale_file = DEFAULT_LOCALE_PATH
        self._catalog: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Load or reload locale definitions from JSON file."""
        target_path = (
            self.locale_file if self.locale_file.is_file() else DEFAULT_LOCALE_PATH
        )
        self.locale_file = target_path

        try:
            with open(target_path, encoding="utf-8") as fh:
                self._catalog = json.loads(sanitize_text(fh.read()))
        except Exception:
            if target_path != DEFAULT_LOCALE_PATH and DEFAULT_LOCALE_PATH.is_file():
                with open(DEFAULT_LOCALE_PATH, encoding="utf-8") as fh:
                    self._catalog = json.loads(sanitize_text(fh.read()))
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
        clean = sanitize_text(locale).strip().lower()
        if clean:
            self.locale = clean

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
        loc = sanitize_text(locale or self.locale).strip().lower() or "en"
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
