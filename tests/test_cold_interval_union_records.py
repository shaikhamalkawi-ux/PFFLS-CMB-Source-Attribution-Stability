"""Synthetic independent cold-union validation tests. No native data or LPs."""
import ast
from collections import Counter
import copy
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_cold_interval_union as audit


def native_fixture():
    species = audit.v.SPECIES
    fields = [item for s in species for item in (s, s[:-1] + "U")]
    header = ["ID", "DATE", "DUR", "STHOUR", "SIZE", "TMAC"] + fields
    receptors = [" ".join(header)]
    for i in range(35):
        receptors.append(" ".join(["FRESNO", str(20000101 + i), "24", "0", "FINE", "10"]
                                  + [value for _ in species for value in ("1", "0.1")]))
    profiles = [" ".join(["SID", "SIZE"] + fields)]
    selector = []
    all_sources = list(dict.fromkeys(s for tup in audit.profile_grid() for s in tup))
    for i, sid in enumerate(all_sources):
        profiles.append(" ".join([sid, "FINE"] + [value for _ in species for value in ("0.1", "0.01")]))
        prefix = list(" " * 36)
        prefix[:2] = list(f"{i:02d}")
        prefix[3:3 + len(sid)] = list(sid)
        if sid in audit.v.SOURCES:
            prefix[22] = "*"
        desc = ("PAVED ROAD" if sid.startswith("SOIL") else
                "CORDWOOD" if sid in audit.FAMILIES["BAMAJC"] else
                "CRUDE BOILER" if sid in audit.FAMILIES["SFCRUC"] else "OTHER")
        selector.append("".join(prefix) + desc)
    species_selector = []
    for name in species:
        row = list(" " * 26)
        row[:len(name)] = list(name)
        row[20] = row[24] = "*"
        species_selector.append("".join(row))
    return {"ADsjvf.txt": ("\n".join(receptors) + "\n").encode("ascii"),
            "PRsjvf.txt": ("\n".join(profiles) + "\n").encode("ascii"),
            "PRsjvf.sel": ("\n".join(selector) + "\n").encode("ascii"),
            "SPsjvf.sel": ("\n".join(species_selector) + "\n").encode("ascii")}


class IndependentInputs(unittest.TestCase):
    def test_exact_grid_and_native_identity(self):
        receptors, profiles = audit.parse_native(native_fixture())
        self.assertEqual(len(receptors), 35)
        grid = audit.profile_grid()
        self.assertEqual(len(grid), 120)
        self.assertEqual(grid[0], audit.v.SOURCES)
        self.assertEqual(receptors[0]["DATE"], "20000101")
        self.assertEqual(receptors[-1]["DATE"], "20000135")
        self.assertIn("MOVES5", profiles)

    def test_duplicate_receptor_fails(self):
        raw = native_fixture()
        lines = raw["ADsjvf.txt"].splitlines()
        lines[-1] = lines[-2]
        raw["ADsjvf.txt"] = b"\n".join(lines)
        with self.assertRaises(audit.v.VerificationError):
            audit.parse_native(raw)

    def test_missing_receptor_fails(self):
        raw = native_fixture()
        raw["ADsjvf.txt"] = b"\n".join(raw["ADsjvf.txt"].splitlines()[:-1])
        with self.assertRaises(audit.v.VerificationError):
            audit.parse_native(raw)

    def test_selector_and_descriptor_drift_fail(self):
        for name, before, after in (("SPsjvf.sel", b"N3IC", b"N0IC"),
                                    ("PRsjvf.sel", b"PAVED ROAD", b"UNPAVED RD")):
            with self.subTest(name=name):
                raw = native_fixture()
                raw[name] = raw[name].replace(before, after)
                with self.assertRaises(audit.v.VerificationError):
                    audit.parse_native(raw)

    def test_duplicate_profile_fails(self):
        raw = native_fixture()
        raw["PRsjvf.txt"] += raw["PRsjvf.txt"].splitlines()[1] + b"\n"
        with self.assertRaises(audit.v.VerificationError):
            audit.parse_native(raw)

    def test_invalid_receptor_or_profile_uncertainty_fails(self):
        for name, before, after in (("ADsjvf.txt", b"1 0.1", b"1 0"),
                                    ("PRsjvf.txt", b"0.1 0.01", b"0.1 -0.01"),
                                    ("PRsjvf.txt", b"0.1 0.01", b"-99 0.01")):
            with self.subTest(name=name, after=after):
                raw = native_fixture()
                raw[name] = raw[name].replace(before, after, 1)
                with self.assertRaises(audit.v.VerificationError):
                    audit.parse_native(raw)

    def test_alternative_carries_own_uncertainty_and_family(self):
        receptors, profiles = audit.parse_native(native_fixture())
        profiles["MOVES1"]["N3IC"] = "0.123456789"
        profiles["MOVES1"]["N3IU"] = "0.0123456789"
        chosen = list(audit.v.SOURCES)
        chosen[3] = "MOVES1"
        model = audit.tuple_model(receptors[0], profiles, chosen)
        self.assertEqual(model["U"][0][3], Q("0.1481481468"))
        self.assertEqual(model["L"][0][3], Q("0.0987654312"))
        self.assertEqual(model["names"][3], "vehicle")
        self.assertEqual(model["sources"], chosen)
        self.assertEqual((model["k"], model["mass_mode"], model["profile_mode"]), (2, "none", "joint_intervals"))

    def test_profile_record_cannot_masquerade_as_alternative(self):
        receptors, profiles = audit.parse_native(native_fixture())
        chosen = list(audit.v.SOURCES); chosen[3] = "MOVES1"
        profiles["MOVES1"] = profiles["MOVES2"]
        with self.assertRaises(audit.v.VerificationError):
            audit.tuple_model(receptors[0], profiles, chosen)

    def test_unapproved_or_incomplete_tuple_fails(self):
        receptors, profiles = audit.parse_native(native_fixture())
        for chosen in (audit.v.SOURCES[:-1], list(reversed(audit.v.SOURCES))):
            with self.assertRaises(audit.v.VerificationError):
                audit.tuple_model(receptors[0], profiles, chosen)

    def test_archive_hash_and_member_inventory(self):
        stream = BytesIO()
        with ZipFile(stream, "w") as archive:
            archive.writestr("x", b"exact bytes")
        recorded = [{"name": "x", "bytes": 11, "sha256": audit.v.digest(b"exact bytes")}]
        self.assertEqual(audit.archive_bytes(stream.getvalue(), recorded), {"x": b"exact bytes"})
        recorded[0]["sha256"] = "0" * 64
        with self.assertRaises(audit.v.VerificationError):
            audit.archive_bytes(stream.getvalue(), recorded)

    def test_duplicate_zip_members_fail(self):
        import warnings
        stream = BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with ZipFile(stream, "w") as archive:
                archive.writestr("x", b"a"); archive.writestr("x", b"b")
        with self.assertRaises(audit.v.VerificationError):
            audit.archive_bytes(stream.getvalue(), [])

    def test_json_duplicate_nonfinite_rejected(self):
        for payload in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e309}'):
            with self.assertRaises(audit.v.VerificationError):
                audit.json_load(payload)

    def test_no_generating_or_numerical_imports_and_no_assert_guards(self):
        tree = ast.parse(Path(audit.__file__).read_text(encoding="utf-8"))
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(tree)))
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else ([node.module] if isinstance(node, ast.ImportFrom) else [])
            self.assertFalse(any(n.startswith(("reproduce_", "audit_", "numpy", "scipy")) for n in names))

    def test_full_input_reader_never_reads_historical_private(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / "inputs"; inputs.mkdir()
            public = root / "outputs/decision_research_20260926"; public.mkdir(parents=True)
            recovery = root / "outputs/strengthening_20260926/source_recovery.json"
            recovery.parent.mkdir()
            hashes, records = {}, []
            names = list(audit.v.ARCHIVE_HASHES)
            collections = [native_fixture(), {"a": b"a"}, {"b": b"b"},
                           {f"x{i}": b"x" for i in range(33)}]
            for name, members in zip(names, collections):
                stream = BytesIO()
                with ZipFile(stream, "w") as archive:
                    for member, payload in members.items():
                        archive.writestr(member, payload)
                payload = stream.getvalue(); (inputs / name).write_bytes(payload)
                hashes[name] = audit.v.digest(payload)
                records.append({"name": name, "sha256": hashes[name], "bytes": len(payload),
                                "members": [{"name": m, "bytes": len(b), "sha256": audit.v.digest(b)}
                                            for m, b in members.items()]})
            recovery.write_bytes(audit.canonical({"records": records}))
            grid = audit.canonical({"families": audit.FAMILIES, "labels": audit.v.LABELS})
            (public / "joint_profile_configuration.json").write_bytes(grid)
            original = Path.read_bytes
            reads = []
            def guarded(path):
                self.assertNotIn("private", path.parts)
                reads.append(path)
                return original(path)
            pins = {"outputs/strengthening_20260926/source_recovery.json": audit.v.digest(recovery.read_bytes())}
            with patch.object(audit, "FROZEN_VERIFIERS", {}), patch.object(audit.v, "DEPENDENCIES", pins), \
                 patch.object(audit, "RECOVERY_HASHES", set(pins.values())), \
                 patch.object(audit.v, "ARCHIVE_HASHES", hashes), patch.object(audit, "GRID_HASH", audit.v.digest(grid)), \
                 patch.object(Path, "read_bytes", guarded):
                receptors, profiles = audit.load_original_inputs(inputs, root)
            self.assertEqual(len(receptors), 35)
            self.assertTrue(reads)
            self.assertFalse((root / "private").exists())


def journal_fixture():
    specs = [("RUN_START", None, 0, 0, {}),
             ("MODEL_BEGIN", "s00_t000", 1, 0, {"admission_gate_elapsed_seconds": 0.05,
                "admission_gate_utc": "2026-09-27T00:00:00.5+00:00"}),
             ("LP_BEGIN", "s00_t000", 1, 1, {"call_id": 1, "method": "highs-ds", "remaining_seconds": 99,
                "admission_gate_elapsed_seconds": 0.15, "admission_gate_utc": "2026-09-27T00:00:01.5+00:00"}),
             ("LP_END", "s00_t000", 1, 1, {"call_id": 1, "solver_status": 0, "invocation_attempted": True,
                "dispatch_gate_elapsed_seconds": 0.25, "dispatch_remaining_seconds": 98.9,
                "dispatch_gate_utc": "2026-09-27T00:00:02.5+00:00", "solver_time_limit_seconds": 98.9}),
             ("MODEL_END", "s00_t000", 1, 1, {"completion": "COMPLETE"}),
             ("RUN_END", None, 1, 1, {"run_status": "COMPLETE"})]
    return [{"seq": i, "event": kind, "model_key": key, "models_started": models, "lp_calls": calls,
             "utc": f"2026-09-27T00:00:0{i}+00:00", "elapsed_seconds": i / 10, **extra}
            for i, (kind, key, models, calls, extra) in enumerate(specs)]


class ExactMetadataPortability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_pins = dict(audit.v.DEPENDENCIES)
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        required = set(audit.v.DEPENDENCIES) | {"scripts/" + p for p in audit.FROZEN_VERIFIERS}
        required.update(("scripts/audit_interval_profile_union.py", "scripts/audit_interval_farkas_margin.py",
            "scripts/reproduce_interval_union.py", "scripts/verify_cold_interval_union.py",
            "tests/test_cold_interval_union.py", "tests/test_cold_interval_union_records.py",
            "outputs/decision_research_20260926/joint_profile_configuration.json",
            "outputs/decision_research_20260926/COLD_RUN_REPRODUCTION_PROPOSAL.md",
            "outputs/decision_research_20260926/COLD_RUN_ROOT_DECISION.md",
            "outputs/decision_research_20260926/COLD_RUN_RECORD_SCHEMA.md",
            "outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md"))
        cls.dependencies = {}
        for relative in required:
            payload = (audit.ROOT / relative).read_bytes()
            destination = cls.root / relative; destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            cls.dependencies[relative] = audit.v.digest(payload)
        payload = (cls.root / audit.RECOVERY_RELATIVE).read_bytes()
        cls.lf = payload.replace(b"\r\n", b"\n")
        cls.crlf = cls.lf.replace(b"\n", b"\r\n")
        if {audit.v.digest(cls.lf), audit.v.digest(cls.crlf)} != audit.RECOVERY_HASHES:
            raise AssertionError("reviewed two-form recovery fixture identity changed")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.path = self.root / audit.RECOVERY_RELATIVE
        self.path.write_bytes(self.crlf)
        self.manifest = {"dependencies": dict(self.dependencies),
            "inputs": {"recovery_verification": {"recovery_record_sha256": audit.v.digest(self.crlf)}},
            "approved_dependency_byte_variants": copy.deepcopy(audit.APPROVED_DEPENDENCY_BYTE_VARIANTS)}
        self.manifest["dependencies"][audit.RECOVERY_RELATIVE] = audit.v.digest(self.crlf)

    def test_both_exact_forms_accepted_and_values_identical(self):
        parsed = []
        for payload in (self.crlf, self.lf):
            self.path.write_bytes(payload)
            observed = audit.pinned_dependency_bytes(self.root, audit.RECOVERY_RELATIVE,
                audit.v.DEPENDENCIES[audit.RECOVERY_RELATIVE])
            self.assertEqual(observed, payload)
            parsed.append(audit.json_load(observed))
            self.manifest["dependencies"][audit.RECOVERY_RELATIVE] = audit.v.digest(payload)
            self.manifest["inputs"]["recovery_verification"]["recovery_record_sha256"] = audit.v.digest(payload)
            audit.verify_dependencies(self.manifest, self.root)
        self.assertEqual(parsed[0], parsed[1])

    def test_third_semantically_equal_encoding_is_rejected(self):
        third = b" " + self.lf
        self.assertEqual(audit.json_load(third), audit.json_load(self.lf))
        self.path.write_bytes(third)
        with self.assertRaises(audit.v.VerificationError):
            audit.pinned_dependency_bytes(self.root, audit.RECOVERY_RELATIVE,
                audit.v.DEPENDENCIES[audit.RECOVERY_RELATIVE])

    def test_changed_recovery_content_rejected(self):
        self.path.write_bytes(self.lf.replace(b"sjvf_data.zip", b"changed__.zip", 1))
        with self.assertRaises(audit.v.VerificationError):
            audit.pinned_dependency_bytes(self.root, audit.RECOVERY_RELATIVE,
                audit.v.DEPENDENCIES[audit.RECOVERY_RELATIVE])

    def test_manifest_cannot_name_other_allowed_form(self):
        self.path.write_bytes(self.lf)
        with self.assertRaises(audit.v.VerificationError): audit.verify_dependencies(self.manifest, self.root)

    def test_dependency_and_consumed_metadata_form_must_agree(self):
        self.manifest["inputs"]["recovery_verification"]["recovery_record_sha256"] = audit.v.digest(self.lf)
        with self.assertRaises(audit.v.VerificationError): audit.verify_dependencies(self.manifest, self.root)

    def test_unrelated_dependency_cannot_use_exception(self):
        relative = "other.json"; path = self.root / relative; path.write_bytes(self.lf)
        with self.assertRaises(audit.v.VerificationError):
            audit.pinned_dependency_bytes(self.root, relative, audit.v.digest(self.crlf))
        self.assertEqual(audit.v.DEPENDENCIES, self.original_pins)

    def test_declared_variants_cannot_broaden_scope_or_forms(self):
        for extra in ({"elsewhere.json": list(audit.RECOVERY_HASHES)},
                      {audit.RECOVERY_RELATIVE: list(audit.APPROVED_DEPENDENCY_BYTE_VARIANTS[audit.RECOVERY_RELATIVE]) + ["0" * 64]}):
            manifest = copy.deepcopy(self.manifest)
            manifest["approved_dependency_byte_variants"].update(extra)
            with self.subTest(extra=extra), self.assertRaises(audit.v.VerificationError):
                audit.verify_dependencies(manifest, self.root)


def proof_fixture(mass=1_000_000):
    model = {"n": 3, "names": ["z", "a", "m"], "mass": Q(mass), "upper_bounds": [None, Q(1), Q(2)],
             "G": [[Q(-1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)]],
             "h": [Q(-3), Q(1), Q(2)]}
    point = {"status": "EXACT_FEASIBLE", "solver_status": 0,
             "primal": {"verified": True, "point": ["3", "1", "2"]}}
    result = {"overall_status": "EXACT_COMPATIBLE", "feasibility": copy.deepcopy(point),
              "co_leaders": {"z": copy.deepcopy(point),
                             "a": {"status": "EXACT_INFEASIBLE", "solver_status": 2,
                                   "farkas": {"verified": True, "y": ["1", "2", "0", "1", "1"], "h_dot_y": "-1"}},
                             "m": {"status": "EXACT_INFEASIBLE", "solver_status": 2,
                                   "farkas": {"verified": True, "y": ["1", "0", "1", "1", "0"], "h_dot_y": "-1"}}},
              "co_leader_search_complete": True, "verified_unique_leaders_above_margin_threshold": [],
              "candidate_leader": "z", "near_zero_threshold": str(Q(mass, 10_000_000)),
              "leader_bounds": {name: {"objective": q, "status": "NUMERICALLY_UNRESOLVED", "solver_status": 4,
                                       "primal": {"verified": False}, "dual": {"verified": False}}
                                for name, q in (("a", ["1", "-1", "0"]), ("m", ["1", "0", "-1"]))}}
    completion = audit.v.encode(audit.f.derive_component(model, result, Q(mass, 10_000_000)))
    return model, result, completion


class ExactProofLayer(unittest.TestCase):
    def test_canonical_key_order_restored_not_trusted(self):
        model, result, completion = proof_fixture()
        saved = audit.json_load(audit.canonical(result))
        self.assertEqual(list(saved["co_leaders"]), ["a", "m", "z"])
        desc, calls = audit.inspect_complete(model, saved, [], completion, "DERIVED", Counter())
        self.assertEqual(desc["possible"], ["z"])
        self.assertEqual(desc["unique"], ["z"])
        self.assertEqual(desc["margin_route"], "FARKAS")
        self.assertEqual(calls, 8)
        self.assertEqual(saved["leader_bounds"]["a"]["status"], "NUMERICALLY_UNRESOLVED")

    def test_fallback_equality_is_not_margin_certificate(self):
        model, result, completion = proof_fixture(5_000_000)
        desc, _ = audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())
        self.assertEqual(desc["unique"], [])
        self.assertIsNone(desc["margin_route"])
        self.assertEqual(completion["bounds"][0]["threshold_relation"], "EQUAL")

    def test_insufficient_bound_remains_saved_hold(self):
        model, result, completion = proof_fixture(6_000_000)
        desc, _ = audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())
        self.assertEqual(desc["unique"], [])
        self.assertEqual(completion["bounds"][0]["threshold_relation"], "BELOW")

    def test_exact_derived_bound_not_merely_reported(self):
        model, result, completion = proof_fixture()
        completion["bounds"][0]["lower_margin"] = "999"
        with self.assertRaises(audit.v.VerificationError):
            audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())

    def test_missing_competitor_or_negative_multiplier_rejected(self):
        for mutation in ("missing", "negative"):
            model, result, completion = proof_fixture()
            if mutation == "missing": del result["co_leaders"]["a"]
            else: result["co_leaders"]["a"]["farkas"]["y"][0] = "-1"
            with self.subTest(mutation=mutation), self.assertRaises(audit.v.VerificationError):
                audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())

    def test_eligible_fallback_cannot_be_silently_skipped(self):
        model, result, _ = proof_fixture()
        with self.assertRaises(audit.v.VerificationError):
            audit.inspect_complete(model, result, [], None, "NOT_ATTEMPTED", Counter())

    def test_objective_failures_cannot_be_relabelled_success(self):
        model, result, completion = proof_fixture()
        result["verified_unique_leaders_above_margin_threshold"] = ["z"]
        with self.assertRaises(audit.v.VerificationError):
            audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())

    def test_unknown_or_error_attempt_not_a_complete_proof(self):
        model, result, completion = proof_fixture()
        for attempt in ("ERROR", "UNKNOWN"):
            with self.assertRaises(audit.v.VerificationError):
                audit.inspect_complete(model, result, [], completion, attempt, Counter())

    def test_inputs_not_mutated_by_replay(self):
        model, result, completion = proof_fixture()
        before = copy.deepcopy((model, result, completion))
        audit.inspect_complete(model, result, [], completion, "DERIVED", Counter())
        self.assertEqual((model, result, completion), before)


class JournalAndAccounting(unittest.TestCase):
    budgets = {"max_models": 4200, "max_lp_calls": 20000, "elapsed_seconds": 100, "deadline_utc": None}

    def replay(self, rows, budgets=None):
        payload = b"".join(json.dumps(r, sort_keys=True).encode() + b"\n" for r in rows)
        return audit.verify_events(payload, budgets or self.budgets)

    def test_exact_charge_and_model_span(self):
        result = self.replay(journal_fixture())
        self.assertEqual((result["models_started"], result["lp_calls"]), (1, 1))
        self.assertEqual(result["model_spans"]["s00_t000"],
                         {"begin": 1, "end": 4, "calls_before": 0, "calls_after": 1})

    def test_failed_or_aborted_call_keeps_charge(self):
        rows = journal_fixture(); rows[3]["event"] = "LP_ERROR"
        rows[3].update(error_category="BudgetStopBeforeInvocation", invocation_attempted=False,
                       charged_but_not_invoked=True)
        for key in ("solver_time_limit_seconds", "dispatch_gate_elapsed_seconds", "dispatch_remaining_seconds", "dispatch_gate_utc"):
            del rows[3][key]
        result = self.replay(rows)
        self.assertEqual((result["lp_calls"], result["solver_invocation_attempts"], result["precall_aborted"]), (1, 0, 1))

    def test_invoked_error_keeps_dispatch_gate_and_charge(self):
        rows = journal_fixture(); rows[3].update(event="LP_ERROR", charged_but_not_invoked=False,
                                               error_category="RuntimeError")
        result = self.replay(rows)
        self.assertEqual((result["lp_calls"], result["solver_invocation_attempts"], result["precall_aborted"]), (1, 1, 0))

    def test_stale_post_flush_allowance_rejected(self):
        for key, value in (("dispatch_gate_elapsed_seconds", 100), ("dispatch_remaining_seconds", 100),
                           ("solver_time_limit_seconds", 99.2)):
            rows = journal_fixture(); rows[3][key] = value
            with self.subTest(key=key), self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_delayed_begin_event_does_not_change_earlier_admission(self):
        rows = journal_fixture()
        rows[2].update(admission_gate_elapsed_seconds=0.11, remaining_seconds=99.89)
        self.assertEqual(self.replay(rows)["lp_calls"], 1)
        rows[2]["admission_gate_elapsed_seconds"] = 101
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_final_budget_conserves_attempts(self):
        journal = self.replay(journal_fixture())
        snapshot = {key: journal[key] for key in ("models_started", "lp_calls", "solver_invocation_attempts", "precall_aborted")}
        snapshot.update(elapsed_seconds=0.6, max_models=4200, max_lp_calls=20000, elapsed_limit_seconds=100,
                        deadline_utc=None, lp_counter_semantics="charged attempts, including explicit pre-invocation aborts")
        audit.verify_budget_snapshot(snapshot, self.budgets, journal, 0.5)
        for key, value in (("precall_aborted", 1), ("max_models", 4201), ("elapsed_seconds", 0.4),
                           ("lp_counter_semantics", "solver calls")):
            bad = {**snapshot, key: value}
            with self.subTest(key=key), self.assertRaises(audit.v.VerificationError):
                audit.verify_budget_snapshot(bad, self.budgets, journal, 0.5)

    def test_no_lp_outside_model(self):
        rows = journal_fixture(); rows[2]["model_key"] = "another"
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_missing_charge_and_false_counters_fail(self):
        for key, value in (("lp_calls", 0), ("call_id", 2), ("models_started", 0), ("seq", 99)):
            rows = journal_fixture(); rows[2][key] = value
            with self.subTest(key=key), self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_counter_bools_rejected(self):
        rows = journal_fixture(); rows[2]["lp_calls"] = True
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_wrong_return_identity_fails(self):
        rows = journal_fixture(); rows[3]["call_id"] = 2
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_time_and_remaining_budget_fail_closed(self):
        for elapsed, remaining in ((100, 1), (0.2, 101), (0.2, 0), (float("inf"), 1)):
            rows = journal_fixture(); rows[2].update(elapsed_seconds=elapsed, remaining_seconds=remaining)
            with self.subTest(elapsed=elapsed), self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_deadline_respected(self):
        budgets = {**self.budgets, "deadline_utc": "2026-09-27T00:00:01+00:00"}
        with self.assertRaises(audit.v.VerificationError): self.replay(journal_fixture(), budgets)

    def test_post_flush_absolute_deadline_gate(self):
        rows = journal_fixture()
        rows[2]["remaining_seconds"] = 0.6
        rows[3].update(dispatch_remaining_seconds=0.1, solver_time_limit_seconds=0.1)
        budgets = {**self.budgets, "deadline_utc": "2026-09-27T00:00:02.6+00:00"}
        self.assertEqual(self.replay(rows, budgets)["lp_calls"], 1)
        rows[3]["dispatch_gate_utc"] = "2026-09-27T00:00:02.7+00:00"
        with self.assertRaises(audit.v.VerificationError): self.replay(rows, budgets)

    def test_model_or_call_cannot_follow_stop(self):
        rows = journal_fixture()
        rows[2] = {**rows[2], "event": "RUN_STOP", "lp_calls": 0, "reason": "STOP"}
        rows[3] = {**rows[3], "event": "LP_BEGIN", "method": "highs-ds", "remaining_seconds": 99,
                   "admission_gate_elapsed_seconds": 0.25, "admission_gate_utc": "2026-09-27T00:00:02.5+00:00"}
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_unmatched_call_never_completed(self):
        rows = journal_fixture(); del rows[3]
        for i, row in enumerate(rows): row["seq"] = i
        with self.assertRaises(audit.v.VerificationError): self.replay(rows)

    def test_partial_line_and_missing_terminal_fail(self):
        payload = b"".join(json.dumps(r).encode() + b"\n" for r in journal_fixture())
        with self.assertRaises(audit.v.VerificationError): audit.verify_events(payload[:-1], self.budgets)
        with self.assertRaises(audit.v.VerificationError): self.replay(journal_fixture()[:-1])

    def test_unvisited_union_is_explicit_hold(self):
        result = audit.conclusion([])
        self.assertEqual(result["systems_covered"], 0)
        self.assertTrue(result["status"].startswith("HOLD"))

    def test_empty_and_incomplete_unions_not_unique(self):
        row = {"status": "EXACT_INFEASIBLE", "possible": [], "unique": []}
        self.assertTrue(audit.conclusion([row], 2)["status"].startswith("HOLD"))
        self.assertEqual(audit.conclusion([row] * 2, 2)["status"], "EXACT_EMPTY_UNION")

    def test_distinct_witnesses_allow_early_stop(self):
        rows = [{"status": "EXACT_COMPATIBLE", "possible": [name], "unique": []} for name in ("a", "b")]
        self.assertEqual(audit.conclusion(rows)["status"], "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER")

    def test_same_w_all_components_and_nonempty_required(self):
        good = {"status": "EXACT_COMPATIBLE", "possible": ["a"], "unique": ["a"]}
        self.assertTrue(audit.conclusion([good], 2)["status"].startswith("HOLD"))
        self.assertEqual(audit.conclusion([good, {"status": "EXACT_INFEASIBLE", "possible": [], "unique": []}], 2)["status"],
                         "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN")
        self.assertTrue(audit.conclusion([good, audit.unresolved_description()], 2)["status"].startswith("HOLD"))

    def test_safe_paths_reject_escape_absolute_and_backslash(self):
        with tempfile.TemporaryDirectory() as directory:
            for value in ("../x", "/x", "C:/x", "cases\\x", "cases//x", "./x"):
                with self.subTest(value=value), self.assertRaises(audit.v.VerificationError):
                    audit.safe_file(directory, value)

    def test_inventory_reader_checks_consumed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.json"
            original = b'{"safe":true}\n'
            path.write_bytes(original)
            output = {"files": [{"path": "x.json", "bytes": len(original), "sha256": audit.v.digest(original)}]}
            read = audit.inventory_reader(directory, output)
            self.assertEqual(read("x.json"), original)
            path.write_bytes(b'{"safe":false}\n')
            with self.assertRaises(audit.v.VerificationError): read("x.json")
            with self.assertRaises(audit.v.VerificationError): read("unlisted.json")


class FullReplay(unittest.TestCase):
    """Actual adapter, original-shaped synthetic decimal models, zero solvers.

    Only the original-file authentication and repeated 4200-model construction
    boundary are stubbed. Those have separate archive/metadata tests above.
    All generated proof arithmetic, bytes, journal and union logic are real.
    """
    @classmethod
    def setUpClass(cls):
        cls.receptors, cls.profiles = audit.parse_native(native_fixture())
        cls.tuples = audit.profile_grid()
        cls.models = [audit.tuple_model(cls.receptors[0], cls.profiles, t) for t in cls.tuples]
        hashes = [audit.v.digest(audit.canonical(m)) for m in cls.models]
        cls.descriptors = [{"sample_index": i, "tuple_index": j, "model_key": f"s{i:02d}_t{j:03d}",
            "model_sha256": h, "case_file": f"cases/m_{i:02d}_{j:03d}_{h[:12]}.json"}
            for i in range(35) for j, h in enumerate(hashes)]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "private/synthetic"
        (self.directory / "cases").mkdir(parents=True)
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(audit, "verify_dependencies"))
        self.stack.enter_context(patch.object(audit, "load_original_inputs",
            return_value=(self.receptors, self.profiles, {"synthetic": True})))
        self.stack.enter_context(patch.object(audit, "expected_descriptors", return_value=self.descriptors))

    def write(self, path, value):
        (self.directory / path).write_bytes(audit.canonical(value))

    def read(self, path):
        return audit.json_load((self.directory / path).read_bytes())

    def seal(self):
        records = [{"path": p.relative_to(self.directory).as_posix(), "bytes": len(p.read_bytes()),
                    "sha256": audit.v.digest(p.read_bytes())} for p in self.directory.rglob("*")
                   if p.is_file() and p.name not in ("output_manifest.json", "independent_verification.json")]
        self.write("output_manifest.json", {"schema": self.manifest["schema"], "run_id": "synthetic",
            "manifest_sha256": self.mh, "run_status": self.index["run_status"], "files": records,
            "budget": self.index["budget"]})

    def build(self, stopped=False, failed_write=False):
        samples = [{"sample_index": i, "identity": {k: r[k] for k in audit.v.IDENTITY}}
                   for i, r in enumerate(self.receptors)]
        digests = {"sample_order_sha256": audit.v.digest(audit.canonical(samples)),
                   "tuple_order_sha256": audit.v.digest(audit.canonical(self.tuples)),
                   "ordered_model_sha256": audit.v.digest(audit.canonical([d["model_sha256"] for d in self.descriptors]))}
        self.manifest = {"schema": "cold_interval_union_v1", "run_id": "synthetic", "output_relative": "private/synthetic",
            "approved_dependency_byte_variants": copy.deepcopy(audit.APPROVED_DEPENDENCY_BYTE_VARIANTS),
            "created_utc": "2026-09-27T00:00:00+00:00", "scientific": audit.scientific(), "inputs": {"synthetic": True},
            "budgets": JournalAndAccounting.budgets, "samples": samples, "tuples": self.tuples,
            "models": self.descriptors, "metadata_digests": digests, "dependencies": {}}
        self.write("manifest.json", self.manifest); self.mh = audit.v.digest(audit.canonical(self.manifest))
        self.write("preflight.json", {"schema": self.manifest["schema"], "manifest_sha256": self.mh,
            "exclusive_write_probe": True, "field_lp_calls": 0, "planned_files": 4206, "maximum_full_path_length": 220,
            "metadata": {"status": "METADATA_ONLY_NO_LP", "archives": 4, "members": 39,
                         "samples": 35, "tuples": 120, "models": 4200, **digests}})
        events, models, calls = [], 0, 0
        moment = datetime(2026, 9, 27, tzinfo=timezone.utc)
        def event(kind, key=None, **extra):
            seq = len(events); elapsed = seq / 100
            if kind in ("MODEL_BEGIN", "LP_BEGIN"):
                extra.update(admission_gate_elapsed_seconds=elapsed - 0.005,
                             admission_gate_utc=(moment + timedelta(seconds=elapsed - 0.005)).isoformat())
            events.append({"seq": seq, "event": kind, "model_key": key, "models_started": models,
                "lp_calls": calls, "elapsed_seconds": elapsed, "utc": (moment + timedelta(seconds=elapsed)).isoformat(), **extra})
            return seq
        def snapshot(elapsed):
            return {"models_started": models, "lp_calls": calls, "solver_invocation_attempts": calls,
                "precall_aborted": 0, "elapsed_seconds": elapsed, "max_models": 4200, "max_lp_calls": 20000,
                "elapsed_limit_seconds": 100, "deadline_utc": None,
                "lp_counter_semantics": "charged attempts, including explicit pre-invocation aborts"}
        self.write("run_started.json", {"schema": self.manifest["schema"], "run_id": "synthetic", "manifest_sha256": self.mh,
            "started_utc": moment.isoformat(), "explicit_execution_acknowledgment": True, "budget": snapshot(0)})
        event("RUN_START")
        rows = []
        for i in range(35):
            visits = []
            if i == 0 or not (stopped or failed_write):
                descriptor = self.descriptors[i * 120]; key = descriptor["model_key"]
                models += 1; begin = event("MODEL_BEGIN", key); before = calls
                if stopped or failed_write:
                    result = None; completion = "ERROR"; description = audit.unresolved_description()
                else:
                    model = self.models[0]
                    def point(j):
                        return {"status": "EXACT_FEASIBLE", "solver_status": 0,
                            "primal": {"verified": True, "point": [str(10 * int(k == j)) for k in range(7)]}}
                    result = {"overall_status": "EXACT_COMPATIBLE", "feasibility": point(0),
                        "co_leaders": {model["names"][0]: point(0), model["names"][1]: point(1)},
                        "co_leader_search_complete": False, "leader_bounds": {},
                        "verified_unique_leaders_above_margin_threshold": [], "stopping_reason": "SECOND_UNION_CO_LEADER_WITNESS"}
                    description, number = audit.inspect_complete(model, result, [], None, "NOT_ATTEMPTED", Counter())
                    for _ in range(number):
                        calls += 1
                        dispatch = len(events) / 100 + 0.005; allowance = 100 - dispatch - 0.001
                        event("LP_BEGIN", key, call_id=calls, method="highs-ds", remaining_seconds=100 - len(events) / 100)
                        event("LP_END", key, call_id=calls, solver_status=0, invocation_attempted=True,
                              dispatch_gate_elapsed_seconds=dispatch, dispatch_remaining_seconds=allowance,
                              dispatch_gate_utc=(moment + timedelta(seconds=dispatch)).isoformat(),
                              solver_time_limit_seconds=allowance)
                    completion = "COMPLETE"
                end = event("MODEL_END", key, completion=completion)
                case = {"schema": self.manifest["schema"], "run_id": "synthetic", "manifest_sha256": self.mh,
                    **descriptor, "model": audit.v.encode(self.models[0]), "prior_possible": [], "completion": completion,
                    "result": result, "farkas_completion": None, "farkas_attempt": "NOT_ATTEMPTED", "farkas_reason": "SYNTHETIC",
                    "description": description, "calls_before": before, "calls_after": calls,
                    "event_seq_begin": begin, "event_seq_end": end}
                if failed_write:
                    (self.directory / descriptor["case_file"]).write_bytes(b'{"partial":')
                    digest = None
                else:
                    self.write(descriptor["case_file"], case); digest = audit.v.digest(audit.canonical(case))
                visits.append({"tuple_index": 0, "model_key": key, "case_file": descriptor["case_file"],
                    "case_sha256": digest, "case_write_complete": not failed_write,
                    "completion": completion, "description": description})
            rows.append({"sample_index": i, "visits": visits, "unvisited_tuple_indices": list(range(len(visits), 120)),
                         "conclusion": audit.conclusion([v["description"] for v in visits])})
        state = "STOPPED_ERROR" if stopped or failed_write else "COMPLETE"
        if state.startswith("STOPPED"):
            event("RUN_STOP", reason="synthetic error")
        event("RUN_END", run_status=state)
        (self.directory / "events.jsonl").write_bytes(b"".join(audit.canonical(e).replace(b"\n", b"") + b"\n" for e in events))
        self.index = {"schema": self.manifest["schema"], "run_id": "synthetic", "manifest_sha256": self.mh,
            "run_status": state, "stop_reason": "synthetic error" if stopped or failed_write else None,
            "started_utc": moment.isoformat(), "completed_utc": (moment + timedelta(seconds=10)).isoformat(),
            "budget": snapshot(10), "samples": rows}
        self.write("index.json", self.index); self.seal()

    def replay(self):
        return audit.verify_run(self.directory, self.root / "no_inputs", root=self.root)

    def test_all35_exact_ambiguity_complete_without_any_lp(self):
        self.build(); result = self.replay()
        self.assertEqual(result["model_attempts_verified"], 35)
        self.assertEqual(result["charged_LP_attempts_verified"], 105)
        self.assertEqual(result["sample_status_counts"], {"EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER": 35})
        self.assertEqual(result["LPs_run_by_verifier"], 0)

    def test_stopped_run_retains_all35_and_unvisited_holds(self):
        self.build(stopped=True); result = self.replay()
        self.assertEqual(result["model_attempts_verified"], 1)
        self.assertEqual(result["sample_status_counts"], {"HOLD_INCOMPLETE_OR_UNRESOLVED_UNION": 35})

    def test_partial_failed_case_write_is_frozen_but_not_interpreted(self):
        self.build(failed_write=True); result = self.replay()
        self.assertEqual(result["proof_counts"]["unverified_failed_case_writes"], 1)

    def test_self_reported_union_promotion_rejected(self):
        self.build(stopped=True)
        self.index["samples"][0]["conclusion"]["status"] = "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN"
        self.write("index.json", self.index); self.seal()
        with self.assertRaises(audit.v.VerificationError): self.replay()

    def test_no_orphan_or_unlisted_files(self):
        self.build(); (self.directory / "unlisted.txt").write_bytes(b"x")
        with self.assertRaises(audit.v.VerificationError): self.replay()

    def test_only_named_independent_output_is_exempt(self):
        self.build(); (self.directory / "independent_verification.json").write_bytes(b"not an input")
        self.assertEqual(self.replay()["status"], "PASS")

    def test_rehashed_case_cannot_invent_prior_witness(self):
        self.build(); visit = self.index["samples"][0]["visits"][0]
        case = self.read(visit["case_file"]); case["prior_possible"] = ["oil"]
        self.write(visit["case_file"], case); visit["case_sha256"] = audit.v.digest(audit.canonical(case))
        self.write("index.json", self.index); self.seal()
        with self.assertRaises(audit.v.VerificationError): self.replay()

    def test_complete_case_call_count_cannot_be_fabricated(self):
        self.build(); visit = self.index["samples"][0]["visits"][0]
        case = self.read(visit["case_file"]); case["calls_after"] -= 1
        self.write(visit["case_file"], case); visit["case_sha256"] = audit.v.digest(audit.canonical(case))
        self.write("index.json", self.index); self.seal()
        with self.assertRaises(audit.v.VerificationError): self.replay()

    def test_original_profile_matrix_not_self_reported(self):
        self.build(); visit = self.index["samples"][0]["visits"][0]
        case = self.read(visit["case_file"]); case["model"]["U"][0][0] = "999"
        self.write(visit["case_file"], case); visit["case_sha256"] = audit.v.digest(audit.canonical(case))
        self.write("index.json", self.index); self.seal()
        with self.assertRaises(audit.v.VerificationError): self.replay()


if __name__ == "__main__":
    unittest.main()
