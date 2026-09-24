import csv
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_cycle02_fairbanks import (  # noqa: E402
    EPA_FIELDS,
    TABLES,
    TableSpec,
    build_crosswalk,
    parse_appendix_table,
)


class FairbanksExtractionTests(unittest.TestCase):
    def test_peger_revised_omni_uses_its_published_column_order(self):
        spec = next(
            table for table in TABLES
            if table.site == "peger_road" and table.system == "omni_revised"
        )
        # Exact Ward Appendix C p. 122 rows: autos, diesel, then fuel oil.
        rows = parse_appendix_table(
            "2/5/09 48.0 3.8 0.7 3.1 0.6 7.4 3.1 0.0 0.0 19.9 3.0 17.8 5.3\n"
            "3/11/09 16.6 1.3 0.3 2.1 0.2 0.0 0.0 2.4 1.0 3.6 1.1 6.8 1.2\n",
            spec,
        )
        source_fields = (
            "autos", "autos_se", "diesel", "diesel_se",
            "no2_fuel_oil", "no2_fuel_oil_se", "wood_smoke", "wood_smoke_se",
        )
        expected = (
            ("7.4", "3.1", "0.0", "0.0", "19.9", "3.0", "17.8", "5.3"),
            ("0.0", "0.0", "2.4", "1.0", "3.6", "1.1", "6.8", "1.2"),
        )
        for row, values in zip(rows, expected):
            self.assertEqual(tuple(row[field] for field in source_fields), values)

    def test_appendix_row_with_estimates_and_standard_errors(self):
        spec = TableSpec("state_building", "epa", 110, 111, EPA_FIELDS)
        rows = parse_appendix_table(
            " 1/25/09 26.7 4.3 0.5 3.7 0.6 0.0 0.0 0.0 0.0 18.2 2.4\n",
            spec,
        )
        self.assertEqual(rows[0]["date"], "2009-01-25")
        self.assertEqual(rows[0]["wood_smoke"], "18.2")
        self.assertEqual(rows[0]["wood_smoke_se"], "2.4")
        self.assertEqual(rows[0]["cmb_row_status"], "valid")

    def test_low_mass_row_is_not_treated_as_a_valid_fit(self):
        spec = TableSpec("state_building", "epa", 110, 111, EPA_FIELDS)
        rows = parse_appendix_table(
            " 1/16/09 2.3** ** ** ** ** ** ** ** ** ** **\n", spec
        )
        self.assertEqual(rows[0]["cmb_row_status"], "mass_too_small_for_cmb")
        self.assertEqual(rows[0]["pm25_mass"], "2.3")
        self.assertEqual(rows[0]["wood_smoke"], "")

    def test_crosswalk_fails_closed_as_profile_system_sensitivity(self):
        epa_spec = TableSpec("state_building", "epa", 110, 111, EPA_FIELDS)
        from extract_cycle02_fairbanks import OMNI_FIELDS

        omni_spec = TableSpec("state_building", "omni", 112, 113, OMNI_FIELDS)
        rows = parse_appendix_table(
            " 1/25/09 26.7 4.3 0.5 3.7 0.6 0.0 0.0 0.0 0.0 18.2 2.4\n",
            epa_spec,
        )
        rows += parse_appendix_table(
            " 1/25/09 26.7 2.4 0.5 2.9 0.4 10.7 2.2 10.3 2.1\n",
            omni_spec,
        )
        pair = build_crosswalk(rows)[0]
        self.assertEqual(pair["source_universe_identical"], "no")
        self.assertEqual(pair["profile_choice_isolated"], "no")
        self.assertEqual(pair["disposition"], "HOLD")

    def test_committed_recovery_counts_and_fail_closed_labels(self):
        output = ROOT / "outputs" / "cycle02"
        with (output / "appendix_c_2008_2009_daily.csv").open(
            encoding="utf-8"
        ) as handle:
            daily = list(csv.DictReader(handle))
        with (output / "exact_case_crosswalk.csv").open(encoding="utf-8") as handle:
            crosswalk = list(csv.DictReader(handle))
        with (output / "aqs_state_building_receptor_candidates.csv").open(
            encoding="utf-8"
        ) as handle:
            receptor = list(csv.DictReader(handle))
        with (output / "aqs_state_building_mass_crosscheck.csv").open(
            encoding="utf-8"
        ) as handle:
            mass = list(csv.DictReader(handle))

        self.assertEqual(len(daily), 294)
        peger_revised = next(
            row for row in daily
            if row["site"] == "peger_road"
            and row["system"] == "omni_revised"
            and row["date"] == "2009-02-05"
        )
        self.assertEqual(peger_revised["autos"], "7.4")
        self.assertEqual(peger_revised["autos_se"], "3.1")
        self.assertEqual(peger_revised["diesel"], "0.0")
        self.assertEqual(peger_revised["no2_fuel_oil"], "19.9")
        self.assertEqual(peger_revised["no2_fuel_oil_se"], "3.0")
        self.assertEqual(len(crosswalk), 107)
        self.assertEqual(
            sum(
                row["epa_status"] == "valid" and row["omni_status"] == "valid"
                for row in crosswalk
            ),
            94,
        )
        self.assertTrue(all(row["profile_choice_isolated"] == "no" for row in crosswalk))
        self.assertTrue(all(row["disposition"] == "HOLD" for row in crosswalk))
        self.assertEqual(len(receptor), 1951)
        self.assertEqual(len(mass), 47)
        self.assertTrue(all(row["matches_report_precision"] == "yes" for row in mass))


if __name__ == "__main__":
    unittest.main()
