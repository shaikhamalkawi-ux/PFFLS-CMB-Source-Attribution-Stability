#!/usr/bin/env python3
"""New private cold reproduction; prepare/metadata do not solve any field LP.

The fixed question is 35 x 120 full-seven-source k=2/no-mass components.
No historical private record or result partition is an input. Numerical execution
requires explicit approval of this run's pre-solve manifest after separate QA.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
import time
import uuid

import numpy as np
import scipy
import audit_epa_native_strengthening as native
import audit_interval_decisions as core
import audit_interval_profile_union as legacy_union
import audit_interval_farkas_margin as farkas

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = Path("outputs/decision_research_20260926")
SCHEMA = "cold_interval_union_v1"
SLOTS = tuple(native.CONFIG["central_initial_sources"])
MAX_PATH = 240
RECOVERY_RELATIVE = "outputs/strengthening_20260926/source_recovery.json"
APPROVED_DEPENDENCY_BYTE_VARIANTS = {RECOVERY_RELATIVE: [
    "4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2",  # 9074-byte CRLF
    "32762085a73ee0b5ad703bc68ab8194303ca0769c49494202343b622e356c0e2",  # 8817-byte Git LF
]}
PINNED = {
    "scripts/audit_epa_native_strengthening.py": "42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09",
    "scripts/audit_interval_decisions.py": "ecb4e8f01f4028eb0a43d85870b3f458b75fce91d8bad9bdddaa815c3597da93",
    "scripts/audit_interval_profile_union.py": "d02e65ad5799f82b8960276d3c9eeee1e43c31cbcc78faddc22924d7431ff21b",
    "scripts/audit_interval_farkas_margin.py": "b5a95a583c533e9dd28cccd6a2737de1bf4b06425b986cad2b20510fe84f54a0",
    "scripts/verify_interval_certificate_records.py": "53d1682413236b394fc24adae1d2dea75c2a621799947111e9a835a5afea1fed",
    "scripts/verify_interval_union_records.py": "2c68cb669ceaff1d95b419e517be4f96f32c37425f2529cab2f2a4ee437dbd5b",
    "scripts/verify_interval_farkas_records.py": "e71f43fd865e2b657109f32bd76f9f47786ab4d1a732315fdb0391c63ad17521",
    "tests/test_interval_decisions.py": "777862955c40b41a147886e701914840ff8eae6a061cd96a510f9e4de5e25033",
    "outputs/decision_research_20260926/interval_configuration.json": "9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a",
    "outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md": "7fede98bd7f789ba8f228667912be15c80e592195b508859c4ca01fecfd8078e",
    str(PUBLIC / "joint_profile_configuration.json").replace("\\", "/"): "f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314",
    str(PUBLIC / "COLD_RUN_REPRODUCTION_PROPOSAL.md").replace("\\", "/"): "d83392e843e409aade87a3dfd050c0da81448fcf9720be3dc828cd17820f9dca",
}
EXTRA_DEPENDENCIES = (
    RECOVERY_RELATIVE,
    str(PUBLIC / "COLD_RUN_ROOT_DECISION.md"),
    str(PUBLIC / "COLD_RUN_RECORD_SCHEMA.md"),
    "scripts/reproduce_interval_union.py", "tests/test_cold_interval_union.py",
    "scripts/verify_cold_interval_union.py", "tests/test_cold_interval_union_records.py",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def data(value):
    return (json.dumps(core.encode_q(value), sort_keys=True, indent=2,
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_sha(path):
    return digest(Path(path).read_bytes())


def exclusive_json(path, value):
    payload = data(value)
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return digest(payload)


def checked_recovery_bytes(path):
    """Only two approved byte identities, not general JSON/newline equivalence."""
    payload = path.read_bytes()
    if digest(payload) not in APPROVED_DEPENDENCY_BYTE_VARIANTS[RECOVERY_RELATIVE]:
        raise ValueError("unapproved recovery metadata byte identity")
    return payload


class _CheckedRecoveryBuffer:
    """Read-only byte source for the unchanged native identity-checking routine."""
    def __init__(self, payload):
        self._payload = payload

    def read_bytes(self):
        return self._payload


def recovery_identities(inventory, path):
    payload = checked_recovery_bytes(path)
    # The frozen function calls read_bytes once. Give it the checked bytes in
    # memory, so its JSON parser cannot reopen an unchecked filesystem version.
    return native.verify_recovery_identities(inventory, _CheckedRecoveryBuffer(payload))


def dependencies():
    answer = {}
    for relative in list(PINNED) + list(EXTRA_DEPENDENCIES):
        relative = relative.replace("\\", "/")
        observed = (digest(checked_recovery_bytes(ROOT / relative)) if relative == RECOVERY_RELATIVE
                    else file_sha(ROOT / relative))
        if relative in PINNED and observed != PINNED[relative]:
            raise ValueError("frozen public dependency changed: " + relative)
        answer[relative] = observed
    return answer


def environment():
    return {"python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "platform": platform.platform()}


def scientific(families):
    return {"samples": 35, "tuples_per_sample": 120, "species": native.CONFIG["species"],
            "source_slots": list(SLOTS), "family_names": [core.LABELS[s] for s in SLOTS],
            "families": families, "k": 2, "profile_mode": "joint_intervals", "mass_mode": "none",
            "nonnegative_contributions": True, "source_pruning": False,
            "delta": "1/10000000 * max(1, TMAC); strict greater-than",
            "receptor_filter": native.CONFIG["receptor_filter"],
            "source_selector": {"member": "PRsjvf.sel", "column": 22, "id_field": 1},
            "species_selector": {"member": "SPsjvf.sel", "column": 20, "identical_column": 24}}


def tuple_model(receptor, profiles, chosen):
    if len(chosen) != len(SLOTS):
        raise ValueError("incomplete source tuple")
    aliased = {slot: profiles[sid] for slot, sid in zip(SLOTS, chosen)}
    result = core.field_model(receptor, aliased, list(SLOTS), 2, "joint_intervals", "none")
    result["sources"] = list(chosen)
    return result


def metadata(inputs, check_time=lambda: None):
    """Native metadata/model reconstruction only. Never call an LP or point fit."""
    check_time()
    # Native archive_inventory checks hard-coded SHA256 before any ZIP parsing.
    inventory = native.archive_inventory(Path(inputs))
    recovered = recovery_identities(inventory, ROOT / RECOVERY_RELATIVE)
    if recovered["archives_checked"] != 4 or recovered["members_checked"] != 39:
        raise ValueError("incomplete original archive/member universe")
    receptors, profiles, summary = native.load_inputs(Path(inputs))
    grid_path = ROOT / PUBLIC / "joint_profile_configuration.json"
    if file_sha(grid_path) != PINNED[str(PUBLIC / "joint_profile_configuration.json").replace("\\", "/")]:
        raise ValueError("frozen historical profile grid changed")
    families = json.loads(grid_path.read_bytes())["families"]
    for slot, alternatives in summary["alternatives"].items():
        if families.get(slot) != [slot] + alternatives:
            raise ValueError("descriptor family order differs from historical grid")
    tuples = [list(t) for t in itertools.product(*(families.get(s, [s]) for s in SLOTS))]
    if len(tuples) != 120 or len({tuple(t) for t in tuples}) != 120 or tuples[0] != list(SLOTS):
        raise ValueError("missing, duplicate or reordered tuple universe")
    fields = ("ID", "DATE", "DUR", "STHOUR", "SIZE")
    samples = [{"sample_index": i, "identity": {k: rec[k] for k in fields}}
               for i, rec in enumerate(receptors)]
    if len(samples) != 35 or len({tuple(x["identity"][k] for k in fields) for x in samples}) != 35:
        raise ValueError("35 distinct ordered receptors required")
    receptor_pairs = profile_pairs = 0
    for rec in receptors:
        if Q(rec["TMAC"]) <= 0:
            raise ValueError("invalid mass used for fixed threshold")
        for name in summary["species"]:
            c, uc = Q(rec[name]), Q(rec[name[:-1] + "U"])
            if uc <= 0 or c == -99:
                raise ValueError("invalid receptor field")
            receptor_pairs += 1
    for sid in sorted({s for t in tuples for s in t}):
        row = profiles[sid]
        if row["SID"] != sid or row["SIZE"] != "FINE":
            raise ValueError("wrong profile identity or size")
        for name in summary["species"]:
            if Q(row[name]) < 0 or Q(row[name[:-1] + "U"]) < 0:
                raise ValueError("invalid profile mean/uncertainty pair")
            profile_pairs += 1
    models = []
    for i, receptor in enumerate(receptors):
        for j, chosen in enumerate(tuples):
            check_time()
            mh = digest(data(tuple_model(receptor, profiles, chosen)))
            key = f"s{i:02d}_t{j:03d}"
            models.append({"sample_index": i, "tuple_index": j, "model_key": key,
                           "model_sha256": mh, "case_file": f"cases/m_{i:02d}_{j:03d}_{mh[:12]}.json"})
    digests = {"sample_order_sha256": digest(data(samples)), "tuple_order_sha256": digest(data(tuples)),
               "ordered_model_sha256": digest(data([m["model_sha256"] for m in models]))}
    frozen = {"scientific": scientific(families), "samples": samples, "tuples": tuples, "models": models,
              "approved_dependency_byte_variants": APPROVED_DEPENDENCY_BYTE_VARIANTS,
              "metadata_digests": digests,
              "inputs": {"archive_inventory": inventory, "recovery_verification": recovered,
                         "input_summary": summary, "validated_receptor_species_pairs": receptor_pairs,
                         "validated_profile_species_pairs": profile_pairs}}
    return frozen, receptors, profiles


def public_metadata(frozen):
    return {"status": "METADATA_ONLY_NO_LP", "archives": 4, "members": 39, "samples": 35,
            "tuples": 120, "models": len(frozen["models"]), **frozen["metadata_digests"]}


def parse_deadline(value):
    if value is None:
        return None
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("deadline must include a timezone")
    return result.astimezone(timezone.utc)


def budget_config(models=4200, calls=20000, seconds=7200, deadline=None):
    if type(models) is not int or not 1 <= models <= 4200:
        raise ValueError("model ceiling must be an integer from 1 to 4200")
    if type(calls) is not int or not 1 <= calls <= 20000:
        raise ValueError("LP ceiling must be an integer from 1 to 20000")
    if isinstance(seconds, bool) or not math.isfinite(seconds) or not 0 < seconds <= 7200:
        raise ValueError("elapsed ceiling must be finite, positive and <=7200 seconds")
    parsed = parse_deadline(deadline)
    return {"max_models": models, "max_lp_calls": calls, "elapsed_seconds": float(seconds),
            "deadline_utc": parsed.isoformat() if parsed else None}


def output_path(path, inputs, root=None, require_absent=True):
    raw = Path(path).absolute()
    root = ROOT if root is None else root
    private = Path(root).resolve() / "private"
    if any(p.is_symlink() or p.is_junction() for p in (raw, *raw.parents)):
        raise ValueError("symlinked output containment is not permitted")
    resolved = raw.resolve()
    if resolved.parent != private or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,40}", resolved.name):
        raise ValueError("output must be a named direct child of repository/private")
    if resolved.name.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                                  *(f"LPT{i}" for i in range(1, 10))}:
        raise ValueError("reserved output name")
    source = Path(inputs).resolve()
    if resolved == source or resolved in source.parents or source in resolved.parents:
        raise ValueError("input/output overlap")
    if require_absent and resolved.exists():
        raise FileExistsError("output already exists; no overwrite or resume")
    return resolved


def prepare(inputs, output, budgets):
    config = budget_config(budgets["max_models"], budgets["max_lp_calls"],
                           budgets["elapsed_seconds"], budgets["deadline_utc"])
    output = output_path(output, inputs)
    deps = dependencies()
    frozen, _, _ = metadata(inputs)
    if frozen["inputs"]["recovery_verification"]["recovery_record_sha256"] != deps[RECOVERY_RELATIVE]:
        raise ValueError("recovery byte identity changed between dependency and metadata checks")
    planned = ["manifest.json", "preflight.json", "run_started.json", "events.jsonl",
               "index.json", "output_manifest.json"] + [m["case_file"] for m in frozen["models"]]
    if len(planned) != len(set(planned)) or max(len(str(output / p)) for p in planned) > MAX_PATH:
        raise ValueError("duplicate or unsafe full output path length")
    output.parent.mkdir(exist_ok=True)
    output.mkdir()  # Exclusive directory creation; no automatic cleanup of failures.
    (output / "cases").mkdir()
    probe = output / ".write_probe"
    with probe.open("xb") as stream:
        stream.write(b"cold-reproduction-preflight\n")
        stream.flush()
        os.fsync(stream.fileno())
    probe.unlink()  # Only the probe just exclusively created by this function.
    manifest = {"schema": SCHEMA, "run_id": str(uuid.uuid4()), "created_utc": now(),
                "output_relative": output.relative_to(ROOT.resolve()).as_posix(),
                "budgets": config,
                "dependencies": deps,
                "environment": environment(), **frozen}
    mh = exclusive_json(output / "manifest.json", manifest)
    exclusive_json(output / "preflight.json", {"schema": SCHEMA, "manifest_sha256": mh,
                   "metadata": public_metadata(frozen), "planned_files": len(planned),
                   "maximum_full_path_length": max(len(str(output / p)) for p in planned),
                   "exclusive_write_probe": True, "field_lp_calls": 0})
    return {"status": "PREPARED_NOT_APPROVED_FOR_FIELD_EXECUTION", "manifest_sha256": mh,
            "metadata": public_metadata(frozen)}


class BudgetStop(Exception):
    """Separate from RuntimeError, which the frozen numerical core catches."""


class Journal:
    def __init__(self, path):
        self.stream = Path(path).open("xb")
        self.seq = 0

    def event(self, event, budget, **extra):
        value = {"seq": self.seq, "event": event, "utc": now(), "elapsed_seconds": budget.elapsed(),
                 "models_started": budget.models, "lp_calls": budget.calls,
                 "model_key": budget.model_key, **extra}
        # Budget checks must not interrupt the recording of an already charged
        # attempt. The dispatch gate is checked again after this durable write.
        was_journaling = budget.journaling
        budget.journaling = True
        try:
            payload = (json.dumps(core.encode_q(value), sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
            self.stream.write(payload)
            self.stream.flush()
            os.fsync(self.stream.fileno())
        finally:
            budget.journaling = was_journaling
        self.seq += 1
        return value["seq"]

    def close(self):
        self.stream.close()


class Budget:
    def __init__(self, config, clock=time.monotonic, utc=lambda: datetime.now(timezone.utc)):
        self.config = budget_config(config["max_models"], config["max_lp_calls"],
                                    config["elapsed_seconds"], config["deadline_utc"])
        self.clock, self.utc, self.started = clock, utc, clock()
        self.deadline = parse_deadline(self.config["deadline_utc"])
        self.models = self.calls = self.invocation_attempts = self.precall_aborted = 0
        self.model_key = None
        self.journal = None
        self.original = None
        self.scientific_active = self.journaling = False

    def elapsed(self):
        return max(0.0, self.clock() - self.started)

    def check_time(self):
        elapsed, utc = self.elapsed(), self.utc()
        self.last_gate_elapsed, self.last_gate_utc = elapsed, utc.isoformat()
        remaining = self.config["elapsed_seconds"] - elapsed
        if self.deadline:
            remaining = min(remaining, (self.deadline - utc).total_seconds())
        if remaining <= 0:
            raise BudgetStop("ELAPSED_OR_DEADLINE_LIMIT")
        return remaining

    def begin_model(self, key):
        self.check_time()
        if self.models >= self.config["max_models"]:
            raise BudgetStop("MODEL_LIMIT")
        if self.calls >= self.config["max_lp_calls"]:
            raise BudgetStop("LP_CALL_LIMIT")
        self.models += 1
        self.model_key = key
        return self.journal.event("MODEL_BEGIN", self,
                                  admission_gate_elapsed_seconds=self.last_gate_elapsed,
                                  admission_gate_utc=self.last_gate_utc)

    def call(self, *args, **kwargs):
        remaining = self.check_time()
        if self.calls >= self.config["max_lp_calls"]:
            raise BudgetStop("LP_CALL_LIMIT")
        self.calls += 1
        call_id = self.calls
        self.journal.event("LP_BEGIN", self, call_id=call_id, method=kwargs.get("method", "highs"),
                           remaining_seconds=remaining,
                           admission_gate_elapsed_seconds=self.last_gate_elapsed,
                           admission_gate_utc=self.last_gate_utc)
        invoked, dispatch = False, {}
        try:
            # Durable journaling can be slow: never use its stale allowance.
            remaining = self.check_time()
            options = dict(kwargs.get("options", {}))
            requested = options.get("time_limit", remaining)
            if isinstance(requested, bool) or not math.isfinite(requested) or requested <= 0:
                raise ValueError("invalid requested numerical time limit")
            options["time_limit"] = min(remaining, requested)
            kwargs["options"] = options
            dispatch = {"dispatch_gate_elapsed_seconds": self.last_gate_elapsed,
                        "dispatch_gate_utc": self.last_gate_utc,
                        "dispatch_remaining_seconds": remaining,
                        "solver_time_limit_seconds": options["time_limit"]}
            self.invocation_attempts += 1
            invoked = True
            result = self.original(*args, **kwargs)
        except BaseException as exc:
            if not invoked:
                self.precall_aborted += 1
            self.journal.event("LP_ERROR", self, call_id=call_id, error_category=type(exc).__name__,
                               invocation_attempted=invoked, charged_but_not_invoked=not invoked, **dispatch)
            raise
        self.journal.event("LP_END", self, call_id=call_id, solver_status=int(result.status),
                           invocation_attempted=True, **dispatch)
        return result

    def snapshot(self):
        return {"models_started": self.models, "lp_calls": self.calls, "elapsed_seconds": self.elapsed(),
                "lp_counter_semantics": "charged attempts, including explicit pre-invocation aborts",
                "solver_invocation_attempts": self.invocation_attempts, "precall_aborted": self.precall_aborted,
                "max_models": self.config["max_models"], "max_lp_calls": self.config["max_lp_calls"],
                "elapsed_limit_seconds": self.config["elapsed_seconds"], "deadline_utc": self.config["deadline_utc"]}

    @contextmanager
    def guard(self):
        self.original = core.linprog
        previous_trace = sys.gettrace()
        guarded_files = {core.__file__, legacy_union.__file__, farkas.__file__}
        ticks = 0

        def trace(frame, event, arg):
            nonlocal ticks
            if (event == "line" and self.scientific_active and not self.journaling
                    and frame.f_code.co_filename in guarded_files):
                ticks += 1
                if ticks % 32 == 0:
                    self.check_time()
            return trace

        core.linprog = self.call
        sys.settrace(trace)  # Cooperative guard inside exact Python arithmetic.
        try:
            yield self
        finally:
            sys.settrace(previous_trace)
            core.linprog = self.original


def complete_margin(model, result):
    """Preserve result; return an independent description and separate fallback."""
    description = {**legacy_union.describe(result), "margin_route": None}
    if description["unique"]:
        description["margin_route"] = "OBJECTIVE"
        return description, None, "NOT_ATTEMPTED", "OBJECTIVE_ALREADY_SUFFICIENT"
    co = result["co_leaders"]
    possible = [name for name in model["names"] if co.get(name, {}).get("status") == "EXACT_FEASIBLE"]
    eligible = (result["overall_status"] == "EXACT_COMPATIBLE" and len(possible) == 1
                and set(co) == set(model["names"])
                and all(co[name]["status"] == "EXACT_INFEASIBLE" for name in model["names"] if name != possible[0]))
    if not eligible:
        return description, None, "NOT_ATTEMPTED", "NONEMPTY_UNIVERSAL_LEADER_PREMISES_NOT_ESTABLISHED"
    threshold = Q(1, 10_000_000) * max(Q(1), Q(model["mass"]))
    completion = farkas.component_margins(model, result, threshold)
    if completion["status"] == "EXACT_FEASIBLE_ALL_MARGIN_PREMISES" and completion["all_margins_above_delta"]:
        description["unique"] = [completion["leader"]]
        description["margin_route"] = "FARKAS"
    return description, completion, "DERIVED", "EXACT_SAVED_EXCLUSIONS_ONLY"


def unresolved_description():
    return {"status": "NUMERICALLY_UNRESOLVED", "possible": [], "unique": [],
            "exhaustive_model_decisions": False, "margin_route": None}


def sample_summary(sample_index, visits, tuple_count):
    indices = [v["tuple_index"] for v in visits]
    if indices != list(range(len(indices))) or len(set(indices)) != len(indices) or len(indices) > tuple_count:
        raise ValueError("sample visits are not a distinct frozen-order prefix")
    return {"sample_index": sample_index, "visits": visits,
            "unvisited_tuple_indices": list(range(len(indices), tuple_count)),
            "conclusion": legacy_union.conclusion([v["description"] for v in visits], tuple_count)}


def seal(output, manifest, manifest_sha, run_status, budget):
    files = []
    for path in sorted(output.rglob("*")):
        if path.is_symlink() or path.is_junction():
            raise ValueError("unexpected symlink in new private output")
        if path.is_file():
            relative = path.relative_to(output).as_posix()
            if relative == "output_manifest.json":
                raise FileExistsError("terminal manifest already exists")
            files.append({"path": relative, "bytes": path.stat().st_size, "sha256": file_sha(path)})
    exclusive_json(output / "output_manifest.json", {"schema": SCHEMA, "run_id": manifest["run_id"],
                   "manifest_sha256": manifest_sha, "run_status": run_status, "files": files,
                   "budget": budget.snapshot()})


def execute(output, manifest, manifest_sha, receptors, profiles, budget,
            inspector=legacy_union.inspect_model):
    """Internal engine; production caller has already revalidated the full scope."""
    visits = [[] for _ in manifest["samples"]]
    lookup = {(m["sample_index"], m["tuple_index"]): m for m in manifest["models"]}
    if len(lookup) != len(manifest["models"]):
        raise ValueError("duplicate model descriptor")
    started = now()
    journal = Journal(output / "events.jsonl")
    budget.journal = journal
    run_status, reason = "COMPLETE", None
    journal.event("RUN_START", budget)

    def visit(i, j):
        descriptor = lookup[i, j]
        budget.check_time()
        model = tuple_model(receptors[i], profiles, manifest["tuples"][j])
        if digest(data(model)) != descriptor["model_sha256"]:
            raise ValueError("preflight model identity changed")
        event_begin = budget.begin_model(descriptor["model_key"])
        calls_before = budget.calls
        prior = sorted({name for v in visits[i] for name in v["description"]["possible"]})
        record = {"schema": SCHEMA, "run_id": manifest["run_id"], "manifest_sha256": manifest_sha,
                  **descriptor, "model": model, "prior_possible": prior, "completion": "COMPLETE",
                  "result": None, "farkas_completion": None, "farkas_attempt": "NOT_ATTEMPTED",
                  "farkas_reason": "MODEL_NOT_COMPLETED", "description": unresolved_description(),
                  "calls_before": calls_before, "event_seq_begin": event_begin}
        stop = None
        try:
            budget.scientific_active = True
            budget.check_time()
            record["result"] = inspector(model, prior)
            budget.check_time()
            desc, fallback, attempted, why = complete_margin(model, record["result"])
            budget.check_time()
            record.update(description=desc, farkas_completion=fallback, farkas_attempt=attempted, farkas_reason=why)
        except BaseException as exc:
            stop = exc
            record["completion"] = "STOPPED" if isinstance(exc, (BudgetStop, KeyboardInterrupt)) else "ERROR"
            record["stop_reason"] = str(exc) if isinstance(exc, BudgetStop) else type(exc).__name__
            record["error_category"] = type(exc).__name__
            record["description"] = unresolved_description()
            if record["result"] is not None:
                record["farkas_attempt"] = "ERROR"
                record["farkas_reason"] = "INTERRUPTED_OR_INVALID_COMPLETION"
        finally:
            budget.scientific_active = False
        record["calls_after"] = budget.calls
        record["event_seq_end"] = journal.event("MODEL_END", budget, completion=record["completion"])
        try:
            case_sha = exclusive_json(output / descriptor["case_file"], record)
        except BaseException:
            # A partial file is retained, never repaired or overwritten. Account
            # for the attempt separately; no proof can rely on this visit.
            visits[i].append({"tuple_index": j, "model_key": descriptor["model_key"],
                              "case_file": descriptor["case_file"], "case_sha256": None,
                              "case_write_complete": False, "completion": "ERROR",
                              "description": unresolved_description()})
            raise
        finally:
            budget.model_key = None
        visits[i].append({"tuple_index": j, "model_key": descriptor["model_key"],
                          "case_file": descriptor["case_file"], "case_sha256": case_sha,
                          "case_write_complete": True,
                          "completion": record["completion"], "description": record["description"]})
        if stop is not None:
            raise stop

    try:
        with budget.guard():
            # Complete the central pass first; no historical target partition.
            for i in range(len(visits)):
                visit(i, 0)
            for i in range(len(visits)):
                for j in range(1, len(manifest["tuples"])):
                    possible = {name for v in visits[i] for name in v["description"]["possible"]}
                    if len(possible) >= 2:
                        break
                    visit(i, j)
    except BudgetStop as exc:
        run_status, reason = "STOPPED_BUDGET", str(exc)
    except KeyboardInterrupt:
        run_status, reason = "STOPPED_INTERRUPT", "KEYBOARD_INTERRUPT"
    except BaseException as exc:
        run_status, reason = "STOPPED_ERROR", type(exc).__name__
    try:
        if reason is not None:
            journal.event("RUN_STOP", budget, reason=reason)
        samples = [sample_summary(i, rows, len(manifest["tuples"])) for i, rows in enumerate(visits)]
        if run_status == "COMPLETE" and any(s["conclusion"]["status"].startswith("HOLD_") for s in samples):
            run_status = "COMPLETE_WITH_HOLDS"
        journal.event("RUN_END", budget, run_status=run_status)
    finally:
        journal.close()
    index = {"schema": SCHEMA, "run_id": manifest["run_id"], "manifest_sha256": manifest_sha,
             "run_status": run_status, "stop_reason": reason, "started_utc": started, "completed_utc": now(),
             "budget": budget.snapshot(), "samples": samples}
    exclusive_json(output / "index.json", index)
    seal(output, manifest, manifest_sha, run_status, budget)
    return {"run_status": run_status, "stop_reason": reason, "budget": budget.snapshot(),
            "sample_status_counts": dict(Counter(s["conclusion"]["status"] for s in samples)),
            "independent_verification": "REQUIRED_NOT_PERFORMED"}


def run(inputs, output, approved_manifest):
    output = output_path(output, inputs, require_absent=False)
    if not re.fullmatch(r"[0-9a-f]{64}", approved_manifest or ""):
        raise ValueError("explicit approved manifest SHA256 required")
    if {p.name for p in output.iterdir()} != {"manifest.json", "preflight.json", "cases"} or any((output / "cases").iterdir()):
        raise FileExistsError("not a pristine prepared directory; no overwrite or resume")
    if any(p.is_symlink() or p.is_junction() for p in output.iterdir()):
        raise ValueError("prepared files/directories must not be symbolic links or junctions")
    raw = (output / "manifest.json").read_bytes()
    if digest(raw) != approved_manifest:
        raise ValueError("approval does not match exact pre-solve manifest")
    manifest = json.loads(raw)
    if (manifest["schema"] != SCHEMA or manifest["dependencies"] != dependencies()
            or manifest["output_relative"] != output.relative_to(ROOT.resolve()).as_posix()
            or manifest["environment"] != environment()):
        raise ValueError("schema or dependency identity drift")
    if max(len(str(output / m["case_file"])) for m in manifest["models"]) > MAX_PATH:
        raise ValueError("prepared output path length is unsafe")
    preflight = json.loads((output / "preflight.json").read_bytes())
    if preflight["manifest_sha256"] != approved_manifest or preflight["field_lp_calls"] != 0:
        raise ValueError("missing no-LP preflight")
    budget = Budget(manifest["budgets"])
    frozen, receptors, profiles = metadata(inputs, budget.check_time)
    for key, value in frozen.items():
        if manifest[key] != value:
            raise ValueError("pre-solve scientific/input/model identity drift: " + key)
    exclusive_json(output / "run_started.json", {"schema": SCHEMA, "run_id": manifest["run_id"],
                   "manifest_sha256": approved_manifest, "started_utc": now(),
                   "explicit_execution_acknowledgment": True, "budget": budget.snapshot()})
    return execute(output, manifest, approved_manifest, receptors, profiles, budget)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--metadata-only", action="store_true")
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--approved-manifest-sha256")
    parser.add_argument("--max-models", type=int)
    parser.add_argument("--max-lp-calls", type=int)
    parser.add_argument("--elapsed-seconds", type=float)
    parser.add_argument("--deadline-utc")
    args = parser.parse_args()
    if args.metadata_only:
        if args.output or args.approved_manifest_sha256 or any(v is not None for v in (
                args.max_models, args.max_lp_calls, args.elapsed_seconds, args.deadline_utc)):
            parser.error("metadata-only accepts only the input directory")
        frozen, _, _ = metadata(args.inputs)
        answer = public_metadata(frozen)
    else:
        if args.output is None:
            parser.error("explicit new private output directory required")
        if args.prepare:
            if args.approved_manifest_sha256:
                parser.error("prepare is not numerical execution approval")
            config = budget_config(args.max_models if args.max_models is not None else 4200,
                                   args.max_lp_calls if args.max_lp_calls is not None else 20000,
                                   args.elapsed_seconds if args.elapsed_seconds is not None else 7200,
                                   args.deadline_utc)
            answer = prepare(args.inputs, args.output, config)
        else:
            if any(v is not None for v in (args.max_models, args.max_lp_calls, args.elapsed_seconds, args.deadline_utc)):
                parser.error("run cannot change frozen operational ceilings")
            answer = run(args.inputs, args.output, args.approved_manifest_sha256)
    print(json.dumps(answer, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
