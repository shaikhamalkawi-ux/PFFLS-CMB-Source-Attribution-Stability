"""No native field LPs: deterministic synthetic and exact-certificate adversaries."""
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_interval_decisions as audit  # noqa: E402


def boxed(L, U, lo, hi, upper=None):
    return audit.make_model(L + [[-Q(v) for v in row] for row in U], hi + [-Q(v) for v in lo], bounds=upper)


def fake_field():
    receptor = {"TMAC": "7"}
    profiles = {sid: {} for sid in audit.native.CONFIG["central_initial_sources"]}
    for name in audit.native.CONFIG["species"]:
        receptor[name] = "7"
        receptor[name[:-1] + "U"] = "0.1"
        for sid in profiles:
            profiles[sid][name] = "1"
            profiles[sid][name[:-1] + "U"] = "0.01"
    return receptor, profiles


class IntervalExactTests(unittest.TestCase):
    def test_frozen_configuration_dependency_identity(self):
        config = audit.configuration()
        self.assertTrue(config["frozen_before_first_interval_field_LP"])
        self.assertEqual(config["k_values"], [1, 2, 3])

    def test_original_decimal_rational_input_not_float_endpoint(self):
        receptor, profiles = fake_field()
        sid = audit.native.CONFIG["central_initial_sources"][0]
        profiles[sid][audit.native.CONFIG["species"][0]] = "0.1234567890123456789"
        model = audit.field_model(receptor, profiles, [sid], 3, "joint_intervals", "none")
        self.assertEqual(model["L"][0][0], Q("0.0934567890123456789"))
        self.assertEqual(model["U"][0][0], Q("0.1534567890123456789"))

    def test_constructive_box_projection_and_zero_contribution(self):
        L, U = [[Q(1), Q(0)], [Q(0), Q(2)]], [[Q(2), Q(3)], [Q(1), Q(4)]]
        x = [Q(2), Q(0)]
        z = [Q(3), Q(1)]
        model = boxed(L, U, z, z)
        self.assertTrue(audit.exact_feasible(model, x))
        F = []
        for low, high, target in zip(L, U, z):
            a, b = audit.dot(low, x), audit.dot(high, x)
            t = (target - a) / (b - a) if b != a else Q(0)
            F.append([lo + t * (hi - lo) for lo, hi in zip(low, high)])
        self.assertEqual([audit.dot(row, x) for row in F], z)

    def test_projected_and_explicit_lifted_lp_bounds_agree(self):
        # Variables of the lifted problem are s0,s1,y00,y01,y10,y11.
        for L, U, concentration, source_caps in (
            ([[1, 0], [0, 1]], [[2, 1], [1, 2]], [2, 3], [2, 3]),
            ([[1, 0], [0, 1]], [[1, 0], [0, 1]], [0, 1], [0, 1]),
        ):
            with self.subTest(L=L, U=U, concentration=concentration):
                projected = boxed(L, U, concentration, concentration, source_caps)
                G, h = [], []
                for i in range(2):
                    for j in range(2):
                        yindex = 2 + 2 * i + j
                        lower, upper = [Q(0)] * 6, [Q(0)] * 6
                        lower[j], lower[yindex] = Q(L[i][j]), Q(-1)
                        upper[j], upper[yindex] = -Q(U[i][j]), Q(1)
                        G += [lower, upper]
                        h += [Q(0), Q(0)]
                    row = [Q(0)] * 6
                    row[2 + 2 * i], row[3 + 2 * i] = Q(1), Q(1)
                    G += [row, [-v for v in row]]
                    h += [Q(concentration[i]), -Q(concentration[i])]
                caps = source_caps + [U[i][j] * source_caps[j] for i in range(2) for j in range(2)]
                lifted = audit.make_model(G, h, bounds=caps)
                pfeas, lfeas = audit.feasibility(projected), audit.feasibility(lifted)
                self.assertEqual(pfeas["status"], "EXACT_FEASIBLE")
                self.assertEqual(lfeas["status"], "EXACT_FEASIBLE")
                for sign in (1, -1):
                    q = [Q(sign), Q(-sign)]
                    p = audit.objective_bound(projected, q, pfeas["primal"]["point"])
                    l = audit.objective_bound(lifted, q + [Q(0)] * 4, lfeas["primal"]["point"])
                    self.assertEqual(p["verified_lower_bound"], l["verified_lower_bound"])
                    self.assertEqual(p["feasible_objective"], l["feasible_objective"])

    def test_exact_zero_width_interval_solution(self):
        model = boxed([[Q(1), Q(0)], [Q(0), Q(1)]], [[Q(1), Q(0)], [Q(0), Q(1)]],
                      [Q(2), Q(3)], [Q(2), Q(3)], [Q(2), Q(3)])
        result = audit.feasibility(model)
        self.assertEqual(result["status"], "EXACT_FEASIBLE")
        self.assertEqual(result["primal"]["point"], [Q(2), Q(3)])
        bound = audit.objective_bound(model, [Q(1), Q(-1)], result["primal"]["point"])
        self.assertEqual(bound["verified_lower_bound"], Q(-1))
        self.assertEqual(bound["feasible_objective"], Q(-1))

    def test_farkas_certificate_for_contradictory_interval(self):
        model = audit.make_model([[1], [-1]], [1, -2], bounds=[1])
        result = audit.feasibility(model)
        self.assertEqual(result["status"], "EXACT_INFEASIBLE")
        self.assertTrue(audit.verify_farkas(model, result["farkas"]["y"]))
        self.assertEqual(audit.analyze_model(model)["overall_status"], "EXACT_INFEASIBLE")

    def test_nonempty_compatibility_needed_for_winner(self):
        result = audit.analyze_model(audit.make_model([[0]], [-1]))
        self.assertEqual(result["overall_status"], "EXACT_INFEASIBLE")
        self.assertEqual(result["pairs"], [])
        self.assertNotIn("verified_unique_leaders_above_margin_threshold", result)

    def test_exact_unbounded_requires_base_point_and_improving_ray(self):
        model = audit.make_model([[-1]], [-1])
        feasible = audit.feasibility(model)
        result = audit.objective_bound(model, [Q(-1)], feasible["primal"]["point"])
        self.assertEqual(result["status"], "EXACT_UNBOUNDED")
        ray = result["recession"]["ray"]
        self.assertTrue(all(v >= 0 for v in ray))
        self.assertLess(audit.dot([Q(-1)], ray), 0)
        self.assertTrue(all(audit.dot(row, ray) <= 0 for row in model["G"]))
        without_base = audit.objective_bound(model, [Q(-1)])
        self.assertEqual(without_base["status"], "NUMERICALLY_UNRESOLVED")

    def test_one_sided_strict_order_survives_opposite_unboundedness(self):
        # A>=2, 0<=B<=1: A-B>=1, while A-B is unbounded above.
        model = audit.make_model([[-1, 0], [0, 1]], [-2, 1], bounds=[None, 1])
        result = audit.analyze_model(model)
        pair = result["pairs"][0]
        self.assertEqual(pair["minimize"]["status"], "VERIFIED_BOUND_AND_WITNESS")
        self.assertEqual(pair["maximize_negative"]["status"], "EXACT_UNBOUNDED")
        self.assertEqual(pair["classification"]["status"], "VERIFIED_A_GREATER_B")
        self.assertEqual(result["verified_unique_leaders_above_margin_threshold"], ["0"])
        reverse = audit.analyze_model(audit.make_model([[0, -1], [1, 0]], [-2, 1], bounds=[1, None]))
        self.assertEqual(reverse["pairs"][0]["classification"]["status"], "VERIFIED_B_GREATER_A")
        self.assertEqual(reverse["verified_unique_leaders_above_margin_threshold"], ["1"])

    def test_exact_repair_rejects_tolerance_only_infeasibility(self):
        model = audit.make_model([[1], [-1]], [Q(1), Q(-1)])
        self.assertFalse(audit.exact_feasible(model, [Q("1.0000000001")]))
        repaired = audit.repair_primal(model, [1.0000000001])
        self.assertTrue(repaired["verified"])
        self.assertEqual(repaired["point"], [Q(1)])

    def test_repair_failure_does_not_fabricate_point(self):
        model = audit.make_model([[1], [-1]], [0, -1])
        self.assertFalse(audit.repair_primal(model, [0.5])["verified"])

    def test_dual_residual_corrected_bound_with_justified_cap(self):
        model = audit.make_model([[1]], [1], bounds=[1])
        bound = audit.lower_certificate(model, [Q(-1)], [-0.999999999999])
        self.assertTrue(bound["verified"])
        self.assertEqual(bound["lower_bound"], -1)
        self.assertLess(bound["correction"], 0)

    def test_dual_residual_without_valid_cap_is_unresolved(self):
        model = audit.make_model([[1]], [1])
        bound = audit.lower_certificate(model, [Q(-1)], [-0.999999999999])
        self.assertFalse(bound["verified"])
        self.assertEqual(bound["reason"], "DUAL_RESIDUAL_REQUIRES_UNAVAILABLE_UPPER_BOUND")

    def test_positive_dual_marginals_clipped_and_rechecked(self):
        model = audit.make_model([[1]], [1], bounds=[1])
        bound = audit.lower_certificate(model, [Q(1)], [0.1])
        self.assertTrue(bound["verified"])
        self.assertEqual(bound["lambda"], [Q(0)])
        self.assertEqual(bound["lower_bound"], 0)

    def test_nonfinite_dual_cannot_be_verified(self):
        self.assertFalse(audit.lower_certificate(audit.make_model([[1]], [1]), [Q(1)], [float("nan")])["verified"])

    def test_possible_co_leader_requires_joint_feasibility(self):
        # a=1, b+c=3. a>=b separately and a>=c separately are possible, but not both.
        base = audit.make_model([[1, 0, 0], [-1, 0, 0], [0, 1, 1], [0, -1, -1]], [1, -1, 3, -3], bounds=[1, 3, 3])
        for row in ([-1, 1, 0], [-1, 0, 1]):
            separate = audit.make_model(base["G"] + [row], base["h"] + [0], bounds=[1, 3, 3])
            self.assertEqual(audit.feasibility(separate)["status"], "EXACT_FEASIBLE")
        self.assertEqual(audit.feasibility(audit.co_leader_model(base, 0))["status"], "EXACT_INFEASIBLE")

    def test_feasible_tie_not_arbitrarily_broken(self):
        model = boxed([[1, 0], [0, 1]], [[1, 0], [0, 1]], [1, 1], [1, 1], [1, 1])
        result = audit.analyze_model(model)
        self.assertEqual(result["pairs"][0]["classification"]["status"], "EXACT_TIE_WITNESSED")
        self.assertEqual(result["exact_possible_co_leaders"], ["0", "1"])
        self.assertEqual(result["verified_unique_leaders_above_margin_threshold"], [])

    def test_box_vs_composition_can_change_leader(self):
        box = boxed([[1, 0], [0, 1]], [[1, 0], [1, 1]], [1, Q(3, 2)], [1, Q(3, 2)], [1, Q(3, 2)])
        self.assertTrue(audit.exact_feasible(box, [Q(1), Q(1, 2)]))
        composition = boxed([[1, 0], [0, 1]], [[1, 0], [0, 1]], [1, Q(3, 2)], [1, Q(3, 2)], [1, Q(3, 2)])
        result = audit.analyze_model(composition)
        self.assertEqual(result["verified_unique_leaders_above_margin_threshold"], ["1"])

    def test_profile_union_does_not_equal_entrywise_envelope(self):
        a = boxed([[1], [0]], [[1], [0]], [1, 1], [1, 1])
        b = boxed([[0], [1]], [[0], [1]], [1, 1], [1, 1])
        self.assertEqual(audit.feasibility(a)["status"], "EXACT_INFEASIBLE")
        self.assertEqual(audit.feasibility(b)["status"], "EXACT_INFEASIBLE")
        envelope = boxed([[0], [0]], [[1], [1]], [1, 1], [1, 1])
        self.assertTrue(audit.exact_feasible(envelope, [Q(2)]))

    def test_known_true_vector_and_interval_nesting(self):
        receptor, profiles = fake_field()
        sources = audit.native.CONFIG["central_initial_sources"]
        point = [Q(1)] * len(sources)
        for mass in ("none", "historical_80_120_band"):
            for k in (1, 2, 3):
                fixed = audit.field_model(receptor, profiles, sources, k, "fixed_profile", mass)
                joint = audit.field_model(receptor, profiles, sources, k, "joint_intervals", mass)
                self.assertTrue(audit.exact_feasible(fixed, point))
                self.assertTrue(audit.exact_feasible(joint, point))
                self.assertTrue(all(a <= b for a, b in zip(fixed["h"], joint["h"])))
                for a, b in zip(fixed["G"], joint["G"]):
                    self.assertTrue(all(y <= x for x, y in zip(a, b)))

    def test_retained_universe_embedding_in_full_by_zeros(self):
        receptor, profiles = fake_field()
        full = audit.native.CONFIG["central_initial_sources"]
        for mass in ("none", "historical_80_120_band"):
            for mode in ("fixed_profile", "joint_intervals"):
                small = audit.field_model(receptor, profiles, [full[0]], 2, mode, mass)
                large = audit.field_model(receptor, profiles, full, 2, mode, mass)
                self.assertTrue(audit.exact_feasible(small, [Q(7)]))
                self.assertTrue(audit.exact_feasible(large, [Q(7)] + [Q(0)] * 6))

    def test_nominal_zero_source_removal_changes_interval_bounds(self):
        # Nominal exact system has s=(1,0); the second source is then removed.
        F = [[1, 1], [0, 1]]
        nominal = boxed(F, F, [1, 0], [1, 0], [1, 0])
        self.assertEqual(audit.feasibility(nominal)["primal"]["point"], [Q(1), Q(0)])
        full = boxed(F, F, [1, 0], [1, 1], [1, 1])
        retained = boxed([[1], [0]], [[1], [0]], [1, 0], [1, 1], [1])
        fpoint, rpoint = audit.feasibility(full), audit.feasibility(retained)
        fb = audit.objective_bound(full, [Q(1), Q(0)], fpoint["primal"]["point"])
        rb = audit.objective_bound(retained, [Q(1)], rpoint["primal"]["point"])
        self.assertEqual(fb["verified_lower_bound"], Q(0))
        self.assertEqual(rb["verified_lower_bound"], Q(1))
        self.assertTrue(audit.exact_feasible(full, [Q(0), Q(1)]))

    def test_missing_profile_and_negative_uncertainty_fail_closed(self):
        receptor, profiles = fake_field()
        sid, species = audit.native.CONFIG["central_initial_sources"][0], audit.native.CONFIG["species"][0]
        profiles[sid][species] = "-99"
        with self.assertRaises(ValueError):
            audit.field_model(receptor, profiles, [sid], 1, "joint_intervals", "none")
        profiles[sid][species] = "1"
        profiles[sid][species[:-1] + "U"] = "-1"
        with self.assertRaises(ValueError):
            audit.field_model(receptor, profiles, [sid], 1, "joint_intervals", "none")

    def test_unapproved_scenarios_fail_closed(self):
        receptor, profiles = fake_field()
        sid = audit.native.CONFIG["central_initial_sources"][0]
        with self.assertRaises(ValueError):
            audit.field_model(receptor, profiles, [sid], 4, "joint_intervals", "none")
        with self.assertRaises(ValueError):
            audit.field_model(receptor, profiles, [sid], 1, "joint_intervals", "physical_mass_upper")

    def test_nonpositive_lower_bound_does_not_prove_reversal(self):
        low = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(-1), "feasible_objective": Q(2)}
        high = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(-4), "feasible_objective": Q(-3)}
        status = audit.pair_classification(low, high, Q(1, 10_000_000))["status"]
        self.assertEqual(status, "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP")

    def test_two_verified_opposite_witnesses_establish_both_orderings(self):
        low = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(-2), "feasible_objective": Q(-1)}
        high = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(-4), "feasible_objective": Q(-3)}
        self.assertEqual(audit.pair_classification(low, high, Q(1, 10_000_000))["status"], "EXACT_BOTH_ORDERINGS_WITNESSED")

    def test_near_zero_positive_margin_is_explicit_hold(self):
        low = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(1, 1_000_000_000), "feasible_objective": Q(1)}
        high = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": Q(-4), "feasible_objective": Q(-3)}
        self.assertEqual(audit.pair_classification(low, high, Q(1, 10_000_000))["status"], "NEAR_ZERO_HOLD")

    def test_numerical_exception_status_not_hidden(self):
        with patch.object(audit, "linprog", side_effect=RuntimeError("synthetic solver failure")):
            result = audit.feasibility(audit.make_model([[1]], [1]))
        self.assertEqual(result["status"], "NUMERICALLY_UNRESOLVED")
        self.assertEqual(result["solver_status"], 4)

    def test_unverified_farkas_is_not_infeasible_certificate(self):
        model = audit.make_model([[1]], [1])
        self.assertFalse(audit.verify_farkas(model, [Q(1)]))
        self.assertFalse(audit.verify_farkas(model, [Q(-1)]))


if __name__ == "__main__":
    unittest.main()
