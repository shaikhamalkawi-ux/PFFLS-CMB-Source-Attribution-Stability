"""Bounded lazy-union logic and tiny synthetic LPs; no field LPs."""
import copy
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_interval_profile_union as union


def d(status="EXACT_COMPATIBLE", possible=("a",), unique=("a",)):
    return {"status": status, "possible": list(possible), "unique": list(unique)}


class UnionLogicTests(unittest.TestCase):
    def test_inherited_ambiguity_proves_union_nonunique_without_exhaustion(self):
        r = union.conclusion([d(possible=("a", "b"), unique=())], 120)
        self.assertEqual(r["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")
        self.assertFalse(r["all_systems_visited"])
        self.assertFalse(r["full_possible_leader_set_claimed"])

    def test_unique_leader_survives_complete_union(self):
        r = union.conclusion([d(), d(), d("EXACT_INFEASIBLE", (), ())], 3)
        self.assertEqual(r["status"], "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN")
        self.assertEqual(r["unique_union_leader"], "a")

    def test_late_system_changes_union_leader(self):
        r = union.conclusion([d()] * 119 + [d(possible=("b",), unique=("b",))], 120)
        self.assertEqual(r["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")

    def test_all_systems_infeasible_is_empty_not_vacuous_unique(self):
        r = union.conclusion([d("EXACT_INFEASIBLE", (), ())] * 120, 120)
        self.assertEqual(r["status"], "EXACT_EMPTY_UNION")
        self.assertIsNone(r["unique_union_leader"])

    def test_incomplete_all_infeasible_is_hold(self):
        self.assertEqual(union.conclusion([d("EXACT_INFEASIBLE", (), ())], 120)["status"], "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION")

    def test_unresolved_system_prevents_positive_union_certificate(self):
        r = union.conclusion([d(), d("NUMERICALLY_UNRESOLVED", (), ())], 2)
        self.assertEqual(r["status"], "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION")

    def test_single_possible_coleader_not_enough_for_strict_unique(self):
        r = union.conclusion([d(unique=())], 1)
        self.assertEqual(r["status"], "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION")

    def test_unresolved_compatible_margin_blocks_positive(self):
        r = union.conclusion([d(), d(unique=())], 2)
        self.assertEqual(r["status"], "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION")

    def test_second_witness_still_valid_when_other_system_unresolved(self):
        r = union.conclusion([d(), d("NUMERICALLY_UNRESOLVED", (), ()), d(possible=("b",), unique=())], 120)
        self.assertEqual(r["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")

    def test_two_witnesses_from_one_tie_exclude_strict_unique(self):
        self.assertEqual(union.conclusion([d(possible=("a", "b"), unique=())], 1)["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")

    def test_too_many_descriptions_rejected(self):
        with self.assertRaises(ValueError):
            union.conclusion([d(), d()], 1)

    def test_grid_is_120_with_central_first_and_fixed_last_three(self):
        families = {"SOIL03": ["SOIL03", "SOIL08", "SOIL12", "SOIL29"],
                    "BAMAJC": ["BAMAJC", "MAFISC", "MAMAJC"], "SFCRUC": ["SFCRUC", "CHCRUC"],
                    "MOVES2": ["MOVES2", "MOVES1", "MOVES3", "MOVES4", "MOVES5"]}
        grid = union.profile_grid(families)
        self.assertEqual(len(grid), 120)
        self.assertEqual(grid[0], union.SLOTS)
        self.assertTrue(all(t[-3:] == union.SLOTS[-3:] for t in grid))

    def test_alternative_carries_its_own_uncertainty_and_stable_label(self):
        species = union.core.native.CONFIG["species"]
        receptor = {"TMAC": "10"}
        for name in species:
            receptor[name], receptor[name[:-1] + "U"] = "1", ".1"
        profiles = {}
        for sid in union.SLOTS + ["SOIL08"]:
            profiles[sid] = {}
            for name in species:
                profiles[sid][name] = ".4" if sid == "SOIL08" else ".2"
                profiles[sid][name[:-1] + "U"] = ".15" if sid == "SOIL08" else ".01"
        original = copy.deepcopy(profiles)
        chosen = ["SOIL08"] + union.SLOTS[1:]
        m = union.tuple_model(receptor, profiles, chosen)
        self.assertEqual(m["L"][0][0], Q(1, 10))
        self.assertEqual(m["U"][0][0], Q(7, 10))
        self.assertEqual(m["names"][0], "soil")
        self.assertEqual(m["sources"][0], "SOIL08")
        self.assertEqual(profiles, original)

    def test_incomplete_profile_tuple_rejected(self):
        with self.assertRaises(ValueError):
            union.tuple_model({}, {}, ["SOIL03"])

    def test_short_case_path_preserves_full_hash_inside_private_workspace(self):
        path = union.case_path("a" * 64)
        self.assertTrue(path.resolve().is_relative_to(union.PRIVATE.resolve()))
        self.assertLess(len(str(path)), 260)
        self.assertEqual(path.name, "u_" + "a" * 64 + ".json")

    def test_interrupted_model_call_upper_bound_is_conservative(self):
        # The reviewed producer uses at most two solves per feasibility/objective
        # (primary + phaseI, crosscheck, or ray); exact repairs do not call LPs.
        self.assertEqual(union.PRIOR_CALLS_RESERVED, 1 + 7 * 2 + 6 * 2)


class BudgetTests(unittest.TestCase):
    def budget(self, maximum=2, elapsed=0, remaining=100):
        instant = datetime(2026, 9, 26, tzinfo=timezone.utc)
        ticks = iter([0, elapsed, elapsed, elapsed, elapsed, elapsed])
        return union.SolverBudget(maximum=maximum, seconds=100, cutoff=instant + timedelta(seconds=remaining),
                                  monotonic=lambda: next(ticks), utc=lambda: instant)

    def test_every_wrapped_call_counted_and_solver_time_limited(self):
        calls = []
        fake = lambda *a, **kw: calls.append(kw) or SimpleNamespace(status=0)
        with patch.object(union.core, "linprog", fake):
            with self.budget() as b:
                union.core.solve_float(union.core.make_model([[1]], [1]), [Q(0)])
                union.core.solve_float(union.core.make_model([[1]], [1]), [Q(0)], method="highs-ipm")
                with self.assertRaises(union.BudgetExceeded):
                    union.core.solve_float(union.core.make_model([[1]], [1]), [Q(0)])
            self.assertIs(union.core.linprog, fake)
        self.assertEqual(b.calls, 2)
        self.assertEqual([c["options"]["time_limit"] for c in calls], [100, 100])

    def test_timeout_stops_before_any_new_solver_call(self):
        with self.assertRaises(union.BudgetExceeded):
            self.budget(elapsed=100).remaining()

    def test_absolute_qa_cutoff_stops(self):
        with self.assertRaises(union.BudgetExceeded):
            self.budget(remaining=0).remaining()

    def test_wrapper_restored_on_exception(self):
        original = union.core.linprog
        with self.assertRaises(KeyError):
            with self.budget():
                raise KeyError("synthetic")
        self.assertIs(union.core.linprog, original)

    def test_real_objective_primary_and_crosscheck_both_counted(self):
        m = union.core.make_model([[1]], [2], bounds=[2])
        with union.SolverBudget(cutoff=datetime.now(timezone.utc) + timedelta(minutes=1)) as b:
            r = union.core.objective_bound(m, [Q(1)], [Q(0)])
        self.assertEqual(r["status"], "VERIFIED_BOUND_AND_WITNESS")
        self.assertEqual(b.calls, 2)

    def test_real_phase_one_helper_is_counted(self):
        m = union.core.make_model([[1], [-1]], [0, -1])
        with union.SolverBudget(cutoff=datetime.now(timezone.utc) + timedelta(minutes=1)) as b:
            r = union.core.feasibility(m)
        self.assertEqual(r["status"], "EXACT_INFEASIBLE")
        self.assertEqual(b.calls, 2)

    def test_real_recession_helper_is_counted(self):
        m = union.core.make_model([], [], n=1)
        with union.SolverBudget(cutoff=datetime.now(timezone.utc) + timedelta(minutes=1)) as b:
            r = union.core.objective_bound(m, [Q(-1)], [Q(0)])
        self.assertEqual(r["status"], "EXACT_UNBOUNDED")
        self.assertEqual(b.calls, 2)


class TinyModelTests(unittest.TestCase):
    def test_joint_coleader_not_pairwise_shortcut(self):
        # a=1,b+c=3: a can exceed b or c separately but cannot co-lead.
        m = union.core.make_model([[1, 0, 0], [-1, 0, 0], [0, 1, 1], [0, -1, -1]],
                                  [1, -1, 3, -3], names=["a", "b", "c"], bounds=[1, 3, 3])
        m["mass"] = Q(4)
        result = union.inspect_model(m, [])
        self.assertEqual(result["co_leaders"]["a"]["status"], "EXACT_INFEASIBLE")
        self.assertEqual(union.describe(result)["possible"], ["b", "c"])
        self.assertFalse(result["co_leader_search_complete"])

    def test_strict_leader_has_all_one_sided_margins(self):
        m = union.core.make_model([[-1, 0], [1, 0], [0, 1]], [-2, 3, 1], names=["a", "b"], bounds=[3, 1])
        m["mass"] = Q(3)
        result = union.inspect_model(m, [])
        self.assertEqual(result["verified_unique_leaders_above_margin_threshold"], ["a"])
        self.assertEqual(result["leader_bounds"]["b"]["verified_lower_bound"], 1)

    def test_same_family_inherited_does_not_count_as_second(self):
        m = union.core.make_model([[-1, 0], [1, 0], [0, 1]], [-2, 3, 1], names=["a", "b"], bounds=[3, 1])
        m["mass"] = Q(3)
        self.assertEqual(union.inspect_model(m, ["a"])["verified_unique_leaders_above_margin_threshold"], ["a"])

    def test_inherited_other_family_stops_without_bounds(self):
        m = union.core.make_model([[-1, 0], [1, 0], [0, 1]], [-2, 3, 1], names=["a", "b"], bounds=[3, 1])
        m["mass"] = Q(3)
        r = union.inspect_model(m, ["b"])
        self.assertEqual(r["stopping_reason"], "SECOND_UNION_CO_LEADER_WITNESS")
        self.assertEqual(r["leader_bounds"], {})


if __name__ == "__main__":
    unittest.main()
