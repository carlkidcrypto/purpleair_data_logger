#!/usr/bin/env python3
"""Standalone desktop application & CLI entry point for PyInstaller bundles.

When invoked with no arguments (e.g. double-clicking the desktop app or `.app` bundle)
or with `gui`, this launches the PurpleAir Data Logger Studio GUI.
When invoked with `cli <subcommand> ...` or any standard CLI subcommand (`run`, `validate`,
`probe`, `request`, `set`, `inspect`, `init-config`, `schema`, `version`, `help`), it
dispatches directly to the C++17 CLI runner so that the packaged binary also functions as the
`CliSubprocessBridge` backend when frozen.
"""

from __future__ import annotations

import multiprocessing
import sys
from typing import Sequence

CLI_SUBCOMMANDS = {
    "run",
    "validate",
    "probe",
    "request",
    "set",
    "inspect",
    "init-config",
    "schema",
    "version",
    "help",
    "-h",
    "--help",
    "-V",
    "--version",
}


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    args = [a for a in args if not a.startswith("-psn_")]

    if not args:
        from purpleair_data_logger.gui import main as gui_main

        return gui_main([])

    first = args[0]
    if first == "cli":
        from purpleair_data_logger.cli import main as cli_main

        return cli_main(args[1:])

    if first == "gui":
        from purpleair_data_logger.gui import main as gui_main

        return gui_main(args[1:])

    if first in CLI_SUBCOMMANDS:
        from purpleair_data_logger.cli import main as cli_main

        return cli_main(args)

    from purpleair_data_logger.gui import main as gui_main

    return gui_main(args)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
