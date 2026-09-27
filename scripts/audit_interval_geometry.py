#!/usr/bin/env python3
"""Post-hoc descriptive audit of completed interval proofs; no fits or LP solves.

The frozen field producer is intentionally not imported or modified.
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


def payload(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def zero_lower_columns(L, U, names) -> list[str]:
    if not L or len(L) != len(U) or any(len(row) != len(names) for row in L + U):
        raise ValueError("inconsistent interval matrix dimensions")
    lower = [[Q(v) for v in row] for row in L]
    upper = [[Q(v) for v in row] for row in U]
    if any(lo < 0 or hi < lo for row_l, row_u in zip(lower, upper) for lo, hi in zip(row_l, row_u)):
        raise ValueError("nonnegative ordered profile intervals are required")
    return [name for j, name in enumerate(names) if all(row[j] == 0 for row in lower)]


def verify_box_shape(model: dict) -> None:
    if model["n"] != len(model["names"]):
        raise ValueError("source dimension differs from labels")
    L, U = model["L"], model["U"]
    zero_lower_columns(L, U, model["names"])
    expected_G = [[Q(v) for v in row] for row in L] + [[-Q(v) for v in row] for row in U]
    expected_h = [Q(v) for v in model["receptor_high"]] + [-Q(v) for v in model["receptor_low"]]
    if model["mass_mode"] == "historical_80_120_band":
        expected_G += [[Q(1)] * model["n"], [Q(-1)] * model["n"]]
        expected_h += [Q(6, 5) * Q(model["mass"]), -Q(4, 5) * Q(model["mass"])]
    elif model["mass_mode"] != "none":
        raise ValueError("unrecognized mass model")
    if expected_G != [[Q(v) for v in row] for row in model["G"]] or expected_h != [Q(v) for v in model["h"]]:
        raise ValueError("extra/missing constraints invalidate the claimed box recession criterion")


def strict_direction(pair: dict):
    status = pair["classification"]["status"]
    if status == "VERIFIED_A_GREATER_B":
        return pair["a"], pair["b"]
    if status == "VERIFIED_B_GREATER_A":
        return pair["b"], pair["a"]
    return None


def describe_case(model: dict, result: dict) -> dict:
    verify_box_shape(model)
    zeros = zero_lower_columns(model["L"], model["U"], model["names"])
    unbounded = [name for name, bounds in result["source_bounds"].items()
                 if bounds["maximize_negative"]["status"] == "EXACT_UNBOUNDED"]
    if model["mass_mode"] != "none" and unbounded:
        raise AssertionError("nonnegative sources with finite mass upper cannot be unbounded")
    if model["mass_mode"] == "none":
        if any(name not in zeros for name in unbounded):
            raise AssertionError("unbounded source is not an all-zero lower column")
        for name in zeros:
            bounds = result["source_bounds"].get(name)
            if bounds is not None and "verified_lower_bound" in bounds["maximize_negative"]:
                raise AssertionError("finite source upper bound contradicts zero-column recession ray")
    pairs = {"|".join(sorted((p["a"], p["b"]))): {
        "status": p["classification"]["status"], "direction": strict_direction(p)} for p in result["pairs"]}
    base = {key: model[key] for key in ("L", "U", "receptor_low", "receptor_high", "sources", "names", "mass", "k", "profile_mode")}
    return {"names": model["names"], "base_model_signature": sha(payload(base)),
            "zero_lower_columns": zeros, "unbounded_sources": unbounded,
            "compatibility": result["overall_status"], "pairs": pairs,
            "unique_leaders": result.get("verified_unique_leaders_above_margin_threshold", []),
            "possible_co_leaders": result.get("exact_possible_co_leaders", []),
            "impossible_co_leaders": result.get("exact_impossible_co_leaders", []),
            "unresolved_co_leaders": result.get("unresolved_co_leaders", [])}


def compare_mass_pair(none: dict, mass: dict) -> dict:
    if (none["names"] != mass["names"] or none["zero_lower_columns"] != mass["zero_lower_columns"]
            or none["base_model_signature"] != mass["base_model_signature"]):
        raise ValueError("mass comparison changed source universe or profile intervals")
    none_ok, mass_ok = none["compatibility"] == "EXACT_COMPATIBLE", mass["compatibility"] == "EXACT_COMPATIBLE"
    if none["compatibility"] == "EXACT_INFEASIBLE" and mass_ok:
        raise AssertionError("adding mass constraints cannot make an exactly empty set nonempty")
    counts = Counter()
    if mass_ok and none_ok:
        if set(none["pairs"]) != set(mass["pairs"]):
            raise ValueError("pairwise decisions changed dimensions")
        for key, post in mass["pairs"].items():
            prior = none["pairs"][key]
            if post["direction"] is None:
                continue
            counts["mass_verified_pair_orders"] += 1
            if prior["direction"] == post["direction"]:
                counts["pair_orders_verified_in_both"] += 1
            elif prior["direction"] is not None:
                raise AssertionError("nonempty nested mass model has opposite verified pair order")
            else:
                counts["pair_orders_verified_only_after_mass_band"] += 1
                if prior["status"] in ("EXACT_BOTH_ORDERINGS_WITNESSED", "EXACT_TIE_WITNESSED"):
                    counts["mass_only_pair_orders_from_exact_no_mass_ambiguity"] += 1
                else:
                    counts["mass_only_pair_orders_from_no_mass_verification_gap_or_near_zero"] += 1
        if none["unique_leaders"] and mass["unique_leaders"] and none["unique_leaders"] != mass["unique_leaders"]:
            raise AssertionError("nonempty nested mass model has a different verified unique leader")
        if mass["unique_leaders"] and not none["unique_leaders"]:
            counts["unique_leader_verified_only_after_mass_band_samples"] += 1
            counts["mass_only_unique_leader_from_exact_no_mass_multiple_co_leaders_samples"] += int(len(none["possible_co_leaders"]) >= 2)
        if none["unique_leaders"] and mass["unique_leaders"]:
            counts["same_unique_leader_verified_in_both_samples"] += 1
        if set(mass["possible_co_leaders"]) & set(none["impossible_co_leaders"]):
            raise AssertionError("mass-feasible co-leader was proved impossible without mass constraints")
        counts["no_mass_possible_co_leaders_proved_impossible_after_mass"] += len(
            set(none["possible_co_leaders"]) & set(mass["impossible_co_leaders"]))
    elif mass_ok:
        counts["mass_feasible_but_no_mass_numerically_unresolved_samples"] += 1
        # Such a mass witness also proves nonempty no-mass compatibility; the
        # producer status is nevertheless preserved, not rewritten post-hoc.
    elif none_ok and mass["compatibility"] == "EXACT_INFEASIBLE":
        counts["compatible_without_mass_but_mass_band_incompatible_samples"] += 1
    return {"feasibility_pair": none["compatibility"] + " -> " + mass["compatibility"],
            "counts": dict(counts), "both_sets_exactly_compatible": none_ok and mass_ok}


def run() -> dict:
    index_bytes = (PRIVATE / "interval_index.json").read_bytes()
    index = json.loads(index_bytes)
    frozen_report = json.loads((PUBLIC / "interval_results.json").read_bytes())
    if frozen_report["status"] != "COMPLETE" or frozen_report["private_index_sha256"] != sha(index_bytes):
        raise ValueError("completed frozen producer/index identities do not agree")
    if len(index["records"]) != 840:
        raise ValueError("not all Stage2 labeled records were completed")
    cache, grouped = {}, defaultdict(dict)
    geometry_groups = defaultdict(list)
    for item in index["records"]:
        mid = item["model_sha256"]
        if mid not in cache:
            path = PRIVATE / "interval_cases" / ("interval_case_" + mid + ".json")
            raw = path.read_bytes()
            if sha(raw) != item["case_sha256"]:
                raise ValueError("case hash does not match completed index")
            case = json.loads(raw)
            if sha(payload(case["model"])) != mid:
                raise ValueError("model hash does not match completed index")
            cache[mid] = describe_case(case["model"], case["result"])
        description = cache[mid]
        group = (item["universe"], item["k"], item["profile_mode"])
        pair_key = group + (item["sample_zero_based_index"],)
        if item["mass_mode"] in grouped[pair_key]:
            raise ValueError("duplicate sample/panel/mass record")
        grouped[pair_key][item["mass_mode"]] = description
        if item["mass_mode"] == "none":
            geometry_groups[group].append(description)
    geometry = []
    for group, cases in sorted(geometry_groups.items()):
        if len(cases) != 35:
            raise ValueError("a geometry panel does not retain all35 samples")
        feasible = [case for case in cases if case["compatibility"] == "EXACT_COMPATIBLE"]
        geometry.append({"universe": group[0], "k": group[1], "profile_mode": group[2],
            "initial_samples": len(cases), "exactly_compatible_samples": len(feasible),
            "zero_lower_column_occurrences_all35": dict(Counter(name for case in cases for name in case["zero_lower_columns"])),
            "nonempty_samples_with_zero_lower_column": sum(bool(case["zero_lower_columns"]) for case in feasible),
            "expected_unbounded_source_occurrences_nonempty_sets": dict(Counter(name for case in feasible for name in case["zero_lower_columns"])),
            "exact_ray_verified_source_occurrences": dict(Counter(name for case in feasible for name in case["unbounded_sources"])),
            "zero_column_unbounded_directions_without_stored_exact_ray": sum(len(set(case["zero_lower_columns"]) - set(case["unbounded_sources"])) for case in feasible)})
    comparisons = defaultdict(list)
    for pair_key, pair in grouped.items():
        if set(pair) != {"none", "historical_80_120_band"}:
            raise ValueError("a paired mass comparison is incomplete")
        comparisons[pair_key[:3]].append(compare_mass_pair(pair["none"], pair["historical_80_120_band"]))
    mass = []
    for group, cases in sorted(comparisons.items()):
        if len(cases) != 35:
            raise ValueError("a mass comparison panel does not retain all35 samples")
        mass.append({"universe": group[0], "k": group[1], "profile_mode": group[2],
                     "initial_samples": len(cases),
                     "both_sets_exactly_compatible_samples": sum(c["both_sets_exactly_compatible"] for c in cases),
                     "feasibility_pair_counts": dict(Counter(c["feasibility_pair"] for c in cases)),
                     "decision_counts": dict(sum((Counter(c["counts"]) for c in cases), Counter()))})
    report = {"status": "PASS", "analysis_type": "post-hoc descriptive geometry/proof-record audit; no new fits or LPs",
              "producer_script_sha256": frozen_report["script_sha256"],
              "configuration_sha256": frozen_report["configuration_sha256"],
              "private_index_sha256": sha(index_bytes), "audit_script_sha256": sha(Path(__file__).read_bytes()),
              "labeled_records_checked": len(index["records"]), "unique_cases_checked": len(cache),
              "no_mass_geometry": geometry, "paired_mass_band_audit": mass,
              "claim_limit": "Conditional independent-box geometry; source profile-system fixed; massband is an assumption, not added evidence or physical conservation."}
    (PUBLIC / "interval_geometry.json").write_bytes(payload(report))
    (PUBLIC / "interval_geometry.md").write_text(render(report), encoding="utf-8", newline="\n")
    return report


def render(report: dict) -> str:
    lines = ["# Post-hoc interval geometry and mass-assumption audit", "",
             "This reads the completed frozen Stage2 proof records. It performs no new fit or LP and changes no uncertainty multiplier, input, or threshold. The geometry is established linear algebra, not a novelty claim.", "",
             "## Exact boundedness criterion and assumptions", "",
             "For a **nonempty** independent-box model without an added mass constraint, with `0 <= L <= U` and `s >= 0`, the recession cone is", "",
             "```text", "{d >= 0: Ld <= 0, -Ud <= 0} = {d >= 0: Ld = 0}.", "```", "",
             "Because all entries of L and d are nonnegative, a positive d_j is possible exactly when every entry of column L[:,j] is zero. Thus the cone is the nonnegative span of those coordinate directions. A source coordinate is unbounded above if and only if its entire lower-profile column is zero. If none is zero, the compatible set is bounded. Empty sets are not called unbounded. The statement does not cover signed sources, correlated-profile constraints, extra equalities, or a different uncertainty model.", "",
             "Adding the finite historical mass upper bound blocks every nonzero nonnegative recession ray. This is a consequence of an extra assumption; it is not newly measured information or proof that the bound is physically correct.", "",
             "## No-mass geometry", "",
             "| Universe | k | Uncertainty | Compatible /35 | Compatible with zero lower column | Exact ray occurrences | Missing stored rays |",
             "|---|---:|---|---:|---:|---:|---:|"]
    for row in report["no_mass_geometry"]:
        lines.append(f"| {row['universe']} | {row['k']} | {row['profile_mode']} | {row['exactly_compatible_samples']}/35 | {row['nonempty_samples_with_zero_lower_column']} | {sum(row['exact_ray_verified_source_occurrences'].values())} | {row['zero_column_unbounded_directions_without_stored_exact_ray']} |")
    lines += ["", "Source-family column occurrences are given explicitly in `interval_geometry.json`, separately for all35 samples and nonempty sets.", "",
              "## Decisions first verified after imposing the historical mass band", "",
              "These are paired results with the same receptor, profiles, source universe, uncertainty multiplier and treatment. Counts of new pair orders are restricted to pairs for which both complete sets are exactly compatible. A missing no-mass proof is distinguished from a verified no-mass reversal/tie. Incompatible mass-band cases produce no winner claim.", "",
              "| Universe | k | Uncertainty | Both sets compatible /35 | Pair orders only after band | Of these: no-mass reversal/tie witnessed | Unique leader only after band | No-mass compatible, band incompatible |",
              "|---|---:|---|---:|---:|---:|---:|---:|"]
    for row in report["paired_mass_band_audit"]:
        c = row["decision_counts"]
        lines.append(f"| {row['universe']} | {row['k']} | {row['profile_mode']} | {row['both_sets_exactly_compatible_samples']}/35 | {c.get('pair_orders_verified_only_after_mass_band',0)} | {c.get('mass_only_pair_orders_from_exact_no_mass_ambiguity',0)} | {c.get('unique_leader_verified_only_after_mass_band_samples',0)} | {c.get('compatible_without_mass_but_mass_band_incompatible_samples',0)} |")
    lines += ["", "Full feasibility transitions, unchanged orders/leaders, verification gaps, and co-leader exclusions are retained in the JSON. The retained-universe bridge is never pooled with the full-seven-source primary analysis. No narrowed set is interpreted as increased evidence.", "",
              f"Checked {report['labeled_records_checked']} labeled records / {report['unique_cases_checked']} unique case files; all case/model hashes and expected constraint structures agreed.",
              f"Frozen private index SHA-256: `{report['private_index_sha256']}`.", "",
              "Reproduce: `python scripts/audit_interval_geometry.py` after completing the approved interval Stage2 run.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    result = run()
    print(json.dumps({"status": result["status"], "labeled_records_checked": result["labeled_records_checked"],
                      "unique_cases_checked": result["unique_cases_checked"]}, indent=2))
