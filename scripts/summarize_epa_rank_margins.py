#!/usr/bin/env python3
"""Exploratory EPA margins from pinned saved fits; standard library, no refitting."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parent / "PFFLS-CMB-Source-Attribution-Stability"
PUBLIC = ROOT / "outputs/continuous_research_20260927/editor_response_20260928"
PRIVATE = ROOT / "private/editor_response_20260928/epa_margins"
IDENTITY = ("ID", "DATE", "DUR", "STHOUR", "SIZE")
PINS = {
    "ledger": "0e3c5c5b74e5f0838a95459ad348de6b49213be0898ff9627915e645881afa9f",
    "configuration": "6d3b10b2090526e3f15e987cc1b796fb02736570e2b3284738001956cacadc39",
    "report": "cf97474a6b5fdacff6eb4949fc776aebc9af4482ee607b390b3bce5ffb7c9bf6",
    "recovery": "4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2",
    "archive": "3ca5bb3d4273e40f9c0f65a11f60e86fadafb525a086a046a9ef29a171fd229f",
    "receptor_member": "49db3300d44991b10c4fc1d041daa7d97428e58d9e2fc9e7bb10036bffe760f0",
    "original_script": "42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09",
    "plan": "41333fb8b74c563e3c5a89b4fb42df6d11a7c62dcf768172cab889a86d80b313",
}
EXPECTED = {
    "eligible": 345, "converged": 323, "nonconverged": 22,
    "two_diagnostic": 283, "three_diagnostic": 26,
    "ordering_converged": 167, "largest_converged": 81,
    "ordering_two_diagnostic": 133, "largest_two_diagnostic": 62,
    "ordering_three_diagnostic": 10, "largest_three_diagnostic": 2,
}
GENERAL = ("central_top_two_gap", "alternative_top_two_gap", "substituted_abs_change",
           "allocation_L1_change", "allocation_Linf_change")
CROSS = ("cross_before", "cross_after", "cross_swing", "cross_min")
GROUPS = ("all_converged", "two_diagnostic", "three_diagnostic",
          "top_change_two_diagnostic", "top_change_three_diagnostic")
UNITS = ("ug_m3", "pct_ambient_pm")


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def decode_json(payload: bytes):
    def reject_constant(value):
        raise ValueError("nonfinite JSON constant")
    return json.loads(payload, object_pairs_hook=unique_object, parse_constant=reject_constant)


def number(value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("required finite numerical value")
    return value


def sample_key(sample: dict) -> tuple[str, ...]:
    if set(sample) != set(IDENTITY) or any(not isinstance(sample[k], str) or not sample[k] for k in IDENTITY):
        raise ValueError("incomplete five-field sample identity")
    return tuple(sample[k] for k in IDENTITY)


def parse_masses(payload: bytes, receptor_filter: dict) -> dict:
    lines = [line.split() for line in payload.decode("ascii").splitlines() if line.strip()]
    if not lines or len(set(lines[0])) != len(lines[0]):
        raise ValueError("missing or duplicated native header")
    header = lines[0]
    if not set(IDENTITY + ("TMAC",)).issubset(header):
        raise ValueError("native identity or measured-mass column absent")
    seen, masses = set(), {}
    for fields in lines[1:]:
        if len(fields) != len(header):
            raise ValueError("incomplete native row")
        row = dict(zip(header, fields))
        key = sample_key({k: row[k] for k in IDENTITY})
        if key in seen:
            raise ValueError("duplicate native five-field identity")
        seen.add(key)
        if all(row[k] == v for k, v in receptor_filter.items()):
            mass = number(float(row["TMAC"]))
            if mass <= 0:
                raise ValueError("measured ambient mass must be positive")
            masses[key] = mass
    return masses


def contribution_vector(result: dict) -> dict:
    ids, vector = result["source_ids"], result["source_contributions"]
    if (not isinstance(ids, list) or len(ids) < 2 or len(set(ids)) != len(ids)
            or set(ids) != set(vector) or any(not isinstance(sid, str) for sid in ids)):
        raise ValueError("source list and contribution keys disagree")
    if type(result["converged"]) is not bool:
        raise ValueError("convergence flag must be boolean")
    for value in vector.values():
        number(value)
    for field in ("R2", "reduced_chi2", "percent_mass"):
        number(result[field])
    return vector


def mapped_vector(control: dict, result: dict, slot: str, alternative: str) -> dict:
    vector = contribution_vector(result)
    expected_ids = [alternative if sid == slot else sid for sid in control["source_ids"]]
    if (slot not in control["source_ids"] or alternative in control["source_ids"]
            or result["source_ids"] != expected_ids):
        raise ValueError("alternative does not preserve one-to-one central source slots")
    mapped = {slot if sid == alternative else sid: value for sid, value in vector.items()}
    if len(mapped) != len(vector) or set(mapped) != set(control["source_ids"]):
        raise ValueError("alternative mapping collides or changes retained slots")
    return mapped


def ranking(a: dict, b: dict, decimals: int | None = None) -> dict:
    if set(a) != set(b):
        raise ValueError("ranking requires equal source slots")
    a = {k: round(v, decimals) if decimals is not None else v for k, v in a.items()}
    b = {k: round(v, decimals) if decimals is not None else v for k, v in b.items()}
    def sign(value):
        return (value > 0) - (value < 0)
    changes = [[x, y] for x, y in itertools.combinations(a, 2)
               if sign(a[x] - a[y]) != sign(b[x] - b[y])]
    top_a = sorted(k for k, v in a.items() if v == max(a.values()))
    top_b = sorted(k for k, v in b.items() if v == max(b.values()))
    return {"ordering_change": bool(changes), "pair_changes": changes,
            "largest_source_change": top_a != top_b,
            "central_top_sources": top_a, "alternative_top_sources": top_b,
            "top_tie": len(top_a) != 1 or len(top_b) != 1}


def targets(result: dict, strict: bool = False) -> bool:
    basic = (result["converged"] and 0.8 <= result["R2"] <= 1
             and 0 <= result["reduced_chi2"] <= 4)
    return bool(basic and (not strict or 80 <= result["percent_mass"] <= 120))


def validate_ledger(ledger: dict, config: dict, masses: dict, expected: dict = EXPECTED) -> tuple[dict, dict]:
    """Validate the complete eligibility universe before computing new margins."""
    central = {}
    for row in ledger["full_runs"]["central_runs"]:
        key, result = sample_key(row["sample"]), row["result"]
        if key in central:
            raise ValueError("duplicate central sample")
        vector = contribution_vector(result)
        if (not result["converged"] or result["controller_status"] != "COMPLETE_NONNEGATIVE"
                or any(value < 0 for value in vector.values())):
            raise ValueError("central fit not completed nonnegative")
        retained = list(config["central_initial_sources"])
        for removal in result["central_removal_history"]:
            sid = removal["removed_source"]
            if sid not in retained or number(removal["negative_contribution"]) >= 0:
                raise ValueError("invalid central source-removal record")
            retained.remove(sid)
        if result["source_ids"] != retained:
            raise ValueError("central source list does not follow recorded removals")
        central[key] = result
    if len(central) != config["expected_receptor_count"] or set(central) != set(masses):
        raise ValueError("central sample universe or complete native mass join differs")
    if any(number(mass) <= 0 for mass in masses.values()):
        raise ValueError("measured ambient mass must be positive")
    universe = {(key, slot, alt) for key, result in central.items()
                for slot, alternatives in config["expected_alternatives"].items()
                if slot in result["source_ids"] for alt in alternatives}
    seen, counts = set(), {name: 0 for name in EXPECTED}
    for row in ledger["full_runs"]["substitutions"]:
        key = sample_key(row["sample"])
        run_key = (key, row["central_slot"], row["alternative"])
        if run_key not in universe or run_key in seen:
            raise ValueError("duplicate or ineligible substitution key")
        seen.add(run_key)
        control, result = central[key], row["result"]
        mapped = mapped_vector(control, result, row["central_slot"], row["alternative"])
        counts["eligible"] += 1
        counts["converged" if result["converged"] else "nonconverged"] += 1
        if result.get("terminal_iterate_not_accepted_outcome_if_nonconverged") is not (not result["converged"]):
            raise ValueError("terminal-iterate status inconsistent")
        if not result["converged"]:
            if any(name in row for name in ("ranking", "ranking_rounded", "two_diagnostic", "three_diagnostic")):
                raise ValueError("nonconverged row has accepted classification fields")
            continue
        raw = ranking(control["source_contributions"], mapped)
        rounded = ranking(control["source_contributions"], mapped, config["ranking_rounding_check_decimals"])
        if raw != row["ranking"] or rounded != row["ranking_rounded"]:
            raise ValueError("saved rank decisions differ from saved vectors")
        if raw["top_tie"] or rounded["top_tie"]:
            raise ValueError("unexpected top tie")
        if any(raw[name] != rounded[name] for name in ("pair_changes", "largest_source_change")):
            raise ValueError("unexpected five-decimal classification disagreement")
        two, three = targets(control) and targets(result), targets(control, True) and targets(result, True)
        if row["two_diagnostic"] is not two or row["three_diagnostic"] is not three:
            raise ValueError("saved diagnostic mask differs")
        counts["two_diagnostic"] += int(two)
        counts["three_diagnostic"] += int(three)
        for group, included in (("converged", True), ("two_diagnostic", two), ("three_diagnostic", three)):
            if included:
                counts["ordering_" + group] += int(raw["ordering_change"])
                counts["largest_" + group] += int(raw["largest_source_change"])
    if seen != universe:
        raise ValueError("incomplete substitution eligibility universe")
    if counts != expected:
        raise ValueError("saved outcome counts differ from the fixed record")
    return central, counts


def top_two(vector: dict) -> dict:
    if len(vector) < 2:
        raise ValueError("top-two margin needs at least two slots")
    values = sorted(vector.values(), reverse=True)
    return {"winners": sorted(k for k, v in vector.items() if v == values[0]),
            "runners_up": sorted(k for k, v in vector.items() if v == values[1]),
            "gap": values[0] - values[1]}


def margin_values(a: dict, b: dict, mass: float, slot: str) -> dict:
    if set(a) != set(b) or slot not in a:
        raise ValueError("margin source slots differ")
    if number(mass) <= 0:
        raise ValueError("measured ambient mass must be positive")
    for value in itertools.chain(a.values(), b.values()):
        number(value)
    before, after = top_two(a), top_two(b)
    if len(before["winners"]) != 1 or len(after["winners"]) != 1:
        raise ValueError("top tie has no unique cross-margin winner")
    p, q = before["winners"][0], after["winners"][0]
    delta = {k: b[k] - a[k] for k in a}
    raw = {"central_top_two_gap": before["gap"], "alternative_top_two_gap": after["gap"],
           "substituted_delta": delta[slot], "substituted_abs_change": abs(delta[slot]),
           "allocation_L1_change": sum(abs(v) for v in delta.values()),
           "allocation_Linf_change": max(abs(v) for v in delta.values()),
           **{name: None for name in CROSS},
           "old_minus_new_before": None, "old_minus_new_after": None}
    if p != q:
        c0, c1 = a[p] - a[q], b[q] - b[p]
        if c0 <= 0 or c1 <= 0:
            raise ValueError("unique-winner reversal has nonpositive cross-margin")
        raw.update(cross_before=c0, cross_after=c1, cross_swing=c0 + c1,
                   cross_min=min(c0, c1), old_minus_new_before=c0, old_minus_new_after=-c1)
    metrics = {f"{name}_{unit}": (None if value is None else value if unit == "ug_m3" else 100 * value / mass)
               for name, value in raw.items() for unit in UNITS}
    return {"central_top": before, "alternative_top": after,
            "central_vector_ug_m3": dict(a), "alternative_vector_ug_m3": dict(b),
            "source_delta_ug_m3": delta, "source_delta_pct_ambient_pm": {k: 100 * v / mass for k, v in delta.items()},
            "ambient_mass_ug_m3": mass, "metrics": metrics}


def descriptive(values: list[float]) -> dict:
    values = sorted(number(v) for v in values)
    if not values:
        return {"n": 0, **{name: None for name in ("min", "p10", "median", "p90", "max")}}
    def quantile(p):
        h = (len(values) - 1) * p
        lo, hi = math.floor(h), math.ceil(h)
        return (1 - (h - lo)) * values[lo] + (h - lo) * values[hi]
    return {"n": len(values), "min": values[0], "p10": quantile(0.1),
            "median": quantile(0.5), "p90": quantile(0.9), "max": values[-1]}


def analyze(ledger: dict, config: dict, masses: dict, expected: dict = EXPECTED) -> tuple[dict, dict]:
    central, counts = validate_ledger(ledger, config, masses, expected)
    rows, groups = [], {name: [] for name in GROUPS}
    for source in ledger["full_runs"]["substitutions"]:
        key, result = sample_key(source["sample"]), source["result"]
        row = {"original": source, "ambient_mass_ug_m3": masses[key], "derived": None}
        if result["converged"]:
            control = central[key]
            b = mapped_vector(control, result, source["central_slot"], source["alternative"])
            row["derived"] = margin_values(control["source_contributions"], b, masses[key], source["central_slot"])
            groups["all_converged"].append(row)
            for group in ("two_diagnostic", "three_diagnostic"):
                if source[group]:
                    groups[group].append(row)
                    if source["ranking"]["largest_source_change"]:
                        groups["top_change_" + group].append(row)
        rows.append(row)
    summaries = {}
    for name, members in groups.items():
        metrics = GENERAL + (CROSS if name.startswith("top_change_") else ())
        summaries[name] = {"substitutions": len(members),
            "unique_samples": len({sample_key(row["original"]["sample"]) for row in members}),
            "metrics": {f"{metric}_{unit}": descriptive([row["derived"]["metrics"][f"{metric}_{unit}"] for row in members])
                        for metric in metrics for unit in UNITS}}
    return ({"counts": counts, "groups": summaries},
            {"central_runs": ledger["full_runs"]["central_runs"], "substitutions": rows,
             "nonconverged_new_outcomes": "null; terminal iterates are not accepted outcomes"})


def validate_paths(public: Path, private: Path, input_paths: list[Path], root: Path = ROOT) -> None:
    public, private = public.resolve(), private.resolve()
    if public != (root / "outputs/continuous_research_20260927/editor_response_20260928").resolve():
        raise ValueError("public output must be the dedicated aggregate candidate directory")
    if private != (root / "private/editor_response_20260928/epa_margins").resolve():
        raise ValueError("full derived ledger must stay in the dedicated private directory")
    permitted_plan = public / "EPA_MARGIN_PLAN.md"
    if any((target == path.resolve() or target in path.resolve().parents)
           and path.resolve() != permitted_plan
           for target in (public, private) for path in input_paths):
        raise ValueError("output overlaps an input location")


def load_pinned(paths: dict) -> tuple[dict, dict, dict, dict]:
    payloads = {name: path.read_bytes() for name, path in paths.items()}
    for name, payload in payloads.items():
        if digest(payload) != PINS[name]:
            raise ValueError(f"pinned input identity differs: {name}")
    ledger, config, report, recovery = (decode_json(payloads[k]) for k in ("ledger", "configuration", "report", "recovery"))
    if (ledger["configuration_sha256"] != PINS["configuration"]
            or report["configuration_sha256"] != PINS["configuration"]
            or report["private_ledger_sha256"] != PINS["ledger"]
            or report["audit_script_sha256"] != PINS["original_script"]
            or report["configuration"] != config
            or report["recovery_identity_verification"]["recovery_record_sha256"] != PINS["recovery"]
            or report["full_aggregate"]["computed_counts"] != EXPECTED):
        raise ValueError("pinned provenance objects disagree")
    native = [r for r in recovery["records"] if r["name"] == "sjvf_data.zip"]
    reported = [r for r in report["input_inventory"] if r["archive"] == "sjvf_data.zip"]
    if len(native) != 1 or len(reported) != 1 or native[0]["sha256"] != PINS["archive"] or reported[0]["sha256"] != PINS["archive"]:
        raise ValueError("recovery and reconstruction archive identities disagree")
    for record in (native[0], reported[0]):
        members = [m for m in record["members"] if m["name"] == "ADsjvf.txt"]
        if len(members) != 1 or members[0]["sha256"] != PINS["receptor_member"]:
            raise ValueError("receptor member provenance disagrees")
    with ZipFile(BytesIO(payloads["archive"])) as archive:
        if archive.namelist().count("ADsjvf.txt") != 1:
            raise ValueError("duplicate or missing native receptor member")
        receptor = archive.read("ADsjvf.txt")
    if digest(receptor) != PINS["receptor_member"]:
        raise ValueError("native receptor member bytes differ")
    return ledger, config, parse_masses(receptor, config["receptor_filter"]), report


def render(summary: dict) -> str:
    lines = ["# Exploratory EPA rank margins from saved fits", "",
             "Post-review descriptive analysis, specified after the original counts were known.",
             "No fits were rerun. These margins are neither uncertainty intervals nor evidence of environmental accuracy.", "",
             "All groups are substitution-weighted and nested. Repeated dates/central margins are not independent replications.",
             "The strict top-change group contains only two events. No practical-significance threshold was selected.", "",
             "Units: ug_m3 = micrograms per cubic metre; pct_ambient_pm = 100 times the quantity divided by that sample's measured TMAC.",
             "Cross-before = old winner minus new winner before substitution; cross-after = new winner minus old winner afterward.",
             "The cross pair need not be either fit's top-two pair. L1 is unhalved and is not transferred mass.",
             "Quantiles use h=(n-1)p with linear interpolation of adjacent sorted values.", ""]
    for name, group in summary["groups"].items():
        lines += [f"## {name}", "", f"{group['substitutions']} substitutions; {group['unique_samples']} unique sample identities.", "",
                  "| Quantity and units | n | Min | P10 | Median | P90 | Max |", "|---|---:|---:|---:|---:|---:|---:|"]
        for metric, stats in group["metrics"].items():
            fields = [str(stats["n"])] + ["null" if stats[k] is None else format(stats[k], ".10g") for k in ("min", "p10", "median", "p90", "max")]
            lines.append(f"| {metric} | " + " | ".join(fields) + " |")
        lines.append("")
    lines += ["## Provenance and limits", "", "Every eligible substitution remains in the private ledger; the 22 nonconverged rows have null new outcomes.",
              "Input hashes, unchanged mask/count checks, source identity and full-precision summaries accompany this note in epa_rank_margins_summary.json.",
              "Full vectors, identities and measured masses remain private. Small or large fitted gaps do not establish statistical or policy significance.", "",
              f"Derived private ledger SHA-256: `{summary['private_ledger_sha256']}`.",
              f"Postprocessor SHA-256: `{summary['postprocessor_sha256']}`.", ""]
    return "\n".join(lines)


def run(paths: dict, public: Path, private: Path) -> dict:
    wall, cpu = time.perf_counter(), time.process_time()
    started = datetime.now(timezone.utc).isoformat()
    validate_paths(public, private, list(paths.values()))
    outputs = [private / "epa_rank_margins_ledger.json", public / "epa_rank_margins_summary.json", public / "EPA_RANK_MARGINS.md"]
    if any(path.exists() for path in outputs):
        raise ValueError("refusing to overwrite an existing output")
    ledger, config, masses, _ = load_pinned(paths)
    summary, private_result = analyze(ledger, config, masses)
    source_hash = digest(Path(__file__).read_bytes())
    private_result.update(input_sha256=PINS, postprocessor_sha256=source_hash)
    private_payload = json_bytes(private_result)
    summary.update(status="SAVED_LEDGER_DESCRIPTIVE_EXTENSION", exploratory_post_review=True,
        input_sha256=PINS, postprocessor_sha256=source_hash,
        private_ledger_sha256=digest(private_payload), python=platform.python_version(),
        started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds_before_output=time.perf_counter() - wall, cpu_seconds_before_output=time.process_time() - cpu,
        new_model_fits=0, numerical_randomness="none", original_eligible_universe_validated=True,
        new_outcomes_for_nonconverged="null", quantiles="sorted linear interpolation, h=(n-1)*p",
        interpretation="Nested substitution-weighted descriptive magnitudes only; no confidence interval, significance cutoff, source truth or superiority claim.")
    public_payload, markdown = json_bytes(summary), render(summary)
    private.mkdir(parents=True, exist_ok=True)
    public.mkdir(parents=True, exist_ok=True)
    with outputs[0].open("xb") as stream:
        stream.write(private_payload)
    with outputs[1].open("xb") as stream:
        stream.write(public_payload)
    with outputs[2].open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(markdown)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=ORIGINAL / "private/strengthening_20260926/epa_native_ledger.json")
    parser.add_argument("--configuration", type=Path, default=ORIGINAL / "private/strengthening_20260926/epa_configuration_frozen.json")
    parser.add_argument("--report", type=Path, default=ROOT / "outputs/strengthening_20260926/epa_native_reconstruction.json")
    parser.add_argument("--recovery", type=Path, default=ORIGINAL / "outputs/strengthening_20260926/source_recovery.json")
    parser.add_argument("--archive", type=Path, default=ROOT.parent / "_inputs/strengthening_20260926/epa/sjvf_data.zip")
    parser.add_argument("--original-script", type=Path, default=ROOT / "scripts/audit_epa_native_strengthening.py")
    parser.add_argument("--plan", type=Path, default=PUBLIC / "EPA_MARGIN_PLAN.md")
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--private", type=Path, default=PRIVATE)
    args = parser.parse_args()
    paths = {name: getattr(args, name) for name in ("ledger", "configuration", "report", "recovery", "archive", "original_script", "plan")}
    try:
        summary = run(paths, args.public, args.private)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "STOPPED", "reason": str(exc), "new_model_fits": 0}), file=sys.stderr)
        return 1
    print(json.dumps({"status": summary["status"], "counts": summary["counts"],
                      "private_ledger_sha256": summary["private_ledger_sha256"], "new_model_fits": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
