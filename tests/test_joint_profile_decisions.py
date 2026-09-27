"""Synthetic decision-logic tests and optional trusted EPA archive integration."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_joint_profile_decisions as joint  # noqa: E402


def row(distance, contributions, *, central=None, converged=True, r2=0.9, chi2=1.0, mass=100):
    central = central or {"a": 4.0, "b": 2.0, "c": 1.0}
    result = {"converged": converged, "R2": r2, "reduced_chi2": chi2, "percent_mass": mass,
              "source_ids": list(contributions), "source_contributions": contributions}
    value = {"distance": distance, "result": result}
    if converged:
        value["mapped"] = contributions
        value["ranking"] = joint.native.ranking_changes(central, contributions)
        value["ranking_rounded_5dp"] = joint.native.ranking_changes(central, contributions, 5)
    return value


class JointProfileSyntheticTests(unittest.TestCase):
    def test_frozen_config_and_dependencies_have_pre_fit_identities(self):
        config = joint.configuration()
        self.assertTrue(config["frozen_before_first_joint_fit"])
        self.assertEqual(config["maximum_grid_per_sample"], 120)

    def test_cartesian_grid_size_distance_and_central_identity(self):
        families = joint.configuration()["families"]
        retained = ["SOIL03", "BAMAJC", "SFCRUC", "MOVES2", "AMSUL"]
        rows = joint.grid(retained, families)
        self.assertEqual(len(rows), 120)
        self.assertEqual(rows[0], {"source_ids": retained, "distance": 0})
        self.assertEqual(sum(r["distance"] == 1 for r in rows), 10)
        self.assertEqual(max(r["distance"] for r in rows), 4)
        self.assertTrue(all(r["source_ids"][-1] == "AMSUL" for r in rows))

    def test_removed_central_slot_is_not_reintroduced(self):
        rows = joint.grid(["SOIL03", "MOVES2", "AMSUL"], joint.configuration()["families"])
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(len(r["source_ids"]) == 3 for r in rows))
        self.assertFalse(any("BAMAJC" in r["source_ids"] for r in rows))

    def test_duplicate_slots_and_wrong_central_option_rejected(self):
        with self.assertRaises(ValueError):
            joint.grid(["a", "a"], {})
        with self.assertRaises(ValueError):
            joint.grid(["a"], {"a": ["b", "a"]})
        with self.assertRaises(ValueError):
            joint.grid(["a"], {"a": ["a", "a"]})

    def test_family_mapping_keeps_negative_values_and_central_slot_order(self):
        result = {"source_ids": ["SOIL12", "MOVES4"], "source_contributions": {"MOVES4": 5, "SOIL12": -0.2}}
        self.assertEqual(joint.mapped_contributions(result, ["SOIL03", "MOVES2"], joint.configuration()["labels"]),
                         {"soil": -0.2, "vehicle": 5})

    def test_nonconvergence_prevents_certificate_even_if_terminal_diagnostics_fail(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 3, "b": 2, "c": 1}),
                row(2, {"a": 4, "b": 2, "c": 1}, converged=False, r2=0.01)]
        got = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertTrue(got["complete_local_stable"])
        self.assertFalse(got["complete_joint_stable"])
        self.assertEqual(got["status"], "UNRESOLVED")
        self.assertEqual(got["unresolved_count"], 1)

    def test_complete_local_stability_can_have_joint_witness(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 3, "b": 2, "c": 1}),
                row(2, {"a": 2, "b": 3, "c": 1})]
        got = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertTrue(got["complete_local_stable_joint_witness"])
        self.assertEqual(got["minimum_observed_witness_distance"], 2)
        self.assertTrue(got["minimum_witness_distance_exact_on_grid"])

    def test_observed_local_stability_is_not_complete_when_unresolved(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 3, "b": 2, "c": 1}),
                row(1, {"a": 0, "b": 0, "c": 0}, converged=False), row(2, {"a": 2, "b": 3, "c": 1})]
        got = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertTrue(got["observed_local_stable_joint_witness"])
        self.assertFalse(got["complete_local_stable_joint_witness"])
        self.assertFalse(got["minimum_witness_distance_exact_on_grid"])

    def test_vacuous_local_stability_not_counted(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 3, "b": 2, "c": 1}, r2=0.1),
                row(2, {"a": 2, "b": 3, "c": 1})]
        got = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertEqual(got["local_admitted_alternative_count"], 0)
        self.assertFalse(got["observed_local_stable"])

    def test_central_screen_exclusion_prevents_comparison(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}, mass=60), row(1, {"a": 2, "b": 3, "c": 1})]
        strict = joint.summarize_decisions(rows, "strict", "largest_source_change")
        basic = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertFalse(strict["central_eligible"])
        self.assertEqual(strict["status"], "CENTRAL_INELIGIBLE")
        self.assertEqual(strict["admitted_count"], 0)
        self.assertEqual(basic["joint_changed_count"], 1)

    def test_top_ties_are_not_arbitrarily_broken(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 3, "b": 3, "c": 1})]
        self.assertTrue(rows[1]["ranking"]["top_tie"])
        got = joint.summarize_decisions(rows, "basic", "largest_source_change")
        self.assertEqual(got["joint_changed_count"], 1)
        self.assertEqual(joint.pairwise_certificate(rows, "basic")["observed_possible_top_families"], ["a", "b"])

    def test_partial_order_margin_and_missing_certificate(self):
        rows = [row(0, {"a": 4, "b": 2, "c": 1}), row(1, {"a": 2, "b": 3, "c": 1})]
        cert = joint.pairwise_certificate(rows, "basic")
        self.assertEqual(cert["status"], "COMPLETE_FINITE_GRID")
        self.assertEqual(sum(p["certified_on_full_diagnostic_admissible_grid"] for p in cert["pairs"]), 2)
        rows.append(row(2, {"a": 0, "b": 0, "c": 0}, converged=False))
        cert = joint.pairwise_certificate(rows, "basic")
        self.assertFalse(cert["top_set_complete_on_grid"])
        self.assertEqual(sum(p["certified_on_full_diagnostic_admissible_grid"] for p in cert["pairs"]), 0)

    def test_output_cannot_redirect_private_ledger_to_public(self):
        with self.assertRaises(ValueError):
            joint.validate_output_paths(joint.native.DEFAULT_INPUT, joint.PUBLIC, joint.PUBLIC)
        with self.assertRaises(ValueError):
            joint.validate_output_paths(joint.PUBLIC, joint.PUBLIC, joint.PRIVATE)

    def test_numerical_failure_is_recorded_unresolved(self):
        control = {"converged": True, "source_ids": ["SOIL03"], "source_contributions": {"SOIL03": 1},
                   "R2": 0.9, "reduced_chi2": 1, "percent_mass": 100}
        receptor = {key: "x" for key in joint.native.CONFIG["case_identity"]}
        with patch.object(joint.native, "central_fit", return_value=control), patch.object(
                joint.native, "effective_variance_fit", side_effect=ValueError("rank deficient")):
            fitted = joint.fit_sample(receptor, {}, joint.configuration())
        self.assertEqual(len(fitted["rows"]), 4)
        self.assertEqual(fitted["summaries"]["basic"]["top"]["unresolved_count"], 3)


@unittest.skipUnless(all((joint.native.DEFAULT_INPUT / name).is_file() for name in joint.native.TRUSTED_ARCHIVE_HASHES),
                     "official EPA archives unavailable; integration explicitly skipped")
class JointNativeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = joint.configuration()
        joint.native.archive_inventory(joint.native.DEFAULT_INPUT)
        receptors, profiles, _ = joint.native.load_inputs(joint.native.DEFAULT_INPUT)
        cls.samples = [joint.fit_sample(receptor, profiles, config) for receptor in receptors]
        cls.summary = joint.aggregate(cls.samples)

    def test_distance_one_reproduces_frozen_prior_one_at_a_time_counts(self):
        distance_one = self.summary["attrition_by_distance"]["1"]
        self.assertEqual(distance_one["attempted"], 345)
        self.assertEqual(distance_one["converged_count"], 323)
        self.assertEqual(distance_one["unresolved"], 22)
        self.assertEqual(distance_one["basic"], {"central_and_alternative_eligible": 283, "top_changed": 62, "order_changed": 133})
        self.assertEqual(distance_one["strict"], {"central_and_alternative_eligible": 26, "top_changed": 2, "order_changed": 10})

    def test_all_samples_and_every_enumerated_choice_accounted_for(self):
        self.assertEqual(self.summary["initial_samples"], 35)
        self.assertEqual(self.summary["central_converged_samples"], 35)
        for distance, counts in self.summary["attrition_by_distance"].items():
            self.assertEqual(counts["attempted"], counts["converged_count"] + counts["unresolved"])
        for sample in self.samples:
            self.assertEqual(sum(row["distance"] == 0 for row in sample["rows"]), 1)
            self.assertEqual(len({tuple(row["source_ids"]) for row in sample["rows"]}), len(sample["rows"]))

    def test_converged_rows_never_clip_negative_values(self):
        negative = 0
        for sample in self.samples:
            for row in sample["rows"]:
                if row["result"]["converged"]:
                    self.assertEqual(list(row["mapped"].values()), list(row["result"]["source_contributions"].values()))
                    negative += any(v < 0 for v in row["mapped"].values())
        self.assertGreater(negative, 0)


if __name__ == "__main__":
    unittest.main()
