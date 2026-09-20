import csv
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
from validate_cycle01_evidence import GATES, evaluate_row, run  # noqa: E402


class EvidenceGateTests(unittest.TestCase):
    def complete_row(self, status="KEEP"):
        row = {
            "candidate_id": "test",
            "campaign": "test campaign",
            "source_profile_choice_test": "yes",
            "reproducible_now": "yes",
            "status": status,
        }
        row.update({gate: "yes" for gate in GATES})
        return row

    def test_complete_keep_is_admissible(self):
        self.assertTrue(evaluate_row(self.complete_row())["admissible"])

    def test_keep_fails_closed_when_one_object_is_missing(self):
        row = self.complete_row()
        row["unambiguous_endpoint_mapping"] = "no"
        with self.assertRaisesRegex(ValueError, "KEEP but fails"):
            evaluate_row(row)

    def test_complete_non_keep_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "passes every gate"):
            evaluate_row(self.complete_row(status="HOLD"))

    def test_repository_registries_validate_and_cycle_is_hold(self):
        summary = run(
            ROOT / "outputs" / "cycle01" / "candidate_campaigns.csv",
            ROOT / "outputs" / "cycle01" / "source_inventory.csv",
            None,
        )
        self.assertEqual(summary["cycle_decision"], "HOLD")
        self.assertEqual(summary["keep_count"], 0)
        self.assertGreaterEqual(summary["candidate_count"], 5)

    def test_bad_inventory_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = root / "candidates.csv"
            inventory = root / "inventory.csv"
            with candidates.open("w", newline="", encoding="utf-8") as handle:
                fieldnames = [
                    "candidate_id",
                    "campaign",
                    *GATES,
                    "source_profile_choice_test",
                    "reproducible_now",
                    "status",
                ]
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(self.complete_row(status="KEEP"))
            with inventory.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "source_id",
                        "title",
                        "url",
                        "retrieval_date",
                        "sha256",
                        "rights_status",
                        "repository_action",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "source_id": "s",
                        "title": "t",
                        "url": "https://example.invalid",
                        "retrieval_date": "2026-09-20",
                        "sha256": "not-a-digest",
                        "rights_status": "unknown",
                        "repository_action": "metadata only",
                    }
                )
            with self.assertRaisesRegex(ValueError, "invalid SHA-256"):
                run(candidates, inventory, None)


if __name__ == "__main__":
    unittest.main()
