import csv
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_cycle03_evidence import (  # noqa: E402
    EXPECTED_SOURCE_FILES,
    aphh_rows,
    barrow_rows,
    fairbanks_rows,
    validate_candidate_matrix,
    validate_crosswalks,
)


class Cycle03EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.output = ROOT / "outputs" / "cycle03"

    def test_candidate_gate_is_fail_closed(self):
        report = validate_candidate_matrix(
            self.output / "candidate_dataset_matrix.csv"
        )
        self.assertEqual(report["candidate_count"], 4)
        self.assertEqual(
            report["disposition_counts"],
            {"KEEP": 0, "HOLD": 3, "REMOVE": 1},
        )
        self.assertEqual(report["overall_decision"], "HOLD")
        self.assertFalse(report["manuscript_change_authorized"])

    def test_fairbanks_archival_crosswalk_exact_counts(self):
        rows = fairbanks_rows()
        reported = [row for row in rows if row["cmb_status"] == "reported"]
        self.assertEqual(len(rows), 39)
        self.assertEqual(len(reported), 37)
        self.assertEqual(
            {
                relation: sum(
                    row["cmb_relative_to_14c_interval"] == relation
                    for row in reported
                )
                for relation in ("above", "inside", "below")
            },
            {"above": 32, "inside": 4, "below": 1},
        )
        summary = validate_crosswalks()
        self.assertEqual(summary["fairbanks_mean_cmb_minus_14c_midpoint_pp"], "27.86")
        self.assertEqual(summary["fairbanks_mae_to_14c_midpoint_pp"], "28.51")

    def test_barrow_crosswalk_preserves_leakage_boundary(self):
        rows = barrow_rows()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["exact_interval_match"] == "yes" for row in rows))
        self.assertTrue(
            all(row["profile_choice_frozen_before_reference"] == "no" for row in rows)
        )
        self.assertTrue(all(row["disposition"] == "HOLD" for row in rows))

    def test_aphh_subset_identity_does_not_invent_daily_cmb(self):
        rows = aphh_rows()
        self.assertEqual(len(rows), 25)
        self.assertEqual(
            {(row["site"], row["season"], row["cmb_group_n"]) for row in rows},
            {
                ("IAP", "winter", "7"),
                ("IAP", "summer", "6"),
                ("PG", "winter", "7"),
                ("PG", "summer", "5"),
            },
        )
        self.assertTrue(
            all(row["sample_level_cmb_value_public"] == "no" for row in rows)
        )

    def test_committed_crosswalks_match_builder(self):
        with (self.output / "fairbanks_2011_2012_table12_crosswalk.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            fairbanks_committed = list(csv.DictReader(handle))
        with (self.output / "barrow_2012_2013_exact_case_crosswalk.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            barrow_committed = list(csv.DictReader(handle))
        with (self.output / "aphh_beijing_radiocarbon_sample_crosswalk.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            aphh_committed = list(csv.DictReader(handle))
        self.assertEqual(fairbanks_committed, fairbanks_rows())
        self.assertEqual(barrow_committed, barrow_rows())
        self.assertEqual(aphh_committed, aphh_rows())
        self.assertEqual(validate_crosswalks()["barrow_exact_interval_rows"], 4)

    def test_source_hash_registry_has_no_placeholder_hashes(self):
        self.assertEqual(len(EXPECTED_SOURCE_FILES), 9)
        for expected in EXPECTED_SOURCE_FILES.values():
            self.assertEqual(len(expected["sha256"]), 64)
            self.assertEqual(len(expected["md5"]), 32)
            self.assertGreater(expected["bytes"], 0)

    def test_external_requests_are_not_misclassified_as_failed(self):
        with (self.output / "external_request_status.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        pending = [row for row in rows if row["status"] == "SENT / PENDING"]
        self.assertEqual(len(pending), 2)
        self.assertTrue(all(row["negative_evidence"] == "no" for row in pending))
        draft = [row for row in rows if row["status"] == "DRAFT ONLY / NOT SENT"]
        self.assertEqual(len(draft), 1)

    def test_machine_readable_audit_locks_manuscript(self):
        report = json.loads((self.output / "admission_audit.json").read_text())
        self.assertEqual(report["admission"]["overall_decision"], "HOLD")
        self.assertFalse(report["admission"]["manuscript_change_authorized"])


if __name__ == "__main__":
    unittest.main()
