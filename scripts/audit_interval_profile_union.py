#!/usr/bin/env python3
"""Approved bounded lazy proof audit over 120 actual historical profile systems.

All35 samples accounted; only four Stage2 undecided union cases receive new LPs.
Independent boxes, k2, original full seven families, no mass assumption. The
reviewed Stage2 producer is imported read-only; every solver call is budgeted.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

import audit_interval_decisions as core

ROOT, PUBLIC, PRIVATE = core.ROOT, core.PUBLIC, core.PRIVATE
CONFIG = PUBLIC / "interval_union_configuration_v2.json"
MANIFEST = PRIVATE / "interval_union_candidates_v2.json"
PROTOCOL = PUBLIC / "interval_stage3_protocol_PROPOSED.md"
PROTOCOL_HASH = "4c3166d1b4dcd3d20a78f4269f8022ee81faf1420a830976ac49a213270bb77e"
INDEX_HASH = "381d20db9a35e1e8a725b535b588a60291def382a6f3196a10ef4a4302b66d40"
CORE_HASH = "ecb4e8f01f4028eb0a43d85870b3f458b75fce91d8bad9bdddaa815c3597da93"
GRID_HASH = "f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314"
CUTOFF = datetime(2026, 9, 27, 5, 0, tzinfo=timezone.utc)
SLOTS = list(core.native.CONFIG["central_initial_sources"])
PRIOR_CONFIG = PUBLIC / "interval_union_configuration.json"
PRIOR_CALLS_RESERVED = 27  # Worst case: feasibility1 + 7joint tests*2 + 6bounds*2.


def sha(path):
    return core.native.sha256(Path(path).read_bytes())


def write_json(path, obj):
    Path(path).write_bytes(core.native.json_bytes(core.encode_q(obj)))


def case_path(model_hash):
    # Windows' host filesystem rejects the original long filename at this depth.
    return PRIVATE / "interval_union_cases" / ("u_" + model_hash + ".json")


class BudgetExceeded(Exception):
    """Not RuntimeError: the frozen solver wrapper must not swallow this stop."""


class SolverBudget:
    def __init__(self, maximum=20000, seconds=7200, cutoff=CUTOFF,
                 monotonic=time.monotonic, utc=lambda: datetime.now(timezone.utc)):
        self.maximum, self.seconds, self.cutoff = maximum, seconds, cutoff
        self.clock, self.utc, self.started = monotonic, utc, monotonic()
        self.calls = 0
        self.original = None

    def remaining(self):
        if self.calls >= self.maximum:
            raise BudgetExceeded("LP_CALL_LIMIT")
        remaining = min(self.seconds - (self.clock() - self.started), (self.cutoff - self.utc()).total_seconds())
        if remaining <= 0:
            raise BudgetExceeded("TIME_OR_QA_CUTOFF")
        return remaining

    def call(self, *args, **kwargs):
        remaining = self.remaining()
        self.calls += 1
        options = dict(kwargs.get("options", {}))
        options["time_limit"] = min(remaining, options.get("time_limit", remaining))
        kwargs["options"] = options
        return self.original(*args, **kwargs)

    def __enter__(self):
        self.original = core.linprog
        core.linprog = self.call
        return self

    def __exit__(self, *_):
        core.linprog = self.original


def profile_grid(families):
    return [list(t) for t in itertools.product(*(families.get(s, [s]) for s in SLOTS))]


def tuple_model(receptor, profiles, chosen):
    if len(chosen) != len(SLOTS):
        raise ValueError("incomplete profile tuple")
    # Each complete source record (both mean and uncertainty) moves as one unit.
    aliased = {slot: profiles[sid] for slot, sid in zip(SLOTS, chosen)}
    model = core.field_model(receptor, aliased, SLOTS, 2, "joint_intervals", "none")
    model["sources"] = list(chosen)
    return model


def inherited_description(case):
    result = case["result"]
    return {"status": result["overall_status"],
            "possible": result.get("exact_possible_co_leaders", []),
            "unique": result.get("verified_unique_leaders_above_margin_threshold", []),
            "exhaustive_model_decisions": True}


def conclusion(descriptions, total_systems):
    possible = sorted({name for d in descriptions for name in d["possible"]})
    covered = len(descriptions)
    if covered > total_systems:
        raise ValueError("duplicate/excess model descriptions")
    complete = covered == total_systems
    if len(possible) >= 2:
        status, winner = "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER", None
    elif complete and all(d["status"] == "EXACT_INFEASIBLE" for d in descriptions):
        status, winner = "EXACT_EMPTY_UNION", None
    else:
        feasible = [d for d in descriptions if d["status"] == "EXACT_COMPATIBLE"]
        winner = possible[0] if len(possible) == 1 else None
        if (complete and winner and feasible
                and all(d["status"] in ("EXACT_COMPATIBLE", "EXACT_INFEASIBLE") for d in descriptions)
                and all(d["unique"] == [winner] for d in feasible)):
            status = "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN"
        else:
            status, winner = "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION", None
    return {"status": status, "possible_co_leaders_lower_bound": possible, "unique_union_leader": winner,
            "systems_covered": covered, "system_universe": total_systems,
            "all_systems_visited": complete,
            "full_possible_leader_set_claimed": False,
            "full_contribution_ranges_computed": False}


def inspect_model(model, already_possible):
    result = {"feasibility": core.feasibility(model), "co_leaders": {}, "leader_bounds": {},
              "co_leader_search_complete": False, "verified_unique_leaders_above_margin_threshold": []}
    feasibility = result["feasibility"]
    if feasibility["status"] != "EXACT_FEASIBLE":
        result["overall_status"] = feasibility["status"]
        return result
    result["overall_status"] = "EXACT_COMPATIBLE"
    possible = set(already_possible)
    for j, name in enumerate(model["names"]):
        info = core.feasibility(core.co_leader_model(model, j))
        result["co_leaders"][name] = info
        if info["status"] == "EXACT_FEASIBLE":
            possible.add(name)
        if len(possible) >= 2:
            result["stopping_reason"] = "SECOND_UNION_CO_LEADER_WITNESS"
            return result
    result["co_leader_search_complete"] = True
    if len(possible) == 1:
        leader = next(iter(possible))
        a = model["names"].index(leader)
        threshold = Q(1, 10_000_000) * max(Q(1), model["mass"])
        result["near_zero_threshold"] = threshold
        for j, other in enumerate(model["names"]):
            if j == a:
                continue
            q = [Q(int(i == a) - int(i == j)) for i in range(model["n"])]
            result["leader_bounds"][other] = core.objective_bound(model, q, feasibility["primal"]["point"])
        if all(info["status"] == "VERIFIED_BOUND_AND_WITNESS"
               and info["verified_lower_bound"] > threshold for info in result["leader_bounds"].values()):
            result["verified_unique_leaders_above_margin_threshold"] = [leader]
        result["candidate_leader"] = leader
    return result


def describe(result):
    return {"status": result["overall_status"],
            "possible": [name for name, info in result["co_leaders"].items() if info["status"] == "EXACT_FEASIBLE"],
            "unique": result["verified_unique_leaders_above_margin_threshold"],
            "exhaustive_model_decisions": result["co_leader_search_complete"]}


def inputs_and_candidates(inputs):
    if sha(PROTOCOL) != PROTOCOL_HASH or sha(core.__file__) != CORE_HASH:
        raise ValueError("approved protocol or frozen producer changed")
    grid_path = PUBLIC / "joint_profile_configuration.json"
    if sha(grid_path) != GRID_HASH or sha(PRIVATE / "interval_index.json") != INDEX_HASH:
        raise ValueError("frozen grid/index changed")
    verification_path = PUBLIC / "interval_certificate_verification.json"
    verification = json.loads(verification_path.read_bytes())
    if (verification["status"] != "PASS" or verification["private_index_sha256"] != INDEX_HASH
            or verification["counts"]["unique_models"] != 492 or verification["counts"]["panel_records"] != 840):
        raise ValueError("complete independent Stage2 verification gate missing")
    metadata, receptors, profiles, _ = core.metadata_audit(inputs, core.configuration())
    families = json.loads(grid_path.read_bytes())["families"]
    tuples = profile_grid(families)
    if len(tuples) != 120 or len({tuple(t) for t in tuples}) != 120 or tuples[0] != SLOTS:
        raise ValueError("historical profile-system universe changed")
    validated = 0
    for sid in sorted({s for t in tuples for s in t}):
        row = profiles[sid]
        if row["SID"] != sid or row["SIZE"] != "FINE":
            raise ValueError("profile particle-size/identity mismatch")
        for name in core.native.CONFIG["species"]:
            f, uf = Q(row[name]), Q(row[name[:-1] + "U"])
            if f < 0 or uf < 0:
                raise ValueError("negative/sentinel alternative profile field")
            validated += 1
    index = json.loads((PRIVATE / "interval_index.json").read_bytes())
    records = [r for r in index["records"] if (r["universe"], r["k"], r["profile_mode"], r["mass_mode"])
               == ("full_seven_primary", 2, "joint_intervals", "none")]
    records.sort(key=lambda r: r["sample_zero_based_index"])
    if [r["sample_zero_based_index"] for r in records] != list(range(35)):
        raise ValueError("all35 central samples not represented one-to-one")
    descriptions, cases = [], {}
    for item in records:
        sid = item["sample_zero_based_index"]
        if any(receptors[sid][key] != value for key, value in item["sample"].items()):
            raise ValueError("central receptor identity changed")
        path = PRIVATE / "interval_cases" / ("interval_case_" + item["model_sha256"] + ".json")
        if sha(path) != item["case_sha256"]:
            raise ValueError("inherited proof hash mismatch")
        case = json.loads(path.read_bytes())
        model = tuple_model(receptors[sid], profiles, SLOTS)
        if core.native.sha256(core.native.json_bytes(core.encode_q(model))) != item["model_sha256"]:
            raise ValueError("central exact model reconstruction differs")
        d = inherited_description(case)
        descriptions.append(d)
        cases[sid] = case
    kinds = Counter("ambiguous" if len(d["possible"]) >= 2 else "unique" if len(d["unique"]) == 1
                    else "infeasible" if d["status"] == "EXACT_INFEASIBLE" else "unexpected" for d in descriptions)
    if dict(kinds) != {"ambiguous": 31, "unique": 2, "infeasible": 2}:
        raise ValueError("approved Stage2 31/2/2 partition differs")
    targets = [r["sample_zero_based_index"] for r, d in zip(records, descriptions) if len(d["possible"]) < 2]
    manifest = {"private_index_sha256": INDEX_HASH, "targets": targets, "records": records,
                "all_profile_tuples": tuples, "central_partition": dict(kinds)}
    metadata.update({"all_alternative_profile_species_pairs_checked": validated,
                     "all_profile_particle_sizes": "FINE", "own_mean_and_uncertainty_per_profile": True,
                     "alternative_family_rules": core.native.CONFIG["alternative_descriptor_rules"],
                     "independent_stage2_verification_sha256": sha(verification_path)})
    return manifest, metadata, receptors, profiles, cases


def freeze(inputs):
    if CONFIG.exists() or MANIFEST.exists():
        raise ValueError("union configuration already frozen; do not overwrite")
    manifest, metadata, receptors, profiles, _ = inputs_and_candidates(inputs)
    path_checks = []
    for sample_id in manifest["targets"]:
        for chosen in manifest["all_profile_tuples"][1:]:
            model_hash = core.native.sha256(core.native.json_bytes(core.encode_q(tuple_model(receptors[sample_id], profiles, chosen))))
            path_probe = case_path(model_hash)
            path_probe.parent.mkdir(exist_ok=True)
            if not path_probe.resolve().is_relative_to(PRIVATE.resolve()) or path_probe.exists():
                raise ValueError("write-path probe outside private workspace or already exists")
            path_probe.write_bytes(b"union write-path preflight only\n")
            if path_probe.read_bytes() != b"union write-path preflight only\n":
                raise ValueError("case write-path roundtrip failed")
            path_checks.append({"model_sha256": model_hash, "path_characters": len(str(path_probe)), "roundtrip": "PASS"})
            path_probe.unlink()  # Exact new marker file; no prior user data.
    preflight = PRIVATE / "interval_union_write_paths_preflight.json"
    write_json(preflight, {"status": "PASS", "all_potential_case_paths": path_checks})
    tests = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests",
                            "-p", "test_interval_profile_union.py", "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("union synthetic gate failed:\n" + tests.stdout + tests.stderr)
    write_json(MANIFEST, manifest)
    prior = json.loads(PRIOR_CONFIG.read_bytes())
    config = {"version": "1.0.1-pathfix", "frozen_utc": core.now(), "scientific_configuration_frozen_before_first_union_field_LP": True,
              "prior_configuration_sha256": sha(PRIOR_CONFIG), "original_scientific_freeze_utc": prior["frozen_utc"],
              "interruption": {"reason": "Post-execution operational correction: solver invoked, then first result write failed on Windows path length; no result persisted/displayed. Only output path and conservative interruption accounting changed.",
                               "prior_unrecorded_LP_calls_charged_upper_bound": PRIOR_CALLS_RESERVED,
                               "prior_model_attempts_charged": 1, "prior_results_available": False,
                               "prior_code_tests_config_preserved": "private/decision_research_20260926/interval_union_pre_pathfix"},
              "root_approval": "Root read approved protocol and authorized gated bounded implementation and execution after complete Stage2 independent PASS; no positive union claim until independent tuple proof replay.",
              "protocol_sha256": PROTOCOL_HASH, "producer_sha256": CORE_HASH,
              "script_sha256": sha(__file__), "tests_sha256": sha(ROOT / "tests/test_interval_profile_union.py"),
              "candidate_manifest_sha256": sha(MANIFEST), "stage2_index_sha256": INDEX_HASH,
              "all476_case_write_paths_preflight_sha256": sha(preflight),
              "grid_configuration_sha256": GRID_HASH, "archive_sha256": core.native.TRUSTED_ARCHIVE_HASHES,
              "scope": {"samples": 35, "inherited_ambiguity": 31, "targeted_samples": 4, "systems_per_sample": 120,
                        "k": 2, "profile_mode": "joint_intervals", "mass_mode": "none", "universe": "full_seven_primary"},
              "budget": {"new_models": 476, "all_numerical_LP_calls": 20000, "wall_seconds": 7200,
                         "absolute_qa_cutoff_utc": CUTOFF.isoformat()},
              "tuple_order": manifest["all_profile_tuples"], "candidate_partition": manifest["central_partition"],
              "stopping": "per sample stop once two distinct exactly witnessed co-leader labels exist; otherwise all120 required for positive or empty certificate",
              "leader_margin": "1e-7*max(1,TMAC), unchanged", "randomness": "none", "metadata": metadata,
              "tests": {"status": "PASS", "exit_code": tests.returncode, "output": tests.stdout + tests.stderr},
              "limits": "Post-Stage2 targeted conditional set-membership audit; no statistical confidence, field truth, full system-distribution characterization, physical profile dependence model, new fit, or manuscript change."}
    write_json(CONFIG, config)
    write_json(PUBLIC / "interval_union_gate.json", {"status": "PASS", "configuration_sha256": sha(CONFIG),
               "script_sha256": config["script_sha256"], "tests_sha256": config["tests_sha256"],
               "candidate_manifest_sha256": sha(MANIFEST), "frozen_utc": config["frozen_utc"]})
    return {"status": "FROZEN_GATE_PASS", "configuration_sha256": sha(CONFIG)}


def run(inputs):
    config = json.loads(CONFIG.read_bytes())
    if (sha(__file__) != config["script_sha256"] or sha(ROOT / "tests/test_interval_profile_union.py") != config["tests_sha256"]
            or sha(MANIFEST) != config["candidate_manifest_sha256"]):
        raise ValueError("union code/tests/manifest differ from pre-solve freeze")
    current, metadata, receptors, profiles, central_cases = inputs_and_candidates(inputs)
    manifest = json.loads(MANIFEST.read_bytes())
    if current != manifest:
        raise ValueError("current candidate manifest differs")
    index_path = PRIVATE / "interval_union_index.json"
    if index_path.exists():
        raise ValueError("completed union run already exists; do not rerun silently")
    case_dir = PRIVATE / "interval_union_cases"
    case_dir.mkdir(exist_ok=True)
    if any(case_dir.iterdir()):
        raise ValueError("prior partial union records exist; preserve and review, do not duplicate")
    started, rows, model_count, stop_reason = core.now(), [], 1, None
    elapsed_since_scientific_freeze = (datetime.now(timezone.utc) - datetime.fromisoformat(config["original_scientific_freeze_utc"])).total_seconds()
    budget = SolverBudget(seconds=max(0, 7200 - elapsed_since_scientific_freeze))
    budget.calls = PRIOR_CALLS_RESERVED
    with budget:
        for item in manifest["records"]:
            sample_id = item["sample_zero_based_index"]
            descriptions = [inherited_description(central_cases[sample_id])]
            visits = [{"profile_tuple": SLOTS, "model_sha256": item["model_sha256"],
                       "case_sha256": item["case_sha256"], "origin": "INHERITED_STAGE2", "description": descriptions[0]}]
            attempted, sample_stop = [], None
            if len(descriptions[0]["possible"]) < 2 and not stop_reason:
                for chosen in manifest["all_profile_tuples"][1:]:
                    try:
                        budget.remaining()
                        if model_count >= config["budget"]["new_models"]:
                            raise BudgetExceeded("MODEL_LIMIT")
                        model_count += 1
                        attempted.append(chosen)
                        model = tuple_model(receptors[sample_id], profiles, chosen)
                        model_hash = core.native.sha256(core.native.json_bytes(core.encode_q(model)))
                        possible = conclusion(descriptions, 120)["possible_co_leaders_lower_bound"]
                        before_calls = budget.calls
                        result = inspect_model(model, possible)
                        description = describe(result)
                        case = {"configuration_sha256": sha(CONFIG), "sample_zero_based_index": sample_id,
                                "profile_tuple": chosen, "model_sha256": model_hash, "model": model, "result": result,
                                "numerical_LP_calls": budget.calls - before_calls}
                        path = case_path(model_hash)
                        write_json(path, case)
                        visits.append({"profile_tuple": chosen, "model_sha256": model_hash, "case_sha256": sha(path),
                                       "origin": "NEW_UNION_MODEL", "description": description})
                        descriptions.append(description)
                        write_json(PRIVATE / "interval_union_current_checkpoint.json", {"sample_zero_based_index": sample_id,
                                   "visits": visits, "attempted_new_tuples": attempted, "LP_calls": budget.calls})
                        if conclusion(descriptions, 120)["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER":
                            sample_stop = "TWO_EXACT_CO_LEADER_WITNESSES"
                            break
                    except BudgetExceeded as exc:
                        sample_stop = stop_reason = str(exc)
                        break
            outcome = conclusion(descriptions, 120)
            visited = {tuple(v["profile_tuple"]) for v in visits}
            row = {"sample_zero_based_index": sample_id, "sample": item["sample"], "visits": visits,
                   "attempted_new_tuples": attempted, "unvisited_tuples": [t for t in manifest["all_profile_tuples"] if tuple(t) not in visited],
                   "stopping_reason": sample_stop or ("INHERITED_AMBIGUITY" if len(descriptions[0]["possible"]) >= 2 else stop_reason or "ALL_SYSTEMS_VISITED"),
                   "outcome": outcome}
            rows.append(row)
            write_json(PRIVATE / "interval_union_index_partial.json", {"records": rows, "LP_calls": budget.calls})
            print(json.dumps({"sample_number_accounted": sample_id + 1, "status": outcome["status"],
                              "systems_visited": len(visits), "LP_calls": budget.calls}), flush=True)
    ledger = {"configuration_sha256": sha(CONFIG), "started_utc": started, "completed_utc": core.now(),
              "numerical_LP_calls_charged_for_budget": budget.calls,
              "numerical_LP_calls_observed_this_run": budget.calls - PRIOR_CALLS_RESERVED,
              "prior_unrecorded_calls_upper_bound": PRIOR_CALLS_RESERVED,
              "new_models_attempted_including_prior_write_failure": model_count, "global_stop_reason": stop_reason,
              "records": rows}
    write_json(index_path, ledger)
    report = {"status": "COMPLETED_BOUNDED_AUDIT" if stop_reason is None else "STOPPED_AT_FROZEN_BUDGET",
              "independent_new_tuple_verification": "PENDING; do not promote positive union claims before independent replay",
              "configuration_sha256": sha(CONFIG), "private_index_sha256": sha(index_path),
              "script_sha256": sha(__file__), "started_utc": started, "completed_utc": core.now(),
              "all_initial_samples": len(rows), "inherited_ambiguity_samples": 31, "targeted_samples": 4,
              "new_models_attempted_including_prior_write_failure": model_count,
              "new_models_completed": sum(len(r["visits"]) - 1 for r in rows),
              "numerical_LP_calls_charged_for_budget": budget.calls,
              "numerical_LP_calls_observed_this_run": budget.calls - PRIOR_CALLS_RESERVED,
              "prior_unrecorded_calls_upper_bound": PRIOR_CALLS_RESERVED,
              "status_counts": dict(Counter(r["outcome"]["status"] for r in rows)),
              "system_visit_count_distribution": dict(Counter(len(r["visits"]) for r in rows)),
              "stopping_counts": dict(Counter(r["stopping_reason"] for r in rows)), "global_stop_reason": stop_reason,
              "limits": config["limits"], "no_full_ranges_or_system_frequency_claim": True}
    write_json(PUBLIC / "interval_union_results.json", report)
    lines = ["# Bounded historical profile-union decision audit", "", config["limits"], "",
             "Independent verification of the newly created tuple records is pending; no positive union certificate is promoted here.", "",
             "Scope: k=2, joint independent receptor/profile boxes, original seven families, no mass constraint, actual120 historical systems rather than a componentwise profile envelope.", "",
             f"All {len(rows)} samples accounted. Central-system ambiguity proofs were inherited for31; only the remaining4 received new model evaluations.",
             f"New models completed: {report['new_models_completed']}; tracked numerical LP calls (including helpers and cross-checks): {budget.calls - PRIOR_CALLS_RESERVED}. Budget charge additionally reserves the maximum27 calls for the first failed case-file write; total charged: {budget.calls}. This is a conservative bound, not a fabricated exact count for the lost attempt.",
             f"Decision counts: `{json.dumps(report['status_counts'], sort_keys=True)}`.", "",
             "A second exact co-leader witness suffices to reject a guaranteed strict unique leader over the union. Positive/empty union certificates require all120 systems and no unresolved component. Early stopping does not characterize the full leader set, contribution hull, or feasible-system fraction.", "",
             "KEEP qualified exact witnesses after independent replay. HOLD physical attainability, confidence coverage, accuracy and unresolved unions. REMOVE claims of a new method, new environmental measurements, or exhaustive characterization of every system for all35 samples.", "",
             f"Configuration SHA-256: `{sha(CONFIG)}`.", f"Private index SHA-256: `{sha(index_path)}`.", ""]
    (PUBLIC / "interval_union_report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=core.native.DEFAULT_INPUT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze(args.inputs) if args.freeze else run(args.inputs), indent=2))
