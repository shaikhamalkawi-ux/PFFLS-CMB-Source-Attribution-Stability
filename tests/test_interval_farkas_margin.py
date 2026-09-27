"""Synthetic exact proof tests only; no field inputs or numerical LP dependency."""
import ast
import copy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_interval_farkas_margin as f


def two_source():
    model = {"n": 2, "names": ["a", "b"], "G": [[-1, 0], [0, 1]], "h": [-2, 1]}
    result = {"overall_status": "EXACT_COMPATIBLE", "feasibility": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [2, 1]}},
              "co_leaders": {"a": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [2, 1]}},
                             "b": {"status": "EXACT_INFEASIBLE", "farkas": {"verified": True, "y": [1, 1, 1]}}}}
    return model, result


def three_source():
    model = {"n": 3, "names": ["a", "b", "c"], "G": [[-1, 0, 0], [0, 1, 0], [0, 0, 1]], "h": [-3, 1, 2]}
    result = {"overall_status": "EXACT_COMPATIBLE", "feasibility": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [3, 1, 2]}},
              "co_leaders": {"a": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [3, 1, 2]}},
                             "b": {"status": "EXACT_INFEASIBLE", "farkas": {"verified": True, "y": [1, 1, 0, 1, 0]}},
                             "c": {"status": "EXACT_INFEASIBLE", "farkas": {"verified": True, "y": [1, 0, 1, 1, 0]}}}}
    return model, result


class ExactMarginTests(unittest.TestCase):
    def test_exact_margin_from_two_source_certificate(self):
        m, r = two_source()
        result = f.component_margins(m, r, Q(1, 10))
        self.assertEqual(result["bounds"][0]["lower_margin"], 1)
        self.assertEqual(result["bounds"][0]["gamma"], 1)
        self.assertEqual(result["bounds"][0]["B"], 1)
        self.assertTrue(result["all_margins_above_delta"])

    def test_three_source_all_competitors_checked(self):
        m, r = three_source()
        result = f.component_margins(m, r, Q(1, 10))
        self.assertEqual([b["lower_margin"] for b in result["bounds"]], [2, 1])

    def test_zero_B_rejected_even_when_infeasible_base_has_farkas(self):
        m = f.exact_model({"n": 2, "names": ["a", "b"], "G": [[0, 0]], "h": [-1]})
        with self.assertRaisesRegex(ValueError, "B must"):
            f.farkas_margin(m, "b", [1, 0])

    def test_negative_multiplier_rejected(self):
        m, r = two_source()
        r["co_leaders"]["b"]["farkas"]["y"] = [-1, 1, 1]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_wrong_multiplier_length_rejected(self):
        m, r = two_source()
        r["co_leaders"]["b"]["farkas"]["y"] = [1, 1]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_negative_column_residual_rejected(self):
        m, r = two_source()
        r["co_leaders"]["b"]["farkas"]["y"] = [2, 1, 1]
        with self.assertRaisesRegex(ValueError, "residual"):
            f.component_margins(m, r, Q(1, 10))

    def test_nonnegative_contradiction_rejected(self):
        m, r = two_source()
        r["co_leaders"]["b"]["farkas"]["y"] = [0, 1, 0]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_missing_competitor_blocks_every_margin_before_arithmetic(self):
        m, r = three_source()
        del r["co_leaders"]["c"]
        with patch.object(f, "farkas_margin", side_effect=AssertionError("no margin should be attempted")):
            with self.assertRaises(ValueError):
                f.component_margins(m, r, Q(1, 10))

    def test_second_invalid_competitor_blocks_first_margin(self):
        m, r = three_source()
        r["co_leaders"]["c"]["farkas"]["verified"] = False
        with patch.object(f, "farkas_margin", side_effect=AssertionError("premise not established")):
            with self.assertRaises(ValueError):
                f.component_margins(m, r, Q(1, 10))

    def test_wrong_expected_W_rejected(self):
        m, r = two_source()
        with self.assertRaisesRegex(ValueError, "wrong W"):
            f.component_margins(m, r, Q(1, 10), expected_leader="b")

    def test_wrong_source_mapping_rejected(self):
        m, r = two_source()
        m["names"] = ["b", "a"]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_wrong_augmented_row_order_rejected(self):
        m, r = three_source()
        r["co_leaders"]["b"]["farkas"]["y"] = [1, 1, 0, 0, 1]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_stored_multiplier_scaling_invariance(self):
        m, r = three_source()
        baseline = f.component_margins(m, r, Q(1, 10))
        for name in ("b", "c"):
            r["co_leaders"][name]["farkas"]["y"] = [Q(3, 7) * x for x in r["co_leaders"][name]["farkas"]["y"]]
        scaled = f.component_margins(m, r, Q(1, 10))
        self.assertEqual([b["lower_margin"] for b in baseline["bounds"]], [b["lower_margin"] for b in scaled["bounds"]])

    def test_threshold_equality_not_pass(self):
        m, r = two_source()
        c = f.component_margins(m, r, 1)
        self.assertEqual(c["bounds"][0]["threshold_relation"], "EQUAL")
        self.assertFalse(c["all_margins_above_delta"])

    def test_threshold_below_bound_passes(self):
        m, r = two_source()
        self.assertEqual(f.component_margins(m, r, Q(1, 2))["bounds"][0]["threshold_relation"], "ABOVE")

    def test_threshold_above_bound_is_hold(self):
        m, r = two_source()
        self.assertEqual(f.component_margins(m, r, 2)["bounds"][0]["threshold_relation"], "BELOW")

    def test_inexact_base_witness_rejected(self):
        m, r = two_source()
        r["feasibility"]["primal"]["point"] = [Q(2) - Q(1, 10**50), 1]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_unverified_base_witness_rejected(self):
        m, r = two_source()
        r["feasibility"]["primal"]["verified"] = False
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_missing_W_witness_rejected(self):
        m, r = two_source()
        r["co_leaders"]["a"].pop("primal")
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_two_possible_coleaders_fail_universal_max_premise(self):
        m, r = two_source()
        r["co_leaders"]["b"] = copy.deepcopy(r["co_leaders"]["a"])
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_duplicate_family_names_rejected(self):
        m, r = two_source()
        m["names"] = ["a", "a"]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_dimension_mismatch_rejected(self):
        m, r = two_source()
        m["G"][0] = [-1]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_inputs_not_mutated(self):
        m, r = three_source()
        prior = copy.deepcopy((m, r))
        f.component_margins(m, r, Q(1, 10))
        self.assertEqual((m, r), prior)

    def test_unknown_competitor_mapping_rejected(self):
        m, _ = two_source()
        with self.assertRaises(ValueError):
            f.leader_rows(f.exact_model(m), "missing")


class UnionCompletionTests(unittest.TestCase):
    def feasible(self, delta=Q(1, 10)):
        return f.component_margins(*two_source(), delta)

    def test_empty_union_does_not_certify_leader(self):
        r = f.union_summary([{"status": "EXACT_INFEASIBLE", "bounds": []}] * 2, 2)
        self.assertEqual(r["status"], "EXACT_EMPTY_UNION_NOT_A_LEADER_CERTIFICATE")

    def test_infeasible_components_and_nonempty_valid_component_can_certify(self):
        r = f.union_summary([self.feasible(), {"status": "EXACT_INFEASIBLE", "bounds": []}], 2)
        self.assertEqual(r["status"], "POSTHOC_CERTIFIED_UNIQUE_UNION_LEADER_ABOVE_ORIGINAL_MARGIN")

    def test_unresolved_component_blocks_positive(self):
        r = f.union_summary([self.feasible(), {"status": "HOLD_UNRESOLVED_COMPONENT", "bounds": []}], 2)
        self.assertTrue(r["status"].startswith("HOLD"))

    def test_missing_component_blocks_positive(self):
        self.assertTrue(f.union_summary([self.feasible()], 2)["status"].startswith("HOLD"))

    def test_any_bound_at_threshold_blocks_positive(self):
        self.assertTrue(f.union_summary([self.feasible(1)], 1)["status"].startswith("HOLD"))

    def test_different_W_across_components_blocks_positive(self):
        a, b = self.feasible(), self.feasible()
        b["leader"] = "b"
        self.assertTrue(f.union_summary([a, b], 2)["status"].startswith("HOLD"))

    def test_base_infeasibility_rechecked(self):
        m = {"n": 2, "names": ["a", "b"], "G": [[1, 0], [-1, 0]], "h": [0, -1]}
        r = {"overall_status": "EXACT_INFEASIBLE", "feasibility": {"status": "EXACT_INFEASIBLE", "farkas": {"verified": True, "y": [1, 1]}}}
        self.assertEqual(f.component_margins(m, r, Q(1, 10))["status"], "EXACT_INFEASIBLE")
        r["feasibility"]["farkas"]["y"] = [1, 0]
        with self.assertRaises(ValueError):
            f.component_margins(m, r, Q(1, 10))

    def test_unresolved_status_not_treated_as_infeasible(self):
        m, r = two_source()
        r["overall_status"] = "NUMERICALLY_UNRESOLVED"
        self.assertEqual(f.component_margins(m, r, Q(1, 10))["status"], "HOLD_UNRESOLVED_COMPONENT")

    def test_standard_library_only_no_numerical_solver_import(self):
        tree = ast.parse(Path(f.__file__).read_text(encoding="utf-8"))
        imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imports |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertTrue(imports <= {"__future__", "argparse", "collections", "datetime", "fractions", "hashlib", "json", "pathlib", "subprocess", "sys"})


if __name__ == "__main__":
    unittest.main()
