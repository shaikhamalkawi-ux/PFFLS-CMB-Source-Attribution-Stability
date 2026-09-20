#!/usr/bin/env python3
"""Fail-closed validation for the Cycle 01 evidence registry.

The script deliberately performs no scientific imputation.  It checks the
admission matrix, applies the eight-object gate from tasks/CODEX_CYCLE_01.md,
and writes a machine-readable summary.  A candidate can be KEEP only when all
eight required objects, a profile-choice test, and present reproducibility are
explicitly marked ``yes``.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


GATES = (
    "receptor_vector",
    "receptor_uncertainty",
    "numerical_source_profiles",
    "source_profile_uncertainty",
    "exact_selector",
    "cmb_implementation",
    "external_reference_same_sample",
    "unambiguous_endpoint_mapping",
)
EXTRA_KEEP_GATES = ("source_profile_choice_test", "reproducible_now")
ALLOWED_EVIDENCE = {"yes", "no", "partial"}
ALLOWED_STATUS = {"KEEP", "HOLD", "REMOVE"}


def evaluate_row(row: dict[str, str]) -> dict[str, object]:
    missing_columns = [
        name
        for name in ("candidate_id", "campaign", *GATES, *EXTRA_KEEP_GATES, "status")
        if name not in row
    ]
    if missing_columns:
        raise ValueError(f"missing columns: {', '.join(missing_columns)}")

    invalid = {
        name: row[name]
        for name in (*GATES, *EXTRA_KEEP_GATES)
        if row[name] not in ALLOWED_EVIDENCE
    }
    if invalid:
        raise ValueError(f"invalid evidence values for {row['candidate_id']}: {invalid}")
    if row["status"] not in ALLOWED_STATUS:
        raise ValueError(
            f"invalid status for {row['candidate_id']}: {row['status']}"
        )

    failed = [name for name in (*GATES, *EXTRA_KEEP_GATES) if row[name] != "yes"]
    admissible = not failed

    if row["status"] == "KEEP" and not admissible:
        raise ValueError(
            f"{row['candidate_id']} is KEEP but fails: {', '.join(failed)}"
        )
    if row["status"] != "KEEP" and admissible:
        raise ValueError(
            f"{row['candidate_id']} passes every gate but is labeled {row['status']}"
        )

    return {
        "candidate_id": row["candidate_id"],
        "campaign": row["campaign"],
        "status": row["status"],
        "admissible": admissible,
        "failed_or_partial_gates": failed,
    }


def validate_inventory(path: Path) -> int:
    required = {
        "source_id",
        "title",
        "url",
        "retrieval_date",
        "sha256",
        "rights_status",
        "repository_action",
    }
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"source inventory missing columns: {sorted(missing)}")
        rows = list(reader)

    if not rows:
        raise ValueError("source inventory is empty")
    for index, row in enumerate(rows, start=2):
        if not row["source_id"].strip() or not row["url"].strip():
            raise ValueError(f"source inventory row {index} lacks id or URL")
        digest = row["sha256"].strip()
        if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError(f"source inventory row {index} has invalid SHA-256")
    return len(rows)


def run(candidates: Path, inventory: Path, output: Path | None) -> dict[str, object]:
    with candidates.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("candidate campaign registry is empty")

    results = [evaluate_row(row) for row in rows]
    inventory_count = validate_inventory(inventory)
    summary = {
        "schema_version": 1,
        "stop_rule": "KEEP requires all eight objects plus a profile-choice test and reproducibility",
        "candidate_count": len(results),
        "source_count": inventory_count,
        "keep_count": sum(item["status"] == "KEEP" for item in results),
        "hold_count": sum(item["status"] == "HOLD" for item in results),
        "remove_count": sum(item["status"] == "REMOVE" for item in results),
        "cycle_decision": "KEEP" if any(item["admissible"] for item in results) else "HOLD",
        "candidates": results,
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = run(args.candidates, args.inventory, args.output)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
