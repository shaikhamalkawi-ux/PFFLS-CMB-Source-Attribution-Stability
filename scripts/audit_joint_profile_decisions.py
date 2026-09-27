#!/usr/bin/env python3
"""Exhaustive, exploratory finite-grid decisions using the frozen EPA solver.

No previous output or manuscript is edited. Joint-input fits are new exploratory
analyses; they are not a re-run of a preregistered study or evidence of accuracy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import platform

import numpy as np

import audit_epa_native_strengthening as native

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
CONFIG_PATH = PUBLIC / "joint_profile_configuration.json"
CONFIG_SHA256 = "f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314"
SCREENS = ("converged", "basic", "strict")


def configuration() -> dict:
    payload = CONFIG_PATH.read_bytes()
    if native.sha256(payload) != CONFIG_SHA256:
        raise ValueError("joint configuration differs from pre-fit frozen identity")
    config = json.loads(payload)
    if native.sha256(Path(native.__file__).read_bytes()) != config["native_solver_script_sha256"]:
        raise ValueError("underlying native solver changed")
    if native.sha256(native.json_bytes(native.CONFIG)) != config["native_configuration_sha256"]:
        raise ValueError("underlying native configuration changed")
    return config


def validate_output_paths(inputs: Path, public: Path, private: Path) -> None:
    if public.resolve() != PUBLIC.resolve() or private.resolve() != PRIVATE.resolve():
        raise ValueError("only dedicated decision-research output directories are permitted")
    if any(p.resolve().is_relative_to(inputs.resolve()) or inputs.resolve().is_relative_to(p.resolve())
           for p in (public, private)):
        raise ValueError("source archive directory overlaps output")


def grid(retained: list[str], families: dict) -> list[dict]:
    if not retained or len(set(retained)) != len(retained):
        raise ValueError("retained source slots must be nonempty and unique")
    for slot, options in families.items():
        if not options or options[0] != slot or len(set(options)) != len(options):
            raise ValueError("central profile must be first among unique family options")
    options = [families.get(slot, [slot]) for slot in retained]
    rows = []
    for choices in itertools.product(*options):
        if len(set(choices)) != len(choices):
            raise ValueError("different slots select the same profile")
        rows.append({"source_ids": list(choices),
                     "distance": sum(choice != slot for choice, slot in zip(choices, retained))})
    return rows


def passes(result: dict, screen: str) -> bool:
    if screen not in SCREENS:
        raise ValueError("unknown diagnostic screen")
    if not result.get("converged", False):
        return False
    return screen == "converged" or native.fit_targets(result, strict=screen == "strict")


def mapped_contributions(result: dict, retained: list[str], labels: dict) -> dict:
    if len(result["source_ids"]) != len(retained):
        raise ValueError("source result differs from retained slots")
    keys = [labels[slot] for slot in retained]
    if len(set(keys)) != len(keys):
        raise ValueError("family labels are not unique")
    values = [result["source_contributions"][sid] for sid in result["source_ids"]]
    if not all(np.isfinite(value) for value in values):
        raise ValueError("nonfinite contribution cannot be ranked")
    return dict(zip(keys, values))


def summarize_decisions(rows: list[dict], screen: str, decision: str) -> dict:
    """Classify witnesses and conditional stability without hiding solver failures.

    Each row has distance, result, and (if converged) ranking. The central row is
    distance zero. A nonconverged row is unresolved even if its terminal iterate
    would have failed the diagnostic screen.
    """
    if decision not in ("largest_source_change", "ordering_change"):
        raise ValueError("unknown decision")
    centers = [row for row in rows if row["distance"] == 0]
    if len(centers) != 1:
        raise ValueError("exactly one central row is required")
    central_eligible = passes(centers[0]["result"], screen)
    unresolved = [r for r in rows if not r["result"].get("converged", False)]
    admitted = [r for r in rows if passes(r["result"], screen)] if central_eligible else []
    local = [r for r in admitted if r["distance"] <= 1]
    local_alts = [r for r in local if r["distance"] == 1]
    changed = [r for r in admitted if r["ranking"][decision]]
    local_changed = [r for r in local if r["ranking"][decision]]
    local_unresolved = [r for r in unresolved if r["distance"] <= 1]
    observed_local_stable = central_eligible and bool(local_alts) and not local_changed
    minimum = min((r["distance"] for r in changed), default=None)
    exact_minimum = minimum is not None and not any(r["distance"] < minimum for r in unresolved)
    full_grid_stable = central_eligible and not changed and not unresolved
    return {
        "central_eligible": central_eligible,
        "grid_count": len(rows), "admitted_count": len(admitted),
        "admitted_alternative_count": sum(r["distance"] > 0 for r in admitted),
        "unresolved_count": len(unresolved),
        "local_admitted_alternative_count": len(local_alts),
        "local_unresolved_count": len(local_unresolved),
        "local_changed_count": len(local_changed), "joint_changed_count": len(changed),
        "observed_local_stable": observed_local_stable,
        "complete_local_stable": observed_local_stable and not local_unresolved,
        "observed_local_stable_joint_witness": observed_local_stable and bool(changed),
        "complete_local_stable_joint_witness": observed_local_stable and not local_unresolved and bool(changed),
        "complete_joint_stable": full_grid_stable,
        "complete_joint_stable_nonvacuous": full_grid_stable and bool(local_alts),
        "minimum_observed_witness_distance": minimum,
        "minimum_witness_distance_exact_on_grid": exact_minimum,
        "status": "CENTRAL_INELIGIBLE" if not central_eligible else "WITNESSED_UNSTABLE" if changed
                  else "UNRESOLVED" if unresolved else "CONDITIONALLY_STABLE_ON_FINITE_GRID",
    }


def pairwise_certificate(rows: list[dict], screen: str) -> dict:
    centers = [r for r in rows if r["distance"] == 0]
    if len(centers) != 1:
        raise ValueError("exactly one central row is required")
    if not passes(centers[0]["result"], screen):
        return {"status": "CENTRAL_INELIGIBLE", "pairs": []}
    admitted = [r for r in rows if passes(r["result"], screen)]
    unresolved_count = sum(not r["result"].get("converged", False) for r in rows)
    names = list(centers[0]["mapped"])
    pairs = []
    for a, b in itertools.combinations(names, 2):
        differences = [r["mapped"][a] - r["mapped"][b] for r in admitted]
        low, high = min(differences), max(differences)
        relation = f"{a}>{b}" if low > 0 else f"{b}>{a}" if high < 0 else None
        pairs.append({"a": a, "b": b, "minimum_observed_margin": low,
                      "maximum_observed_margin": high, "resolved_subset_relation": relation,
                      "certified_on_full_diagnostic_admissible_grid": relation is not None and unresolved_count == 0})
    top_set = sorted({name for r in admitted for name in r["ranking"]["alternative_top_sources"]})
    return {"status": "COMPLETE_FINITE_GRID" if not unresolved_count else "UNRESOLVED_GRID_CHOICES",
            "admitted_count": len(admitted), "unresolved_count": unresolved_count,
            "observed_possible_top_families": top_set,
            "top_set_complete_on_grid": unresolved_count == 0,
            "pairs": pairs}


def fit_sample(receptor: dict, profiles: dict, config: dict) -> dict:
    control = native.central_fit(receptor, profiles)
    sample = {key: receptor[key] for key in native.CONFIG["case_identity"]}
    if not control["converged"]:
        return {"sample": sample, "central": control, "status": "CENTRAL_UNRESOLVED", "rows": []}
    retained = control["source_ids"]
    central_mapped = mapped_contributions(control, retained, config["labels"])
    rows = []
    for choice in grid(retained, config["families"]):
        try:
            result = control if choice["distance"] == 0 else native.effective_variance_fit(receptor, profiles, choice["source_ids"])
        except ValueError as exc:
            result = {"converged": False, "numerical_failure": str(exc), "source_ids": choice["source_ids"]}
        row = {**choice, "result": result}
        if result["converged"]:
            mapped = mapped_contributions(result, retained, config["labels"])
            row["mapped"] = mapped
            row["ranking"] = native.ranking_changes(central_mapped, mapped)
            row["ranking_rounded_5dp"] = native.ranking_changes(central_mapped, mapped, 5)
        rows.append(row)
    summaries = {screen: {
        "top": summarize_decisions(rows, screen, "largest_source_change"),
        "ordering": summarize_decisions(rows, screen, "ordering_change"),
        "partial_order": pairwise_certificate(rows, screen)} for screen in SCREENS}
    return {"sample": sample, "status": "GRID_ENUMERATED", "central": control,
            "retained_slots": retained, "rows": rows, "summaries": summaries}


def aggregate(samples: list[dict]) -> dict:
    complete = [sample for sample in samples if sample["status"] == "GRID_ENUMERATED"]
    rows = [row for sample in complete for row in sample["rows"]]
    distances = sorted({row["distance"] for row in rows})
    attrition = {}
    for distance in distances:
        chosen = [row for row in rows if row["distance"] == distance]
        attrition[str(distance)] = {"attempted": len(chosen),
            "converged_count": sum(row["result"].get("converged", False) for row in chosen),
            "unresolved": sum(not row["result"].get("converged", False) for row in chosen),
            "numerical_failure": sum("numerical_failure" in row["result"] for row in chosen)}
        for screen in SCREENS:
            paired = [(sample, row) for sample in complete for row in sample["rows"]
                      if row["distance"] == distance and passes(sample["central"], screen)
                      and passes(row["result"], screen)]
            attrition[str(distance)][screen] = {
                "central_and_alternative_eligible": len(paired),
                "top_changed": sum(row["ranking"]["largest_source_change"] for _, row in paired),
                "order_changed": sum(row["ranking"]["ordering_change"] for _, row in paired)}
    screens = {}
    for screen in SCREENS:
        screen_report = {"central_eligible_samples": sum(passes(sample["central"], screen) for sample in complete),
                         "all_initial_samples": len(samples)}
        for decision in ("top", "ordering"):
            summaries = [sample["summaries"][screen][decision] for sample in complete]
            counters = ["observed_local_stable", "complete_local_stable", "observed_local_stable_joint_witness",
                        "complete_local_stable_joint_witness", "complete_joint_stable", "complete_joint_stable_nonvacuous"]
            decision_report = {key + "_samples": sum(s[key] for s in summaries) for key in counters}
            decision_report["statuses"] = dict(sorted(Counter(s["status"] for s in summaries).items()))
            decision_report["minimum_observed_witness_distance_histogram"] = dict(sorted(Counter(
                str(s["minimum_observed_witness_distance"]) for s in summaries
                if s["minimum_observed_witness_distance"] is not None).items()))
            decision_report["exact_minimum_witness_distance_histogram"] = dict(sorted(Counter(
                str(s["minimum_observed_witness_distance"]) for s in summaries
                if s["minimum_witness_distance_exact_on_grid"]).items()))
            decision_report["central_eligible_without_admitted_local_alternative_samples"] = sum(
                s["central_eligible"] and not s["local_admitted_alternative_count"] for s in summaries)
            screen_report[decision] = decision_report
        certs = [sample["summaries"][screen]["partial_order"] for sample in complete]
        screen_report["partial_order"] = {
            "resolved_grid_samples": sum(c["status"] == "COMPLETE_FINITE_GRID" for c in certs),
            "total_observed_fixed_pair_relations": sum(p["resolved_subset_relation"] is not None for c in certs for p in c["pairs"]),
            "total_certified_pair_relations": sum(p["certified_on_full_diagnostic_admissible_grid"] for c in certs for p in c["pairs"]),
            "observed_top_set_size_histogram": dict(sorted(Counter(str(len(c["observed_possible_top_families"]))
                for c in certs if "observed_possible_top_families" in c).items()))}
        screens[screen] = screen_report
    return {"initial_samples": len(samples), "central_converged_samples": len(complete),
            "central_unresolved_samples": len(samples) - len(complete),
            "grid_size_histogram": dict(sorted(Counter(str(len(sample["rows"])) for sample in complete).items())),
            "total_grid_choices_including_central": len(rows),
            "attrition_by_distance": attrition,
            "rank_changes_disagreeing_after_5dp_rounding": sum(
                any(row["ranking"][key] != row["ranking_rounded_5dp"][key]
                    for key in ("largest_source_change", "ordering_change"))
                for row in rows if row["result"].get("converged", False)),
            "converged_rows_with_negative_contributions": sum(
                any(value < 0 for value in row["mapped"].values())
                for row in rows if row["result"].get("converged", False)),
            "screens": screens}


def render_report(report: dict) -> str:
    totals = report["aggregate"]
    lines = ["# Exploratory joint-profile decision audit", "",
             "This is a new finite-grid analysis, not a manuscript change, field validation, or novelty claim.", "",
             f"Configuration frozen before the first joint fit: `{CONFIG_SHA256}`.",
             f"All {totals['initial_samples']} initial samples retained; {totals['central_converged_samples']} converged central fits.",
             f"Grid choices including central fits: **{totals['total_grid_choices_including_central']}**.", "",
             "## Attrition by number of coordinated substitutions", "",
             "| Changed slots | Attempted | Converged | Unresolved | Basic admitted | Basic top changes | Strict admitted | Strict top changes |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for distance, row in totals["attrition_by_distance"].items():
        lines.append(f"| {distance} | {row['attempted']} | {row['converged_count']} | {row['unresolved']} | {row['basic']['central_and_alternative_eligible']} | {row['basic']['top_changed']} | {row['strict']['central_and_alternative_eligible']} | {row['strict']['top_changed']} |")
    lines.extend(["", "## Sample-level comparisons", "",
        "A local-stability count requires at least one admitted distance-one alternative. Complete local stability additionally requires every distance-one choice to be resolved. Thus a numerically unresolved choice is not silently removed from a stability claim.", "",
        "| Screen | Central eligible / initial | Observed local top stable | Complete local top stable | Observed-local-stable with joint top witness | Complete-local-stable with joint top witness | Complete joint top stable |",
        "|---|---:|---:|---:|---:|---:|---:|"])
    for screen, row in totals["screens"].items():
        top = row["top"]
        lines.append(f"| {screen} | {row['central_eligible_samples']}/{row['all_initial_samples']} | {top['observed_local_stable_samples']} | {top['complete_local_stable_samples']} | {top['observed_local_stable_joint_witness_samples']} | {top['complete_local_stable_joint_witness_samples']} | {top['complete_joint_stable_samples']} |")
    lines.extend(["", "Full-order and witness-distance histograms, partial-order counts, and all screen-specific denominators are in `joint_profile_results.json`.", "",
        "## Limits and disposition", "",
        "- KEEP: exhaustive counts, reproducible witnesses, and unresolved-state-aware finite-grid statements.",
        "- HOLD: novelty, generalization to unenumerated profiles, probability coverage, environmental accuracy, and unrestricted source universes.",
        "- REMOVE: any inference that a screened-out converged fit proves physical impossibility, or that nonconvergence proves inadmissibility.",
        "- Profiles are combined only for the central-retained slots. A source removed from the central solution is not reintroduced; these are conditional source-universe results.",
        "- Basic/strict screening is a declared numerical eligibility convention, not independent scientific validation of profiles.",
        "- Negative alternative contributions are retained, not clipped. Their presence limits physical interpretation.",
        "- The Cartesian combinations are exploratory mathematical combinations of historical family alternatives; simultaneous environmental plausibility is not independently established.",
        "- Minimum observed witness distance is exact only when every smaller-distance choice was resolved. A witness remains valid even if other grid choices are unresolved.",
        "- No baseline manuscript, previous reconstruction outputs, Zenodo archive, or raw data were changed.", "",
        f"Private ledger SHA-256: `{report['private_ledger_sha256']}`. Full source vectors, dates, margins, and per-sample witnesses stay in ignored private storage.", "",
        "## Reproduce", "", "```text", "python scripts/audit_joint_profile_decisions.py --inputs <official-EPA-archive-directory>",
        "python -m unittest discover -s tests -p test_joint_profile_decisions.py -v", "```", ""])
    return "\n".join(lines)


def run(inputs: Path, public: Path = PUBLIC, private: Path = PRIVATE) -> dict:
    validate_output_paths(inputs, public, private)
    config = configuration()
    private.mkdir(parents=True, exist_ok=True)
    frozen = private / "joint_profile_configuration_frozen.json"
    payload = CONFIG_PATH.read_bytes()
    if frozen.exists() and frozen.read_bytes() != payload:
        raise ValueError("private pre-fit configuration differs")
    if not frozen.exists():
        frozen.write_bytes(payload)
    inventory = native.archive_inventory(inputs)
    verified = native.verify_recovery_identities(inventory, ROOT / "outputs/strengthening_20260926/source_recovery.json")
    receptors, profiles, input_summary = native.load_inputs(inputs)
    started = datetime.now(timezone.utc).isoformat()
    samples = [fit_sample(receptor, profiles, config) for receptor in receptors]
    ledger = native.json_bytes({"configuration_sha256": CONFIG_SHA256, "samples": samples})
    (private / "joint_profile_ledger.json").write_bytes(ledger)
    report = {"configuration_sha256": CONFIG_SHA256, "script_sha256": native.sha256(Path(__file__).read_bytes()),
              "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "randomness": "none"},
              "input_identity_verification": verified,
              "input_archive_hashes": {r["archive"]: r["sha256"] for r in inventory},
              "input_summary": input_summary, "aggregate": aggregate(samples),
              "private_ledger_sha256": native.sha256(ledger), "configuration": config,
              "scope": "Exploratory conditional finite-grid attribution decisions; no external accuracy or novelty claim."}
    public.mkdir(parents=True, exist_ok=True)
    (public / "joint_profile_results.json").write_bytes(native.json_bytes(report))
    (public / "joint_profile_report.md").write_text(render_report(report), encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=native.DEFAULT_INPUT)
    args = parser.parse_args()
    report = run(args.inputs)
    print(json.dumps(report["aggregate"], indent=2))


if __name__ == "__main__":
    main()
