"""Independent union-verifier tests: exact synthetic records, no LPs."""
import ast
import copy
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_interval_union_records as u


def feasible(point):
    return {"status": "EXACT_FEASIBLE", "solver_status": 0, "primal": {"verified": True, "point": point}}


def fixture():
    model = {"G": [[Q(-1), Q(0)], [Q(1), Q(0)], [Q(0), Q(1)]],
             "h": [Q(-2), Q(3), Q(1)], "n": 2, "names": ["a", "b"],
             "mass": Q(3), "upper_bounds": [Q(3), Q(1)]}
    impossible_b = {"status": "EXACT_INFEASIBLE", "solver_status": 2,
                    "farkas": {"verified": True, "y": ["1", "0", "1", "1"], "h_dot_y": "-1"}}
    bound = {"objective": ["1", "-1"], "solver_status": 0, "status": "VERIFIED_BOUND_AND_WITNESS",
             "primal": {"verified": True, "point": ["2", "1"]}, "feasible_objective": "1",
             "dual": {"verified": True, "lambda": ["-1", "0", "-1"], "residual": ["0", "0"],
                      "correction": "0", "lower_bound": "1", "upper_bounds_used": {}},
             "verified_lower_bound": "1", "verified_gap": "0", "crosscheck_agrees": True, "crosscheck_status": 0}
    result = {"feasibility": feasible(["2", "0"]), "overall_status": "EXACT_COMPATIBLE",
              "co_leaders": {"a": feasible(["2", "0"]), "b": impossible_b},
              "co_leader_search_complete": True, "candidate_leader": "a", "near_zero_threshold": "3/10000000",
              "leader_bounds": {"b": bound}, "verified_unique_leaders_above_margin_threshold": ["a"]}
    return model, result


def description(status="EXACT_COMPATIBLE", possible=("a",), unique=("a",)):
    return {"status": status, "possible": list(possible), "unique": list(unique)}


class ProofTests(unittest.TestCase):
    def test_exact_positive_record_and_call_count(self):
        m, r = fixture()
        d, calls = u.inspect_saved(m, r, [], Counter())
        self.assertEqual(d["unique"], ["a"])
        self.assertEqual(calls, 6)

    def test_all_joint_leader_inequalities_checked(self):
        m, r = fixture()
        r["co_leaders"]["b"] = feasible(["2", "1"])
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, [], Counter())

    def test_wrong_farkas_sign_rejected(self):
        m, r = fixture()
        r["co_leaders"]["b"]["farkas"]["y"][0] = "-1"
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, [], Counter())

    def test_missing_rival_bound_rejected(self):
        m, r = fixture()
        r["leader_bounds"] = {}
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, [], Counter())

    def test_changed_margin_rejected(self):
        m, r = fixture()
        r["near_zero_threshold"] = "0"
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, [], Counter())

    def test_unresolved_objective_blocks_declared_margin(self):
        m, r = fixture()
        r["leader_bounds"]["b"]["status"] = "NUMERICALLY_UNRESOLVED"
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, [], Counter())
        r["verified_unique_leaders_above_margin_threshold"] = []
        d, _ = u.inspect_saved(m, r, [], Counter())
        self.assertEqual(d["unique"], [])

    def test_one_prior_different_leader_allows_early_stop(self):
        m, r = fixture()
        r["co_leaders"].pop("b")
        r["co_leader_search_complete"] = False
        r["leader_bounds"] = {}
        r["verified_unique_leaders_above_margin_threshold"] = []
        r["stopping_reason"] = "SECOND_UNION_CO_LEADER_WITNESS"
        d, calls = u.inspect_saved(m, r, ["b"], Counter())
        self.assertFalse(d["exhaustive_model_decisions"])
        self.assertEqual(calls, 2)

    def test_falsely_complete_early_stop_rejected(self):
        m, r = fixture()
        with self.assertRaises(u.v.VerificationError):
            u.inspect_saved(m, r, ["b"], Counter())

    def test_guards_active_under_optimized_python(self):
        tree = ast.parse(Path(u.__file__).read_text())
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(tree)))


class UnionConclusionTests(unittest.TestCase):
    def test_incomplete_unique_never_promoted(self):
        self.assertTrue(u.expected_conclusion([description()])["status"].startswith("HOLD"))

    def test_complete_unique_with_empty_components(self):
        out = u.expected_conclusion([description(), description("EXACT_INFEASIBLE", (), ())], 2)
        self.assertEqual(out["unique_union_leader"], "a")

    def test_unresolved_component_blocks_positive(self):
        out = u.expected_conclusion([description(), description("NUMERICALLY_UNRESOLVED", (), ())], 2)
        self.assertTrue(out["status"].startswith("HOLD"))

    def test_exact_empty_not_vacuous_unique(self):
        out = u.expected_conclusion([description("EXACT_INFEASIBLE", (), ())], 1)
        self.assertEqual(out["status"], "EXACT_EMPTY_UNION")
        self.assertIsNone(out["unique_union_leader"])

    def test_late_opposite_leader_blocks_unique(self):
        out = u.expected_conclusion([description()] * 119 + [description(possible=("b",), unique=("b",))])
        self.assertEqual(out["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")

    def test_second_witness_valid_despite_other_unresolved(self):
        out = u.expected_conclusion([description("NUMERICALLY_UNRESOLVED", (), ()), description(possible=("a", "b"), unique=())])
        self.assertEqual(out["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")
        self.assertFalse(out["all_systems_visited"])

    def test_qualitative_unique_does_not_satisfy_fixed_margin_contract(self):
        out = u.expected_conclusion([description(unique=())], 1)
        self.assertTrue(out["status"].startswith("HOLD"))


class InputTests(unittest.TestCase):
    def test_alternative_own_mean_and_uncertainty(self):
        receptor = {"TMAC": "10"}
        profiles = {}
        for sid in u.v.SOURCES + ["SOIL08"]:
            profiles[sid] = {"SID": sid, "SIZE": "FINE"}
            for name in u.v.SPECIES:
                receptor[name], receptor[name[:-1]+"U"] = "1", ".1"
                profiles[sid][name] = ".4" if sid == "SOIL08" else ".2"
                profiles[sid][name[:-1]+"U"] = ".15" if sid == "SOIL08" else ".01"
        chosen = ["SOIL08"] + u.v.SOURCES[1:]
        before = copy.deepcopy(profiles)
        model = u.tuple_model(receptor, profiles, chosen, [chosen])
        self.assertEqual(model["L"][0][0], Q(1, 10))
        self.assertEqual(model["U"][0][0], Q(7, 10))
        self.assertEqual(model["sources"], chosen)
        self.assertEqual(model["names"][0], "soil")
        self.assertEqual(profiles, before)

    def test_unapproved_tuple_rejected(self):
        with self.assertRaises(u.v.VerificationError):
            u.tuple_model({}, {}, ["unknown"] * 7, [u.v.SOURCES])

    def test_native_solver_call_accounting(self):
        self.assertEqual(u.call_count({"solver_status": 0}), 1)
        self.assertEqual(u.call_count({"solver_status": 2}), 2)
        self.assertEqual(u.call_count({"solver_status": 0}, True), 2)
        self.assertEqual(u.call_count({"solver_status": 3}, True), 2)
        with self.assertRaises(u.v.VerificationError):
            u.call_count({"solver_status": 100})


if __name__ == "__main__":
    unittest.main()

