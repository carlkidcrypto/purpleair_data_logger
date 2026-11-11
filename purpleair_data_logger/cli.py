"""Unified CLI entry point for purpleair_data_logger.

All operational commands (`run`, `validate`, `probe`, `request`, `set`, `inspect`,
`init-config`, `schema`, `version`, `help`) are executed by the C++17 `CliRunner`.
The `gui` subcommand launches the Cross-Platform GUI which drives this CLI behind the scenes.
"""

from __future__ import annotations

import sys
from typing import Sequence

from .purpleair_data_logger_swig import CliRunner, StringVector


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args and args[0] == "gui":
        from .gui import main as gui_main

        return gui_main(args[1:])

    vec = StringVector(args)
    return int(CliRunner.run(vec))


def main_gui(argv: Sequence[str] | None = None) -> int:
    from .gui import main as gui_main

    args = list(sys.argv[1:] if argv is None else argv)
    return gui_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
