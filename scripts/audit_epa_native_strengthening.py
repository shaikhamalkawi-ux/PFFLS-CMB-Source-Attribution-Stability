#!/usr/bin/env python3
"""Clean-room audit of native EPA SJVF inputs; no EPA executable is invoked.

The documented configuration below was frozen before this reconstruction's first
fit. Expected manuscript outputs are consulted only after the fits. Raw inputs
and the complete per-sample ledger are never written to the public output tree.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import itertools
import json
from pathlib import Path
import platform
from zipfile import ZipFile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT.parent / "_inputs/strengthening_20260926/epa"
PUBLIC = ROOT / "outputs/strengthening_20260926"
PRIVATE = ROOT / "private/strengthening_20260926"
TRUSTED_ARCHIVE_HASHES = {
    "sjvf_data.zip": "3ca5bb3d4273e40f9c0f65a11f60e86fadafb525a086a046a9ef29a171fd229f",
    "pacs_data.zip": "e83d859f6a794504271ff4e84704787fe8b7a03e87940e6dcb105e560a7fef4f",
    "epa-cmb82test.zip": "f653311c3b9d0b89611a337b625e77d82d35650c852f5df8d7cb10c76f86d7ff",
    "sourcecmb82.zip": "44acea483c66cd5eb859340ecb7083fff18ab4b0401dde5d4f34972a22fbe8c9",
}
WORKED_COMPARATOR_SHA256 = "27b5a28132de94a09db836c7ad8d62183f6888372f138be18d989c695cbd2e0d"
CONFIG = {
    "version": "1.0.0",
    "data_archive": "sjvf_data.zip",
    "receptor_member": "ADsjvf.txt",
    "profile_member": "PRsjvf.txt",
    "receptor_filter": {"ID": "FRESNO", "SIZE": "FINE"},
    "expected_receptor_count": 35,
    "source_selector_member": "PRsjvf.sel",
    "source_selector_zero_based_column": 22,
    "central_initial_sources": ["SOIL03", "BAMAJC", "SFCRUC", "MOVES2", "AMSUL", "AMNIT", "NANO3"],
    "species_selector_member": "SPsjvf.sel",
    "species_selector_zero_based_column": 20,
    "identical_species_selector_column": 24,
    "species": ["N3IC", "S4IC", "N4TC", "KPAC", "NAAC", "ECTC", "OCTC", "ALXC", "SIXC", "CLXC", "KPXC", "CAXC", "TIXC", "VAXC", "CRXC", "MNXC", "FEXC", "NIXC", "BRXC", "PBXC"],
    "max_iterations": 20,
    "relative_tolerance": 0.01,
    "relative_denominator": "abs(new contribution); exact zero unchanged passes, changed-to-zero fails",
    "initial_contributions": "zero for every fresh fit",
    "numeric_precision": "float64",
    "linear_solver": "numpy.linalg.lstsq, rcond=None; fail on rank deficiency",
    "diagnostic_variance": "effective variance used in the final least-squares solve, not recomputed afterward",
    "central_controller": "fit; if converged remove the most negative source and restart from zero; stop when nonnegative; if nonconverged stop and mark unresolved, no source pruning from unconverged outputs",
    "alternative_controller": "replace the eligible source in the final central retained set; no pruning and no nonnegativity constraint",
    "alternative_descriptor_rules": {"SOIL03": "PAVED ROAD excluding UNPAVED", "BAMAJC": "CORDWOOD", "SFCRUC": "CRUDE BOILER", "MOVES2": "SID begins MOVES"},
    "expected_alternatives": {"SOIL03": ["SOIL08", "SOIL12", "SOIL29"], "BAMAJC": ["MAFISC", "MAMAJC"], "SFCRUC": ["CHCRUC"], "MOVES2": ["MOVES1", "MOVES3", "MOVES4", "MOVES5"]},
    "fit_filter": {"R2": [0.8, 1.0], "reduced_chi2": [0.0, 4.0], "percent_mass_stricter": [80.0, 120.0]},
    "ranking": "consistent central source slots; compare all pairwise signs and unique largest-source identity; ties recorded, not broken",
    "ranking_rounding_check_decimals": 5,
    "case_identity": {"ID": "FRESNO", "DATE": "05/10/89", "DUR": "24", "STHOUR": "0", "SIZE": "FINE"},
    "case_numeric_agreement": "round clean-room result to six decimal places and compare with published six-decimal value; no tuning",
    "configuration_basis": [
        "R3nR8 Main equations/methods and Supplement EPA alternatives, attrition and worked-case sections.",
        "Released SPsjvf.sel arrays 2/4 are identical 20-species arrays; PRsjvf.sel array 3 uniquely uses the declared SOIL03 central slot.",
        "EPA-CMB82DLLsrc.zip/CMB82a.for lines 542-545, 623-632, 724-736, 1004-1025: zero initialization, EVLS, stopping and diagnostics.",
        "Existing reviewed NFRAQS clean-room EVLS implementation used for method inspection only, not imported.",
    ],
    "limitations": [
        "This is a Python float64 clean-room implementation, not execution of the original EPA float32 Fortran/Delphi program.",
        "Original manuscript executable ledger and exact historical code remain unrecovered.",
        "Source precision, empty cells, raw uncertainty fields and sample/source selectors are not tuned to outcomes.",
    ],
}


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def freeze_configuration(private: Path) -> str:
    private.mkdir(parents=True, exist_ok=True)
    path = private / "epa_configuration_frozen.json"
    payload = json_bytes(CONFIG)
    if path.exists() and path.read_bytes() != payload:
        raise ValueError("configuration differs from frozen pre-fit record; stop rather than tune")
    if not path.exists():
        path.write_bytes(payload)
        (private / "epa_configuration_freeze_time.txt").write_text(
            datetime.now(timezone.utc).isoformat() + "\n", encoding="ascii")
    return sha256(payload)


def table(payload: bytes) -> list[dict[str, str]]:
    lines = [line.split() for line in payload.decode("ascii").splitlines() if line.strip()]
    if not lines or len(set(lines[0])) != len(lines[0]):
        raise ValueError("missing or duplicated table header")
    header = lines[0]
    if any(len(line) != len(header) for line in lines[1:]):
        raise ValueError("incomplete table row; no imputation permitted")
    return [dict(zip(header, line)) for line in lines[1:]]


def selected(payload: bytes, column: int, id_field: int = 0) -> list[str]:
    return [line.split()[id_field] for line in payload.decode("ascii").splitlines()
            if len(line) > column and line[column] == "*"]


def archive_inventory(inputs: Path) -> list[dict]:
    records = []
    for name in ("sjvf_data.zip", "pacs_data.zip", "epa-cmb82test.zip", "sourcecmb82.zip"):
        payload = (inputs / name).read_bytes()
        if sha256(payload) != TRUSTED_ARCHIVE_HASHES[name]:
            raise ValueError(f"untrusted archive identity before ZIP parsing: {name}")
        with ZipFile(BytesIO(payload)) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"bad ZIP CRC: {name}")
            members = [{"name": item.filename, "bytes": item.file_size,
                        "sha256": sha256(archive.read(item.filename))}
                       for item in archive.infolist() if not item.is_dir()]
        record = {"archive": name, "bytes": len(payload), "sha256": sha256(payload), "members": members}
        if name == "sourcecmb82.zip":
            with ZipFile(BytesIO(payload)) as outer:
                with ZipFile(BytesIO(outer.read("EPA-CMB82DLLsrc.zip"))) as inner:
                    native_source = inner.read("CMB82a.for")
            record["inspected_native_source"] = {
                "path": "sourcecmb82.zip/EPA-CMB82DLLsrc.zip/CMB82a.for",
                "bytes": len(native_source), "sha256": sha256(native_source),
                "used_for": "Method inspection only; not executed or redistributed.",
            }
        records.append(record)
    return records


def verify_recovery_identities(inventory: list[dict], recovery_record: Path) -> dict:
    payload = recovery_record.read_bytes()
    recorded = json.loads(payload)
    expected = {row["name"]: row for row in recorded["records"]}
    members_checked = 0
    for row in inventory:
        prior = expected[row["archive"]]
        if row["sha256"] != prior["sha256"] or row["bytes"] != prior["bytes"]:
            raise ValueError("native archive differs from independently recovered identity")
        actual_members = {m["name"]: (m["bytes"], m["sha256"]) for m in row["members"]}
        expected_members = {m["name"]: (m["bytes"], m["sha256"]) for m in prior["members"]}
        if actual_members != expected_members:
            raise ValueError("native archive member differs from recovered identity")
        members_checked += len(actual_members)
    return {"status": "PASS", "archives_checked": len(inventory),
            "members_checked": members_checked,
            "recovery_record_sha256": sha256(payload), "performed_before_fitting": True}


def load_inputs(inputs: Path) -> tuple[list[dict], dict[str, dict], dict]:
    with ZipFile(inputs / CONFIG["data_archive"]) as archive:
        receptors = table(archive.read(CONFIG["receptor_member"]))
        profiles_all = table(archive.read(CONFIG["profile_member"]))
        profile_selector = archive.read(CONFIG["source_selector_member"])
        species_selector = archive.read(CONFIG["species_selector_member"])
        source_ids = selected(profile_selector, CONFIG["source_selector_zero_based_column"], 1)
        species = selected(species_selector, CONFIG["species_selector_zero_based_column"])
        identical = selected(species_selector, CONFIG["identical_species_selector_column"])
        if source_ids != CONFIG["central_initial_sources"]:
            raise ValueError("declared central selector not reproduced")
        if species != CONFIG["species"] or identical != species:
            raise ValueError("declared 20-species selector not reproduced")
    chosen = [row for row in receptors
              if all(row[key] == value for key, value in CONFIG["receptor_filter"].items())]
    identity_fields = ("ID", "DATE", "DUR", "STHOUR", "SIZE")
    if (len(chosen) != CONFIG["expected_receptor_count"] or
            len({tuple(row[field] for field in identity_fields) for row in chosen}) != len(chosen)):
        raise ValueError("Fresno FINE receptor count or sample identity differs")
    profile_rows = [row for row in profiles_all if row["SIZE"] == "FINE"]
    profiles = {row["SID"]: row for row in profile_rows}
    if len(profiles) != len(profile_rows):
        raise ValueError("duplicated fine-fraction source mnemonic")
    descriptions = {}
    for line in profile_selector.decode("ascii").splitlines():
        if line.strip():
            fields = line[:36].split()
            descriptions[fields[1]] = line[36:].strip()
    alternatives = {}
    for central in CONFIG["expected_alternatives"]:
        admitted = []
        for sid, row in profiles.items():
            description = descriptions.get(sid, "")
            matches = ((central == "SOIL03" and "PAVED ROAD" in description and "UNPAVED" not in description)
                       or (central == "BAMAJC" and "CORDWOOD" in description)
                       or (central == "SFCRUC" and "CRUDE BOILER" in description)
                       or (central == "MOVES2" and sid.startswith("MOVES")))
            if not matches or sid == central:
                continue
            for species_name in species:
                for field in (species_name, species_name[:-1] + "U"):
                    if field not in row or not np.isfinite(float(row[field])):
                        raise ValueError("descriptor-matched source has missing fitting values")
            admitted.append(sid)
        alternatives[central] = sorted(admitted)
    if alternatives != CONFIG["expected_alternatives"]:
        raise ValueError(f"descriptor rule does not reproduce fixed alternatives: {alternatives}")
    return chosen, profiles, {
        "receptor_rows_in_archive": len(receptors), "fine_profiles_in_archive": len(profiles),
        "fresno_fine_samples": len(chosen), "species": species,
        "initial_source_ids": source_ids, "alternatives": alternatives,
        "species_arrays_2_and_4_identical": True,
    }


def effective_variance_fit(receptor: dict, profiles: dict, source_ids: list[str],
                           species: list[str] | None = None,
                           max_iterations: int | None = None) -> dict:
    """EVLS A-5--A-12; diagnostics use the final solve's effective variance."""
    species = CONFIG["species"] if species is None else species
    max_iterations = CONFIG["max_iterations"] if max_iterations is None else max_iterations
    if len(species) <= len(source_ids) or not source_ids or max_iterations < 1:
        raise ValueError("need positive residual degrees of freedom and iteration budget")
    c = np.asarray([float(receptor[name]) for name in species], dtype=float)
    uc = np.asarray([float(receptor[name[:-1] + "U"]) for name in species], dtype=float)
    f = np.asarray([[float(profiles[sid][name]) for sid in source_ids] for name in species], dtype=float)
    uf = np.asarray([[float(profiles[sid][name[:-1] + "U"]) for sid in source_ids]
                     for name in species], dtype=float)
    mass = float(receptor["TMAC"])
    if (not all(np.all(np.isfinite(array)) for array in (c, uc, f, uf))
            or np.any(uc <= 0) or np.any(uf < 0) or not np.isfinite(mass) or mass <= 0):
        raise ValueError("invalid concentration, uncertainty or ambient mass; no imputation")
    old = np.zeros(len(source_ids), dtype=float)
    converged = False
    history = []
    for iteration in range(1, max_iterations + 1):
        variance = uc ** 2 + (uf ** 2) @ (old ** 2)
        weighted_f = f / np.sqrt(variance)[:, None]
        weighted_c = c / np.sqrt(variance)
        new, _, rank, singular_values = np.linalg.lstsq(weighted_f, weighted_c, rcond=None)
        if rank != len(source_ids) or not np.all(np.isfinite(new)):
            raise ValueError("rank-deficient or nonfinite native fit; do not tune solver")
        relative = np.zeros(len(source_ids), dtype=float)
        nonzero = new != 0
        relative[nonzero] = np.abs(new[nonzero] - old[nonzero]) / np.abs(new[nonzero])
        relative[~nonzero] = np.where(old[~nonzero] == 0, 0, np.inf)
        history.append({"iteration": iteration,
                        "max_relative_change": float(relative.max()) if np.isfinite(relative.max()) else None,
                        "changed_to_zero": bool(np.any(~nonzero & (old != 0))),
                        "rank": int(rank), "smallest_singular_value": float(singular_values.min())})
        old = new
        if np.all(relative <= CONFIG["relative_tolerance"]):
            converged = True
            break
    residual = c - f @ new
    weighted_residual = float(np.sum(residual ** 2 / variance))
    weighted_observed = float(np.sum(c ** 2 / variance))
    if weighted_observed <= 0:
        raise ValueError("R-squared denominator is nonpositive")
    return {
        "converged": converged, "iterations": len(history), "history": history,
        "source_ids": list(source_ids), "source_contributions": dict(zip(source_ids, map(float, new))),
        "degrees_freedom": len(species) - len(source_ids),
        "R2": 1 - weighted_residual / weighted_observed,
        "reduced_chi2": weighted_residual / (len(species) - len(source_ids)),
        "percent_mass": 100 * float(np.sum(new)) / mass,
        "terminal_iterate_not_accepted_outcome_if_nonconverged": not converged,
    }


def central_fit(receptor: dict, profiles: dict) -> dict:
    sources = list(CONFIG["central_initial_sources"])
    removal_history = []
    while sources:
        result = effective_variance_fit(receptor, profiles, sources)
        result["central_removal_history"] = list(removal_history)
        if not result["converged"]:
            result["controller_status"] = "HOLD_NONCONVERGED_NO_PRUNING"
            return result
        worst = min(sources, key=result["source_contributions"].__getitem__)
        if result["source_contributions"][worst] >= 0:
            result["controller_status"] = "COMPLETE_NONNEGATIVE"
            return result
        removal_history.append({"removed_source": worst,
                                "negative_contribution": result["source_contributions"][worst],
                                "fit_iterations": result["iterations"]})
        sources.remove(worst)
    raise ValueError("central controller removed all sources")


def ranking_changes(central: dict[str, float], alternative: dict[str, float],
                    decimal_places: int | None = None) -> dict:
    if set(central) != set(alternative):
        raise ValueError("rank comparison requires identical source slots")
    a = {name: round(value, decimal_places) if decimal_places is not None else value
         for name, value in central.items()}
    b = {name: round(value, decimal_places) if decimal_places is not None else value
         for name, value in alternative.items()}
    def sign(value):
        return (value > 0) - (value < 0)
    pair_changes = [(x, y) for x, y in itertools.combinations(a, 2)
                    if sign(a[x] - a[y]) != sign(b[x] - b[y])]
    top_a = sorted(name for name, value in a.items() if value == max(a.values()))
    top_b = sorted(name for name, value in b.items() if value == max(b.values()))
    return {"ordering_change": bool(pair_changes), "pair_changes": pair_changes,
            "largest_source_change": top_a != top_b,
            "central_top_sources": top_a, "alternative_top_sources": top_b,
            "top_tie": len(top_a) != 1 or len(top_b) != 1}


def fit_targets(result: dict, strict: bool = False) -> bool:
    basic = result["converged"] and 0.8 <= result["R2"] <= 1 and 0 <= result["reduced_chi2"] <= 4
    return bool(basic and (not strict or 80 <= result["percent_mass"] <= 120))


def worked_case(receptors: list[dict], profiles: dict) -> tuple[dict, dict]:
    matches = [row for row in receptors if all(row[key] == value
               for key, value in CONFIG["case_identity"].items())]
    if len(matches) != 1:
        raise ValueError("worked sample does not have one exact match")
    receptor = matches[0]
    control = central_fit(receptor, profiles)
    runs = {"MOVES2": control}
    if control["converged"] and "MOVES2" in control["source_ids"]:
        for alternative in CONFIG["expected_alternatives"]["MOVES2"]:
            sources = [alternative if name == "MOVES2" else name for name in control["source_ids"]]
            runs[alternative] = effective_variance_fit(receptor, profiles, sources)
    expected_path = ROOT / "outputs/publication_archive_20260926/publication_derived/derived_data/epa_fresno_1989_05_10_publication_summary.csv"
    if sha256(expected_path.read_bytes()) != WORKED_COMPARATOR_SHA256:
        raise ValueError("published worked comparator identity changed")
    with expected_path.open(encoding="utf-8", newline="") as stream:
        expected_rows = list(csv.DictReader(stream))
    comparison = []
    for expected in expected_rows:
        name = expected["profile_id"]
        if name not in runs:
            comparison.append({"profile_id": name, "reconstructed": False, "all_fields_match": False})
            continue
        run = runs[name]
        metrics = {key: run[key] for key in ("R2", "reduced_chi2", "percent_mass")}
        metrics["MOVES_contribution_ug_m3"] = run["source_contributions"][name]
        differences = {key: value - float(expected[key]) for key, value in metrics.items()}
        matches = {key: round(value, 6) == float(expected[key]) for key, value in metrics.items()}
        top_sources = [source for source, value in run["source_contributions"].items()
                       if value == max(run["source_contributions"].values())]
        category = "MOVES" if top_sources == [name] else top_sources[0] if len(top_sources) == 1 else "TIE"
        top_match = category == expected["largest_source_category"]
        comparison.append({"profile_id": name, "converged": run["converged"],
                           "metrics": metrics, "difference_from_displayed": differences,
                           "rounds_to_all_four_published_values": all(matches.values()),
                           "largest_source_category": category, "largest_source_matches": top_match,
                           "all_fields_match": run["converged"] and all(matches.values()) and top_match})
    summary = {
        "sample_identity": CONFIG["case_identity"], "source_native_reconstruction": True,
        "control_retained_sources": control["source_ids"],
        "control_controller_status": control["controller_status"],
        "published_comparator_sha256": sha256(expected_path.read_bytes()),
        "all_five_runs_match_displayed_precision": len(comparison) == 5 and all(r["all_fields_match"] for r in comparison),
        "comparison": comparison,
    }
    return summary, runs


def full_substitutions(receptors: list[dict], profiles: dict) -> tuple[dict, dict]:
    central_runs, substitutions = [], []
    counts = {"eligible": 0, "converged": 0, "nonconverged": 0,
              "two_diagnostic": 0, "three_diagnostic": 0,
              "ordering_converged": 0, "largest_converged": 0,
              "ordering_two_diagnostic": 0, "largest_two_diagnostic": 0,
              "ordering_three_diagnostic": 0, "largest_three_diagnostic": 0}
    per_alternative = {name: {"eligible": 0, "converged": 0, "nonconverged": 0}
                       for names in CONFIG["expected_alternatives"].values() for name in names}
    rounding_disagreements = 0
    any_top_ties = 0
    for receptor in receptors:
        identity = {key: receptor[key] for key in CONFIG["case_identity"]}
        control = central_fit(receptor, profiles)
        central_runs.append({"sample": identity, "result": control})
        if not control["converged"]:
            return {"status": "HOLD_CENTRAL_NONCONVERGENCE", "all_35_central_fits_completed": False,
                    "central_fits_attempted": len(central_runs), "no_aggregate_comparison_claimed": True}, {
                        "central_runs": central_runs, "substitutions": substitutions}
        for central_slot, alternatives in CONFIG["expected_alternatives"].items():
            if central_slot not in control["source_ids"]:
                continue
            for alternative in alternatives:
                sources = [alternative if sid == central_slot else sid for sid in control["source_ids"]]
                result = effective_variance_fit(receptor, profiles, sources)
                row = {"sample": identity, "central_slot": central_slot, "alternative": alternative, "result": result}
                counts["eligible"] += 1
                per_alternative[alternative]["eligible"] += 1
                field = "converged" if result["converged"] else "nonconverged"
                counts[field] += 1
                per_alternative[alternative][field] += 1
                if result["converged"]:
                    mapped = {central_slot if sid == alternative else sid: value
                              for sid, value in result["source_contributions"].items()}
                    rank = ranking_changes(control["source_contributions"], mapped)
                    rounded = ranking_changes(control["source_contributions"], mapped,
                                               CONFIG["ranking_rounding_check_decimals"])
                    row["ranking"] = rank
                    row["ranking_rounded"] = rounded
                    mismatch = any(rank[key] != rounded[key] for key in ("pair_changes", "largest_source_change"))
                    rounding_disagreements += int(mismatch)
                    any_top_ties += int(rank["top_tie"] or rounded["top_tie"])
                    two = fit_targets(control) and fit_targets(result)
                    three = fit_targets(control, True) and fit_targets(result, True)
                    row["two_diagnostic"] = two
                    row["three_diagnostic"] = three
                    counts["two_diagnostic"] += int(two)
                    counts["three_diagnostic"] += int(three)
                    for label, included in (("converged", True), ("two_diagnostic", two), ("three_diagnostic", three)):
                        if included:
                            counts["ordering_" + label] += int(rank["ordering_change"])
                            counts["largest_" + label] += int(rank["largest_source_change"])
                substitutions.append(row)
    expected = {"eligible": 345, "converged": 323, "nonconverged": 22,
                "two_diagnostic": 283, "three_diagnostic": 26,
                "ordering_converged": 167, "largest_converged": 81,
                "ordering_two_diagnostic": 133, "largest_two_diagnostic": 62,
                "ordering_three_diagnostic": 10, "largest_three_diagnostic": 2}
    return {
        "status": "RECONSTRUCTED_MATCH" if counts == expected else "RECONSTRUCTED_DIFFERENCES",
        "all_35_central_fits_completed": len(central_runs) == 35,
        "computed_counts": counts, "reported_counts": expected,
        "differences": {key: counts[key] - expected[key] for key in counts},
        "per_alternative_attrition": per_alternative,
        "rank_decision_disagreements_after_rounding_5dp": rounding_disagreements,
        "converged_runs_with_top_tie_before_or_after_rounding": any_top_ties,
        "source_native_recomputed": True,
        "historical_original_execution_ledger_recovered": False,
    }, {"central_runs": central_runs, "substitutions": substitutions}


def validate_output_paths(inputs: Path, public: Path, private: Path, root: Path = ROOT) -> None:
    private_root = (root / "private").resolve()
    private_resolved = private.resolve()
    public_resolved = public.resolve()
    if private_resolved == private_root or not private_resolved.is_relative_to(private_root):
        raise ValueError("row ledger must be in a dedicated subdirectory under repository private/")
    if public_resolved != (root / "outputs/strengthening_20260926").resolve():
        raise ValueError("public output must be the dedicated strengthening output directory")
    if any(target.is_relative_to(inputs.resolve()) or inputs.resolve().is_relative_to(target)
           for target in (private_resolved, public_resolved)):
        raise ValueError("output overlaps source-archive directory")


def run(inputs: Path, public: Path, private: Path) -> dict:
    validate_output_paths(inputs, public, private)
    config_hash = freeze_configuration(private)  # Must precede all fitting.
    inventory = archive_inventory(inputs)
    identities = verify_recovery_identities(inventory, ROOT / "outputs/strengthening_20260926/source_recovery.json")
    receptors, profiles, input_summary = load_inputs(inputs)
    case_summary, case_ledger = worked_case(receptors, profiles)
    if case_summary["all_five_runs_match_displayed_precision"]:
        aggregate, full_ledger = full_substitutions(receptors, profiles)
    else:
        aggregate = {"status": "HOLD_CASE_MISMATCH_FULL_RUN_NOT_ATTEMPTED", "source_native_recomputed": False}
        full_ledger = {}
    private_payload = json_bytes({"configuration_sha256": config_hash,
                                  "case_runs": case_ledger, "full_runs": full_ledger})
    (private / "epa_native_ledger.json").write_bytes(private_payload)
    report = {
        "audit_date": "2026-09-26", "configuration_sha256": config_hash,
        "audit_script_sha256": sha256(Path(__file__).read_bytes()),
        "configuration": CONFIG, "input_inventory": inventory,
        "recovery_identity_verification": identities,
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "randomness": "none"},
        "input_summary": input_summary, "worked_case": case_summary, "full_aggregate": aggregate,
        "private_ledger_sha256": sha256(private_payload),
        "public_scope": "Code, configuration, hashes, aggregate results and comparison with already-published worked-case summary only. No raw archive or full per-sample contribution ledger redistributed.",
        "decision": "KEEP clean-room numerical reconstruction if matching; HOLD any assertion of original executable/ledger recovery or independent field accuracy. No manuscript/baseline modification.",
    }
    public.mkdir(parents=True, exist_ok=True)
    (public / "epa_native_reconstruction.json").write_bytes(json_bytes(report))
    (public / "EPA_NATIVE_RECONSTRUCTION.md").write_text(render_report(report), encoding="utf-8", newline="\n")
    return report


def render_report(report: dict) -> str:
    case, aggregate = report["worked_case"], report["full_aggregate"]
    details = "\n".join(f"| {row['profile_id']} | {row.get('converged', False)} | {row.get('rounds_to_all_four_published_values', False)} | {row.get('largest_source_matches', False)} |"
                        for row in case["comparison"])
    count_rows = "\n".join(f"| {key} | {value} | {aggregate['reported_counts'][key]} | {aggregate['differences'][key]} |"
                           for key, value in aggregate.get("computed_counts", {}).items())
    return f"""# EPA native-input clean-room reconstruction — 26 September 2026

## Result and limits

Worked Fresno 10 May 1989: all five central/MOVES runs reproduce all four
published numeric values to six decimal places and the reported largest-source
category: **{case['all_five_runs_match_displayed_precision']}**.
Full-run status: **{aggregate['status']}**.

This executes an independently written Python float64 EVLS reconstruction on
newly recovered official EPA input files. It does not execute the original EPA
float32 Fortran/Delphi software, recover the historical original ledger, establish
environmental accuracy, or alter the active manuscript baseline. A successful
result is source-native clean-room numerical reconstruction, not merely checking
publication-summary arithmetic. PACS is inventoried but not numerically audited here.

## Configuration frozen before fitting

Configuration SHA-256: `{report['configuration_sha256']}`.
The private freeze record is written and checked before fitting; a changed
configuration is rejected. No profiles, species, tolerances or solver settings
were selected to improve agreement with the reported results. Targets were
already known from the task and manuscript, so this is not a blinded replication.

Native `PRsjvf.sel` array 3 supplies SOIL03, BAMAJC, SFCRUC, MOVES2, AMSUL,
AMNIT and NANO3. Native `SPsjvf.sel` arrays 2 and 4 are identical and provide
20 fitting species. The complete FRESNO/FINE receptor filter gives 35 unique
24-hour samples. Native descriptors independently regenerate all ten declared
alternatives, including PAVED ROAD with UNPAVED excluded.

EVLS starts from zero; uses released receptor and profile uncertainties without
rescaling; allows 20 solves; and stops when every nonzero new contribution changes
by at most 1% relative to its new value. Diagnostics use the weights of the last
solve. Central fits sequentially remove the most negative source after a converged
fit and restart; alternatives retain the final central source set, substituting
only the declared profile and recomputing effective weights. Unconverged
alternatives are excluded from allocation outcomes rather than imputed.

Official `sourcecmb82.zip` / `EPA-CMB82DLLsrc.zip` / `CMB82a.for` was inspected:
lines 542–545 initialize contributions to zero; 623–632 form effective variance;
724–736 use new-contribution relative stopping; 1004–1025 compute diagnostics.
The legacy implementation's undefined exact-zero stopping corner is not copied:
an unchanged exact zero passes and a changed-to-zero contribution fails the
relative test. No profile renormalization, forced nonnegative alternative fit,
extra species, covariance or accuracy reference is introduced.

## Worked-case check

| Run | Converged | Four values match at six decimals | Largest source matches |
|---|---|---|---|
{details}

The four quantities are MOVES contribution, R-squared, reduced chi-square and
percent mass. Full calculated values, signed differences and input SHA-256
identities are recorded in `epa_native_reconstruction.json`. The central retained
sources are {', '.join(case['control_retained_sources'])}.

## Aggregate comparison

| Quantity | Native clean-room | Manuscript | Difference |
|---|---:|---:|---:|
{count_rows}

Pairwise and largest-source decisions changing after five-decimal rounding:
**{aggregate.get('rank_decision_disagreements_after_rounding_5dp', 'not evaluated')}**.
Converged runs with a top-source tie before or after rounding:
**{aggregate.get('converged_runs_with_top_tie_before_or_after_rounding', 'not evaluated')}**.
All alternative-specific eligibility/convergence counts are retained in the JSON.

The full private ledger retains unrounded contributions, convergence histories,
source-removal decisions, every eligible substitution, complete pairwise changes,
subset masks and the five-decimal ranking check. Its SHA-256 is
`{report['private_ledger_sha256']}`. It is not copied to the public return package.
No negative or discordant reconstruction result is hidden.

## Reproduce

```text
python scripts/audit_epa_native_strengthening.py --inputs <official-EPA-archive-directory>
python -m unittest discover -s tests -p test_epa_native_strengthening.py -v
```

Required archives: `sjvf_data.zip`, `pacs_data.zip`, `epa-cmb82test.zip`,
`sourcecmb82.zip`. Exact ZIP and member hashes are in the JSON inventory.
All four archive identities and all {report['recovery_identity_verification']['members_checked']}
member identities are checked against the independent `source_recovery.json`
record before fitting. Configuration and implementing-script hashes are public.
Validated with Python {report['environment']['python']} and NumPy {report['environment']['numpy']}.
Tests of native inputs skip explicitly if these
third-party archives are unavailable; synthetic solver tests remain runnable.
Raw archives remain outside the repository; full row-level derived results stay
under the ignored private directory. Redistribution rights are not inferred.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--private", type=Path, default=PRIVATE)
    args = parser.parse_args()
    report = run(args.inputs, args.public, args.private)
    print(json.dumps({"case_match": report["worked_case"]["all_five_runs_match_displayed_precision"],
                      "aggregate": report["full_aggregate"]}, indent=2))


if __name__ == "__main__":
    main()
