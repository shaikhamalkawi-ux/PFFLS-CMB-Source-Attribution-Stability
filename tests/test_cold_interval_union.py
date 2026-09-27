"""Synthetic/metadata-only producer gate. No original field LPs or private reads."""
import ast
from collections import Counter
import copy
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reproduce_interval_union as p


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class MemoryJournal:
    def __init__(self, after=None):
        self.rows = []
        self.after = after

    def event(self, event, budget, **extra):
        self.rows.append({"event": event, "lp_calls": budget.calls,
                          "model_key": budget.model_key, **extra})
        if self.after:
            self.after(event)
        return len(self.rows) - 1


def example(mass=10):
    model = p.core.make_model([[-1, 0], [0, 1]], [-2, 1], names=["a", "b"])
    model["mass"] = Q(mass)
    result = {"overall_status": "EXACT_COMPATIBLE",
              "feasibility": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [2, 1]}},
              "co_leaders": {
                  "a": {"status": "EXACT_FEASIBLE", "primal": {"verified": True, "point": [2, 1]}},
                  "b": {"status": "EXACT_INFEASIBLE", "farkas": {"verified": True, "y": [1, 1, 1]}}},
              "leader_bounds": {"b": {"status": "NUMERICALLY_UNRESOLVED"}},
              "verified_unique_leaders_above_margin_threshold": [], "co_leader_search_complete": True}
    return model, result


def plain_result(possible=(), status="EXACT_COMPATIBLE", unique=()):
    return {"overall_status": status, "feasibility": {"status": status},
            "co_leaders": {x: {"status": "EXACT_FEASIBLE"} for x in possible},
            "leader_bounds": {}, "verified_unique_leaders_above_margin_threshold": list(unique),
            "co_leader_search_complete": False}


def fixture(output, sample_count=2, tuple_count=3):
    output.mkdir()
    (output / "cases").mkdir()
    model, _ = example()
    manifest = {"schema": p.SCHEMA, "run_id": "synthetic-only",
                "samples": [{"sample_index": i} for i in range(sample_count)],
                "tuples": [[j] for j in range(tuple_count)], "models": []}
    for i in range(sample_count):
        for j in range(tuple_count):
            manifest["models"].append({"sample_index": i, "tuple_index": j,
                "model_key": f"s{i:02d}_t{j:03d}", "model_sha256": p.digest(p.data(model)),
                "case_file": f"cases/m_{i:02d}_{j:03d}.json"})
    manifest_sha = p.exclusive_json(output / "manifest.json", manifest)
    p.exclusive_json(output / "preflight.json", {"schema": p.SCHEMA, "manifest_sha256": manifest_sha, "field_lp_calls": 0})
    p.exclusive_json(output / "run_started.json", {"schema": p.SCHEMA, "manifest_sha256": manifest_sha})
    return manifest, model


class BudgetTests(unittest.TestCase):
    def budget(self, calls=10, seconds=20, after=None):
        self.clock = Clock()
        b = p.Budget(p.budget_config(calls=calls, seconds=seconds), clock=self.clock)
        b.journal = MemoryJournal(after)
        b.original = Mock(return_value=SimpleNamespace(status=0))
        return b

    def test_ceiling_validation(self):
        for kwargs in ({"models": 4201}, {"models": 0}, {"models": True}, {"calls": 20001},
                       {"calls": 0}, {"seconds": 7201}, {"seconds": 0}, {"seconds": float("nan")},
                       {"seconds": float("inf")}, {"seconds": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                p.budget_config(**kwargs)

    def test_deadline_must_be_timezone_aware(self):
        with self.assertRaises(ValueError):
            p.parse_deadline("2026-01-01T00:00:00")
        self.assertEqual(p.parse_deadline("2026-01-01T04:00:00+04:00").hour, 0)

    def test_expired_deadline_prevents_model_and_call(self):
        utc = datetime(2030, 1, 1, tzinfo=timezone.utc)
        b = p.Budget(p.budget_config(deadline=utc.isoformat()), utc=lambda: utc)
        b.journal = MemoryJournal()
        for fn in (lambda: b.begin_model("x"), lambda: b.call()):
            with self.assertRaises(p.BudgetStop):
                fn()
        self.assertEqual((b.models, b.calls), (0, 0))

    def test_count_charged_before_dispatch_and_no_overrun(self):
        b = self.budget(calls=1)
        b.original.side_effect = lambda *a, **kw: (
            self.assertEqual((b.calls, b.journal.rows[-1]["event"]), (1, "LP_BEGIN"))
            or SimpleNamespace(status=0))
        b.call([1])
        with self.assertRaises(p.BudgetStop):
            b.call([1])
        self.assertEqual(b.original.call_count, 1)
        self.assertEqual(b.snapshot()["solver_invocation_attempts"], 1)

    def test_post_flush_expiry_is_charged_not_invoked(self):
        b = self.budget(seconds=2, after=lambda event: setattr(self.clock, "t", 2) if event == "LP_BEGIN" else None)
        with self.assertRaises(p.BudgetStop):
            b.call()
        b.original.assert_not_called()
        self.assertEqual((b.calls, b.invocation_attempts, b.precall_aborted), (1, 0, 1))
        self.assertTrue(b.journal.rows[-1]["charged_but_not_invoked"])

    def test_post_flush_allowance_is_fresh(self):
        b = self.budget(seconds=10, after=lambda event: setattr(self.clock, "t", 7) if event == "LP_BEGIN" else None)
        b.call(options={"presolve": False, "time_limit": 9})
        self.assertEqual(b.original.call_args.kwargs["options"], {"presolve": False, "time_limit": 3})
        self.assertEqual(b.journal.rows[-1]["dispatch_remaining_seconds"], 3)

    def test_delayed_event_keeps_original_admission_sample_and_fresh_dispatch(self):
        b = self.budget(seconds=10)
        self.clock.t = 1
        original_event = b.journal.event
        def delayed(event, budget, **extra):
            if event == "LP_BEGIN":
                self.clock.t += 0.1  # Scheduling delay before event timestamp/flush.
            return original_event(event, budget, **extra)
        b.journal.event = delayed
        b.call()
        begin, end = b.journal.rows
        self.assertEqual((begin["admission_gate_elapsed_seconds"], begin["remaining_seconds"]), (1, 9))
        self.assertAlmostEqual(end["dispatch_gate_elapsed_seconds"], 1.1)
        self.assertAlmostEqual(end["dispatch_remaining_seconds"], 8.9)
        self.assertEqual(b.original.call_args.kwargs["options"]["time_limit"], end["dispatch_remaining_seconds"])

    def test_model_admission_sample_is_preserved_through_delayed_event(self):
        b = self.budget(seconds=10, after=lambda event: setattr(self.clock, "t", 11))
        self.clock.t = 9
        b.begin_model("one")
        self.assertEqual(b.journal.rows[0]["admission_gate_elapsed_seconds"], 9)
        with self.assertRaises(p.BudgetStop):
            b.call()
        self.assertEqual((b.models, b.calls), (1, 0))

    def test_requested_shorter_allowance_preserved(self):
        b = self.budget()
        b.call(options={"time_limit": 0.25})
        self.assertEqual(b.original.call_args.kwargs["options"]["time_limit"], 0.25)

    def test_invalid_numerical_allowance_charged_without_dispatch(self):
        for limit in (-1, 0, float("nan"), float("inf"), True):
            b = self.budget()
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                b.call(options={"time_limit": limit})
            b.original.assert_not_called()
            self.assertEqual((b.calls, b.precall_aborted), (1, 1))

    def test_solver_exception_charged_and_closed(self):
        b = self.budget()
        b.original.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            b.call()
        self.assertEqual((b.calls, b.invocation_attempts, b.precall_aborted), (1, 1, 0))
        self.assertEqual(b.journal.rows[-1]["event"], "LP_ERROR")

    def test_model_limit_has_no_unrecorded_increment(self):
        b = self.budget()
        b.config["max_models"] = 1
        b.begin_model("one")
        with self.assertRaises(p.BudgetStop):
            b.begin_model("two")
        self.assertEqual(b.models, 1)

    def test_guard_restores_solver_and_prior_trace(self):
        b = self.budget()
        original, previous = p.core.linprog, sys.gettrace()
        with self.assertRaises(ValueError):
            with b.guard():
                self.assertNotEqual(p.core.linprog, original)
                raise ValueError("synthetic")
        self.assertIs(p.core.linprog, original)
        self.assertIs(sys.gettrace(), previous)

    def test_budget_exception_not_swallowed_by_frozen_solver(self):
        b = self.budget(calls=1)
        b.calls = 1
        model, _ = example()
        with b.guard(), self.assertRaises(p.BudgetStop):
            p.core.solve_float(model, [1, 0])

    def test_exact_python_work_is_time_guarded(self):
        b = self.budget()
        b.scientific_active = True
        self.clock.t = 21
        with b.guard(), self.assertRaises(p.BudgetStop):
            p.core.encode_q([Q(1, 2)] * 100)

    def test_bookkeeping_after_expiry_is_not_time_interrupted(self):
        b = self.budget()
        self.clock.t = 21
        with b.guard():
            self.assertEqual(len(p.core.encode_q([Q(1, 2)] * 100)), 100)

    def test_real_synthetic_helper_calls_all_charged(self):
        b = self.budget(calls=20)
        model = p.core.make_model([[1], [-1]], [0, -1], names=["a"])
        with b.guard():
            result = p.core.feasibility(model)
        self.assertEqual(result["status"], "EXACT_INFEASIBLE")
        self.assertEqual(b.calls, 2)  # Initial infeasibility plus phase-I helper.
        self.assertEqual([r["event"] for r in b.journal.rows], ["LP_BEGIN", "LP_END"] * 2)


class MarginTests(unittest.TestCase):
    def test_fallback_preserves_original_objective_failure(self):
        model, result = example()
        before = copy.deepcopy(result)
        desc, fallback, attempted, _ = p.complete_margin(model, result)
        self.assertEqual(result, before)
        self.assertEqual((desc["unique"], desc["margin_route"], attempted), (["a"], "FARKAS", "DERIVED"))
        self.assertTrue(fallback["all_margins_above_delta"])

    def test_equality_and_insufficient_fallback_retained_as_hold(self):
        for mass, relation in ((10_000_000, "EQUAL"), (20_000_000, "BELOW")):
            desc, fallback, attempted, _ = p.complete_margin(*example(mass))
            self.assertEqual((desc["unique"], attempted), ([], "DERIVED"))
            self.assertEqual(fallback["bounds"][0]["threshold_relation"], relation)

    def test_original_objective_success_no_redundant_fallback(self):
        model, result = example()
        result["verified_unique_leaders_above_margin_threshold"] = ["a"]
        with patch.object(p.farkas, "component_margins", side_effect=AssertionError("no fallback")):
            desc, fallback, attempted, _ = p.complete_margin(model, result)
        self.assertEqual((desc["margin_route"], fallback, attempted), ("OBJECTIVE", None, "NOT_ATTEMPTED"))

    def test_missing_exclusion_does_not_attempt_fallback(self):
        model, result = example()
        result["co_leaders"].pop("b")
        with patch.object(p.farkas, "component_margins", side_effect=AssertionError("no fallback")):
            self.assertIsNone(p.complete_margin(model, result)[1])

    def test_invalid_exact_premise_raises_not_promotes(self):
        model, result = example()
        result["co_leaders"]["b"]["farkas"]["y"] = [-1, 1, 1]
        with self.assertRaises(ValueError):
            p.complete_margin(model, result)

    def test_description_preserves_model_traversal_order(self):
        model, _ = example()
        result = plain_result(("b", "a"))
        self.assertEqual(p.complete_margin(model, result)[0]["possible"], ["b", "a"])


class WorkflowTests(unittest.TestCase):
    def execute(self, inspector, sample_count=2, tuple_count=3, **budget_kwargs):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "synthetic"
        self.manifest, self.model = fixture(self.output, sample_count, tuple_count)
        self.budget = p.Budget(p.budget_config(**budget_kwargs))
        with patch.object(p, "tuple_model", return_value=self.model):
            answer = p.execute(self.output, self.manifest, p.digest(p.data(self.manifest)), list(range(sample_count)), {},
                               self.budget, inspector=inspector)
        self.index = json.loads((self.output / "index.json").read_bytes())
        self.events = [json.loads(x) for x in (self.output / "events.jsonl").read_text().splitlines()]
        return answer

    def test_central_pass_before_remaining_and_early_two_witness_stop(self):
        answers = iter([plain_result(("a",)), plain_result(("a", "b")), plain_result(("b",))])
        answer = self.execute(lambda m, prior: next(answers))
        begins = [e["model_key"] for e in self.events if e["event"] == "MODEL_BEGIN"]
        self.assertEqual(begins, ["s00_t000", "s01_t000", "s00_t001"])
        self.assertEqual(answer["run_status"], "COMPLETE")
        self.assertEqual([s["unvisited_tuple_indices"] for s in self.index["samples"]], [[2], [1, 2]])
        second = json.loads((self.output / "cases/m_00_001.json").read_bytes())
        self.assertEqual(second["prior_possible"], ["a"])

    def test_positive_requires_all_components_and_same_leader(self):
        self.execute(lambda m, prior: copy.deepcopy(example()[1]))
        self.assertEqual(self.budget.models, 6)
        self.assertTrue(all(s["conclusion"]["status"] == "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN"
                            for s in self.index["samples"]))

    def test_all_empty_is_not_leadership(self):
        self.execute(lambda m, prior: plain_result(status="EXACT_INFEASIBLE"))
        self.assertEqual(self.index["samples"][0]["conclusion"]["status"], "EXACT_EMPTY_UNION")

    def test_complete_unresolved_remains_hold(self):
        answer = self.execute(lambda m, prior: plain_result(status="NUMERICALLY_UNRESOLVED"))
        self.assertEqual(answer["run_status"], "COMPLETE_WITH_HOLDS")
        self.assertTrue(all(s["conclusion"]["status"].startswith("HOLD_") for s in self.index["samples"]))

    def test_model_exhaustion_preserves_all_sample_denominators(self):
        answer = self.execute(lambda m, prior: plain_result(("a",)), models=1)
        self.assertEqual(answer["run_status"], "STOPPED_BUDGET")
        self.assertEqual([len(s["visits"]) for s in self.index["samples"]], [1, 0])
        self.assertEqual(self.index["samples"][1]["unvisited_tuple_indices"], [0, 1, 2])

    def test_lp_exhaustion_mid_model_preserves_charge_and_unresolved_case(self):
        def inspector(model, prior):
            p.core.linprog([1], bounds=[(0, 1)], method="highs")
            p.core.linprog([1], bounds=[(0, 1)], method="highs")
        answer = self.execute(inspector, calls=1)
        self.assertEqual((answer["run_status"], self.budget.calls), ("STOPPED_BUDGET", 1))
        visit = self.index["samples"][0]["visits"][0]
        self.assertEqual(visit["completion"], "STOPPED")
        case = json.loads((self.output / visit["case_file"]).read_bytes())
        self.assertIsNone(case["result"])
        self.assertEqual(case["description"]["possible"], [])

    def test_keyboard_interrupt_records_without_resume(self):
        answer = self.execute(Mock(side_effect=KeyboardInterrupt()))
        self.assertEqual(answer["run_status"], "STOPPED_INTERRUPT")
        self.assertEqual(self.index["samples"][0]["visits"][0]["completion"], "STOPPED")
        self.assertTrue((self.output / "output_manifest.json").is_file())

    def test_invalid_fallback_records_error_not_completed_proof(self):
        result = example()[1]
        result["co_leaders"]["b"]["farkas"]["y"] = [0, 0, 0]
        answer = self.execute(lambda m, prior: result)
        self.assertEqual(answer["run_status"], "STOPPED_ERROR")
        self.assertEqual(self.index["samples"][0]["visits"][0]["description"]["unique"], [])

    def test_case_write_error_closes_model_and_is_never_a_proof(self):
        real = p.exclusive_json
        def fail_case(path, value):
            if Path(path).parent.name == "cases":
                raise OSError("synthetic write failure")
            return real(path, value)
        with patch.object(p, "exclusive_json", side_effect=fail_case):
            answer = self.execute(lambda m, prior: plain_result(("a", "b")))
        self.assertEqual(answer["run_status"], "STOPPED_ERROR")
        visit = self.index["samples"][0]["visits"][0]
        self.assertFalse(visit["case_write_complete"])
        self.assertIsNone(visit["case_sha256"])
        self.assertIsNone(self.events[-1]["model_key"])
        self.assertEqual(visit["description"]["possible"], [])

    def test_terminal_manifest_hashes_every_file_and_is_exclusive(self):
        self.execute(lambda m, prior: plain_result(("a", "b")))
        terminal = json.loads((self.output / "output_manifest.json").read_bytes())
        for entry in terminal["files"]:
            path = self.output / entry["path"]
            self.assertEqual((path.stat().st_size, p.file_sha(path)), (entry["bytes"], entry["sha256"]))
        with self.assertRaises(FileExistsError):
            p.seal(self.output, self.manifest, "0" * 64, "COMPLETE", self.budget)

    def test_actual_synthetic_writer_passes_independent_event_inventory_and_proof_primitives(self):
        # Only this test imports both sides; the independent verifier never
        # imports the producer. This is a two-source toy LP, not native data.
        import verify_cold_interval_union as independent
        self.execute(p.legacy_union.inspect_model, sample_count=1, tuple_count=1)
        terminal = json.loads((self.output / "output_manifest.json").read_bytes())
        independent.verify_inventory(self.output, terminal)
        replay = independent.verify_events((self.output / "events.jsonl").read_bytes(), self.budget.config)
        self.assertEqual((replay["models_started"], replay["lp_calls"]), (self.budget.models, self.budget.calls))
        counts = Counter()
        for sample in self.index["samples"]:
            prior = set()
            for visit in sample["visits"]:
                case = json.loads((self.output / visit["case_file"]).read_bytes())
                self.assertEqual(case["model"], json.loads(p.data(self.model)))
                desc, calls = independent.inspect_complete(self.model, case["result"], sorted(prior),
                    case["farkas_completion"], case["farkas_attempt"], counts)
                self.assertEqual(desc, visit["description"])
                self.assertEqual(calls, case["calls_after"] - case["calls_before"])
                self.assertEqual(calls, replay["model_spans"][case["model_key"]]["calls_after"]
                                 - replay["model_spans"][case["model_key"]]["calls_before"])
                prior.update(desc["possible"])

    def test_duplicate_nonprefix_excess_visits_rejected(self):
        for indices in ([1], [0, 0], [0, 2], [0, 1, 2, 3]):
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                p.sample_summary(0, [{"tuple_index": j, "description": p.unresolved_description()} for j in indices], 3)


class StorageAndInputTests(unittest.TestCase):
    def test_invalid_prepare_budget_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "never_created"
            config = p.budget_config()
            config["max_models"] = 9999
            with self.assertRaises(ValueError):
                p.prepare("unused", target, config)
            self.assertFalse(target.exists())

    def test_exclusive_write_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "one.json"
            p.exclusive_json(path, {"n": Q(1, 3)})
            prior = path.read_bytes()
            with self.assertRaises(FileExistsError):
                p.exclusive_json(path, {"n": 5})
            self.assertEqual(path.read_bytes(), prior)

    def test_canonical_fraction_and_nonfinite_rejection(self):
        self.assertEqual(p.data({"b": Q(1, 2), "a": 1}), b'{\n  "a": 1,\n  "b": "1/2"\n}\n')
        with self.assertRaises(ValueError):
            p.data({"value": float("nan")})

    def test_output_scope_names_overlap_existing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / "inputs"
            good = root / "private" / "cold_test"
            self.assertEqual(p.output_path(good, inputs, root), good.resolve())
            for path in (root, root / "outside", root / "private" / "nested" / "a", root / "private" / "CON",
                         root / "private" / "bad.name", root / "private" / ("x" * 42)):
                with self.subTest(path=path.name), self.assertRaises(ValueError):
                    p.output_path(path, inputs, root)
            with self.assertRaises(ValueError):
                p.output_path(good, good / "input", root)
            good.mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                p.output_path(good, inputs, root)

    def test_link_or_junction_at_output_or_any_ancestor_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            target = root / "private" / "fresh"
            for method in ("is_symlink", "is_junction"):
                for linked in (target, target.parent, root):
                    def is_link(path, linked=linked):
                        return path == linked
                    with self.subTest(method=method, ancestor=linked.name), \
                            patch.object(Path, method, is_link), \
                            self.assertRaisesRegex(ValueError, "symlinked"):
                        p.output_path(target, root / "inputs", root)

    def test_journal_exclusive_and_consecutive_durable_events(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            b = p.Budget(p.budget_config())
            j = p.Journal(path)
            try:
                self.assertEqual(j.event("RUN_START", b), 0)
                self.assertEqual(j.event("RUN_END", b), 1)
                with self.assertRaises(FileExistsError):
                    p.Journal(path)
            finally:
                j.close()
            self.assertEqual([json.loads(row)["seq"] for row in path.read_text().splitlines()], [0, 1])

    def test_run_rejects_missing_approval_before_dependency_or_input_access(self):
        with patch.object(p, "output_path", return_value=Path("irrelevant")), \
                patch.object(p, "metadata", side_effect=AssertionError("must not access")):
            with self.assertRaisesRegex(ValueError, "approved manifest"):
                p.run("unused", "unused", None)

    def test_run_refuses_populated_snapshot_without_reusing_old_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "cases").mkdir()
            p.exclusive_json(output / "manifest.json", {})
            p.exclusive_json(output / "preflight.json", {})
            p.exclusive_json(output / "run_started.json", {})
            with patch.object(p, "output_path", return_value=output), self.assertRaises(FileExistsError):
                p.run("unused", output, "0" * 64)

    def test_wrong_approval_rejected_before_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "cases").mkdir()
            p.exclusive_json(output / "manifest.json", {})
            p.exclusive_json(output / "preflight.json", {})
            with patch.object(p, "output_path", return_value=output), \
                    patch.object(p, "metadata", side_effect=AssertionError("must not access")), \
                    self.assertRaisesRegex(ValueError, "approval does not match"):
                p.run("unused", output, "0" * 64)

    def test_dependency_or_environment_drift_rejected_before_inputs(self):
        for kind in ("dependencies", "environment"):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                output = root / "private" / "prepared"
                output.mkdir(parents=True)
                (output / "cases").mkdir()
                manifest = {"schema": p.SCHEMA, "dependencies": {"synthetic": "same"},
                            "environment": p.environment(), "output_relative": "private/prepared"}
                manifest[kind] = {"changed": "must reject"}
                mh = p.exclusive_json(output / "manifest.json", manifest)
                p.exclusive_json(output / "preflight.json", {})
                with patch.object(p, "ROOT", root), \
                        patch.object(p, "dependencies", return_value={"synthetic": "same"}), \
                        patch.object(p, "metadata", side_effect=AssertionError("must not access")), \
                        self.assertRaisesRegex(ValueError, "identity drift"):
                    p.run(root / "inputs", output, mh)

    def test_no_historical_runner_or_pointfit_call(self):
        tree = ast.parse(Path(p.__file__).read_text(encoding="utf-8"))
        forbidden = {"fit", "fit_evls", "inputs_and_candidates", "stage1", "stage2", "freeze"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden)
        text = Path(p.__file__).read_text(encoding="utf-8")
        self.assertNotIn("central_retained_bridge", text)
        self.assertNotIn("34/1", text)


class MetadataOnlyTests(unittest.TestCase):
    def fake_inputs(self):
        families = json.loads((p.ROOT / p.PUBLIC / "joint_profile_configuration.json").read_bytes())["families"]
        species = p.native.CONFIG["species"]
        receptors = []
        for i in range(35):
            rec = {"ID": f"synthetic{i}", "DATE": "synthetic", "DUR": "24", "STHOUR": "0", "SIZE": "FINE", "TMAC": "10"}
            for name in species:
                rec[name], rec[name[:-1] + "U"] = "1", "0.1"
            receptors.append(rec)
        profiles = {}
        for sid in {sid for slot in p.SLOTS for sid in families.get(slot, [slot])}:
            rec = {"SID": sid, "SIZE": "FINE"}
            for name in species:
                rec[name], rec[name[:-1] + "U"] = "0.2", "0.01"
            profiles[sid] = rec
        summary = {"species": species, "alternatives": {k: v[1:] for k, v in families.items()}}
        return receptors, profiles, summary

    def invoke(self, inputs):
        with patch.object(p.native, "archive_inventory", return_value={"synthetic": True}), \
                patch.object(p.native, "verify_recovery_identities", return_value={"archives_checked": 4, "members_checked": 39}), \
                patch.object(p.native, "load_inputs", return_value=inputs), \
                patch.object(p.core, "linprog", side_effect=AssertionError("metadata must never solve")):
            return p.metadata("unused")

    def test_full_synthetic_metadata_universe_no_lp(self):
        frozen, _, _ = self.invoke(self.fake_inputs())
        self.assertEqual((len(frozen["samples"]), len(frozen["tuples"]), len(frozen["models"])), (35, 120, 4200))
        self.assertEqual(len({x["case_file"] for x in frozen["models"]}), 4200)
        self.assertEqual(frozen["tuples"][0], list(p.SLOTS))
        self.assertEqual(frozen["metadata_digests"]["ordered_model_sha256"],
                         p.digest(p.data([x["model_sha256"] for x in frozen["models"]])))
        self.assertEqual(frozen["inputs"]["validated_receptor_species_pairs"], 700)

    def test_duplicate_receptor_identity_rejected(self):
        receptors, profiles, summary = self.fake_inputs()
        receptors[1] = copy.deepcopy(receptors[0])
        with self.assertRaisesRegex(ValueError, "35 distinct"):
            self.invoke((receptors, profiles, summary))

    def test_descriptor_order_drift_rejected(self):
        receptors, profiles, summary = self.fake_inputs()
        summary["alternatives"]["SOIL03"].reverse()
        with self.assertRaisesRegex(ValueError, "descriptor family order"):
            self.invoke((receptors, profiles, summary))

    def test_invalid_profile_and_receptor_fields_rejected_before_hashing(self):
        for category, value in (("receptor_uncertainty", "0"), ("receptor_uncertainty", "-1"),
                                ("receptor_mean", "-99"), ("receptor_mean", "NaN"),
                                ("profile_uncertainty", "-1"), ("profile_mean", "Infinity"),
                                ("profile_mean", "-99")):
            receptors, profiles, summary = self.fake_inputs()
            name = summary["species"][0]
            row = receptors[0] if category.startswith("receptor") else profiles[p.SLOTS[0]]
            row[name[:-1] + "U" if category.endswith("uncertainty") else name] = value
            with self.subTest(category=category, value=value), \
                    patch.object(p, "tuple_model", side_effect=AssertionError("invalid input must not reach models")), \
                    self.assertRaises(ValueError):
                self.invoke((receptors, profiles, summary))

    def test_alternative_uses_own_uncertainty_without_mutating_profile(self):
        receptors, profiles, _ = self.fake_inputs()
        species = p.native.CONFIG["species"][0]
        profiles["SOIL08"][species] = "0.4"
        profiles["SOIL08"][species[:-1] + "U"] = "0.15"
        before = copy.deepcopy(profiles)
        model = p.tuple_model(receptors[0], profiles, ["SOIL08", *p.SLOTS[1:]])
        self.assertEqual((model["L"][0][0], model["U"][0][0]), (Q(1, 10), Q(7, 10)))
        self.assertEqual((model["names"][0], model["sources"][0]), ("soil", "SOIL08"))
        self.assertEqual(profiles, before)

    def test_incomplete_tuple_rejected(self):
        with self.assertRaises(ValueError):
            p.tuple_model({}, {}, ["SOIL03"])


class RecoveryPortabilityTests(unittest.TestCase):
    def forms(self):
        original = (p.ROOT / p.RECOVERY_RELATIVE).read_bytes()
        lf = original.replace(b"\r\n", b"\n")
        crlf = lf.replace(b"\n", b"\r\n")
        return crlf, lf

    def test_exact_two_diagnosed_forms_and_equal_json(self):
        crlf, lf = self.forms()
        self.assertEqual((len(crlf), len(lf), crlf.count(b"\r\n"), lf.count(b"\r\n")), (9074, 8817, 257, 0))
        self.assertEqual([p.digest(crlf), p.digest(lf)], p.APPROVED_DEPENDENCY_BYTE_VARIANTS[p.RECOVERY_RELATIVE])
        self.assertEqual(json.loads(crlf), json.loads(lf))
        self.assertEqual(crlf.replace(b"\r\n", b"\n"), lf)

    def test_both_forms_are_consumed_without_rewriting_bytes(self):
        for payload in self.forms():
            path = Mock()
            path.read_bytes.return_value = payload
            self.assertIs(p.checked_recovery_bytes(path), payload)
            path.read_bytes.assert_called_once_with()

    def test_semantically_equal_third_form_rejected(self):
        _, lf = self.forms()
        third = lf + b"\n"
        self.assertEqual(json.loads(third), json.loads(lf))
        with self.assertRaisesRegex(ValueError, "unapproved recovery"):
            p.checked_recovery_bytes(Mock(read_bytes=Mock(return_value=third)))

    def test_changed_member_identity_rejected_before_native_parser(self):
        _, lf = self.forms()
        changed = lf.replace(b"3ca5bb3d", b"3ca5bb3e", 1)
        self.assertNotEqual(changed, lf)
        with patch.object(p.native, "verify_recovery_identities", side_effect=AssertionError("must not parse")), \
                self.assertRaisesRegex(ValueError, "unapproved recovery"):
            p.recovery_identities([], Mock(read_bytes=Mock(return_value=changed)))

    def test_frozen_native_parser_gets_checked_buffer_not_unchecked_reopen(self):
        for payload in self.forms():
            source = Mock()
            source.read_bytes.side_effect = [payload, b"unchecked changed bytes"]
            records = json.loads(payload)["records"]
            inventory = [{"archive": r["name"], "sha256": r["sha256"], "bytes": r["bytes"],
                          "members": r["members"]} for r in records]
            result = p.recovery_identities(inventory, source)
            self.assertEqual(result["recovery_record_sha256"], p.digest(payload))
            self.assertEqual((result["archives_checked"], result["members_checked"]), (4, 39))
            source.read_bytes.assert_called_once_with()

    def test_dependency_map_records_actual_form_and_nineteen_files(self):
        for payload in self.forms():
            def other_hash(path):
                return p.PINNED.get(path.relative_to(p.ROOT).as_posix(), "a" * 64)
            with patch.object(Path, "read_bytes", return_value=payload), patch.object(p, "file_sha", side_effect=other_hash):
                deps = p.dependencies()
            self.assertEqual(deps[p.RECOVERY_RELATIVE], p.digest(payload))
            self.assertEqual(len(deps), 19)
            self.assertIn("outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md", deps)

    def test_unrelated_dependency_remains_exact_byte_pinned(self):
        payload = self.forms()[0]
        def changed_hash(path):
            relative = path.relative_to(p.ROOT).as_posix()
            return "0" * 64 if relative == "scripts/audit_interval_decisions.py" else p.PINNED.get(relative, "a" * 64)
        with patch.object(Path, "read_bytes", return_value=payload), patch.object(p, "file_sha", side_effect=changed_hash), \
                self.assertRaisesRegex(ValueError, "frozen public dependency changed"):
            p.dependencies()

    def test_manifest_claiming_other_approved_form_is_still_rejected(self):
        crlf, lf = self.forms()
        for claimed, actual in ((crlf, lf), (lf, crlf)):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                output = root / "private" / "prepared"
                output.mkdir(parents=True)
                (output / "cases").mkdir()
                manifest = {"schema": p.SCHEMA, "dependencies": {p.RECOVERY_RELATIVE: p.digest(claimed)},
                            "environment": p.environment(), "output_relative": "private/prepared"}
                mh = p.exclusive_json(output / "manifest.json", manifest)
                p.exclusive_json(output / "preflight.json", {})
                with patch.object(p, "ROOT", root), \
                        patch.object(p, "dependencies", return_value={p.RECOVERY_RELATIVE: p.digest(actual)}), \
                        patch.object(p, "metadata", side_effect=AssertionError("must stop before metadata")), \
                        self.assertRaisesRegex(ValueError, "identity drift"):
                    p.run(root / "inputs", output, mh)

    def test_prepare_rejects_variant_switch_before_creating_output(self):
        first, second = p.APPROVED_DEPENDENCY_BYTE_VARIANTS[p.RECOVERY_RELATIVE]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "private" / "fresh"
            frozen = {"inputs": {"recovery_verification": {"recovery_record_sha256": second}}}
            with patch.object(p, "ROOT", root), \
                    patch.object(p, "dependencies", return_value={p.RECOVERY_RELATIVE: first}), \
                    patch.object(p, "metadata", return_value=(frozen, [], {})), \
                    self.assertRaisesRegex(ValueError, "between dependency and metadata"):
                p.prepare(root / "inputs", output, p.budget_config())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
