#!/usr/bin/env python3
"""Build a deterministic PRIVATE reviewer bundle; never a public data release.

The explicit allowlists intentionally fail when source/report files are missing
or candidate/private directory contents change. No broad directory packaging,
network access, extraction, or manuscript modification is performed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from io import BytesIO, StringIO
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "PFFLS_FAIRBANKS_RECEIVED_DATA_AND_AUTHOR_CANDIDATE_PRIVATE_RETURN"
FIXED_ZIP_TIME = (2026, 9, 25, 0, 0, 0)
EXPECTED_ZIP_SHA256 = "e0498220b12ef493bd3d3a16fa27c17becefd8495f0123463a78053cc85d05ac"
EXPECTED_ORIGINAL_MEMBERS = {"Fairbanks summary 08-11_cpp.xlsx", "LevoglucosanResults_final1.xlsx"}
ORIGINAL_ZIP_NAME = "Fairbanks_original_received_attachment.zip"
REPOSITORY_FILES = (
    "README.md",
    "CODEX.md",
    "PROJECT_STATE.md",
    "scripts/audit_received_fairbanks.py",
    "scripts/build_received_fairbanks_return.py",
    "scripts/extract_cycle02_fairbanks.py",
    "tests/test_received_fairbanks.py",
    "tests/test_received_fairbanks_package.py",
    "tests/test_cycle02_fairbanks.py",
    "outputs/cycle02/appendix_c_2008_2009_daily.csv",
    "outputs/cycle02/artifact_manifest_sha256.csv",
    "outputs/received_fairbanks/aggregate_summary.json",
    "outputs/received_fairbanks/AUDIT_REPORT.md",
    "outputs/received_fairbanks/README.md",
    "outputs/received_fairbanks/AUTHOR_CHANGE_NOTE.md",
    "outputs/received_fairbanks/VALIDATION.md",
)
PRIVATE_FILES = (
    "aggregate_summary.json", "both_marker_overlap.csv", "levoglucosan_comparisons.csv",
    "levoglucosan_exclusions.csv", "levoglucosan_rows.csv", "radiocarbon_comparisons.csv",
    "radiocarbon_exclusions.csv", "sensitivity_levo_CF_13_3.csv", "sensitivity_levo_native_PM.csv",
    "sensitivity_levo_partial_brackets.csv", "sensitivity_levo_recomputed.csv",
    "sensitivity_radiocarbon_native_PM.csv", "summary_rows.csv",
)
CANDIDATE_FILES = (
    "PFFLS_R3nR8_Author_Update_Candidate_Manuscript_PLUS_Supplement.pdf",
    "PFFLS_R3nR8_Author_Update_Candidate_Overleaf_Source.zip",
    "CHANGE_NOTE.md", "QA_REPORT.json", "SHA256SUMS.txt",
)
PACKAGE_README = """# NOT PUBLIC — private independent-review bundle

This archive contains investigator-supplied Fairbanks spreadsheets, sample-level
derived records, and an author-update manuscript candidate. It is intended only
for the authorized project team and independent reviewer. Do not post this ZIP,
its original attachment, private row-level CSVs, or manuscript candidate in a
public repository. Data use and redistribution permissions remain to be clarified.

## Contents

- repository/: public-safe audit code, synthetic tests, reports, aggregate results,
  and the corrected historical Cycle 02 extraction artifacts.
- private_data/original/: the exact hash-verified investigator attachment ZIP.
- private_data/derived/: privately derived records and cell/formula provenance.
- manuscript_candidate/: exactly the five supplied author-update candidate files.
- artifact_manifest_sha256.csv: byte length and SHA-256 for every other member.

The repository code and tests contain no investigator-supplied raw rows. The
original attachment is included here only for authorized private reproduction.
Read repository/outputs/received_fairbanks/README.md and AUDIT_REPORT.md first.

## Scientific and authorship boundaries

The strict source-native levoglucosan comparison has 52 complete marker brackets.
The 53-row partial-endpoint fill and 54-row full arithmetic reconstruction are
separately labeled sensitivities, not additional complete source observations.
Missing endpoint reasons are unknown. EPA/OMNI source universes differ, and these
comparisons do not establish an externally validated profile-choice winner.
The author-update manuscript is a candidate requiring author review; it does not
silently promote a baseline or establish author approval/consent.

## Reproduction and integrity

Use the audit CLI on the original attachment with output restricted to the
repository's private/received_fairbanks directory. It requires openpyxl; the
archive builder itself uses Python's standard library only. The supplied audit
README contains the command template. Native spreadsheet formulas are preserved
as evidence; no embedded formulas, macros, or attachments are executed.

ZIP member times and ordering are fixed. The manifest excludes itself to avoid a
recursive hash; the separate ZIP SHA-256 sidecar covers the whole archive.
Cycle 02's historical manifest is included as archival context and lists some
files intentionally not copied into this focused private return. The return's
own artifact manifest is authoritative for this archive's contents.
"""


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def safe_member(name):
    if not name or "\\" in name or name.startswith("/"):
        raise ValueError("Unsafe ZIP member path")
    parts = name.rstrip("/").split("/")
    if any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ValueError("Unsafe ZIP member path")
    if PurePosixPath(name).is_absolute():
        raise ValueError("Absolute ZIP member path")
    return name


def checked_path(path):
    path = Path(path)
    if ".." in path.parts:
        raise ValueError("Path traversal is not allowed")
    absolute = path.absolute()
    for part in (absolute, *absolute.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError("Symlink/junction paths are not allowed")
    return absolute.resolve()


def exact_directory(directory, expected):
    directory = checked_path(directory)
    if not directory.is_dir():
        raise ValueError("Required directory does not exist")
    names = {path.name for path in directory.iterdir()}
    if names != set(expected):
        raise ValueError(f"Unexpected/missing directory files: extra={sorted(names-set(expected))}, missing={sorted(set(expected)-names)}")
    paths = {}
    for name in expected:
        path = checked_path(directory / name)
        if not path.is_file() or path.parent != directory:
            raise ValueError("Allowlisted directory entry is not a regular contained file")
        paths[name] = path
    return paths


def validate_zip_bytes(blob, expected_members=None):
    with zipfile.ZipFile(BytesIO(blob)) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP member")
        for item in infos:
            safe_member(item.filename)
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("ZIP symlink entry")
            if item.flag_bits & 1:
                raise ValueError("Encrypted ZIP member is not auditable")
        if expected_members is not None and set(names) != set(expected_members):
            raise ValueError("Unexpected original attachment members")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC integrity failure")


def validate_candidate(paths):
    manifest = paths["SHA256SUMS.txt"].read_text(encoding="utf-8-sig")
    expected = set(CANDIDATE_FILES) - {"SHA256SUMS.txt"}
    found = {}
    for line in manifest.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})  (.+)", line)
        if match is None:
            raise ValueError("Malformed candidate SHA256SUMS")
        digest, name = match.groups()
        safe_member(name)
        if name not in expected or name in found:
            raise ValueError("Unexpected/duplicate candidate manifest member")
        if sha256(paths[name].read_bytes()) != digest.lower():
            raise ValueError("Candidate SHA256 mismatch")
        found[name] = digest
    if set(found) != expected:
        raise ValueError("Candidate manifest does not cover exactly four payload files")
    for name, path in paths.items():
        if name.endswith(".zip"):
            validate_zip_bytes(path.read_bytes())


def payloads(root, input_zip, candidate_dir):
    root, source = checked_path(root), checked_path(input_zip)
    if not source.is_file():
        raise ValueError("Original attachment missing")
    original = source.read_bytes()
    if sha256(original) != EXPECTED_ZIP_SHA256:
        raise ValueError("Original attachment SHA256 mismatch")
    validate_zip_bytes(original, EXPECTED_ORIGINAL_MEMBERS)
    candidates = exact_directory(candidate_dir, CANDIDATE_FILES)
    validate_candidate(candidates)
    private = exact_directory(root / "private/received_fairbanks/independent_reproduction", PRIVATE_FILES)
    contents = {"README.md": PACKAGE_README.encode("utf-8")}
    for relative in REPOSITORY_FILES:
        safe_member(relative)
        path = checked_path(root / relative)
        if not path.is_file() or root not in path.parents:
            raise ValueError(f"Required repository file missing: {relative}")
        contents[f"repository/{relative}"] = path.read_bytes()
    if private["aggregate_summary.json"].read_bytes() != contents["repository/outputs/received_fairbanks/aggregate_summary.json"]:
        raise ValueError("Private/public aggregate summaries differ")
    for name, path in private.items():
        contents[f"private_data/derived/{name}"] = path.read_bytes()
    for name, path in candidates.items():
        contents[f"manuscript_candidate/{name}"] = path.read_bytes()
    contents[f"private_data/original/{ORIGINAL_ZIP_NAME}"] = original
    # Reject accidentally pasted user-machine paths in prose/JSON, without
    # treating literal path-security test strings in Python code as disclosures.
    for name, content in contents.items():
        safe_member(name)
        if name.endswith((".md", ".json", ".txt")):
            text = content.decode("utf-8-sig")
            if re.search(r"(?i)[a-z]:[\\/](?:users|documents and settings)[\\/]|/(?:home|Users)/", text):
                raise ValueError("Local absolute user path leaked into packaged text")
    return contents


def manifest_bytes(contents):
    handle = StringIO(newline="")
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(("relative_path", "bytes", "sha256"))
    for name, blob in sorted(contents.items()):
        writer.writerow((safe_member(name), len(blob), sha256(blob)))
    return handle.getvalue().encode("utf-8")


def verify_return(path, contents):
    blob = Path(path).read_bytes()
    expected = {f"{PACKAGE_NAME}/{name}" for name in contents}
    validate_zip_bytes(blob, expected)
    with zipfile.ZipFile(BytesIO(blob)) as archive:
        for name, content in contents.items():
            if archive.read(f"{PACKAGE_NAME}/{name}") != content:
                raise ValueError("Return payload differs after compression")
        manifest = archive.read(f"{PACKAGE_NAME}/artifact_manifest_sha256.csv").decode("utf-8")
        rows = list(csv.DictReader(StringIO(manifest)))
        payload_names = set(contents) - {"artifact_manifest_sha256.csv"}
        if len(rows) != len(payload_names) or {r["relative_path"] for r in rows} != payload_names:
            raise ValueError("Return manifest coverage mismatch")
        for row in rows:
            data = archive.read(f"{PACKAGE_NAME}/{safe_member(row['relative_path'])}")
            if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
                raise ValueError("Return member hash mismatch")
    return sha256(blob)


def build(root, input_zip, candidate_dir, output_dir):
    root, output = checked_path(root), checked_path(output_dir)
    allowed = root / "private/received_fairbanks/return"
    if output != allowed and allowed not in output.parents:
        raise ValueError("Return output must remain below private/received_fairbanks/return")
    contents = payloads(root, input_zip, candidate_dir)
    contents["artifact_manifest_sha256.csv"] = manifest_bytes(contents)
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{PACKAGE_NAME}.zip"
    sidecar = output / f"{PACKAGE_NAME}.zip.sha256.txt"
    checked_path(target)
    checked_path(sidecar)
    with tempfile.NamedTemporaryFile(prefix=".private-return-", suffix=".zip", dir=output, delete=False) as temporary:
        staging = Path(temporary.name)
    try:
        with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, blob in sorted(contents.items()):
                item = zipfile.ZipInfo(f"{PACKAGE_NAME}/{name}", FIXED_ZIP_TIME)
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | 0o644) << 16
                item.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(item, blob, compresslevel=9)
        digest = verify_return(staging, contents)
        sidecar_content = f"{digest}  {target.name}\n"
        if target.exists() and sha256(target.read_bytes()) != digest:
            raise ValueError("Existing private return differs; choose a new output subdirectory")
        if sidecar.exists() and sidecar.read_text(encoding="ascii") != sidecar_content:
            raise ValueError("Existing SHA sidecar differs; choose a new output subdirectory")
        if not target.exists():
            staging.replace(target)
        if not sidecar.exists():
            sidecar.write_text(sidecar_content, encoding="ascii")
        return target, sidecar, digest, len(contents) - 1
    finally:
        if staging.exists():
            staging.unlink()  # Only this invocation's validated temporary file.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-zip", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    archive, sidecar, digest, count = build(ROOT, args.input_zip, args.candidate_dir, args.output_dir)
    print(f"PRIVATE return: {archive.name}\nSHA256: {digest}\nManifest payload members: {count}\nSidecar: {sidecar.name}")


if __name__ == "__main__":
    main()
