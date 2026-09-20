#!/usr/bin/env python3
"""Build the deterministic Cycle 02 review package and manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import zipfile


PACKAGE_NAME = "PFFLS_CODEX_CYCLE02_FAIRBANKS_RETURN_20260920"
FIXED_ZIP_TIME = (2026, 9, 20, 0, 0, 0)


def digest(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def included_files(root: Path) -> list[Path]:
    manifest = root / "outputs" / "cycle02" / "artifact_manifest_sha256.csv"
    candidates = [
        root / "tasks" / "CODEX_CYCLE_02_FAIRBANKS.md",
        *sorted((root / "outputs" / "cycle02").glob("*")),
        root / "scripts" / "extract_cycle02_fairbanks.py",
        root / "scripts" / "build_cycle02_package.py",
        root / "tests" / "test_cycle02_fairbanks.py",
    ]
    return [path for path in candidates if path.is_file() and path != manifest]


def write_manifest(root: Path, paths: list[Path]) -> Path:
    target = root / "outputs" / "cycle02" / "artifact_manifest_sha256.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("relative_path", "bytes", "sha256"))
        for path in paths:
            size, value = digest(path)
            writer.writerow((path.relative_to(root).as_posix(), size, value))
    return target


def add_file(archive: zipfile.ZipFile, root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{relative}", FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, path.read_bytes())


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
