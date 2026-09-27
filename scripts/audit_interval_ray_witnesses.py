#!/usr/bin/env python3
"""Post-hoc finite-witness completion from stored exact rays; no new LP or fit.

Frozen producer and geometry artifacts are read-only. Original gap labels remain
unchanged; this separate audit records only implications of their proof objects.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"


def payload(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def enc(obj):
    if isinstance(obj, Q):
        return str(obj)
    if isinstance(obj, list):
        return [enc(v) for v in obj]
    if isinstance(obj, dict):
        return {key: enc(value) for key, value in obj.items()}
    return obj


def dot(a, b):
    return sum((Q(x) * Q(y) for x, y in zip(a, b)), Q(0))


def feasible(model, point):
    return (len(point) == model["n"] and all(Q(x) >= 0 for x in point)
            and all(dot(row, point) <= Q(rhs) for row, rhs in zip(model["G"], model["h"])))


def finite_ray_witness(model, objective, point, ray):
    objective, point, ray = [[Q(v) for v in values] for values in (objective, point, ray)]
    if len(objective) != model["n"] or len(ray) != model["n"] or not feasible(model, point):
        raise ValueError("no exactly feasible base point or inconsistent dimensions")
    if any(v < 0 for v in ray) or any(dot(row, ray) > 0 for row in model["G"]):
        raise ValueError("not an exact nonnegative recession ray")
    slope = dot(objective, ray)
    if slope >= 0:
        raise ValueError("ray does not strictly decrease this objective")
    # -1 is merely a convenient finite proof target, not an uncertainty bound,
    # data threshold or new measurement. Any strict negative target would work.
    t = max(Q(0), (dot(objective, point) + 1) / (-slope))
    witness = [x + t * d for x, d in zip(point, ray)]
    value = dot(objective, witness)
    if not feasible(model, witness) or value > -1:
        raise AssertionError("constructive exact witness verification failed")
    return {"base_point": point, "ray": ray, "objective": objective,
            "step": t, "constructed_point": witness, "objective_value": value,
            "verification": "exact rational nonnegativity, all Gx<=h, Gd<=0 and objective<=-1"}


def complete_pair(model, pair, base_feasibility=None, co_leaders=None, extra_points=()):
    names = model["names"]
    q = [Q(int(name == pair["a"]) - int(name == pair["b"])) for name in names]
    witnesses = []
    for key, sign in (("minimize", 1), ("maximize_negative", -1)):
        run = pair[key]
        expected = [sign * v for v in q]
        if [Q(v) for v in run["objective"]] != expected:
            raise ValueError("stored objective differs from declared family contrast")
        primal = run.get("primal", {})
        if primal.get("verified"):
            point = [Q(v) for v in primal["point"]]
            if not feasible(model, point):
                raise ValueError("stored primal is not exactly feasible")
            witnesses.append({"origin": key + "/primal", "point": point, "contrast": dot(q, point)})
        if run["status"] == "EXACT_UNBOUNDED":
            recession = run["recession"]
            if not recession.get("verified"):
                raise ValueError("unbounded label lacks verified ray record")
            derived = finite_ray_witness(model, expected, recession["point"], recession["ray"])
            witnesses.append({"origin": key + "/recession", "point": derived["constructed_point"],
                              "contrast": dot(q, derived["constructed_point"]), "construction": derived})
    extra = []
    if base_feasibility and base_feasibility.get("primal", {}).get("verified"):
        extra.append(("base_feasibility/primal", base_feasibility["primal"]["point"]))
    for name, info in sorted((co_leaders or {}).items()):
        if info.get("primal", {}).get("verified"):
            extra.append(("co_leaders/" + name + "/primal", info["primal"]["point"]))
    extra.extend(extra_points)
    for origin, raw_point in extra:
        point = [Q(v) for v in raw_point]
        if not feasible(model, point):
            raise ValueError("stored auxiliary point is not exactly feasible in base model")
        witnesses.append({"origin": origin, "point": point, "contrast": dot(q, point)})
    negative = next((w for w in witnesses if w["contrast"] < 0), None)
    positive = next((w for w in witnesses if w["contrast"] > 0), None)
    tied = next((w for w in witnesses if w["contrast"] == 0), None)
    status = "EXACT_BOTH_ORDERINGS_COMPLETED" if negative and positive else "EXACT_TIE_COMPLETED" if tied else "NO_OPPOSITE_SIGN_IN_STORED_PROOFS"
    return {"a": pair["a"], "b": pair["b"], "original_status": pair["classification"]["status"],
            "derived_status": status, "constructed_ray_points": sum("construction" in w for w in witnesses),
            "negative_witness": negative, "positive_witness": positive, "tie_witness": tied,
            "all_witnesses": witnesses}


def stored_points(case, prefix):
    result = case["result"]
    runs = [("feasibility", result["feasibility"])]
    runs += [("co_leaders/" + name, run) for name, run in sorted(result["co_leaders"].items())]
    for p in result["pairs"]:
        runs += [("pairs/" + p["a"] + "/" + p["b"] + "/" + key, p[key])
                 for key in ("minimize", "maximize_negative")]
    return [(prefix + "/" + name + "/primal", run["primal"]["point"])
            for name, run in runs if run.get("primal", {}).get("verified")]


def audit_case(case, extra_points=()):
    model, result = case["model"], case["result"]
    outcomes = {}
    for pair in result["pairs"]:
        if pair["classification"]["status"] != "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP":
            continue
        if not any(pair[key]["status"] == "EXACT_UNBOUNDED" for key in ("minimize", "maximize_negative")):
            continue
        key = "|".join(sorted((pair["a"], pair["b"])))
        outcomes[key] = complete_pair(model, pair, result["feasibility"], result["co_leaders"], extra_points)
    return outcomes


def run():
    index_raw = (PRIVATE / "interval_index.json").read_bytes()
    index = json.loads(index_raw)
    frozen_raw = (PUBLIC / "interval_results.json").read_bytes()
    frozen = json.loads(frozen_raw)
    geometry_raw = (PUBLIC / "interval_geometry.json").read_bytes()
    if frozen["status"] != "COMPLETE" or frozen["private_index_sha256"] != sha(index_raw):
        raise ValueError("frozen producer and index identities disagree")
    cases, case_hashes = {}, {}
    for item in index["records"]:
        mid = item["model_sha256"]
        if mid in cases:
            continue
        raw = (PRIVATE / "interval_cases" / ("interval_case_" + mid + ".json")).read_bytes()
        if sha(raw) != item["case_sha256"]:
            raise ValueError("source case hash differs from frozen index")
        case = json.loads(raw)
        if sha(payload(case["model"])) != mid:
            raise ValueError("source model hash differs from frozen index")
        cases[mid], case_hashes[mid] = case, item["case_sha256"]
    counterparts = defaultdict(dict)
    for item in index["records"]:
        key = (item["universe"], item["k"], item["profile_mode"], item["sample_zero_based_index"])
        counterparts[key][item["mass_mode"]] = item["model_sha256"]
    extra_by_model = {}
    for pair in counterparts.values():
        mid, mass_mid = pair["none"], pair["historical_80_120_band"]
        base, mass = cases[mid]["model"], cases[mass_mid]["model"]
        if (base["names"] != mass["names"] or base["G"] != mass["G"][:-2]
                or base["h"] != mass["h"][:-2]):
            raise ValueError("paired mass model is not the same base model plus two constraints")
        extra_by_model[mid] = stored_points(cases[mass_mid], "case/" + mass_mid)
    case_cache, private = {}, []
    for mid, case in cases.items():
        outcomes = audit_case(case, extra_by_model.get(mid, ()))
        case_cache[mid] = {
            "outcomes": outcomes, "overall_status": case["result"]["overall_status"],
            "pair_status": {"|".join(sorted((p["a"], p["b"]))): p["classification"]["status"] for p in case["result"]["pairs"]}}
        if outcomes:
            private.append({"model_sha256": mid, "source_case_sha256": case_hashes[mid], "pairs": outcomes})
    panels, paired = defaultdict(list), defaultdict(dict)
    for item in index["records"]:
        info = case_cache[item["model_sha256"]]
        key = (item["universe"], item["k"], item["profile_mode"], item["mass_mode"])
        panels[key].append(info)
        paired[key[:3] + (item["sample_zero_based_index"],)][item["mass_mode"]] = info
    aggregates = []
    for key, rows in sorted(panels.items()):
        if len(rows) != 35:
            raise ValueError("all35 samples must remain in every panel")
        outcomes = [outcome for row in rows for outcome in row["outcomes"].values()]
        aggregates.append({"universe": key[0], "k": key[1], "profile_mode": key[2], "mass_mode": key[3],
            "initial_samples": 35, "samples_with_attempted_ray_completion": sum(bool(row["outcomes"]) for row in rows),
            "pair_attempts": len(outcomes), "derived_status_counts": dict(Counter(o["derived_status"] for o in outcomes)),
            "finite_ray_points_constructed": sum(o["constructed_ray_points"] for o in outcomes)})
    mass_counts = defaultdict(Counter)
    for key, pair in paired.items():
        if set(pair) != {"none", "historical_80_120_band"}:
            raise ValueError("incomplete mass/no-mass pair")
        a, b = pair["none"], pair["historical_80_120_band"]
        group = key[:3]
        mass_counts[group]["initial_samples"] += 1
        if a["overall_status"] != "EXACT_COMPATIBLE" or b["overall_status"] != "EXACT_COMPATIBLE":
            continue
        for pair_key, status in b["pair_status"].items():
            if status not in ("VERIFIED_A_GREATER_B", "VERIFIED_B_GREATER_A"):
                continue
            if a["pair_status"].get(pair_key) != "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP":
                continue
            mass_counts[group]["mass_only_orders_originally_gap_labeled"] += 1
            completed = a["outcomes"].get(pair_key, {})
            if completed.get("derived_status") in ("EXACT_BOTH_ORDERINGS_COMPLETED", "EXACT_TIE_COMPLETED"):
                mass_counts[group]["gap_labels_with_exact_no_mass_ambiguity_completed_from_stored_rays"] += 1
            else:
                mass_counts[group]["gap_labels_not_resolved_by_this_audit"] += 1
    ledger = payload(enc({"private_index_sha256": sha(index_raw), "cases": private}))
    (PRIVATE / "interval_ray_witnesses.json").write_bytes(ledger)
    report = {"status": "PASS", "analysis_type": "post-hoc constructive proof completion; no new LP, fit, input or uncertainty assumption",
        "script_sha256": sha(Path(__file__).read_bytes()), "private_index_sha256": sha(index_raw),
        "frozen_producer_results_sha256": sha(frozen_raw), "frozen_geometry_results_sha256": sha(geometry_raw),
        "private_witness_ledger_sha256": sha(ledger), "unique_cases_read": len(case_cache),
        "unique_cases_with_attempted_completion": len(private),
        "unique_pair_attempts": sum(len(c["pairs"]) for c in private),
        "unique_derived_status_counts": dict(Counter(p["derived_status"] for c in private for p in c["pairs"].values())),
        "panels": aggregates,
        "mass_only_order_gap_completion": [{"universe": k[0], "k": k[1], "profile_mode": k[2], **dict(v)}
                                           for k, v in sorted(mass_counts.items())],
        "limits": "Original gap labels and reports are unchanged. Completion is conditional on the original independent boxes. Paired mass-band points are reused only after every original no-mass inequality is verified, not by imposing the mass band on that model. Constructing a witness from an exact recession ray is not additional data or a new uncertainty choice."}
    if (PUBLIC / "interval_results.json").read_bytes() != frozen_raw or (PUBLIC / "interval_geometry.json").read_bytes() != geometry_raw:
        raise RuntimeError("frozen artifact changed during post-hoc audit")
    (PUBLIC / "interval_ray_results.json").write_bytes(payload(report))
    (PUBLIC / "interval_ray_report.md").write_text(render(report), encoding="utf-8", newline="\n")
    return report


def render(report):
    lines = ["# Post-hoc finite witnesses from existing recession proofs", "",
        "No LP or fit was rerun. The frozen interval producer and geometry artifacts, including their original gap labels, remain unchanged.", "",
        "For an exactly feasible x and recession ray d with q·d<0, set `t=max(0,(q·x+1)/(-q·d))`. Then `x+t*d` is an exactly feasible finite point with `q·(x+t*d)<=-1`. The number1 is only a convenient proof target; it is not a new interval, confidence level, or empirical measurement. Every constructed point was rechecked with rational arithmetic against all original inequalities.", "",
        f"Read {report['unique_cases_read']} unique cases; attempted {report['unique_pair_attempts']} previously gap-labeled pair decisions containing an exact unbounded-ray proof.",
        f"Derived statuses: `{json.dumps(report['unique_derived_status_counts'], sort_keys=True)}`.", "",
        "## Previously gap-labeled orders first verified with the mass band", "",
        "The following compares original mass-band and no-mass results at unchanged inputs. Verified paired mass-band points are additionally checked against every original no-mass inequality before witness reuse; this does not impose a mass assumption on the no-mass model. These are additional proofs of ambiguity already implied by the no-mass model, not increased empirical evidence.", "",
        "| Universe | k | Uncertainty | Samples | Original mass-only order gaps | No-mass ambiguity completed from stored rays | Not completed |",
        "|---|---:|---|---:|---:|---:|---:|"]
    for row in report["mass_only_order_gap_completion"]:
        lines.append(f"| {row['universe']} | {row['k']} | {row['profile_mode']} | {row['initial_samples']} | {row.get('mass_only_orders_originally_gap_labeled',0)} | {row.get('gap_labels_with_exact_no_mass_ambiguity_completed_from_stored_rays',0)} | {row.get('gap_labels_not_resolved_by_this_audit',0)} |")
    lines += ["", "All24 labeled panels, including zero-attempt and incompatible cases, remain in the JSON; source universes are not pooled. The private ledger links each constructed point to its source case hash and original proof location.",
        f"Private witness ledger SHA-256: `{report['private_witness_ledger_sha256']}`.", "",
        "Reproduce: `python scripts/audit_interval_ray_witnesses.py`. No third-party material is newly redistributed.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    result = run()
    print(json.dumps({key: result[key] for key in ("status", "unique_pair_attempts", "unique_derived_status_counts")}, indent=2))
