#!/usr/bin/env python3
"""Fail-closed validation for the Cycle 04 submission-candidate gate.

The successful scientific outcome may be HOLD.  Validation fails only when the
audited record drifts from the locked numbers, evidence boundaries, provenance,
or package restrictions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_ROOT = REPOSITORY_ROOT / "outputs" / "cycle04"
LOCKED_BASELINE = "PFFLS R4.3.30R3nR7-AE"
LOCKED_TITLE = (
    "Source Attribution Can Change Despite Favorable Fit Diagnostics: "
    "Evidence from Source-Profile Choice in Chemical Mass Balance"
)
ANCHOR_SHA256 = "681c04cc0d95a0b819b42f1403f601d0b0d7d1418aa9b9eff1a567615ca6eb8c"
CANDIDATE_DELTA_SHA256 = "9be0a8bc9c653b7c9517f947b145947fcb82c9a1cf2106bcd088b361d329d5e2"

CORE_OUTPUT_FILES = (
    "README.md",
    "baseline_search_manifest.csv",
    "historical_manuscript_inventory.csv",
    "historical_anchor_extraction.json",
    "LOCKED_RESULTS.json",
    "claim_evidence_traceability.csv",
    "reproducibility_gap_register.csv",
    "LINEAGE_DECISION.md",
    "CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md",
    "SUBMISSION_READINESS_MATRIX.csv",
    "KEEP_HOLD_REMOVE.md",
    "SCIENTIFIC_CHANGELOG.md",
    "EDITORIAL_RECOMMENDATION.md",
    "reproduction.md",
)
GENERATED_OUTPUT_FILES = (
    "qa_report.json",
    "test_results.txt",
    "artifact_manifest_sha256.csv",
)
ALLOWED_OUTPUT_FILES = frozenset(CORE_OUTPUT_FILES + GENERATED_OUTPUT_FILES)
PACKAGE_PAYLOAD_RELATIVE_PATHS = (
    ".gitattributes",
    "requirements-cycle04.txt",
    "tasks/CODEX_CYCLE_04_SUBMISSION_CANDIDATE_RECONSTRUCTION.md",
    "outputs/cycle04/README.md",
    "outputs/cycle04/baseline_search_manifest.csv",
    "outputs/cycle04/historical_manuscript_inventory.csv",
    "outputs/cycle04/historical_anchor_extraction.json",
    "outputs/cycle04/LOCKED_RESULTS.json",
    "outputs/cycle04/claim_evidence_traceability.csv",
    "outputs/cycle04/reproducibility_gap_register.csv",
    "outputs/cycle04/LINEAGE_DECISION.md",
    "outputs/cycle04/CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md",
    "outputs/cycle04/SUBMISSION_READINESS_MATRIX.csv",
    "outputs/cycle04/KEEP_HOLD_REMOVE.md",
    "outputs/cycle04/SCIENTIFIC_CHANGELOG.md",
    "outputs/cycle04/EDITORIAL_RECOMMENDATION.md",
    "outputs/cycle04/reproduction.md",
    "outputs/cycle04/qa_report.json",
    "outputs/cycle04/test_results.txt",
    "scripts/validate_cycle04_submission_gate.py",
    "scripts/build_cycle04_package.py",
    "tests/test_cycle04_package_local.py",
)
MANIFEST_RELATIVE_PATH = "outputs/cycle04/artifact_manifest_sha256.csv"
REVIEWED_STATIC_SHA256 = {
    ".gitattributes": "53a57c423556328e906465e0a18c8d3fbe1ac9d8d3cd267ab027244ede3045d5",
    "requirements-cycle04.txt": "bbe749e9ee4041fc88b03993741c82f3220a28a957178b2b844eb7a54dd8e219",
    "tasks/CODEX_CYCLE_04_SUBMISSION_CANDIDATE_RECONSTRUCTION.md": "14df1c74f17a117223cec1cbc2fa08cebe140a54c968c608e0355186e57ce663",
    "outputs/cycle04/README.md": "f05514548a8274366ed09546892120553b01e87d78efef6287320680980c4b20",
    "outputs/cycle04/baseline_search_manifest.csv": "42a1713c133e9e19dc56df9dc3b56e447727aa83de1506510333483120b55b49",
    "outputs/cycle04/historical_manuscript_inventory.csv": "893093a1381bf21050226ac9aa908dddcbdf5616077deb6c04a6f61ee8816b3e",
    "outputs/cycle04/historical_anchor_extraction.json": "8208b0e31883bdcde35360a38d154c94a720b59a5d1be162a659fecabc54455f",
    "outputs/cycle04/LOCKED_RESULTS.json": "2c54b438a3d5b00be1526ec99f7e5374662afe8f3debb946d04bf2161c034242",
    "outputs/cycle04/claim_evidence_traceability.csv": "f00367bac2e202fab13d3c1bf8b204ab4dee305d94aa2c25e876a230052127d7",
    "outputs/cycle04/reproducibility_gap_register.csv": "dcd04284cce0e6f109118d2a2ca0c3e4175dcc59e5db6e518025ff7d437a1f2b",
    "outputs/cycle04/LINEAGE_DECISION.md": "7453fce51c5b0a0da8e2a886d94617f3ad4a982e23ff280ec19c2b44f92e3e65",
    "outputs/cycle04/CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md": "9be0a8bc9c653b7c9517f947b145947fcb82c9a1cf2106bcd088b361d329d5e2",
    "outputs/cycle04/SUBMISSION_READINESS_MATRIX.csv": "80a87d872c8acf7cd42b2debca61d321979222a13f00d0a3b0ade00ba33ca07a",
    "outputs/cycle04/KEEP_HOLD_REMOVE.md": "c5ff9505d1633982b3706662a762ddddda7ad2f072cb33195faa89344739e933",
    "outputs/cycle04/SCIENTIFIC_CHANGELOG.md": "5ce3472643d77def4b807943b5e80c771fa7c251175b47008a197db08f66ccd1",
    "outputs/cycle04/EDITORIAL_RECOMMENDATION.md": "02ab455d68e280c2961c05926d9b9942ab230320166124205dd441b69839f632",
    "outputs/cycle04/reproduction.md": "c29b3549c57b75aadbe6c73bb75a4081e7ccea83119dcb0b197a15222373dce5",
}
RESTRICTED_SUFFIXES = {
    ".accdb",
    ".db",
    ".doc",
    ".docx",
    ".mdb",
    ".odt",
    ".pdf",
    ".rtf",
    ".sqlite",
    ".tex",
    ".xls",
    ".xlsx",
    ".zip",
}

EXPECTED_CLAIMS = {
    "JRC_DAILY_SAMPLES": 364,
    "JRC_SPECIES": 38,
    "JRC_PROFILE_SETS": 12,
    "JRC_COMPARISONS": 30,
    "JRC_DISCORDANCE": 9,
    "EPA_ELIGIBLE": 345,
    "EPA_CONVERGED": 323,
    "EPA_TWO_DIAGNOSTIC": 283,
    "EPA_ORDERING": 133,
    "EPA_LARGEST": 62,
    "EPA_STRICT_SUBSET": 26,
    "EPA_STRICT_ORDERING": 10,
    "EPA_STRICT_LARGEST": 2,
}

EXPECTED_CLAIM_SCHEMA = {
    "JRC_DAILY_SAMPLES": ("JRC", "daily_samples", None, "missing_row_level_inputs_code_and_outputs"),
    "JRC_SPECIES": ("JRC", "species", None, "missing_row_level_inputs_code_and_outputs"),
    "JRC_PROFILE_SETS": ("JRC", "frozen_profile_sets", None, "missing_exact_profile_set_archive"),
    "JRC_COMPARISONS": ("JRC", "prespecified_one_profile_comparisons", None, "missing_comparison_registry_and_outputs"),
    "JRC_DISCORDANCE": ("JRC", "primary_lower_mean_reduced_chi_square_discordances", "JRC_COMPARISONS", "missing_row_level_comparison_outputs"),
    "EPA_ELIGIBLE": ("EPA", "eligible_substitutions", None, "missing_substitution_registry"),
    "EPA_CONVERGED": ("EPA", "converged", None, "missing_run_level_outputs"),
    "EPA_TWO_DIAGNOSTIC": ("EPA", "preserved_r2_and_reduced_chi_square_ranges", None, "missing_run_level_diagnostic_outputs"),
    "EPA_ORDERING": ("EPA", "ordering_changes_within_two_diagnostic_set", "EPA_TWO_DIAGNOSTIC", "missing_source_contribution_rank_outputs"),
    "EPA_LARGEST": ("EPA", "largest_source_changes_within_two_diagnostic_set", "EPA_TWO_DIAGNOSTIC", "missing_source_contribution_rank_outputs"),
    "EPA_STRICT_SUBSET": ("EPA", "also_preserved_percent_mass", None, "missing_percent_mass_outputs"),
    "EPA_STRICT_ORDERING": ("EPA", "ordering_changes_within_strict_subset", "EPA_STRICT_SUBSET", "missing_source_contribution_rank_outputs"),
    "EPA_STRICT_LARGEST": ("EPA", "largest_source_changes_within_strict_subset", "EPA_STRICT_SUBSET", "missing_source_contribution_rank_outputs"),
}

EXPECTED_TRACE_LOCATORS = {
    "JRC_DAILY_SAMPLES": "R3l PDF p.1 abstract; p.16 Supplement S1",
    "JRC_SPECIES": "R3l PDF p.1 abstract; p.16 Supplement S1",
    "JRC_PROFILE_SETS": "R3l PDF p.1 abstract; p.19 Table S4",
    "JRC_COMPARISONS": "R3l PDF p.1 abstract; p.19 text before Table S5",
    "JRC_DISCORDANCE": "R3l PDF p.1 abstract; p.6 Table 1; p.19 Table S5",
    "EPA_ELIGIBLE": "R3l PDF p.5 Methods; p.21 Supplement S7; p.22 Table S9",
    "EPA_CONVERGED": "R3l PDF p.1 abstract; p.5 Methods; p.22 Table S9",
    "EPA_TWO_DIAGNOSTIC": "R3l PDF p.7 Results; p.22 Table S9",
    "EPA_ORDERING": "R3l PDF p.1 abstract; p.7 Results; p.22 Table S9",
    "EPA_LARGEST": "R3l PDF p.1 abstract; p.7 Results; p.22 Table S9",
    "EPA_STRICT_SUBSET": "R3l PDF p.7 Results; p.22 Table S9",
    "EPA_STRICT_ORDERING": "R3l PDF p.7 Results; p.22 Table S9",
    "EPA_STRICT_LARGEST": "R3l PDF p.7 Results; p.22 Table S9",
}

EXPECTED_HISTORICAL = {
    "R4.3.15": (
        "PFFLS_R4_3_15_Claim_First_Manuscript.pdf",
        591610,
        "48a9828fa49569d05fd589b465a31685c40489fe411963ff9083115102d35713",
    ),
    "R2": (
        "PFFLS_R4_3_30R2_Identified_Manuscript_and_Supplement.pdf",
        735468,
        "b651c93e8e69aeae49321c3c77fceb2ba08010c0a86747eee05494943edb75f3",
    ),
    "R3a": (
        "PFFLS_R4_3_30R3a_Identified_Manuscript_and_Supplement.pdf",
        591231,
        "f213f2b9c8c1976daab93e06dacf45b58ed8ad11a2e010adafe1f2a08cb9ab1d",
    ),
    "R3d": (
        "PFFLS_R4_3_30R3d_AE_Manuscript_and_Supplement.pdf",
        726180,
        "862e089497dc09ac138abf47ac6104ad862ecf1a217a6da7df64387f765b70e5",
    ),
    "R3f": (
        "PFFLS_R4_3_30R3f_AE_Manuscript_and_Supplement.pdf",
        754097,
        "0facdb80cd033305c3f112b4811679b338c460a0a0499b121a4f18aa02ca47c4",
    ),
    "R3i": (
        "PFFLS_R4_3_30R3i_AE_Manuscript_and_Supplement.pdf",
        751789,
        "6dad9b5a34fe18752e29b2a61eb76f39b216770309c5282f7738fad7f1e5ddfd",
    ),
    "R3l": (
        "PFFLS_R4_3_30R3l_AE_Manuscript_and_Supplement.pdf",
        795081,
        ANCHOR_SHA256,
    ),
}

EXPECTED_SEARCH_ROWS = {
    "drive_exact_full_version": ("1PAkw7SDbEU951HcThwr4QRb87IM1T1xD", "R4.3.30R3nR7-AE", "Drive keyword search topn=100", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "drive_exact_short_version": ("1PAkw7SDbEU951HcThwr4QRb87IM1T1xD", "R3nR7-AE", "Drive keyword search topn=100", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "drive_name_contains_r3n": ("all_accessible_drives", "name contains 'R3n'", "Drive metadata document search with raw name filter topn=100", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "drive_active_baseline": ("1dr9OYN9fAu_nbvf1TuXWSud9n3AEjYiG", "00_ACTIVE_BASELINE", "Direct folder listing top_k=100", 1, 0, "216f27fa72a7ed937d3c06f8e959f6b42065ffe0b5e03d00aa8e44f2444165d4"),
    "drive_manuscript_history": ("1nI9p7s_9MGAbrossDU9f_K3f5c1bixSn", "05_MANUSCRIPT_HISTORY", "Direct folder listing top_k=100", 5, 0, "342095b9d003c70690247c4fcaab8ce0a421c6ecf0400f1a41e8272853b52e98"),
    "drive_archive": ("1IEu-ZXTByxW_wwbuKvn2DXGVGl0vj95W", "99_ARCHIVE", "Direct folder listing top_k=100", 3, 0, "d05ea838742f9fdd4d6eb1bc89823ceecc6707b76b5ecf3417a395433242e73c"),
    "drive_code_execution": ("11gvLtX-t3zaLc2HxLS2gDBCm_tOgz7f_", "06_CODE_EXECUTION", "Direct folder listing top_k=100", 1, 0, "dc5aa53213afbf778c279de6b6c779f0844773c0cda7532e400f92325b257d40"),
    "drive_external_validation": ("1x34RiGUka7D4yzqlbSQnXDzt-DTEdg5Q", "03_EXTERNAL_VALIDATION", "Direct folder listing top_k=100", 1, 0, "14b950408b10d7bef498aa0eab544df177bef6f5b839682de8ba1f29980d940e"),
    "drive_search_repro": ("all_accessible_drives", "PFFLS reproducibility", "Drive keyword search topn=100", 13, 0, "b32e82f20086dc13af8f07309a8cc9d4a8e5beb5b255b17ccb9e8f787ace34d7"),
    "drive_search_jrc": ("all_accessible_drives", "JRC Round-2", "Drive keyword search topn=100", 7, 0, "88ce9c39fb5d66f27cbe5212aae469510f3fb0e7bcb070d9e864701ef1ab82e4"),
    "drive_search_sjvf": ("all_accessible_drives", "SJVF", "Drive keyword search topn=100", 8, 0, "4d42cb23eb4c18fc4e7165d9a4fe34bcbc3595e0b42d71306cbcff3de332d7bc"),
    "drive_search_r4_3_30": ("all_accessible_drives", "R4_3_30", "Drive keyword search topn=100", 4, 0, "6d6724f369b5c0cfa1c9afc8bba0b36a80559fd82d79ee178ac6659136cbaa28"),
    "drive_search_cmb82_evls": ("all_accessible_drives", "CMB8.2 EVLS", "Drive keyword search topn=100", 4, 0, "6d6724f369b5c0cfa1c9afc8bba0b36a80559fd82d79ee178ac6659136cbaa28"),
    "repository_artifact_scan": ("86aef2647217ae47defe21110e1bbe4b0833a3a9", "R3nR7-AE binary/source and manuscript extensions", "Tracked-file inventory and ripgrep", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "local_downloads_r3n": ("local_downloads_2026-09-21", "R3n", "Filename inventory", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "authorized_conversation": ("6a8d0a95-f800-83eb-bae6-295e735d63ce", "R3nR7-AE attachment or exact source link", "Read-only conversation inspection", 0, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
}

EXPECTED_BLOCKING_GAPS = {
    "GAP-01",
    "GAP-04",
    "GAP-05",
    "GAP-08",
}
EXPECTED_NONBLOCKING_ARCHIVAL_GAPS = {
    "GAP-02",
    "GAP-03",
    "GAP-06",
}
EXPECTED_BLOCKED_GATES = {
    "MAN-01",
    "MAN-03",
    "MAN-04",
    "SUB-01",
    "SUB-02",
    "SUB-03",
}
EXPECTED_NONBLOCKING_LIMITATION_GATES = {
    "SCI-03",
    "SCI-04",
    "REP-04",
    "REP-05",
}
EXPECTED_CYCLE01_MISMATCHES = {
    "CODEX.md",
    "README.md",
    "PROJECT_STATE.md",
    "outputs/cycle01/admission_summary.json",
    "outputs/cycle01/candidate_campaigns.csv",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(path: Path, required_columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(required_columns).difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name} is empty")
    return rows


def _require_fragments(path: Path, fragments: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    folded = " ".join(text.split()).casefold()
    missing = [
        fragment
        for fragment in fragments
        if " ".join(fragment.split()).casefold() not in folded
    ]
    if missing:
        raise ValueError(f"{path.name} missing required content: {missing}")


def validate_output_files(package_root: Path) -> dict[str, Any]:
    if not package_root.is_dir():
        raise ValueError(f"Cycle 04 output directory does not exist: {package_root}")

    symlinks = [
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_symlink()
    ]
    if symlinks:
        raise ValueError(f"Cycle 04 output contains symbolic links: {symlinks}")

    files = [path for path in package_root.rglob("*") if path.is_file()]
    relative = {path.relative_to(package_root).as_posix() for path in files}
    nested = sorted(name for name in relative if "/" in name)
    if nested:
        raise ValueError(f"Cycle 04 output must remain flat: {nested}")

    restricted = sorted(
        name for name in relative if Path(name).suffix.casefold() in RESTRICTED_SUFFIXES
    )
    if restricted:
        raise ValueError(f"restricted artifact(s) in Cycle 04 output: {restricted}")

    unexpected = sorted(relative.difference(ALLOWED_OUTPUT_FILES))
    if unexpected:
        raise ValueError(f"unexpected Cycle 04 output file(s): {unexpected}")

    missing = sorted(set(CORE_OUTPUT_FILES).difference(relative))
    if missing:
        raise ValueError(f"missing required Cycle 04 output file(s): {missing}")

    empty = sorted(
        name for name in CORE_OUTPUT_FILES if (package_root / name).stat().st_size == 0
    )
    if empty:
        raise ValueError(f"empty required Cycle 04 output file(s): {empty}")

    return {
        "required_core_file_count": len(CORE_OUTPUT_FILES),
        "allowed_output_file_count": len(ALLOWED_OUTPUT_FILES),
        "restricted_artifact_count": 0,
        "unexpected_file_count": 0,
    }


def validate_reviewed_static_content(root: Path) -> dict[str, Any]:
    changed: list[str] = []
    missing: list[str] = []
    for relative, expected_digest in REVIEWED_STATIC_SHA256.items():
        path = root / Path(relative)
        if not path.is_file() or path.is_symlink():
            missing.append(relative)
        elif _sha256(path) != expected_digest:
            changed.append(relative)
    if missing or changed:
        raise ValueError(
            "reviewed static content changed; "
            f"missing={sorted(missing)}, changed={sorted(changed)}"
        )
    return {
        "reviewed_file_count": len(REVIEWED_STATIC_SHA256),
        "identity_match_count": len(REVIEWED_STATIC_SHA256),
    }


def validate_search_manifest(path: Path) -> dict[str, Any]:
    columns = (
        "search_id",
        "scope",
        "scope_id",
        "query_or_location",
        "method",
        "result_count",
        "candidate_artifact_count",
        "result_ids",
        "result_ids_sha256",
        "exact_artifact_found",
        "checked_date",
        "evidence",
        "scope_limit",
    )
    rows = _read_csv(path, columns)
    by_id = {row["search_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("baseline search manifest has duplicate search_id values")
    if set(by_id) != set(EXPECTED_SEARCH_ROWS):
        raise ValueError(
            "baseline search scope changed; "
            f"missing={sorted(set(EXPECTED_SEARCH_ROWS).difference(by_id))}, "
            f"extra={sorted(set(by_id).difference(EXPECTED_SEARCH_ROWS))}"
        )
    for search_id, expected in EXPECTED_SEARCH_ROWS.items():
        row = by_id[search_id]
        actual = (
            row["scope_id"],
            row["query_or_location"],
            row["method"],
            int(row["result_count"]),
            int(row["candidate_artifact_count"]),
            row["result_ids_sha256"],
        )
        if actual != expected:
            raise ValueError(
                f"baseline search record changed for {search_id}: "
                f"expected={expected}, actual={actual}"
            )
        result_ids = row["result_ids"]
        if hashlib.sha256(result_ids.encode("utf-8")).hexdigest() != row["result_ids_sha256"]:
            raise ValueError(f"baseline search result snapshot hash changed for {search_id}")
        listed_ids = [] if not result_ids else result_ids.split(";")
        if listed_ids != sorted(listed_ids, key=str.casefold) or len(listed_ids) != int(row["result_count"]):
            raise ValueError(f"baseline search result IDs are incomplete or unsorted for {search_id}")
        if not row["scope"].strip() or not row["evidence"].strip() or not row["scope_limit"].strip():
            raise ValueError(f"baseline search record is under-specified: {search_id}")
    promoted = [
        row["search_id"]
        for row in rows
        if row["exact_artifact_found"].strip().casefold() != "no"
    ]
    if promoted:
        raise ValueError(f"unverified exact baseline recovery claimed: {promoted}")
    if any(row["checked_date"] != "2026-09-21" for row in rows):
        raise ValueError("baseline search dates drifted")
    return {
        "search_record_count": len(rows),
        "exact_artifact_found": False,
        "candidate_artifact_count": 0,
        "result_snapshot_hashes_verified": len(rows),
        "scope_boundary": "accessible_storage_only",
    }


def validate_historical_inventory(path: Path) -> dict[str, Any]:
    columns = (
        "version",
        "filename",
        "bytes",
        "sha256",
        "storage_scope",
        "drive_file_id",
        "drive_bridge_status",
        "cycle04_role",
        "exact_locked_baseline",
        "repository_action",
        "rights_status",
        "notes",
    )
    rows = _read_csv(path, columns)
    by_version = {row["version"]: row for row in rows}
    if len(by_version) != len(rows):
        raise ValueError("historical inventory has duplicate versions")
    if set(by_version) != set(EXPECTED_HISTORICAL):
        raise ValueError("historical inventory version set changed")

    for version, (filename, size, digest) in EXPECTED_HISTORICAL.items():
        row = by_version[version]
        actual = (row["filename"], int(row["bytes"]), row["sha256"])
        if actual != (filename, size, digest):
            raise ValueError(
                f"historical identity changed for {version}: "
                f"expected={(filename, size, digest)}, actual={actual}"
            )
        if row["exact_locked_baseline"] != "no":
            raise ValueError(f"historical file promoted to baseline: {version}")
        if row["repository_action"] != "metadata_only":
            raise ValueError(f"historical file has unsafe repository action: {version}")

    anchors = [row["version"] for row in rows if row["cycle04_role"] == "historical_anchor"]
    if anchors != ["R3l"]:
        raise ValueError(f"historical anchor must be R3l only, found: {anchors}")
    return {
        "historical_artifact_count": len(rows),
        "historical_anchor": "R3l",
        "historical_anchor_sha256": ANCHOR_SHA256,
        "exact_baseline_artifact_count": 0,
    }


def validate_anchor_extraction(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("anchor_version") != "R3l":
        raise ValueError("anchor extraction version is not R3l")
    if data.get("sha256") != ANCHOR_SHA256 or data.get("bytes") != 795081:
        raise ValueError("anchor extraction identity changed")
    if data.get("exact_locked_baseline") is not False:
        raise ValueError("anchor extraction promotes R3l to the locked baseline")
    pdf = data.get("pdf_metadata", {})
    if pdf.get("pages") != 27 or pdf.get("encrypted") is not False:
        raise ValueError("anchor PDF metadata changed")
    text_audit = data.get("text_audit", {})
    if text_audit.get("normalized_text_sha256") != (
        "78945c92360bf2087311591975c68f62bd84abc4ce39bf3f47c5c51d82e71a01"
    ):
        raise ValueError("anchor normalized-text identity changed")
    visual = data.get("visual_qa", {})
    if visual.get("rendered_pages") != 27 or visual.get("inspected_pages") != 27:
        raise ValueError("anchor visual QA is incomplete")
    if visual.get("result") != "PASS_AS_HISTORICAL_ANCHOR":
        raise ValueError("anchor visual QA status changed")
    return {
        "page_count": 27,
        "normalized_text_sha256": text_audit["normalized_text_sha256"],
        "visual_qa": visual["result"],
    }


def validate_locked_results(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    baseline = data.get("baseline", {})
    if baseline.get("id") != LOCKED_BASELINE or baseline.get("title") != LOCKED_TITLE:
        raise ValueError("locked baseline identity or title changed")
    if baseline.get("binary_status") != "MISSING_FROM_ACCESSIBLE_STORAGE":
        raise ValueError("baseline binary status was promoted without evidence")
    if baseline.get("source_status") != "MISSING_FROM_ACCESSIBLE_STORAGE":
        raise ValueError("baseline source status was promoted without evidence")
    if baseline.get("promoted_by_cycle04") is not False:
        raise ValueError("Cycle 04 cannot promote the baseline")
    anchor = data.get("historical_anchor", {})
    if (
        anchor.get("version") != "R3l"
        or anchor.get("sha256") != ANCHOR_SHA256
        or anchor.get("identity") != "HISTORICAL_ANCHOR_NOT_BASELINE"
    ):
        raise ValueError("historical anchor identity changed")
    if data.get("global_status") != "LOCKED_REPORTED_NOT_RECOMPUTABLE":
        raise ValueError("locked-result status changed")

    claims = data.get("claims", [])
    by_id = {claim.get("id"): claim for claim in claims}
    if len(by_id) != len(claims) or set(by_id) != set(EXPECTED_CLAIMS):
        raise ValueError("locked claim set changed or contains duplicates")
    for claim_id, expected_value in EXPECTED_CLAIMS.items():
        claim = by_id[claim_id]
        if claim.get("value") != expected_value:
            raise ValueError(
                f"locked claim changed for {claim_id}: "
                f"expected={expected_value}, actual={claim.get('value')}"
            )
        expected_layer, expected_metric, expected_denominator, _ = (
            EXPECTED_CLAIM_SCHEMA[claim_id]
        )
        actual_schema = (
            claim.get("layer"),
            claim.get("metric"),
            claim.get("denominator_claim_id"),
        )
        if actual_schema != (
            expected_layer,
            expected_metric,
            expected_denominator,
        ):
            raise ValueError(
                f"locked claim schema changed for {claim_id}: {actual_schema}"
            )
        allowed_fields = {
            "id",
            "layer",
            "metric",
            "value",
            "denominator_claim_id",
            "recomputed_from_raw",
            "reproduction_status",
        }
        unexpected_fields = set(claim).difference(allowed_fields)
        if unexpected_fields:
            raise ValueError(
                f"locked claim has unreviewed fields for {claim_id}: "
                f"{sorted(unexpected_fields)}"
            )
        if claim.get("recomputed_from_raw") is not False:
            raise ValueError(f"unverified recomputation claimed for {claim_id}")
        if claim.get("reproduction_status") != "BLOCKED_MISSING_CORE_ARCHIVE":
            raise ValueError(f"reproduction status changed for {claim_id}")

    boundary = data.get("claim_boundary", {})
    if boundary.get("epa_evidence_type") != "REFERENCE_FREE_FIELD_DATA_SENSITIVITY":
        raise ValueError("EPA evidence type changed")
    for field in (
        "field_experiment",
        "external_accuracy_validation",
        "identifies_environmentally_correct_profile",
        "best_fit_identifies_truth",
    ):
        if boundary.get(field) is not False:
            raise ValueError(f"forbidden EPA claim enabled: {field}")
    return {
        "claim_count": len(claims),
        "jrc_claim_count": sum(claim["layer"] == "JRC" for claim in claims),
        "epa_claim_count": sum(claim["layer"] == "EPA" for claim in claims),
        "recomputed_claim_count": 0,
        "baseline_promoted": False,
    }


def validate_traceability(path: Path) -> dict[str, Any]:
    columns = (
        "claim_id",
        "layer",
        "metric",
        "locked_value",
        "authoritative_lock_source",
        "historical_anchor_locator",
        "lock_disposition",
        "recomputed_from_raw",
        "reproduction_status",
        "input_artifact_status",
        "recomputation_disposition",
        "notes",
    )
    rows = _read_csv(path, columns)
    by_id = {row["claim_id"]: row for row in rows}
    if len(by_id) != len(rows) or set(by_id) != set(EXPECTED_CLAIMS):
        raise ValueError("claim traceability set changed or contains duplicates")
    for claim_id, value in EXPECTED_CLAIMS.items():
        row = by_id[claim_id]
        if row["locked_value"] != str(value):
            raise ValueError(f"traceability value changed for {claim_id}")
        expected_layer, expected_metric, _, expected_input_status = (
            EXPECTED_CLAIM_SCHEMA[claim_id]
        )
        if row["layer"] != expected_layer or row["metric"] != expected_metric:
            raise ValueError(f"traceability schema changed for {claim_id}")
        if row["authoritative_lock_source"] != "PROJECT_STATE.md":
            raise ValueError(f"traceability authority changed for {claim_id}")
        if row["historical_anchor_locator"] != EXPECTED_TRACE_LOCATORS[claim_id]:
            raise ValueError(f"traceability locator changed for {claim_id}")
        if row["lock_disposition"] != "KEEP":
            raise ValueError(f"traceability lock disposition changed for {claim_id}")
        if row["recomputed_from_raw"] != "no":
            raise ValueError(f"traceability overstates recomputation for {claim_id}")
        if row["reproduction_status"] != "BLOCKED_MISSING_CORE_ARCHIVE":
            raise ValueError(f"traceability status changed for {claim_id}")
        if row["input_artifact_status"] != expected_input_status:
            raise ValueError(f"traceability input status changed for {claim_id}")
        if row["recomputation_disposition"] != "HOLD":
            raise ValueError(
                f"traceability recomputation disposition changed for {claim_id}"
            )
    return {
        "claim_count": len(rows),
        "lock_keep_count": len(rows),
        "recomputation_hold_count": len(rows),
    }


def validate_gap_register(path: Path) -> dict[str, Any]:
    columns = (
        "gap_id",
        "domain",
        "severity",
        "status",
        "submission_blocker",
        "required_artifact_or_action",
        "evidence",
        "owner_boundary",
        "disposition",
    )
    rows = _read_csv(path, columns)
    by_id = {row["gap_id"]: row for row in rows}
    if len(by_id) != len(rows) or set(by_id) != {f"GAP-{index:02d}" for index in range(1, 10)}:
        raise ValueError("reproducibility gap set changed or contains duplicates")
    blockers = {
        gap_id
        for gap_id, row in by_id.items()
        if row["submission_blocker"] == "yes"
    }
    if blockers != EXPECTED_BLOCKING_GAPS:
        raise ValueError(f"submission blocker set changed: {sorted(blockers)}")
    if by_id["GAP-09"]["status"] != "LIVE_PENDING":
        raise ValueError("pending external evidence was treated as closed")
    if by_id["GAP-09"]["submission_blocker"] != "no":
        raise ValueError("pending external evidence was made a new submission blocker")
    if "Palmer/Ward" not in by_id["GAP-09"]["evidence"] or "Watson/Chow" not in by_id["GAP-09"]["evidence"]:
        raise ValueError("pending external evidence does not name both live channels")
    if (
        by_id["GAP-07"]["status"] != "DOCUMENTED_NOT_ENFORCED"
        or by_id["GAP-07"]["submission_blocker"] != "no"
        or by_id["GAP-07"]["disposition"] != "HOLD_FUTURE"
    ):
        raise ValueError("Cycle 04 environment documentation overstates runtime enforcement")
    for gap_id in EXPECTED_BLOCKING_GAPS:
        if by_id[gap_id]["disposition"] != "HOLD":
            raise ValueError(f"blocking gap {gap_id} is not HOLD")
    for gap_id in EXPECTED_NONBLOCKING_ARCHIVAL_GAPS:
        row = by_id[gap_id]
        if row["submission_blocker"] != "no":
            raise ValueError(f"archival limitation was promoted to blocker: {gap_id}")
        if row["disposition"] != "HOLD_FUTURE":
            raise ValueError(f"archival limitation disposition changed: {gap_id}")
    if by_id["GAP-02"]["status"] != "ARCHIVAL_LIMITATION":
        raise ValueError("JRC archive gap must remain a non-blocking archival limitation")
    if by_id["GAP-03"]["status"] != "ARCHIVAL_LIMITATION":
        raise ValueError("EPA archive gap must remain a non-blocking archival limitation")
    if by_id["GAP-06"]["status"] != "KNOWN_STALE":
        raise ValueError("Cycle 01 manifest drift must remain archival housekeeping debt")
    return {
        "gap_count": len(rows),
        "submission_blocker_count": len(blockers),
        "nonblocking_archival_gap_count": len(EXPECTED_NONBLOCKING_ARCHIVAL_GAPS),
        "pending_external_register_row_count": 1,
        "pending_external_channel_count": 2,
    }


def validate_candidate_delta(path: Path) -> dict[str, Any]:
    if _sha256(path) != CANDIDATE_DELTA_SHA256:
        raise ValueError(
            "candidate delta differs from the independently reviewed canonical text"
        )
    _require_fragments(
        path,
        (
            "CANDIDATE DELTA FROM R3l — NOT R3nR7-AE — NOT BASELINE",
            "HOLD for independent review",
            ANCHOR_SHA256,
            LOCKED_TITLE,
            "364 daily samples",
            "38 species",
            "12 frozen profile sets",
            "30 prespecified",
            "9/30",
            "345 eligible",
            "323 converged",
            "283 preserving",
            "133/283",
            "62/283",
            "26-case subset",
            "10 ordering changes",
            "2 largest-source changes",
            "not a field experiment",
            "do not constitute external accuracy validation",
            "cannot identify which profile is environmentally correct",
            "not independently recomputed",
            "No other R3nR7-AE wording",
        ),
    )
    text = " ".join(path.read_text(encoding="utf-8").split()).casefold()
    prohibited_patterns = {
        r"r3l\s+(?:is|equals|constitutes|represents)\s+(?:the\s+)?(?:authoritative\s+)?(?:locked\s+)?baseline": "historical anchor promoted to baseline",
        r"epa.{0,100}(?:demonstrate|establish|prove|validate).{0,100}(?:external|predictive|accuracy|accurate|truth|correct)": "EPA sensitivity promoted to accuracy or truth",
        r"best\s+fit.{0,80}(?:identifies|establishes|proves).{0,80}(?:correct|truth|accurate)": "fit promoted to truth",
        r"cycle\s+04.{0,80}independently\s+reproduced.{0,80}(?:jrc|epa)": "central recomputation overstated",
    }
    violations = [
        reason
        for pattern, reason in prohibited_patterns.items()
        if re.search(pattern, text)
    ]
    if violations:
        raise ValueError(f"candidate delta contains forbidden claim(s): {violations}")
    return {
        "document_type": "section_level_delta",
        "anchor": "R3l",
        "baseline_identity_claimed": False,
        "independent_review_required": True,
    }


def validate_readiness(path: Path) -> dict[str, Any]:
    columns = (
        "gate_id",
        "domain",
        "criterion",
        "status",
        "evidence",
        "blocking_action",
        "disposition",
    )
    rows = _read_csv(path, columns)
    by_id = {row["gate_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("readiness matrix has duplicate gate IDs")
    if "OVERALL" not in by_id:
        raise ValueError("readiness matrix has no OVERALL row")
    if by_id["OVERALL"]["status"] != "HOLD_WITH_EXACT_BLOCKERS":
        raise ValueError("readiness matrix improperly promotes the package")
    if by_id["OVERALL"]["disposition"] != "HOLD":
        raise ValueError("overall readiness disposition must be HOLD")
    missing = EXPECTED_BLOCKED_GATES.difference(by_id)
    if missing:
        raise ValueError(f"readiness matrix missing blocking gates: {sorted(missing)}")
    for gate_id in EXPECTED_BLOCKED_GATES:
        if by_id[gate_id]["status"] != "BLOCKED" or by_id[gate_id]["disposition"] != "HOLD":
            raise ValueError(f"blocking readiness gate was promoted: {gate_id}")
    for gate_id in EXPECTED_NONBLOCKING_LIMITATION_GATES:
        if gate_id not in by_id:
            raise ValueError(f"readiness matrix missing limitation gate: {gate_id}")
        if by_id[gate_id]["status"] == "BLOCKED":
            raise ValueError(f"archival limitation was promoted to submission blocker: {gate_id}")
        if by_id[gate_id]["disposition"] != "HOLD_FUTURE":
            raise ValueError(f"limitation gate disposition changed: {gate_id}")
    return {
        "gate_count": len(rows) - 1,
        "blocked_gate_count": len(EXPECTED_BLOCKED_GATES),
        "nonblocking_limitation_gate_count": len(EXPECTED_NONBLOCKING_LIMITATION_GATES),
        "overall_status": "HOLD_WITH_EXACT_BLOCKERS",
    }


def _audit_csv_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    rows = _read_csv(manifest_path, ("relative_path", "bytes", "sha256"))
    missing: list[str] = []
    mismatched: list[str] = []
    for row in rows:
        relative = row["relative_path"]
        target = root / Path(relative)
        if not target.is_file():
            missing.append(relative)
            continue
        if target.stat().st_size != int(row["bytes"]) or _sha256(target) != row["sha256"]:
            mismatched.append(relative)
    return {
        "entry_count": len(rows),
        "missing": sorted(missing),
        "mismatched": sorted(mismatched),
    }


def _audit_sha256s(root: Path, manifest_path: Path) -> dict[str, Any]:
    missing: list[str] = []
    mismatched: list[str] = []
    entries = 0
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(
                f"invalid SHA256SUMS line {line_number}: {line!r}"
            ) from exc
        entries += 1
        target = root / Path(relative)
        if not target.is_file():
            missing.append(relative)
        elif _sha256(target) != expected:
            mismatched.append(relative)
    return {
        "entry_count": entries,
        "missing": sorted(missing),
        "mismatched": sorted(mismatched),
    }


def validate_legacy_manifests(root: Path) -> dict[str, Any]:
    audits = {
        "cycle01": _audit_csv_manifest(
            root, root / "outputs" / "cycle01" / "artifact_manifest_sha256.csv"
        ),
        "cycle02": _audit_csv_manifest(
            root, root / "outputs" / "cycle02" / "artifact_manifest_sha256.csv"
        ),
        "cycle03": _audit_csv_manifest(
            root, root / "outputs" / "cycle03" / "artifact_manifest_sha256.csv"
        ),
        "outreach03": _audit_sha256s(
            root, root / "outputs" / "outreach03" / "SHA256SUMS.txt"
        ),
    }
    cycle01 = audits["cycle01"]
    if set(cycle01["mismatched"]) != EXPECTED_CYCLE01_MISMATCHES:
        raise ValueError(
            "Cycle 01 known-stale set changed: "
            f"expected={sorted(EXPECTED_CYCLE01_MISMATCHES)}, "
            f"actual={cycle01['mismatched']}"
        )
    if cycle01["missing"]:
        raise ValueError(f"Cycle 01 manifest now has missing files: {cycle01['missing']}")
    for name in ("cycle02", "cycle03", "outreach03"):
        if audits[name]["missing"] or audits[name]["mismatched"]:
            raise ValueError(f"{name} manifest no longer verifies: {audits[name]}")
    return audits


def validate_project_state(root: Path) -> dict[str, Any]:
    required = {
        "README.md": (
            LOCKED_BASELINE,
            "Issue #9",
            "PR #10",
            "Issue #8 is closed",
            "ADEC public-records request remains unsent",
            "Cycle 04",
        ),
        "PROJECT_STATE.md": (
            LOCKED_BASELINE,
            "PR #10 has been merged",
            "Issue #8 is closed",
            "Issue #9",
            "DRAFT ONLY / NOT SENT",
            "USER-REPORTED SENT / PENDING — UNVERIFIED",
            "Cycle 04",
        ),
        "CODEX.md": (
            LOCKED_BASELINE,
            "Issue #9",
            "PR #10 is merged",
            "do not send the ADEC public-records request",
            "Cycle 04",
        ),
    }
    for relative, fragments in required.items():
        _require_fragments(root / relative, fragments)
    _require_fragments(
        root / ".gitattributes",
        (
            "/tasks/CODEX_CYCLE_02_FAIRBANKS.md text eol=crlf",
            "/tasks/CODEX_CYCLE_03_REMAINING_EVIDENCE.md text eol=crlf",
            "/outputs/cycle03/admission_audit.json text eol=crlf",
            "/tasks/CODEX_OUTREACH_THREE_EVIDENCE_REQUESTS.md text eol=crlf",
        ),
    )
    return {
        "pr10": "MERGED",
        "issue8": "CLOSED",
        "issue9": "OPEN_CONTINUOUS_MANDATE",
        "adec_request": "DRAFT_ONLY_NOT_SENT",
        "baseline": LOCKED_BASELINE,
    }


def validate_decision_documents(package_root: Path) -> dict[str, Any]:
    _require_fragments(
        package_root / "README.md",
        (
            "HOLD_WITH_EXACT_BLOCKERS",
            "not R3nR7-AE",
            "not the locked baseline",
            "did not independently recompute",
            "ADEC",
        ),
    )
    _require_fragments(
        package_root / "LINEAGE_DECISION.md",
        (
            "R3l",
            ANCHOR_SHA256,
            "must never be labeled as the locked baseline",
            "sole historical reconstruction anchor",
        ),
    )
    _require_fragments(
        package_root / "KEEP_HOLD_REMOVE.md",
        (
            "## KEEP",
            "## HOLD",
            "## REMOVE",
            "HOLD_WITH_EXACT_BLOCKERS",
            "DRAFT ONLY / NOT SENT",
            "not negative evidence",
        ),
    )
    _require_fragments(
        package_root / "SCIENTIFIC_CHANGELOG.md",
        (
            "No scientific result changed",
            "PR #10 is merged",
            "Issue #8 is closed",
            "Issue #9 remains open",
            LOCKED_BASELINE,
        ),
    )
    _require_fragments(
        package_root / "EDITORIAL_RECOMMENDATION.md",
        (
            "Do not submit a journal package",
            "Do not promote R3l",
            "Do not claim that the central JRC/EPA results were independently recomputed",
            "No ADEC request should be sent",
        ),
    )
    _require_fragments(
        package_root / "reproduction.md",
        (
            "CPython 3.12.14",
            "standard library only",
            "their exact computational archives are absent",
            "--refresh-manifest",
            "Any missing file",
        ),
    )
    return {
        "overall_decision": "HOLD_WITH_EXACT_BLOCKERS",
        "manuscript_change_authorized": False,
        "adec_submission_authorized": False,
    }


def validate_test_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("Cycle 04 test_results.txt is missing")
    text = path.read_text(encoding="utf-8")
    required = (
        "status: PASS",
        "interpreter: CPython 3.12.14",
        "python -m unittest discover -s tests -p \"test_*.py\" -v",
    )
    for fragment in required:
        if fragment not in text:
            raise ValueError(f"test_results.txt missing required content: {fragment}")
    match = re.search(r"^tests_run:\s*(\d+)\s*$", text, flags=re.MULTILINE)
    if not match or int(match.group(1)) < 1:
        raise ValueError("test_results.txt has no positive tests_run value")
    return {"status": "PASS", "tests_run": int(match.group(1))}


def validate_cycle04_payload(root: Path) -> dict[str, Any]:
    root = root.resolve()
    package_root = root / "outputs" / "cycle04"
    return {
        "schema_version": "1.1",
        "overall_status": "HOLD_WITH_EXACT_BLOCKERS",
        "baseline": LOCKED_BASELINE,
        "baseline_promoted": False,
        "manuscript_change_authorized": False,
        "central_results_recomputed": False,
        "output_files": validate_output_files(package_root),
        "baseline_search": validate_search_manifest(
            package_root / "baseline_search_manifest.csv"
        ),
        "historical_inventory": validate_historical_inventory(
            package_root / "historical_manuscript_inventory.csv"
        ),
        "anchor_extraction": validate_anchor_extraction(
            package_root / "historical_anchor_extraction.json"
        ),
        "locked_results": validate_locked_results(package_root / "LOCKED_RESULTS.json"),
        "claim_traceability": validate_traceability(
            package_root / "claim_evidence_traceability.csv"
        ),
        "reproducibility_gaps": validate_gap_register(
            package_root / "reproducibility_gap_register.csv"
        ),
        "candidate_delta": validate_candidate_delta(
            package_root / "CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md"
        ),
        "readiness": validate_readiness(
            package_root / "SUBMISSION_READINESS_MATRIX.csv"
        ),
        "decision_documents": validate_decision_documents(package_root),
        "reviewed_static_content": validate_reviewed_static_content(root),
        "tests": validate_test_record(package_root / "test_results.txt"),
        "exact_blockers": [
            "exact_R3nR7_AE_binary_and_source_missing",
            "authoritative_editable_main_and_supplement_missing",
            "repository_identifier_and_licence_unresolved",
            "target_journal_and_author_submission_metadata_missing",
        ],
        "nonblocking_archival_reproducibility_gaps": [
            "JRC_core_computational_archive_missing",
            "EPA_core_computational_archive_missing",
            "cycle01_current_tree_manifest_known_stale",
        ],
    }


def validate_artifact_manifest(root: Path, *, require_exact_tree: bool) -> dict[str, Any]:
    root = root.resolve()
    manifest = root / Path(MANIFEST_RELATIVE_PATH)
    rows = _read_csv(manifest, ("relative_path", "bytes", "sha256"))
    by_path = {row["relative_path"]: row for row in rows}
    expected = set(PACKAGE_PAYLOAD_RELATIVE_PATHS)
    if len(by_path) != len(rows) or set(by_path) != expected:
        raise ValueError(
            "Cycle 04 artifact manifest membership changed; "
            f"missing={sorted(expected.difference(by_path))}, "
            f"extra={sorted(set(by_path).difference(expected))}"
        )
    for relative, row in by_path.items():
        target = root / Path(relative)
        if not target.is_file() or target.is_symlink():
            raise ValueError(f"manifested package file is missing or unsafe: {relative}")
        if target.suffix.casefold() in RESTRICTED_SUFFIXES:
            raise ValueError(f"manifested package file has restricted suffix: {relative}")
        if target.stat().st_size != int(row["bytes"]) or _sha256(target) != row["sha256"]:
            raise ValueError(f"manifested package file identity changed: {relative}")

    if require_exact_tree:
        allowed_runtime_cache_patterns = (
            re.compile(
                r"scripts/__pycache__/validate_cycle04_submission_gate\."
                r"cpython-\d+(?:\.opt-\d+)?\.pyc"
            ),
            re.compile(
                r"tests/__pycache__/test_cycle04_package_local\."
                r"cpython-\d+(?:\.opt-\d+)?\.pyc"
            ),
        )

        def is_allowed_runtime_cache(relative: Path) -> bool:
            name = relative.as_posix()
            return any(pattern.fullmatch(name) for pattern in allowed_runtime_cache_patterns)

        actual = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
            and not is_allowed_runtime_cache(path.relative_to(root))
        }
        expected_tree = expected | {MANIFEST_RELATIVE_PATH}
        if actual != expected_tree:
            raise ValueError(
                "extracted return package tree differs from the allowlist; "
                f"missing={sorted(expected_tree.difference(actual))}, "
                f"extra={sorted(actual.difference(expected_tree))}"
            )
    return {
        "manifest_entry_count": len(rows),
        "identity_match_count": len(rows),
        "exact_tree_verified": require_exact_tree,
    }


def validate_return_package(root: Path) -> dict[str, Any]:
    root = root.resolve()
    payload = validate_cycle04_payload(root)
    manifest = validate_artifact_manifest(root, require_exact_tree=True)
    qa_path = root / "outputs" / "cycle04" / "qa_report.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    mismatched_sections = [
        key for key, value in payload.items() if qa.get(key) != value
    ]
    if mismatched_sections:
        raise ValueError(
            "packaged QA snapshot disagrees with package-local validation: "
            f"{mismatched_sections}"
        )
    return {
        "schema_version": "1.1",
        "overall_status": "HOLD_WITH_EXACT_BLOCKERS",
        "package_local_validation": "PASS",
        "payload": payload,
        "artifact_manifest": manifest,
    }


def validate_repository(root: Path) -> dict[str, Any]:
    root = root.resolve()
    report = validate_cycle04_payload(root)
    report["legacy_manifest_audit"] = validate_legacy_manifests(root)
    report["project_state"] = validate_project_state(root)
    return report


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="Repository root; defaults to the script's parent repository.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        help="Write the canonical QA JSON snapshot to this path.",
    )
    parser.add_argument(
        "--package-local",
        action="store_true",
        help="Validate an extracted Cycle 04 return package without a full repository checkout.",
    )
    args = parser.parse_args()
    if args.package_local and args.write_report:
        parser.error("--package-local cannot be combined with --write-report")
    report = (
        validate_return_package(args.repository_root)
        if args.package_local
        else validate_repository(args.repository_root)
    )
    payload = canonical_report_bytes(report)
    if args.write_report:
        target = args.write_report
        if not target.is_absolute():
            target = args.repository_root / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
