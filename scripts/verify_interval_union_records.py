#!/usr/bin/env python3
"""Independent original-input Stage3 proof replay. No producer imports or LPs."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import time

import verify_interval_certificate_records as v

ROOT, PUBLIC, PRIVATE = v.ROOT, v.PUBLIC, v.PRIVATE
CONFIG_HASH = "33f10f141aad7d8dc5f72bf7cfd06e89c7a2f61c839f1fd8f3b50477f086331a"
INDEX_HASH = "383b73ca7b0ebdb79b04008adff2085acbca48f2be8b5355062ec73d86452d92"
VERIFIER_HASH = "53d1682413236b394fc24adae1d2dea75c2a621799947111e9a835a5afea1fed"
PRIOR_HASH = "bba9d04eb6ffb20d55f754cfc4ad4876cb4c92af176aef39044d06ae54100e44"
GRID_HASH = "f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314"
require = v.require


def read(path, expected=None):
    return json.loads(v.check_hash(path, expected) if expected else path.read_bytes())


def tuple_model(receptor, profiles, chosen, allowed):
    require(list(chosen) in allowed and len(chosen) == 7, "unapproved complete profile tuple")
    for sid in chosen:
        require(profiles[sid]["SID"] == sid and profiles[sid]["SIZE"] == "FINE", "profile identity/size")
    aliased = {slot: profiles[sid] for slot, sid in zip(v.SOURCES, chosen)}
    result = v.reconstruct_model(receptor, aliased, v.SOURCES, 2, "joint_intervals", "none")
    result["sources"] = list(chosen)
    return result


def expected_conclusion(descriptions, total=120):
    require(0 < len(descriptions) <= total, "invalid union coverage")
    possible = sorted({s for d in descriptions for s in d["possible"]})
    complete = len(descriptions) == total
    winner = None
    if len(possible) >= 2:
        status = "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER"
    elif complete and all(d["status"] == "EXACT_INFEASIBLE" for d in descriptions):
        status = "EXACT_EMPTY_UNION"
    else:
        feasible = [d for d in descriptions if d["status"] == "EXACT_COMPATIBLE"]
        good = complete and len(possible) == 1 and bool(feasible)
        good = good and all(d["status"] in ("EXACT_COMPATIBLE", "EXACT_INFEASIBLE") for d in descriptions)
        good = good and all(d["unique"] == possible for d in feasible)
        status = "VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN" if good else "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION"
        if good:
            winner = possible[0]
    return {"status": status, "possible_co_leaders_lower_bound": possible, "unique_union_leader": winner,
            "systems_covered": len(descriptions), "system_universe": total, "all_systems_visited": complete,
            "full_possible_leader_set_claimed": False, "full_contribution_ranges_computed": False}


def call_count(info, objective=False):
    status = info["solver_status"]
    require(isinstance(status, int) and status in (0, 1, 2, 3, 4), "invalid solver status")
    # Frozen producer: phase-I on status2; objective cross-check on status0 or
    # recession helper on status3. Exact algebraic repair invokes no LP.
    return 1 + int(status == 2 or (objective and status in (0, 3)))


def inspect_saved(model, result, prior_possible, counts):
    G, h, n = model["G"], model["h"], model["n"]
    base = result["feasibility"]
    v.verify_feasibility(base, G, h, n, counts)
    calls = call_count(base)
    feasible = base["status"] == "EXACT_FEASIBLE"
    require(result["overall_status"] == ("EXACT_COMPATIBLE" if feasible else base["status"]), "overall feasibility mismatch")
    current = []
    possible = set(prior_possible)
    co = result["co_leaders"]
    require(list(co) == model["names"][:len(co)], "co-leader traversal not fixed prefix")
    if not feasible:
        require(not co and not result["leader_bounds"] and not result["co_leader_search_complete"], "proof search on failed base")
        require(not result["verified_unique_leaders_above_margin_threshold"], "unique leader on failed base")
    else:
        stopped = False
        for j, (name, info) in enumerate(co.items()):
            require(not stopped, "search continued after second distinct witnessed leader")
            restrictions = [[Q(int(i == k) - int(i == j)) for i in range(n)] for k in range(n) if k != j]
            v.verify_feasibility(info, G + restrictions, h + [Q(0)] * (n-1), n, counts)
            calls += call_count(info)
            counts["joint_co_leader_problems"] += 1
            if info["status"] == "EXACT_FEASIBLE":
                current.append(name)
                possible.add(name)
            stopped = len(possible) >= 2
        if stopped:
            require(result.get("stopping_reason") == "SECOND_UNION_CO_LEADER_WITNESS", "missing early stop")
            require(not result["co_leader_search_complete"] and not result["leader_bounds"], "early stop falsely exhaustive")
            require(not result["verified_unique_leaders_above_margin_threshold"], "early ambiguity marked unique")
        else:
            require(len(co) == n and result["co_leader_search_complete"], "incomplete co-leader search not disclosed")
            unique = []
            if len(possible) == 1:
                leader = next(iter(possible))
                threshold = Q(1, 10_000_000) * max(Q(1), model["mass"])
                require(result.get("candidate_leader") == leader and v.fraction(result["near_zero_threshold"]) == threshold, "candidate/margin changed")
                require(set(result["leader_bounds"]) == set(model["names"]) - {leader}, "missing rival margin")
                j = model["names"].index(leader)
                for rival, info in result["leader_bounds"].items():
                    k = model["names"].index(rival)
                    objective = [Q(int(i == j)-int(i == k)) for i in range(n)]
                    v.verify_objective(info, G, h, n, model["upper_bounds"], objective, "none", counts)
                    calls += call_count(info, True)
                    counts["leader_margin_objectives"] += 1
                if all(r["status"] == "VERIFIED_BOUND_AND_WITNESS" and v.fraction(r["verified_lower_bound"]) > threshold
                       for r in result["leader_bounds"].values()):
                    unique = [leader]
            else:
                require(not result["leader_bounds"] and "candidate_leader" not in result, "candidate invented without witness")
            require(result["verified_unique_leaders_above_margin_threshold"] == unique, "strict-margin classification mismatch")
    return {"status": result["overall_status"], "possible": current,
            "unique": result["verified_unique_leaders_above_margin_threshold"],
            "exhaustive_model_decisions": result["co_leader_search_complete"]}, calls


def check_lineage(config):
    old_dir = PRIVATE / "interval_union_pre_pathfix"
    prior = read(PUBLIC / "interval_union_configuration.json", PRIOR_HASH)
    v.check_hash(old_dir / "audit_interval_profile_union.py", prior["script_sha256"])
    v.check_hash(old_dir / "test_interval_profile_union.py", prior["tests_sha256"])
    require((old_dir / "interval_union_configuration.json").read_bytes() == (PUBLIC / "interval_union_configuration.json").read_bytes(), "v1 configuration not preserved")
    require(config["prior_configuration_sha256"] == PRIOR_HASH and config["original_scientific_freeze_utc"] == prior["frozen_utc"], "clock/config lineage lost")
    scientific = ("root_approval", "protocol_sha256", "producer_sha256", "stage2_index_sha256", "grid_configuration_sha256",
                  "archive_sha256", "scope", "budget", "tuple_order", "candidate_partition", "stopping", "leader_margin", "randomness", "metadata", "limits")
    require(all(config[k] == prior[k] for k in scientific), "scientific configuration changed after first execution")
    def functions(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    a = functions(old_dir / "audit_interval_profile_union.py")
    b = functions(ROOT / "scripts/audit_interval_profile_union.py")
    unchanged = ("SolverBudget", "profile_grid", "tuple_model", "inherited_description", "conclusion", "inspect_model", "describe", "inputs_and_candidates")
    require(all(a[k] == b[k] for k in unchanged), "scientific function changed")
    require((old_dir / "interval_union_candidates.json").read_bytes() == (PRIVATE / "interval_union_candidates_v2.json").read_bytes(), "candidate manifest changed")
    preflight = read(PRIVATE / "interval_union_write_paths_preflight.json", config["all476_case_write_paths_preflight_sha256"])
    paths = preflight["all_potential_case_paths"]
    require(preflight["status"] == "PASS" and len(paths) == 476 and len({p["model_sha256"] for p in paths}) == 476, "preflight coverage incomplete")
    require(all(p["roundtrip"] == "PASS" and p["path_characters"] < 260 for p in paths), "preflight failed/long")
    interruption = config["interruption"]
    require(interruption["prior_unrecorded_LP_calls_charged_upper_bound"] == 27 and interruption["prior_model_attempts_charged"] == 1, "lost attempt uncharged")
    return {"scientific_fields_unchanged": len(scientific), "scientific_functions_AST_identical": len(unchanged),
            "manifest_byte_identical": True, "path_preflight_records": 476,
            "max_saved_path_length": max(p["path_characters"] for p in paths),
            "original_freeze_utc": prior["frozen_utc"], "lost_attempt_LP_upper_allowance": 27}


def hold_details(visits, cases):
    result = Counter()
    gaps = []
    for visit in visits:
        desc = visit["description"]
        result["component_" + desc["status"]] += 1
        case = cases[visit["model_sha256"]]
        data = case["result"]
        if desc["status"] == "NUMERICALLY_UNRESOLVED":
            gaps.append({"model_sha256": visit["model_sha256"], "type": "unresolved_base_feasibility",
                         "solver_status": data["feasibility"]["solver_status"],
                         "farkas_verified": data["feasibility"].get("farkas", {}).get("verified")})
        for name, info in data.get("co_leaders", {}).items():
            if info["status"] == "NUMERICALLY_UNRESOLVED":
                result["unresolved_co_leader_problems"] += 1
        if desc["status"] == "EXACT_COMPATIBLE" and not desc["unique"]:
            result["compatible_without_verified_strict_margin"] += 1
            for name, info in data.get("leader_bounds", {}).items():
                threshold = v.fraction(data["near_zero_threshold"])
                if info["status"] != "VERIFIED_BOUND_AND_WITNESS":
                    result["unresolved_margin_objectives"] += 1
                    result["unresolved_margin_with_exact_primal" if info.get("primal", {}).get("verified")
                           else "unresolved_margin_without_exact_primal"] += 1
                    result["unresolved_margin_with_exact_dual" if info.get("dual", {}).get("verified")
                           else "unresolved_margin_without_exact_dual"] += 1
                    if not info.get("crosscheck_agrees", False):
                        result["unresolved_margin_without_agreeing_numeric_crosscheck"] += 1
                    gaps.append({"model_sha256": visit["model_sha256"], "type": "unresolved_margin",
                                 "rival": name, "status": info["status"],
                                 "primal_verification_method": info.get("primal", {}).get("method"),
                                 "dual_failure_reason": info.get("dual", {}).get("reason"),
                                 "numeric_crosscheck_agrees": info.get("crosscheck_agrees")})
                elif v.fraction(info["verified_lower_bound"]) <= threshold:
                    result["verified_bound_not_above_threshold"] += 1
                    gaps.append({"model_sha256": visit["model_sha256"], "type": "verified_bound_not_above_threshold",
                                 "rival": name, "lower_bound": info["verified_lower_bound"], "threshold": str(threshold)})
    return {"systems": len(visits), "counts": dict(result), "proof_gap_records": gaps}


def verify(max_seconds=600):
    started = time.monotonic()
    v.check_hash(Path(v.__file__), VERIFIER_HASH)
    config = read(PUBLIC / "interval_union_configuration_v2.json", CONFIG_HASH)
    v.check_hash(ROOT / "scripts/audit_interval_profile_union.py", config["script_sha256"])
    v.check_hash(ROOT / "tests/test_interval_profile_union.py", config["tests_sha256"])
    v.check_hash(PUBLIC / "interval_stage3_protocol_PROPOSED.md", config["protocol_sha256"])
    lineage = check_lineage(config)
    receptors, profiles, _ = v.load_original_inputs(v.DEFAULT_INPUT)
    grid_config = read(PUBLIC / "joint_profile_configuration.json", GRID_HASH)
    grid = [list(t) for t in itertools.product(*(grid_config["families"].get(s, [s]) for s in v.SOURCES))]
    require(len(grid) == len({tuple(t) for t in grid}) == 120 and grid[0] == v.SOURCES, "historical grid incomplete")
    manifest = read(PRIVATE / "interval_union_candidates_v2.json", config["candidate_manifest_sha256"])
    require(grid == config["tuple_order"] == manifest["all_profile_tuples"], "tuple universe/order mismatch")
    # Independently reconstruct all 476 path-preflight model hashes.
    path_rows = read(PRIVATE / "interval_union_write_paths_preflight.json")["all_potential_case_paths"]
    path_hashes = [v.digest(v.json_bytes(v.encode(tuple_model(receptors[i], profiles, t, grid))))
                   for i in manifest["targets"] for t in grid[1:]]
    require(path_hashes == [p["model_sha256"] for p in path_rows], "preflight did not cover original tuple models")
    stage2 = read(PRIVATE / "interval_index.json", config["stage2_index_sha256"])
    inherited = {r["sample_zero_based_index"]: r for r in stage2["records"]
                 if (r["universe"], r["k"], r["profile_mode"], r["mass_mode"]) == ("full_seven_primary", 2, "joint_intervals", "none")}
    require(len(inherited) == 35 and manifest["records"] == [inherited[i] for i in range(35)], "manifest inherited index mismatch")
    index = read(PRIVATE / "interval_union_index.json", INDEX_HASH)
    require(index["configuration_sha256"] == CONFIG_HASH and len(index["records"]) == 35, "union final identity/denominator")
    require([r["sample_zero_based_index"] for r in index["records"]] == list(range(35)), "sample reorder/omission")
    counters, cases, outcomes, targets, holds = Counter(), {}, [], [], []
    observed_calls = new_models = 0
    for row in index["records"]:
        require(time.monotonic()-started <= max_seconds, "independent replay time budget exceeded")
        i = row["sample_zero_based_index"]
        require(row["sample"] == {k: receptors[i][k] for k in v.IDENTITY}, "receptor identity mismatch")
        visits = row["visits"]
        require([visit["profile_tuple"] for visit in visits] == grid[:len(visits)], "tuple omissions/order/duplicates")
        require(row["attempted_new_tuples"] == grid[1:len(visits)], "attempted/new visit accounting")
        require(row["unvisited_tuples"] == grid[len(visits):], "unvisited universe accounting")
        descriptions = []
        for j, visit in enumerate(visits):
            chosen = visit["profile_tuple"]
            model = tuple_model(receptors[i], profiles, chosen, grid)
            mid = v.digest(v.json_bytes(v.encode(model)))
            require(mid == visit["model_sha256"], "original-decimal tuple model mismatch")
            if j == 0:
                original = inherited[i]
                require(visit["origin"] == "INHERITED_STAGE2" and mid == original["model_sha256"]
                        and visit["case_sha256"] == original["case_sha256"], "inherited provenance")
                case = read(PRIVATE / "interval_cases" / ("interval_case_" + mid + ".json"), visit["case_sha256"])
                v.verify_result(case["result"], model, counters)
                data = case["result"]
                description = {"status": data["overall_status"], "possible": data.get("exact_possible_co_leaders", []),
                               "unique": data.get("verified_unique_leaders_above_margin_threshold", []), "exhaustive_model_decisions": True}
                if len(description["possible"]) < 2:
                    targets.append(i)
            else:
                require(visit["origin"] == "NEW_UNION_MODEL", "new visit provenance")
                require(expected_conclusion(descriptions)["status"] != "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER", "continued after proven ambiguity")
                case = read(PRIVATE / "interval_union_cases" / ("u_" + mid + ".json"), visit["case_sha256"])
                require(case["configuration_sha256"] == CONFIG_HASH and case["profile_tuple"] == chosen
                        and case["sample_zero_based_index"] == i, "new case identity")
                prior = expected_conclusion(descriptions)["possible_co_leaders_lower_bound"]
                description, calls = inspect_saved(model, case["result"], prior, counters)
                require(calls == case["numerical_LP_calls"], "new-case tracked solver calls mismatch")
                observed_calls += calls
                new_models += 1
            require(case["model"] == v.encode(model) and case["model_sha256"] == mid, "saved matrix not original model")
            require(visit["description"] == description, "visit proof summary mismatch")
            descriptions.append(description)
            cases[mid] = case
        expected = expected_conclusion(descriptions)
        require(row["outcome"] == expected, "union claim not implied by verified components")
        if len(descriptions[0]["possible"]) >= 2:
            reason = "INHERITED_AMBIGUITY"
            require(len(visits) == 1, "unneeded inherited-ambiguity solves")
        elif expected["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER":
            reason = "TWO_EXACT_CO_LEADER_WITNESSES"
        else:
            require(len(visits) == 120, "unexplained incomplete union")
            reason = "ALL_SYSTEMS_VISITED"
        require(row["stopping_reason"] == reason, "stopping reason mismatch")
        outcomes.append(expected)
        if expected["status"].startswith("HOLD"):
            holds.append(hold_details(visits, cases))
    require(targets == manifest["targets"] and len(targets) == 4, "targeted sample predicate differs")
    files = list((PRIVATE / "interval_union_cases").glob("u_*.json"))
    require(len(files) == new_models and {p.stem[2:] for p in files} == {visit["model_sha256"] for row in index["records"] for visit in row["visits"][1:]}, "orphan/missing new cases")
    require(index["global_stop_reason"] is None and observed_calls == index["numerical_LP_calls_observed_this_run"], "observed call count/global stop")
    require(index["numerical_LP_calls_charged_for_budget"] == observed_calls + 27 <= config["budget"]["all_numerical_LP_calls"], "cumulative LP budget")
    require(index["prior_unrecorded_calls_upper_bound"] == 27 and index["new_models_attempted_including_prior_write_failure"] == new_models + 1 <= config["budget"]["new_models"], "cumulative model budget")
    elapsed = (datetime.fromisoformat(index["completed_utc"]) - datetime.fromisoformat(config["original_scientific_freeze_utc"])).total_seconds()
    require(0 <= elapsed <= config["budget"]["wall_seconds"] and datetime.fromisoformat(index["completed_utc"]) <= datetime.fromisoformat(config["budget"]["absolute_qa_cutoff_utc"]), "original wall/QA budget exceeded")
    report = read(PUBLIC / "interval_union_results.json")
    require(report["private_index_sha256"] == INDEX_HASH and report["configuration_sha256"] == CONFIG_HASH and report["script_sha256"] == config["script_sha256"], "public identities")
    require(report["all_initial_samples"] == 35 and report["inherited_ambiguity_samples"] == 31 and report["targeted_samples"] == 4, "public sample counts")
    for key in ("numerical_LP_calls_charged_for_budget", "numerical_LP_calls_observed_this_run", "prior_unrecorded_calls_upper_bound", "new_models_attempted_including_prior_write_failure", "global_stop_reason"):
        require(report[key] == index[key], "public budget mismatch")
    require(report["new_models_completed"] == new_models, "public completed count")
    statuses = dict(Counter(o["status"] for o in outcomes))
    require(report["status_counts"] == statuses, "public union status counts")
    require(report["system_visit_count_distribution"] == dict(Counter(str(o["systems_covered"]) for o in outcomes)), "public system coverage")
    require(report["stopping_counts"] == dict(Counter(r["stopping_reason"] for r in index["records"])), "public stopping counts")
    return {"status": "PASS", "completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": round(time.monotonic()-started, 3),
            "configuration_sha256": CONFIG_HASH, "private_index_sha256": INDEX_HASH,
            "verifier_sha256": v.digest(Path(__file__).read_bytes()), "exact_primitive_dependency_sha256": VERIFIER_HASH,
            "lineage": lineage, "all_samples": 35, "new_tuple_models": new_models, "proof_counts_including_inherited": dict(counters),
            "observed_numerical_calls_reconciled": observed_calls, "prior_unrecorded_call_allowance": 27,
            "cumulative_model_attempts": new_models+1, "status_counts": statuses, "HOLD_diagnostics": holds,
            "LPs_rerun": 0, "interpretation": "Exact consistency with the frozen conditional boxes/union; no confidence, physical-realizability or field-truth claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-seconds", type=float, default=600)
    args = parser.parse_args()
    require(0 < args.max_seconds <= 1800, "invalid verification time budget")
    result = verify(args.max_seconds)
    output = PUBLIC / "interval_union_certificate_verification.json"
    output.write_bytes(v.json_bytes(result))
    display = {key: value for key, value in result.items() if key != "HOLD_diagnostics"}
    display["HOLD_diagnostics"] = [{key: value for key, value in item.items() if key != "proof_gap_records"}
                                   for item in result["HOLD_diagnostics"]]
    print(json.dumps(display, indent=2))


if __name__ == "__main__":
    main()
