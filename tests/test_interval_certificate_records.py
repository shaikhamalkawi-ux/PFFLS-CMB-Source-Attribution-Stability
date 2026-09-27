"""Adversarial tests for the independent proof replayer; no field LPs."""
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_interval_certificate_records as verify


def bounded_run():
    return {"objective": ["-1"], "status": "VERIFIED_BOUND_AND_WITNESS",
            "primal": {"verified": True, "point": ["1"]},
            "feasible_objective": "-1", "verified_lower_bound": "-1", "verified_gap": "0",
            "dual": {"verified": True, "lambda": ["-1"], "residual": ["0"],
                     "correction": "0", "lower_bound": "-1", "upper_bounds_used": {}},
            "crosscheck_agrees": True, "crosscheck_status": 0}


def unbounded_run():
    return {"objective": ["-1"], "status": "EXACT_UNBOUNDED",
            "recession": {"verified": True, "point": ["1"], "ray": ["1"], "objective_ray": "-1"}}


class CertificateReplayTests(unittest.TestCase):
    def check_bounded(self, run, caps=None):
        verify.verify_objective(run, [[Q(1)]], [Q(1)], 1, [Q(1)] if caps is None else caps,
                                [Q(-1)], "none", Counter())

    def test_valid_primal_and_dual(self):
        self.check_bounded(bounded_run())

    def test_invalid_primal_rejected(self):
        bad = bounded_run()
        bad["primal"]["point"] = ["10000000001/10000000000"]
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_inactive_inequality_checked(self):
        with self.assertRaises(verify.VerificationError):
            verify.primal_point([[Q(1)], [Q(-1)]], [Q(1), Q(-2)], ["1"], 1)

    def test_negative_primal_rejected(self):
        with self.assertRaises(verify.VerificationError):
            verify.primal_point([[Q(1)]], [Q(1)], ["-1/1000000000000"], 1)

    def test_wrong_objective_mapping_rejected(self):
        bad = bounded_run()
        bad["objective"] = ["1"]
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_positive_dual_multiplier_rejected(self):
        bad = bounded_run()
        bad["dual"]["lambda"] = ["1"]
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_dual_residual_cannot_be_self_asserted(self):
        bad = bounded_run()
        bad["dual"]["residual"] = ["1/1000000000000"]
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_corrected_bound_with_valid_cap(self):
        good = bounded_run()
        good["dual"].update({"lambda": ["-999/1000"], "residual": ["-1/1000"],
                             "correction": "-1/1000", "upper_bounds_used": {"0": "1"}})
        self.check_bounded(good)
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(good, [None])

    def test_fake_cap_provenance_rejected(self):
        bad = bounded_run()
        bad["dual"].update({"lambda": ["-999/1000"], "residual": ["-1/1000"],
                            "correction": "-1/1000", "upper_bounds_used": {"0": "1/2"}})
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_fabricated_bound_and_gap_rejected(self):
        for key in ("verified_lower_bound", "verified_gap"):
            bad = bounded_run()
            bad[key] = "0" if key == "verified_lower_bound" else "1"
            with self.assertRaises(verify.VerificationError):
                self.check_bounded(bad)

    def test_unverified_dual_cannot_supply_bound(self):
        bad = bounded_run()
        bad["dual"]["verified"] = False
        with self.assertRaises(verify.VerificationError):
            self.check_bounded(bad)

    def test_valid_farkas_certificate(self):
        verify.farkas([[Q(1)], [Q(-1)]], [Q(1), Q(-2)], 1,
                      {"verified": True, "y": ["1", "1"], "h_dot_y": "-1"})

    def test_farkas_wrong_multiplier_sign_rejected(self):
        with self.assertRaises(verify.VerificationError):
            verify.farkas([[Q(1)], [Q(-1)]], [Q(1), Q(-2)], 1,
                          {"verified": True, "y": ["-1", "-1"], "h_dot_y": "1"})

    def test_farkas_wrong_column_sign_rejected(self):
        with self.assertRaises(verify.VerificationError):
            verify.farkas([[Q(-1)]], [Q(-1)], 1,
                          {"verified": True, "y": ["1"], "h_dot_y": "-1"})

    def test_farkas_zero_is_not_strict_contradiction(self):
        with self.assertRaises(verify.VerificationError):
            verify.farkas([[Q(0)]], [Q(0)], 1,
                          {"verified": True, "y": ["1"], "h_dot_y": "0"})

    def test_valid_recession_certificate(self):
        verify.verify_objective(unbounded_run(), [[Q(-1)]], [Q(-1)], 1, [None], [Q(-1)], "none", Counter())

    def test_recession_needs_valid_base_and_direction(self):
        for key, value in (("point", ["0"]), ("ray", ["-1"]), ("ray", ["0"]), ("objective_ray", "0")):
            bad = unbounded_run()
            bad["recession"][key] = value
            with self.assertRaises(verify.VerificationError):
                verify.verify_objective(bad, [[Q(-1)]], [Q(-1)], 1, [None], [Q(-1)], "none", Counter())

    def test_historical_mass_unbounded_claim_rejected(self):
        with self.assertRaises(verify.VerificationError):
            verify.verify_objective(unbounded_run(), [[Q(-1)]], [Q(-1)], 1, [None], [Q(-1)], "historical_80_120_band", Counter())

    def test_all_co_leader_constraints_required(self):
        G = [[Q(1), Q(0)], [Q(-1), Q(0)], [Q(0), Q(1)], [Q(0), Q(-1)], [Q(-1), Q(1)]]
        h = [Q(1), Q(-1), Q(2), Q(-2), Q(0)]
        with self.assertRaises(verify.VerificationError):
            verify.verify_feasibility({"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": ["1", "2"]}}, G, h, 2, Counter())

    def test_one_sided_bound_with_opposite_unboundedness(self):
        low = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": "1", "feasible_objective": "1"}
        opposite = {"status": "EXACT_UNBOUNDED"}
        result = verify.classify_pair(low, opposite, Q(1, 10000000))
        self.assertEqual(result["status"], "VERIFIED_A_GREATER_B")
        self.assertEqual(verify.classify_pair(opposite, low, Q(1, 10000000))["status"], "VERIFIED_B_GREATER_A")

    def test_nonpositive_bound_does_not_prove_reversal(self):
        low = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": "-1", "feasible_objective": "2"}
        negative = {"status": "VERIFIED_BOUND_AND_WITNESS", "verified_lower_bound": "-4", "feasible_objective": "-3"}
        self.assertEqual(verify.classify_pair(low, negative, Q(1, 10000000))["status"], "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP")

    def test_rational_parser_rejects_float_bool_nan_and_bad_fraction(self):
        for value in (0.1, True, "nan", "1/0"):
            with self.assertRaises(verify.VerificationError):
                verify.fraction(value)

    def test_guards_survive_python_optimization(self):
        tree = ast.parse(Path(verify.__file__).read_text(encoding="utf-8"))
        self.assertEqual([node for node in ast.walk(tree) if isinstance(node, ast.Assert)], [])

    def test_original_decimal_model_and_caps_reconstructed(self):
        receptor = {"TMAC": "1"}
        sid = verify.SOURCES[0]
        profiles = {sid: {}}
        for species in verify.SPECIES:
            receptor[species], receptor[species[:-1] + "U"] = "1", "0.01"
            profiles[sid][species], profiles[sid][species[:-1] + "U"] = "1", "0.1"
        model = verify.reconstruct_model(receptor, profiles, [sid], 1, "joint_intervals", "none")
        self.assertEqual(model["upper_bounds"], [Q(101, 90)])
        self.assertEqual(model["L"][0], [Q(9, 10)])
        self.assertEqual(model["U"][0], [Q(11, 10)])
        altered = deepcopy(profiles)
        altered[sid][verify.SPECIES[0]] = "-99"
        with self.assertRaises(verify.VerificationError):
            verify.reconstruct_model(receptor, altered, [sid], 1, "joint_intervals", "none")


if __name__ == "__main__":
    unittest.main()
