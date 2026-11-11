#!/usr/bin/env python3
"""Convenience CLI script to install the PurpleAir Data Logger Studio desktop launcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from purpleair_data_logger.gui.launcher import install_desktop_launcher


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install native desktop launcher with custom PurpleAir Data Logger icon."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Target directory (defaults to ~/Applications on macOS, ~/.local/share/applications on Linux).",
    )
    args = parser.parse_args()

    installed = install_desktop_launcher(target_dir=args.dir)
    print(
        f"Successfully installed PurpleAir Data Logger desktop launcher at: {installed}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
