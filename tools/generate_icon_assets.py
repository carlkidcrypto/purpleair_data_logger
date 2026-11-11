#!/usr/bin/env python3
"""Generates multi-platform icons, favicons, and application badges for purpleair_data_logger.

Generates:
- `favicon.svg`: Modern vector SVG icon for browser tabs.
- `favicon.ico`, `favicon-32x32.png`, `favicon-16x16.png`, `apple-touch-icon.png`: Browser favicons.
- `app_icon.png`, `app_icon_256.png`, `app_icon_128.png`, `app_icon_64.png`, `app_icon_32.png`, `app_icon_16.png`: Native desktop app icons.
- `app_icon.ico`: Multi-resolution Windows ICO (16, 32, 48, 64, 128, 256).
- `app_icon.icns`: Retina macOS application bundle ICNS.
- `purpleair_logo.png`: Full resolution PurpleAir Data Logger brand logo.
"""

from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "purpleair_data_logger" / "gui" / "static"


def write_ico(png_paths: list[Path], output_ico: Path) -> None:
    """Create a standard multi-resolution Windows ICO file embedding PNG byte streams."""
    entries: list[bytes] = []
    data_blobs: list[bytes] = []
    offset = 6 + len(png_paths) * 16

    for p in png_paths:
        png_data = p.read_bytes()
        w, h = struct.unpack(">II", png_data[16:24])
        b_w = 0 if w >= 256 else w
        b_h = 0 if h >= 256 else h
        size = len(png_data)

        entry = struct.pack("<BBBBHHII", b_w, b_h, 0, 0, 1, 32, size, offset)
        entries.append(entry)
        data_blobs.append(png_data)
        offset += size

    header = struct.pack("<HHH", 0, 1, len(png_paths))
    with open(output_ico, "wb") as f:
        f.write(header)
        for e in entries:
            f.write(e)
        for d in data_blobs:
            f.write(d)


def build_icons() -> None:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    svg_favicon = STATIC_DIR / "favicon.svg"

    tmp_dir = STATIC_DIR / ".icon_build_tmp"
    tmp_dir.mkdir(exist_ok=True)

    try:
        if svg_favicon.is_file() and shutil.which("sips"):
            print(f"Generating favicons and app icons from {svg_favicon}...")
            fav_sizes = [
                ("favicon-16x16.png", 16),
                ("favicon-32x32.png", 32),
                ("apple-touch-icon.png", 180),
                ("icon-192x192.png", 192),
                ("icon-512x512.png", 512),
                ("app_icon.png", 512),
                ("app_icon_256.png", 256),
                ("app_icon_128.png", 128),
                ("app_icon_64.png", 64),
                ("app_icon_32.png", 32),
                ("app_icon_16.png", 16),
                ("purpleair_logo.png", 512),
            ]
            for fname, sz in fav_sizes:
                out = STATIC_DIR / fname
                subprocess.run(
                    [
                        "sips",
                        "-s",
                        "format",
                        "png",
                        "-z",
                        str(sz),
                        str(sz),
                        str(svg_favicon),
                        "--out",
                        str(out),
                    ],
                    check=True,
                    capture_output=True,
                )

            fav_ico_pngs = []
            for s in [16, 32, 48]:
                p = tmp_dir / f"fav_{s}.png"
                subprocess.run(
                    [
                        "sips",
                        "-s",
                        "format",
                        "png",
                        "-z",
                        str(s),
                        str(s),
                        str(svg_favicon),
                        "--out",
                        str(p),
                    ],
                    check=True,
                    capture_output=True,
                )
                fav_ico_pngs.append(p)
            write_ico(fav_ico_pngs, STATIC_DIR / "favicon.ico")

            ico_pngs = [
                STATIC_DIR / "app_icon_16.png",
                STATIC_DIR / "app_icon_32.png",
                STATIC_DIR / "app_icon_64.png",
                STATIC_DIR / "app_icon_128.png",
                STATIC_DIR / "app_icon_256.png",
            ]
            write_ico(ico_pngs, STATIC_DIR / "app_icon.ico")

            if shutil.which("iconutil"):
                iconset = tmp_dir / "AppIcon.iconset"
                iconset.mkdir(exist_ok=True)
                mac_icon_map = [
                    ("icon_16x16.png", 16),
                    ("icon_16x16@2x.png", 32),
                    ("icon_32x32.png", 32),
                    ("icon_32x32@2x.png", 64),
                    ("icon_128x128.png", 128),
                    ("icon_128x128@2x.png", 256),
                    ("icon_256x256.png", 256),
                    ("icon_256x256@2x.png", 512),
                    ("icon_512x512.png", 512),
                    ("icon_512x512@2x.png", 1024),
                ]
                for iname, isz in mac_icon_map:
                    subprocess.run(
                        [
                            "sips",
                            "-s",
                            "format",
                            "png",
                            "-z",
                            str(isz),
                            str(isz),
                            str(svg_favicon),
                            "--out",
                            str(iconset / iname),
                        ],
                        check=True,
                        capture_output=True,
                    )
                icns_dest = STATIC_DIR / "app_icon.icns"
                subprocess.run(
                    ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_dest)],
                    check=True,
                    capture_output=True,
                )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("All launcher and browser icon assets built successfully in:", STATIC_DIR)


if __name__ == "__main__":
    build_icons()
