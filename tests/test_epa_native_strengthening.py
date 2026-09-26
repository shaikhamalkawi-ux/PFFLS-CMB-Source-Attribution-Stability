"""Synthetic tests always run; native integrations require the official archives."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_epa_native_strengthening as epa  # noqa: E402


def synthetic_problem():
    receptor = {"AC": "2", "AU": "1", "BC": "3", "BU": "1", "CC": "5", "CU": "1", "TMAC": "10"}
    profiles = {
        "X": {"AC": "1", "AU": "0", "BC": "0", "BU": "0", "CC": "1", "CU": "0"},
        "Y": {"AC": "0", "AU": "0", "BC": "1", "BU": "0", "CC": "1", "CU": "0"},
    }
    return receptor, profiles, ["AC", "BC", "CC"]


class EPANativeSyntheticTests(unittest.TestCase):
    def test_exact_synthetic_solution_matches_independent_normal_equations(self):
        receptor, profiles, species = synthetic_problem()
        result = epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species)
        f = np.array([[1, 0], [0, 1], [1, 1]], dtype=float)
        independent = np.linalg.solve(f.T @ f, f.T @ np.array([2, 3, 5]))
        np.testing.assert_allclose(list(result["source_contributions"].values()), independent, atol=1e-12)
        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations"], 2)
        self.assertAlmostEqual(result["R2"], 1)
        self.assertAlmostEqual(result["reduced_chi2"], 0)
        self.assertAlmostEqual(result["percent_mass"], 50)

    def test_iteration_limit_is_not_promoted_to_convergence(self):
        receptor, profiles, species = synthetic_problem()
        result = epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species, max_iterations=1)
        self.assertFalse(result["converged"])
        self.assertTrue(result["terminal_iterate_not_accepted_outcome_if_nonconverged"])
        self.assertFalse(epa.fit_targets(result))

    def test_negative_alternative_contributions_are_not_clipped(self):
        receptor, profiles, species = synthetic_problem()
        receptor["AC"], receptor["BC"], receptor["CC"] = "-2", "3", "1"
        result = epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species)
        self.assertTrue(result["converged"])
        self.assertAlmostEqual(result["source_contributions"]["X"], -2)
        self.assertAlmostEqual(result["source_contributions"]["Y"], 3)

    def test_missing_zero_negative_or_nonfinite_uncertainty_fails(self):
        for value in ("0", "-1", "NaN"):
            receptor, profiles, species = synthetic_problem()
            receptor["AU"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "invalid"):
                epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species)
        receptor, profiles, species = synthetic_problem()
        del receptor["AU"]
        with self.assertRaises(KeyError):
            epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species)

    def test_rank_deficient_design_fails_without_solver_tuning(self):
        receptor, profiles, species = synthetic_problem()
        profiles["Y"] = profiles["X"].copy()
        with self.assertRaisesRegex(ValueError, "rank-deficient"):
            epa.effective_variance_fit(receptor, profiles, ["X", "Y"], species)

    def test_incomplete_text_rows_are_not_imputed(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            epa.table(b"A B C\n1 2\n")
        with self.assertRaisesRegex(ValueError, "duplicated"):
            epa.table(b"A A\n1 2\n")

    def test_controller_removes_most_negative_then_restarts(self):
        calls = []
        def fake_fit(receptor, profiles, source_ids):
            calls.append(list(source_ids))
            contributions = {name: 1.0 for name in source_ids}
            if len(calls) == 1:
                contributions["SFCRUC"] = -2.0
                contributions["NANO3"] = -1.0
            return {"converged": True, "source_ids": list(source_ids),
                    "source_contributions": contributions, "iterations": 3}
        with patch.object(epa, "effective_variance_fit", side_effect=fake_fit):
            result = epa.central_fit({}, {})
        self.assertEqual(len(calls), 2)
        self.assertNotIn("SFCRUC", calls[1])
        self.assertIn("NANO3", calls[1])
        self.assertEqual(result["central_removal_history"][0]["removed_source"], "SFCRUC")

    def test_controller_does_not_prune_nonconverged_negative_result(self):
        output = {"converged": False, "source_ids": list(epa.CONFIG["central_initial_sources"]),
                  "source_contributions": {"SFCRUC": -2.0}, "iterations": 20}
        with patch.object(epa, "effective_variance_fit", return_value=output) as mock:
            result = epa.central_fit({}, {})
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(result["controller_status"], "HOLD_NONCONVERGED_NO_PRUNING")

    def test_ranking_uses_fixed_slots_and_retains_ties(self):
        central = {"A": 2.0, "B": 1.0, "C": 0.5}
        alternative = {"A": 1.0, "B": 2.0, "C": 0.5}
        result = epa.ranking_changes(central, alternative)
        self.assertTrue(result["ordering_change"])
        self.assertTrue(result["largest_source_change"])
        self.assertEqual(result["pair_changes"], [("A", "B")])
        self.assertTrue(epa.ranking_changes(central, {"A": 2, "B": 2, "C": 0.5})["top_tie"])
        with self.assertRaisesRegex(ValueError, "identical source slots"):
            epa.ranking_changes(central, {"X": 2, "B": 1, "C": 0.5})

    def test_rounding_check_can_detect_a_real_decision_change(self):
        a, b = {"A": 1.000004, "B": 1.0}, {"A": 0.999996, "B": 1.0}
        self.assertTrue(epa.ranking_changes(a, b)["ordering_change"])
        self.assertFalse(epa.ranking_changes(a, b, 5)["ordering_change"])
        self.assertTrue(epa.ranking_changes(a, b, 5)["top_tie"])

    def test_changed_frozen_configuration_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            initial = epa.freeze_configuration(target)
            self.assertEqual(initial, "6d3b10b2090526e3f15e987cc1b796fb02736570e2b3284738001956cacadc39")
            changed = copy.deepcopy(epa.CONFIG)
            changed["relative_tolerance"] = 0.02
            with patch.object(epa, "CONFIG", changed), self.assertRaisesRegex(ValueError, "stop rather than tune"):
                epa.freeze_configuration(target)

    def test_path_guards_prevent_public_ledger_and_input_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / "input"
            public = root / "outputs/strengthening_20260926"
            private = root / "private/epa-native-test"
            epa.validate_output_paths(inputs, public, private, root)
            for bad in (public / "ledger", root / "outside", root / "private", root / "private/../../escape"):
                with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "row ledger"):
                    epa.validate_output_paths(inputs, public, bad, root)
            with self.assertRaisesRegex(ValueError, "dedicated strengthening"):
                epa.validate_output_paths(inputs, root / "outputs/publication_archive_20260926", private, root)
            with self.assertRaisesRegex(ValueError, "overlaps"):
                epa.validate_output_paths(public / "inputs", public, private, root)

    def test_untrusted_archive_fails_before_zip_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            inputs = Path(directory)
            (inputs / "sjvf_data.zip").write_bytes(b"not a trusted archive")
            with patch.object(epa, "ZipFile", side_effect=AssertionError("should not parse")):
                with self.assertRaisesRegex(ValueError, "before ZIP parsing"):
                    epa.archive_inventory(inputs)

    def test_recovery_identity_mutation_fails(self):
        recovery = {"records": [{"name": "sample.zip", "sha256": "abc", "bytes": 4, "members": []}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.json"
            path.write_bytes(epa.json_bytes(recovery))
            with self.assertRaisesRegex(ValueError, "recovered identity"):
                epa.verify_recovery_identities([{"archive": "sample.zip", "sha256": "def", "bytes": 4}], path)


NATIVE_PRESENT = all((epa.DEFAULT_INPUT / name).is_file() for name in epa.TRUSTED_ARCHIVE_HASHES)


@unittest.skipUnless(NATIVE_PRESENT, "Official third-party EPA archives absent; native integration not run")
class EPANativeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inventory = epa.archive_inventory(epa.DEFAULT_INPUT)
        cls.identities = epa.verify_recovery_identities(inventory, ROOT / "outputs/strengthening_20260926/source_recovery.json")
        cls.receptors, cls.profiles, cls.summary = epa.load_inputs(epa.DEFAULT_INPUT)
        cls.case, cls.case_ledger = epa.worked_case(cls.receptors, cls.profiles)
        cls.aggregate, cls.ledger = epa.full_substitutions(cls.receptors, cls.profiles)

    def test_source_and_member_identities_match_recovery_before_fits(self):
        self.assertEqual(self.identities["archives_checked"], 4)
        self.assertEqual(self.identities["members_checked"], 39)
        self.assertTrue(self.identities["performed_before_fitting"])

    def test_native_selection_and_descriptor_exhaustiveness(self):
        self.assertEqual(self.summary["fresno_fine_samples"], 35)
        self.assertEqual(len(self.summary["species"]), 20)
        self.assertEqual(self.summary["alternatives"], epa.CONFIG["expected_alternatives"])
        self.assertTrue(self.summary["species_arrays_2_and_4_identical"])

    def test_case_reproduces_all_twenty_numeric_fields_and_five_top_sources(self):
        self.assertTrue(self.case["all_five_runs_match_displayed_precision"])
        self.assertEqual(self.case["control_retained_sources"], ["SOIL03", "BAMAJC", "MOVES2", "AMSUL", "AMNIT", "NANO3"])
        self.assertEqual(self.case["published_comparator_sha256"], epa.WORKED_COMPARATOR_SHA256)
        for row in self.case["comparison"]:
            self.assertTrue(row["all_fields_match"])
            self.assertLess(max(abs(value) for value in row["difference_from_displayed"].values()), 0.0000005)

    def test_all_headline_counts_and_attrition_match_without_tuning(self):
        result = self.aggregate
        self.assertEqual(result["status"], "RECONSTRUCTED_MATCH")
        self.assertTrue(result["source_native_recomputed"])
        self.assertFalse(result["historical_original_execution_ledger_recovered"])
        self.assertEqual(set(result["differences"].values()), {0})
        expected_nonconvergence = {"MAFISC": 13, "MAMAJC": 7, "MOVES3": 1, "MOVES5": 1}
        for name, row in result["per_alternative_attrition"].items():
            self.assertEqual(row["nonconverged"], expected_nonconvergence.get(name, 0))
        self.assertEqual(result["rank_decision_disagreements_after_rounding_5dp"], 0)
        self.assertEqual(result["converged_runs_with_top_tie_before_or_after_rounding"], 0)

    def test_independent_sort_based_reclassification_recovers_133_and_62(self):
        controls = {tuple(row["sample"].items()): row["result"] for row in self.ledger["central_runs"]}
        included = ordering = largest = 0
        for row in self.ledger["substitutions"]:
            alt = row["result"]
            central = controls[tuple(row["sample"].items())]
            if not (alt["converged"] and 0.8 <= central["R2"] <= 1 and 0 <= central["reduced_chi2"] <= 4
                    and 0.8 <= alt["R2"] <= 1 and 0 <= alt["reduced_chi2"] <= 4):
                continue
            included += 1
            source_values = central["source_contributions"]
            mapped = {row["central_slot"] if key == row["alternative"] else key: value
                      for key, value in alt["source_contributions"].items()}
            order_a = sorted(source_values, key=source_values.__getitem__)
            order_b = sorted(mapped, key=mapped.__getitem__)
            self.assertEqual(len(set(source_values.values())), len(source_values))
            self.assertEqual(len(set(mapped.values())), len(mapped))
            ordering += order_a != order_b
            largest += order_a[-1] != order_b[-1]
        self.assertEqual((included, ordering, largest), (283, 133, 62))

    def test_repeated_native_calculation_has_identical_private_ledger_bytes(self):
        aggregate, ledger = epa.full_substitutions(self.receptors, self.profiles)
        self.assertEqual(epa.json_bytes(ledger), epa.json_bytes(self.ledger))
        self.assertEqual(aggregate, self.aggregate)


if __name__ == "__main__":
    unittest.main()
