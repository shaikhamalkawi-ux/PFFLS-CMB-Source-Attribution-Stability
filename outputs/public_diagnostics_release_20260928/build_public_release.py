"""Explicit public allowlist packager; no fits, tests, network, or source edits."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

RELEASE = "outputs/public_diagnostics_release_20260928"
SCIENCE = "outputs/continuous_research_20260927/editor_response_20260928"
UPSTREAM = "outputs/journal_editorial_20260926/publication_derived/derived_data"
ARCHIVE = "PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip"
TITLE = "PFFLS source-profile sensitivity diagnostics: JRC family structure and EPA rank margins"
PINS = {
    "scripts/summarize_epa_rank_margins.py": "06f30d2316331f1ceefec5d2bf39b57012cc4a35a6a24a8f66a0afd569b44130",
    "tests/test_epa_rank_margins.py": "12d643e3da557d67461ed8323d343882a46ee238e212e3544e2298fcda2aec6b",
    f"{SCIENCE}/audit_jrc_family_structure.py": "9429a4b32ed0dbe0ad2db68f57636db078efaa803f69941898a527f26212f186",
    f"{SCIENCE}/test_jrc_family_structure_independent.py": "b63d1b392a3f4f81ea599561c6c0598ddd4fd2c4681bd844da9bdc7016dea952",
    f"{SCIENCE}/JRC_FAMILY_RESULT.json": "9a27b3b19a22e099a2fca45090c35741cba61570c736900ee4648c552194df31",
    f"{SCIENCE}/JRC_FAMILY_RESULT.md": "c3472f80c76e4eddb089dd5c87ea1272f233171547bdcbd8b01cbbc225fd0d10",
    f"{SCIENCE}/epa_rank_margins_summary.json": "fcfa9c2783234bd10ed7b56c41eedb9b307b12e9dae76b44a27630e2c11975c4",
    f"{SCIENCE}/EPA_RANK_MARGINS.md": "762903a1da8e5e316caca49de3b4fad7223fd8ca8a77f637f12aceffdd8eccc9",
    f"{UPSTREAM}/jrc_12set_landscape.csv": "b1f0081b9e8943b1e13a09a9ece7c79aca373bff4b4f2e702eb65a1689333356",
    f"{UPSTREAM}/jrc_profile_choice_edges_reconstructed.csv": "9695d1d70ae7f48bc14ee7e51dcd49c99ee82f13ffb7f7529072b18107adca36",
    f"{SCIENCE}/LICENSE_CODE_MIT.txt": "80efd532702d24e3a10672b8f5bcb64ecc6839d9ed0723b48cb6b532bafa4c0e",
}
DOCS = ("README.md", "CITATION.cff", "LICENSE_SCOPE.md", "UPSTREAM_ATTRIBUTION.md",
        "DEPENDENCIES.md", "RELEASE_REVIEW.md")
OWN_CODE = ("build_public_release.py", "verify_public_release.py")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def normal_path(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or "\\" in value or ":" in value or path.is_absolute()
            or ".." in path.parts or str(path) != value):
        raise ValueError(f"Unsafe archive path: {value}")
    return value


def read_source(repository: Path, relative: str) -> bytes:
    source = repository.joinpath(*PurePosixPath(normal_path(relative)).parts)
    if source.is_symlink() or any(p.is_symlink() for p in source.parents if p != repository.parent):
        raise ValueError(f"Symlink source refused: {relative}")
    if not source.resolve().is_relative_to(repository):
        raise ValueError(f"Source escaped repository: {relative}")
    return source.read_bytes()


def specification():
    # Every member is explicitly named. No traversal-based or glob-based inclusion.
    records = []
    for path in PINS:
        if path.endswith("/LICENSE_CODE_MIT.txt"):
            records.append((path, "LICENSE_CODE_MIT.txt", "preserved copyright/license notice", "MIT", "PFFLS research contributors"))
        elif path.endswith(".py"):
            records.append((path, path, "unchanged scientific code or artificial-fixture test", "MIT", "PFFLS research contributors"))
        elif path.startswith(UPSTREAM + "/"):
            records.append((path, path, "unchanged upstream publication-derived table", "CC-BY-4.0", "Malkawi; Elsayed; Alhagyan; Hussein; doi:10.5281/zenodo.22976190"))
        else:
            records.append((path, path, "unchanged saved descriptive aggregate", "CC-BY-4.0", "PFFLS diagnostics increment; original scientific bytes preserved"))
    records += [(f"{RELEASE}/{name}", name, "new release documentation", "CC-BY-4.0", "Ghassan O. Malkawi") for name in DOCS]
    records += [(f"{RELEASE}/{name}", name, "new public packaging/verification code", "MIT", "Ghassan O. Malkawi; preserve included MIT notice") for name in OWN_CODE]
    return records


def build(repository: Path, output: Path):
    repository, output = repository.resolve(strict=True), output.resolve()
    if not repository.is_dir() or not output.is_relative_to(repository / RELEASE):
        raise ValueError("Output must be inside the new public release directory")
    targets = [output / ARCHIVE, output / (ARCHIVE + ".sha256"), output / "PUBLIC_BUILD_RECEIPT.json"]
    if any(path.exists() for path in targets):
        raise FileExistsError("Preserve an existing build; no overwrite or status-only rebuild")
    payloads, inventory = {}, []
    for source, member, role, license_id, attribution in specification():
        normal_path(member)
        if member.casefold() in {name.casefold() for name in payloads}:
            raise ValueError("Duplicate archive member")
        data = read_source(repository, source)
        digest = sha(data)
        if source in PINS and digest != PINS[source]:
            raise ValueError(f"Pinned scientific source changed: {source}")
        payloads[member] = data
        inventory.append({"path": member, "bytes": len(data), "sha256": digest,
                          "role": role, "license": license_id, "attribution": attribution,
                          "source_repository_path": source})
    record = {"schema_version": 1, "title": TITLE, "version": "1.0.0", "date": "2026-09-28",
              "release_creator": "Ghassan O. Malkawi", "doi_reserved": "10.5281/zenodo.23019083",
              "upstream_doi": "10.5281/zenodo.22976190", "payloads": inventory,
              "scope": "No manuscript, raw data, private ledger, native fits, or claim of complete native reproduction",
              "manifest_scope": "All payloads and this inventory; manifest excludes itself; external sidecar covers ZIP"}
    payloads["PACKAGE_INVENTORY.json"] = encoded(record)
    payloads["SHA256SUMS"] = "".join(f"{sha(data)}  {name}\n" for name, data in sorted(payloads.items())).encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(targets[0], "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payloads.items()):
            info = ZipInfo(name, date_time=(2026, 9, 28, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    digest = sha(targets[0].read_bytes())
    with targets[1].open("x", encoding="ascii", newline="\n") as handle:
        handle.write(f"{digest}  {ARCHIVE}\n")
    receipt = {"created_utc": datetime.now(timezone.utc).isoformat(), "archive": ARCHIVE,
               "bytes": targets[0].stat().st_size, "sha256": digest,
               "payload_count": len(inventory), "member_count": len(payloads),
               "scientific_sources_modified": False, "fits": 0, "tests_executed": 0,
               "public_verification_executed": False, "uploaded": False}
    with targets[2].open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded(receipt).decode("utf-8"))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.repository, args.output_dir), indent=2))
