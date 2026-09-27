"""Post-run, independently vectorized ledger verification; never refits or tunes."""
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
from scipy.stats import chi2, norm

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
PAIRS = list(itertools.combinations(range(5), 2))
summary = json.loads((PUBLIC / "truth_results.json").read_text())
with np.load(PRIVATE / "truth_frozen_arrays.npz", allow_pickle=False) as stored:
    inputs = {key: stored[key] for key in stored.files}

checks = []
for panel_index, panel in enumerate(summary["panels"]):
    name = panel["panel"]
    with np.load(PRIVATE / f"truth_ledger_{name}.npz", allow_pickle=False) as stored:
        ledger = {key: stored[key] for key in stored.files}
    if panel_index == 0:
        x, sigma, truth = inputs["released_x"], inputs["released_sigma"], inputs["M0"]
    else:
        x = inputs["generated_x"][panel_index - 1].reshape(-1, 82)
        sigma = inputs["generated_sigma"][panel_index - 1].reshape(-1, 82)
        truth = inputs["generated_truth"][panel_index - 1].reshape(-1, 5)
    source_ids = panel["source_ids_fitted"]
    n, p = len(x), len(source_ids)
    coefficients = np.take(ledger["contributions"], source_ids, axis=2)
    covariance = np.take(np.take(ledger["covariance"], source_ids, axis=2), source_ids, axis=3)
    candidate_profiles = np.take(inputs["candidates"], source_ids, axis=1)
    predicted_x = np.einsum("nkp,kpj->nkj", coefficients, candidate_profiles)
    q_reference = np.sum(((x[:, None] - predicted_x) / sigma[:, None]) ** 2, axis=2)
    numeric = ledger["numeric"]
    assert np.allclose(q_reference[numeric], ledger["Q"][numeric], rtol=1e-10, atol=1e-10)
    tau = 1e-10 * np.maximum(1., np.max(np.abs(coefficients), axis=2))
    physical = np.all(coefficients >= -tau[:, :, None], axis=2)
    admitted_reference = numeric & physical & (q_reference <= chi2.ppf(.95, 82 - p))
    assert np.array_equal(admitted_reference, ledger["accepted"])
    admitted = ledger["accepted"]
    assert int(admitted.sum()) == panel["admissible_fits"]
    nonempty = admitted.any(axis=1)
    assert int((~nonempty).sum()) == panel["samples_without_admissible_fit"]
    q_selected = np.where(admitted, ledger["Q"], np.inf)
    selected = np.where(nonempty, q_selected.argmin(axis=1), -1)
    assert np.array_equal(selected, ledger["selected_index"])
    diagnostic = np.where(numeric.any(axis=1), np.where(numeric, ledger["Q"], np.inf).argmin(axis=1), -1)
    assert np.array_equal(diagnostic, ledger["diagnostic_index"])
    profile_w = candidate_profiles[None] / sigma[:, None, None, :]
    gram = np.einsum("nkpi,nkqi->nkpq", profile_w, profile_w)
    identity_product = np.einsum("nkij,nkjl->nkil", gram, covariance)
    assert np.allclose(identity_product[numeric], np.eye(p), rtol=1e-8, atol=1e-8)
    top = np.max(coefficients, axis=2, keepdims=True) - coefficients <= tau[:, :, None]
    bits = 1 << np.asarray(source_ids)
    top_masks = np.sum(top * bits, axis=2).astype(np.uint8)
    expected_point = np.zeros(n, np.uint8)
    expected_point[nonempty] = top_masks[np.where(nonempty)[0], selected[nonempty]]
    expected_union = np.bitwise_or.reduce(np.where(admitted, top_masks, 0), axis=1)
    assert np.array_equal(expected_point, ledger["predicted_masks"][0])
    assert np.array_equal(expected_union, ledger["predicted_masks"][1])
    truth_tau = 1e-10 * np.maximum(1., np.max(np.abs(truth), axis=1))
    true_tops = np.max(truth, axis=1, keepdims=True) - truth <= truth_tau[:, None]
    truth_masks = np.sum(true_tops * (1 << np.arange(5)), axis=1).astype(np.uint8)
    assert np.array_equal(truth_masks, ledger["truth_masks"])
    true_differences = np.asarray([truth[:, j] - truth[:, k] for j, k in PAIRS]).T
    true_signs = np.where(true_differences > truth_tau[:, None], 1,
                          np.where(true_differences < -truth_tau[:, None], -1, 0))
    assert np.array_equal(true_signs, ledger["truth_orders"])
    covariance_diagonal = np.diagonal(covariance, axis1=-2, axis2=-1)
    pair_variance = covariance_diagonal[:, :, :, None] + covariance_diagonal[:, :, None, :] - 2 * covariance
    difference = coefficients[:, :, :, None] - coefficients[:, :, None, :]
    for method_index, method in enumerate(panel["methods"]):
        if method["alpha"] is not None:
            z = norm.ppf(1 - method["alpha"] / (p * (p - 1)))
            halfwidth = z * np.sqrt(np.maximum(pair_variance, 0))
            candidates = np.all(difference + halfwidth >= -tau[:, :, None, None], axis=-1)
            candidate_masks = np.sum(candidates * bits, axis=2).astype(np.uint8)
            if method["family"] == "selected_joint_contrast":
                expected = np.zeros(n, np.uint8)
                expected[nonempty] = candidate_masks[np.where(nonempty)[0], selected[nonempty]]
            else:
                expected = np.bitwise_or.reduce(np.where(admitted, candidate_masks, 0), axis=1)
            assert np.array_equal(expected, ledger["predicted_masks"][method_index])
        predictions = ledger["predicted_masks"][method_index]
        size = np.asarray([int(mask).bit_count() for mask in predictions])
        single = size == 1
        wrong = single & ((predictions & truth_masks) == 0)
        covered = (predictions & truth_masks) == truth_masks
        assert int(single.sum()) == method["singletons"]
        assert int(wrong.sum()) == method["wrong_singletons"]
        assert int(covered.sum()) == method["truth_all_coleaders_covered"]
        assert int((size == 0).sum()) == method["empty_failures"]
        assert int(size.sum()) == method["set_size_sum"]
        assert method["all_pair_opportunities"] == n * 10
        assert method["fitted_pair_opportunities"] == n * p * (p - 1) // 2
        orders = ledger["orders"][method_index]
        assert int((orders != 0).sum()) == method["pair_declarations"]
        assert int(((orders != 0) & (orders != true_signs)).sum()) == method["false_pair_declarations"]
        if p == 4:
            assert np.all(predictions < 16)
            omitted_columns = [index for index, pair in enumerate(PAIRS) if 4 in pair]
            assert np.all(orders[:, omitted_columns] == 0)
    checks.append({"panel": name, "rows": n, "numerical_fits_verified": int(numeric.sum()),
                   "methods_verified": len(panel["methods"]), "status": "PASS"})

assert np.array_equal(inputs["generated_x"][0], inputs["generated_x"][3])
assert np.array_equal(inputs["generated_x"][0], inputs["generated_x"][4])
assert np.array_equal(inputs["generated_sigma"][3], .5 * inputs["generated_sigma"][0])
result = {"status": "PASS", "new_fits_or_parameter_changes": False,
          "scope": "Independent vectorized reconstruction of saved Q/covariance identities, admission, winners, point/contrast candidate sets, truth ties and aggregate denominators",
          "verified_rows": sum(check["rows"] for check in checks),
          "verified_numerical_fits": sum(check["numerical_fits_verified"] for check in checks),
          "panels": checks, "truth_results_sha256": hashlib.sha256((PUBLIC / "truth_results.json").read_bytes()).hexdigest()}
print(json.dumps(result, indent=2))
