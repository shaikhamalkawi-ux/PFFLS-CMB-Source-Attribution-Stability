"""Independent deterministic/publication-scope and adversarial audit tests."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_strengthening_claims as claims  # noqa: E402


class StrengtheningClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = ROOT / claims.ARCHIVE
        cls.data = cls.archive / "derived_data"
        cls.landscape = claims.read_csv(cls.data / "jrc_12set_landscape.csv")
        cls.outcomes = claims.read_csv(cls.data / "epa_primary_outcome_summary.csv")
        cls.attrition = claims.read_csv(cls.data / "epa_profile_alternatives_and_attrition.csv")
        cls.report = claims.audit(cls.archive)

    def test_original_integrity_and_scope_are_explicit(self):
        self.assertEqual(self.report["integrity"]["verified_entries"], 20)
        self.assertEqual(self.report["integrity"]["manifest_sha256"], claims.MANIFEST_SHA256)
        self.assertFalse(self.report["jrc_primary"]["recomputed_from_raw"])
        self.assertFalse(self.report["epa_aggregates"]["recomputed_from_raw"])
        self.assertFalse(self.report["epa_aggregates"]["row_level_event_labels_recomputed"])

    def test_complete_grid_and_expected_discordant_edges(self):
        result = self.report["jrc_primary"]
        self.assertEqual(result["comparisons"], 30)
        self.assertEqual(result["discordances"], 9)
        self.assertEqual(result["discordant_edge_ids"],
                         ["E01", "E04", "E05", "E06", "E07", "E10", "E11", "E12", "E18"])
        self.assertEqual(result["by_family"]["Wood"], {"comparisons": 18, "discordances": 9})
        self.assertEqual(result["by_family"]["Vehicle"], {"comparisons": 12, "discordances": 0})
        self.assertEqual(set(result["node_degrees"].values()), {5})
        pairs = [frozenset((row[1], row[2])) for row in [edge[1:] for edge in claims.graph_edges()]]
        self.assertEqual(len(set(pairs)), 30)

    def test_rounding_proof_has_positive_margins_for_every_edge(self):
        result = self.report["jrc_primary"]
        self.assertEqual(result["rounding_robust_comparisons"], 30)
        self.assertEqual(Decimal(result["minimum_chi_rounding_margin"]), Decimal("0.0003"))
        self.assertEqual(Decimal(result["minimum_error_rounding_margin_pp"]), Decimal("0.23"))
        self.assertEqual(Decimal(result["median_discordant_regret_pp_displayed"]), Decimal("2.18"))
        self.assertEqual(Decimal(result["maximum_discordant_regret_pp_displayed"]), Decimal("4.46"))

    def test_nearest_rounding_intervals_are_exact_and_conservative(self):
        self.assertEqual(claims.rounding_interval("2.27"), (Decimal("2.265"), Decimal("2.275")))
        self.assertEqual(claims.rounding_interval("0.0508"), (Decimal("0.05075"), Decimal("0.05085")))
        self.assertEqual(claims.separated_margin("1.01", "1.00"), Decimal("0"))
        self.assertLess(claims.separated_margin("1.00", "1.00"), 0)

    def test_missing_duplicate_and_unexpected_profiles_fail_closed(self):
        for rows in (self.landscape[:-1], self.landscape + [self.landscape[0]],
                     [{**self.landscape[0], "profile_set": "W99-V2"}] + self.landscape[1:]):
            with self.subTest(rows=len(rows)), self.assertRaisesRegex(ValueError, "complete 4-by-3"):
                claims.reconstruct_jrc(rows)

    def test_nonfinite_and_changed_precision_fail_closed(self):
        for field, value in ((claims.ERROR, "NaN"), (claims.CHI, "0.05"), (claims.R2, "1.5000")):
            rows = copy.deepcopy(self.landscape)
            rows[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                claims.reconstruct_jrc(rows)

    def test_primary_selector_tie_is_not_arbitrarily_resolved(self):
        rows = copy.deepcopy(self.landscape)
        rows[0][claims.CHI] = rows[3][claims.CHI]
        with self.assertRaisesRegex(ValueError, "tied"):
            claims.reconstruct_jrc(rows)

    def test_frozen_ledger_drift_is_detected(self):
        ledger = claims.read_csv(self.data / "jrc_profile_choice_edges_reconstructed.csv")
        claims.compare_frozen_ledger(self.report["jrc_primary"], ledger)
        ledger[0]["fit_favored_endpoint"] = "W4-V2"
        with self.assertRaisesRegex(ValueError, "ledger mismatch"):
            claims.compare_frozen_ledger(self.report["jrc_primary"], ledger)

    def test_frozen_ledger_count_and_duplicate_ids_are_rejected(self):
        ledger = claims.read_csv(self.data / "jrc_profile_choice_edges_reconstructed.csv")
        ledger[1]["edge_id"] = ledger[0]["edge_id"]
        with self.assertRaisesRegex(ValueError, "30 unique"):
            claims.compare_frozen_ledger(self.report["jrc_primary"], ledger)

    def test_rank_helpers_include_residual_ties(self):
        self.assertEqual(claims.ranks([7, 2, 2, 8]), [3.0, 1.5, 1.5, 4.0])
        for n, count in ((1, 1), (2, 3), (3, 13)):
            partitions = claims.ordered_partitions(tuple(range(n)))
            self.assertEqual(len(partitions), count)
            self.assertEqual(len(set(partitions)), count)
        with self.assertRaisesRegex(ValueError, "undefined"):
            claims.correlation([1, 1], [1, 2])

    def test_r2_exhaustive_rank_enumeration_is_compatible_not_verification(self):
        result = self.report["jrc_R2_precision"]
        self.assertEqual(result["all_weak_refinements"], 39)
        self.assertEqual(result["strict_refinements"], 12)
        self.assertEqual(result["refinements_rounding_to_reported"], 3)
        self.assertEqual(result["strict_refinements_rounding_to_reported"], 3)
        self.assertAlmostEqual(result["displayed_midrank_rho"], 0.927725666496, places=11)
        self.assertEqual(result["possible_rho_range"], [0.902097902098, 0.937062937063])
        self.assertTrue(result["reported_value_compatible_with_rounding"])
        self.assertFalse(result["reported_value_independently_verified"])

    def test_strict_spearman_values_match_independent_squared_rank_formula(self):
        error_order = sorted(self.landscape, key=lambda row: Decimal(row[claims.ERROR]))
        error_ranks = {row["profile_set"]: index + 1 for index, row in enumerate(error_order)}
        for candidate in self.report["jrc_R2_precision"]["refinements"]:
            if not candidate["strict_order"]:
                continue
            ordered = [block[0] for block in candidate["ascending_one_minus_R2_rank_blocks"]]
            squared_distance = sum((error_ranks[name] - (i + 1)) ** 2 for i, name in enumerate(ordered))
            independent = 1 - 6 * squared_distance / (12 * (12 ** 2 - 1))
            self.assertAlmostEqual(candidate["rho"], independent, places=11)

    def test_epa_nested_aggregate_arithmetic_is_not_row_recovery(self):
        result = self.report["epa_aggregates"]
        self.assertEqual((result["eligible"], result["converged"], result["nonconverged"]), (345, 323, 22))
        self.assertEqual(result["two_diagnostic_ordering_percent"], 47.0)
        self.assertEqual(result["two_diagnostic_largest_percent"], 21.9)
        complement = result["conditional_complement_arithmetic"]
        self.assertEqual([(r["n"], r["ordering_changes"], r["largest_source_changes"])
                          for r in complement], [(40, 34, 19), (257, 123, 60)])
        self.assertFalse(result["row_level_event_labels_recomputed"])

    def test_epa_attrition_mutation_is_detected(self):
        rows = copy.deepcopy(self.attrition)
        rows[0]["converged"] = "34"
        with self.assertRaisesRegex(ValueError, "per-alternative attrition"):
            claims.epa_audit(self.outcomes, rows)

    def test_epa_impossible_nested_event_counts_are_detected(self):
        outcomes = copy.deepcopy(self.outcomes)
        outcomes[2]["any_ordering_change"] = "120"
        with self.assertRaisesRegex(ValueError, "nested-complement"):
            claims.epa_audit(outcomes, self.attrition)

    def test_epa_fractional_count_is_not_silently_truncated(self):
        outcomes = copy.deepcopy(self.outcomes)
        outcomes[2]["any_ordering_change"] = "133.5"
        with self.assertRaisesRegex(ValueError, "nonnegative integer"):
            claims.epa_audit(outcomes, self.attrition)

    def test_missing_or_modified_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "archive"
            shutil.copytree(self.archive, archive)
            target = archive / "derived_data" / "jrc_12set_landscape.csv"
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "manifest mismatch"):
                claims.audit(archive)
            target.unlink()
            with self.assertRaises(FileNotFoundError):
                claims.audit(archive)

    def test_changed_manifest_cannot_bless_new_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "archive"
            shutil.copytree(self.archive, archive)
            manifest = archive / "SHA256SUMS.txt"
            manifest.write_bytes(manifest.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "manifest identity"):
                claims.audit(archive)

    def test_output_cannot_modify_frozen_archive(self):
        with self.assertRaisesRegex(ValueError, "within the frozen archive"):
            claims.write_outputs(self.report, self.archive / "new-output", self.archive)

    def test_outputs_deterministic_and_source_archive_unchanged(self):
        before = {path.relative_to(self.archive): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in self.archive.rglob("*") if path.is_file()}
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "one", Path(directory) / "two"
            claims.write_outputs(claims.audit(self.archive), first, self.archive)
            claims.write_outputs(claims.audit(self.archive), second, self.archive)
            for name in ("claims_audit.json", "CLAIM_AUDIT.md"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            loaded = json.loads((first / "claims_audit.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded, self.report)
        after = {path.relative_to(self.archive): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in self.archive.rglob("*") if path.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
