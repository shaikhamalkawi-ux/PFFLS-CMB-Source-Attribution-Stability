#!/usr/bin/env python3
"""Independent original-input replay of post-hoc Farkas margins; no LPs."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import time

import verify_interval_certificate_records as v
import verify_interval_union_records as u

ROOT, PUBLIC, PRIVATE = v.ROOT, v.PUBLIC, v.PRIVATE
PROTOCOL_HASH = "f67d9288b8ed6e546c01f7a24af1993b37bb4a95b78a7bd1b5b4222a69391783"
PRODUCER_HASH = "b5a95a583c533e9dd28cccd6a2737de1bf4b06425b986cad2b20510fe84f54a0"
TESTS_HASH = "88f1dd649e9bc8bda30da3535e056d9972d20b50380e93ec226dd8ba5c421b78"
UNION_VERIFIER_HASH = "2c68cb669ceaff1d95b419e517be4f96f32c37425f2529cab2f2a4ee437dbd5b"
CONFIG_HASH = "eb76edf1493a94e7aae172039ea636f47557f0e98f102865036e702a9d6a005b"
LEDGER_HASH = "b4148121cec2e76b91a6ed4ec8f5818c9d2118b2eaac9f80e56df7bf61854c80"
require = v.require


def rows_for(model, leader):
    require(leader in model["names"], "unknown competitor/leader")
    j, n = model["names"].index(leader), model["n"]
    return [[Q(int(i == k)-int(i == j)) for i in range(n)] for k in range(n) if k != j]


def compare_threshold(bound, delta):
    require(delta > 0, "nonpositive frozen threshold")
    return "ABOVE" if bound > delta else "EQUAL" if bound == delta else "BELOW"


def derive_component(model, result, delta):
    n, names, G, h = model["n"], model["names"], model["G"], model["h"]
    require(n >= 2 and len(names) == len(set(names)) == n and len(G) == len(h)
            and all(len(row) == n for row in G), "invalid dimensions/names")
    require(delta > 0, "nonpositive frozen delta")
    base = result["feasibility"]
    v.verify_feasibility(base, G, h, n, Counter())
    if result["overall_status"] == "EXACT_INFEASIBLE":
        require(base["status"] == "EXACT_INFEASIBLE", "false infeasible component")
        y = v.vector(base["farkas"]["y"])
        residual = [sum(y[i]*G[i][j] for i in range(len(G))) for j in range(n)]
        return {"status": "EXACT_INFEASIBLE", "y": y, "residual": residual,
                "h_dot_y": v.dot(h, y), "bounds": []}
    require(result["overall_status"] == "EXACT_COMPATIBLE" and base["status"] == "EXACT_FEASIBLE",
            "unresolved component cannot establish universal-leader premise")
    base_point = v.primal_point(G, h, base["primal"]["point"], n)
    co = result["co_leaders"]
    require(set(co) == set(names), "all competitor proofs required")
    winners = [name for name in names if co[name]["status"] == "EXACT_FEASIBLE"]
    require(len(winners) == 1, "not exactly one witnessed possible leader")
    leader = winners[0]
    # Independently verify every augmented system before computing any ratio.
    for name in names:
        info, D = co[name], rows_for(model, name)
        require(info["status"] == ("EXACT_FEASIBLE" if name == leader else "EXACT_INFEASIBLE"),
                "competitor has no exact exclusion")
        v.verify_feasibility(info, G+D, h+[Q(0)]*(n-1), n, Counter())
    leader_point = v.vector(co[leader]["primal"]["point"])
    bounds = []
    for name in names:
        if name == leader:
            continue
        D = rows_for(model, name)
        y = v.vector(co[name]["farkas"]["y"])
        a, b = y[:len(G)], y[len(G):]
        require(len(b) == n-1 and all(x >= 0 for x in a+b), "multiplier row partition/sign mismatch")
        gamma = -v.dot(a, h)
        B = sum(b, Q(0))
        require(gamma > 0 and B > 0, "gamma/B requires strictly positive gamma and B")
        residual = [sum(a[i]*G[i][j] for i in range(len(G))) +
                    sum(b[i]*D[i][j] for i in range(n-1)) for j in range(n)]
        require(all(x >= 0 for x in residual), "negative augmented column residual")
        lower = gamma/B
        bounds.append({"competitor": name, "a": a, "b": b, "D_rows": D,
                       "augmented_residual": residual, "gamma": gamma, "B": B,
                       "lower_margin": lower, "leader": leader, "delta": delta,
                       "threshold_relation": compare_threshold(lower, delta)})
    return {"status": "EXACT_FEASIBLE_ALL_MARGIN_PREMISES", "leader": leader,
            "base_point": base_point, "leader_point": leader_point, "bounds": bounds,
            "all_margins_above_delta": all(b["lower_margin"] > delta for b in bounds)}


def summarize(components, total):
    require(total > 0 and len(components) <= total, "invalid component coverage")
    viable = [c for c in components if c["status"] == "EXACT_FEASIBLE_ALL_MARGIN_PREMISES"]
    names = sorted({c["leader"] for c in viable})
    complete = len(components) == total
    empty = complete and all(c["status"] == "EXACT_INFEASIBLE" for c in components)
    certified = (complete and bool(viable) and len(names) == 1
                 and all(c["status"] in ("EXACT_INFEASIBLE", "EXACT_FEASIBLE_ALL_MARGIN_PREMISES") for c in components)
                 and all(c["all_margins_above_delta"] for c in viable))
    status = ("EXACT_EMPTY_UNION_NOT_A_LEADER_CERTIFICATE" if empty else
              "POSTHOC_CERTIFIED_UNIQUE_UNION_LEADER_ABOVE_ORIGINAL_MARGIN" if certified else
              "HOLD_MISSING_INVALID_UNRESOLVED_OR_INSUFFICIENT_MARGIN")
    return {"status": status, "expected_systems": total, "components_checked": len(components),
            "component_status_counts": dict(Counter(c["status"] for c in components)),
            "feasible_component_leaders": names,
            "threshold_relations": dict(Counter(b["threshold_relation"] for c in viable for b in c["bounds"])),
            "bounds_checked": sum(len(c["bounds"]) for c in viable)}


def verify():
    started = time.monotonic()
    v.check_hash(Path(v.__file__), u.VERIFIER_HASH)
    v.check_hash(Path(u.__file__), UNION_VERIFIER_HASH)
    v.check_hash(ROOT / "scripts/audit_interval_farkas_margin.py", PRODUCER_HASH)
    v.check_hash(ROOT / "tests/test_interval_farkas_margin.py", TESTS_HASH)
    v.check_hash(PUBLIC / "interval_farkas_protocol_PROPOSED.md", PROTOCOL_HASH)
    config_path = PUBLIC / "interval_farkas_configuration.json"
    config = u.read(config_path, CONFIG_HASH)
    config_hash = v.digest(config_path.read_bytes())
    require(config["script_sha256"] == PRODUCER_HASH and config["tests_sha256"] == TESTS_HASH
            and config["protocol_sha256"] == PROTOCOL_HASH, "proof-layer freeze mismatch")
    require(config["solver_calls_permitted"] == 0 and config["frozen_before_first_field_gamma_over_B_evaluation"] is True, "freeze/no-LP rule")
    require(config["synthetic_gate"]["status"] == "PASS", "synthetic gate missing")
    original = u.read(PRIVATE / "interval_union_index.json", u.INDEX_HASH)
    original_config = u.read(PUBLIC / "interval_union_configuration_v2.json", u.CONFIG_HASH)
    v.check_hash(PUBLIC / "interval_union_results.json", config["original_union_results_sha256"])
    v.check_hash(PUBLIC / "interval_union_report.md", config["original_union_report_sha256"])
    prior_review = u.read(PUBLIC / "interval_union_certificate_verification.json")
    require(prior_review["status"] == "PASS" and prior_review["private_index_sha256"] == u.INDEX_HASH
            and prior_review["verifier_sha256"] == UNION_VERIFIER_HASH and prior_review["all_samples"] == 35,
            "faithful independent Stage3 verification prerequisite absent")
    require(config["original_union_index_sha256"] == u.INDEX_HASH and config["original_union_configuration_sha256"] == u.CONFIG_HASH,
            "original union lineage mismatch")
    manifest = u.read(PRIVATE / "interval_farkas_manifest.json", config["manifest_sha256"])
    require([r["sample_zero_based_index"] for r in original["records"]] == list(range(35)), "all35 identity/accounting")
    targets = [r for r in original["records"] if r["outcome"]["status"] == "HOLD_INCOMPLETE_OR_UNRESOLVED_UNION"]
    inherited = [r["sample_zero_based_index"] for r in original["records"] if r["outcome"]["status"] == "EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER"]
    require(len(targets) == 1 and len(inherited) == 34 and manifest["target"] == targets[0]
            and manifest["inherited_nonunique_sample_indices"] == inherited, "target/inherited partition mismatch")
    target = targets[0]
    require(len(target["visits"]) == 120, "incomplete target union")
    report = u.read(PUBLIC / "interval_farkas_results.json")
    require(report["private_ledger_sha256"] == LEDGER_HASH, "frozen proof-ledger identity mismatch")
    ledger = u.read(PRIVATE / "interval_farkas_ledger.json", LEDGER_HASH)
    require(ledger["configuration_sha256"] == report["configuration_sha256"] == config_hash
            and ledger["manifest_sha256"] == config["manifest_sha256"]
            and ledger["original_union_index_sha256"] == u.INDEX_HASH, "derived ledger identity mismatch")
    require(datetime.fromisoformat(config["frozen_utc"]) < datetime.fromisoformat(report["completed_utc"]), "freeze after completion")
    receptors, profiles, _ = v.load_original_inputs(v.DEFAULT_INPUT)
    grid_config = u.read(PUBLIC / "joint_profile_configuration.json", u.GRID_HASH)
    grid = [list(t) for t in itertools.product(*(grid_config["families"].get(s, [s]) for s in v.SOURCES))]
    require([item["profile_tuple"] for item in target["visits"]] == grid == original_config["tuple_order"], "actual historical union coverage")
    require(len(ledger["cases"]) == 120, "derived ledger missing/extra component")
    rec = receptors[target["sample_zero_based_index"]]
    require(target["sample"] == {k: rec[k] for k in v.IDENTITY}, "original receptor identity")
    delta = Q(1, 10_000_000)*max(Q(1), v.fraction(rec["TMAC"]))
    require(v.fraction(ledger["delta"]) == delta, "unchanged threshold not retained")
    components = []
    nonzero_residual = 0
    for number, (visit, saved) in enumerate(zip(target["visits"], ledger["cases"])):
        require(time.monotonic()-started < 600, "bounded replay exceeded")
        require(saved["source_visit"] == visit, "source proof provenance mismatch")
        model = u.tuple_model(rec, profiles, visit["profile_tuple"], grid)
        mid = v.digest(v.json_bytes(v.encode(model)))
        require(mid == visit["model_sha256"], "derived bound model not original exact tuple")
        if visit["origin"] == "INHERITED_STAGE2":
            path = PRIVATE / "interval_cases" / ("interval_case_"+mid+".json")
        else:
            require(visit["origin"] == "NEW_UNION_MODEL", "unknown source provenance")
            path = PRIVATE / "interval_union_cases" / ("u_"+mid+".json")
        case = u.read(path, visit["case_sha256"])
        require(case["model"] == v.encode(model), "stored source model differs")
        if visit["origin"] == "NEW_UNION_MODEL":
            require(case["profile_tuple"] == visit["profile_tuple"], "new case tuple differs")
        completed = derive_component(model, case["result"], delta)
        require(v.encode(completed) == saved["completed"], "saved exact Farkas derivation differs")
        components.append(completed)
        nonzero_residual += sum(any(x > 0 for x in bound["augmented_residual"]) for bound in completed["bounds"])
    summary = summarize(components, 120)
    require(summary == ledger["summary"] == report["targeted_union_result"], "union margin conclusion mismatch")
    require(summary["component_status_counts"] == {"EXACT_INFEASIBLE": 72, "EXACT_FEASIBLE_ALL_MARGIN_PREMISES": 48}, "component partition differs")
    bounds = [b for c in components for b in c["bounds"]]
    require(len(bounds) == report["valid_bounds_checked"] == report["bound_attempts_prespecified"] == 288, "all288 denominator mismatch")
    require(report["unavailable_due_to_invalid_premises"] == 0 and report["numerical_solver_calls"] == 0
            and report["original_Stage3_HOLD_preserved"] is True and report["all_initial_samples"] == 35
            and report["inherited_witnessed_nonunique_unions"] == 34, "all35/failures/no-LP accounting")
    minimum = min(b["lower_margin"] for b in bounds)
    require(float(minimum/delta) == report["minimum_bound_over_original_delta_rounded"], "rounded public minimum ratio mismatch")
    v.check_hash(PUBLIC / "interval_union_results.json", config["original_union_results_sha256"])
    v.check_hash(PUBLIC / "interval_union_report.md", config["original_union_report_sha256"])
    return {"status": "PASS", "completed_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.monotonic()-started, 3),
            "verifier_sha256": v.digest(Path(__file__).read_bytes()),
            "configuration_sha256": config_hash, "private_ledger_sha256": report["private_ledger_sha256"],
            "original_stage3_index_sha256": u.INDEX_HASH, "all_initial_samples": 35, "inherited_nonunique": 34,
            "original_models_reconstructed": 120, "exact_base_infeasibilities": 72,
            "exact_base_and_W_witness_pairs": 48, "exact_competitor_exclusions": len(bounds),
            "strictly_positive_augmented_residual_vectors": nonzero_residual,
            "universal_leader_family": summary["feasible_component_leaders"],
            "threshold_relations": summary["threshold_relations"], "separate_proof_layer_outcome": summary["status"],
            "minimum_lower_margin_exact": str(minimum), "original_delta_exact": str(delta),
            "minimum_margin_over_delta_exact": str(minimum/delta),
            "minimum_margin_over_delta_approximate": float(minimum/delta),
            "original_Stage3_HOLD_preserved": True, "LPs_rerun": 0,
            "limits": "Post-hoc exact proof reuse under unchanged deterministic boxes and finite profile systems; not new data, a new theorem, statistical coverage, physical realizability or environmental validation."}


if __name__ == "__main__":
    result = verify()
    (PUBLIC / "interval_farkas_certificate_verification.json").write_bytes(v.json_bytes(result))
    print(json.dumps(result, indent=2))
