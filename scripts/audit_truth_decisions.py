#!/usr/bin/env python3
"""Frozen construction-truth decision benchmark: test -> prepare -> score.

No named environmental-source or total atmospheric mass endpoint is asserted.
Public outputs are aggregates; generated arrays and row-level decisions are private.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import itertools
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from zipfile import ZipFile

import numpy as np
import scipy
from scipy.stats import chi2, norm

import audit_epa_native_strengthening as native


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
ARCHIVE = ROOT / "_inputs/decision_research_20260926/truth_benchmark/datasets_bamf_horseshoe.zip"
V2 = PUBLIC / "TRUTH_BENCHMARK_AUDIT.md"
V2_SOURCES = PUBLIC / "truth_benchmark_sources.json"
V3 = PUBLIC / "truth_protocol_v3.md"
TESTS = ROOT / "tests/test_truth_decisions.py"
MEMBER = "datasets/online_SDs/Zurich/Zurich_0.h5"
TRUSTED = {
    "archive": "e4f6e055a3db15e22f7c0c449a84d2d23a1f86270d658ff3f1a63fc435367501",
    "member": "fa62a734a1dda779df572e0c975e3103a2c9ad06d2a3eaffc2ed8affd3d89d64",
    "v2": "5b5ad892f2ca2c44e498deab3e34118d67b85bad8e96ba08e72e5fdac6675ac0",
    "v2_sources": "f4530e2093f143f76d72536f18077bee729ecbc6fcc19094d16f671c5ca67bb0",
    "native_solver": "42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09",
}
ALL_IDS = tuple(range(5))
ALL_PAIRS = tuple(itertools.combinations(ALL_IDS, 2))
REGIMES = (
    "included_truth", "excluded_profile_truth", "correlated_receptor_error",
    "underreported_uncertainty", "omitted_source_4", "near_tied_leaders",
)
ALPHAS = (0.5, 0.2, 0.1, 0.05, 0.01, 0.001)
CONFIG = {
    "version": 3,
    "endpoint": "largest modeled integrated signal across the 82 released channels; not total atmospheric mass",
    "source_ids": list(ALL_IDS), "archive_member": MEMBER,
    "released_rows": 336, "channels": 82, "generated_rows": [14 * i for i in range(24)],
    "replicates": 32, "regimes": list(REGIMES),
    "profile_seed": 2026092701, "noise_seed": 2026092702,
    "bootstrap_seed": 2026092703, "rng": "PCG64", "bootstrap_resamples": 2000,
    "profile_directions": 4, "candidate_log_multiplier": 0.15,
    "excluded_truth_log_multiplier": 0.30,
    "noise_scale": 1.0, "correlation": 0.5, "underreport_multiplier": 0.5,
    "near_tie_max_multiplier": 1.2, "near_tie_ratio": 0.99,
    "alpha_grid": list(ALPHAS), "admission_q_probability": 0.95,
    "source_tolerance_relative": 1e-10, "variance_cancellation_tolerance": 1e-12,
    "nonnegativity": "exclude fit below -tau; retain/count tiny negative values without clipping",
    "profile_error_within_candidate": 0,
    "solver": "unchanged audit_epa_native_strengthening.effective_variance_fit; no source pruning",
    "native_mass_placeholder": "TMAC=1 only for ignored native percent_mass diagnostic, never an endpoint",
    "covariance": "inverse weighted profile Gram matrix using absolute supplied sigma; no empirical scale",
    "fit_admission": "finite positive sigma; finite full-rank converged fit/covariance; shared nonnegativity; inclusive Q gate",
    "winner": "minimum Q among shared-admissible fits, index tie-break; separate numerical pre-admission diagnostic",
    "truth_set_coverage": "all true co-leaders must be in prediction set; empty failures never covered",
    "wrong_singleton": "predicted singleton is not a true co-leader; zero singleton denominator gives null",
    "pairwise_denominators": "all ten source pairs and fitted pairs (six when source4 omitted) separately",
    "contrast_threshold": "Bonferroni two-sided normal across fitted unordered pairs; candidate upper>=-tau, strict lower>tau",
    "no_nominal_guarantee": "profile selection, fit gates, model misspecification and release error mismatch preclude automatic nominal interpretation",
    "public_scope": "configuration, hashes, tests and aggregate metrics only; all full arrays and row decisions private",
    "continuous_box_method": "not included or authorized",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    return sha(path.read_bytes())


def immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"immutable artifact differs: {path.name}")
        return
    with path.open("xb") as handle:
        handle.write(payload)


def array_hash(value: np.ndarray) -> str:
    value = np.ascontiguousarray(value)
    if value.dtype.hasobject:
        raise ValueError("object arrays forbidden")
    return sha(json_bytes({"dtype": value.dtype.str, "shape": list(value.shape)}) + value.tobytes(order="C"))


def implementation_hashes() -> dict:
    records = {
        "script": file_hash(Path(__file__)), "tests": file_hash(TESTS),
        "native_solver": file_hash(Path(native.__file__)), "v2": file_hash(V2),
        "v2_sources": file_hash(V2_SOURCES), "v3": file_hash(V3),
    }
    for name in ("native_solver", "v2", "v2_sources"):
        if records[name] != TRUSTED[name]:
            raise ValueError(f"preserved provenance mismatch: {name}")
    return records


def checked_h5py():
    # Scoped read-only binary parser dependency, not a global-runtime installation.
    dependency = ROOT / "tmp/decision_research_hdf5_deps"
    if str(dependency) not in sys.path:
        sys.path.insert(0, str(dependency))
    import h5py
    return h5py


def compensated_profile(f: np.ndarray, g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f, g = np.asarray(f, float), np.asarray(g, float)
    if f.ndim != 2 or g.ndim != 2 or f.shape[0] != g.shape[1]:
        raise ValueError("profile/contribution shape mismatch")
    if not np.isfinite(f).all() or not np.isfinite(g).all() or np.any(f < 0) or np.any(g < 0):
        raise ValueError("invalid generating profiles or truth")
    row_sum = f.sum(axis=1)
    if np.any(row_sum <= 0):
        raise ValueError("zero profile mass")
    p, m = f / row_sum[:, None], g * row_sum[None, :]
    if not np.allclose(g @ f, m @ p, rtol=1e-12, atol=1e-12):
        raise ValueError("compensated normalization did not preserve forward signal")
    return p, m


def load_release(path: Path = ARCHIVE) -> tuple[dict[str, np.ndarray], str]:
    payload = path.read_bytes()
    if sha(payload) != TRUSTED["archive"]:
        raise ValueError("archive hash mismatch")
    with ZipFile(BytesIO(payload)) as archive:
        member = archive.read(MEMBER)
    if sha(member) != TRUSTED["member"]:
        raise ValueError("member hash mismatch")
    h5py = checked_h5py()
    with h5py.File(BytesIO(member), "r") as h5:
        if set(h5) != {"F", "G", "data", "error"}:
            raise ValueError("unexpected HDF5 groups")
        arrays = {name: h5[f"{name}/block0_values"][()] for name in ("F", "G", "data", "error")}
        expected = {"F": (5, 82), "G": (336, 5), "data": (336, 82), "error": (336, 82)}
        for name, values in arrays.items():
            if values.shape != expected[name] or values.dtype.kind != "f" or not np.isfinite(values).all() or np.any(values <= 0):
                raise ValueError(f"invalid released array: {name}")
        if not np.array_equal(h5["F/axis1"][()], np.arange(5)) or not np.array_equal(h5["G/axis0"][()], np.arange(5)):
            raise ValueError("source axes mismatch")
        channels = h5["F/axis0"][()]
        for name in ("data", "error"):
            if not np.array_equal(h5[f"{name}/axis0"][()], channels):
                raise ValueError("channel axes mismatch")
        for name in ("G", "data", "error"):
            if not np.array_equal(h5[f"{name}/axis1"][()], np.arange(336)):
                raise ValueError("row axes mismatch")
    p, m = compensated_profile(arrays["F"], arrays["G"])
    return {"P0": p, "M0": m, "released_x": arrays["data"],
            "released_sigma": arrays["error"], "channels": channels}, h5py.__version__


def generate_controls(p: np.ndarray, m: np.ndarray, sigma: np.ndarray, config: dict = CONFIG) -> tuple[dict, dict]:
    """Only input generation; no fitting, estimated decisions or scoring here."""
    rows = np.asarray(config["generated_rows"], dtype=np.int64)
    repeats = int(config["replicates"])
    if p.ndim != 2 or p.shape[0] != 5 or m.shape[1] != 5 or sigma.shape != (m.shape[0], p.shape[1]):
        raise ValueError("invalid generator dimensions")
    if not all(np.isfinite(v).all() for v in (p, m, sigma)) or np.any(p <= 0) or np.any(m < 0) or np.any(sigma <= 0):
        raise ValueError("invalid generator values")
    if not np.allclose(p.sum(axis=1), 1.0, rtol=1e-12, atol=1e-12):
        raise ValueError("generator profiles not on declared integrated-signal scale")
    profile_rng = np.random.Generator(np.random.PCG64(config["profile_seed"]))
    noise_rng = np.random.Generator(np.random.PCG64(config["noise_seed"]))
    states = {"profile_before": profile_rng.bit_generator.state, "noise_before": noise_rng.bit_generator.state}
    directions = profile_rng.standard_normal((config["profile_directions"], *p.shape))
    candidates = [p.copy()]
    for direction in directions:
        for sign in (1.0, -1.0):
            alternative = p * np.exp(sign * config["candidate_log_multiplier"] * direction)
            candidates.append(alternative / alternative.sum(axis=1)[:, None])
    excluded_direction = profile_rng.standard_normal(p.shape)
    excluded = p * np.exp(config["excluded_truth_log_multiplier"] * excluded_direction)
    excluded /= excluded.sum(axis=1)[:, None]
    z = noise_rng.standard_normal((repeats, len(rows), p.shape[1]))
    a = noise_rng.standard_normal((repeats, len(rows)))
    base_m, base_sigma = m[rows], sigma[rows]
    truth = np.broadcast_to(base_m, (len(REGIMES), repeats, *base_m.shape)).copy()
    generated_sigma = np.broadcast_to(base_sigma, (len(REGIMES), repeats, *base_sigma.shape)).copy()
    generated_x = np.empty_like(generated_sigma)
    for index, regime in enumerate(REGIMES):
        true_p = excluded if regime == "excluded_profile_truth" else p
        if regime == "near_tied_leaders":
            height = config["near_tie_max_multiplier"] * np.max(base_m, axis=1)
            truth[index, :, :, 0] = height
            truth[index, :, :, 1] = config["near_tie_ratio"] * height
        noise = z
        if regime == "correlated_receptor_error":
            rho = config["correlation"]
            noise = np.sqrt(rho) * a[:, :, None] + np.sqrt(1.0 - rho) * z
        generated_x[index] = truth[index] @ true_p + base_sigma[None, :, :] * noise
        if regime == "underreported_uncertainty":
            generated_sigma[index] *= config["underreport_multiplier"]
    states.update(profile_after=profile_rng.bit_generator.state, noise_after=noise_rng.bit_generator.state)
    return {
        "candidates": np.asarray(candidates), "profile_directions": directions,
        "excluded_direction": excluded_direction, "excluded_profile": excluded,
        "noise_z": z, "noise_a": a, "generated_x": generated_x,
        "generated_sigma": generated_sigma, "generated_truth": truth, "generated_rows": rows,
    }, states


def tolerance(values: np.ndarray) -> float:
    return CONFIG["source_tolerance_relative"] * max(1.0, float(np.max(np.abs(values))))


def top_mask(values: np.ndarray, source_ids=ALL_IDS) -> int:
    values = np.asarray(values, float)
    if values.shape != (len(source_ids),) or not np.isfinite(values).all() or len(source_ids) == 0:
        raise ValueError("invalid contribution vector")
    tau = tolerance(values)
    return sum(1 << int(sid) for sid, value in zip(source_ids, values) if float(values.max() - value) <= tau)


def declared_pair_signs(values: np.ndarray, source_ids) -> np.ndarray:
    tau = tolerance(values)
    local = {sid: index for index, sid in enumerate(source_ids)}
    out = np.zeros(len(ALL_PAIRS), dtype=np.int8)
    for index, (j, k) in enumerate(ALL_PAIRS):
        if j in local and k in local:
            difference = values[local[j]] - values[local[k]]
            out[index] = 1 if difference > tau else (-1 if difference < -tau else 0)
    return out


def contrast_variance(covariance: np.ndarray) -> np.ndarray:
    covariance = np.asarray(covariance, float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1] or not np.isfinite(covariance).all():
        raise ValueError("invalid covariance")
    v = np.diag(covariance)[:, None] + np.diag(covariance)[None, :] - 2 * covariance
    allowance = CONFIG["variance_cancellation_tolerance"] * max(1.0, float(np.max(np.abs(covariance))))
    if np.any(v < -allowance):
        raise ValueError("negative contrast variance beyond cancellation tolerance")
    return np.maximum(v, 0.0)


def joint_contrast_decision(values: np.ndarray, covariance: np.ndarray, source_ids, alpha: float) -> tuple[int, np.ndarray]:
    if not 0 < alpha < 1 or len(source_ids) < 2:
        raise ValueError("invalid contrast alpha or universe")
    values = np.asarray(values, float)
    if values.shape != (len(source_ids),) or covariance.shape != (len(source_ids), len(source_ids)) or not np.isfinite(values).all():
        raise ValueError("contrast shape/nonfinite error")
    pairs = len(source_ids) * (len(source_ids) - 1) // 2
    z = norm.ppf(1.0 - alpha / (2.0 * pairs))
    half_width = z * np.sqrt(contrast_variance(covariance))
    difference = values[:, None] - values[None, :]
    tau = tolerance(values)
    upper, lower = difference + half_width, difference - half_width
    candidates = np.all(upper >= -tau, axis=1)
    mask = sum(1 << int(sid) for sid, keep in zip(source_ids, candidates) if keep)
    local = {sid: i for i, sid in enumerate(source_ids)}
    signs = np.zeros(len(ALL_PAIRS), dtype=np.int8)
    for index, (j, k) in enumerate(ALL_PAIRS):
        if j not in local or k not in local:
            continue
        a, b = local[j], local[k]
        signs[index] = 1 if lower[a, b] > tau else (-1 if upper[a, b] < -tau else 0)
    return mask, signs


def make_native_profiles(candidates: np.ndarray, source_ids) -> tuple[list[str], list[dict]]:
    species = [f"S{index:03d}C" for index in range(candidates.shape[2])]
    profiles = []
    for profile in candidates:
        item = {}
        for sid in source_ids:
            row = {}
            for channel, name in enumerate(species):
                row[name] = float(profile[sid, channel])
                row[name[:-1] + "U"] = 0.0
            item[str(sid)] = row
        profiles.append(item)
    return species, profiles


def admit_fit(values: np.ndarray, q: float, q_limit: float, converged=True, covariance_valid=True) -> tuple[bool, list[str], bool]:
    values = np.asarray(values, float)
    flags = []
    if not converged:
        flags.append("nonconverged")
    if not np.isfinite(values).all() or not np.isfinite(q) or q < 0:
        flags.append("nonfinite_fit")
    if not covariance_valid:
        flags.append("invalid_covariance")
    tiny_negative = False
    if np.isfinite(values).all() and len(values):
        tau = tolerance(values)
        if np.any(values < -tau):
            flags.append("negative_contribution")
        tiny_negative = bool(np.any((values < 0) & (values >= -tau)))
    if np.isfinite(q) and q > q_limit:
        flags.append("q_rejected")
    return not flags, flags, tiny_negative


def fit_family(y: np.ndarray, sigma: np.ndarray, candidates: np.ndarray, source_ids=ALL_IDS, prepared_profiles=None) -> list[dict]:
    y, sigma, candidates = np.asarray(y, float), np.asarray(sigma, float), np.asarray(candidates, float)
    n, p = len(y), len(source_ids)
    invalid = y.ndim != 1 or sigma.shape != y.shape or candidates.ndim != 3 or candidates.shape[1] != 5 or candidates.shape[2] != n or n <= p
    invalid |= not np.isfinite(y).all() or not np.isfinite(sigma).all() or np.any(sigma <= 0) or not np.isfinite(candidates).all()
    if invalid:
        return [{"index": i, "numeric": False, "accepted": False, "flags": ["invalid_input"], "tiny_negative": False}
                for i in range(len(candidates))]
    species, profiles = prepared_profiles if prepared_profiles is not None else make_native_profiles(candidates, source_ids)
    receptor = {"TMAC": 1.0}
    for name, value, error in zip(species, y, sigma):
        receptor[name] = float(value)
        receptor[name[:-1] + "U"] = float(error)
    q_limit = float(chi2.ppf(CONFIG["admission_q_probability"], n - p))
    output = []
    for index, profile in enumerate(candidates):
        row = {"index": index, "numeric": False, "accepted": False, "flags": [], "tiny_negative": False}
        try:
            result = native.effective_variance_fit(receptor, profiles[index], [str(sid) for sid in source_ids], species=species)
            values = np.asarray([result["source_contributions"][str(sid)] for sid in source_ids])
            q = float(result["reduced_chi2"] * (n - p))
            weighted = profile[list(source_ids)].T / sigma[:, None]
            covariance = np.linalg.inv(weighted.T @ weighted)
            covariance = (covariance + covariance.T) / 2.0
            covariance_valid = bool(np.isfinite(covariance).all() and np.all(np.linalg.eigvalsh(covariance) > 0))
            if covariance_valid:
                contrast_variance(covariance)
            numeric = bool(result["converged"] and np.isfinite(values).all() and np.isfinite(q) and covariance_valid)
            accepted, flags, tiny = admit_fit(values, q, q_limit, result["converged"], covariance_valid)
            row.update(numeric=numeric, accepted=accepted, flags=flags, tiny_negative=tiny,
                       values=values, covariance=covariance, q=q, iterations=result["iterations"])
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            flag = "rank_deficient" if "rank" in str(exc).lower() or isinstance(exc, np.linalg.LinAlgError) else "numerical_exception"
            row.update(flags=[flag], error=str(exc))
        output.append(row)
    return output


def method_specs() -> list[dict]:
    records = [{"id": "selected_point", "family": "selected_point", "alpha": None},
               {"id": "finite_point_union", "family": "finite_point_union", "alpha": None}]
    for alpha in ALPHAS:
        for family in ("selected_joint_contrast", "union_joint_contrast"):
            records.append({"id": f"{family}@{alpha:g}", "family": family, "alpha": alpha})
    return records


METHODS = method_specs()


def family_decisions(fits: list[dict], source_ids) -> dict:
    masks = np.zeros(len(METHODS), dtype=np.uint8)
    orders = np.zeros((len(METHODS), len(ALL_PAIRS)), dtype=np.int8)
    numeric = [fit for fit in fits if fit["numeric"]]
    accepted = [fit for fit in fits if fit["accepted"]]
    diagnostic = min(numeric, key=lambda fit: (fit["q"], fit["index"])) if numeric else None
    selected = min(accepted, key=lambda fit: (fit["q"], fit["index"])) if accepted else None
    info = {"masks": masks, "orders": orders, "accepted_count": len(accepted),
            "selected_index": -1 if selected is None else selected["index"],
            "diagnostic_index": -1 if diagnostic is None else diagnostic["index"],
            "diagnostic_mask": 0 if diagnostic is None else top_mask(diagnostic["values"], source_ids),
            "subset_checks": 0}
    if not accepted:
        return info
    point_masks = [top_mask(fit["values"], source_ids) for fit in accepted]
    masks[0] = top_mask(selected["values"], source_ids)
    masks[1] = np.bitwise_or.reduce(np.asarray(point_masks, dtype=np.uint8))
    point_orders = np.asarray([declared_pair_signs(fit["values"], source_ids) for fit in accepted])
    orders[0] = declared_pair_signs(selected["values"], source_ids)
    orders[1] = np.where(np.all(point_orders == 1, axis=0), 1, np.where(np.all(point_orders == -1, axis=0), -1, 0))
    for method_index, method in enumerate(METHODS[2:], start=2):
        contrast_results = [joint_contrast_decision(fit["values"], fit["covariance"], source_ids, method["alpha"]) for fit in accepted]
        selected_local_index = accepted.index(selected)
        if method["family"] == "selected_joint_contrast":
            masks[method_index], orders[method_index] = contrast_results[selected_local_index]
            contained = masks[0]
        else:
            masks[method_index] = np.bitwise_or.reduce(np.asarray([item[0] for item in contrast_results], dtype=np.uint8))
            signs = np.asarray([item[1] for item in contrast_results])
            orders[method_index] = np.where(np.all(signs == 1, axis=0), 1, np.where(np.all(signs == -1, axis=0), -1, 0))
            contained = masks[1]
        if int(contained) & ~int(masks[method_index]):
            raise AssertionError("point-set containment in contrast set violated")
        info["subset_checks"] += 1
    return info


def metric_counts(predictions: np.ndarray, truth_masks: np.ndarray, orders: np.ndarray, truth_orders: np.ndarray, fitted_pair_count: int) -> dict:
    predictions, truth_masks = np.asarray(predictions, np.uint8), np.asarray(truth_masks, np.uint8)
    if predictions.shape != truth_masks.shape or orders.shape != truth_orders.shape or orders.shape != (len(predictions), 10):
        raise ValueError("metric shape mismatch")
    if np.any(truth_masks == 0) or np.any(truth_masks > 31) or np.any(predictions > 31):
        raise ValueError("invalid truth/prediction bit masks")
    size = np.asarray([int(mask).bit_count() for mask in predictions])
    singleton = size == 1
    wrong = singleton & ((predictions & truth_masks) == 0)
    covered = (predictions & truth_masks) == truth_masks
    declared = orders != 0
    false = declared & (orders != truth_orders)
    return {
        "samples": len(predictions), "singletons": int(singleton.sum()),
        "wrong_singletons": int(wrong.sum()), "truth_all_coleaders_covered": int(covered.sum()),
        "empty_failures": int((size == 0).sum()), "nonempty_ambiguous": int((size > 1).sum()),
        "nonempty": int((size > 0).sum()), "set_size_sum": int(size.sum()),
        "pair_declarations": int(declared.sum()), "false_pair_declarations": int(false.sum()),
        "all_pair_opportunities": len(predictions) * 10,
        "fitted_pair_opportunities": len(predictions) * fitted_pair_count,
    }


def ratio(numerator, denominator):
    return float(numerator / denominator) if denominator else None


def metrics_from_counts(counts: dict) -> dict:
    n = counts["samples"]
    return {
        **counts,
        "singleton_coverage": ratio(counts["singletons"], n),
        "wrong_singleton_risk": ratio(counts["wrong_singletons"], counts["singletons"]),
        "truth_in_set_all_coleaders_coverage": ratio(counts["truth_all_coleaders_covered"], n),
        "empty_failure_fraction": ratio(counts["empty_failures"], n),
        "mean_set_size_all_samples": ratio(counts["set_size_sum"], n),
        "mean_set_size_nonempty": ratio(counts["set_size_sum"], counts["nonempty"]),
        "pair_declaration_coverage_all_ten": ratio(counts["pair_declarations"], counts["all_pair_opportunities"]),
        "pair_declaration_coverage_fitted": ratio(counts["pair_declarations"], counts["fitted_pair_opportunities"]),
        "false_pair_declaration_risk": ratio(counts["false_pair_declarations"], counts["pair_declarations"]),
    }


def interval(values: np.ndarray) -> dict:
    finite = np.asarray(values)[np.isfinite(values)]
    return {"lower": float(np.quantile(finite, 0.025)) if len(finite) else None,
            "upper": float(np.quantile(finite, 0.975)) if len(finite) else None,
            "defined_resamples": len(finite), "total_resamples": len(values)}


def bootstrap_paired(rep_counts: list[list[dict]]) -> dict:
    # Axes: method, replicate. Shared resampling preserves all pairing.
    replicates = len(rep_counts[0])
    rng = np.random.Generator(np.random.PCG64(CONFIG["bootstrap_seed"]))
    sampled = rng.integers(0, replicates, size=(CONFIG["bootstrap_resamples"], replicates))
    arrays = {key: np.asarray([[row[key] for row in method] for method in rep_counts])
              for key in ("samples", "singletons", "wrong_singletons", "truth_all_coleaders_covered")}
    totals = {key: values[:, sampled].sum(axis=2) for key, values in arrays.items()}
    coverage = totals["singletons"] / totals["samples"]
    risk = np.full_like(coverage, np.nan, dtype=float)
    np.divide(totals["wrong_singletons"], totals["singletons"], out=risk, where=totals["singletons"] > 0)
    truth_coverage = totals["truth_all_coleaders_covered"] / totals["samples"]
    marginal = {method["id"]: {"singleton_coverage": interval(coverage[index]),
                               "wrong_singleton_risk": interval(risk[index]),
                               "truth_in_set_coverage": interval(truth_coverage[index])}
                for index, method in enumerate(METHODS)}
    comparisons = {(index, 0) for index in range(1, len(METHODS))}
    for alpha in ALPHAS:
        selected = next(i for i, m in enumerate(METHODS) if m["family"] == "selected_joint_contrast" and m["alpha"] == alpha)
        union = next(i for i, m in enumerate(METHODS) if m["family"] == "union_joint_contrast" and m["alpha"] == alpha)
        comparisons.add((union, selected))
        if alpha == 0.05:
            comparisons.update(((1, selected), (1, union)))
    paired = [{"left": METHODS[left]["id"], "right": METHODS[right]["id"],
               "singleton_coverage_difference": interval(coverage[left] - coverage[right]),
               "wrong_singleton_risk_difference": interval(risk[left] - risk[right])}
              for left, right in sorted(comparisons)]
    return {"unit": "whole independent replicate containing 24 paired rows", "replicates": replicates,
            "marginal_percentile_intervals": marginal, "paired_differences": paired,
            "warning": "Descriptive empirical bootstrap; retained singleton sets differ, not matched coverage; zero observed errors do not prove zero risk"}


def evaluate_panel(name: str, x: np.ndarray, sigma: np.ndarray, truth: np.ndarray, candidates: np.ndarray, source_ids, replicate_ids: np.ndarray) -> tuple[dict, dict]:
    n = len(x)
    if x.shape != sigma.shape or truth.shape != (n, 5) or len(replicate_ids) != n:
        raise ValueError("panel dimension mismatch")
    prepared = make_native_profiles(candidates, source_ids)
    masks = np.zeros((len(METHODS), n), dtype=np.uint8)
    orders = np.zeros((len(METHODS), n, 10), dtype=np.int8)
    truth_masks = np.asarray([top_mask(row) for row in truth], dtype=np.uint8)
    truth_orders = np.asarray([declared_pair_signs(row, ALL_IDS) for row in truth], dtype=np.int8)
    contribution = np.full((n, len(candidates), 5), np.nan)
    covariance = np.full((n, len(candidates), 5, 5), np.nan)
    q_values = np.full((n, len(candidates)), np.nan)
    accepted = np.zeros((n, len(candidates)), dtype=bool)
    numeric = np.zeros_like(accepted)
    selected = np.full(n, -1, dtype=np.int16)
    diagnostic = np.full(n, -1, dtype=np.int16)
    diagnostic_masks = np.zeros(n, dtype=np.uint8)
    flags, first_flags = Counter(), Counter()
    tiny_negative = 0
    subset_checks = 0
    failures = []
    for row_index in range(n):
        fits = fit_family(x[row_index], sigma[row_index], candidates, source_ids, prepared)
        for fit in fits:
            index = fit["index"]
            flags.update(fit["flags"])
            first_flags.update([fit["flags"][0] if fit["flags"] else "accepted"])
            tiny_negative += int(fit["tiny_negative"])
            numeric[row_index, index] = fit["numeric"]
            accepted[row_index, index] = fit["accepted"]
            if "values" in fit:
                contribution[row_index, index, list(source_ids)] = fit["values"]
                covariance[row_index, index][np.ix_(source_ids, source_ids)] = fit["covariance"]
                q_values[row_index, index] = fit["q"]
            if fit["flags"]:
                failures.append({"row": row_index, "profile": index, "flags": fit["flags"], "error": fit.get("error")})
        decisions = family_decisions(fits, source_ids)
        masks[:, row_index], orders[:, row_index] = decisions["masks"], decisions["orders"]
        selected[row_index], diagnostic[row_index] = decisions["selected_index"], decisions["diagnostic_index"]
        diagnostic_masks[row_index] = decisions["diagnostic_mask"]
        subset_checks += decisions["subset_checks"]
    fitted_pair_count = len(source_ids) * (len(source_ids) - 1) // 2
    results, replicate_counts = [], []
    for index, method in enumerate(METHODS):
        counts = metric_counts(masks[index], truth_masks, orders[index], truth_orders, fitted_pair_count)
        results.append({**method, **metrics_from_counts(counts)})
        replicate_counts.append([metric_counts(masks[index, replicate_ids == rep], truth_masks[replicate_ids == rep],
                                              orders[index, replicate_ids == rep], truth_orders[replicate_ids == rep], fitted_pair_count)
                                 for rep in np.unique(replicate_ids)])
    diagnostic_singletons = np.asarray([int(mask).bit_count() == 1 for mask in diagnostic_masks])
    report = {
        "panel": name, "samples": n, "source_ids_fitted": list(source_ids), "truth_source_ids": list(ALL_IDS),
        "fit_attempts": n * len(candidates), "numerical_fits": int(numeric.sum()), "admissible_fits": int(accepted.sum()),
        "fit_flags_overlapping": dict(flags), "first_exclusion_or_accepted_counts": dict(first_flags),
        "fits_with_retained_tiny_negative_coefficients": tiny_negative,
        "samples_without_admissible_fit": int(np.sum(selected < 0)),
        "subset_invariant_checks_passed": subset_checks,
        "numerical_minQ_before_admission_diagnostic": {
            "label": "Not a primary admissible method; can include negative coefficients and failed Q gates",
            "available_samples": int(np.sum(diagnostic >= 0)), "singletons": int(diagnostic_singletons.sum()),
            "wrong_singletons": int(np.sum(diagnostic_singletons & ((diagnostic_masks & truth_masks) == 0))),
            "samples_with_different_numerical_and_admissible_winner": int(np.sum((diagnostic >= 0) & (selected >= 0) & (diagnostic != selected))),
        },
        "methods": results,
        "bootstrap": bootstrap_paired(replicate_counts) if len(np.unique(replicate_ids)) > 1 else None,
        "interpretation": "simulation-integrated-signal truth only; no automatic nominal coverage or novel-method claim",
    }
    ledger = {"predicted_masks": masks, "orders": orders, "truth_masks": truth_masks, "truth_orders": truth_orders,
              "contributions": contribution, "covariance": covariance, "Q": q_values, "accepted": accepted,
              "numeric": numeric, "selected_index": selected, "diagnostic_index": diagnostic,
              "diagnostic_masks": diagnostic_masks, "replicate_ids": replicate_ids,
              "failure_details": failures}
    return report, ledger


def run_test_gate(public: Path = PUBLIC, private: Path = PRIVATE) -> dict:
    hashes = implementation_hashes()
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_truth_decisions.py", "-v"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
    log = result.stdout + result.stderr
    match = re.search(r"Ran (\d+) tests?", log)
    count = int(match.group(1)) if match else 0
    record = {"created_at_utc": now(), "passed": result.returncode == 0 and count >= 20,
              "returncode": result.returncode, "tests_run": count, "hashes": hashes,
              "log_sha256": sha(log.encode()), "command": command,
              "benchmark_arrays_or_fits_used": False}
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    # Gate can be rerun before preparation, but never silently replace a prepared gate.
    if (private / "truth_input_freeze.json").exists():
        raise ValueError("inputs already frozen; test gate replacement prohibited")
    (public / "truth_test_log.txt").write_text(log, encoding="utf-8")
    for directory in (public, private):
        (directory / "truth_test_gate.json").write_bytes(json_bytes(record))
    if not record["passed"]:
        raise ValueError(f"synthetic test gate failed: {count} tests; inspect truth_test_log.txt")
    return record


def validate_gate(private: Path) -> dict:
    gate = json.loads((private / "truth_test_gate.json").read_bytes())
    if not gate["passed"] or gate["hashes"] != implementation_hashes() or gate["tests_run"] < 20:
        raise ValueError("test gate stale or unsuccessful")
    return gate


def prepare(public: Path = PUBLIC, private: Path = PRIVATE) -> dict:
    gate = validate_gate(private)
    manifest_path = private / "truth_input_freeze.json"
    if manifest_path.exists():
        return verify_frozen(private)
    release, h5py_version = load_release()
    config = {"config": CONFIG, "hashes": gate["hashes"], "test_gate_sha256": file_hash(private / "truth_test_gate.json"),
              "environment": {"python": platform.python_version(), "numpy": np.__version__,
                              "scipy": scipy.__version__, "h5py": h5py_version},
              "created_at_utc": now(), "no_scoring_has_occurred": True}
    payload = json_bytes(config)
    for directory in (public, private):
        immutable_write(directory / "truth_configuration_frozen.json", payload)
    generated, rng_states = generate_controls(release["P0"], release["M0"], release["released_sigma"])
    arrays = {**release, **generated}
    buffer = BytesIO()
    np.savez_compressed(buffer, **arrays)
    array_path = private / "truth_frozen_arrays.npz"
    immutable_write(array_path, buffer.getvalue())
    manifest = {
        "created_at_utc": now(), "configuration_sha256": sha(payload), "archive_sha256": TRUSTED["archive"],
        "member_sha256": TRUSTED["member"], "frozen_array_file": array_path.name,
        "frozen_array_file_sha256": file_hash(array_path),
        "arrays": {key: {"shape": list(value.shape), "dtype": value.dtype.str, "sha256": array_hash(value)} for key, value in arrays.items()},
        "rng_states": rng_states, "no_fit_or_scoring_performed": True,
    }
    for directory in (public, private):
        immutable_write(directory / "truth_input_freeze.json", json_bytes(manifest))
    return manifest


def verify_frozen(private: Path = PRIVATE) -> dict:
    validate_gate(private)
    config_payload = (private / "truth_configuration_frozen.json").read_bytes()
    config = json.loads(config_payload)
    if config["config"] != CONFIG or config["hashes"] != implementation_hashes():
        raise ValueError("frozen configuration/implementation mismatch")
    if config["test_gate_sha256"] != file_hash(private / "truth_test_gate.json"):
        raise ValueError("frozen test-gate hash mismatch")
    manifest = json.loads((private / "truth_input_freeze.json").read_bytes())
    if manifest["configuration_sha256"] != sha(config_payload):
        raise ValueError("configuration digest mismatch")
    archive = private / manifest["frozen_array_file"]
    if archive.parent.resolve() != private.resolve() or file_hash(archive) != manifest["frozen_array_file_sha256"]:
        raise ValueError("frozen-array archive mismatch")
    with np.load(archive, allow_pickle=False) as arrays:
        if set(arrays.files) != set(manifest["arrays"]):
            raise ValueError("frozen-array keys mismatch")
        for key, record in manifest["arrays"].items():
            value = arrays[key]
            if list(value.shape) != record["shape"] or value.dtype.str != record["dtype"] or array_hash(value) != record["sha256"]:
                raise ValueError(f"frozen array changed: {key}")
    return manifest


def render_report(report: dict) -> str:
    rows = []
    for panel in report["panels"]:
        for method in panel["methods"]:
            if method["alpha"] not in (None, 0.05):
                continue
            risk = "undefined" if method["wrong_singleton_risk"] is None else f"{method['wrong_singleton_risk']:.4f}"
            rows.append(f"| {panel['panel']} | {method['id']} | {method['singletons']}/{method['samples']} | {method['wrong_singletons']} | {risk} | {method['truth_all_coleaders_covered']}/{method['samples']} | {method['empty_failures']} |")
    attrition = "\n".join(f"| {panel['panel']} | {panel['admissible_fits']}/{panel['fit_attempts']} | {panel['samples_without_admissible_fit']}/{panel['samples']} |"
                          for panel in report["panels"])
    return "\n".join([
        "# Frozen truth-index decision comparison", "", 
        "This is a known-construction synthetic benchmark, not a named-source field validation or total atmospheric mass result. The endpoint is the largest modeled 82-channel integrated signal. All outcomes, including failures, are retained. No continuous-box method was tested.", "",
        "Source: [Via et al. 2026](https://doi.org/10.5194/amt-19-2175-2026), [CC BY 4.0 dataset](https://doi.org/10.5281/zenodo.19223353). The released error field is not assumed to calibrate its construction noise. Generated controls impose a new, explicit Gaussian law. All source-profile errors within a candidate are zero; the historical EVLS solver therefore reduces to WLS.", "",
        "## Primary operating points", "",
        "The table shows point methods and alpha 0.05 contrasts; the JSON preserves the entire six-alpha grid and paired bootstrap differences. Alpha is an operational threshold, not a promised post-selection coverage level. A lower wrong-singleton risk at lower reporting coverage is a tradeoff, not by itself an improvement.", "",
        "| Panel | Method | Singletons/all rows | Wrong singletons | Conditional risk | All-co-leader truth covered | Empty failures |",
        "|---|---|---:|---:|---:|---:|---:|", *rows, "", "## Fit attrition", "",
        "| Panel | Shared-admissible fits / attempts | Rows without admissible fits |", "|---|---:|---:|", attrition, "",
        "Negative coefficients below the declared tolerance exclude the entire fit; no clipping or pruning occurs. Overlapping rejection flags, first-exclusion counts, tiny retained negatives and pre-admission numerical winner diagnostics are in the JSON. Omitted-source metrics retain all five truth IDs and all ten pairwise opportunities, with the six fitted pairs reported separately.", "",
        f"Point-set containment in ordinary union-of-contrast sets passed {report['subset_checks_passed']} checks. This known subset relation is not a novel method. Source-specific scale-invariance was verified before fitting. Zero observed errors or a degenerate empirical bootstrap interval do not imply zero population risk.", "",
        "## Reproducibility", "", f"Implementation SHA256: `{report['hashes']['script']}`.",
        f"Frozen configuration SHA256: `{report['configuration_sha256']}`.",
        f"Frozen generated-array archive SHA256: `{report['frozen_arrays_sha256']}`.", "",
        "Protocol v2 remains byte-preserved; truth_protocol_v3.md clarifies pre-outcome admission, ties, denominators and absolute covariance. Tests, configuration and input hashes preceded scoring. Full arrays and per-row numerical ledgers remain private. Public outputs contain aggregates only.", "",
        "Reproduce in order: `python scripts/audit_truth_decisions.py test`, `... prepare`, `... score`. Preparation requires the licensed, hash-verified release and scoped h5py dependency. Synthetic tests do not need the release. Scoring checks immutable hashes and refuses stale code or inputs.", "",
    ])


def score(public: Path = PUBLIC, private: Path = PRIVATE) -> dict:
    manifest = verify_frozen(private)
    configuration = json.loads((private / "truth_configuration_frozen.json").read_bytes())
    start_path = private / "truth_score_started.json"
    if not start_path.exists():
        started = {"created_at_utc": now(), "configuration_sha256": manifest["configuration_sha256"],
                   "input_freeze_sha256": file_hash(private / "truth_input_freeze.json"),
                   "implementation_sha256": configuration["hashes"]["script"]}
        for directory in (public, private):
            immutable_write(directory / "truth_score_started.json", json_bytes(started))
    else:
        started = json.loads(start_path.read_bytes())
        if started["input_freeze_sha256"] != file_hash(private / "truth_input_freeze.json") or started["implementation_sha256"] != configuration["hashes"]["script"]:
            raise ValueError("resume score identity mismatch")
    with np.load(private / manifest["frozen_array_file"], allow_pickle=False) as frozen:
        arrays = {name: frozen[name] for name in frozen.files}
    panels = []
    for index, name in enumerate(("released_descriptive", *REGIMES)):
        result_path = public / f"truth_panel_{name}.json"
        ledger_path = private / f"truth_ledger_{name}.npz"
        failures_path = private / f"truth_failures_{name}.json"
        if result_path.exists():
            report = json.loads(result_path.read_bytes())
            if report["configuration_sha256"] != manifest["configuration_sha256"] or report["private_ledger_sha256"] != file_hash(ledger_path) or report["private_failures_sha256"] != file_hash(failures_path):
                raise ValueError("saved panel checkpoint mismatch")
        else:
            if index == 0:
                x, sigma, truth = arrays["released_x"], arrays["released_sigma"], arrays["M0"]
                replicate_ids = np.zeros(len(x), dtype=np.int16)
            else:
                x = arrays["generated_x"][index - 1].reshape(-1, 82)
                sigma = arrays["generated_sigma"][index - 1].reshape(-1, 82)
                truth = arrays["generated_truth"][index - 1].reshape(-1, 5)
                replicate_ids = np.repeat(np.arange(CONFIG["replicates"], dtype=np.int16), len(CONFIG["generated_rows"]))
            source_ids = tuple(range(4)) if name == "omitted_source_4" else ALL_IDS
            report, ledger = evaluate_panel(name, x, sigma, truth, arrays["candidates"], source_ids, replicate_ids)
            failures = ledger.pop("failure_details")
            buffer = BytesIO()
            np.savez_compressed(buffer, **ledger)
            immutable_write(ledger_path, buffer.getvalue())
            immutable_write(failures_path, json_bytes(failures))
            report.update(configuration_sha256=manifest["configuration_sha256"],
                          private_ledger_sha256=file_hash(ledger_path), private_failures_sha256=file_hash(failures_path),
                          completed_at_utc=now())
            immutable_write(result_path, json_bytes(report))
        panels.append(report)
        progress = {"updated_at_utc": now(), "completed_panels": [panel["panel"] for panel in panels],
                    "total_panels": 7, "configuration_sha256": manifest["configuration_sha256"]}
        (public / "truth_progress.json").write_bytes(json_bytes(progress))
        print(json.dumps({"panel_completed": name, "admissible_fits": report["admissible_fits"],
                          "samples_without_admissible_fit": report["samples_without_admissible_fit"]}), flush=True)
    final = {"configuration_sha256": manifest["configuration_sha256"], "hashes": configuration["hashes"],
             "frozen_arrays_sha256": manifest["frozen_array_file_sha256"],
             "started_at_utc": started["created_at_utc"], "panels": panels,
             "subset_checks_passed": sum(panel["subset_invariant_checks_passed"] for panel in panels),
             "source": {"article_doi": "10.5194/amt-19-2175-2026", "dataset_doi": "10.5281/zenodo.19223353", "license": "CC BY 4.0"},
             "no_field_truth_or_novel_method_claim": True}
    immutable_write(public / "truth_results.json", json_bytes(final))
    immutable_write(public / "truth_report.md", render_report(final).encode())
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("test", "prepare", "score", "verify"))
    args = parser.parse_args()
    if args.stage == "test":
        result = run_test_gate()
        print(json.dumps({"tests": result["tests_run"], "passed": result["passed"], "script_sha256": result["hashes"]["script"]}))
    elif args.stage == "prepare":
        result = prepare()
        print(json.dumps({"configuration_sha256": result["configuration_sha256"], "array_archive_sha256": result["frozen_array_file_sha256"], "no_scoring": True}))
    elif args.stage == "verify":
        result = verify_frozen()
        print(json.dumps({"verified": True, "configuration_sha256": result["configuration_sha256"]}))
    else:
        result = score()
        print(json.dumps({"completed_panels": len(result["panels"]), "subset_checks": result["subset_checks_passed"]}))


if __name__ == "__main__":
    main()
