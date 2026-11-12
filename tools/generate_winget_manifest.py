#!/usr/bin/env python3
"""Generate WinGet (Windows Package Manager) community repository manifests.

Produces valid multi-file manifests (version, installer, defaultLocale) conforming to
WinGet manifest specification 1.6.0 for submission to microsoft/winget-pkgs.
"""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PACKAGE_ID = "carlkidcrypto.PurpleAirDataLogger"
DEFAULT_PACKAGE_NAME = "PurpleAir Data Logger"
DEFAULT_PUBLISHER = "carlkidcrypto"
DEFAULT_PUBLISHER_URL = "https://github.com/carlkidcrypto"
MANIFEST_VERSION = "1.6.0"


def _read_current_calsemver() -> str:
    version_file = REPO_ROOT / "src" / "version.cpp"
    if version_file.is_file():
        text = version_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "PROJECT_VERSION_STRING" in line and '"' in line:
                raw = line.split('"')[1].strip()
                if "a" in raw and "-" not in raw:
                    prefix, num = raw.split("a", 1)
                    return f"{prefix}-alpha.{num}"
                return raw
    return "2026.11.3-alpha.0"


def get_canonical_manifest_dir(
    package_id: str,
    package_version: str,
    out_dir: Path,
) -> Path:
    """Return canonical WinGet directory: manifests/{first-letter}/{Publisher}/{AppName}/{Version}/"""
    parts = package_id.split(".", 1)
    publisher = parts[0]
    app_name = parts[1] if len(parts) > 1 else package_id
    first_letter = publisher[0].lower()

    if out_dir.name.lower() == "manifests":
        return out_dir / first_letter / publisher / app_name / package_version
    return out_dir / "manifests" / first_letter / publisher / app_name / package_version


def compute_sha256(path_or_url: str) -> str:
    """Compute the lowercase SHA256 hex digest of a local file or remote URL."""
    p = Path(path_or_url)
    h = hashlib.sha256()
    if p.is_file():
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest().lower()

    dist_candidate = REPO_ROOT / "dist" / p.name
    if dist_candidate.is_file():
        with open(dist_candidate, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest().lower()

    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        import ssl

        ctx = ssl.create_default_context()
        try:
            import certifi

            ctx.load_verify_locations(certifi.where())
        except Exception:
            pass

        try:
            req = urllib.request.Request(
                path_or_url, headers={"User-Agent": "winget-manifest-gen/1.0"}
            )
            with urllib.request.urlopen(req, context=ctx) as resp:
                while chunk := resp.read(65536):
                    h.update(chunk)
            return h.hexdigest().lower()
        except Exception:
            return "0000000000000000000000000000000000000000000000000000000000000000"

    raise FileNotFoundError(f"Cannot compute hash for: {path_or_url}")


def generate_manifests(
    package_id: str = DEFAULT_PACKAGE_ID,
    package_version: str = "",
    installer_url: str = "",
    installer_sha256: str = "",
    out_dir: Path | None = None,
    architecture: str = "x64",
    installer_type: str = "auto",
) -> dict[str, Path]:
    """Generate the 3 canonical WinGet manifest YAML files."""
    if not package_version:
        package_version = _read_current_calsemver()

    if out_dir is None:
        out_dir = REPO_ROOT / "dist-winget"

    dest = get_canonical_manifest_dir(package_id, package_version, out_dir)
    dest.mkdir(parents=True, exist_ok=True)

    if not installer_url:
        installer_url = (
            f"https://github.com/carlkidcrypto/purpleair_data_logger/releases/download/"
            f"v{package_version}/PurpleAirDataLogger-Windows-x64-Setup.exe"
        )

    resolved_type = (installer_type or "auto").strip().lower()
    if resolved_type in ("", "auto"):
        resolved_type = "zip" if installer_url.lower().endswith(".zip") else "inno"

    if not installer_sha256:
        installer_sha256 = (
            "0000000000000000000000000000000000000000000000000000000000000000"
            if not installer_url.startswith("http")
            and not Path(installer_url).is_file()
            else compute_sha256(installer_url)
        )

    version_yaml = (
        f"PackageIdentifier: {package_id}\n"
        f"PackageVersion: {package_version}\n"
        "DefaultLocale: en-US\n"
        "ManifestType: version\n"
        f"ManifestVersion: {MANIFEST_VERSION}\n"
    )

    locale_yaml = (
        f"PackageIdentifier: {package_id}\n"
        f"PackageVersion: {package_version}\n"
        "PackageLocale: en-US\n"
        f"Publisher: {DEFAULT_PUBLISHER}\n"
        f"PublisherUrl: {DEFAULT_PUBLISHER_URL}\n"
        "PublisherSupportUrl: https://github.com/carlkidcrypto/purpleair_data_logger/issues\n"
        f"Author: {DEFAULT_PUBLISHER}\n"
        f"PackageName: {DEFAULT_PACKAGE_NAME}\n"
        "PackageUrl: https://carlkidcrypto.github.io/purpleair_data_logger/\n"
        "License: MIT\n"
        "LicenseUrl: https://raw.githubusercontent.com/carlkidcrypto/purpleair_data_logger/main/LICENSE\n"
        "Copyright: Copyright (c) 2023-2026 carlkidcrypto\n"
        "CopyrightUrl: https://raw.githubusercontent.com/carlkidcrypto/purpleair_data_logger/main/LICENSE\n"
        "ShortDescription: Self-contained C++17 PurpleAir Data Logger with SWIG bindings, CLI, and GUI Studio.\n"
        "Description: |-\n"
        "  PurpleAir Data Logger provides high-performance PurpleAir air-quality telemetry\n"
        "  ingestion, local storage sinks (SQLite3, JSONL, CSV, Prometheus, PostgreSQL), and\n"
        "  unified CLI/GUI operation across Windows, Linux, and macOS.\n"
        "Moniker: purpleair-data-logger\n"
        "Tags:\n"
        "  - purpleair\n"
        "  - air-quality\n"
        "  - telemetry\n"
        "  - data-logger\n"
        "  - monitoring\n"
        "ManifestType: defaultLocale\n"
        f"ManifestVersion: {MANIFEST_VERSION}\n"
    )

    if resolved_type == "inno":
        installer_yaml = (
            f"PackageIdentifier: {package_id}\n"
            f"PackageVersion: {package_version}\n"
            "InstallerLocale: en-US\n"
            "Platform:\n"
            "  - Windows.Desktop\n"
            "MinimumOSVersion: 10.0.0.0\n"
            "InstallerType: inno\n"
            "Scope: user\n"
            "InstallModes:\n"
            "  - interactive\n"
            "  - silent\n"
            "  - silentWithProgress\n"
            "InstallerSwitches:\n"
            "  Silent: /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-\n"
            "  SilentWithProgress: /SILENT /SUPPRESSMSGBOXES /NORESTART /SP-\n"
            "UpgradeBehavior: install\n"
            "AppsAndFeaturesEntries:\n"
            "  - DisplayName: PurpleAir Data Logger\n"
            "    Publisher: carlkidcrypto\n"
            f"    DisplayVersion: {package_version}\n"
            "    ProductCode: '{B7C9F812-3D4A-491B-8E72-554F912A6D3C}_is1'\n"
            "Installers:\n"
            f"  - Architecture: {architecture}\n"
            f"    InstallerUrl: {installer_url}\n"
            f"    InstallerSha256: {installer_sha256.upper()}\n"
            "ManifestType: installer\n"
            f"ManifestVersion: {MANIFEST_VERSION}\n"
        )
    else:
        installer_yaml = (
            f"PackageIdentifier: {package_id}\n"
            f"PackageVersion: {package_version}\n"
            "InstallerLocale: en-US\n"
            "Platform:\n"
            "  - Windows.Desktop\n"
            "MinimumOSVersion: 10.0.0.0\n"
            "InstallerType: zip\n"
            "NestedInstallerType: portable\n"
            "NestedInstallerFiles:\n"
            "  - RelativeFilePath: PurpleAirDataLogger.exe\n"
            "    PortableCommandAlias: PurpleAirDataLogger\n"
            "  - RelativeFilePath: purpleair-data-logger.exe\n"
            "    PortableCommandAlias: purpleair-data-logger\n"
            "Installers:\n"
            f"  - Architecture: {architecture}\n"
            f"    InstallerUrl: {installer_url}\n"
            f"    InstallerSha256: {installer_sha256.upper()}\n"
            "ManifestType: installer\n"
            f"ManifestVersion: {MANIFEST_VERSION}\n"
        )

    version_path = dest / f"{package_id}.yaml"
    locale_path = dest / f"{package_id}.locale.en-US.yaml"
    installer_path = dest / f"{package_id}.installer.yaml"

    version_path.write_text(version_yaml, encoding="utf-8")
    locale_path.write_text(locale_yaml, encoding="utf-8")
    installer_path.write_text(installer_yaml, encoding="utf-8")

    return {
        "version": version_path,
        "locale": locale_path,
        "installer": installer_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate WinGet manifests.")
    parser.add_argument("--package-id", default=DEFAULT_PACKAGE_ID)
    parser.add_argument("--version", default="")
    parser.add_argument(
        "--installer-url",
        default="",
        help="Download URL of installer executable or portable zip",
    )
    parser.add_argument("--sha256", default="")
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "dist-winget"))
    parser.add_argument("--arch", default="x64")
    parser.add_argument(
        "--installer-type",
        default="auto",
        choices=["auto", "inno", "zip"],
        help="Installer type: inno (default for .exe) or zip (for portable .zip)",
    )
    args = parser.parse_args(argv)

    ver = args.version or _read_current_calsemver()
    installer_url = args.installer_url or (
        f"https://github.com/carlkidcrypto/purpleair_data_logger/releases/download/"
        f"v{ver}/PurpleAirDataLogger-Windows-x64-Setup.exe"
    )

    sha = args.sha256 or (
        "0000000000000000000000000000000000000000000000000000000000000000"
        if not installer_url.startswith("http") and not Path(installer_url).is_file()
        else compute_sha256(installer_url)
    )

    out = Path(args.out_dir)
    res = generate_manifests(
        package_id=args.package_id,
        package_version=ver,
        installer_url=installer_url,
        installer_sha256=sha,
        out_dir=out,
        architecture=args.arch,
        installer_type=args.installer_type,
    )

    print(f"Generated WinGet manifests for {args.package_id} v{ver}:")
    for k, p in res.items():
        print(f"  {k}: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
