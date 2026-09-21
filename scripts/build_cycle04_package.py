#!/usr/bin/env python3
"""Build the fail-closed deterministic Cycle 04 review package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path
import tempfile
import zipfile

from validate_cycle04_submission_gate import (
    ALLOWED_OUTPUT_FILES,
    MANIFEST_RELATIVE_PATH as MANIFEST_RELATIVE_PATH_STRING,
    PACKAGE_PAYLOAD_RELATIVE_PATHS,
    RESTRICTED_SUFFIXES,
    canonical_report_bytes,
    validate_repository,
    validate_return_package,
)


PACKAGE_NAME = "PFFLS_CODEX_CYCLE04_SUBMISSION_GATE_RETURN"
FIXED_ZIP_TIME = (2026, 9, 21, 0, 0, 0)
MANIFEST_RELATIVE_PATH = Path(MANIFEST_RELATIVE_PATH_STRING)
PACKAGE_RELATIVE_PATHS = tuple(Path(path) for path in PACKAGE_PAYLOAD_RELATIVE_PATHS)


def digest(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def _ensure_within_root(root: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"package path escapes repository root: {path}") from exc


def included_files(root: Path) -> list[Path]:
    root = root.resolve()
    output_root = root / "outputs" / "cycle04"
    actual_output_names = {
        path.relative_to(output_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file()
    }
    unexpected_output = sorted(actual_output_names.difference(ALLOWED_OUTPUT_FILES))
    if unexpected_output:
        raise ValueError(f"unexpected Cycle 04 output file(s): {unexpected_output}")

    paths = [root / relative for relative in PACKAGE_RELATIVE_PATHS]
    missing = [
        path.relative_to(root).as_posix() for path in paths if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"required Cycle 04 package file(s) missing: {missing}")

    for path in paths:
        _ensure_within_root(root, path)
        if path.is_symlink():
            raise ValueError(f"symbolic links are forbidden in the package: {path}")
        if path.suffix.casefold() in RESTRICTED_SUFFIXES:
            raise ValueError(f"restricted artifact is forbidden in the package: {path}")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def manifest_bytes(root: Path, paths: list[Path]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(("relative_path", "bytes", "sha256"))
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        size, value = digest(path)
        writer.writerow((path.relative_to(root).as_posix(), size, value))
    return buffer.getvalue().encode("utf-8")


def write_manifest(root: Path, paths: list[Path]) -> Path:
    target = root / MANIFEST_RELATIVE_PATH
    target.write_bytes(manifest_bytes(root, paths))
    return target


def verify_manifest(root: Path, paths: list[Path]) -> Path:
    target = root / MANIFEST_RELATIVE_PATH
    if not target.is_file():
        raise FileNotFoundError(
            "Cycle 04 artifact manifest is missing; rerun with --refresh-manifest"
        )
    expected = manifest_bytes(root, paths)
    if target.read_bytes() != expected:
        raise ValueError(
            "Cycle 04 artifact manifest does not match the payload; "
            "review changes, then rerun with --refresh-manifest"
        )
    return target


def verify_qa_snapshot(root: Path, report: dict[str, object]) -> None:
    target = root / "outputs" / "cycle04" / "qa_report.json"
    if not target.is_file():
        raise FileNotFoundError("Cycle 04 qa_report.json is missing")
    if target.read_bytes() != canonical_report_bytes(report):
        raise ValueError(
            "Cycle 04 qa_report.json is stale; rerun the validator with --write-report"
        )


def add_file(archive: zipfile.ZipFile, root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{relative}", FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, path.read_bytes())


def build(
    root: Path, destination: Path, *, refresh_manifest: bool = False
) -> tuple[Path, Path]:
    root = root.resolve()
    destination = destination.resolve()
    controlled_output = (root / "outputs" / "cycle04").resolve()
    try:
        destination.relative_to(controlled_output)
    except ValueError:
        pass
    else:
        raise ValueError(
            "package destination must not be at or below outputs/cycle04"
        )
    report = validate_repository(root)
    verify_qa_snapshot(root, report)

    paths = included_files(root)
    manifest = (
        write_manifest(root, paths)
        if refresh_manifest
        else verify_manifest(root, paths)
    )
    archive_paths = sorted(
        paths + [manifest], key=lambda path: path.relative_to(root).as_posix()
    )

    destination.mkdir(parents=True, exist_ok=True)
    zip_path = destination / f"{PACKAGE_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in archive_paths:
            add_file(archive, root, path)

    _, value = digest(zip_path)
    sha_path = destination / f"{zip_path.name}.sha256.txt"
    sha_path.write_text(f"{value}  {zip_path.name}\n", encoding="ascii", newline="\n")

    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("built Cycle 04 ZIP failed its integrity check")
        expected_members = {
            f"{PACKAGE_NAME}/{path.relative_to(root).as_posix()}"
            for path in archive_paths
        }
        if set(archive.namelist()) != expected_members:
            raise ValueError("built Cycle 04 ZIP membership differs from the allowlist")
        with tempfile.TemporaryDirectory() as directory:
            archive.extractall(directory)
            validate_return_package(Path(directory) / PACKAGE_NAME)
    return zip_path, sha_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--refresh-manifest",
        action="store_true",
        help="Refresh the tracked Cycle 04 artifact manifest before building.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    zip_path, sha_path = build(
        root, args.destination, refresh_manifest=args.refresh_manifest
    )
    print(zip_path)
    print(sha_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
