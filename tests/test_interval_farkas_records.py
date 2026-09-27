"""Independent exact Farkas-margin replay tests; no field data or LP."""
import ast
import copy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_interval_farkas_records as f


def fixture():
    model = {"n": 3, "names": ["a", "b", "c"],
             "G": [[Q(-1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]],
             "h": [Q(-3), Q(1), Q(2)]}
    point = {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": ["3", "1", "2"]}}
    # b certificate includes both a-b and c-b, and a strictly positive residual.
    result = {"overall_status": "EXACT_COMPATIBLE", "feasibility": copy.deepcopy(point),
              "co_leaders": {"a": copy.deepcopy(point),
                            "b": {"status": "EXACT_INFEASIBLE",
                                  "farkas": {"verified": True, "y": ["1", "2", "0", "1", "1"], "h_dot_y": "-1"}},
                            "c": {"status": "EXACT_INFEASIBLE",
                                  "farkas": {"verified": True, "y": ["1", "0", "1", "1", "0"], "h_dot_y": "-1"}}}}
    return model, result


class ExactReplayTests(unittest.TestCase):
    def test_positive_residual_and_non_W_row_weight_are_sound(self):
        m, r = fixture()
        result = f.derive_component(m, r, Q(1, 10))
        b = result["bounds"][0]
        self.assertEqual(b["augmented_residual"], [0, 0, 1])
        self.assertEqual(b["b"], [1, 1])
        self.assertEqual(b["lower_margin"], Q(1, 2))
        self.assertEqual(result["leader"], "a")
        self.assertTrue(result["all_margins_above_delta"])

    def test_every_premise_before_ratio(self):
        m, r = fixture()
        r["co_leaders"]["c"]["status"] = "NUMERICALLY_UNRESOLVED"
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_all_competitors_required(self):
        m, r = fixture()
        r["co_leaders"].pop("c")
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_negative_multiplier_rejected(self):
        m, r = fixture()
        r["co_leaders"]["b"]["farkas"]["y"][0] = "-1"
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_wrong_augmentation_order_rejected(self):
        m, r = fixture()
        r["co_leaders"]["c"]["farkas"]["y"][-2:] = ["0", "1"]
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_wrong_stored_contradiction_rejected(self):
        m, r = fixture()
        r["co_leaders"]["b"]["farkas"]["h_dot_y"] = "-2"
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_missing_multiplier_rejected(self):
        m, r = fixture()
        r["co_leaders"]["b"]["farkas"]["y"].pop()
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_universal_leader_cannot_be_chosen_arbitrarily(self):
        m, r = fixture()
        r["co_leaders"]["a"], r["co_leaders"]["b"] = r["co_leaders"]["b"], r["co_leaders"]["a"]
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_nonfeasible_base_cannot_be_used(self):
        m, r = fixture()
        r["feasibility"]["primal"]["point"][0] = "299999999999/100000000000"
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_positive_scaling_invariance(self):
        m, r = fixture()
        baseline = f.derive_component(m, r, Q(1, 10))
        for name in ("b", "c"):
            cert = r["co_leaders"][name]["farkas"]
            cert["y"] = [str(Q(value)*Q(7, 3)) for value in cert["y"]]
            cert["h_dot_y"] = str(Q(cert["h_dot_y"])*Q(7, 3))
        other = f.derive_component(m, r, Q(1, 10))
        self.assertEqual([b["lower_margin"] for b in baseline["bounds"]],
                         [b["lower_margin"] for b in other["bounds"]])

    def test_zero_augmentation_weight_never_accepted(self):
        m, r = fixture()
        r["co_leaders"]["b"]["farkas"]["y"][-2:] = ["0", "0"]
        with self.assertRaises(f.v.VerificationError):
            f.derive_component(m, r, Q(1, 10))

    def test_equal_delta_is_not_positive_certificate(self):
        component = f.derive_component(*fixture(), Q(1, 2))
        self.assertEqual(component["bounds"][0]["threshold_relation"], "EQUAL")
        self.assertTrue(f.summarize([component], 1)["status"].startswith("HOLD"))

    def test_below_delta_is_not_positive_certificate(self):
        component = f.derive_component(*fixture(), Q(3, 4))
        self.assertEqual(component["bounds"][0]["threshold_relation"], "BELOW")
        self.assertTrue(f.summarize([component], 1)["status"].startswith("HOLD"))

    def test_incomplete_union_not_certified(self):
        component = f.derive_component(*fixture(), Q(1, 10))
        self.assertTrue(f.summarize([component], 2)["status"].startswith("HOLD"))

    def test_same_W_required_across_components(self):
        a = f.derive_component(*fixture(), Q(1, 10))
        b = copy.deepcopy(a); b["leader"] = "b"
        self.assertTrue(f.summarize([a, b], 2)["status"].startswith("HOLD"))

    def test_empty_union_not_stable(self):
        out = f.summarize([{"status": "EXACT_INFEASIBLE", "bounds": []}], 1)
        self.assertEqual(out["status"], "EXACT_EMPTY_UNION_NOT_A_LEADER_CERTIFICATE")

    def test_valid_complete_nonempty_union(self):
        a = f.derive_component(*fixture(), Q(1, 10))
        out = f.summarize([a, {"status": "EXACT_INFEASIBLE", "bounds": []}], 2)
        self.assertEqual(out["status"], "POSTHOC_CERTIFIED_UNIQUE_UNION_LEADER_ABOVE_ORIGINAL_MARGIN")

    def test_input_not_mutated(self):
        m, r = fixture(); before = copy.deepcopy((m, r))
        f.derive_component(m, r, Q(1, 10))
        self.assertEqual((m, r), before)

    def test_no_numerical_solver_or_assert_guards(self):
        tree = ast.parse(Path(f.__file__).read_text())
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(tree)))
        forbidden = ("scipy", "numpy", "audit_interval")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any(a.name.startswith(forbidden) for a in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertFalse(node.module.startswith(forbidden))


if __name__ == "__main__":
    unittest.main()

