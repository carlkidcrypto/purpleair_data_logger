"""Cross-platform Graphical User Interface launcher for purpleair_data_logger.

Supports Linux, macOS, and Windows via:
1. `tk`: Native cross-platform desktop application (`tkinter.ttk`), or
2. `web`: Cross-platform Browser Studio (`http.server` + HTML5/SVG).

Both frontends interact strictly with the `purpleair-data-logger` CLI behind the scenes
and store 100% of configuration and GUI settings in JSON.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .cli_bridge import CliSubprocessBridge
from .locale_manager import LocaleManager


def can_use_tkinter_display() -> bool:
    """Return True if tkinter is installed and a graphical display is available."""
    try:
        import tkinter  # noqa: F401
    except Exception:
        return False

    if sys.platform in ("win32", "darwin"):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def select_frontend(requested: str) -> str:
    """Resolve 'auto' | 'tk' | 'web' to a concrete cross-platform frontend."""
    mode = (requested or "auto").strip().lower()
    if mode == "tk":
        return "tk"
    if mode == "web":
        return "web"
    return "tk" if can_use_tkinter_display() else "web"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for `purpleair-data-logger-gui` and `purpleair-data-logger gui`."""
    parser = argparse.ArgumentParser(
        prog="purpleair-data-logger-gui",
        description="Cross-platform GUI for purpleair_data_logger (drives the CLI via JSON).",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="./configs/example.json",
        help="Path to the JSON configuration file (created from demo template if missing).",
    )
    parser.add_argument(
        "--frontend",
        choices=["auto", "tk", "web"],
        default="",
        help="Override gui.frontend from the JSON configuration ('auto', 'tk', or 'web').",
    )
    parser.add_argument(
        "--host",
        default="",
        help="Override gui.host when launching the 'web' frontend.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=-1,
        help="Override gui.port when launching the 'web' frontend.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open the system web browser in 'web' mode.",
    )
    parser.add_argument(
        "--cli-executable",
        default="",
        help="Override path to the purpleair-data-logger CLI executable.",
    )
    parser.add_argument(
        "--locale",
        default="",
        help="Override gui.locale ('en', 'es', etc.) for UI titles, buttons, and bars.",
    )
    parser.add_argument(
        "--locale-file",
        default="",
        help="Path to custom locale.json file defining UI strings.",
    )
    parser.add_argument(
        "--install-launcher",
        action="store_true",
        help="Install native cross-platform desktop application launcher with custom icon (.app on macOS, .desktop on Linux).",
    )
    parser.add_argument(
        "--launcher-dir",
        type=Path,
        default=None,
        help="Target directory for desktop launcher (defaults to ~/Applications or ~/.local/share/applications).",
    )
    args = parser.parse_args(argv)

    if args.install_launcher:
        from .launcher import install_desktop_launcher

        path = install_desktop_launcher(target_dir=args.launcher_dir)
        print(f"[purpleair-data-logger-gui] Installed desktop launcher at: {path}")
        return 0

    bridge = CliSubprocessBridge(Path(args.config), cli_override=args.cli_executable)
    cfg = bridge.load_config_dict()
    gui_cfg = cfg.get("gui", {}) if isinstance(cfg.get("gui"), dict) else {}

    locale_code = (
        args.locale
        or str(gui_cfg.get("locale", ""))
        or str(gui_cfg.get("language", "en"))
    )
    locale_file = args.locale_file or str(gui_cfg.get("locale_file", ""))
    locale_mgr = LocaleManager(
        locale=locale_code,
        locale_file=locale_file if locale_file else None,
    )

    chosen = select_frontend(args.frontend or str(gui_cfg.get("frontend", "auto")))
    if chosen == "tk":
        try:
            from .desktop_tk import launch_desktop_gui

            return launch_desktop_gui(bridge, locale_mgr=locale_mgr)
        except Exception as exc:
            print(
                f"[purpleair-data-logger-gui] Native Tk desktop unavailable ({exc}); "
                "falling back to cross-platform Browser Studio.",
                file=sys.stderr,
            )

    from .server import launch_web_gui

    host = args.host or str(gui_cfg.get("host", "127.0.0.1"))
    port = args.port if args.port >= 0 else int(gui_cfg.get("port", 8765))
    open_browser = False if args.no_browser else bool(gui_cfg.get("open_browser", True))
    return launch_web_gui(
        bridge,
        locale_mgr=locale_mgr,
        host=host,
        port=port,
        open_browser=open_browser,
    )


__all__ = [
    "CliSubprocessBridge",
    "LocaleManager",
    "can_use_tkinter_display",
    "main",
    "select_frontend",
]
