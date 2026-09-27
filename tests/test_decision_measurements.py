"""Meaningful leakage, boundary, missingness and outcome tests for tracer design."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_decision_measurements as measurements


def fixture():
    identity = dict(zip(measurements.IDENTITY, ("FRESNO", "DATE", "24", "0", "FINE")))
    result = {"converged": True, "R2": 0.9, "reduced_chi2": 1.0,
              "source_ids": ["X", "Y"], "source_contributions": {"X": 3.0, "Y": 1.0}}
    other = copy.deepcopy(result)
    other["source_contributions"] = {"X": 1.0, "Y": 3.0}
    sample = {"sample": identity, "central": result,
              "rows": [{"source_ids": ["X", "Y"], "result": result, "mapped": {"A": 3.0, "B": 1.0}},
                       {"source_ids": ["X", "Y"], "result": other, "mapped": {"A": 1.0, "B": 3.0}}]}
    uncertainties = {name[:-1] + "U": "1" for name in measurements.CANDIDATES}
    profiles = {sid: {field: "0" for name in measurements.CANDIDATES for field in (name, name[:-1] + "U")}
                for sid in ("X", "Y")}
    profiles["X"]["SUXC"] = "1"
    profiles["X"]["CUXC"] = "2"
    profiles["X"]["ZNXC"] = "1.5"
    return sample, uncertainties, profiles


class ForbiddenMeans(dict):
    def __getitem__(self, key):
        if key in measurements.CANDIDATES:
            raise AssertionError("held-out means accessed during design")
        return super().__getitem__(key)


class MeasurementTests(unittest.TestCase):
    def test_design_uses_no_heldout_means(self):
        sample, uncertainty, profiles = fixture()
        guarded = ForbiddenMeans(uncertainty)
        guarded.update({name: "not a number" for name in measurements.CANDIDATES})
        record = measurements.design_sample(sample, guarded, profiles)
        self.assertEqual(record["selected"], "CUXC")
        self.assertEqual(record["candidates"]["CUXC"]["score"], 2)

    def test_projection_does_not_return_concentrations(self):
        rows = measurements.projected_table(b"ID SUXC SUXU\nFRESNO FORBIDDEN 1\n", ("ID", "SUXU"))
        self.assertEqual(rows, [{"ID": "FRESNO", "SUXU": "1"}])

    def test_projection_rejects_incomplete_or_duplicate_columns(self):
        for raw in (b"A A\n1 2\n", b"A B\n1\n"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                measurements.projected_table(raw, ("A",))

    def test_evaluation_verifies_before_reader(self):
        with patch.object(measurements, "verify_selection", side_effect=ValueError("missing freeze")), \
                patch.object(measurements, "source_inputs") as reader:
            with self.assertRaisesRegex(ValueError, "missing freeze"):
                measurements.evaluate(Path("unused"))
            reader.assert_not_called()

    def test_existing_selection_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp)
            (private / "measurement_selection.json").write_text("frozen", encoding="utf-8")
            with patch.object(measurements, "PRIVATE", private), self.assertRaisesRegex(ValueError, "already frozen"):
                measurements.design(Path("unused"))

    def test_selection_hash_tampering_blocks_before_mean_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            private, public = Path(tmp) / "private", Path(tmp) / "public"
            private.mkdir()
            public.mkdir()
            original = b'{"frozen": true}\n'
            (private / "measurement_selection.json").write_bytes(b'{"frozen": false}\n')
            (private / "measurement_selection.sha256").write_text(measurements.digest(original), encoding="ascii")
            (public / "measurement_design.json").write_text(json.dumps({"selection_sha256": measurements.digest(original)}), encoding="utf-8")
            with patch.object(measurements, "PRIVATE", private), patch.object(measurements, "PUBLIC", public), \
                    patch.object(measurements, "source_inputs") as reader:
                with self.assertRaisesRegex(ValueError, "selection identity differs"):
                    measurements.evaluate(Path("unused"))
                reader.assert_not_called()

    def test_saved_integration_records_validate_and_design_precedes_evaluation(self):
        required = [measurements.PRIVATE / "measurement_selection.json",
                    measurements.PRIVATE / "measurement_evaluation.json",
                    measurements.PUBLIC / "measurement_results.json"]
        if not all(path.exists() for path in required):
            self.skipTest("completed private experiment not available")
        if not (measurements.native.DEFAULT_INPUT / "sjvf_data.zip").exists():
            self.skipTest("official source archive not available")
        selection, public_design = measurements.verify_selection(measurements.native.DEFAULT_INPUT)
        evaluation_payload = required[1].read_bytes()
        evaluation = json.loads(evaluation_payload)
        public_result = json.loads(required[2].read_bytes())
        self.assertLess(measurements.datetime.fromisoformat(selection["created_utc"]),
                        measurements.datetime.fromisoformat(evaluation["evaluation_started_utc"]))
        self.assertEqual(public_design["selection_sha256"], evaluation["selection_sha256"])
        self.assertEqual(measurements.digest(evaluation_payload), public_result["private_evaluation_sha256"])
        self.assertFalse(selection["heldout_concentrations_accessed"])

    def test_invalid_receptor_uncertainty_excludes_candidate(self):
        for value in ("0", "-1", "nan", "inf", "bad"):
            sample, uncertainty, profiles = fixture()
            uncertainty["CUXU"] = value
            with self.subTest(value=value):
                record = measurements.design_sample(sample, uncertainty, profiles)
                self.assertEqual(record["candidates"]["CUXC"]["status"], "INVALID_DESIGN_FIELDS")
                self.assertEqual(record["selected"], "ZNXC")

    def test_missing_profile_field_invalidates_whole_candidate(self):
        sample, uncertainty, profiles = fixture()
        del profiles["Y"]["CUXC"]
        record = measurements.design_sample(sample, uncertainty, profiles)
        self.assertEqual(record["candidates"]["CUXC"]["status"], "INVALID_DESIGN_FIELDS")
        self.assertEqual(len(record["candidates"]["SUXC"]["predictions"]), 2)

    def test_zero_profile_uncertainty_allowed_negative_nonfinite_not(self):
        sample, uncertainty, profiles = fixture()
        self.assertEqual(measurements.design_sample(sample, uncertainty, profiles)["selected"], "CUXC")
        for value in ("-1", "nan", "inf"):
            altered = copy.deepcopy(profiles)
            altered["X"]["CUXU"] = value
            with self.subTest(value=value):
                self.assertEqual(measurements.design_sample(sample, uncertainty, altered)["candidates"]["CUXC"]["status"], "INVALID_DESIGN_FIELDS")

    def test_negative_and_nonfinite_profile_means_invalid(self):
        for value in ("-99", "-0.1", "nan", "inf"):
            sample, uncertainty, profiles = fixture()
            profiles["X"]["CUXC"] = value
            with self.subTest(value=value):
                self.assertEqual(measurements.design_sample(sample, uncertainty, profiles)["candidates"]["CUXC"]["status"], "INVALID_DESIGN_FIELDS")

    def test_no_ambiguous_pair_is_not_applicable(self):
        sample, uncertainty, profiles = fixture()
        sample["rows"] = sample["rows"][:1]
        record = measurements.design_sample(sample, uncertainty, profiles)
        self.assertEqual(record["status"], "NO_CROSS_TOP_PAIRS")
        self.assertIsNone(record["selected"])

    def test_tied_top_does_not_create_unique_cross_pair(self):
        sample, uncertainty, profiles = fixture()
        sample["rows"][1]["result"]["source_contributions"] = {"X": 2.0, "Y": 2.0}
        sample["rows"][1]["mapped"] = {"A": 2.0, "B": 2.0}
        record = measurements.design_sample(sample, uncertainty, profiles)
        self.assertEqual(record["attrition"]["tied_top_rows"], 1)
        self.assertEqual(record["status"], "NO_CROSS_TOP_PAIRS")

    def test_zero_scores_keep_low_separation_and_lexical_tie(self):
        sample, uncertainty, profiles = fixture()
        for candidate in measurements.CANDIDATES:
            profiles["X"][candidate] = profiles["Y"][candidate] = "1"
        record = measurements.design_sample(sample, uncertainty, profiles)
        self.assertEqual(record["status"], "SELECTED_LOW_SEPARATION")
        self.assertEqual(record["selected"], "CUXC")

    def test_basic_negative_and_unresolved_attrition(self):
        sample, _, _ = fixture()
        negative = copy.deepcopy(sample["rows"][1])
        negative["result"]["source_contributions"]["X"] = -1
        negative["mapped"]["A"] = -1
        unresolved = copy.deepcopy(sample["rows"][1])
        unresolved["result"]["converged"] = False
        nonfinite = copy.deepcopy(sample["rows"][1])
        nonfinite["result"]["source_contributions"]["X"] = float("nan")
        sample["rows"] += [negative, unresolved, nonfinite]
        scenarios, attrition = measurements.physical_scenarios(sample)
        self.assertEqual(len(scenarios), 2)
        self.assertEqual(attrition["negative_rows"], 1)
        self.assertEqual(attrition["unresolved_rows"], 1)
        self.assertEqual(attrition["invalid_contribution_rows"], 1)

    def test_central_ineligible_blocks_secondary_set(self):
        sample, _, _ = fixture()
        sample["central"]["R2"] = 0.7
        scenarios, attrition = measurements.physical_scenarios(sample)
        self.assertEqual(scenarios, [])
        self.assertFalse(attrition["central_basic_eligible"])

    def test_cutoff_boundary_is_inclusive(self):
        predictions = [{"row_index": 0, "prediction": 1.0, "scale": 2.0, "top_sources": ["A"]}]
        self.assertEqual(measurements.screen(predictions, 3.0, 1.0)["retained_scenarios"], 1)
        self.assertEqual(measurements.screen(predictions, 3.0000001, 1.0)["retained_scenarios"], 0)

    def test_all_rejected_is_not_success(self):
        predictions = [{"row_index": 0, "prediction": 1.0, "scale": 1.0, "top_sources": ["A"]},
                       {"row_index": 1, "prediction": 2.0, "scale": 1.0, "top_sources": ["B"]}]
        result = measurements.screen(predictions, 100.0, 1.0)
        self.assertTrue(result["rejected_all"])
        self.assertFalse(result["resolved_to_single_top"])
        self.assertFalse(result["top_set_reduced_nonempty"])
        self.assertFalse(result["no_top_set_reduction"])

    def test_nonfinite_observation_or_invalid_scale_rejected(self):
        predictions = [{"row_index": 0, "prediction": 1.0, "scale": 1.0, "top_sources": ["A"]}]
        for value in (float("nan"), float("inf"), -99):
            with self.subTest(value=value), self.assertRaises(ValueError):
                measurements.screen(predictions, value, 1.0)
        for scale in (0, -1, float("nan")):
            predictions[0]["scale"] = scale
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                measurements.screen(predictions, 1.0, 1.0)

    def test_fixed_candidates_evaluated_and_matched_even_when_not_selected(self):
        sample, uncertainty, profiles = fixture()
        designed = measurements.design_sample(sample, uncertainty, profiles)
        evaluated = measurements.evaluate_sample(designed, {"SUXC": 3, "CUXC": 100, "ZNXC": 1.5})
        aggregate = measurements.evaluation_aggregate([evaluated])
        cutoff = aggregate["cutoffs"]["1"]
        self.assertEqual(cutoff["strategies"]["selected"]["rejected_all_samples"], 1)
        self.assertEqual(cutoff["strategies"]["SUXC"]["resolved_to_single_top_samples"], 1)
        self.assertEqual(cutoff["matched_selected_vs_fixed"]["SUXC"]["fixed_only_resolved"], 1)
        self.assertEqual(cutoff["matched_selected_vs_fixed"]["SUXC"]["matched_samples"], 1)
        self.assertEqual(designed["selected"], "CUXC")

    def test_public_aggregate_contains_no_sample_identity_or_predictions(self):
        sample, uncertainty, profiles = fixture()
        designed = measurements.design_sample(sample, uncertainty, profiles)
        evaluated = measurements.evaluate_sample(designed, {"SUXC": 3, "CUXC": 6, "ZNXC": 1.5})
        public = json.dumps({"design": measurements.design_aggregate([designed]),
                             "evaluation": measurements.evaluation_aggregate([evaluated])})
        for private_key in ('"sample"', '"prediction"', '"observed"', '"DATE"', '"contributions"'):
            self.assertNotIn(private_key, public)


if __name__ == "__main__":
    unittest.main()
