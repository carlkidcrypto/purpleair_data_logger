"""Allow invoking `python3 -m purpleair_data_logger <subcommand> [options]`."""

import sys

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
