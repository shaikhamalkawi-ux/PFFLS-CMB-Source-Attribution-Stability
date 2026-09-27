"""Synthetic-only analytic-reference tests. No released archive is read."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.stats import chi2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_truth_decisions as audit


def orthogonal_profiles():
    # Each normalized source contributes to two disjoint channels.
    return np.concatenate((np.eye(5), np.eye(5)), axis=1) / 2


def synthetic_fit(index, values, q=1.0, accepted=True, covariance=None):
    values = np.asarray(values, float)
    return {"index": index, "values": values, "q": q, "accepted": accepted,
            "numeric": True, "flags": [] if accepted else ["negative_contribution"],
            "tiny_negative": False, "covariance": np.eye(len(values)) if covariance is None else covariance}


class ScaleAndStorageTests(unittest.TestCase):
    def test_compensated_normalization_preserves_forward_signal(self):
        f = orthogonal_profiles() * np.arange(1, 6)[:, None]
        g = np.arange(1, 16, dtype=float).reshape(3, 5)
        p, m = audit.compensated_profile(f, g)
        np.testing.assert_allclose(p.sum(axis=1), 1)
        np.testing.assert_allclose(m @ p, g @ f, atol=1e-12)

    def test_source_specific_scale_invariance(self):
        f = orthogonal_profiles()
        g = np.array([[2., 3., 1., 4., 2.]])
        scale = np.array([0.5, 2, 3, 4, .25])
        p, m = audit.compensated_profile(f, g)
        p2, m2 = audit.compensated_profile(f * scale[:, None], g / scale)
        np.testing.assert_allclose(p, p2)
        np.testing.assert_allclose(m, m2)
        self.assertEqual(audit.top_mask(m[0]), audit.top_mask(m2[0]))
        self.assertNotEqual(audit.top_mask(g[0]), audit.top_mask((g / scale)[0]))

    def test_invalid_generating_profile_rejected(self):
        f = orthogonal_profiles()
        f[2] = 0
        with self.assertRaises(ValueError):
            audit.compensated_profile(f, np.ones((2, 5)))

    def test_array_hash_sensitive_to_shape_dtype_and_value(self):
        data = np.arange(6, dtype=np.float64)
        self.assertNotEqual(audit.array_hash(data), audit.array_hash(data.reshape(2, 3)))
        self.assertNotEqual(audit.array_hash(data), audit.array_hash(data.astype(np.float32)))
        changed = data.copy(); changed[0] = 1
        self.assertNotEqual(audit.array_hash(data), audit.array_hash(changed))

    def test_object_arrays_forbidden(self):
        with self.assertRaises(ValueError):
            audit.array_hash(np.asarray([{}], dtype=object))

    def test_immutable_file_refuses_change(self):
        with tempfile.TemporaryDirectory(prefix="truth_test_") as directory:
            path = Path(directory) / "truth_test.bin"
            audit.immutable_write(path, b"original")
            audit.immutable_write(path, b"original")
            with self.assertRaises(ValueError):
                audit.immutable_write(path, b"different")
            self.assertEqual(path.read_bytes(), b"original")

    def test_stale_test_gate_rejected(self):
        with tempfile.TemporaryDirectory(prefix="truth_test_") as directory:
            path = Path(directory)
            audit.immutable_write(path / "truth_test_gate.json", audit.json_bytes({"passed": True, "tests_run": 25, "hashes": {"script": "before"}}))
            with patch.object(audit, "implementation_hashes", return_value={"script": "after"}):
                with self.assertRaises(ValueError):
                    audit.validate_gate(path)

    def test_frozen_archive_and_individual_array_tamper_detected(self):
        with tempfile.TemporaryDirectory(prefix="truth_test_") as directory:
            path = Path(directory)
            hashes = {"script": "synthetic"}
            gate = audit.json_bytes({"passed": True, "tests_run": 25, "hashes": hashes})
            audit.immutable_write(path / "truth_test_gate.json", gate)
            config = audit.json_bytes({"config": audit.CONFIG, "hashes": hashes, "test_gate_sha256": audit.sha(gate)})
            audit.immutable_write(path / "truth_configuration_frozen.json", config)
            data = np.arange(4, dtype=float)
            buffer = BytesIO(); np.savez_compressed(buffer, data=data)
            payload = buffer.getvalue()
            audit.immutable_write(path / "truth_frozen_arrays.npz", payload)
            manifest = {"configuration_sha256": audit.sha(config), "frozen_array_file": "truth_frozen_arrays.npz",
                        "frozen_array_file_sha256": audit.sha(payload),
                        "arrays": {"data": {"shape": [4], "dtype": data.dtype.str, "sha256": audit.array_hash(data)}}}
            (path / "truth_input_freeze.json").write_bytes(audit.json_bytes(manifest))
            with patch.object(audit, "implementation_hashes", return_value=hashes):
                audit.verify_frozen(path)
                manifest["arrays"]["data"]["sha256"] = "wrong"
                (path / "truth_input_freeze.json").write_bytes(audit.json_bytes(manifest))
                with self.assertRaisesRegex(ValueError, "frozen array changed"):
                    audit.verify_frozen(path)
                manifest["frozen_array_file_sha256"] = "wrong"
                (path / "truth_input_freeze.json").write_bytes(audit.json_bytes(manifest))
                with self.assertRaisesRegex(ValueError, "archive mismatch"):
                    audit.verify_frozen(path)


class SolverAndAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.p = orthogonal_profiles()
        self.truth = np.arange(3., 8.)
        self.sigma = np.linspace(.7, 1.6, 10)
        self.y = self.p.T @ self.truth + np.linspace(-.05, .05, 10)

    def test_native_adapter_matches_independent_closed_form(self):
        fit = audit.fit_family(self.y, self.sigma, self.p[None])[0]
        self.assertTrue(fit["accepted"])
        # Analytic disjoint-channel WLS: no shared implementation with native solver.
        denominator = .25 * (1 / self.sigma[:5] ** 2 + 1 / self.sigma[5:] ** 2)
        reference = .5 * (self.y[:5] / self.sigma[:5] ** 2 + self.y[5:] / self.sigma[5:] ** 2) / denominator
        np.testing.assert_allclose(fit["values"], reference, atol=1e-12)
        np.testing.assert_allclose(fit["covariance"], np.diag(1 / denominator), atol=1e-12)
        q = sum(((self.y - self.p.T @ reference) / self.sigma) ** 2)
        self.assertAlmostEqual(fit["q"], q, places=12)

    def test_absolute_sigma_not_empirical_residual_rescale(self):
        a = audit.fit_family(self.y, self.sigma, self.p[None])[0]
        b = audit.fit_family(self.y, self.sigma * 2, self.p[None])[0]
        np.testing.assert_allclose(a["values"], b["values"], atol=1e-12)
        np.testing.assert_allclose(b["covariance"], 4 * a["covariance"], atol=1e-12)
        self.assertAlmostEqual(b["q"], a["q"] / 4, places=12)

    def test_negative_coefficients_exclude_entire_fit_without_clipping(self):
        beta = np.array([-1., 3., 4., 5., 6.])
        fit = audit.fit_family(self.p.T @ beta, self.sigma, self.p[None])[0]
        self.assertTrue(fit["numeric"])
        self.assertFalse(fit["accepted"])
        self.assertIn("negative_contribution", fit["flags"])
        self.assertLess(fit["values"][0], -.99)

    def test_negative_boundary_inclusive_and_no_clipping(self):
        values = np.array([-1e-10, 0., 0., 0., 0.])
        original = values.copy()
        accepted, flags, tiny = audit.admit_fit(values, 0., 10.)
        self.assertTrue(accepted); self.assertTrue(tiny); self.assertFalse(flags)
        np.testing.assert_array_equal(values, original)
        values[0] = np.nextafter(-1e-10, -np.inf)
        self.assertFalse(audit.admit_fit(values, 0., 10.)[0])

    def test_q_gate_boundary_inclusive(self):
        cutoff = chi2.ppf(.95, 5)
        self.assertTrue(audit.admit_fit(np.ones(5), cutoff, cutoff)[0])
        flags = audit.admit_fit(np.ones(5), np.nextafter(cutoff, np.inf), cutoff)[1]
        self.assertEqual(flags, ["q_rejected"])

    def test_all_applicable_admission_flags_retained(self):
        _, flags, _ = audit.admit_fit(np.array([-1., 2., 2.]), 100., 1., converged=False, covariance_valid=False)
        self.assertEqual(flags, ["nonconverged", "invalid_covariance", "negative_contribution", "q_rejected"])

    def test_invalid_sigma_zero_negative_nan_infinity(self):
        for bad in [0., -1., np.nan, np.inf]:
            sigma = self.sigma.copy(); sigma[0] = bad
            fit = audit.fit_family(self.y, sigma, self.p[None])[0]
            self.assertFalse(fit["accepted"])
            self.assertEqual(fit["flags"], ["invalid_input"])

    def test_nonfinite_observation_and_profile(self):
        y = self.y.copy(); y[0] = np.nan
        self.assertEqual(audit.fit_family(y, self.sigma, self.p[None])[0]["flags"], ["invalid_input"])
        p = self.p.copy(); p[0, 0] = np.inf
        self.assertEqual(audit.fit_family(self.y, self.sigma, p[None])[0]["flags"], ["invalid_input"])

    def test_rank_deficiency_not_repaired(self):
        p = self.p.copy(); p[1] = p[0]
        fit = audit.fit_family(self.y, self.sigma, p[None])[0]
        self.assertFalse(fit["numeric"])
        self.assertIn("rank_deficient", fit["flags"])

    def test_native_zero_observation_guard_is_explicit_failure(self):
        fit = audit.fit_family(np.zeros(10), self.sigma, self.p[None])[0]
        self.assertFalse(fit["accepted"])
        self.assertEqual(fit["flags"], ["numerical_exception"])

    def test_nonfinite_fit_not_admitted(self):
        self.assertFalse(audit.admit_fit(np.array([1., np.nan]), 1., 10.)[0])
        self.assertFalse(audit.admit_fit(np.ones(2), np.inf, 10.)[0])


class DecisionTests(unittest.TestCase):
    def test_coleader_ties_are_not_arbitrarily_broken(self):
        values = np.array([3., 3. - 1e-11, 1., 0., 0.])
        self.assertEqual(audit.top_mask(values), 3)

    def test_covariance_terms_change_contrast_decision(self):
        values = np.array([2., 1.])
        correlated = np.array([[1., .9], [.9, 1.]])
        mask, signs = audit.joint_contrast_decision(values, correlated, (0, 1), .05)
        self.assertEqual(mask, 1)
        self.assertEqual(signs[0], 1)
        uncorrelated_mask, _ = audit.joint_contrast_decision(values, np.eye(2), (0, 1), .05)
        self.assertEqual(uncorrelated_mask, 3)

    def test_invalid_contrast_variance_rejected(self):
        with self.assertRaises(ValueError):
            audit.contrast_variance(np.array([[1., 2.], [2., 1.]]))
        cancellation = np.array([[1., 1. + 1e-14], [1. + 1e-14, 1.]])
        self.assertEqual(audit.contrast_variance(cancellation)[0, 1], 0.)

    def test_bad_alpha_and_nonfinite_covariance(self):
        for alpha in [0., 1., -1.]:
            with self.assertRaises(ValueError):
                audit.joint_contrast_decision(np.ones(2), np.eye(2), (0, 1), alpha)
        with self.assertRaises(ValueError):
            audit.contrast_variance(np.full((2, 2), np.nan))

    def test_near_numerical_tie_contained_even_with_tiny_covariance(self):
        values = np.array([1., 1. - .5e-10])
        point = audit.top_mask(values, (0, 1))
        mask, _ = audit.joint_contrast_decision(values, np.eye(2) * 1e-30, (0, 1), .5)
        self.assertEqual(point, 3)
        self.assertEqual(point & ~mask, 0)

    def test_numerical_pre_gate_and_admissible_winner_separate(self):
        fits = [synthetic_fit(0, [-1, 5, 4, 2, 1], q=.1, accepted=False),
                synthetic_fit(1, [7, 5, 4, 2, 1], q=2.)]
        result = audit.family_decisions(fits, audit.ALL_IDS)
        self.assertEqual(result["diagnostic_index"], 0)
        self.assertEqual(result["selected_index"], 1)
        self.assertEqual(result["diagnostic_mask"], 2)
        self.assertEqual(result["masks"][0], 1)

    def test_equal_Q_profile_index_tie_break(self):
        fits = [synthetic_fit(3, [1, 5, 4, 2, 1], q=1.), synthetic_fit(1, [7, 5, 4, 2, 1], q=1.)]
        result = audit.family_decisions(fits, audit.ALL_IDS)
        self.assertEqual(result["selected_index"], 1)

    def test_all_rejected_is_failure_not_successful_abstention(self):
        fits = [synthetic_fit(0, [-1, 5, 4, 2, 1], accepted=False)]
        result = audit.family_decisions(fits, audit.ALL_IDS)
        self.assertTrue(np.all(result["masks"] == 0))
        self.assertTrue(np.all(result["orders"] == 0))
        counts = audit.metric_counts(np.array([0]), np.array([2]), np.zeros((1, 10)), np.zeros((1, 10)), 10)
        metrics = audit.metrics_from_counts(counts)
        self.assertEqual(metrics["truth_all_coleaders_covered"], 0)
        self.assertEqual(metrics["empty_failures"], 1)
        self.assertIsNone(metrics["wrong_singleton_risk"])

    def test_subset_invariant_random_families(self):
        rng = np.random.default_rng(81)
        for _ in range(12):
            fits = []
            for index in range(4):
                a = rng.normal(size=(5, 5))
                fits.append(synthetic_fit(index, rng.uniform(.1, 5, 5), q=4-index,
                                          covariance=a @ a.T + np.eye(5) * .001))
            result = audit.family_decisions(fits, audit.ALL_IDS)
            self.assertEqual(result["subset_checks"], 12)
            for index, method in enumerate(audit.METHODS):
                if method["family"] == "union_joint_contrast":
                    self.assertEqual(int(result["masks"][1]) & ~int(result["masks"][index]), 0)

    def test_contrast_sets_expand_at_stricter_alpha(self):
        values = np.array([3., 2., 1., .5, .2])
        previous = 0
        for alpha in audit.ALPHAS:
            mask, _ = audit.joint_contrast_decision(values, np.eye(5) * .2, audit.ALL_IDS, alpha)
            self.assertEqual(previous & ~mask, 0)
            previous = mask

    def test_truth_set_requires_all_coleaders_but_singleton_member_not_wrong(self):
        predictions = np.array([1, 4, 3], dtype=np.uint8)
        truth = np.array([3, 3, 3], dtype=np.uint8)
        counts = audit.metric_counts(predictions, truth, np.zeros((3, 10)), np.zeros((3, 10)), 10)
        self.assertEqual(counts["singletons"], 2)
        self.assertEqual(counts["wrong_singletons"], 1)
        self.assertEqual(counts["truth_all_coleaders_covered"], 1)

    def test_omitted_source_uses_five_truth_ids_and_ten_pairs(self):
        values = np.array([4., 3., 2., 1.])
        orders = audit.declared_pair_signs(values, (0, 1, 2, 3))[None]
        true_values = np.array([4., 3., 2., 1., 5.])
        true_orders = audit.declared_pair_signs(true_values, audit.ALL_IDS)[None]
        counts = audit.metric_counts(np.array([1]), np.array([16]), orders, true_orders, 6)
        self.assertEqual(counts["all_pair_opportunities"], 10)
        self.assertEqual(counts["fitted_pair_opportunities"], 6)
        self.assertEqual(counts["pair_declarations"], 6)
        self.assertEqual(counts["wrong_singletons"], 1)
        self.assertEqual(counts["truth_all_coleaders_covered"], 0)

    def test_strict_order_against_true_tie_is_false(self):
        order = np.zeros((1, 10), dtype=np.int8); order[0, 0] = 1
        counts = audit.metric_counts(np.array([1]), np.array([3]), order, np.zeros((1, 10)), 10)
        self.assertEqual(counts["false_pair_declarations"], 1)

    def test_empty_predictions_not_credited_for_small_set_size(self):
        counts = audit.metric_counts(np.array([0, 3]), np.array([1, 1]), np.zeros((2, 10)), np.zeros((2, 10)), 10)
        metrics = audit.metrics_from_counts(counts)
        self.assertEqual(metrics["mean_set_size_all_samples"], 1.)
        self.assertEqual(metrics["mean_set_size_nonempty"], 2.)
        self.assertEqual(metrics["truth_in_set_all_coleaders_coverage"], .5)


class GeneratorAndPanelTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(9)
        self.p = rng.uniform(.1, 1, (5, 8)); self.p /= self.p.sum(axis=1)[:, None]
        self.m = rng.uniform(1., 5., (6, 5))
        self.sigma = rng.uniform(.1, .4, (6, 8))
        self.config = {**audit.CONFIG, "generated_rows": [0, 2, 4], "replicates": 2}

    def test_generator_reproducible_and_common_profile_mass_scale(self):
        a, states_a = audit.generate_controls(self.p, self.m, self.sigma, self.config)
        b, states_b = audit.generate_controls(self.p, self.m, self.sigma, self.config)
        self.assertEqual(states_a, states_b)
        for name in a:
            np.testing.assert_array_equal(a[name], b[name])
        np.testing.assert_allclose(a["candidates"].sum(axis=2), 1)
        self.assertEqual(a["candidates"].shape, (9, 5, 8))

    def test_generator_uses_shared_noise_and_predeclared_misspecification(self):
        out, _ = audit.generate_controls(self.p, self.m, self.sigma, self.config)
        x, sigma, truth = out["generated_x"], out["generated_sigma"], out["generated_truth"]
        np.testing.assert_array_equal(x[0], x[3])
        np.testing.assert_array_equal(x[0], x[4])
        np.testing.assert_array_equal(sigma[3], .5 * sigma[0])
        np.testing.assert_array_equal(truth[0], truth[1])
        expected_correlation_noise = np.sqrt(.5) * (out["noise_a"][:, :, None] + out["noise_z"])
        np.testing.assert_allclose(x[2], truth[2] @ self.p + sigma[2] * expected_correlation_noise)
        np.testing.assert_allclose(truth[5, :, :, 1], .99 * truth[5, :, :, 0])
        self.assertTrue(np.all(np.argmax(truth[5], axis=2) == 0))

    def test_generator_preserves_negative_observations_without_redraw(self):
        large_sigma = self.sigma * 1e6
        out, _ = audit.generate_controls(self.p, self.m, large_sigma, self.config)
        self.assertTrue(np.any(out["generated_x"] < 0))
        expected = out["generated_truth"][0] @ self.p + large_sigma[[0, 2, 4]][None] * out["noise_z"]
        np.testing.assert_array_equal(out["generated_x"][0], expected)

    def test_generator_never_calls_fit_or_decision_scoring(self):
        with patch.object(audit, "fit_family", side_effect=AssertionError("leak")), \
             patch.object(audit, "top_mask", side_effect=AssertionError("leak")), \
             patch.object(audit.native, "effective_variance_fit", side_effect=AssertionError("leak")):
            audit.generate_controls(self.p, self.m, self.sigma, self.config)

    def test_generator_rejects_invalid_uncertainty_or_scale(self):
        sigma = self.sigma.copy(); sigma[0, 0] = 0
        with self.assertRaises(ValueError):
            audit.generate_controls(self.p, self.m, sigma, self.config)
        with self.assertRaises(ValueError):
            audit.generate_controls(self.p * 2, self.m, self.sigma, self.config)

    def test_complete_tiny_synthetic_panel_has_consistent_denominators(self):
        p = orthogonal_profiles()
        truth = np.array([[3., 2., 1., .5, .1], [.1, .5, 1., 2., 3.]])
        x = truth @ p
        report, ledger = audit.evaluate_panel("synthetic_unit", x, np.ones_like(x) * .01, truth, p[None], audit.ALL_IDS, np.zeros(2, dtype=int))
        self.assertEqual(report["fit_attempts"], 2)
        self.assertEqual(report["admissible_fits"], 2)
        self.assertEqual(report["subset_invariant_checks_passed"], 24)
        self.assertEqual(report["methods"][0]["singletons"], 2)
        self.assertEqual(report["methods"][0]["wrong_singletons"], 0)
        self.assertTrue(np.all(ledger["accepted"]))

    def test_paired_bootstrap_has_null_risk_when_no_singletons(self):
        counts = audit.metric_counts(np.array([31, 31]), np.array([1, 2]), np.zeros((2, 10)), np.zeros((2, 10)), 10)
        report = audit.bootstrap_paired([[dict(counts), dict(counts)] for _ in audit.METHODS])
        risk = report["marginal_percentile_intervals"]["selected_point"]["wrong_singleton_risk"]
        self.assertIsNone(risk["lower"])
        self.assertEqual(risk["defined_resamples"], 0)
        for comparison in report["paired_differences"]:
            self.assertEqual(comparison["singleton_coverage_difference"]["lower"], 0.)
            self.assertEqual(comparison["singleton_coverage_difference"]["upper"], 0.)


if __name__ == "__main__":
    unittest.main()
