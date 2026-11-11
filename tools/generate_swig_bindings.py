#!/usr/bin/env python3
"""Generate SWIG 4.x bindings for the 4 supported target languages:
python, javascript (Node.js N-API), csharp (.NET), and go (cgo).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERFACE_FILE = ROOT / "interface" / "purpleair_data_logger.i"
INCLUDE_DIR = ROOT / "include"
INTERFACE_DIR = ROOT / "interface"

LANGUAGE_SPECS: dict[str, dict[str, object]] = {
    "python": {
        "flags": ["-c++", "-python", "-threads"],
        "wrapper": "purpleair_data_logger_python_wrap.cxx",
    },
    "javascript": {
        "flags": ["-c++", "-javascript", "-napi"],
        "wrapper": "purpleair_data_logger_javascript_wrap.cxx",
    },
    "csharp": {
        "flags": [
            "-c++",
            "-csharp",
            "-namespace",
            "PurpleAirDataLogger",
            "-dllimport",
            "purpleair_data_logger_csharp",
        ],
        "wrapper": "purpleair_data_logger_csharp_wrap.cxx",
    },
    "go": {
        "flags": ["-c++", "-go", "-cgo", "-intgosize", "64"],
        "wrapper": "purpleair_data_logger_go_wrap.cxx",
    },
}


SWIG_LANGUAGE_TARGETS = LANGUAGE_SPECS


def generate_language(swig_bin: str, lang: str, out_base: Path) -> Path:
    if lang not in LANGUAGE_SPECS:
        raise ValueError(f"Unsupported SWIG target language: {lang}")

    spec = LANGUAGE_SPECS[lang]
    lang_dir = out_base / lang
    if lang_dir.exists():
        shutil.rmtree(lang_dir)
    lang_dir.mkdir(parents=True, exist_ok=True)

    wrapper_path = lang_dir / str(spec["wrapper"])
    cmd = [
        swig_bin,
        *list(spec["flags"]),  # type: ignore[arg-type]
        f"-I{INCLUDE_DIR}",
        f"-I{INTERFACE_DIR}",
        "-outdir",
        str(lang_dir),
        "-o",
        str(wrapper_path),
        str(INTERFACE_FILE),
    ]

    subprocess.run(cmd, check=True)
    return wrapper_path


def generate_for_language(
    swig_bin: str, lang: str, out_base: Path
) -> dict[str, object]:
    try:
        wrapper = generate_language(swig_bin, lang, out_base)
        files = sorted(str(p) for p in wrapper.parent.iterdir())
        return {
            "ok": True,
            "wrapper": str(wrapper),
            "generated_files": files,
            "stderr": "",
        }
    except subprocess.CalledProcessError as exc:
        return {"ok": False, "wrapper": "", "generated_files": [], "stderr": str(exc)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SWIG bindings across the 4 supported target languages."
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=list(LANGUAGE_SPECS.keys()),
        choices=list(LANGUAGE_SPECS.keys()),
        help="Target languages to generate (default: python, javascript, csharp, go).",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "generated_swig"),
        help="Output directory for generated bindings.",
    )
    parser.add_argument(
        "--swig",
        default=shutil.which("swig") or "swig",
        help="Path to swig executable.",
    )
    args = parser.parse_args(argv)

    out_base = Path(args.out_dir).resolve()
    out_base.mkdir(parents=True, exist_ok=True)

    for lang in args.languages:
        wrapper = generate_language(args.swig, lang, out_base)
        files = sorted(p.name for p in wrapper.parent.iterdir())
        print(
            f"[SWIG:{lang}] Generated {len(files)} file(s) in {wrapper.parent}: {', '.join(files)}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
