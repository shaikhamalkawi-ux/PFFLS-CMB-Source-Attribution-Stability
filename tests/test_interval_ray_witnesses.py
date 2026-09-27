"""Exact post-hoc constructions; no field data and no numerical solver."""
import copy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_interval_ray_witnesses as ray


def model():
    return {"n": 2, "names": ["a", "b"], "G": [[0, 1], [0, -1]], "h": [1, -1]}


def pair():
    return {"a": "a", "b": "b", "classification": {"status": "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP"},
            "minimize": {"objective": [1, -1], "status": "VERIFIED_BOUND_AND_WITNESS",
                         "primal": {"verified": True, "point": [0, 1]}},
            "maximize_negative": {"objective": [-1, 1], "status": "EXACT_UNBOUNDED",
                                  "recession": {"verified": True, "point": [0, 1], "ray": [1, 0]}}}


class RayWitnessTests(unittest.TestCase):
    def test_finite_exact_improving_point(self):
        result = ray.finite_ray_witness(model(), [-1, 1], [0, 1], [1, 0])
        self.assertEqual(result["constructed_point"], [2, 1])
        self.assertEqual(result["objective_value"], -1)

    def test_positive_ray_scaling_preserves_constructed_point(self):
        a = ray.finite_ray_witness(model(), [-1, 1], [0, 1], [1, 0])
        b = ray.finite_ray_witness(model(), [-1, 1], [0, 1], [Q(3, 7), 0])
        self.assertEqual(a["constructed_point"], b["constructed_point"])

    def test_already_negative_point_needs_zero_step(self):
        result = ray.finite_ray_witness(model(), [-1, 1], [5, 1], [1, 0])
        self.assertEqual(result["step"], 0)
        self.assertEqual(result["objective_value"], -4)

    def test_infeasible_base_rejected(self):
        with self.assertRaises(ValueError):
            ray.finite_ray_witness(model(), [-1, 1], [0, 2], [1, 0])

    def test_negative_ray_rejected(self):
        with self.assertRaises(ValueError):
            ray.finite_ray_witness(model(), [1, -1], [0, 1], [-1, 0])

    def test_nonrecession_direction_rejected(self):
        with self.assertRaises(ValueError):
            ray.finite_ray_witness(model(), [-1, -1], [0, 1], [0, 1])

    def test_nonimproving_ray_rejected(self):
        for q in ([0, 1], [1, 0]):
            with self.assertRaises(ValueError):
                ray.finite_ray_witness(model(), q, [0, 1], [1, 0])

    def test_dimensions_rejected(self):
        for q, x, d in (([-1], [0, 1], [1, 0]), ([-1, 1], [0], [1, 0]), ([-1, 1], [0, 1], [1])):
            with self.assertRaises(ValueError):
                ray.finite_ray_witness(model(), q, x, d)

    def test_extreme_rationals_do_not_round(self):
        tiny = Q(1, 10**100)
        result = ray.finite_ray_witness(model(), [-tiny, 1], [0, 1], [tiny, 0])
        self.assertEqual(result["objective_value"], -1)
        self.assertEqual(result["step"], Q(2) / tiny**2)

    def test_pair_both_signs_are_exactly_witnessed(self):
        result = ray.complete_pair(model(), pair())
        self.assertEqual(result["derived_status"], "EXACT_BOTH_ORDERINGS_COMPLETED")
        self.assertEqual(result["negative_witness"]["contrast"], -1)
        self.assertEqual(result["positive_witness"]["contrast"], 1)

    def test_one_sided_order_is_not_fabricated_ambiguity(self):
        m, p = model(), pair()
        m["G"] += [[-1, 0]]
        m["h"] += [-2]
        p["minimize"]["primal"]["point"] = [2, 1]
        p["maximize_negative"]["recession"]["point"] = [2, 1]
        result = ray.complete_pair(m, p)
        self.assertEqual(result["derived_status"], "NO_OPPOSITE_SIGN_IN_STORED_PROOFS")
        self.assertIsNone(result["negative_witness"])

    def test_exact_tie_is_preserved(self):
        m, p = model(), pair()
        p["minimize"]["primal"]["point"] = [1, 1]
        result = ray.complete_pair(m, p)
        self.assertEqual(result["derived_status"], "EXACT_TIE_COMPLETED")

    def test_wrong_objective_rejected(self):
        p = pair()
        p["minimize"]["objective"] = [-1, 1]
        with self.assertRaises(ValueError):
            ray.complete_pair(model(), p)

    def test_unverified_ray_label_rejected(self):
        p = pair()
        p["maximize_negative"]["recession"]["verified"] = False
        with self.assertRaises(ValueError):
            ray.complete_pair(model(), p)

    def test_inputs_unchanged(self):
        m, p = model(), pair()
        expected = copy.deepcopy((m, p))
        ray.complete_pair(m, p)
        self.assertEqual((m, p), expected)

    def test_original_nongap_status_not_relabelled(self):
        p = pair()
        p["classification"]["status"] = "VERIFIED_A_GREATER_B"
        result = ray.audit_case({"model": model(), "result": {"pairs": [p]}})
        self.assertEqual(result, {})

    def test_feasible_point_from_subset_completes_opposite_sign(self):
        p = pair()
        p["minimize"].pop("primal")
        result = ray.complete_pair(model(), p, extra_points=[("verified_subset_case/primal", [0, 1])])
        self.assertEqual(result["derived_status"], "EXACT_BOTH_ORDERINGS_COMPLETED")

    def test_external_point_is_not_trusted_without_base_feasibility(self):
        with self.assertRaises(ValueError):
            ray.complete_pair(model(), pair(), extra_points=[("subset/primal", [0, 2])])


if __name__ == "__main__":
    unittest.main()
