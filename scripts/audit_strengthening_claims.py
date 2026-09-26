#!/usr/bin/env python3
"""Audit publication-derived claim arithmetic without pretending to rerun CMB.

Standard-library only; deterministic outputs; no network or manuscript writes.
Rounding intervals concern displayed precision, NOT measurement/reference error.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path("outputs/publication_archive_20260926/publication_derived")
OUTPUT = Path("outputs/strengthening_20260926")
WOODS = ("W3", "W4", "W5", "W6")
VEHICLES = ("V2", "V3", "V4")
ERROR = "EL1_percent_reference_mass"
CHI = "mean_reduced_chi2"
R2 = "median_R2"
MANIFEST_SHA256 = "b2e466157104c77da7c8d5346a5f62d4926f00b50532200ad37473ddb3cd63c4"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def number(text: str) -> Decimal:
    value = Decimal(text)
    if not value.is_finite():
        raise ValueError("non-finite input")
    return value


def decimal_text(value: Decimal) -> str:
    return format(value, "f")


def rounding_interval(text: str) -> tuple[Decimal, Decimal]:
    """Conservative closed half-last-place bounds under nearest rounding."""
    value = number(text)
    half_quantum = Decimal(1).scaleb(value.as_tuple().exponent) / 2
    return value - half_quantum, value + half_quantum


def separated_margin(first: str, second: str) -> Decimal:
    """Positive iff order is strict even with conservative rounding endpoints."""
    low, high = sorted((first, second), key=number)
    return rounding_interval(high)[0] - rounding_interval(low)[1]


def manifest_audit(archive: Path) -> dict:
    manifest = archive / "SHA256SUMS.txt"
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != MANIFEST_SHA256:
        raise ValueError("frozen manifest identity changed")
    entries = []
    seen = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split("  ", 1)
        target = (archive / name).resolve()
        if name in seen or not target.is_relative_to(archive.resolve()):
            raise ValueError("duplicate or out-of-scope manifest entry")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"manifest mismatch: {name}")
        seen.add(name)
        entries.append({"path": name, "sha256": actual})
    if len(entries) != 20:
        raise ValueError("expected 20 frozen publication-derived manifest entries")
    return {
        "status": "PASS", "verified_entries": len(entries),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "entries": entries,
        "meaning": "Byte integrity only; hashes do not authenticate scientific truth.",
    }


def graph_edges() -> list[tuple[str, str, str, str]]:
    pairs = []
    for vehicle in VEHICLES:
        pairs.extend(("Wood", f"{a}-{vehicle}", f"{b}-{vehicle}")
                     for a, b in itertools.combinations(WOODS, 2))
    for wood in WOODS:
        pairs.extend(("Vehicle", f"{wood}-{a}", f"{wood}-{b}")
                     for a, b in itertools.combinations(VEHICLES, 2))
    return [(f"E{i:02d}", *row) for i, row in enumerate(pairs, 1)]


def validate_landscape(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    lookup = {row["profile_set"]: row for row in rows}
    expected = {f"{w}-{v}" for w in WOODS for v in VEHICLES}
    if len(rows) != 12 or set(lookup) != expected:
        raise ValueError("expected unique complete 4-by-3 profile grid")
    for row in rows:
        for column, places in ((ERROR, 2), (CHI, 4), (R2, 4)):
            value = number(row[column])
            if value.as_tuple().exponent != -places:
                raise ValueError(f"unexpected displayed precision in {column}")
            if value < 0 or (column == R2 and value > 1):
                raise ValueError(f"out-of-range value in {column}")
    return lookup


def reconstruct_jrc(rows: list[dict[str, str]]) -> dict:
    lookup = validate_landscape(rows)
    output = []
    for edge_id, family, a, b in graph_edges():
        ca, cb = number(lookup[a][CHI]), number(lookup[b][CHI])
        ea, eb = number(lookup[a][ERROR]), number(lookup[b][ERROR])
        fit = a if ca < cb else b if cb < ca else None
        reference = a if ea < eb else b if eb < ea else None
        if fit is None or reference is None:
            raise ValueError("primary comparison is tied; do not choose a winner")
        chi_margin = separated_margin(lookup[a][CHI], lookup[b][CHI])
        error_margin = separated_margin(lookup[a][ERROR], lookup[b][ERROR])
        regret = number(lookup[fit][ERROR]) - min(ea, eb)
        output.append({
            "edge_id": edge_id, "source_family": family,
            "profile_a_id": a, "profile_b_id": b,
            "fit_favored_endpoint": fit, "reference_closer_endpoint": reference,
            "discordance": fit != reference,
            "regret_pp_displayed": decimal_text(regret),
            "chi_gap_displayed": decimal_text(abs(ca - cb)),
            "chi_order_margin_after_rounding": decimal_text(chi_margin),
            "error_order_margin_pp_after_rounding": decimal_text(error_margin),
            "rounding_robust": chi_margin > 0 and error_margin > 0,
        })
    discordant = [row for row in output if row["discordance"]]
    regret = [number(row["regret_pp_displayed"]) for row in discordant]
    return {
        "profile_count": len(lookup), "comparisons": len(output),
        "discordances": len(discordant),
        "discordant_edge_ids": [row["edge_id"] for row in discordant],
        "by_family": {family: {
            "comparisons": sum(row["source_family"] == family for row in output),
            "discordances": sum(row["source_family"] == family and row["discordance"]
                                for row in output),
        } for family in ("Wood", "Vehicle")},
        "node_degrees": {name: sum(name in (row["profile_a_id"], row["profile_b_id"])
                                  for row in output) for name in sorted(lookup)},
        "median_discordant_regret_pp_displayed": decimal_text(median(regret)),
        "maximum_discordant_regret_pp_displayed": decimal_text(max(regret)),
        "rounding_robust_comparisons": sum(row["rounding_robust"] for row in output),
        "minimum_chi_rounding_margin": decimal_text(min(
            number(row["chi_order_margin_after_rounding"]) for row in output)),
        "minimum_error_rounding_margin_pp": decimal_text(min(
            number(row["error_order_margin_pp_after_rounding"]) for row in output)),
        "rounding_assumption": "Each displayed error is nearest-rounded to 0.01 pp and each mean reduced chi-square to 0.0001. Conservative closed half-last-place intervals are used. This is NOT reference/measurement uncertainty or a raw-fit validation.",
        "recomputed_from_raw": False,
        "evidence_level": "Reconstructed from publication-displayed set summaries.",
        "edges": output,
    }


def compare_frozen_ledger(rebuilt: dict, original: list[dict[str, str]]) -> None:
    if len(original) != 30 or len({row["edge_id"] for row in original}) != 30:
        raise ValueError("frozen edge ledger must have 30 unique IDs")
    lookup = {row["edge_id"]: row for row in original}
    for row in rebuilt["edges"]:
        old = lookup[row["edge_id"]]
        for key in ("source_family", "profile_a_id", "profile_b_id",
                    "fit_favored_endpoint", "reference_closer_endpoint"):
            if row[key] != old[key]:
                raise ValueError(f"frozen edge ledger mismatch: {row['edge_id']} {key}")
        if str(row["discordance"]) != old["discordance"]:
            raise ValueError("frozen discordance mismatch")
        if abs(number(old["selection_regret_pp_from_published_values"])
               - number(row["regret_pp_displayed"])) > Decimal("1e-12"):
            raise ValueError("frozen regret mismatch")


def ranks(values: list) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        for index in order[start:end]:
            result[index] = (start + 1 + end) / 2
        start = end
    return result


def correlation(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("rank arrays must have equal positive length")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    numerator = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    denominator = math.sqrt(sum((x - ma) ** 2 for x in a)
                            * sum((y - mb) ** 2 for y in b))
    if denominator == 0:
        raise ValueError("correlation is undefined for constant ranks")
    return numerator / denominator


def ordered_partitions(indices: tuple[int, ...]) -> list[tuple[tuple[int, ...], ...]]:
    """All weak orderings (including exact residual ties), each exactly once."""
    if not indices or len(indices) > 6:
        raise ValueError("weak-order enumeration requires 1 to 6 tied items")
    output = []
    for labels in itertools.product(range(len(indices)), repeat=len(indices)):
        if set(labels) != set(range(max(labels) + 1)):
            continue
        output.append(tuple(tuple(index for index, label in zip(indices, labels)
                                  if label == level) for level in range(max(labels) + 1)))
    return output


def r2_rounding_audit(rows: list[dict[str, str]]) -> dict:
    validate_landscape(rows)
    errors = ranks([number(row[ERROR]) for row in rows])
    values = [number(row[R2]) for row in rows]
    groups = [tuple(i for i, value in enumerate(values) if value == distinct)
              for distinct in sorted(set(values), reverse=True)]
    candidates = []
    choices = [ordered_partitions(group) for group in groups]
    if math.prod(len(choice) for choice in choices) > 100000:
        raise ValueError("too many rank refinements for exhaustive audit")
    for chosen in itertools.product(*choices):
        partition = list(itertools.chain.from_iterable(chosen))
        candidate_ranks = [0.0] * len(rows)
        start = 1
        for block in partition:
            for i in block:
                candidate_ranks[i] = start + (len(block) - 1) / 2
            start += len(block)
        rho = correlation(errors, candidate_ranks)
        candidates.append({
            "rho": round(rho, 12),
            "strict_order": all(len(block) == 1 for block in partition),
            "rounds_to_reported_0_909": Decimal("0.9085") <= Decimal(str(rho)) < Decimal("0.9095"),
            "ascending_one_minus_R2_rank_blocks": [[rows[i]["profile_set"] for i in block]
                                                     for block in partition],
        })
    strict = [item for item in candidates if item["strict_order"]]
    matching = [item for item in candidates if item["rounds_to_reported_0_909"]]
    return {
        "displayed_midrank_rho": round(correlation(errors, ranks([-value for value in values])), 12),
        "displayed_tie_groups": [[rows[i]["profile_set"] for i in group]
                                 for group in groups if len(group) > 1],
        "all_weak_refinements": len(candidates), "strict_refinements": len(strict),
        "possible_rho_range": [min(item["rho"] for item in candidates),
                               max(item["rho"] for item in candidates)],
        "strict_rho_range": [min(item["rho"] for item in strict),
                             max(item["rho"] for item in strict)],
        "refinements_rounding_to_reported": len(matching),
        "strict_refinements_rounding_to_reported": sum(item["strict_order"] for item in matching),
        "reported_value_compatible_with_rounding": bool(matching),
        "reported_value_independently_verified": False,
        "interpretation": "Possible rank configurations, NOT recovered latent values or probabilities. Within each displayed R-squared tie, enumerate every weak order; distinct displayed values retain their order under consistent nearest rounding. The actual unrounded order and correlation remain unavailable.",
        "refinements": candidates,
    }


def integer(text: str) -> int:
    value = number(text)
    if value != value.to_integral_value() or value < 0:
        raise ValueError("count must be a nonnegative integer")
    return int(value)


def epa_audit(outcomes: list[dict[str, str]], attrition: list[dict[str, str]]) -> dict:
    expected_names = (
        "Eligible substitutions", "Converged substitutions",
        "Central + alternative R2 and reduced-chi2 in range",
        "Central + alternative R2, reduced-chi2, and percent mass in range",
        "Nonconverged",
    )
    lookup = {row["subset"]: row for row in outcomes}
    if len(outcomes) != 5 or set(lookup) != set(expected_names):
        raise ValueError("unexpected EPA subset labels")
    counts = {name: integer(lookup[name]["n"]) for name in expected_names}
    eligible, converged, fit, strict, nonconverged = [counts[name] for name in expected_names]
    if not eligible == converged + nonconverged or not eligible >= converged >= fit >= strict:
        raise ValueError("EPA nesting/attrition arithmetic inconsistent")
    if not attrition or len({(r["central"], r["alternative"]) for r in attrition}) != len(attrition):
        raise ValueError("missing or duplicated EPA alternative")
    for row in attrition:
        if integer(row["eligible"]) != integer(row["converged"]) + integer(row["nonconverged"]):
            raise ValueError("EPA per-alternative attrition inconsistent")
    for field, expected in (("eligible", eligible), ("converged", converged),
                            ("nonconverged", nonconverged)):
        if sum(integer(row[field]) for row in attrition) != expected:
            raise ValueError("EPA aggregate attrition inconsistent")
    nested = []
    for name in expected_names[1:4]:
        row = lookup[name]
        n = counts[name]
        ordering, largest = integer(row["any_ordering_change"]), integer(row["largest_source_change"])
        if not 0 <= largest <= ordering <= n:
            raise ValueError("EPA event counts inconsistent")
        nested.append({"subset": name, "n": n, "ordering_changes": ordering,
                       "largest_source_changes": largest})
    differences = []
    for outer, inner in zip(nested, nested[1:]):
        difference = {key: outer[key] - inner[key]
                      for key in ("n", "ordering_changes", "largest_source_changes")}
        if not 0 <= difference["largest_source_changes"] <= difference["ordering_changes"] <= difference["n"]:
            raise ValueError("EPA nested-complement counts inconsistent")
        differences.append({"stratum": f"{outer['subset']} minus {inner['subset']}", **difference})
    return {
        "arithmetic_status": "PASS", "eligible": eligible, "converged": converged,
        "nonconverged": nonconverged, "alternative_count": len(attrition),
        "reported_nested_subsets": nested, "conditional_complement_arithmetic": differences,
        "two_diagnostic_ordering_percent": round(100 * nested[1]["ordering_changes"] / fit, 1),
        "two_diagnostic_largest_percent": round(100 * nested[1]["largest_source_changes"] / fit, 1),
        "conditional_assumptions": "Use the publication's asserted nested subsets and consistent source ordering with no top-source tie. Complement counts are arithmetic consequences, not recovered or invented row-level assignments.",
        "row_level_event_labels_recomputed": False, "recomputed_from_raw": False,
        "missing_for_independent_recomputation": [
            "Per-sample and per-alternative canonical IDs plus frozen model inputs/settings.",
            "Unrounded central and alternative full-source contribution vectors.",
            "Convergence labels and diagnostics defining each subset.",
            "Deterministic tie handling and pairwise ordering/top-source event ledger.",
        ],
    }


def audit(archive: Path) -> dict:
    integrity = manifest_audit(archive)
    data = archive / "derived_data"
    landscape = read_csv(data / "jrc_12set_landscape.csv")
    jrc = reconstruct_jrc(landscape)
    compare_frozen_ledger(jrc, read_csv(data / "jrc_profile_choice_edges_reconstructed.csv"))
    jrc["matches_frozen_reconstructed_ledger"] = True
    return {
        "audit_version": "1.0.0", "audit_date": "2026-09-26",
        "scope": "Candidate strengthening audit; no baseline/manuscript/published-archive edits.",
        "evidence_scope_note": "The false raw-reconstruction flags and missing-input lists below refer only to the frozen publication-derived archive assessed by THIS script. A later separate native-input clean-room reconstruction is documented in EPA_NATIVE_RECONSTRUCTION.md and epa_native_reconstruction.json; consult that report for the updated EPA reconstruction status.",
        "source_relative_path": ARCHIVE.as_posix(),
        "environment": {"python": platform.python_version(), "dependencies": "standard library only",
                        "randomness": "none; exhaustive deterministic enumeration"},
        "integrity": integrity, "jrc_primary": jrc,
        "jrc_R2_precision": r2_rounding_audit(landscape),
        "epa_aggregates": epa_audit(read_csv(data / "epa_primary_outcome_summary.csv"),
                                    read_csv(data / "epa_profile_alternatives_and_attrition.csv")),
        "decisions": {
            "KEEP": ["JRC 9/30 as a publication-summary reconstruction, robust to displayed rounding under the stated assumption.",
                     "EPA 133/283 and 62/283 as reported aggregate sensitivity counts whose arithmetic is internally consistent."],
            "HOLD": ["Independent source-native verification cannot be supplied by this publication-derived archive alone; see the separate EPA native reconstruction for later evidence.",
                     "Exact unrounded rho=0.909: compatible with rounding but not independently verified.",
                     "EPA row-level ordering/top-source classifications and true sample nesting cannot be checked by these aggregate tables alone; see the separate EPA native reconstruction."],
            "REMOVE": ["Any claim that summary arithmetic checks constitute a full raw-data rerun or field-accuracy validation.",
                       "Any inference that displayed rho=0.927726 proves the reported 0.909 is erroneous."],
        },
    }


def render_report(report: dict) -> str:
    jrc, r2, epa = report["jrc_primary"], report["jrc_R2_precision"], report["epa_aggregates"]
    edge_rows = "\n".join(
        f"| {r['edge_id']} | {r['profile_a_id']} / {r['profile_b_id']} | {r['fit_favored_endpoint']} | {r['reference_closer_endpoint']} | {r['regret_pp_displayed']} |"
        for r in jrc["edges"] if r["discordance"])
    return f"""# Independent publication-derived claim audit — 26 September 2026

## Scope and result

This new audit leaves the active manuscript baseline and published archive unchanged.
It does not rerun CMB, reconstruct missing model outputs, or validate environmental accuracy.
The original public package's {report['integrity']['verified_entries']} manifest entries match their hashes.
The full machine-readable result, input hashes, edge decisions and all rank refinements
are in `claims_audit.json`.

**Scope update:** This report assesses only the frozen publication-derived archive.
The later, separately executed native-input EPA clean-room reconstruction is in
`EPA_NATIVE_RECONSTRUCTION.md` and `epa_native_reconstruction.json`. That independent
work reproduces the EPA worked case and headline aggregates from recovered native
inputs. The false raw-reconstruction flags and gaps below are local to this
publication-summary audit, not a claim that the new combined work still lacks an
EPA numerical reconstruction. The original historical executable ledger remains
distinct from a new clean-room calculation.

## JRC primary result: KEEP with explicit provenance

Reconstructing the complete 4-by-3 grid independently gives {jrc['comparisons']} one-profile
comparisons: 18 wood-profile and 12 vehicle-profile comparisons, with five neighbors
per profile set. The reported 9/30 lower-mean-chi-square discordances are reproduced;
all nine occur within wood-profile comparisons. Every reconstructed endpoint agrees
with the frozen publication-derived ledger. This does NOT recover the original
unrounded CMB ledger or validate the source-native fits.

| Edge | Compared sets | Fit-favored | Reference-closer | Displayed regret (pp) |
|---|---|---|---|---|
{edge_rows}

Discordant median regret is {jrc['median_discordant_regret_pp_displayed']} pp and maximum
regret is {jrc['maximum_discordant_regret_pp_displayed']} pp, calculated from displayed values.

### New displayed-precision robustness check

Assume each displayed mean chi-square was rounded to the nearest 0.0001 and each
displayed error to the nearest 0.01 pp. Give every value its conservative closed
half-last-place interval. All {jrc['rounding_robust_comparisons']}/30 comparison classifications
remain unchanged throughout those intervals: even the smallest residual chi-square
separation is {jrc['minimum_chi_rounding_margin']}, and the smallest residual error separation
is {jrc['minimum_error_rounding_margin_pp']} pp. This is an interval proof, not a Monte Carlo sample.

Thus ordinary display rounding cannot explain away the reconstructed 9/30 result.
This check concerns numerical display precision only. It is not uncertainty
propagation for the external reference, receptor measurements or source profiles.
The 30 comparisons share profile sets and are not independent random trials;
no binomial confidence interval or population p-value is added.

## Secondary R-squared correlation: compatible, not verified

Using exact ties in displayed R-squared values gives Spearman rho
{r2['displayed_midrank_rho']:.12f}, rather than the manuscript's 0.909. Exhaustively
refining only the two displayed tie groups (sizes 3 and 2) gives
{r2['all_weak_refinements']} weak rank orderings, including {r2['strict_refinements']} fully
strict orderings. Their possible rho range is {r2['possible_rho_range'][0]:.12f}
to {r2['possible_rho_range'][1]:.12f};
{r2['refinements_rounding_to_reported']} weak orderings, of which
{r2['strict_refinements_rounding_to_reported']} are strict, round to 0.909.

The reported value is therefore **compatible with unrounded ranks**. This is not a
recovery of the actual ordering: possibilities have no probabilities, and no latent
R-squared values are imputed. HOLD exact verification pending the original outputs.
Do not silently replace 0.909 by the rounded-table correlation or call it a proven error.

## EPA aggregate counts: KEEP as reported; HOLD row-level verification

The ten alternative-level attrition rows sum to 345 eligible substitutions,
323 converged and 22 nonconverged. The reported converged / two-diagnostic /
three-diagnostic subsets have respectively 323 / 283 / 26 rows, ordering-change
counts 167 / 133 / 10 and largest-source-change counts 81 / 62 / 2.
The displayed percentages 47.0% and 21.9% follow from 133/283 and 62/283.

Conditional on the stated nesting and consistent strict ranking, the complementary
strata contain 40 / 257 rows, with 34 / 123 ordering changes and 19 / 60 largest-source
changes. All count inequalities are consistent. These are arithmetic consequences
of aggregate assertions, not recovered row identities or a verification of actual nesting.

The archived worked Fresno example does not supply complete contribution vectors
for every source or the full substitution ledger. Therefore neither it nor the
aggregate CSVs can independently regenerate 133 or 62 event classifications.
Raw rerun and row-level event checks remain explicitly false in the JSON audit.

## What would close the remaining gaps

1. JRC: original receptor/profile inputs, exact settings, unrounded contributions and
   diagnostics for all 12 profile sets; the canonical 30-comparison ledger and
   reference mapping. A precision audit is not a replacement.
2. EPA: exact sample/alternative IDs; full unrounded central and alternative source
   vectors; convergence/diagnostic masks; source-label and tie-handling rules;
   then regenerate all 345 / 323 / 283 / 26 masks and 133 / 62 event labels.
3. Keep field sensitivity separate from external accuracy. Do not add a claim of
   full reproducibility or external validation based on this audit.

## Reproduce

From the repository root, using Python 3 (standard library only):

```text
python scripts/audit_strengthening_claims.py
python -m unittest discover -s tests -p test_strengthening_claims.py -v
```

Outputs are deterministic for a fixed Python version and input archive. The script
fails closed on missing/corrupt inputs and cannot write within the frozen archive.
No manuscript, published archive, baseline or scientific count was changed.
"""


def write_outputs(report: dict, destination: Path, archive: Path) -> None:
    if destination.resolve().is_relative_to(archive.resolve()):
        raise ValueError("audit output cannot be within the frozen archive")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "claims_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (destination / "CLAIM_AUDIT.md").write_text(render_report(report), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / ARCHIVE)
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    args = parser.parse_args()
    report = audit(args.archive)
    write_outputs(report, args.output, args.archive)
    print("PASS: 9/30 publication-derived JRC comparisons reconstructed; 30/30 rounding-robust.")
    print("PASS: EPA aggregate arithmetic consistent in this publication-only audit; see the separate EPA_NATIVE_RECONSTRUCTION.md for native row-level reconstruction.")
    print("R2 rho=0.909 is rounding-compatible, NOT independently verified.")


if __name__ == "__main__":
    main()
