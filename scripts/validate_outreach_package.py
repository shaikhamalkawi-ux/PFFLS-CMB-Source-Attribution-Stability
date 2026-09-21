#!/usr/bin/env python3
"""Fail-closed validation for the Outreach 03 evidence-request package.

The validator checks only repository artifacts.  It does not send email,
submit a public-records request, or infer that a provider accepted a message.
User reports that the two investigator requests were sent are preserved as
unverified external state.  Under the task's strict status rule, neither row may
be labeled ``SENT`` unless an actual provider confirmation is available.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_ROOT = REPOSITORY_ROOT / "outputs" / "outreach03"
LOCKED_BASELINE = "PFFLS R4.3.30R3nR7-AE"

ALLOWED_STATUSES = {
    "SENT",
    "SUBMITTED",
    "READY_TO_SEND",
    "READY_TO_SUBMIT",
    "BLOCKED_USER_ACTION",
}

# SHA256SUMS.txt is deliberately not included here: the deterministic package
# builder creates it after this source-package validation succeeds.
REQUIRED_FILES = (
    "01_Palmer_Ward_READY_TO_SEND.md",
    "01_Palmer_Ward_FOLLOWUP.md",
    "02_Watson_Chow_READY_TO_SEND.md",
    "02_Watson_Chow_FOLLOWUP.md",
    "03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md",
    "03_ADEC_WEB_FORM_SHORT_VERSION.md",
    "03_ADEC_SUBMISSION_INSTRUCTIONS.md",
    "SUBMIT_THIS_NOW.md",
    "CONTACTS_VERIFIED.csv",
    "OUTREACH_STATUS.csv",
    "OUTREACH_LOG.md",
    "README.md",
    "KEEP_HOLD_REMOVE.md",
    "EDITORIAL_RECOMMENDATION.md",
    "SCIENTIFIC_CHANGELOG.md",
    "reproduction.md",
    "source_inventory.csv",
    "test_results.txt",
)

STATUS_COLUMNS = (
    "request_id",
    "status",
    "external_state",
    "status_authority",
    "provider_confirmation_available",
    "sent_or_submitted_by_codex",
    "negative_evidence",
    "duplication_boundary",
    "next_action",
)

EXPECTED_STATUS_ROWS = {
    "palmer_ward_fairbanks_spreadsheet": {
        "status": "BLOCKED_USER_ACTION",
        "external_state": "USER-REPORTED SENT / PENDING — UNVERIFIED",
        "status_authority": "user_and_project_state",
        "provider_confirmation_available": "no",
        "sent_or_submitted_by_codex": "no",
        "negative_evidence": "no",
    },
    "watson_chow_nfraqs_mapping": {
        "status": "BLOCKED_USER_ACTION",
        "external_state": "USER-REPORTED SENT / PENDING — UNVERIFIED",
        "status_authority": "user_and_project_state",
        "provider_confirmation_available": "no",
        "sent_or_submitted_by_codex": "no",
        "negative_evidence": "no",
    },
    "adec_fairbanks_electronic_package": {
        "status": "BLOCKED_USER_ACTION",
        "external_state": "DRAFT ONLY / NOT SENT",
        "status_authority": "repository_and_drive",
        "provider_confirmation_available": "no",
        "sent_or_submitted_by_codex": "no",
        "negative_evidence": "no",
    },
}

CONTACT_COLUMNS = (
    "request_id",
    "person",
    "role",
    "organization",
    "email",
    "alternate_email",
    "phone",
    "address",
    "primary_source_url",
    "secondary_source_url",
    "retrieved_date",
    "verification_status",
    "notes",
)

EXPECTED_CONTACT_EMAILS = {
    ("palmer_ward_fairbanks_spreadsheet", "Christopher P. Palmer"): (
        "christopher.palmer@umontana.edu",
        "chris.palmer@mso.umt.edu",
    ),
    ("palmer_ward_fairbanks_spreadsheet", "Tony J. Ward"): (
        "tony.ward@umontana.edu",
        "tony.ward@mso.umt.edu",
    ),
    ("watson_chow_nfraqs_mapping", "John G. Watson"): (
        "John.Watson@dri.edu",
        "",
    ),
    ("watson_chow_nfraqs_mapping", "Judith C. Chow"): (
        "Judith.Chow@dri.edu",
        "",
    ),
    ("adec_fairbanks_electronic_package", "Nick Czarnecki"): (
        "nick.czarnecki@alaska.gov",
        "",
    ),
    ("adec_fairbanks_electronic_package", "Cory McDonald"): (
        "cory.mcdonald@alaska.gov",
        "",
    ),
    ("adec_fairbanks_electronic_package", "AMQA Data Requests"): (
        "amqa-data-request@alaska.gov",
        "",
    ),
    ("adec_fairbanks_electronic_package", "Jason Olds"): (
        "jason.olds@alaska.gov",
        "",
    ),
}

EXPECTED_SOURCE_IDS = {
    "um_palmer_directory",
    "um_ward_directory",
    "um_fairbanks_publication",
    "dri_watson_directory",
    "dri_chow_directory",
    "dri_eaf",
    "adec_online_services",
    "adec_records_form",
    "adec_contacts",
    "adec_anpms_contacts",
    "adec_fairbanks_research",
    "adec_amqa_requests",
    "alaska_apra_guidance",
    "alaska_public_records_regulations",
    "cycle03_draft",
}

CONTENT_GUARDS = {
    "01_Palmer_Ward_READY_TO_SEND.md": (
        "SENT / PENDING",
        "did not resend",
        "christopher.palmer@umontana.edu",
        "tony.ward@umontana.edu",
        "PFFLS-CMB reproducibility",
        "XLS/XLSX/CSV",
        "radiocarbon subset",
        "sample IDs",
        "not for unpublished conclusions or a new analysis",
        "last known custodian",
        "[REQUESTER NAME]",
    ),
    "01_Palmer_Ward_FOLLOWUP.md": (
        "5–7 business days",
        "Do not infer the send date",
        "christopher.palmer@umontana.edu",
        "tony.ward@umontana.edu",
        "No new analysis is requested",
        "[REQUESTER NAME]",
    ),
    "02_Watson_Chow_READY_TO_SEND.md": (
        "SENT / PENDING",
        "did not resend",
        "John.Watson@dri.edu",
        "Judith.Chow@dri.edu",
        "PFFLS-CMB reproducibility",
        "contemporary or fossil",
        "carbon contribution",
        "numerator and denominator",
        "source-specific carbon endmembers",
        "negative CMB contributions",
        "including or excluding samples",
        "exact sample IDs",
        "not for a new analysis",
        "last known custodian",
        "[REQUESTER NAME]",
    ),
    "02_Watson_Chow_FOLLOWUP.md": (
        "5–7 business days",
        "Do not infer the send date",
        "John.Watson@dri.edu",
        "Judith.Chow@dri.edu",
        "No new calculation is requested",
        "negative-contribution handling",
        "exact sample IDs",
        "[REQUESTER NAME]",
    ),
    "03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md": (
        "BLOCKED_USER_ACTION",
        "not submitted by Codex",
        "nick.czarnecki@alaska.gov",
        "cory.mcdonald@alaska.gov",
        "amqa-data-request@alaska.gov",
        "AS 40.25.100–40.25.295",
        "EPA-CMB8.2",
        "sample- and species-specific uncertainty",
        "91 EPA/SPECIATE/Missoula profiles",
        "OMNI profiles 100–108",
        "IN*.in8",
        "AD*.sel",
        "SP*.sel",
        "PR*.sel",
        "Native final and preserved trial/sensitivity outputs",
        "crosswalks linking filter/sample identifiers",
        "RTI and DRI analytical-result deliveries",
        "41 emissions trials",
        "yC,biomass = 0.837",
        "not asking DEC to conduct research, perform a new analysis",
        "native electronic form",
        "noncommercial scientific reproducibility",
        "does not duplicate the separately pending Palmer/Ward request",
        "USD 25",
        "[FULL LEGAL NAME]",
        "include only if true",
        "Do not use the bracketed certification",
    ),
    "03_ADEC_WEB_FORM_SHORT_VERSION.md": (
        "not submitted",
        "AS 40.25.100–40.25.295",
        "EPA-CMB8.2",
        "OMNI 100–108",
        "RTI/DRI",
        "no new analysis, query, record, or format conversion",
        "separately pending Palmer/Ward",
        "USD 25",
        "Requester information still required",
    ),
    "03_ADEC_SUBMISSION_INSTRUCTIONS.md": (
        "https://dec.alaska.gov/online-services/",
        "https://dec.alaska.gov/media/x5yl25jk/public-records-request-form.docx",
        "nick.czarnecki@alaska.gov",
        "cory.mcdonald@alaska.gov",
        "amqa-data-request@alaska.gov",
        "Codex must not sign",
        "Certification clause 3",
        "neither a notary nor another oath-administering official is available",
        "Do not sign the optional form unless all three certification clauses are true",
        "Send only after explicit user approval",
        "Codex did not transmit, sign, certify, or submit",
        "BLOCKED_USER_ACTION",
    ),
    "SUBMIT_THIS_NOW.md": (
        "BLOCKED_USER_ACTION",
        "Codex did not transmit this request",
        "signature is required only if the optional",
        "https://dec.alaska.gov/online-services/",
        "nick.czarnecki@alaska.gov",
        "cory.mcdonald@alaska.gov",
        "amqa-data-request@alaska.gov",
        "AS 40.25.100–40.25.295",
        "EPA-CMB8.2",
        "noncommercial scientific reproducibility",
        "not asking ADEC to create a new analysis",
        "inseparable native archive",
        "USD 25",
        "[FULL LEGAL NAME]",
        "[INSERT ONLY IF TRUE",
        "Preserve the sent timestamp",
    ),
    "README.md": (
        "USER-REPORTED SENT / PENDING — UNVERIFIED",
        "BLOCKED_USER_ACTION",
        "Codex did not submit it",
        LOCKED_BASELINE,
        "No manuscript file",
    ),
    "KEEP_HOLD_REMOVE.md": (
        "## KEEP",
        "## HOLD",
        "## REMOVE",
        "non-response is not negative evidence",
        "Any manuscript or baseline change",
    ),
    "OUTREACH_LOG.md": (
        "No email was sent",
        "No browser form, email provider, or government intake was used",
        "No manuscript or locked scientific result was modified",
    ),
    "EDITORIAL_RECOMMENDATION.md": (
        "Do not revise the manuscript or baseline",
        "Do not submit the ADEC request",
        "creates no new admissible scientific evidence",
    ),
    "SCIENTIFIC_CHANGELOG.md": (
        "Added no scientific result",
        "SENT / PENDING",
        LOCKED_BASELINE,
    ),
}

MANUSCRIPT_SUFFIXES = {".doc", ".docx", ".odt", ".pdf", ".rtf", ".tex"}
BASELINE_PATTERN = re.compile(r"\bPFFLS\s+R[0-9A-Za-z.-]+")


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


def validate_required_files(package_root: Path) -> dict[str, object]:
    if not package_root.is_dir():
        raise ValueError(f"package directory does not exist: {package_root}")

    missing = [name for name in REQUIRED_FILES if not (package_root / name).is_file()]
    if missing:
        raise ValueError(f"missing required package files: {missing}")

    empty = [name for name in REQUIRED_FILES if (package_root / name).stat().st_size == 0]
    if empty:
        raise ValueError(f"empty required package files: {empty}")

    manuscript_artifacts = sorted(
        path.name
        for path in package_root.rglob("*")
        if path.is_file()
        and (
            path.suffix.casefold() in MANUSCRIPT_SUFFIXES
            or "manuscript" in path.name.casefold()
        )
    )
    if manuscript_artifacts:
        raise ValueError(
            "outreach package contains manuscript-like artifacts: "
            f"{manuscript_artifacts}"
        )

    return {
        "required_file_count": len(REQUIRED_FILES),
        "manifest_present": (package_root / "SHA256SUMS.txt").is_file(),
        "manuscript_artifact_count": 0,
    }


def validate_status(path: Path) -> dict[str, object]:
    rows = _read_csv(path, STATUS_COLUMNS)
    by_id: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        request_id = row["request_id"].strip()
        if not request_id:
            raise ValueError(f"{path.name} row {row_number} has no request_id")
        if request_id in by_id:
            raise ValueError(f"duplicate request_id in {path.name}: {request_id}")
        by_id[request_id] = row

        if row["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"invalid outreach status for {request_id}: {row['status']}")
        for field in (
            "provider_confirmation_available",
            "sent_or_submitted_by_codex",
            "negative_evidence",
        ):
            if row[field] not in {"yes", "no"}:
                raise ValueError(
                    f"invalid yes/no value for {request_id}.{field}: {row[field]}"
                )
        if not row["duplication_boundary"].strip() or not row["next_action"].strip():
            raise ValueError(f"{request_id} lacks a boundary or next action")

        provider_confirmed = row["provider_confirmation_available"] == "yes"
        codex_sent = row["sent_or_submitted_by_codex"] == "yes"
        if codex_sent and not provider_confirmed:
            raise ValueError(
                f"{request_id} attributes transmission to Codex without provider confirmation"
            )
        if row["status"] in {"SENT", "SUBMITTED"} and not provider_confirmed:
            raise ValueError(
                f"{request_id} is {row['status']} without provider confirmation"
            )
        if row["negative_evidence"] != "no":
            raise ValueError(
                f"{request_id} incorrectly treats an outreach state as negative evidence"
            )

    if set(by_id) != set(EXPECTED_STATUS_ROWS):
        missing = sorted(set(EXPECTED_STATUS_ROWS).difference(by_id))
        extra = sorted(set(by_id).difference(EXPECTED_STATUS_ROWS))
        raise ValueError(f"outreach request IDs differ; missing={missing}, extra={extra}")

    for request_id, expected in EXPECTED_STATUS_ROWS.items():
        row = by_id[request_id]
        mismatches = {
            field: {"expected": expected_value, "actual": row[field]}
            for field, expected_value in expected.items()
            if row[field] != expected_value
        }
        if mismatches:
            raise ValueError(f"status semantics changed for {request_id}: {mismatches}")

    for request_id in (
        "palmer_ward_fairbanks_spreadsheet",
        "watson_chow_nfraqs_mapping",
    ):
        if "do not resend" not in by_id[request_id]["duplication_boundary"].casefold():
            raise ValueError(f"{request_id} lacks the no-resend boundary")

    return {
        "request_count": len(rows),
        "status_counts": {
            status: sum(row["status"] == status for row in rows)
            for status in sorted(ALLOWED_STATUSES)
            if any(row["status"] == status for row in rows)
        },
        "provider_confirmed_count": sum(
            row["provider_confirmation_available"] == "yes" for row in rows
        ),
        "codex_transmission_count": sum(
            row["sent_or_submitted_by_codex"] == "yes" for row in rows
        ),
    }


def validate_contacts(path: Path) -> dict[str, object]:
    rows = _read_csv(path, CONTACT_COLUMNS)
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        key = (row["request_id"].strip(), row["person"].strip())
        if not all(key):
            raise ValueError(f"{path.name} row {row_number} lacks request_id or person")
        if key in by_key:
            raise ValueError(f"duplicate contact in {path.name}: {key}")
        by_key[key] = row

        if not row["role"].strip() or not row["organization"].strip():
            raise ValueError(f"contact {key} lacks role or organization")
        if row["verification_status"] != "VERIFIED_OFFICIAL":
            raise ValueError(f"contact {key} is not VERIFIED_OFFICIAL")
        for url_field in ("primary_source_url", "secondary_source_url"):
            if not row[url_field].startswith("https://"):
                raise ValueError(f"contact {key} has a non-HTTPS {url_field}")
        try:
            date.fromisoformat(row["retrieved_date"])
        except ValueError as exc:
            raise ValueError(f"contact {key} has an invalid retrieval date") from exc

    if set(by_key) != set(EXPECTED_CONTACT_EMAILS):
        missing = sorted(set(EXPECTED_CONTACT_EMAILS).difference(by_key))
        extra = sorted(set(by_key).difference(EXPECTED_CONTACT_EMAILS))
        raise ValueError(f"verified contacts differ; missing={missing}, extra={extra}")

    for key, expected_emails in EXPECTED_CONTACT_EMAILS.items():
        row = by_key[key]
        actual_emails = (row["email"], row["alternate_email"])
        if actual_emails != expected_emails:
            raise ValueError(
                f"contact emails changed for {key}: "
                f"expected={expected_emails}, actual={actual_emails}"
            )

    return {
        "contact_count": len(rows),
        "verified_official_count": sum(
            row["verification_status"] == "VERIFIED_OFFICIAL" for row in rows
        ),
    }


def validate_source_inventory(path: Path) -> dict[str, object]:
    columns = (
        "source_id",
        "title",
        "url",
        "retrieved_date",
        "authority",
        "use",
        "limitations",
    )
    rows = _read_csv(path, columns)
    source_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        source_id = row["source_id"].strip()
        if not source_id or source_id in source_ids:
            raise ValueError(f"invalid or duplicate source_id at row {row_number}")
        source_ids.add(source_id)
        if not row["title"].strip() or not row["authority"].strip():
            raise ValueError(f"source {source_id} lacks title or authority")
        url = row["url"].strip()
        if source_id == "cycle03_draft":
            if not url.startswith("outputs/cycle03/"):
                raise ValueError("cycle03_draft must remain a repository-relative source")
        elif not url.startswith("https://"):
            raise ValueError(f"source {source_id} does not use an HTTPS official URL")
        try:
            date.fromisoformat(row["retrieved_date"])
        except ValueError as exc:
            raise ValueError(f"source {source_id} has an invalid retrieval date") from exc

    if source_ids != EXPECTED_SOURCE_IDS:
        missing = sorted(EXPECTED_SOURCE_IDS.difference(source_ids))
        extra = sorted(source_ids.difference(EXPECTED_SOURCE_IDS))
        raise ValueError(f"source inventory differs; missing={missing}, extra={extra}")

    return {"source_count": len(rows)}


def validate_content(package_root: Path) -> dict[str, object]:
    for filename, fragments in CONTENT_GUARDS.items():
        _require_fragments(package_root / filename, fragments)

    baseline_mentions: set[str] = set()
    for path in package_root.glob("*.md"):
        baseline_mentions.update(BASELINE_PATTERN.findall(path.read_text(encoding="utf-8")))
    if baseline_mentions != {LOCKED_BASELINE}:
        raise ValueError(
            "outreach package changes or omits the locked baseline: "
            f"{sorted(baseline_mentions)}"
        )

    adec_request = (package_root / "03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md").read_text(
        encoding="utf-8"
    )
    adec_short = (package_root / "03_ADEC_WEB_FORM_SHORT_VERSION.md").read_text(
        encoding="utf-8"
    )
    instructions = (package_root / "03_ADEC_SUBMISSION_INSTRUCTIONS.md").read_text(
        encoding="utf-8"
    )
    submit_handoff = (package_root / "SUBMIT_THIS_NOW.md").read_text(encoding="utf-8")

    for path_name, text in (
        ("03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md", adec_request),
        ("03_ADEC_WEB_FORM_SHORT_VERSION.md", adec_short),
        ("SUBMIT_THIS_NOW.md", submit_handoff),
    ):
        if "[FEE CAP]" in text:
            raise ValueError(f"{path_name} retains an unresolved fee-cap placeholder")
        normalized = " ".join(text.split()).casefold()
        exclusion = re.search(
            r"(?:exclude|does not duplicate).{0,220}palmer/ward.{0,260}"
            r"(?:unless|except).{0,100}inseparable.{0,100}(?:native )?archive",
            normalized,
        )
        if exclusion is None:
            raise ValueError(
                f"{path_name} lacks the strict inseparable-native-archive exclusion"
            )

    signature_boundary = " ".join(
        (instructions + "\n" + submit_handoff).split()
    ).casefold()
    email_signature_guard = re.search(
        r"signature is required only if.{0,120}optional.{0,80}(?:docx|hard-copy)",
        signature_boundary,
    )
    if email_signature_guard is None:
        raise ValueError(
            "03_ADEC_SUBMISSION_INSTRUCTIONS.md must state that email submission "
            "does not require a signature"
        )

    return {
        "content_guard_file_count": len(CONTENT_GUARDS),
        "locked_baseline": LOCKED_BASELINE,
        "manuscript_change_authorized": False,
        "direct_transmission_authorized": False,
    }


def validate_package(package_root: Path = DEFAULT_PACKAGE_ROOT) -> dict[str, object]:
    package_root = package_root.resolve()
    files = validate_required_files(package_root)
    status = validate_status(package_root / "OUTREACH_STATUS.csv")
    contacts = validate_contacts(package_root / "CONTACTS_VERIFIED.csv")
    sources = validate_source_inventory(package_root / "source_inventory.csv")
    content = validate_content(package_root)
    return {
        "schema_version": 1,
        "package": str(package_root),
        "files": files,
        "status": status,
        "contacts": contacts,
        "sources": sources,
        "content": content,
        "decision": "ADMINISTRATIVE_PACKAGE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Outreach 03 without sending or submitting anything."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_PACKAGE_ROOT,
        help="Path to outputs/outreach03 (default: repository package)",
    )
    args = parser.parse_args()
    print(json.dumps(validate_package(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
