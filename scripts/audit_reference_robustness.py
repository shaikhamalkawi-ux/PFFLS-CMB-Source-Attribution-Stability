"""Conditional L1 reference-ranking certificates from publication-derived scores.

This is not a raw CMB reproduction, an uncertainty model, or a significance test.
Only Python's standard library is required. All published input files are read-only.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import platform
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "outputs/publication_archive_20260926/publication_derived/derived_data"
DEFAULT_OUTPUT = ROOT / "outputs/strengthening_20260926"
ZERO = Decimal(0)
HUNDRED = Decimal(100)
REFERENCE_KEYS = ("BioB", "SO4", "NO3", "DUST", "ROAD", "SALT", "TRA", "INDU")


def finite_decimal(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid numeric input: {value!r}") from error
    if not result.is_finite():
        raise ValueError("Non-finite numeric input")
    return result


def exact_text(value: Decimal) -> str:
    """JSON strings retain all decimal precision and avoid binary float artifacts."""
    return format(value, "f")


def l1_distance(left: Iterable[object], right: Iterable[object]) -> Decimal:
    a, b = list(map(finite_decimal, left)), list(map(finite_decimal, right))
    if not a or len(a) != len(b):
        raise ValueError("Vectors must have equal, nonzero dimension")
    return sum((abs(x - y) for x, y in zip(a, b)), ZERO)


def normalized_error_percent(allocation: Iterable[object], reference: Iterable[object]) -> Decimal:
    ref = list(map(finite_decimal, reference))
    total = sum(ref, ZERO)
    if total <= ZERO:
        raise ValueError("The shared reference total must be positive")
    return HUNDRED * l1_distance(allocation, ref) / total


def radius_certificate(
    error_a_pp: object,
    error_b_pp: object,
    reference_total: object,
    absolute_score_error_bound_pp: object = "0.01",
) -> dict:
    """Sufficient open-ball radius for preserving an L1-distance ordering.

    e_a,e_b are percentages, not fractions. Each underlying score is assumed
    within b percentage points of its displayed value. Hence the absolute
    distance gap is at least max(0, |e_a-e_b|-2b)*T/100. Triangle inequality
    gives preservation whenever ||r'-r||_1 is STRICTLY less than half this gap.
    The default b=0.01 uses a full displayed unit rather than assuming rounding
    to nearest. It is a declared reporting-precision envelope, not statistical
    uncertainty. It does not include bias or error in original computations.
    """
    ea, eb, total, bound = map(
        finite_decimal,
        (error_a_pp, error_b_pp, reference_total, absolute_score_error_bound_pp),
    )
    if ea < ZERO or eb < ZERO or bound < ZERO or total <= ZERO:
        raise ValueError("Errors/bound must be nonnegative and total positive")
    gap = abs(ea - eb)
    lower_gap = max(ZERO, gap - 2 * bound)
    radius = lower_gap * total / (2 * HUNDRED)
    return {
        "displayed_absolute_error_gap_pp": exact_text(gap),
        "score_error_bound_per_endpoint_pp": exact_text(bound),
        "guaranteed_gap_lower_bound_pp": exact_text(lower_gap),
        "sufficient_open_ball_radius_ug_m3": exact_text(radius),
        "sufficient_open_ball_radius_percent_reference_total": exact_text(lower_gap / 2),
        "strictly_positive_certificate": radius > ZERO,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Empty or malformed CSV: {path.name}")
    return rows


def inventory_csvs(data_dir: Path) -> list[dict]:
    result = []
    for path in sorted(data_dir.glob("*.csv")):
        rows = read_csv(path)
        result.append({
            "file": path.name,
            "rows": len(rows),
            "columns": list(rows[0]),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return result


def build_report(data_dir: Path = DEFAULT_DATA) -> dict:
    landscape_rows = read_csv(data_dir / "jrc_12set_landscape.csv")
    reference = read_csv(data_dir / "jrc_campaign_point_reference.csv")
    edge_rows = read_csv(data_dir / "jrc_profile_choice_edges_reconstructed.csv")
    expected_sets = {f"W{w}-V{v}" for w in (3, 4, 5, 6) for v in (2, 3, 4)}
    if len(landscape_rows) != 12 or {r["profile_set"] for r in landscape_rows} != expected_sets:
        raise ValueError("Expected the original twelve profile sets")
    if tuple(r["reference_key"] for r in reference) != REFERENCE_KEYS:
        raise ValueError("Expected the eight declared reference categories in order")
    if len(edge_rows) != 30 or [r["edge_id"] for r in edge_rows] != [f"E{i:02d}" for i in range(1, 31)]:
        raise ValueError("Expected all thirty original comparison IDs in order")
    means = [finite_decimal(r["published_mean_ug_m3"]) for r in reference]
    if any(value < ZERO for value in means):
        raise ValueError("Published reference contributions must be nonnegative")
    total = sum(means, ZERO)
    if total != Decimal("43.09"):
        raise ValueError("Unexpected published reference normalization; inspect before reanalysis")
    landscape = {r["profile_set"]: r for r in landscape_rows}
    certificates = []
    for edge in edge_rows:
        a_id, b_id = edge["profile_a_id"], edge["profile_b_id"]
        a, b = landscape[a_id], landscape[b_id]
        ea, eb = a["EL1_percent_reference_mass"], b["EL1_percent_reference_mass"]
        if finite_decimal(ea) != finite_decimal(edge["reference_distance_a_EL1_percent"]):
            raise ValueError(f"Landscape/edge disagreement: {edge['edge_id']}")
        if finite_decimal(eb) != finite_decimal(edge["reference_distance_b_EL1_percent"]):
            raise ValueError(f"Landscape/edge disagreement: {edge['edge_id']}")
        chi_a, chi_b = finite_decimal(a["mean_reduced_chi2"]), finite_decimal(b["mean_reduced_chi2"])
        if chi_a == chi_b or finite_decimal(ea) == finite_decimal(eb):
            raise ValueError("Ties require explicit handling before certificates are interpreted")
        fit_favored = a_id if chi_a < chi_b else b_id
        ref_closer = a_id if finite_decimal(ea) < finite_decimal(eb) else b_id
        discordant = fit_favored != ref_closer
        if (edge["fit_favored_endpoint"] != fit_favored
                or edge["reference_closer_endpoint"] != ref_closer
                or edge["discordance"] != str(discordant)):
            raise ValueError(f"Reported labels do not match displayed scores: {edge['edge_id']}")
        certificates.append({
            "edge_id": edge["edge_id"],
            "profile_a": a_id,
            "profile_b": b_id,
            "reference_closer_at_displayed_target": ref_closer,
            "fit_favored_frozen": fit_favored,
            "discordant_at_displayed_target": discordant,
            "conservative_full_display_unit_envelope": radius_certificate(ea, eb, total, "0.01"),
            "conditional_nearest_rounding_envelope": radius_certificate(ea, eb, total, "0.005"),
        })
    discordant_edges = [r for r in certificates if r["discordant_at_displayed_target"]]
    if len(discordant_edges) != 9:
        raise ValueError("Original primary discordance count has changed; investigate")
    scenarios = []
    for percent in map(Decimal, ("0", "0.1", "0.5", "1", "2")):
        radius = total * percent / HUNDRED
        certified = [r for r in certificates if radius < finite_decimal(
            r["conservative_full_display_unit_envelope"]["sufficient_open_ball_radius_ug_m3"])]
        certified_discordant = sum(r["discordant_at_displayed_target"] for r in certified)
        certified_concordant = len(certified) - certified_discordant
        scenarios.append({
            "scenario_l1_radius_percent_of_original_reference_total": exact_text(percent),
            "scenario_l1_radius_ug_m3": exact_text(radius),
            "certified_unchanged_reference_orderings": len(certified),
            "guaranteed_discordances_at_least": certified_discordant,
            "guaranteed_discordances_at_most": 30 - certified_concordant,
            "unresolved_orderings": 30 - len(certified),
            "interpretation": "Declared sensitivity budget, not estimated reference uncertainty; count bounds need not be attainable jointly.",
        })
    global_best = min(landscape_rows, key=lambda r: finite_decimal(r["EL1_percent_reference_mass"]))
    global_radii = [radius_certificate(
        global_best["EL1_percent_reference_mass"], row["EL1_percent_reference_mass"], total
    ) for row in landscape_rows if row is not global_best]
    all_radius = min(finite_decimal(r["conservative_full_display_unit_envelope"]["sufficient_open_ball_radius_ug_m3"]) for r in certificates)
    return {
        "analysis": "Exploratory, conditional publication-derived L1 reference-ranking certificates",
        "decision": "KEEP conditional mathematical diagnostic; HOLD statistical reference-uncertainty claims",
        "baseline_modified": False,
        "recomputed_from_raw": False,
        "reference_total_ug_m3": exact_text(total),
        "reference_categories": list(REFERENCE_KEYS),
        "inputs": inventory_csvs(data_dir),
        "availability": {
            "eight_component_reference_mean": True,
            "eight_component_fitted_mean_vectors_in_inspected_public_archive": False,
            "daily_reference_vectors_in_inspected_public_archive": False,
            "joint_reference_covariance_in_inspected_public_archive": False,
            "evidence": "CSV header/row inventory and publication-derived REPRODUCIBILITY_LIMITS.md; manuscript Supplement S10 explicitly says full allocation vectors are not included.",
        },
        "assumptions": [
            "Published error summaries correctly describe fixed fitted allocations at the displayed campaign reference.",
            "Each underlying score lies within the declared reporting-precision envelope of its displayed score; the full-unit envelope is 0.01 percentage points per score.",
            "The original reference is the displayed eight-vector with total 43.09 ug/m3; possible reference-rounding displacement is part of the perturbation budget, not an extra independent confidence interval.",
            "Only the shared reference is perturbed; allocations, fit diagnostics, candidate universe, sample basis and selectors remain frozen.",
            "Every perturbed reference has positive total. A common positive changed denominator preserves ordering but changes normalized error magnitudes.",
        ],
        "mathematical_result": {
            "bound": "|[||a-r'||_1-||b-r'||_1]-[||a-r||_1-||b-r||_1]| <= 2||r'-r||_1",
            "certificate": "||r'-r||_1 < max(0, |e_a-e_b|-2b)*T0/200, where e_a,e_b,b are in percentage points",
            "boundary": "Strict inequality. Equality does not certify strict ordering. The certificate is sufficient, not an exact or necessary reversal threshold.",
        },
        "all_thirty_orderings_certificate": {
            "sufficient_open_ball_radius_ug_m3": exact_text(all_radius),
            "sufficient_open_ball_radius_percent_reference_total": exact_text(HUNDRED * all_radius / total),
            "consequence": "All thirty reference-ordering labels, hence the 9/30 discordance count, persist inside this open ball under the stated envelope assumptions.",
        },
        "global_minimum_certificate": {
            "profile_set": global_best["profile_set"],
            "sufficient_open_ball_radius_ug_m3": exact_text(min(finite_decimal(r["sufficient_open_ball_radius_ug_m3"]) for r in global_radii)),
            "scope": "Preservation against all eleven other fixed candidates; a sufficient lower bound only.",
        },
        "scenario_budgets": scenarios,
        "edge_certificates": certificates,
        "excluded_interpretations": [
            "No sampling confidence interval, p-value, probability of correctness or posterior is estimated.",
            "The 20% synthetic-noise statement is not treated as uncertainty or a standard error of the campaign mean.",
            "Failure to certify an ordering does not show it reverses, is wrong or is statistically insignificant.",
            "No source covariance, day-level reference, fitted allocation vector or missing source profile is imputed.",
            "No raw-data reproduction or external field-accuracy validation has been achieved by this diagnostic.",
        ],
        "software": {"python": platform.python_version(), "dependencies": "standard library only", "randomness": "none", "arithmetic": "Decimal from original CSV text"},
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Conditional reference-ranking robustness diagnostic",
        "",
        "Exploratory audit, 26 September 2026. No manuscript or baseline change.",
        "",
        "## Evidence available",
        "",
        "The inspected public archive supplies twelve scalar campaign-level error scores, an eight-component reference vector, and thirty reconstructed comparison rows. It does not supply the twelve fitted eight-component mean vectors, daily reference series, or a joint reference covariance. Consequently, a direct perturbed-reference reanalysis or statistical uncertainty propagation is not currently possible.",
        "",
        "This diagnostic uses a consequence of the triangle inequality to give sufficient reference-perturbation budgets. It does not recreate the missing vectors.",
        "",
        "## Mathematical guarantee",
        "",
        "For fixed fitted allocations a and b and reference r, define D(r) = ||a-r||_1 - ||b-r||_1. Each L1 distance changes by at most ||r'-r||_1, hence |D(r')-D(r)| <= 2||r'-r||_1. A nonzero distance ordering therefore persists whenever ||r'-r||_1 < |D(r)|/2.",
        "",
        "The published error scores e_a and e_b are percentages normalized by T0 = 43.09 ug/m3. Allowing an absolute reporting error of b percentage points for each score gives the conservative sufficient open-ball radius:",
        "",
        "`radius = max(0, abs(e_a - e_b) - 2*b) * 43.09 / 200`.",
        "",
        "The default b = 0.01 pp allows one full displayed unit per score, avoiding an undocumented assumption about rounding-to-nearest. A secondary b = 0.005 pp calculation is included in JSON and applies only if nearest rounding is justified. Neither envelope covers mistakes in the original computations. The displayed reference defines the center; reference rounding or other reference error consumes the same total L1 displacement budget.",
        "",
        "The denominator at the perturbed reference may change. As long as it is shared by both candidates and positive, it does not change their ordering. The bound concerns ordering, not constancy of normalized regret.",
        "",
        "## Results from the conservative full-unit envelope",
        "",
        f"All thirty reference-ordering labels, and thus the 9/30 primary discordance count, are certified unchanged for total L1 reference displacement strictly below **{report['all_thirty_orderings_certificate']['sufficient_open_ball_radius_ug_m3']} ug/m3** ({report['all_thirty_orderings_certificate']['sufficient_open_ball_radius_percent_reference_total']}% of the original total). This small sufficient radius does not establish that a reversal occurs outside it.",
        "",
        f"W4-V2 remains the global minimum-error candidate for displacement strictly below **{report['global_minimum_certificate']['sufficient_open_ball_radius_ug_m3']} ug/m3** under the same assumptions.",
        "",
        "| Discordant comparison | Fit-favored | Reference-closer | Displayed error gap (pp) | Sufficient open-ball radius (ug/m3) |",
        "|---|---|---|---:|---:|",
    ]
    for edge in report["edge_certificates"]:
        if edge["discordant_at_displayed_target"]:
            cert = edge["conservative_full_display_unit_envelope"]
            lines.append(f"| {edge['edge_id']} | {edge['fit_favored_frozen']} | {edge['reference_closer_at_displayed_target']} | {cert['displayed_absolute_error_gap_pp']} | {cert['sufficient_open_ball_radius_ug_m3']} |")
    lines += [
        "",
        "### Declared perturbation-budget scenarios",
        "",
        "These budgets are illustrative sensitivity settings, not estimates of actual reference uncertainty or confidence levels. Bounds apply to any reference within the stated closed budget ball; unresolved edge outcomes need not be attainable together because comparisons share the same reference. Falling outside a certificate only means this inequality is inconclusive.",
        "",
        "| Budget (% of original total) | Budget (ug/m3) | Certified unchanged orderings / 30 | Guaranteed discordance-count bounds |",
        "|---:|---:|---:|---:|",
    ]
    for scenario in report["scenario_budgets"]:
        lines.append(f"| {scenario['scenario_l1_radius_percent_of_original_reference_total']} | {scenario['scenario_l1_radius_ug_m3']} | {scenario['certified_unchanged_reference_orderings']} | {scenario['guaranteed_discordances_at_least']} to {scenario['guaranteed_discordances_at_most']} |")
    lines += [
        "",
        "## Decision and limitations",
        "",
        "- KEEP this conditional mathematical diagnostic and exact per-edge certificates as a separately labeled audit result.",
        "- HOLD any claim that 9/30 is robust to the actual JRC reference uncertainty: its admissible joint region is unavailable, and the sufficient radii do not recover it.",
        "- HOLD exact reversal thresholds until the fixed fitted allocation vectors are recovered. Even those vectors would not alone identify a statistical uncertainty distribution.",
        "- REMOVE any inference that 20% synthetic construction noise is a standard error or confidence interval for the campaign mean. This audit makes no such conversion.",
        "",
        "The fit selector and fitted allocations are frozen. The comparison universe is unchanged. No Monte Carlo draws, covariance, negative/positive dependence assumptions, missing profiles, daily values, or allocation components have been invented. No original CMB fits were rerun. These results do not validate a field profile or alter the accepted baseline.",
        "",
        "## Reproduction and provenance",
        "",
        "Run from the repository root:",
        "",
        "```text",
        "python scripts/audit_reference_robustness.py",
        "python -m unittest discover -s tests -p test_reference_robustness.py -v",
        "```",
        "",
        "The adjacent JSON records all inspected CSV headers, row counts, SHA-256 hashes, exact decimal values, both reporting-precision envelopes, and software version. It is generated without network access or third-party Python dependencies. Inputs are read-only from the frozen public archive; reports are separate exploratory outputs.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: dict, destination: Path, data_dir: Path = DEFAULT_DATA) -> None:
    """Never place audit output in the frozen archive or input directory tree."""
    source_root = data_dir.parent if data_dir.name == "derived_data" else data_dir
    protected_roots = {DEFAULT_DATA.parent.parent.resolve(), source_root.resolve()}
    targets = [destination.resolve()] + [
        (destination / name).resolve()
        for name in ("reference_robustness.json", "REFERENCE_ROBUSTNESS.md")
    ]
    if any(target.is_relative_to(root) for target in targets for root in protected_roots):
        raise ValueError("Audit output cannot be within the frozen archive or input tree")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "reference_robustness.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (destination / "REFERENCE_ROBUSTNESS.md").write_text(markdown_report(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = build_report(args.data_dir)
    write_outputs(report, args.output_dir, args.data_dir)
    print(json.dumps({"all_thirty_orderings_certificate": report["all_thirty_orderings_certificate"], "global_minimum_certificate": report["global_minimum_certificate"], "scenario_budgets": report["scenario_budgets"]}, indent=2))


if __name__ == "__main__":
    main()
