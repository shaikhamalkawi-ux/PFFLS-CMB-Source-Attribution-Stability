#!/usr/bin/env python3
"""Build the deterministic three-request outreach package and SHA-256 files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import zipfile


PACKAGE_NAME = "PFFLS_CODEX_OUTREACH_THREE_REQUESTS_RETURN"
FIXED_ZIP_TIME = (2026, 9, 21, 0, 0, 0)
MANIFEST_RELATIVE_PATH = Path("outputs") / "outreach03" / "SHA256SUMS.txt"


def digest(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def included_files(root: Path) -> list[Path]:
    manifest = root / MANIFEST_RELATIVE_PATH
    required = [
        root / "tasks" / "CODEX_OUTREACH_THREE_EVIDENCE_REQUESTS.md",
        root / "scripts" / "validate_outreach_package.py",
        root / "scripts" / "build_outreach_package.py",
        root / "tests" / "test_outreach_package.py",
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        names = ", ".join(path.relative_to(root).as_posix() for path in missing)
        raise FileNotFoundError(f"required outreach package file(s) missing: {names}")

    output_files = [
        path
        for path in (root / "outputs" / "outreach03").rglob("*")
        if path.is_file() and path != manifest
    ]
    candidates = required + output_files
    return sorted(
        set(candidates), key=lambda path: path.relative_to(root).as_posix()
    )


def write_manifest(root: Path, paths: list[Path]) -> Path:
    target = root / MANIFEST_RELATIVE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        _, value = digest(path)
        relative = path.relative_to(root).as_posix()
        lines.append(f"{value}  {relative}\n")
    target.write_bytes("".join(lines).encode("utf-8"))
    return target


def add_file(archive: zipfile.ZipFile, root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{relative}", FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, path.read_bytes(), compresslevel=9)


def build(root: Path, destination: Path) -> tuple[Path, Path]:
    paths = included_files(root)
    manifest = write_manifest(root, paths)
    paths.append(manifest)
    paths = sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())

    destination.mkdir(parents=True, exist_ok=True)
    zip_path = destination / f"{PACKAGE_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in paths:
            add_file(archive, root, path)

    _, value = digest(zip_path)
    sha_path = destination / f"{zip_path.name}.sha256.txt"
    sha_path.write_text(f"{value}  {zip_path.name}\n", encoding="ascii")
    return zip_path, sha_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    zip_path, sha_path = build(root, args.destination.resolve())
    print(zip_path)
    print(sha_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
