#!/usr/bin/env python3
"""Exact proof-only completion from saved co-leader Farkas certificates.

Standard library only. No numerical solver, new fit, field-input modification,
or replacement of the original Stage3 HOLD.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
PROTOCOL = PUBLIC / "interval_farkas_protocol_PROPOSED.md"
PROTOCOL_HASH = "f67d9288b8ed6e546c01f7a24af1993b37bb4a95b78a7bd1b5b4222a69391783"
INDEX = PRIVATE / "interval_union_index.json"
INDEX_HASH = "383b73ca7b0ebdb79b04008adff2085acbca48f2be8b5355062ec73d86452d92"
UNION_CONFIG = PUBLIC / "interval_union_configuration_v2.json"
UNION_CONFIG_HASH = "33f10f141aad7d8dc5f72bf7cfd06e89c7a2f61c839f1fd8f3b50477f086331a"
CONFIG = PUBLIC / "interval_farkas_configuration.json"
MANIFEST = PRIVATE / "interval_farkas_manifest.json"
NAMES = ["soil", "wood", "oil", "vehicle", "ammonium_sulfate", "ammonium_nitrate", "sodium_nitrate"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(obj):
    if isinstance(obj, Q):
        return str(obj)
    if isinstance(obj, dict):
        return {k: encode(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [encode(v) for v in obj]
    return obj


def data(obj):
    return (json.dumps(encode(obj), ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_json(path, obj):
    Path(path).write_bytes(data(obj))


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("dot-product dimension mismatch")
    return sum((Q(x) * Q(y) for x, y in zip(a, b)), Q(0))


def exact_model(raw):
    n, names = raw["n"], list(raw["names"])
    G, h = [[Q(x) for x in row] for row in raw["G"]], [Q(x) for x in raw["h"]]
    if n < 2 or len(names) != n or len(set(names)) != n or len(G) != len(h) or any(len(row) != n for row in G):
        raise ValueError("invalid model dimensions or family names")
    return {"n": n, "names": names, "G": G, "h": h}


def check_point(model, raw_point):
    point = [Q(v) for v in raw_point]
    if len(point) != model["n"] or any(v < 0 for v in point) or any(dot(row, point) > rhs for row, rhs in zip(model["G"], model["h"])):
        raise ValueError("point does not exactly satisfy original nonnegative model")
    return point


def leader_rows(model, name):
    if name not in model["names"]:
        raise ValueError("co-leader family not in source mapping")
    j = model["names"].index(name)
    rows = []
    for k in range(model["n"]):
        if k != j:
            row = [Q(0)] * model["n"]
            row[k], row[j] = Q(1), Q(-1)
            rows.append(row)
    return rows


def verify_farkas(G, h, n, raw_y):
    y = [Q(v) for v in raw_y]
    if len(G) != len(h) or len(y) != len(G) or any(len(row) != n for row in G) or any(v < 0 for v in y):
        raise ValueError("Farkas multiplier dimensions or nonnegative signs fail")
    residual = [sum((y[i] * Q(G[i][j]) for i in range(len(G))), Q(0)) for j in range(n)]
    h_dot_y = dot(h, y)
    if any(v < 0 for v in residual) or h_dot_y >= 0:
        raise ValueError("exact Farkas residual or contradiction sign fails")
    return y, residual, h_dot_y


def farkas_margin(model, competitor, raw_y):
    """Algebra only; a certificate requires all universal-max premises upstream."""
    D = leader_rows(model, competitor)
    y, residual, h_dot_y = verify_farkas(model["G"] + D, model["h"] + [Q(0)] * len(D), model["n"], raw_y)
    m = len(model["G"])
    a, b = y[:m], y[m:]
    B = sum(b, Q(0))
    if B <= 0:
        raise ValueError("B must be strictly positive")
    gamma = -dot(a, model["h"])
    if gamma != -h_dot_y or gamma <= 0:
        raise ValueError("gamma disagrees with exact augmented contradiction")
    return {"competitor": competitor, "a": a, "b": b, "D_rows": D,
            "augmented_residual": residual, "gamma": gamma, "B": B,
            "lower_margin": gamma / B}


def component_margins(raw_model, result, delta, expected_leader=None):
    model = exact_model(raw_model)
    delta = Q(delta)
    if delta <= 0:
        raise ValueError("frozen positive margin required")
    if result["overall_status"] == "EXACT_INFEASIBLE":
        cert = result["feasibility"].get("farkas", {})
        if result["feasibility"]["status"] != "EXACT_INFEASIBLE" or not cert.get("verified"):
            raise ValueError("base infeasibility proof missing")
        y, residual, contradiction = verify_farkas(model["G"], model["h"], model["n"], cert["y"])
        return {"status": "EXACT_INFEASIBLE", "y": y, "residual": residual, "h_dot_y": contradiction, "bounds": []}
    if result["overall_status"] != "EXACT_COMPATIBLE":
        return {"status": "HOLD_UNRESOLVED_COMPONENT", "bounds": []}
    feasibility = result["feasibility"]
    if feasibility["status"] != "EXACT_FEASIBLE" or not feasibility.get("primal", {}).get("verified"):
        raise ValueError("exact base feasible witness missing")
    base_point = check_point(model, feasibility["primal"]["point"])
    co = result["co_leaders"]
    if set(co) != set(model["names"]):
        raise ValueError("missing/extra competitor co-leader proof")
    possible = [name for name, info in co.items() if info["status"] == "EXACT_FEASIBLE"]
    if len(possible) != 1:
        raise ValueError("a single witnessed possible co-leader is required")
    leader = possible[0]
    if expected_leader is not None and leader != expected_leader:
        raise ValueError("wrong W/family mapping")
    if not co[leader].get("primal", {}).get("verified"):
        raise ValueError("W joint co-leader witness missing")
    leader_point = check_point(model, co[leader]["primal"]["point"])
    if any(dot(row, leader_point) > 0 for row in leader_rows(model, leader)):
        raise ValueError("W witness fails joint co-leader inequalities")
    certificates = []
    # Verify every impossibility first. No field bound is called a margin until
    # these collectively establish W is universally the unique maximum.
    for competitor in model["names"]:
        if competitor == leader:
            continue
        info = co[competitor]
        cert = info.get("farkas", {})
        if info["status"] != "EXACT_INFEASIBLE" or not cert.get("verified"):
            raise ValueError("competitor impossibility not exactly certified")
        D = leader_rows(model, competitor)
        verify_farkas(model["G"] + D, model["h"] + [Q(0)] * len(D), model["n"], cert["y"])
        certificates.append((competitor, cert["y"]))
    bounds = []
    for competitor, y in certificates:
        bound = farkas_margin(model, competitor, y)
        lower = bound["lower_margin"]
        bound.update({"leader": leader, "delta": delta,
                      "threshold_relation": "ABOVE" if lower > delta else "EQUAL" if lower == delta else "BELOW"})
        bounds.append(bound)
    return {"status": "EXACT_FEASIBLE_ALL_MARGIN_PREMISES", "leader": leader, "base_point": base_point,
            "leader_point": leader_point, "bounds": bounds,
            "all_margins_above_delta": all(b["threshold_relation"] == "ABOVE" for b in bounds)}


def union_summary(components, expected_systems):
    feasible = [c for c in components if c["status"] == "EXACT_FEASIBLE_ALL_MARGIN_PREMISES"]
    names = {c["leader"] for c in feasible}
    complete = len(components) == expected_systems
    if len(components) > expected_systems:
        raise ValueError("extra or duplicated components")
    if complete and all(c["status"] == "EXACT_INFEASIBLE" for c in components):
        status = "EXACT_EMPTY_UNION_NOT_A_LEADER_CERTIFICATE"
    elif (complete and feasible and len(names) == 1
          and all(c["status"] in ("EXACT_INFEASIBLE", "EXACT_FEASIBLE_ALL_MARGIN_PREMISES") for c in components)
          and all(c["all_margins_above_delta"] for c in feasible)):
        status = "POSTHOC_CERTIFIED_UNIQUE_UNION_LEADER_ABOVE_ORIGINAL_MARGIN"
    else:
        status = "HOLD_MISSING_INVALID_UNRESOLVED_OR_INSUFFICIENT_MARGIN"
    return {"status": status, "expected_systems": expected_systems, "components_checked": len(components),
            "component_status_counts": dict(Counter(c["status"] for c in components)),
            "feasible_component_leaders": sorted(names),
            "threshold_relations": dict(Counter(b["threshold_relation"] for c in feasible for b in c["bounds"])),
            "bounds_checked": sum(len(c["bounds"]) for c in feasible)}


def case_path(visit):
    if visit["origin"] == "INHERITED_STAGE2":
        return PRIVATE / "interval_cases" / ("interval_case_" + visit["model_sha256"] + ".json")
    if visit["origin"] == "NEW_UNION_MODEL":
        return PRIVATE / "interval_union_cases" / ("u_" + visit["model_sha256"] + ".json")
    raise ValueError("unknown proof origin")


def manifest():
    if sha(PROTOCOL) != PROTOCOL_HASH or sha(INDEX) != INDEX_HASH or sha(UNION_CONFIG) != UNION_CONFIG_HASH:
        raise ValueError("approved protocol or original union identity changed")
    index = json.loads(INDEX.read_bytes())
    rows = index["records"]
    if len(rows) != 35:
        raise ValueError("all35 accounting gate failed")
    targets = [r for r in rows if r["outcome"]["status"] == "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION"]
    inherited = [r for r in rows if r["outcome"]["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER"]
    if len(targets) != 1 or len(inherited) != 34 or len(targets[0]["visits"]) != 120:
        raise ValueError("approved single-HOLD/34-ambiguity partition differs")
    target = targets[0]
    if len({tuple(v["profile_tuple"]) for v in target["visits"]}) != 120:
        raise ValueError("target does not cover120 distinct systems")
    for visit in target["visits"]:
        if sha(case_path(visit)) != visit["case_sha256"]:
            raise ValueError("source case identity differs")
    return {"original_union_index_sha256": INDEX_HASH, "target": target,
            "inherited_nonunique_sample_indices": [r["sample_zero_based_index"] for r in inherited]}


def freeze():
    if CONFIG.exists() or MANIFEST.exists():
        raise ValueError("proof-only configuration already frozen")
    selected = manifest()  # Hashes and existing labels only; no gamma/B arithmetic.
    tests = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests",
                            "-p", "test_interval_farkas_margin.py", "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("synthetic gate failed\n" + tests.stdout + tests.stderr)
    write_json(MANIFEST, selected)
    config = {"version": "1.0.0", "frozen_utc": datetime.now(timezone.utc).isoformat(),
              "frozen_before_first_field_gamma_over_B_evaluation": True,
              "root_approval": "Root read the complete proposed protocol and approved its exact SHA-256 before field evaluation.",
              "protocol_sha256": PROTOCOL_HASH, "script_sha256": sha(__file__),
              "tests_sha256": sha(ROOT / "tests/test_interval_farkas_margin.py"),
              "manifest_sha256": sha(MANIFEST), "original_union_index_sha256": INDEX_HASH,
              "original_union_configuration_sha256": UNION_CONFIG_HASH,
              "original_union_results_sha256": sha(PUBLIC / "interval_union_results.json"),
              "original_union_report_sha256": sha(PUBLIC / "interval_union_report.md"),
              "scope": {"all_samples": 35, "inherited_nonunique": 34, "targeted_union": 1,
                        "systems": 120, "expected_exact_feasible": 48, "expected_exact_infeasible": 72,
                        "bounds": 288, "k": 2, "full_seven_families": True, "mass_constraint": "none"},
              "threshold": "delta=1e-7*max(1,TMAC); strict greater-than required; unchanged",
              "solver_calls_permitted": 0, "randomness": "none", "multiplier_selection": "existing stored certificates only; no optimization, scaling search or substitution",
              "synthetic_gate": {"status": "PASS", "output": tests.stdout + tests.stderr},
              "interpretation_gate": "Independent original-input and actual-record proof replay required before positive claims; original Stage3 HOLD unchanged."}
    write_json(CONFIG, config)
    return {"status": "FROZEN_SYNTHETIC_GATE_PASS", "configuration_sha256": sha(CONFIG)}


def run():
    config = json.loads(CONFIG.read_bytes())
    if sha(__file__) != config["script_sha256"] or sha(ROOT / "tests/test_interval_farkas_margin.py") != config["tests_sha256"] or sha(MANIFEST) != config["manifest_sha256"]:
        raise ValueError("code/test/manifest identity differs from pre-evaluation freeze")
    selected = manifest()
    if selected != json.loads(MANIFEST.read_bytes()):
        raise ValueError("manifest changed")
    if (PRIVATE / "interval_farkas_ledger.json").exists():
        raise ValueError("proof-only run already exists; do not overwrite silently")
    cases, deltas = [], set()
    for visit in selected["target"]["visits"]:
        case = json.loads(case_path(visit).read_bytes())
        raw = case["model"]
        if hashlib.sha256(data(raw)).hexdigest() != visit["model_sha256"]:
            raise ValueError("original exact model hash differs")
        if (raw["names"] != NAMES or raw["sources"] != visit["profile_tuple"] or raw["k"] != 2
                or raw["profile_mode"] != "joint_intervals" or raw["mass_mode"] != "none"):
            raise ValueError("source/universe/uncertainty mapping differs")
        delta = Q(1, 10_000_000) * max(Q(1), Q(raw["mass"]))
        deltas.add(delta)
        try:
            completed = component_margins(raw, case["result"], delta)
        except (KeyError, ValueError, TypeError) as exc:
            completed = {"status": "HOLD_INVALID_OR_MISSING_PROOF", "error": str(exc), "bounds": []}
        cases.append({"source_visit": visit, "completed": completed})
    if len(deltas) != 1:
        raise ValueError("same-sample frozen margin differs across systems")
    components = [c["completed"] for c in cases]
    summary = union_summary(components, 120)
    original_counts = Counter(v["description"]["status"] for v in selected["target"]["visits"])
    if original_counts != {"EXACT_INFEASIBLE": 72, "EXACT_COMPATIBLE": 48}:
        raise ValueError("approved72/48 partition differs")
    ledger = {"configuration_sha256": sha(CONFIG), "manifest_sha256": sha(MANIFEST),
              "original_union_index_sha256": INDEX_HASH, "delta": next(iter(deltas)), "cases": cases, "summary": summary}
    write_json(PRIVATE / "interval_farkas_ledger.json", ledger)
    for path, key in ((PUBLIC / "interval_union_results.json", "original_union_results_sha256"),
                      (PUBLIC / "interval_union_report.md", "original_union_report_sha256")):
        if sha(path) != config[key]:
            raise ValueError("original frozen Stage3 artifact changed")
    valid_bounds = [b for c in components for b in c["bounds"]]
    ratios = [b["lower_margin"] / b["delta"] for b in valid_bounds]
    report = {"status": "COMPLETED_PROOF_ONLY_AUDIT", "new_interpretation_review": "PENDING_INDEPENDENT_ACTUAL_RECORD_REPLAY",
              "configuration_sha256": sha(CONFIG), "private_ledger_sha256": sha(PRIVATE / "interval_farkas_ledger.json"),
              "completed_utc": datetime.now(timezone.utc).isoformat(), "numerical_solver_calls": 0,
              "original_Stage3_HOLD_preserved": True, "all_initial_samples": 35,
              "inherited_witnessed_nonunique_unions": 34, "targeted_union_result": summary,
              "bound_attempts_prespecified": 288, "valid_bounds_checked": len(valid_bounds),
              "unavailable_due_to_invalid_premises": 288 - len(valid_bounds),
              "minimum_bound_over_original_delta_rounded": float(min(ratios)) if ratios else None,
              "limits": "Separate post-hoc algebraic proof completion from existing exact Farkas multipliers; known linear inequality reasoning; same independent boxes and original threshold. No new measurements, LPs, fit, uncertainty assumptions, confidence coverage or environmental truth."}
    write_json(PUBLIC / "interval_farkas_results.json", report)
    lines = ["# Post-hoc co-leader Farkas margin completion", "", report["limits"], "",
             "Independent actual-record replay remains required before positive interpretation. The original Stage3 HOLD/report is unchanged.", "",
             "All 35 samples remain accounted for: 34 witnessed non-unique unions are inherited. The remaining union has 120 components, with the frozen 72 infeasible / 48 feasible partition; all 288 competitor margins are prespecified.",
             f"New proof-only outcome: `{summary['status']}`. Exact threshold comparisons: `{json.dumps(summary['threshold_relations'], sort_keys=True)}`.",
             f"Valid bound checks: {len(valid_bounds)}/288. No numerical solver was imported or called.", "",
             "Each margin follows only after all competing co-leaders are exactly excluded and W is therefore always the maximum: nonnegative augmented Farkas multipliers give gamma=-a·h>0 and B=sum(b)>0, hence sW-sj>=gamma/B. This lower bound is compared strictly against the unchanged delta=1e-7*max(1,TMAC). Equality or a missing premise remains HOLD.", "",
             f"Configuration SHA-256: `{sha(CONFIG)}`.",
             f"Private proof-ledger SHA-256: `{report['private_ledger_sha256']}`.", "",
             "KEEP only independently replayed conditional certificates. HOLD physical box attainability, source realism, probability coverage, out-of-universe extrapolation and external accuracy. Do not rewrite the original numerical-gap history.", ""]
    (PUBLIC / "interval_farkas_report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--freeze", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze() if args.freeze else run(), indent=2))
