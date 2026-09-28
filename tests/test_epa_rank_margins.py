"""New artificial fixtures only: no EPA inputs, original solver or old tests."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import summarize_epa_rank_margins as margins


SAMPLE = {"ID": "INVENTED", "DATE": "01/01/00", "DUR": "24", "STHOUR": "0", "SIZE": "FINE"}


def invented_fixture():
    config = {"central_initial_sources": ["A", "B", "C"], "expected_receptor_count": 1,
              "expected_alternatives": {"A": ["X", "Y"]}, "ranking_rounding_check_decimals": 5}
    def fit(vector, converged=True):
        return {"source_ids": list(vector), "source_contributions": vector, "converged": converged,
                "R2": 0.9, "reduced_chi2": 2.0, "percent_mass": 100.0,
                "terminal_iterate_not_accepted_outcome_if_nonconverged": not converged}
    control = fit({"A": 10.0, "B": 8.0, "C": 1.0})
    control.update(controller_status="COMPLETE_NONNEGATIVE", central_removal_history=[])
    accepted = fit({"X": 0.0, "B": 7.0, "C": 11.0})
    mapped = {"A": 0.0, "B": 7.0, "C": 11.0}
    row = {"sample": SAMPLE, "central_slot": "A", "alternative": "X", "result": accepted,
           "ranking": margins.ranking(control["source_contributions"], mapped),
           "ranking_rounded": margins.ranking(control["source_contributions"], mapped, 5),
           "two_diagnostic": True, "three_diagnostic": True}
    unresolved = {"sample": SAMPLE, "central_slot": "A", "alternative": "Y",
                  "result": fit({"Y": 3.0, "B": -2.0, "C": 1.0}, False)}
    ledger = {"full_runs": {"central_runs": [{"sample": SAMPLE, "result": control}],
                            "substitutions": [row, unresolved]}}
    expected = {"eligible": 2, "converged": 1, "nonconverged": 1, "two_diagnostic": 1,
                "three_diagnostic": 1, "ordering_converged": 1, "largest_converged": 1,
                "ordering_two_diagnostic": 1, "largest_two_diagnostic": 1,
                "ordering_three_diagnostic": 1, "largest_three_diagnostic": 1}
    return ledger, config, {margins.sample_key(SAMPLE): 20.0}, expected


class ArtificialMarginTests(unittest.TestCase):
    def test_reversal_cross_pair_is_not_top_two_pair(self):
        value = margins.margin_values({"A": 10., "B": 8., "C": 1.},
                                      {"A": 0., "B": 7., "C": 11.}, 20., "A")["metrics"]
        expected = {"central_top_two_gap_ug_m3": 2., "alternative_top_two_gap_ug_m3": 4.,
                    "cross_before_ug_m3": 9., "cross_after_ug_m3": 11.,
                    "old_minus_new_before_ug_m3": 9., "old_minus_new_after_ug_m3": -11.,
                    "cross_swing_ug_m3": 20., "cross_min_ug_m3": 9.,
                    "central_top_two_gap_pct_ambient_pm": 10., "allocation_L1_change_ug_m3": 21.}
        for key, wanted in expected.items():
            self.assertEqual(value[key], wanted, key)

    def test_unchanged_winner_has_null_cross_fields_and_signed_changes(self):
        result = margins.margin_values({"A": 10., "B": 8., "C": 1.},
                                       {"A": 12., "B": 7., "C": -1.}, 20., "C")
        self.assertEqual(result["source_delta_ug_m3"], {"A": 2., "B": -1., "C": -2.})
        self.assertEqual(result["metrics"]["allocation_L1_change_ug_m3"], 5.)
        self.assertEqual(result["metrics"]["substituted_delta_pct_ambient_pm"], -10.)
        for key in margins.CROSS:
            self.assertIsNone(result["metrics"][key + "_ug_m3"])

    def test_top_tie_not_broken_and_runner_ties_preserved(self):
        self.assertEqual(margins.top_two({"A": 4., "B": 4., "C": 1.})["gap"], 0.)
        self.assertEqual(margins.top_two({"A": 4., "B": 1., "C": 1.})["runners_up"], ["B", "C"])
        with self.assertRaisesRegex(ValueError, "top tie"):
            margins.margin_values({"A": 4., "B": 4.}, {"A": 4., "B": 1.}, 10., "A")

    def test_source_mnemonic_maps_to_central_slot(self):
        ledger, _, _, _ = invented_fixture()
        control = ledger["full_runs"]["central_runs"][0]["result"]
        result = ledger["full_runs"]["substitutions"][0]["result"]
        self.assertEqual(margins.mapped_vector(control, result, "A", "X"), {"A": 0., "B": 7., "C": 11.})
        result["source_ids"] = ["X", "A", "C"]
        result["source_contributions"] = {"X": 0., "A": 7., "C": 11.}
        with self.assertRaises(ValueError):
            margins.mapped_vector(control, result, "A", "X")

    def test_nonconverged_row_retained_with_null_outcomes(self):
        ledger, config, masses, expected = invented_fixture()
        summary, private = margins.analyze(ledger, config, masses, expected)
        self.assertEqual(len(private["substitutions"]), 2)
        self.assertIsNone(private["substitutions"][1]["derived"])
        self.assertEqual(summary["counts"], expected)
        for group in margins.GROUPS:
            self.assertEqual(summary["groups"][group]["substitutions"], 1)
            self.assertEqual(summary["groups"][group]["unique_samples"], 1)
        self.assertNotIn("central_runs", summary)
        self.assertNotIn("source_delta_ug_m3", summary)

    def test_incomplete_eligibility_universe_rejected(self):
        ledger, config, masses, expected = invented_fixture()
        ledger["full_runs"]["substitutions"].pop()
        with self.assertRaisesRegex(ValueError, "incomplete substitution"):
            margins.validate_ledger(ledger, config, masses, expected)

    def test_duplicate_key_rejected_even_with_unchanged_row_count(self):
        ledger, config, masses, expected = invented_fixture()
        ledger["full_runs"]["substitutions"][1] = deepcopy(ledger["full_runs"]["substitutions"][0])
        with self.assertRaisesRegex(ValueError, "duplicate or ineligible"):
            margins.validate_ledger(ledger, config, masses, expected)

    def test_missing_join_invalid_mass_and_extra_join_rejected(self):
        ledger, config, masses, expected = invented_fixture()
        for candidate in ({}, {next(iter(masses)): 0.}, {**masses, ("OTHER", "x", "x", "x", "x"): 20.}):
            with self.subTest(candidate_size=len(candidate)), self.assertRaises(ValueError):
                margins.validate_ledger(ledger, config, candidate, expected)
        for value in (0., -1., float("inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                margins.margin_values({"A": 2., "B": 1.}, {"A": 3., "B": 1.}, value, "A")

    def test_native_identity_duplicate_and_incomplete_rows_rejected(self):
        header = "ID DATE DUR STHOUR SIZE TMAC\n"
        line = "INVENTED 01/01/00 24 0 FINE 20\n"
        receptor_filter = {"ID": "INVENTED", "SIZE": "FINE"}
        self.assertEqual(margins.parse_masses((header + line).encode(), receptor_filter), {margins.sample_key(SAMPLE): 20.})
        for text in (header + line + line, header + "INVENTED 01/01/00 24 0 FINE\n", header + line.replace("20", "0")):
            with self.assertRaises(ValueError):
                margins.parse_masses(text.encode(), receptor_filter)

    def test_original_filter_boundaries_remain_inclusive(self):
        for r2, chi, mass in ((0.8, 0., 80.), (1., 4., 120.)):
            self.assertTrue(margins.targets({"converged": True, "R2": r2, "reduced_chi2": chi, "percent_mass": mass}, True))
        self.assertFalse(margins.targets({"converged": True, "R2": 0.799999999999, "reduced_chi2": 0., "percent_mass": 100.}))

    def test_saved_mask_and_ranking_mismatches_rejected(self):
        for field in ("two_diagnostic", "ranking"):
            ledger, config, masses, expected = invented_fixture()
            row = ledger["full_runs"]["substitutions"][0]
            if field == "ranking":
                row[field]["largest_source_change"] = False
            else:
                row[field] = False
            with self.subTest(field=field), self.assertRaises(ValueError):
                margins.validate_ledger(ledger, config, masses, expected)

    def test_source_removal_and_vector_key_mismatches_rejected(self):
        ledger, config, masses, expected = invented_fixture()
        control = ledger["full_runs"]["central_runs"][0]["result"]
        control["central_removal_history"] = [{"removed_source": "C", "negative_contribution": -1.}]
        with self.assertRaisesRegex(ValueError, "recorded removals"):
            margins.validate_ledger(ledger, config, masses, expected)
        control["source_ids"] = ["A", "B"]
        with self.assertRaisesRegex(ValueError, "contribution keys"):
            margins.contribution_vector(control)

    def test_small_group_quantiles_are_fixed_linear_interpolation(self):
        self.assertEqual(margins.descriptive([0., 10.]), {"n": 2, "min": 0., "p10": 1., "median": 5., "p90": 9., "max": 10.})
        self.assertIsNone(margins.descriptive([])["median"])
        self.assertEqual(margins.descriptive([7.])["p90"], 7.)

    def test_duplicate_json_keys_and_nonfinite_constants_rejected(self):
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.assertRaises(ValueError):
                margins.decode_json(payload)

    def test_private_public_path_separation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public = root / "outputs/continuous_research_20260927/editor_response_20260928"
            private = root / "private/editor_response_20260928/epa_margins"
            margins.validate_paths(public, private, [root / "inputs/input.json"], root)
            with self.assertRaises(ValueError):
                margins.validate_paths(public, public / "full_vectors", [], root)
            with self.assertRaises(ValueError):
                margins.validate_paths(public, private, [private / "old_ledger.json"], root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
