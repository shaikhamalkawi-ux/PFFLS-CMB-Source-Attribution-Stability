"""Post-hoc geometry logic only; no LPs or native data are used."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_interval_geometry as geometry  # noqa: E402


def description(*, status="EXACT_COMPATIBLE", pair_status="EXACT_BOTH_ORDERINGS_WITNESSED", direction=None, leaders=None):
    return {"names": ["a", "b"], "base_model_signature": "same", "zero_lower_columns": [],
            "unbounded_sources": [], "compatibility": status,
            "pairs": {"a|b": {"status": pair_status, "direction": direction}} if status == "EXACT_COMPATIBLE" else {},
            "unique_leaders": leaders or [], "possible_co_leaders": ["a", "b"],
            "impossible_co_leaders": [], "unresolved_co_leaders": []}


class IntervalGeometryTests(unittest.TestCase):
    def test_zero_columns_define_nonnegative_coordinate_recession(self):
        self.assertEqual(geometry.zero_lower_columns([[1, 0, 0], [0, 0, 2]], [[2, 1, 1], [1, 1, 3]], ["a", "b", "c"]), ["b"])

    def test_species_and_source_permutations_preserve_corresponding_result(self):
        self.assertEqual(geometry.zero_lower_columns([[0, 0, 1], [2, 0, 0]], [[3, 1, 2], [3, 1, 1]], ["c", "b", "a"]), ["b"])

    def test_negative_lower_entries_cannot_use_zero_column_lemma(self):
        # With [1,-1], the direction(1,1) is a recession direction despite nozero column.
        with self.assertRaises(ValueError):
            geometry.zero_lower_columns([[1, -1]], [[1, 0]], ["a", "b"])

    def test_reversed_intervals_rejected(self):
        with self.assertRaises(ValueError):
            geometry.zero_lower_columns([[2]], [[1]], ["a"])

    def test_zero_lower_column_cannot_be_inferred_from_small_positive_value(self):
        self.assertEqual(geometry.zero_lower_columns([["1/1000000000000000000000000000000", "0"]], [[1, 1]], ["a", "b"]), ["b"])

    def test_new_mass_order_from_verified_ambiguity_is_separate(self):
        no = description()
        mass = description(pair_status="VERIFIED_A_GREATER_B", direction=("a", "b"), leaders=["a"])
        mass["possible_co_leaders"], mass["impossible_co_leaders"] = ["a"], ["b"]
        result = geometry.compare_mass_pair(no, mass)["counts"]
        self.assertEqual(result["pair_orders_verified_only_after_mass_band"], 1)
        self.assertEqual(result["mass_only_pair_orders_from_exact_no_mass_ambiguity"], 1)
        self.assertEqual(result["unique_leader_verified_only_after_mass_band_samples"], 1)
        self.assertEqual(result["no_mass_possible_co_leaders_proved_impossible_after_mass"], 1)

    def test_no_mass_proof_gap_not_called_witnessed_ambiguity(self):
        no = description(pair_status="NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP")
        no["possible_co_leaders"] = ["a"]
        mass = description(pair_status="VERIFIED_A_GREATER_B", direction=("a", "b"), leaders=["a"])
        result = geometry.compare_mass_pair(no, mass)["counts"]
        self.assertEqual(result["mass_only_pair_orders_from_no_mass_verification_gap_or_near_zero"], 1)
        self.assertNotIn("mass_only_pair_orders_from_exact_no_mass_ambiguity", result)

    def test_unchanged_verified_order_not_counted_new(self):
        no = description(pair_status="VERIFIED_A_GREATER_B", direction=("a", "b"), leaders=["a"])
        result = geometry.compare_mass_pair(no, copy.deepcopy(no))["counts"]
        self.assertEqual(result["pair_orders_verified_in_both"], 1)
        self.assertNotIn("pair_orders_verified_only_after_mass_band", result)

    def test_incompatible_mass_band_does_not_produce_vacuous_winner(self):
        result = geometry.compare_mass_pair(description(), description(status="EXACT_INFEASIBLE"))["counts"]
        self.assertEqual(result, {"compatible_without_mass_but_mass_band_incompatible_samples": 1})

    def test_nested_infeasible_to_feasible_is_rejected(self):
        with self.assertRaises(AssertionError):
            geometry.compare_mass_pair(description(status="EXACT_INFEASIBLE"), description())

    def test_opposite_verified_nested_orders_rejected(self):
        no = description(pair_status="VERIFIED_A_GREATER_B", direction=("a", "b"))
        mass = description(pair_status="VERIFIED_B_GREATER_A", direction=("b", "a"))
        with self.assertRaises(AssertionError):
            geometry.compare_mass_pair(no, mass)

    def test_other_model_changes_not_attributed_to_mass(self):
        mass = description()
        mass["base_model_signature"] = "changed receptor orprofile"
        with self.assertRaises(ValueError):
            geometry.compare_mass_pair(description(), mass)

    def test_mass_witness_with_unresolved_no_mass_run_preserves_status(self):
        result = geometry.compare_mass_pair(description(status="NUMERICALLY_UNRESOLVED"), description())
        self.assertEqual(result["feasibility_pair"], "NUMERICALLY_UNRESOLVED -> EXACT_COMPATIBLE")
        self.assertEqual(result["counts"], {"mass_feasible_but_no_mass_numerically_unresolved_samples": 1})


if __name__ == "__main__":
    unittest.main()
