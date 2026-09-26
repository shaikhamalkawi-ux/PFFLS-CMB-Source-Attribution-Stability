"""Synthetic unit tests plus optional, private-workbook integration checks."""
import importlib.util
from datetime import datetime
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_fairbanks_strengthening.py"
SPEC = importlib.util.spec_from_file_location("fairbanks_strengthening", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class FairbanksAuditUnitTests(unittest.TestCase):
    def test_native_date(self):
        self.assertEqual(audit.parse_date(datetime(2011, 2, 8)), ("2011-02-08", "excel_date"))

    def test_explicit_us_text_date(self):
        self.assertEqual(audit.parse_date(" 2/8/2011"), ("2011-02-08", "us_text_date"))

    def test_mixed_identifier_not_silently_parsed(self):
        self.assertEqual(audit.parse_date("ABC Example Site 2/8/2011"), (None, None))
        self.assertEqual(audit.parse_date(40216), (None, None))

    def test_numeric_excludes_bool_and_nonfinite(self):
        self.assertFalse(audit.numeric(True))
        self.assertFalse(audit.numeric(float("nan")))
        self.assertFalse(audit.numeric(float("inf")))
        self.assertTrue(audit.numeric(0))

    def test_interval_distance_and_bad_order(self):
        self.assertEqual(audit.interval_distance(4, 2, 3), 1)
        self.assertEqual(audit.interval_distance(1, 2, 3), 1)
        self.assertEqual(audit.interval_distance(2, 2, 3), 0)
        with self.assertRaises(ValueError):
            audit.interval_distance(2, 3, 2)

    def test_duplicate_keys_count_not_silent_overwrite(self):
        rows = [{"site": "test", "date": "2011-02-08"}] * 2
        self.assertEqual(audit.inventory_duplicates(rows)[0]["count"], 2)

    def test_primary_bracket_missing_is_not_bad_cache(self):
        values = [[None] * 7 for _ in range(6)]
        formulas = [[None] * 7 for _ in range(6)]
        values[2][5:7] = [9.01, 13.27]
        values[5] = [datetime(2011, 2, 8), None, 10, 100, 1, 9.01, None]
        formulas[5] = [datetime(2011, 2, 8), None, 10, 100, "=share", "=low", None]
        result = audit.extract_levo({"State Building": formulas}, {"State Building": values})
        self.assertEqual(result[1][0]["issue"], "missing_output_not_formula_error")
        self.assertEqual(len(result[4]), 2)
        self.assertTrue(all(r["agrees"] for r in result[4]))

    def test_bad_existing_cache_detected(self):
        values = [[None] * 7 for _ in range(6)]
        formulas = [[None] * 7 for _ in range(6)]
        values[2][5:7] = [9.01, 13.27]
        values[5] = [datetime(2011, 2, 8), None, 10, 100, 1, 99, 13.27]
        formulas[5] = [datetime(2011, 2, 8), None, 10, 100, "=share", "=low", "=high"]
        result = audit.extract_levo({"State Building": formulas}, {"State Building": values})
        self.assertEqual(result[1][0]["issue"], "cached_value_mismatch")
        self.assertEqual(sum(not r["agrees"] for r in result[4]), 1)

    def test_private_output_guard(self):
        with self.assertRaisesRegex(ValueError, "only inside repository/private"):
            audit.run_audit(private_dir=audit.REPO / "outputs/forbidden_private_rows")


@unittest.skipUnless(all((audit.INPUT_DIR / name).is_file() for name in audit.HASHES),
                     "Private original workbooks not distributed with this repository")
class FairbanksAuditPrivateIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.run_audit()

    def test_inventory_and_date_types(self):
        levo = self.result["levo_inventory"]
        self.assertEqual(levo["native_excel_date_rows"], 241)
        self.assertEqual(levo["dated_rows"], 244)
        self.assertEqual(levo["date_types"]["us_text_date"], 3)
        self.assertEqual(levo["duplicate_site_date_keys"], 0)
        summary = self.result["summary_inventory"]
        self.assertEqual(summary["dated_rows"], 361)
        self.assertEqual(summary["dated_rows_with_two_radio_bounds"], 26)
        self.assertEqual(summary["mixed_id_site_date_annotations_excluded"], 4)

    def test_formula_caches_not_missing_output_imputation(self):
        checks = self.result["cached_formula_audit"]
        self.assertEqual(checks["existing_formula_checks"], 684)
        self.assertEqual(checks["existing_endpoint_formula_checks"], 455)
        self.assertEqual(checks["existing_formula_bad_caches"], 0)
        self.assertEqual(checks["missing_source_output_cells"], 9)

    def test_primary_levo_is_52_not_53(self):
        levo = self.result["levo_cached"]
        self.assertEqual(levo["n"], 52)
        self.assertEqual(levo["sites"], {"north_pole": 13, "peger_road": 15, "state_building": 24})
        self.assertEqual(levo["closer_system"], {"epa": 17, "omni": 32, "tie": 3})
        self.assertAlmostEqual(levo["epa"]["mean_interval_distance_pp"], 32.34534953552906)
        self.assertAlmostEqual(levo["omni"]["mean_interval_distance_pp"], 24.72552126137556)

    def test_53_and_54_only_labeled_recomputation_sensitivities(self):
        self.assertEqual(self.result["levo_partial_recomputed_sensitivity"]["n"], 53)
        self.assertEqual(self.result["levo_recomputed"]["n"], 54)
        self.assertEqual(self.result["levo_recomputed"]["epa"]["positions"]["below"], 1)

    def test_radiocarbon_and_denominator_sensitivity(self):
        radio = self.result["radiocarbon"]
        self.assertEqual(radio["n"], 12)
        self.assertEqual(radio["closer_system"], {"epa": 7, "omni": 4, "tie": 1})
        self.assertAlmostEqual(radio["epa"]["mean_interval_distance_pp"], 13.722044071333563)
        sensitivity = self.result["radiocarbon_native_pm_sensitivity"]
        self.assertAlmostEqual(sensitivity["epa"]["mean_interval_distance_pp"], 13.734750875702915)

    def test_identity_is_site_date_mass_not_filter_id(self):
        self.assertEqual(self.result["paired_levo_rows_without_filter_id"], 52)
        self.assertLessEqual(self.result["maximum_paired_levo_pm_difference_ug_m3"], 0.04 + 1e-12)

    def test_admission_boundary_and_marker_overlap(self):
        self.assertEqual(self.result["both_marker_dates"], 3)
        self.assertEqual(self.result["marker_overlap_dates"], 1)
        self.assertEqual(self.result["admission"]["external_profile_choice_accuracy"], "HOLD")


if __name__ == "__main__":
    unittest.main()
