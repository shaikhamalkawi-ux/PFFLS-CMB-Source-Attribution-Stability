"""Mathematical examples are constructed tests, never empirical JRC vectors."""

from decimal import Decimal
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_reference_robustness import (  # noqa: E402
    DEFAULT_DATA,
    build_report,
    finite_decimal,
    l1_distance,
    normalized_error_percent,
    radius_certificate,
    write_outputs,
)


class ReferenceRobustnessTests(unittest.TestCase):
    def test_percentage_points_not_fractions(self):
        result = radius_certificate("3.25", "2.27", "43.09", "0")
        self.assertEqual(Decimal(result["sufficient_open_ball_radius_ug_m3"]), Decimal("0.211141"))
        self.assertEqual(Decimal(result["sufficient_open_ball_radius_percent_reference_total"]), Decimal("0.49"))

    def test_full_display_unit_envelope(self):
        result = radius_certificate("3.25", "2.27", "43.09")
        self.assertEqual(Decimal(result["guaranteed_gap_lower_bound_pp"]), Decimal("0.96"))
        self.assertEqual(Decimal(result["sufficient_open_ball_radius_ug_m3"]), Decimal("0.206832"))

    def test_nearest_rounding_secondary_envelope(self):
        result = radius_certificate("3.25", "2.27", "43.09", "0.005")
        self.assertEqual(Decimal(result["guaranteed_gap_lower_bound_pp"]), Decimal("0.97"))
        self.assertEqual(Decimal(result["sufficient_open_ball_radius_ug_m3"]), Decimal("0.2089865"))

    def test_overlap_and_tie_fail_closed(self):
        for a, b in (("2", "2"), ("2", "2.01"), ("2", "2.02")):
            result = radius_certificate(a, b, "43.09")
            self.assertEqual(Decimal(result["sufficient_open_ball_radius_ug_m3"]), Decimal(0))
            self.assertFalse(result["strictly_positive_certificate"])

    def test_invalid_scalar_inputs_rejected(self):
        for args in (("-1", "1", "43.09"), ("1", "2", "0"), ("1", "2", "-3"), ("1", "2", "43.09", "-0.1"), ("NaN", "2", "43.09"), ("1", "Infinity", "43.09")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                radius_certificate(*args)
        with self.assertRaises(ValueError):
            finite_decimal("missing")

    def test_unit_scaling(self):
        base = radius_certificate("2", "4", "10", "0")
        scaled = radius_certificate("2", "4", "1000", "0")
        self.assertEqual(Decimal(scaled["sufficient_open_ball_radius_ug_m3"]), 100 * Decimal(base["sufficient_open_ball_radius_ug_m3"]))
        self.assertEqual(scaled["sufficient_open_ball_radius_percent_reference_total"], base["sufficient_open_ball_radius_percent_reference_total"])

    def test_strict_radius_endpoint_can_tie(self):
        reference, a, b = [1, 1], [1, 1], [3, 1]
        ea, eb = normalized_error_percent(a, reference), normalized_error_percent(b, reference)
        cert = radius_certificate(ea, eb, 2, 0)
        radius = Decimal(cert["sufficient_open_ball_radius_ug_m3"])
        endpoint = [2, 1]
        self.assertEqual(radius, Decimal(1))
        self.assertEqual(l1_distance(reference, endpoint), radius)
        self.assertEqual(l1_distance(a, endpoint), l1_distance(b, endpoint))
        inside, outside = [Decimal("1.99"), 1], [Decimal("2.01"), 1]
        self.assertLess(l1_distance(a, inside), l1_distance(b, inside))
        self.assertGreater(l1_distance(a, outside), l1_distance(b, outside))

    def test_two_lipschitz_constant_can_be_tight(self):
        a, b, original, shifted = [1, 1], [3, 1], [1, 1], [Decimal("1.3"), 1]
        d0 = l1_distance(a, original) - l1_distance(b, original)
        d1 = l1_distance(a, shifted) - l1_distance(b, shifted)
        self.assertEqual(abs(d1 - d0), 2 * l1_distance(original, shifted))

    def test_failed_certificate_does_not_imply_reversal(self):
        a, b, ref, shifted = [2], [3], [1], [Decimal("0.1")]
        cert = radius_certificate(normalized_error_percent(a, ref), normalized_error_percent(b, ref), 1, 0)
        self.assertGreater(l1_distance(ref, shifted), Decimal(cert["sufficient_open_ball_radius_ug_m3"]))
        self.assertLess(l1_distance(a, shifted), l1_distance(b, shifted))

    def test_positive_shared_normalization_preserves_ranking(self):
        a, b = [1, 1], [3, 1]
        for ref in ([1, 1], [Decimal("1.8"), 1], [3, 1]):
            raw_gap = l1_distance(a, ref) - l1_distance(b, ref)
            norm_gap = normalized_error_percent(a, ref) - normalized_error_percent(b, ref)
            self.assertEqual(raw_gap.compare(0), norm_gap.compare(0))
        with self.assertRaises(ValueError):
            normalized_error_percent(a, [0, 0])
        with self.assertRaises(ValueError):
            normalized_error_percent(a, [-3, 1])

    def test_dimension_and_missing_vectors_not_imputed(self):
        for a, b in (([], []), ([1], [1, 2]), ([1, None], [2, 3])):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                l1_distance(a, b)

    def test_constructed_eight_component_vectors(self):
        # Exact Decimal arithmetic and fixed seed; these are synthetic unit cases.
        rng = random.Random(20260926)
        for _ in range(500):
            a = [Decimal(rng.randrange(-20, 100)) / 10 for _ in range(8)]
            b = [Decimal(rng.randrange(-20, 100)) / 10 for _ in range(8)]
            r = [Decimal(rng.randrange(1, 100)) / 10 for _ in range(8)]
            q = [v + Decimal(rng.randrange(-5, 6)) / 10 for v in r]
            d0 = l1_distance(a, r) - l1_distance(b, r)
            d1 = l1_distance(a, q) - l1_distance(b, q)
            self.assertLessEqual(abs(d1 - d0), 2 * l1_distance(r, q))
            if 2 * l1_distance(r, q) < abs(d0):
                self.assertEqual(d0.compare(0), d1.compare(0))

    def test_precision_envelope_worst_case_lower_gap(self):
        # Conservative endpoints reduce the observed gap by two error bounds.
        result = radius_certificate("5", "4", "10", "0.1")
        actual_a = Decimal("4.9")
        actual_b = Decimal("4.1")
        self.assertEqual(actual_a - actual_b, Decimal(result["guaranteed_gap_lower_bound_pp"]))

    def test_archive_report_and_scope(self):
        report = build_report()
        self.assertEqual(len(report["edge_certificates"]), 30)
        self.assertEqual(sum(r["discordant_at_displayed_target"] for r in report["edge_certificates"]), 9)
        self.assertFalse(report["recomputed_from_raw"])
        self.assertFalse(report["baseline_modified"])
        self.assertFalse(report["availability"]["eight_component_fitted_mean_vectors_in_inspected_public_archive"])
        self.assertEqual(Decimal(report["all_thirty_orderings_certificate"]["sufficient_open_ball_radius_ug_m3"]), Decimal("0.047399"))
        self.assertEqual(Decimal(report["global_minimum_certificate"]["sufficient_open_ball_radius_ug_m3"]), Decimal("0.206832"))
        self.assertEqual(report["global_minimum_certificate"]["profile_set"], "W4-V2")
        self.assertTrue(all(len(item["sha256"]) == 64 for item in report["inputs"]))

    def test_scenario_certificates_are_nested_and_not_probabilities(self):
        scenarios = build_report()["scenario_budgets"]
        counts = [r["certified_unchanged_reference_orderings"] for r in scenarios]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertEqual(scenarios[0]["guaranteed_discordances_at_least"], 9)
        self.assertEqual(scenarios[0]["guaranteed_discordances_at_most"], 9)
        for scenario in scenarios:
            self.assertLessEqual(scenario["guaranteed_discordances_at_least"], 9)
            self.assertGreaterEqual(scenario["guaranteed_discordances_at_most"], 9)
            self.assertIn("not estimated", scenario["interpretation"])

    def test_missing_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(FileNotFoundError):
            build_report(Path(directory))

    def test_output_guard_protects_entire_frozen_archive(self):
        report = build_report()
        for destination in (DEFAULT_DATA.parent.parent, DEFAULT_DATA.parent,
                            DEFAULT_DATA, DEFAULT_DATA.parent / "new-output"):
            with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, "frozen archive"):
                write_outputs(report, destination)

    def test_output_guard_protects_custom_inputs_and_allows_separate_output(self):
        report = build_report()
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "source" / "derived_data"
            for destination in (data, data.parent / "new-output"):
                with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, "input tree"):
                    write_outputs(report, destination, data)
                self.assertFalse(destination.exists())
            destination = Path(directory) / "result"
            write_outputs(report, destination, data)
            self.assertTrue((destination / "REFERENCE_ROBUSTNESS.md").is_file())
            self.assertEqual(json.loads((destination / "reference_robustness.json").read_text(encoding="utf-8")), report)

    def test_committed_json_matches_builder(self):
        saved = json.loads((ROOT / "outputs/strengthening_20260926/reference_robustness.json").read_text(encoding="utf-8"))
        generated = build_report()
        # Runtime version can differ between independent standard-library reruns.
        saved.pop("software")
        generated.pop("software")
        self.assertEqual(saved, generated)


if __name__ == "__main__":
    unittest.main()
