#!/usr/bin/env python3
"""Independent public-input cold-union proof replay. No producer imports or LPs.

The raw-input reader intentionally does not call the historical reader that
requires a retained-source private ledger. Historical output files are never
inputs. Exact arithmetic is reused only from frozen independent validators.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from io import BytesIO
import itertools
import json
import math
from pathlib import Path
import time
from zipfile import ZipFile

import verify_interval_certificate_records as v
import verify_interval_union_records as u
import verify_interval_farkas_records as f

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
require = v.require
GRID_HASH = "f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314"
RECOVERY_RELATIVE = "outputs/strengthening_20260926/source_recovery.json"
# A diagnosed transport-only exception, not generic JSON/newline normalization.
# Every other frozen dependency and every original archive/member stays exact.
APPROVED_DEPENDENCY_BYTE_VARIANTS = {RECOVERY_RELATIVE: [
    "4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2",
    "32762085a73ee0b5ad703bc68ab8194303ca0769c49494202343b622e356c0e2",
]}
RECOVERY_HASHES = set(APPROVED_DEPENDENCY_BYTE_VARIANTS[RECOVERY_RELATIVE])
FROZEN_VERIFIERS = {
    "verify_interval_certificate_records.py": "53d1682413236b394fc24adae1d2dea75c2a621799947111e9a835a5afea1fed",
    "verify_interval_union_records.py": "2c68cb669ceaff1d95b419e517be4f96f32c37425f2529cab2f2a4ee437dbd5b",
    "verify_interval_farkas_records.py": "e71f43fd865e2b657109f32bd76f9f47786ab4d1a732315fdb0391c63ad17521",
}
FAMILIES = {
    "SOIL03": ["SOIL03", "SOIL08", "SOIL12", "SOIL29"],
    "BAMAJC": ["BAMAJC", "MAFISC", "MAMAJC"],
    "SFCRUC": ["SFCRUC", "CHCRUC"],
    "MOVES2": ["MOVES2", "MOVES1", "MOVES3", "MOVES4", "MOVES5"],
}


def json_load(payload):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def real(token):
        value = float(token)
        require(math.isfinite(value), "nonfinite JSON float")
        return value
    return json.loads(payload, object_pairs_hook=unique,
                      parse_float=real,
                      parse_constant=lambda value: (_ for _ in ()).throw(v.VerificationError("nonfinite JSON")))


def canonical(value):
    return (json.dumps(v.encode(value), ensure_ascii=False, allow_nan=False,
                       sort_keys=True, indent=2) + "\n").encode("utf-8")


def pinned_dependency_bytes(root, relative, expected):
    """Read once; permit only the specifically reviewed recovery-byte forms."""
    if relative != RECOVERY_RELATIVE:
        return v.check_hash(safe_file(root, relative), expected)
    require(expected in RECOVERY_HASHES, "unreviewed recovery metadata pin")
    payload = safe_file(root, relative).read_bytes()
    require(v.digest(payload) in RECOVERY_HASHES, "unreviewed recovery metadata encoding/content")
    return payload


def profile_grid():
    rows = [list(t) for t in itertools.product(*(FAMILIES.get(s, [s]) for s in v.SOURCES))]
    require(len(rows) == len({tuple(t) for t in rows}) == 120 and rows[0] == v.SOURCES,
            "fixed historical grid changed")
    return rows


def selected(payload, column, field):
    result = []
    for line in payload.decode("ascii").splitlines():
        if len(line) > column and line[column] == "*":
            parts = line.split()
            require(len(parts) > field, "incomplete selector entry")
            result.append(parts[field])
    return result


def archive_bytes(payload, recorded):
    """Identity-check members without extracting archive-controlled paths."""
    with ZipFile(BytesIO(payload)) as archive:
        entries = [i for i in archive.infolist() if not i.is_dir()]
        require(len(entries) == len({i.filename for i in entries}), "duplicate ZIP member")
        actual = {i.filename: archive.read(i.filename) for i in entries}
    require(len(recorded) == len({r["name"] for r in recorded}), "duplicate recovery member")
    expected = {r["name"]: (r["bytes"], r["sha256"]) for r in recorded}
    require({name: (len(data), v.digest(data)) for name, data in actual.items()} == expected,
            "original archive member identity differs")
    return actual


def parse_native(sjvf):
    require(selected(sjvf["PRsjvf.sel"], 22, 1) == v.SOURCES, "source selector differs")
    require(selected(sjvf["SPsjvf.sel"], 20, 0) == v.SPECIES ==
            selected(sjvf["SPsjvf.sel"], 24, 0), "species selectors differ")
    receptors = [r for r in v.table(sjvf["ADsjvf.txt"])
                 if r["ID"] == "FRESNO" and r["SIZE"] == "FINE"]
    require(len(receptors) == len({tuple(r[k] for k in v.IDENTITY) for r in receptors}) == 35,
            "35 ordered distinct receptors required")
    rows = [r for r in v.table(sjvf["PRsjvf.txt"]) if r["SIZE"] == "FINE"]
    profiles = {r["SID"]: r for r in rows}
    require(len(rows) == len(profiles), "duplicate FINE profile identity")
    descriptions = {}
    for line in sjvf["PRsjvf.sel"].decode("ascii").splitlines():
        if line.strip():
            fields = line[:36].split()
            require(len(fields) >= 2 and fields[1] not in descriptions, "invalid descriptor row")
            descriptions[fields[1]] = line[36:].strip()
    for slot, expected in FAMILIES.items():
        matches = []
        for sid in profiles:
            desc = descriptions.get(sid, "")
            admitted = ((slot == "SOIL03" and "PAVED ROAD" in desc and "UNPAVED" not in desc)
                        or (slot == "BAMAJC" and "CORDWOOD" in desc)
                        or (slot == "SFCRUC" and "CRUDE BOILER" in desc)
                        or (slot == "MOVES2" and sid.startswith("MOVES")))
            if sid != slot and admitted:
                matches.append(sid)
        require([slot] + sorted(matches) == expected, "descriptor-derived alternatives differ")
    for row in receptors:
        require(v.fraction(row["TMAC"]) > 0, "nonpositive receptor mass")
        for species in v.SPECIES:
            require(v.fraction(row[species]) != -99 and v.fraction(row[species[:-1] + "U"]) > 0,
                    "invalid receptor mean/uncertainty")
    for sid in {s for t in profile_grid() for s in t}:
        row = profiles[sid]
        require(row["SID"] == sid and row["SIZE"] == "FINE", "profile identity/size differs")
        for species in v.SPECIES:
            require(v.fraction(row[species]) >= 0 and v.fraction(row[species[:-1] + "U"]) >= 0,
                    "negative or sentinel profile mean/uncertainty")
    return receptors, profiles


def load_original_inputs(inputs, root=ROOT, include_metadata=False):
    """All four archives + public metadata only; no historical private reads."""
    root, inputs = Path(root), Path(inputs)
    for name, expected in FROZEN_VERIFIERS.items():
        v.check_hash(root / "scripts" / name, expected)
    for relative, expected in v.DEPENDENCIES.items():
        pinned_dependency_bytes(root, relative, expected)
    grid = json_load(v.check_hash(root / "outputs/decision_research_20260926/joint_profile_configuration.json", GRID_HASH))
    require(grid["families"] == FAMILIES and grid["labels"] == v.LABELS, "frozen family mapping differs")
    require(RECOVERY_RELATIVE in v.DEPENDENCIES, "original recovery metadata pin missing")
    recovery_payload = pinned_dependency_bytes(root, RECOVERY_RELATIVE, v.DEPENDENCIES[RECOVERY_RELATIVE])
    recovery = json_load(recovery_payload)
    records = {r["name"]: r for r in recovery["records"]}
    require(len(records) == len(recovery["records"]) == 4 and set(records) == set(v.ARCHIVE_HASHES),
            "four-archive recovery inventory differs")
    count, sjvf, inventory = 0, None, []
    for name, expected in v.ARCHIVE_HASHES.items():
        payload = v.check_hash(inputs / name, expected)
        require(records[name]["sha256"] == expected and records[name]["bytes"] == len(payload),
                "archive recovery identity differs")
        members = archive_bytes(payload, records[name]["members"])
        item = {"archive": name, "bytes": len(payload), "sha256": expected,
                "members": [{"name": key, "bytes": len(value), "sha256": v.digest(value)}
                            for key, value in members.items()]}
        if name == "sourcecmb82.zip" and "EPA-CMB82DLLsrc.zip" in members:
            with ZipFile(BytesIO(members["EPA-CMB82DLLsrc.zip"])) as nested:
                source = nested.read("CMB82a.for")
            item["inspected_native_source"] = {
                "path": "sourcecmb82.zip/EPA-CMB82DLLsrc.zip/CMB82a.for", "bytes": len(source),
                "sha256": v.digest(source), "used_for": "Method inspection only; not executed or redistributed."}
        inventory.append(item)
        count += len(members)
        if name == "sjvf_data.zip":
            sjvf = members
    require(count == 39 and sjvf is not None, "39 original archive members required")
    receptors, profiles = parse_native(sjvf)
    if include_metadata:
        metadata = {"archive_inventory": inventory,
                    "recovery_verification": {"status": "PASS", "archives_checked": 4,
                        "members_checked": 39, "recovery_record_sha256": v.digest(recovery_payload),
                        "performed_before_fitting": True},
                    "input_summary": {"receptor_rows_in_archive": len(v.table(sjvf["ADsjvf.txt"])),
                        "fine_profiles_in_archive": len(profiles), "fresno_fine_samples": 35,
                        "species": v.SPECIES, "initial_source_ids": v.SOURCES,
                        "alternatives": {key: value[1:] for key, value in FAMILIES.items()},
                        "species_arrays_2_and_4_identical": True},
                    "validated_receptor_species_pairs": 35 * len(v.SPECIES),
                    "validated_profile_species_pairs": len({s for t in profile_grid() for s in t}) * len(v.SPECIES)}
        return receptors, profiles, metadata
    return receptors, profiles


def scientific():
    return {"samples": 35, "tuples_per_sample": 120, "species": v.SPECIES,
            "source_slots": v.SOURCES, "family_names": [v.LABELS[s] for s in v.SOURCES],
            "families": FAMILIES, "k": 2, "profile_mode": "joint_intervals", "mass_mode": "none",
            "nonnegative_contributions": True, "source_pruning": False,
            "delta": "1/10000000 * max(1, TMAC); strict greater-than",
            "receptor_filter": {"ID": "FRESNO", "SIZE": "FINE"},
            "source_selector": {"member": "PRsjvf.sel", "column": 22, "id_field": 1},
            "species_selector": {"member": "SPsjvf.sel", "column": 20, "identical_column": 24}}


def tuple_model(receptor, profiles, chosen):
    require(chosen in profile_grid() and len(chosen) == 7, "unapproved complete historical tuple")
    aliased = {slot: profiles[sid] for slot, sid in zip(v.SOURCES, chosen)}
    for sid, row in zip(chosen, aliased.values()):
        require(row["SID"] == sid and row["SIZE"] == "FINE", "wrong profile record mapping")
    model = v.reconstruct_model(receptor, aliased, v.SOURCES, 2, "joint_intervals", "none")
    model["sources"] = list(chosen)
    return model


def metadata_check(inputs, root=ROOT, max_seconds=600):
    started = time.monotonic()
    receptors, profiles = load_original_inputs(inputs, root)
    hashes = []
    for receptor in receptors:
        for chosen in profile_grid():
            require(time.monotonic() - started <= max_seconds, "metadata verification time limit")
            hashes.append(v.digest(canonical(tuple_model(receptor, profiles, chosen))))
    return {"status": "PASS", "archive_count": 4, "archive_members": 39,
            "samples": 35, "profile_tuples": 120, "models_reconstructed_without_solving": len(hashes),
            "ordered_model_sha256": v.digest(canonical(hashes)),
            "sample_order_sha256": v.digest(canonical([{"sample_index": i, "identity": {k: r[k] for k in v.IDENTITY}}
                                                       for i, r in enumerate(receptors)])),
            "tuple_order_sha256": v.digest(canonical(profile_grid())),
            "elapsed_seconds": round(time.monotonic() - started, 3), "LPs_run": 0,
            "historical_private_inputs": 0}


def expected_descriptors(receptors, profiles, max_seconds=600):
    started = time.monotonic()
    descriptors = []
    for i, receptor in enumerate(receptors):
        for j, chosen in enumerate(profile_grid()):
            require(time.monotonic() - started <= max_seconds, "model reconstruction time limit")
            digest = v.digest(canonical(tuple_model(receptor, profiles, chosen)))
            descriptors.append({"sample_index": i, "tuple_index": j,
                                "model_key": f"s{i:02d}_t{j:03d}", "model_sha256": digest,
                                "case_file": f"cases/m_{i:02d}_{j:03d}_{digest[:12]}.json"})
    return descriptors


def verify_model_manifest(manifest, receptors, profiles, max_seconds=600):
    """Exact scope is reconstructed; published outcomes never select samples."""
    samples = [{"sample_index": i, "identity": {k: r[k] for k in v.IDENTITY}}
               for i, r in enumerate(receptors)]
    tuples = profile_grid()
    require(manifest["samples"] == samples, "manifest sample omission/reorder/identity")
    require(manifest["tuples"] == tuples, "manifest tuple universe/order differs")
    descriptors = expected_descriptors(receptors, profiles, max_seconds)
    require(manifest["models"] == descriptors, "model descriptors not original exact models")
    expected = {"sample_order_sha256": v.digest(canonical(samples)),
                "tuple_order_sha256": v.digest(canonical(tuples)),
                "ordered_model_sha256": v.digest(canonical([r["model_sha256"] for r in descriptors]))}
    require(manifest["metadata_digests"] == expected, "pre-solve metadata digest differs")
    return descriptors, expected


def inspect_complete(model, result, prior_possible, completion, attempt, counts):
    """Verify original objectives first, and a separate exact fallback second."""
    require(attempt in ("NOT_ATTEMPTED", "DERIVED"), "complete case cannot hide fallback error")
    co = result["co_leaders"]
    require(set(co) == set(model["names"][:len(co)]), "non-prefix co-leader search")
    # Canonical JSON sorts object keys. Restore the independently fixed prefix,
    # not producer-supplied order; all coefficient/list row order is unchanged.
    restored = dict(result)
    restored["co_leaders"] = {name: co[name] for name in model["names"] if name in co}
    base, calls = u.inspect_saved(model, restored, prior_possible, counts)
    route = "OBJECTIVE" if base["unique"] else None
    feasible_names = [name for name in model["names"] if co.get(name, {}).get("status") == "EXACT_FEASIBLE"]
    eligible = (not base["unique"] and base["status"] == "EXACT_COMPATIBLE"
                and len(co) == model["n"] and len(feasible_names) == 1
                and all(info["status"] == ("EXACT_FEASIBLE" if name == feasible_names[0] else "EXACT_INFEASIBLE")
                        for name, info in co.items()))
    require((attempt == "DERIVED") == eligible, "fallback eligibility/attempt mismatch")
    if eligible:
        require(completion is not None, "missing prospective Farkas fallback")
        delta = Q(1, 10_000_000) * max(Q(1), model["mass"])
        independent = f.derive_component(model, restored, delta)
        require(v.encode(independent) == completion, "Farkas fallback algebra/premises mismatch")
        counts["fallback_components"] += 1
        counts["fallback_bounds"] += len(independent["bounds"])
        if independent["all_margins_above_delta"]:
            base["unique"] = [independent["leader"]]
            route = "FARKAS"
    else:
        require(completion is None, "unnecessary/ineligible Farkas record")
    base["margin_route"] = route
    return base, calls


def conclusion(descriptions, total=120):
    require(type(total) is int and total > 0 and len(descriptions) <= total, "invalid union coverage")
    if descriptions:
        return u.expected_conclusion(descriptions, total)
    return {"status": "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION", "possible_co_leaders_lower_bound": [],
            "unique_union_leader": None, "systems_covered": 0, "system_universe": total,
            "all_systems_visited": False, "full_possible_leader_set_claimed": False,
            "full_contribution_ranges_computed": False}


def unresolved_description():
    return {"status": "NUMERICALLY_UNRESOLVED", "possible": [], "unique": [],
            "exhaustive_model_decisions": False, "margin_route": None}


def integer(value, lower=0, upper=None):
    require(type(value) is int and value >= lower and (upper is None or value <= upper), "invalid integer/counter")
    return value


def utc(value):
    moment = datetime.fromisoformat(value)
    require(moment.tzinfo is not None, "timezone-aware timestamp required")
    return moment


def safe_file(directory, relative):
    require(isinstance(relative, str) and relative and "\\" not in relative and ":" not in relative,
            "invalid relative record path")
    parts = relative.split("/")
    require(all(part not in ("", ".", "..") for part in parts), "unsafe record path")
    directory = Path(directory).resolve()
    path = directory.joinpath(*parts)
    require(path.resolve().is_relative_to(directory) and not path.is_symlink(), "record escapes run directory")
    require(all(not directory.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts))),
            "symlinked record ancestor")
    return path


def verify_inventory(directory, output):
    """Check terminal byte freeze before reading any scientific case record."""
    rows = output["files"]
    paths = [row["path"] for row in rows]
    require(len(paths) == len(set(paths)) and "output_manifest.json" not in paths,
            "duplicate/self-including output inventory")
    require({"manifest.json", "preflight.json", "run_started.json", "events.jsonl", "index.json"}.issubset(paths),
            "incomplete terminal output inventory")
    for row in rows:
        path = safe_file(directory, row["path"])
        payload = v.check_hash(path, row["sha256"])
        require(integer(row["bytes"]) == len(payload), "output byte count mismatch")
    actual = {p.relative_to(directory).as_posix() for p in Path(directory).rglob("*") if p.is_file()}
    require(actual - {"output_manifest.json", "independent_verification.json"} == set(paths),
            "unlisted/missing run files")
    return set(paths)


def inventory_reader(directory, output):
    """Consume the same hashed bytes that the immutable inventory identifies."""
    records = {row["path"]: row for row in output["files"]}
    def read(relative):
        require(relative in records, "consumed record absent from terminal inventory")
        record = records[relative]
        payload = v.check_hash(safe_file(directory, relative), record["sha256"])
        require(integer(record["bytes"]) == len(payload), "consumed record byte count mismatch")
        return payload
    return read


def finite(value, lower=0, upper=None):
    require(type(value) in (int, float) and math.isfinite(value) and value >= lower
            and (upper is None or value <= upper), "invalid finite time/budget")
    return value


def verify_events(payload, budgets):
    """Replay the journal's state machine, not just self-reported totals."""
    require(payload.endswith(b"\n"), "partial final journal line")
    lines = payload.splitlines()
    require(bool(lines) and all(line.strip() for line in lines), "empty journal/line")
    maximum_models = integer(budgets["max_models"], 1, 4200)
    maximum_calls = integer(budgets["max_lp_calls"], 1, 20000)
    duration = finite(budgets["elapsed_seconds"], 0, 7200)
    require(duration > 0, "positive elapsed budget required")
    deadline = utc(budgets["deadline_utc"]) if budgets.get("deadline_utc") else None
    events = [json_load(line) for line in lines]
    require(events[0]["event"] == "RUN_START" and events[-1]["event"] == "RUN_END",
            "journal missing start or terminal closure")
    models = calls = invocations = aborted = 0
    active = open_call = None
    previous_elapsed = 0
    previous_utc = None
    stopped = False
    spans, lp_records = {}, {}
    for seq, event in enumerate(events):
        require(integer(event["seq"]) == seq, "journal sequence omission/reorder")
        elapsed = finite(event["elapsed_seconds"])
        require(elapsed >= previous_elapsed, "elapsed clock moved backwards")
        stamp = utc(event["utc"])
        require(previous_utc is None or stamp >= previous_utc, "UTC journal moved backwards")
        older_elapsed, older_utc = previous_elapsed, previous_utc
        previous_elapsed, previous_utc = elapsed, stamp
        kind, key = event["event"], event["model_key"]
        if kind in ("MODEL_BEGIN", "LP_BEGIN"):
            admission = finite(event["admission_gate_elapsed_seconds"])
            admission_utc = utc(event["admission_gate_utc"])
            require(older_elapsed <= admission <= elapsed and admission < duration
                    and (older_utc is None or older_utc <= admission_utc) and admission_utc <= stamp
                    and (deadline is None or admission_utc < deadline), "attempt admitted outside time budget")
        if kind == "RUN_START":
            require(seq == 0 and key is None, "duplicate run start")
        elif kind == "MODEL_BEGIN":
            require(not stopped and active is None and open_call is None and isinstance(key, str)
                    and key not in spans, "invalid or duplicate model start")
            models += 1
            require(models <= maximum_models, "model budget exceeded")
            active = key
            spans[key] = {"begin": seq, "end": None, "calls_before": calls, "calls_after": None}
        elif kind == "LP_BEGIN":
            require(not stopped and active is not None and key == active and open_call is None,
                    "LP outside model or overlapping another call")
            calls += 1
            require(integer(event["call_id"], 1) == calls <= maximum_calls, "LP identity/charge/limit failure")
            remaining = finite(event["remaining_seconds"])
            require(remaining > 0 and remaining <= duration - admission + 1e-8,
                    "LP remaining-time allowance exceeds elapsed budget")
            require(deadline is None or remaining <= (deadline - admission_utc).total_seconds() + 1e-6,
                    "LP exceeds operational deadline")
            require(event["method"] in ("highs-ds", "highs-ipm", "highs"), "undeclared solver method")
            open_call = calls
            lp_records[calls] = {"model_key": key, "begin": seq, "end": None, "outcome": None}
        elif kind in ("LP_END", "LP_ERROR"):
            require(open_call is not None and integer(event["call_id"], 1) == open_call
                    and key == active, "LP completion without matching charged begin")
            if kind == "LP_END":
                integer(event["solver_status"], 0, 4)
                require(event["invocation_attempted"] is True, "LP result without invocation attempt")
            else:
                require(type(event["invocation_attempted"]) is bool
                        and event["charged_but_not_invoked"] is (not event["invocation_attempted"]),
                        "aborted invocation accounting ambiguous")
            if event["invocation_attempted"]:
                begin = events[lp_records[open_call]["begin"]]
                dispatch = finite(event["dispatch_gate_elapsed_seconds"])
                dispatch_utc = utc(event["dispatch_gate_utc"])
                left = finite(event["dispatch_remaining_seconds"])
                allowance = finite(event["solver_time_limit_seconds"])
                require(begin["elapsed_seconds"] <= dispatch <= elapsed and dispatch < duration
                        and utc(begin["utc"]) <= dispatch_utc <= stamp,
                        "invocation gate outside live time budget")
                require(0 < allowance <= left and 0 < left <= duration - dispatch + 1e-8,
                        "solver granted stale pre-flush time allowance")
                require(deadline is None or (dispatch_utc < deadline
                        and left <= (deadline - dispatch_utc).total_seconds() + 1e-6),
                        "invocation gate exceeded operational deadline")
            else:
                require(not any(key in event for key in ("dispatch_gate_elapsed_seconds", "dispatch_remaining_seconds",
                                                        "dispatch_gate_utc", "solver_time_limit_seconds")),
                        "aborted call has invocation allowance")
            invocations += int(event["invocation_attempted"])
            aborted += int(not event["invocation_attempted"])
            lp_records[open_call].update({"end": seq, "outcome": kind})
            open_call = None
        elif kind == "MODEL_END":
            require(active is not None and key == active and open_call is None, "model end before LP closure")
            spans[key].update({"end": seq, "calls_after": calls})
            active = None
        elif kind == "RUN_STOP":
            require(not stopped and isinstance(event["reason"], str) and event["reason"], "invalid repeated stop")
            require(key == active, "stop model identity mismatch")
            stopped = True
        elif kind == "RUN_END":
            require(seq == len(events) - 1 and active is None and open_call is None and key is None,
                    "run closed with unfinished model/LP")
        else:
            require(False, "unknown journal event")
        require(integer(event["models_started"]) == models and integer(event["lp_calls"]) == calls,
                "journal cumulative counters do not replay")
    require(all(span["end"] is not None for span in spans.values()), "unclosed model attempt")
    return {"events": events, "model_spans": spans, "lp_records": lp_records,
            "models_started": models, "lp_calls": calls, "stopped": stopped,
            "solver_invocation_attempts": invocations, "precall_aborted": aborted,
            "elapsed_seconds": previous_elapsed}


def verify_budget_snapshot(snapshot, budgets, journal, minimum_elapsed=0):
    for key in ("models_started", "lp_calls", "solver_invocation_attempts", "precall_aborted"):
        require(integer(snapshot[key]) == journal[key], "final budget counter mismatch")
    require(snapshot["solver_invocation_attempts"] + snapshot["precall_aborted"] == snapshot["lp_calls"],
            "charged attempts lost or double-counted")
    require(snapshot["lp_counter_semantics"] == "charged attempts, including explicit pre-invocation aborts",
            "budget counters mislabelled as exact solver invocations")
    require(snapshot["max_models"] == budgets["max_models"] and snapshot["max_lp_calls"] == budgets["max_lp_calls"]
            and snapshot["elapsed_limit_seconds"] == budgets["elapsed_seconds"]
            and snapshot["deadline_utc"] == budgets["deadline_utc"], "operational ceilings changed")
    require(finite(snapshot["elapsed_seconds"]) >= minimum_elapsed, "budget elapsed time moved backwards")


def verify_dependencies(manifest, root=ROOT):
    dependencies = manifest["dependencies"]
    require(manifest["approved_dependency_byte_variants"] == APPROVED_DEPENDENCY_BYTE_VARIANTS,
            "undeclared/broadened dependency byte exception")
    require(manifest["inputs"]["recovery_verification"]["recovery_record_sha256"] ==
            dependencies.get(RECOVERY_RELATIVE), "dependency and consumed recovery-byte provenance differ")
    required = {**v.DEPENDENCIES,
                **{"scripts/" + key: value for key, value in FROZEN_VERIFIERS.items()},
                "scripts/audit_interval_profile_union.py": "d02e65ad5799f82b8960276d3c9eeee1e43c31cbcc78faddc22924d7431ff21b",
                "scripts/audit_interval_farkas_margin.py": "b5a95a583c533e9dd28cccd6a2737de1bf4b06425b986cad2b20510fe84f54a0",
                "outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md":
                "7fede98bd7f789ba8f228667912be15c80e592195b508859c4ca01fecfd8078e",
                "outputs/decision_research_20260926/joint_profile_configuration.json": GRID_HASH,
                "outputs/decision_research_20260926/COLD_RUN_REPRODUCTION_PROPOSAL.md":
                "d83392e843e409aade87a3dfd050c0da81448fcf9720be3dc828cd17820f9dca"}
    for relative, expected in required.items():
        if relative == RECOVERY_RELATIVE:
            require(dependencies.get(relative) in RECOVERY_HASHES, "recovery dependency is not a reviewed byte form")
        else:
            require(dependencies.get(relative) == expected, "frozen dependency missing or altered: " + relative)
    new_required = ("scripts/reproduce_interval_union.py", "scripts/verify_cold_interval_union.py",
                    "tests/test_cold_interval_union.py", "tests/test_cold_interval_union_records.py",
                    "outputs/decision_research_20260926/COLD_RUN_ROOT_DECISION.md",
                    "outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md",
                    "outputs/decision_research_20260926/COLD_RUN_RECORD_SCHEMA.md")
    require(all(path in dependencies for path in new_required), "new implementation/schema dependency missing")
    for relative, expected in dependencies.items():
        require(relative.split("/")[0] in ("scripts", "tests", "outputs") and "private" not in relative.split("/"),
                "historical private dependency prohibited")
        v.check_hash(safe_file(root, relative), expected)


def verify_run(directory, inputs, max_seconds=1200, root=ROOT):
    started = time.monotonic()
    def remaining():
        left = max_seconds - (time.monotonic() - started)
        require(left > 0, "independent replay time budget exhausted")
        return left
    directory, root = Path(directory), Path(root).resolve()
    require(directory.is_dir() and not directory.is_symlink(), "missing/symlinked new run directory")
    directory = directory.resolve()
    terminal_payload = safe_file(directory, "output_manifest.json").read_bytes()
    output = json_load(terminal_payload)
    paths = verify_inventory(directory, output)
    read = inventory_reader(directory, output)
    payload = read("manifest.json")
    mh = v.digest(payload)
    manifest = json_load(payload)
    require(manifest["schema"] == "cold_interval_union_v1" and output["schema"] == manifest["schema"], "schema mismatch")
    require(isinstance(manifest["run_id"], str) and manifest["run_id"] and output["run_id"] == manifest["run_id"]
            and output["manifest_sha256"] == mh, "terminal run identity mismatch")
    require(manifest["output_relative"].split("/")[0] == "private"
            and len(manifest["output_relative"].split("/")) == 2, "not a newly named private output")
    verify_dependencies(manifest, root)
    receptors, profiles, input_metadata = load_original_inputs(inputs, root, include_metadata=True)
    require(manifest["scientific"] == scientific(), "scientific scope changed")
    require(manifest["inputs"] == input_metadata, "original input inventory or selector metadata differs")
    descriptors, metadata_digests = verify_model_manifest(manifest, receptors, profiles, remaining())
    descriptor_map = {(row["sample_index"], row["tuple_index"]): row for row in descriptors}
    preflight = json_load(read("preflight.json"))
    require(preflight["schema"] == manifest["schema"] and preflight["manifest_sha256"] == mh
            and preflight["exclusive_write_probe"] is True and preflight["field_lp_calls"] == 0
            and preflight["planned_files"] == 4206 and 0 < preflight["maximum_full_path_length"] <= 240,
            "no-LP preflight/path gate missing")
    require(preflight["metadata"] == {"status": "METADATA_ONLY_NO_LP", "archives": 4, "members": 39,
                                      "samples": 35, "tuples": 120, "models": 4200, **metadata_digests},
            "preflight model metadata differs")
    start = json_load(read("run_started.json"))
    index = json_load(read("index.json"))
    for record in (start, index):
        require(record["schema"] == manifest["schema"] and record["run_id"] == manifest["run_id"]
                and record["manifest_sha256"] == mh, "run record identity mismatch")
    require(start["explicit_execution_acknowledgment"] is True, "no execution acknowledgment")
    require(utc(manifest["created_utc"]) <= utc(start["started_utc"]) <= utc(index["started_utc"])
            <= utc(index["completed_utc"]), "freeze/run chronology differs")
    for key in ("models_started", "lp_calls", "solver_invocation_attempts", "precall_aborted"):
        require(integer(start["budget"][key]) == 0, "numerical work before start record")
    zero = {key: 0 for key in ("models_started", "lp_calls", "solver_invocation_attempts", "precall_aborted")}
    verify_budget_snapshot(start["budget"], manifest["budgets"], zero)
    journal = verify_events(read("events.jsonl"), manifest["budgets"])
    run_status = index["run_status"]
    require(run_status in ("COMPLETE", "COMPLETE_WITH_HOLDS", "STOPPED_BUDGET", "STOPPED_INTERRUPT", "STOPPED_ERROR"),
            "unknown run status")
    require(output["run_status"] == run_status == journal["events"][-1]["run_status"], "run closure status differs")
    require(journal["stopped"] == run_status.startswith("STOPPED_"), "stop state hidden or fabricated")
    require((index["stop_reason"] is None) == (not journal["stopped"]), "stop reason missing/unexpected")
    if journal["stopped"]:
        require([e["reason"] for e in journal["events"] if e["event"] == "RUN_STOP"] == [index["stop_reason"]], "stop reasons disagree")
    verify_budget_snapshot(index["budget"], manifest["budgets"], journal, journal["elapsed_seconds"])
    verify_budget_snapshot(output["budget"], manifest["budgets"], journal, index["budget"]["elapsed_seconds"])
    rows = index["samples"]
    require([integer(row["sample_index"], 0, 34) for row in rows] == list(range(35)), "35 sample rows omitted/reordered")
    counts, all_visits, case_paths, outcomes = Counter(), [], set(), []
    for i, row in enumerate(rows):
        remaining()
        visits = row["visits"]
        require([integer(visit["tuple_index"], 0, 119) for visit in visits] == list(range(len(visits))), "tuple prefix omitted/reordered")
        require(row["unvisited_tuple_indices"] == list(range(len(visits), 120)), "unvisited tuple accounting differs")
        descriptions = []
        for j, visit in enumerate(visits):
            remaining()
            require(conclusion(descriptions)["status"] != "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER", "continued after exact ambiguity")
            descriptor = descriptor_map[i, j]
            key = descriptor["model_key"]
            require(visit["model_key"] == key and visit["case_file"] == descriptor["case_file"], "visit model/path identity differs")
            require(key in journal["model_spans"], "case without journaled model attempt")
            span = journal["model_spans"][key]
            if visit["completion"] != "COMPLETE" or visit["case_write_complete"] is not True:
                require(key == list(journal["model_spans"])[-1], "scientific work continued after incomplete/error case")
            all_visits.append((i, j, key))
            case_paths.add(visit["case_file"])
            if visit["case_write_complete"] is False:
                require(visit["case_sha256"] is None and visit["completion"] == "ERROR"
                        and run_status == "STOPPED_ERROR", "failed-write claim not conservative")
                expected = unresolved_description()
                counts["unverified_failed_case_writes"] += 1
            else:
                require(visit["case_write_complete"] is True, "ambiguous write-completion flag")
                case_payload = read(visit["case_file"])
                require(v.digest(case_payload) == visit["case_sha256"], "visit/terminal case identity differs")
                case = json_load(case_payload)
                require(case["schema"] == manifest["schema"] and case["run_id"] == manifest["run_id"]
                        and case["manifest_sha256"] == mh, "case run identity differs")
                require(all(case[k] == value for k, value in descriptor.items()), "case descriptor differs")
                model = tuple_model(receptors[i], profiles, manifest["tuples"][j])
                require(case["model"] == v.encode(model) and v.digest(canonical(model)) == descriptor["model_sha256"],
                        "stored matrix not original exact-decimal model")
                prior = sorted({name for d in descriptions for name in d["possible"]})
                require(case["prior_possible"] == prior, "prior witness provenance differs")
                require(case["calls_before"] == span["calls_before"] and case["calls_after"] == span["calls_after"]
                        and case["event_seq_begin"] == span["begin"] and case["event_seq_end"] == span["end"],
                        "case/journal span or charges differ")
                require(case["completion"] == visit["completion"] == journal["events"][span["end"]]["completion"], "completion states differ")
                if case["completion"] == "COMPLETE":
                    require(case["result"] is not None, "complete case has no proof result")
                    expected, calls = inspect_complete(model, case["result"], prior,
                        case["farkas_completion"], case["farkas_attempt"], counts)
                    require(calls == span["calls_after"] - span["calls_before"], "complete proof call structure differs")
                    counts["completed_models"] += 1
                else:
                    require(case["completion"] in ("STOPPED", "ERROR") and run_status.startswith("STOPPED_"),
                            "unfinished case hidden in complete run")
                    require(case["farkas_completion"] is None, "stopped model retained promotable fallback")
                    expected = unresolved_description()
                    if case["result"] is not None:
                        restored = dict(case["result"])
                        co = restored["co_leaders"]
                        require(set(co) == set(model["names"][:len(co)]), "interrupted returned result has wrong prefix")
                        restored["co_leaders"] = {name: co[name] for name in model["names"] if name in co}
                        _, calls = u.inspect_saved(model, restored, prior, counts)
                        require(calls == span["calls_after"] - span["calls_before"], "returned-but-stopped proof charges differ")
                    counts["unverified_stopped_models"] += 1
                require(case["description"] == expected, "case conclusion not implied by exact proof")
            require(visit["description"] == expected, "visit changed its case outcome")
            descriptions.append(expected)
        outcome = conclusion(descriptions)
        require(row["conclusion"] == outcome, "sample union claim not implied by coverage/proofs")
        if not run_status.startswith("STOPPED_"):
            require(len(visits) == 120 or outcome["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER",
                    "completed run stopped early without ambiguity proof")
        outcomes.append(outcome)
    central = [(i, 0, row["visits"][0]["model_key"]) for i, row in enumerate(rows) if row["visits"]]
    require([i for i, _, _ in central] == list(range(len(central))), "central pass skipped a sample")
    rest = [(i, j, key) for i, j, key in all_visits if j > 0]
    require(not rest or len(central) == 35, "tuple enumeration preceded complete central pass")
    for i, _, _ in rest:
        require(all(len(rows[earlier]["visits"]) == 120 or
                    outcomes[earlier]["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER"
                    for earlier in range(i)), "second pass skipped an unfinished earlier sample")
    expected_order = [key for _, _, key in central + rest]
    require(list(journal["model_spans"]) == expected_order, "model execution order differs from fixed two-pass plan")
    require(len(all_visits) == journal["models_started"] and set(expected_order) == set(journal["model_spans"]),
            "attempted case or model lost")
    require({path for path in paths if path.startswith("cases/")} == {p for p in case_paths if safe_file(directory, p).exists()},
            "extra/orphan case record")
    holds = any(o["status"].startswith("HOLD") for o in outcomes)
    if not journal["stopped"]:
        require(run_status == ("COMPLETE_WITH_HOLDS" if holds else "COMPLETE"), "numerical HOLDs hidden in run status")
    remaining()
    # Confirm immutable case/index bytes and code still match after the replay.
    verify_inventory(directory, output)
    require(safe_file(directory, "output_manifest.json").read_bytes() == terminal_payload, "terminal inventory changed during replay")
    verify_dependencies(manifest, root)
    return {"status": "PASS", "run_status": run_status, "completed_utc": datetime.now(timezone.utc).isoformat(),
            "manifest_sha256": mh, "output_manifest_sha256": v.digest(terminal_payload),
            "verifier_sha256": v.digest(Path(__file__).read_bytes()), "all_samples": 35,
            "models_reconstructed_without_solving": 4200, "metadata_digests": metadata_digests,
            "sample_status_counts": dict(Counter(o["status"] for o in outcomes)),
            "proof_counts": dict(counts), "model_attempts_verified": journal["models_started"],
            "charged_LP_attempts_verified": journal["lp_calls"],
            "solver_invocation_attempts_recorded": journal["solver_invocation_attempts"],
            "preinvocation_aborts_recorded": journal["precall_aborted"], "LPs_run_by_verifier": 0,
            "historical_private_inputs": 0, "elapsed_seconds": round(time.monotonic() - started, 3),
            "limits": "New-run exact conditional proof replay, not historical byte reproduction, confidence coverage, or environmental truth."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--metadata-only", action="store_true")
    modes.add_argument("--run-directory", type=Path)
    parser.add_argument("--max-seconds", type=float, default=1200)
    parser.add_argument("--check-only", action="store_true", help="Replay without writing verification metadata")
    args = parser.parse_args()
    require(0 < finite(args.max_seconds) <= 1800, "replay budget outside approved bound")
    if args.metadata_only:
        require(not args.check_only, "metadata-only already writes nothing")
        result = metadata_check(args.inputs, max_seconds=args.max_seconds)
    else:
        destination = args.run_directory / "independent_verification.json"
        require(args.check_only or not destination.exists(), "verification output exists; use --check-only")
        result = verify_run(args.run_directory, args.inputs, args.max_seconds)
        if not args.check_only:
            with destination.open("xb") as stream:
                stream.write(canonical(result))
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
