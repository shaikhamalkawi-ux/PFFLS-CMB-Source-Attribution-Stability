"""Synthetic tests; no received private measurements or identities as fixtures.

Optional hash-guarded local integration:
  set FAIRBANKS_RECEIVED_ZIP to the original private attachment ZIP.
"""

from copy import deepcopy
from datetime import datetime
from decimal import Decimal as D
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_received_fairbanks import (  # noqa: E402
    cmb_pairs, compare_markers, date_value, interval_metrics, load_cmb,
    load_received, make_summary, marker_bracket, marker_overlaps, number,
    private_directory, summarize_comparisons, unique_index, value_flag,
)


def synthetic_marker():
    return {
        "site": "synthetic_site", "date": "2000-01-01", "date_kind": "excel_date",
        "workbook": "SYNTHETIC.xlsx", "sheet": "Artificial", "source_range": "A6:G6",
        "filter_id_present": False, "pm25_ug_m3": D("10"),
        "levoglucosan_ng_m3": D("100"),
        "fine_cached_percent": D("9.01"), "omni_cached_percent": D("13.27"),
        "fine_ws_percent": D("9.01"), "omni_ws_percent": D("13.27"),
        "fine_cache_difference_pp": D(0), "omni_cache_difference_pp": D(0),
        "fine_formula_expected": True, "omni_formula_expected": True,
        "fine_formula_present": True, "omni_formula_present": True,
        "cell_evidence_json": "SYNTHETIC_PRIVATE_EVIDENCE",
    }


def synthetic_cmb():
    base = {"site": "synthetic_site", "date": "2000-01-01", "cmb_row_status": "valid",
            "pm25_mass": "10", "wood_smoke_se": "0.1", "report_pages": "synthetic"}
    return [dict(base, system="epa", wood_smoke="2"),
            dict(base, system="omni", wood_smoke="1.2"),
            dict(base, system="omni_revised", wood_smoke="9.0")]


class ReceivedFairbanksTests(unittest.TestCase):
    def test_missing_errors_and_limits_never_become_zero(self):
        for value in (None, "", "AN", "<error", "<0.3", "#DIV/0!", True):
            self.assertIsNone(number(value))
        self.assertEqual(value_flag("<error"), "source_less_than_error_flag")
        self.assertEqual(value_flag("<0.3"), "censored_or_limit_flag")
        self.assertEqual(value_flag("#VALUE!"), "excel_error")
        self.assertEqual(value_flag(0), "zero")
        self.assertEqual(number(0), D(0))

    def test_native_and_text_dates_remain_distinct(self):
        self.assertEqual(date_value(datetime(2000, 1, 1)), ("2000-01-01", "excel_date"))
        self.assertEqual(date_value(" 1/1/2000"), ("2000-01-01", "text_date"))
        self.assertEqual(date_value("Date"), (None, "not_date"))
        with self.assertRaises(ValueError):
            date_value(datetime(2000, 1, 1, 1))

    def test_unit_conversion_and_exact_factor_not_rounded_13_3(self):
        low, high = marker_bracket(10, 100)
        self.assertEqual((low, high), (D("9.01"), D("13.27")))
        self.assertNotEqual(high, D("13.3"))
        self.assertIsNone(marker_bracket(0, 100))
        self.assertIsNone(marker_bracket(10, 0))
        self.assertIsNone(marker_bracket(10, "<1"))
        self.assertGreater(marker_bracket(1, 1000)[0], 100)  # Never clip.

    def test_interval_distance_is_not_midpoint_absolute_error(self):
        result = interval_metrics(D(11), D(10), D(14))
        self.assertEqual(result["relation"], "inside")
        self.assertEqual(result["interval_distance_pp"], 0)
        self.assertEqual(result["midpoint_absolute_difference_pp"], 1)
        self.assertEqual(interval_metrics(10, 10, 14)["relation"], "inside")
        self.assertEqual(interval_metrics(14, 10, 14)["relation"], "inside")
        self.assertEqual(interval_metrics(8, 10, 14)["interval_distance_pp"], 2)
        self.assertEqual(interval_metrics(16, 10, 14)["interval_distance_pp"], 2)
        with self.assertRaises(ValueError):
            interval_metrics(11, 14, 10)

    def test_exact_original_cmb_not_revised(self):
        pairs = cmb_pairs(synthetic_cmb())
        self.assertEqual(set(pairs[("synthetic_site", "2000-01-01")]), {"epa", "omni"})
        rows, excluded = compare_markers([synthetic_marker()], pairs, "levoglucosan")
        self.assertFalse(excluded)
        self.assertEqual(rows[0]["omni_wood_smoke_percent"], 12)
        self.assertEqual(rows[0]["closer_to_interval"], "omni")

    def test_native_blank_outputs_are_not_imputed_in_primary(self):
        marker = synthetic_marker()
        marker["fine_cached_percent"] = marker["omni_cached_percent"] = None
        pairs = cmb_pairs(synthetic_cmb())
        rows, excluded = compare_markers([marker], pairs, "levoglucosan")
        self.assertFalse(rows)
        self.assertEqual(excluded[0]["reason"], "source_marker_outputs_missing_or_flagged")
        sensitivity, _ = compare_markers([marker], pairs, "levoglucosan", recompute_missing=True)
        self.assertEqual(len(sensitivity), 1)
        self.assertFalse(sensitivity[0]["source_marker_outputs_present"])

    def test_partial_fill_sensitivity_does_not_fill_fully_missing_bracket(self):
        marker = synthetic_marker()
        marker["omni_cached_percent"] = None
        pairs = cmb_pairs(synthetic_cmb())
        partial, _ = compare_markers([marker], pairs, "levoglucosan", recompute_partial=True)
        self.assertEqual(len(partial), 1)
        self.assertFalse(partial[0]["source_marker_outputs_present"])
        marker["fine_cached_percent"] = None
        partial, _ = compare_markers([marker], pairs, "levoglucosan", recompute_partial=True)
        self.assertFalse(partial)

    def test_primary_uses_native_cached_bounds_not_recomputed_replacements(self):
        marker = synthetic_marker()
        marker["fine_cached_percent"], marker["omni_cached_percent"] = D(25), D(30)
        rows, _ = compare_markers([marker], cmb_pairs(synthetic_cmb()), "levoglucosan")
        self.assertEqual(rows[0]["marker_low_percent"], 25)
        self.assertEqual(rows[0]["epa_relation"], "below")

    def test_partial_fill_preserves_each_existing_native_endpoint(self):
        pairs = cmb_pairs(synthetic_cmb())
        for native_low, native_high, expected in (
            (D("10"), None, (D("10"), D("13.27"))),
            (None, D("12"), (D("9.01"), D("12"))),
        ):
            with self.subTest(native_low=native_low, native_high=native_high):
                marker = synthetic_marker()
                marker["fine_cached_percent"] = native_low
                marker["omni_cached_percent"] = native_high
                rows, excluded = compare_markers(
                    [marker], pairs, "levoglucosan", recompute_partial=True)
                self.assertFalse(excluded)
                self.assertEqual(len(rows), 1)
                self.assertEqual((rows[0]["marker_low_percent"],
                                  rows[0]["marker_high_percent"]), expected)

    def test_no_fuzzy_match_and_invalid_system_excluded(self):
        marker = synthetic_marker()
        marker["date"] = "2000-01-02"
        rows, excluded = compare_markers([marker], cmb_pairs(synthetic_cmb()), "levoglucosan")
        self.assertFalse(rows)
        self.assertEqual(excluded[0]["reason"], "no_exact_original_CMB_pair")
        cmb = synthetic_cmb()
        cmb[0]["cmb_row_status"] = "mass_too_small_for_cmb"
        rows, excluded = compare_markers([synthetic_marker()], cmb_pairs(cmb), "levoglucosan")
        self.assertFalse(rows)
        self.assertEqual(excluded[0]["reason"], "at_least_one_CMB_system_invalid")

    def test_duplicate_identities_fail_closed(self):
        with self.assertRaises(ValueError):
            unique_index([synthetic_marker(), synthetic_marker()])
        with self.assertRaises(ValueError):
            cmb_pairs(synthetic_cmb() + [synthetic_cmb()[0]])

    def test_denominator_sensitivity_is_explicit_not_mass_filter(self):
        marker = synthetic_marker()
        marker["pm25_ug_m3"] = D(20)
        pairs = cmb_pairs(synthetic_cmb())
        primary, _ = compare_markers([marker], pairs, "levoglucosan")
        native, _ = compare_markers([marker], pairs, "levoglucosan", denominator="marker_workbook")
        self.assertEqual(primary[0]["epa_wood_smoke_percent"], 20)
        self.assertEqual(native[0]["epa_wood_smoke_percent"], 10)
        self.assertEqual(primary[0]["epa_mass_absolute_difference_ug_m3"], 10)
        self.assertEqual(len(primary), 1)  # Diagnostic mismatch not hidden exclusion.

    def test_same_date_two_marker_overlap_and_interval_ties(self):
        rows, _ = compare_markers([synthetic_marker()], cmb_pairs(synthetic_cmb()), "levoglucosan")
        other = deepcopy(rows)
        other[0]["marker_low_percent"], other[0]["marker_high_percent"] = D("13.27"), D(15)
        self.assertTrue(marker_overlaps(rows, other)[0]["intervals_overlap"])
        other[0]["marker_low_percent"] = D(14)
        self.assertFalse(marker_overlaps(rows, other)[0]["intervals_overlap"])
        cmb = synthetic_cmb()
        cmb[0]["wood_smoke"] = "1.1"
        tied, _ = compare_markers([synthetic_marker()], cmb_pairs(cmb), "levoglucosan")
        self.assertEqual(tied[0]["closer_to_interval"], "tie")

    def test_aggregate_summary_omits_private_rows_dates_and_ids(self):
        marker = synthetic_marker()
        cmb = synthetic_cmb()
        rows, excluded = compare_markers([marker], cmb_pairs(cmb), "levoglucosan")
        summary = make_summary([marker], [], cmb, rows, [], [], excluded, [])
        text = str(summary)
        for forbidden in ("2000-01-01", "SYNTHETIC_PRIVATE_EVIDENCE", "A6:G6", "SYNTHETIC.xlsx"):
            self.assertNotIn(forbidden, text)
        self.assertEqual(summary["levoglucosan_comparison"]["n"], 1)
        self.assertEqual(summarize_comparisons([])["n"], 0)

    def test_detailed_output_cannot_escape_private_directory(self):
        permitted = ROOT / "private/received_fairbanks/test"
        self.assertEqual(private_directory(permitted), permitted.resolve())
        with self.assertRaises(ValueError):
            private_directory(ROOT / "outputs/received_fairbanks")
        with self.assertRaises(ValueError):
            private_directory(ROOT / "private/received_fairbanks/../../outputs")

    def test_wrong_private_zip_hash_rejected_before_parse(self):
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "synthetic.zip"
            input_path.write_bytes(b"not a private dataset")
            with self.assertRaisesRegex(ValueError, "hash differs"):
                load_received(input_path)

    @unittest.skipUnless(os.environ.get("FAIRBANKS_RECEIVED_ZIP"), "Private hash-guarded integration is opt-in")
    def test_optional_private_hash_locked_reproduction(self):
        levo, summary = load_received(os.environ["FAIRBANKS_RECEIVED_ZIP"])
        self.assertEqual(sum(r["date_kind"] == "excel_date" for r in levo), 241)
        self.assertEqual(sum(r["date_kind"] == "text_date" for r in levo), 3)
        self.assertEqual(len(summary), 361)
        self.assertEqual(sum(r["radiocarbon_interval_present"] for r in summary), 26)
        pairs = cmb_pairs(load_cmb(ROOT / "outputs/cycle02/appendix_c_2008_2009_daily.csv"))
        lm, _ = compare_markers(levo, pairs, "levoglucosan")
        rm, _ = compare_markers(summary, pairs, "radiocarbon")
        extra, _ = compare_markers(levo, pairs, "levoglucosan", recompute_missing=True)
        self.assertEqual(len(lm), 52)
        self.assertEqual(len(rm), 12)
        self.assertEqual(len(extra), 54)
        self.assertEqual(sum(not r["source_marker_outputs_present"] for r in extra), 2)
        partial, _ = compare_markers(levo, pairs, "levoglucosan", recompute_partial=True)
        self.assertEqual(len(partial), 53)
        self.assertEqual(summarize_comparisons(lm)["closer_to_interval"], {"epa": 17, "omni": 32, "tie": 3})
        self.assertEqual(summarize_comparisons(partial)["closer_to_interval"], {"epa": 18, "omni": 32, "tie": 3})
        self.assertEqual(summarize_comparisons(rm)["closer_to_interval"], {"epa": 7, "omni": 4, "tie": 1})
        both = marker_overlaps(lm, rm)
        self.assertEqual(len(both), 3)
        self.assertEqual(sum(r["intervals_overlap"] for r in both), 1)


if __name__ == "__main__":
    unittest.main()
