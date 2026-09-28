"""Retrospective fixed-grid arithmetic only; no native model fits or inference."""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import platform
from statistics import median
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = ROOT / "outputs/journal_editorial_20260926/publication_derived/derived_data"
PINS = {
    "jrc_12set_landscape.csv": "b1f0081b9e8943b1e13a09a9ece7c79aca373bff4b4f2e702eb65a1689333356",
    "jrc_profile_choice_edges_reconstructed.csv": "9695d1d70ae7f48bc14ee7e51dcd49c99ee82f13ffb7f7529072b18107adca36",
}


def load(name):
    payload = (INPUT / name).read_bytes()
    if hashlib.sha256(payload).hexdigest() != PINS[name]:
        raise ValueError(f"Input identity changed: {name}")
    return list(csv.DictReader(payload.decode("utf-8-sig").splitlines()))


def summaries(edges):
    positive = [e["signed_EL1_delta_pp"] for e in edges if e["signed_EL1_delta_pp"] > 0]
    signed = [e["signed_EL1_delta_pp"] for e in edges]
    gaps = [e["chi2_gap"] for e in edges]
    return {
        "n": len(edges), "discordant": len(positive),
        "concordant": sum(x < 0 for x in signed), "reference_ties": sum(x == 0 for x in signed),
        "signed_delta_pp_min_median_max": [min(signed), median(signed), max(signed)],
        "chi2_gap_min_median_max": [min(gaps), median(gaps), max(gaps)],
        "discordant_delta_pp_median_max": [median(positive), max(positive)] if positive else None,
        "edge_ids": [e["edge_id"] for e in edges],
    }


def analyse():
    rows = load("jrc_12set_landscape.csv")
    cached = load("jrc_profile_choice_edges_reconstructed.csv")
    expected_ids = {f"W{w}-V{v}" for w in range(3, 7) for v in range(2, 5)}
    if len(rows) != 12 or {r["profile_set"] for r in rows} != expected_ids:
        raise ValueError("Incomplete or duplicate landscape")
    by_id = {r["profile_set"]: r for r in rows}
    pairs = [("Wood", f"V{v}", f"W{a}-V{v}", f"W{b}-V{v}")
             for v in range(2, 5) for a, b in itertools.combinations(range(3, 7), 2)]
    pairs += [("Vehicle", f"W{w}", f"W{w}-V{a}", f"W{w}-V{b}")
              for w in range(3, 7) for a, b in itertools.combinations(range(2, 5), 2)]
    if len(cached) != 30 or len({r["edge_id"] for r in cached}) != 30:
        raise ValueError("Incomplete or duplicate cached edges")
    cached_by_id = {r["edge_id"]: r for r in cached}
    result = []
    for index, (family, fixed, aid, bid) in enumerate(pairs, 1):
        eid = f"E{index:02d}"
        a, b = by_id[aid], by_id[bid]
        ca, cb = Decimal(a["mean_reduced_chi2"]), Decimal(b["mean_reduced_chi2"])
        if ca == cb:
            raise ValueError("Unexpected selector tie; no arbitrary tie break")
        ea, eb = Decimal(a["EL1_percent_reference_mass"]), Decimal(b["EL1_percent_reference_mass"])
        fit, delta = (aid, ea-eb) if ca < cb else (bid, eb-ea)
        reference = aid if ea < eb else bid if eb < ea else None
        old = cached_by_id[eid]
        if (old["profile_a_id"], old["profile_b_id"], old["source_family"], old["fit_favored_endpoint"], old["reference_closer_endpoint"], old["discordance"]) != (aid, bid, family, fit, reference, str(delta > 0)):
            raise ValueError(f"Existing comparison identity/direction mismatch: {eid}")
        if abs(Decimal(old["selection_regret_pp_from_published_values"]) - max(Decimal(0), delta)) > Decimal("1e-12"):
            raise ValueError(f"Cached regret mismatch: {eid}")
        result.append({"edge_id": eid, "family": family, "fixed": fixed,
                       "a": aid, "b": bid, "fit_favored": fit, "reference_closer": reference,
                       "signed_EL1_delta_pp": delta, "chi2_gap": abs(ca-cb)})
    groups = {family: summaries([e for e in result if e["family"] == family])
              for family in ("Wood", "Vehicle")}
    strata = {f"{family}; fixed {fixed}": summaries([e for e in result if e["family"] == family and e["fixed"] == fixed])
              for family, values in (("Wood", ["V2", "V3", "V4"]), ("Vehicle", ["W3", "W4", "W5", "W6"]))
              for fixed in values}
    return {"input_sha256": PINS, "mode": "exploratory publication-summary postprocessing",
            "source_native_reproduction": False, "native_fits": 0, "random_draws": 0,
            "signed_delta_definition": "EL1(lower-chi2 endpoint) minus EL1(other endpoint), percentage points",
            "limitations": ["Displayed summary values, not original full-precision vectors",
                            "Dependent finite comparisons; no population probability or p-value",
                            "Family association does not identify chemical or weighting mechanism",
                            "Point-reference distance is not established environmental accuracy"],
            "all": summaries(result), "families": groups, "strata": strata, "edges": result}


def main():
    outputs = [HERE / "JRC_FAMILY_RESULT.json", HERE / "JRC_FAMILY_RESULT.md"]
    if any(p.exists() for p in outputs):
        raise FileExistsError("Preserve prior output; this calculation was already saved")
    started = time.perf_counter()
    value = analyse()
    value["python"] = platform.python_version()
    value["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    value["active_postprocessing_seconds"] = time.perf_counter() - started
    text = ["# JRC source-family structure", "", "Exploratory post-review calculation from the unchanged published tables; no original model fits were rerun.", "",
            "Positive signed delta means the lower-chi-square profile has greater distance from the campaign-level point reference. Units are percentage points of the original reference total.", "",
            "| Substituted family / fixed profile | Comparisons | Discordant | Signed delta: min / median / max (pp) |", "|---|---:|---:|---:|"]
    for name, record in list(value["families"].items()) + list(value["strata"].items()):
        numbers = " / ".join(str(x) for x in record["signed_delta_pp_min_median_max"])
        text.append(f"| {name} | {record['n']} | {record['discordant']} | {numbers} |")
    text += ["", "## Interpretation", "", "This identifies where the already reported discrepancies occur. It does not establish their chemical cause, eliminate reference uncertainty, recover JRC native outputs, or generalize to other source families or campaigns.", "", "The existing conditional reference-radius audit is not repeated here. Its sufficient bounds must not be interpreted as measured reference uncertainty or exact reversal thresholds.", "", "Provenance, complete comparisons, consistency checks against all 30 existing edge records, and execution time are in the adjacent JSON."]
    with outputs[0].open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, default=str, allow_nan=False)
        f.write("\n")
    with outputs[1].open("x", encoding="utf-8") as f:
        f.write("\n".join(text) + "\n")
    print(json.dumps({"families": value["families"], "active_seconds": value["active_postprocessing_seconds"]}, default=str))


if __name__ == "__main__":
    main()
