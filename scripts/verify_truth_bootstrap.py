"""Independent saved-mask cluster-bootstrap replay. No model fit or producer import."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import platform

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
RESULT_HASH = "e4bf45de87335c853edc15170e3a8706a1540797069766fed552fe5ead49362b"
CONFIG_HASH = "8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9"
ROUNDING_ATOL = 4e-15  # Declared before replay; alternative type-7 interpolation order.
METRICS = ("singleton_coverage", "wrong_singleton_risk", "truth_in_set_coverage")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def checked(path, expected):
    payload = Path(path).read_bytes()
    require(digest(payload) == expected, "Pinned input hash mismatch: " + Path(path).name)
    return payload


def cluster_counts(predicted, truth, groups):
    """Integer counts via row iteration, independent of the producer's metric helper."""
    predicted, truth, groups = map(np.asarray, (predicted, truth, groups))
    require(predicted.ndim == 2 and truth.ndim == groups.ndim == 1,
            "Invalid mask/group rank")
    require(predicted.shape[1] == len(truth) == len(groups) and len(truth) > 0,
            "Mask/group lengths differ or empty")
    for value in (predicted, truth, groups):
        require(np.issubdtype(value.dtype, np.integer), "Integer mask/group arrays required")
    require(np.all((predicted >= 0) & (predicted <= 31)), "Invalid predicted bit mask")
    require(np.all((truth > 0) & (truth <= 31)), "Invalid true bit mask")
    levels = sorted(set(map(int, groups)))
    require(levels == list(range(len(levels))), "Noncanonical replicate labels")
    counts = np.zeros((predicted.shape[0], len(levels), 4), dtype=np.int64)
    for row, group in enumerate(groups):
        target = int(truth[row])
        for method in range(len(predicted)):
            mask = int(predicted[method, row])
            single = mask.bit_count() == 1
            counts[method, group] += (
                1, int(single), int(single and not (mask & target)),
                int((mask & target) == target),
            )
    return counts


def resampled_rates(counts, resamples, seed):
    """Use cluster multiplicities and integer dot products, not advanced indexing."""
    counts = np.asarray(counts)
    require(counts.ndim == 3 and counts.shape[2] == 4 and counts.shape[1] > 0,
            "Invalid count tensor")
    require(np.issubdtype(counts.dtype, np.integer) and np.all(counts >= 0),
            "Counts must be nonnegative integers")
    require(resamples > 0, "Positive resample count required")
    n_groups = counts.shape[1]
    draws = np.random.Generator(np.random.PCG64(seed)).integers(
        0, n_groups, size=(resamples, n_groups))
    multiplicities = np.stack([np.bincount(row, minlength=n_groups) for row in draws])
    totals = np.einsum("br,mrk->mbk", multiplicities, counts)
    require(np.all(totals[:, :, 0] > 0), "Empty resampled denominator")
    rates = np.empty((len(counts), resamples, 3), dtype=float)
    rates[:, :, 0] = totals[:, :, 1] / totals[:, :, 0]
    rates[:, :, 1] = np.nan
    valid = totals[:, :, 1] > 0
    rates[:, :, 1][valid] = totals[:, :, 2][valid] / totals[:, :, 1][valid]
    rates[:, :, 2] = totals[:, :, 3] / totals[:, :, 0]
    return rates


def percentile_summary(values):
    """Explicit type-7 order-statistic interpolation; no np.quantile call."""
    values = list(map(float, values))
    ordered = sorted(value for value in values if math.isfinite(value))
    def percentile(p):
        if not ordered:
            return None
        index = (len(ordered) - 1) * p
        low = math.floor(index)
        high = math.ceil(index)
        return ordered[low] + (index - low) * (ordered[high] - ordered[low])
    return {"lower": percentile(.025), "upper": percentile(.975),
            "defined_resamples": len(ordered), "total_resamples": len(values)}


def compare_interval(actual, expected):
    require(set(actual) == set(expected), "Interval schema differs")
    largest = 0.0
    for key in ("defined_resamples", "total_resamples"):
        require(actual[key] == expected[key], "Resample denominator mismatch")
    for key in ("lower", "upper"):
        a, b = actual[key], expected[key]
        require((a is None) == (b is None), "Undefined risk was not preserved")
        if a is not None:
            require(math.isfinite(b), "Nonfinite recorded endpoint")
            difference = abs(a - b)
            require(difference <= ROUNDING_ATOL, "Percentile endpoint mismatch")
            largest = max(largest, difference)
    return largest


def verify_panel(panel, private, config):
    name = panel["panel"]
    require(name in ["released_descriptive", *config["regimes"]], "Unexpected panel")
    path = Path(private) / ("truth_ledger_" + name + ".npz")
    with np.load(BytesIO(checked(path, panel["private_ledger_sha256"])), allow_pickle=False) as record:
        masks = record["predicted_masks"]
        truth = record["truth_masks"]
        groups = record["replicate_ids"]
    counts = cluster_counts(masks, truth, groups)
    methods = panel["methods"]
    require(len(counts) == len(methods) == 14, "Unexpected method count")
    ids = [method["id"] for method in methods]
    require(len(set(ids)) == len(ids), "Duplicate method identifier")
    for index, method in enumerate(methods):
        total = counts[index].sum(axis=0)
        expected = [method[key] for key in
                    ("samples", "singletons", "wrong_singletons", "truth_all_coleaders_covered")]
        require(total.tolist() == expected, "Independent cluster totals differ")
    if name == "released_descriptive":
        require(counts.shape[1] == 1 and panel["bootstrap"] is None,
                "Released descriptive rows must not be treated as independent replicates")
        return {"panel": name, "status": "PASS_NO_BOOTSTRAP_BY_DESIGN", "intervals": 0,
                "ledger_sha256": panel["private_ledger_sha256"]}
    require(counts.shape[1] == config["replicates"] == 32, "Wrong replicate count")
    require(np.all(counts[:, :, 0] == 24), "Each independent replicate must contain 24 rows")
    rates = resampled_rates(counts, config["bootstrap_resamples"], config["bootstrap_seed"])
    recorded = panel["bootstrap"]
    require(recorded["replicates"] == 32 and
            recorded["unit"] == "whole independent replicate containing 24 paired rows",
            "Wrong resampling unit")
    require(set(recorded["marginal_percentile_intervals"]) == set(ids), "Marginal method set differs")
    comparisons = {(i, 0) for i in range(1, len(ids))}
    for alpha in config["alpha_grid"]:
        selected = [i for i, m in enumerate(methods)
                    if m["family"] == "selected_joint_contrast" and m["alpha"] == alpha]
        union = [i for i, m in enumerate(methods)
                 if m["family"] == "union_joint_contrast" and m["alpha"] == alpha]
        require(len(selected) == len(union) == 1, "Missing or duplicate contrast operating point")
        comparisons.add((union[0], selected[0]))
        if alpha == .05:
            comparisons.update(((1, selected[0]), (1, union[0])))
    pair_records = recorded["paired_differences"]
    pairs = [(p["left"], p["right"]) for p in pair_records]
    require(len(pairs) == len(set(pairs)) and
            set(pairs) == {(ids[a], ids[b]) for a, b in comparisons}, "Paired comparison set differs")
    maximum, intervals = 0.0, 0
    for i, method in enumerate(ids):
        record = recorded["marginal_percentile_intervals"][method]
        require(set(record) == set(METRICS), "Marginal metric set differs")
        for k, key in enumerate(METRICS):
            maximum = max(maximum, compare_interval(percentile_summary(rates[i, :, k]), record[key]))
            intervals += 1
    for record in pair_records:
        a, b = ids.index(record["left"]), ids.index(record["right"])
        require(set(record) == {"left", "right", "singleton_coverage_difference",
                                "wrong_singleton_risk_difference"}, "Paired metric schema differs")
        for k, key in enumerate(("singleton_coverage_difference", "wrong_singleton_risk_difference")):
            difference = rates[a, :, k] - rates[b, :, k]
            maximum = max(maximum, compare_interval(percentile_summary(difference), record[key]))
            intervals += 1
    return {"panel": name, "status": "PASS", "intervals": intervals,
            "replicates": 32, "paired_resamples": config["bootstrap_resamples"],
            "maximum_absolute_endpoint_difference": maximum,
            "ledger_sha256": panel["private_ledger_sha256"]}


def verify(private=PRIVATE):
    configuration = json.loads(checked(PUBLIC / "truth_configuration_frozen.json", CONFIG_HASH))
    report = json.loads(checked(PUBLIC / "truth_results.json", RESULT_HASH))
    config = configuration["config"]
    require(report["configuration_sha256"] == CONFIG_HASH, "Report configuration mismatch")
    require(config["bootstrap_resamples"] == 2000 and config["bootstrap_seed"] == 2026092703,
            "Frozen resampling plan differs")
    require([panel["panel"] for panel in report["panels"]] ==
            ["released_descriptive", *config["regimes"]], "Panel order/universe differs")
    panels = [verify_panel(panel, private, config) for panel in report["panels"]]
    return {"status": "PASS", "completed_utc": datetime.now(timezone.utc).isoformat(),
            "truth_results_sha256": RESULT_HASH, "configuration_sha256": CONFIG_HASH,
            "verifier_sha256": digest(Path(__file__).read_bytes()),
            "tests_sha256": digest((ROOT / "tests/test_truth_bootstrap_records.py").read_bytes()),
            "python": platform.python_version(), "numpy": np.__version__,
            "new_model_fits": 0, "producer_imported": False,
            "method": "Rowwise bit-mask counts, integer cluster multiplicities, explicit type-7 interpolation",
            "endpoint_rounding_absolute_tolerance": ROUNDING_ATOL,
            "intervals_verified": sum(panel["intervals"] for panel in panels), "panels": panels,
            "limits": "Saved-decision arithmetic replay only; no added samples, calibrated population coverage, matched reporting coverage or zero-risk guarantee. All original null results and failures preserved."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, default=PRIVATE)
    parser.add_argument("--output", type=Path, default=PUBLIC / "truth_bootstrap_verification.json")
    args = parser.parse_args()
    require(not args.output.exists(), "Output exists; never replace historical verification")
    result = verify(args.private)
    payload = (json.dumps(result, indent=2, allow_nan=False) + "\n").encode()
    with args.output.open("xb") as stream:
        stream.write(payload)
    print(json.dumps(result, indent=2))
