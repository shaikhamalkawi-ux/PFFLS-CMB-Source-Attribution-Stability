"""Synthetic tests only; never reads the original bootstrap ledgers."""
import ast
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_truth_bootstrap as v


class BootstrapReplayTests(unittest.TestCase):
    def test_mask_counts_include_empty_ambiguous_and_tied_truth(self):
        counts = v.cluster_counts([[0, 1, 3, 2]], [1, 3, 3, 1], [0, 0, 1, 1])
        self.assertEqual(counts.tolist(), [[[2, 1, 0, 0], [2, 1, 1, 1]]])

    def test_wrong_singleton_is_not_all_true_ties_coverage(self):
        self.assertEqual(v.cluster_counts([[1]], [3], [0]).tolist(), [[[1, 1, 0, 0]]])

    def test_bad_masks_groups_and_dimensions_fail(self):
        for masks, truth, groups in [([[32]], [1], [0]), ([[-1]], [1], [0]),
                                     ([[1]], [0], [0]), ([[1]], [1], [2]),
                                     ([[1.0]], [1], [0]), ([[1, 2]], [1], [0])]:
            with self.assertRaises(ValueError):
                v.cluster_counts(masks, truth, groups)

    def test_zero_singletons_are_undefined_not_zero_risk(self):
        rates = v.resampled_rates(np.array([[[3, 0, 0, 0], [3, 0, 0, 0]]]), 17, 4)
        self.assertTrue(np.isnan(rates[:, :, 1]).all())
        self.assertEqual(v.percentile_summary(rates[0, :, 1]),
                         {"lower": None, "upper": None, "defined_resamples": 0, "total_resamples": 17})

    def test_identical_methods_share_every_resample(self):
        counts = np.array([[[2, 1, 0, 1], [2, 2, 1, 2]]] * 2)
        rates = v.resampled_rates(counts, 91, 123)
        np.testing.assert_array_equal(rates[0], rates[1])
        self.assertEqual(v.percentile_summary(rates[0, :, 0] - rates[1, :, 0])["upper"], 0)

    def test_replay_deterministic(self):
        counts = np.array([[[2, 1, 0, 1], [2, 2, 1, 2]]])
        np.testing.assert_array_equal(v.resampled_rates(counts, 32, 123), v.resampled_rates(counts, 32, 123))

    def test_paired_risk_uses_intersection_of_defined_resamples(self):
        left = np.array([0., np.nan, 0., 1.])
        right = np.array([np.nan, 0., 1., 0.])
        result = v.percentile_summary(left - right)
        self.assertEqual(result["total_resamples"], 4)
        self.assertEqual(result["defined_resamples"], 2)
        self.assertAlmostEqual(result["lower"], -.95)
        self.assertAlmostEqual(result["upper"], .95)

    def test_type_seven_interpolation_and_nonfinite_filter(self):
        self.assertEqual(v.percentile_summary([0, 1, float("nan")]),
                         {"lower": .025, "upper": .975, "defined_resamples": 2, "total_resamples": 3})
        self.assertEqual(v.percentile_summary([7])["lower"], 7)

    def test_mismatch_tampering_and_undefined_rejected(self):
        a = v.percentile_summary([0, 1])
        self.assertEqual(v.compare_interval(a, a), 0)
        for key, value in [("lower", .25), ("upper", None), ("defined_resamples", 0),
                           ("total_resamples", 3), ("upper", float("inf"))]:
            b = dict(a, **{key: value})
            with self.assertRaises(ValueError):
                v.compare_interval(a, b)

    def test_no_producer_or_solver_import_or_quantile_call(self):
        tree = ast.parse(Path(v.__file__).read_text())
        imported = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        imported += [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any(name.startswith(("audit_", "scipy")) for name in imported))
        self.assertFalse(any(isinstance(node, ast.Attribute) and node.attr in ("quantile", "percentile", "linprog")
                             for node in ast.walk(tree)))


if __name__ == "__main__":
    unittest.main()
