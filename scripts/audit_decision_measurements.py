#!/usr/bin/env python3
"""Frozen, two-stage held-out tracer feasibility experiment; no source refitting.

Design reads receptor identifier/uncertainty columns only. Evaluation verifies
the saved selection and provenance before projecting held-out concentration
columns. Source bytes are hashed in both stages; hashing is not outcome access.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import itertools
import json
import math
from pathlib import Path
from zipfile import ZipFile

import audit_epa_native_strengthening as native

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
IDENTITY = ("ID", "DATE", "DUR", "STHOUR", "SIZE")
CANDIDATES = ("SUXC", "CUXC", "ZNXC")
CONFIG = {
    "version": "1.0.0",
    "candidates": list(CANDIDATES),
    "cutoffs": [1.0, 2.0, 3.0],
    "cutoff_boundary": "retain when absolute residual / heuristic scale <= cutoff",
    "scenario_screen": "central and scenario converged and basic eligible; all scenario contributions nonnegative",
    "candidate_validity": "complete finite nonnegative profile means and uncertainties across every physical scenario; strictly positive finite receptor uncertainty",
    "candidate_invalidity": "exclude candidate, not individual scenarios; disclose reason",
    "prediction": "sum(profile mean * fixed fitted contribution)",
    "scale": "sqrt(receptor uncertainty^2 + sum((profile uncertainty * fixed fitted contribution)^2))",
    "score": "minimum absolute predicted separation / sum of two heuristic scales over pairs with different unique top labels",
    "tie_break": "lexicographic candidate name on exact score tie",
    "negligible_score_threshold": 1e-12,
    "negligible_handling": "retain frozen selection but explicitly label low separation; no hindsight replacement",
    "no_cross_top_pairs": "not applicable; no selected candidate",
    "native_missing_receptor_value": -99.0,
    "selection_access": "receptor identifiers and candidate uncertainties only; candidate receptor concentration columns excluded",
    "limitations": [
        "Heuristic scale omits fitted-contribution uncertainty, all covariance and model discrepancy.",
        "Cutoffs 1, 2 and 3 are sensitivity scenarios, not confidence levels.",
        "Model-set screening is not identification of the environmentally true source.",
        "Unresolved joint fits prevent complete-universe guarantees.",
        "Sulfur is related to fitted sulfate and is not an independent accuracy endpoint.",
        "Historical Cartesian profile combinations are not independently validated as jointly environmentally plausible.",
        "No assay cost, independent source truth, or conditioning-design comparator is available in this experiment.",
    ],
}


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def projected_table(payload: bytes, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Project only explicitly requested columns; never materialize full row dicts.

    Text fields in the physical source row are necessarily traversed to locate
    columns. Only permitted cells are retained; forbidden means are not converted,
    returned or used in design computations.
    """
    lines = payload.decode("ascii").splitlines()
    nonempty = iter(line for line in lines if line.strip())
    header = next(nonempty, "").split()
    if not header or len(set(header)) != len(header):
        raise ValueError("missing or duplicated source header")
    if not set(columns).issubset(header):
        raise ValueError("requested source columns missing")
    indexes = {name: header.index(name) for name in columns}
    output = []
    for line in nonempty:
        fields = line.split()
        if len(fields) != len(header):
            raise ValueError("incomplete source row")
        output.append({name: fields[index] for name, index in indexes.items()})
    return output


def sample_key(row: dict) -> tuple[str, ...]:
    return tuple(row[name] for name in IDENTITY)


def finite(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite value")
    return number


def source_inputs(inputs: Path, stage: str) -> tuple[dict, dict, dict]:
    if stage not in ("design", "evaluate"):
        raise ValueError("unknown stage")
    payload = (inputs / "sjvf_data.zip").read_bytes()
    if digest(payload) != native.TRUSTED_ARCHIVE_HASHES["sjvf_data.zip"]:
        raise ValueError("source archive differs from trusted identity")
    fields = tuple(name[:-1] + "U" for name in CANDIDATES) if stage == "design" else CANDIDATES
    with ZipFile(BytesIO(payload)) as archive:
        receptor_bytes = archive.read("ADsjvf.txt")
        rows = projected_table(receptor_bytes, IDENTITY + fields)
        profile_bytes = archive.read("PRsjvf.txt")
        profiles = {}
        if stage == "design":
            profile_fields = tuple(field for candidate in CANDIDATES
                                   for field in (candidate, candidate[:-1] + "U"))
            for row in projected_table(profile_bytes, ("SID", "SIZE") + profile_fields):
                if row["SIZE"] == "FINE":
                    if row["SID"] in profiles:
                        raise ValueError("duplicate profile identity")
                    profiles[row["SID"]] = row
    chosen = [r for r in rows if r["ID"] == "FRESNO" and r["SIZE"] == "FINE"]
    receptors = {sample_key(r): r for r in chosen}
    if len(chosen) != 35 or len(receptors) != len(chosen):
        raise ValueError("source sample count or identity differs")
    return receptors, profiles, {
        "sjvf_archive_sha256": digest(payload),
        "receptor_member_sha256": digest(receptor_bytes),
        "profile_member_sha256": digest(profile_bytes),
    }


def basic(result: dict) -> bool:
    if not result.get("converged", False):
        return False
    try:
        r2, chi = finite(result["R2"]), finite(result["reduced_chi2"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return False
    return 0.8 <= r2 <= 1.0 and 0.0 <= chi <= 4.0


def physical_scenarios(sample: dict) -> tuple[list[dict], dict]:
    rows = sample.get("rows", [])
    attrition = {"grid_rows": len(rows), "unresolved_rows": sum(not r["result"].get("converged", False) for r in rows),
                 "central_basic_eligible": basic(sample["central"]), "basic_rows": 0,
                 "negative_rows": 0, "invalid_contribution_rows": 0, "physical_rows": 0,
                 "tied_top_rows": 0}
    if not attrition["central_basic_eligible"]:
        return [], attrition
    scenarios = []
    for index, row in enumerate(rows):
        result = row["result"]
        if not basic(result):
            continue
        attrition["basic_rows"] += 1
        try:
            ids = result["source_ids"]
            if not ids or len(ids) != len(set(ids)) or ids != row["source_ids"]:
                raise ValueError("inconsistent source identifiers")
            values = [finite(result["source_contributions"][sid]) for sid in ids]
            mapped = {label: finite(value) for label, value in row["mapped"].items()}
            if sorted(values) != sorted(mapped.values()):
                raise ValueError("contribution mapping differs")
        except (KeyError, TypeError, ValueError, OverflowError):
            attrition["invalid_contribution_rows"] += 1
            continue
        if min(values) < 0:
            attrition["negative_rows"] += 1
            continue
        largest = max(mapped.values())
        tops = sorted(label for label, value in mapped.items() if value == largest)
        attrition["tied_top_rows"] += len(tops) > 1
        scenarios.append({"row_index": index, "source_ids": ids,
                          "contributions": values, "top_sources": tops})
    attrition["physical_rows"] = len(scenarios)
    return scenarios, attrition


def prediction(candidate: str, scenario: dict, receptor: dict, profiles: dict) -> dict:
    uncertainty_name = candidate[:-1] + "U"
    receptor_uncertainty = finite(receptor[uncertainty_name])
    if receptor_uncertainty <= 0:
        raise ValueError("nonpositive_receptor_uncertainty")
    mean_terms, uncertainty_terms = [], []
    for sid, contribution in zip(scenario["source_ids"], scenario["contributions"]):
        source_mean = finite(profiles[sid][candidate])
        source_uncertainty = finite(profiles[sid][uncertainty_name])
        if source_mean < 0 or source_uncertainty < 0:
            raise ValueError("negative_or_missing_profile_field")
        mean_terms.append(finite(source_mean * contribution))
        uncertainty_terms.append(finite(source_uncertainty * contribution))
    mean = finite(math.fsum(mean_terms))
    scale = finite(math.hypot(receptor_uncertainty, *uncertainty_terms))
    if scale <= 0:
        raise ValueError("nonpositive_scale")
    return {"row_index": scenario["row_index"], "prediction": mean,
            "scale": scale, "top_sources": scenario["top_sources"]}


def design_sample(sample: dict, receptor: dict, profiles: dict) -> dict:
    """Pure design API: accesses uncertainty keys only on the receptor mapping."""
    scenarios, attrition = physical_scenarios(sample)
    cross_pairs = [(i, j) for i, j in itertools.combinations(range(len(scenarios)), 2)
                   if len(scenarios[i]["top_sources"]) == len(scenarios[j]["top_sources"]) == 1
                   and scenarios[i]["top_sources"] != scenarios[j]["top_sources"]]
    record = {"sample": sample["sample"], "attrition": attrition,
              "scenario_set_sha256": digest(json_bytes(scenarios)),
              "baseline_top_sources": sorted({top for s in scenarios for top in s["top_sources"]}),
              "cross_top_pairs": len(cross_pairs), "candidates": {}, "selected": None}
    for candidate in CANDIDATES:
        if not scenarios:
            record["candidates"][candidate] = {"status": "NO_PHYSICAL_SCENARIOS"}
            continue
        try:
            predictions = [prediction(candidate, scenario, receptor, profiles) for scenario in scenarios]
            score = min((abs(predictions[i]["prediction"] - predictions[j]["prediction"])
                         / (predictions[i]["scale"] + predictions[j]["scale"])
                         for i, j in cross_pairs), default=None)
            if score is not None:
                score = finite(score)
            record["candidates"][candidate] = {"status": "VALID", "score": score,
                                                 "predictions": predictions}
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            # Candidate exclusion retains the common physical set for all others.
            record["candidates"][candidate] = {"status": "INVALID_DESIGN_FIELDS", "reason": str(exc)}
    if not attrition["central_basic_eligible"]:
        record["status"] = "CENTRAL_NOT_BASIC_ELIGIBLE"
    elif not scenarios:
        record["status"] = "NO_PHYSICAL_SCENARIOS"
    elif not cross_pairs:
        record["status"] = "NO_CROSS_TOP_PAIRS"
    else:
        valid = [(row["score"], candidate) for candidate, row in record["candidates"].items()
                 if row["status"] == "VALID"]
        if not valid:
            record["status"] = "NO_VALID_CANDIDATE"
        else:
            best_score, chosen = sorted(valid, key=lambda item: (-item[0], item[1]))[0]
            record["selected"] = chosen
            record["status"] = ("SELECTED_LOW_SEPARATION" if best_score <= CONFIG["negligible_score_threshold"]
                                else "SELECTED")
    return record


def design_aggregate(samples: list[dict]) -> dict:
    counts = {name: sum(int(s["attrition"][name]) for s in samples)
              for name in samples[0]["attrition"]} if samples else {}
    return {"samples": len(samples), "attrition_totals": counts,
            "statuses": dict(sorted(Counter(s["status"] for s in samples).items())),
            "selection_counts": dict(sorted(Counter(s["selected"] for s in samples if s["selected"]).items())),
            "candidate_status_counts": {candidate: dict(sorted(Counter(
                s["candidates"][candidate]["status"] for s in samples).items())) for candidate in CANDIDATES}}


def local_provenance(ledger_path: Path) -> dict:
    return {"measurement_script_sha256": digest(Path(__file__).read_bytes()),
            "native_script_sha256": digest(Path(native.__file__).read_bytes()),
            "plan_sha256": digest((PUBLIC / "MEASUREMENT_DESIGN_PLAN.md").read_bytes()),
            "joint_ledger_sha256": digest(ledger_path.read_bytes()),
            "joint_configuration_file_sha256": digest((PUBLIC / "joint_profile_configuration.json").read_bytes())}


def design(inputs: Path) -> dict:
    """Persist selection before evaluation; refuses overwrite to prevent retuning."""
    target = PRIVATE / "measurement_selection.json"
    if target.exists() or (PRIVATE / "measurement_selection.sha256").exists():
        raise ValueError("selection already frozen; use evaluate, do not overwrite or retune")
    config_payload = json_bytes(CONFIG)
    frozen_path = PRIVATE / "measurement_configuration_frozen.json"
    if frozen_path.exists():
        if frozen_path.read_bytes() != config_payload:
            raise ValueError("configuration differs from frozen record")
    else:
        exclusive_write(frozen_path, config_payload)
    ledger_path = PRIVATE / "joint_profile_ledger.json"
    provenance = local_provenance(ledger_path)
    ledger = json.loads(ledger_path.read_bytes())
    joint_report = json.loads((PUBLIC / "joint_profile_results.json").read_bytes())
    if provenance["joint_ledger_sha256"] != joint_report["private_ledger_sha256"]:
        raise ValueError("joint ledger differs from completed joint experiment")
    if ledger["configuration_sha256"] != joint_report["configuration_sha256"]:
        raise ValueError("joint configuration differs")
    receptors, profiles, input_provenance = source_inputs(inputs, "design")
    if input_provenance["sjvf_archive_sha256"] != joint_report["input_archive_hashes"]["sjvf_data.zip"]:
        raise ValueError("joint source archive differs")
    provenance.update(input_provenance)
    if {sample_key(s["sample"]) for s in ledger["samples"]} != set(receptors):
        raise ValueError("joint and native sample identities differ")
    records = [design_sample(s, receptors[sample_key(s["sample"])], profiles) for s in ledger["samples"]]
    selection = {"created_utc": now(), "configuration_sha256": digest(config_payload),
                 "configuration": CONFIG, "provenance": provenance, "samples": records,
                 "heldout_concentrations_accessed": False}
    payload = json_bytes(selection)
    exclusive_write(target, payload)
    exclusive_write(PRIVATE / "measurement_selection.sha256", (digest(payload) + "\n").encode("ascii"))
    report = {"created_utc": selection["created_utc"], "selection_sha256": digest(payload),
              "configuration_sha256": selection["configuration_sha256"], "configuration": CONFIG,
              "provenance": provenance, "aggregate": design_aggregate(records),
              "heldout_concentrations_accessed": False}
    exclusive_write(PUBLIC / "measurement_configuration.json", config_payload)
    exclusive_write(PUBLIC / "measurement_design.json", json_bytes(report))
    return report


def verify_selection(inputs: Path) -> tuple[dict, dict]:
    """Must complete before any held-out receptor concentration reader is called."""
    payload = (PRIVATE / "measurement_selection.json").read_bytes()
    expected = (PRIVATE / "measurement_selection.sha256").read_text(encoding="ascii").strip()
    public_record = json.loads((PUBLIC / "measurement_design.json").read_bytes())
    if digest(payload) != expected or expected != public_record["selection_sha256"]:
        raise ValueError("frozen selection identity differs")
    selection = json.loads(payload)
    config_payload = json_bytes(CONFIG)
    if (selection["configuration_sha256"] != digest(config_payload)
            or (PRIVATE / "measurement_configuration_frozen.json").read_bytes() != config_payload
            or (PUBLIC / "measurement_configuration.json").read_bytes() != config_payload):
        raise ValueError("configuration differs from frozen selection")
    for key, value in local_provenance(PRIVATE / "joint_profile_ledger.json").items():
        if selection["provenance"][key] != value:
            raise ValueError("code, plan or scenario identity changed after selection")
    archive_hash = digest((inputs / "sjvf_data.zip").read_bytes())
    if archive_hash != selection["provenance"]["sjvf_archive_sha256"]:
        raise ValueError("source archive changed after selection")
    if selection["heldout_concentrations_accessed"] is not False:
        raise ValueError("selection does not assert blinded design")
    datetime.fromisoformat(selection["created_utc"])
    return selection, public_record


def screen(predictions: list[dict], observed, cutoff: float) -> dict:
    value = finite(observed)
    if value == CONFIG["native_missing_receptor_value"]:
        raise ValueError("missing_native_receptor_value")
    if not math.isfinite(cutoff) or cutoff <= 0:
        raise ValueError("invalid cutoff")
    retained = []
    for row in predictions:
        mean, scale = finite(row["prediction"]), finite(row["scale"])
        if scale <= 0:
            raise ValueError("nonpositive_scale")
        if abs(value - mean) / scale <= cutoff:
            retained.append(row)
    original_tops = sorted({top for row in predictions for top in row["top_sources"]})
    tops = sorted({top for row in retained for top in row["top_sources"]})
    return {"original_scenarios": len(predictions), "retained_scenarios": len(retained),
            "original_top_sources": original_tops, "retained_top_sources": tops,
            "rejected_all": bool(predictions) and not retained,
            "top_set_reduced_nonempty": bool(retained) and len(tops) < len(original_tops),
            "resolved_to_single_top": bool(retained) and len(original_tops) > 1 and len(tops) == 1,
            "no_top_set_reduction": bool(retained) and len(tops) == len(original_tops),
            "no_scenario_reduction": len(retained) == len(predictions),
            "retained_row_indexes": [r["row_index"] for r in retained]}


def evaluate_sample(record: dict, receptor_means: dict) -> dict:
    candidates = {}
    for candidate in CANDIDATES:
        designed = record["candidates"][candidate]
        if designed["status"] != "VALID":
            candidates[candidate] = {"status": "UNAVAILABLE_AT_DESIGN"}
            continue
        try:
            observed = finite(receptor_means[candidate])
            results = {str(int(cutoff)): screen(designed["predictions"], observed, cutoff)
                       for cutoff in CONFIG["cutoffs"]}
            candidates[candidate] = {"status": "EVALUATED", "observed": observed, "cutoffs": results}
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            candidates[candidate] = {"status": "INVALID_HELDOUT_MEAN", "reason": str(exc)}
    return {"sample": record["sample"], "design_status": record["status"],
            "selected": record["selected"], "baseline_top_count": len(record["baseline_top_sources"]),
            "candidates": candidates}


def summarize_outcomes(outcomes: list[dict]) -> dict:
    names = ("rejected_all", "top_set_reduced_nonempty", "resolved_to_single_top",
             "no_top_set_reduction", "no_scenario_reduction")
    return {"evaluated_samples": len(outcomes),
            "baseline_ambiguous_samples": sum(len(o["original_top_sources"]) > 1 for o in outcomes),
            **{name + "_samples": sum(o[name] for o in outcomes) for name in names},
            "original_scenarios": sum(o["original_scenarios"] for o in outcomes),
            "retained_scenarios": sum(o["retained_scenarios"] for o in outcomes),
            "retained_top_count_histogram": dict(sorted(Counter(str(len(o["retained_top_sources"]))
                                                                for o in outcomes).items()))}


def evaluation_aggregate(records: list[dict]) -> dict:
    report = {"samples": len(records), "candidate_evaluation_statuses": {}, "cutoffs": {}}
    for candidate in CANDIDATES:
        report["candidate_evaluation_statuses"][candidate] = dict(sorted(Counter(
            record["candidates"][candidate]["status"] for record in records).items()))
    for cutoff in (str(int(c)) for c in CONFIG["cutoffs"]):
        strategies, paired = {}, {}
        for strategy in ("selected",) + CANDIDATES:
            eligible = [(r, r["selected"] if strategy == "selected" else strategy) for r in records]
            outcomes = [r["candidates"][candidate]["cutoffs"][cutoff] for r, candidate in eligible
                        if candidate and r["candidates"][candidate]["status"] == "EVALUATED"]
            strategies[strategy] = summarize_outcomes(outcomes)
        for fixed in CANDIDATES:
            matched = [r for r in records if r["selected"]
                       and r["candidates"][r["selected"]]["status"] == "EVALUATED"
                       and r["candidates"][fixed]["status"] == "EVALUATED"]
            chosen_results = [r["candidates"][r["selected"]]["cutoffs"][cutoff] for r in matched]
            fixed_results = [r["candidates"][fixed]["cutoffs"][cutoff] for r in matched]
            paired[fixed] = {"matched_samples": len(matched), "selected": summarize_outcomes(chosen_results),
                            "fixed": summarize_outcomes(fixed_results),
                            "selected_only_resolved": sum(a["resolved_to_single_top"] and not b["resolved_to_single_top"]
                                                          for a, b in zip(chosen_results, fixed_results)),
                            "fixed_only_resolved": sum(b["resolved_to_single_top"] and not a["resolved_to_single_top"]
                                                       for a, b in zip(chosen_results, fixed_results))}
        report["cutoffs"][cutoff] = {"strategies": strategies, "matched_selected_vs_fixed": paired}
    return report


def render_report(report: dict) -> str:
    lines = ["# Frozen held-out measurement feasibility experiment", "",
             "Exploratory screening of a finite historical model set; no confidence, source-truth or novelty claim.", "",
             f"Selection saved at `{report['selection_created_utc']}` before evaluation started at `{report['evaluation_started_utc']}`.",
             f"Immutable selection SHA-256: `{report['selection_sha256']}`.", "",
             "## Design and attrition", "",
             "```json", json.dumps(report["design_aggregate"], indent=2), "```", "",
             "## Evaluation", "",
             "Fixed-candidate rows include all evaluable samples; selected rows include only samples with a preselected candidate. Matched comparisons below remove that denominator difference.", "",
             "| Cutoff | Strategy | Evaluable samples | Baseline ambiguous | Nonempty top-set reductions | Resolved to one top | All rejected | No top-set reduction |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for cutoff, row in report["aggregate"]["cutoffs"].items():
        for strategy, values in row["strategies"].items():
            lines.append(f"| {cutoff} | {strategy} | {values['evaluated_samples']} | {values['baseline_ambiguous_samples']} | {values['top_set_reduced_nonempty_samples']} | {values['resolved_to_single_top_samples']} | {values['rejected_all_samples']} | {values['no_top_set_reduction_samples']} |")
    lines += ["", "## Comparisons on matched samples", "",
              "| Cutoff | Fixed candidate | Matched samples | Selected resolves | Fixed resolves | Selected all rejected | Fixed all rejected |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for cutoff, row in report["aggregate"]["cutoffs"].items():
        for fixed, values in row["matched_selected_vs_fixed"].items():
            lines.append(f"| {cutoff} | {fixed} | {values['matched_samples']} | {values['selected']['resolved_to_single_top_samples']} | {values['fixed']['resolved_to_single_top_samples']} | {values['selected']['rejected_all_samples']} | {values['fixed']['rejected_all_samples']} |")
    lines += ["", "## Limits", ""] + ["- " + limit for limit in CONFIG["limitations"]]
    lines += ["- All-rejected outcomes are model inadequacy warnings, never successful attribution.",
              "- The common physical scenario set is not pruned separately for candidate completeness; an incomplete candidate is unavailable.",
              "- Full predictions, dates, held-out values and row selections stay in ignored private storage.", "",
              "## Reproduce", "", "```text", "python scripts/audit_decision_measurements.py design --inputs <EPA-archive-directory>",
              "python scripts/audit_decision_measurements.py evaluate --inputs <EPA-archive-directory>",
              "python -m unittest discover -s tests -p test_decision_measurements.py -v", "```", "",
              "Design refuses to overwrite an existing frozen selection. Evaluation requires unchanged code, plan, configuration, scenario ledger and source archive.", ""]
    return "\n".join(lines)


def evaluate(inputs: Path) -> dict:
    selection, public_design = verify_selection(inputs)
    started = now()
    # This is the first call permitted to expose held-out receptor concentrations.
    receptors, _, input_provenance = source_inputs(inputs, "evaluate")
    if any(selection["provenance"][key] != value for key, value in input_provenance.items()):
        raise ValueError("source members differ from frozen design")
    records = [evaluate_sample(record, receptors[sample_key(record["sample"])]) for record in selection["samples"]]
    private_result = {"selection_sha256": public_design["selection_sha256"],
                      "evaluation_started_utc": started, "completed_utc": now(), "samples": records}
    private_payload = json_bytes(private_result)
    report = {"selection_sha256": public_design["selection_sha256"],
              "selection_created_utc": selection["created_utc"], "evaluation_started_utc": started,
              "completed_utc": private_result["completed_utc"], "configuration": CONFIG,
              "provenance": selection["provenance"], "design_aggregate": public_design["aggregate"],
              "aggregate": evaluation_aggregate(records), "private_evaluation_sha256": digest(private_payload),
              "scope": "Conditional screening feasibility; no source truth or confidence coverage."}
    exclusive_write(PRIVATE / "measurement_evaluation.json", private_payload)
    exclusive_write(PUBLIC / "measurement_results.json", json_bytes(report))
    exclusive_write(PUBLIC / "measurement_report.md", render_report(report).encode("utf-8"))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("design", "evaluate"))
    parser.add_argument("--inputs", type=Path, default=native.DEFAULT_INPUT)
    args = parser.parse_args()
    report = design(args.inputs) if args.stage == "design" else evaluate(args.inputs)
    print(json.dumps(report["aggregate"], indent=2))


if __name__ == "__main__":
    main()
