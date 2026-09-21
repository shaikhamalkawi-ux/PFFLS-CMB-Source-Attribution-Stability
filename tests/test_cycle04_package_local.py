import hashlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_cycle04_submission_gate import (  # noqa: E402
    validate_artifact_manifest,
    validate_cycle04_payload,
    validate_return_package,
)


EXPECTED_CLAIMS = {
    "JRC_DAILY_SAMPLES": ("JRC", "daily_samples", 364, None),
    "JRC_SPECIES": ("JRC", "species", 38, None),
    "JRC_PROFILE_SETS": ("JRC", "frozen_profile_sets", 12, None),
    "JRC_COMPARISONS": ("JRC", "prespecified_one_profile_comparisons", 30, None),
    "JRC_DISCORDANCE": (
        "JRC",
        "primary_lower_mean_reduced_chi_square_discordances",
        9,
        "JRC_COMPARISONS",
    ),
    "EPA_ELIGIBLE": ("EPA", "eligible_substitutions", 345, None),
    "EPA_CONVERGED": ("EPA", "converged", 323, None),
    "EPA_TWO_DIAGNOSTIC": (
        "EPA",
        "preserved_r2_and_reduced_chi_square_ranges",
        283,
        None,
    ),
    "EPA_ORDERING": (
        "EPA",
        "ordering_changes_within_two_diagnostic_set",
        133,
        "EPA_TWO_DIAGNOSTIC",
    ),
    "EPA_LARGEST": (
        "EPA",
        "largest_source_changes_within_two_diagnostic_set",
        62,
        "EPA_TWO_DIAGNOSTIC",
    ),
    "EPA_STRICT_SUBSET": ("EPA", "also_preserved_percent_mass", 26, None),
    "EPA_STRICT_ORDERING": (
        "EPA",
        "ordering_changes_within_strict_subset",
        10,
        "EPA_STRICT_SUBSET",
    ),
    "EPA_STRICT_LARGEST": (
        "EPA",
        "largest_source_changes_within_strict_subset",
        2,
        "EPA_STRICT_SUBSET",
    ),
}
EXPECTED_CANDIDATE_SHA256 = (
    "9be0a8bc9c653b7c9517f947b145947fcb82c9a1cf2106bcd088b361d329d5e2"
)
EXPECTED_REVIEWED_STATIC_SHA256 = {
    ".gitattributes": "53a57c423556328e906465e0a18c8d3fbe1ac9d8d3cd267ab027244ede3045d5",
    "requirements-cycle04.txt": "bbe749e9ee4041fc88b03993741c82f3220a28a957178b2b844eb7a54dd8e219",
    "tasks/CODEX_CYCLE_04_SUBMISSION_CANDIDATE_RECONSTRUCTION.md": "14df1c74f17a117223cec1cbc2fa08cebe140a54c968c608e0355186e57ce663",
    "outputs/cycle04/README.md": "f05514548a8274366ed09546892120553b01e87d78efef6287320680980c4b20",
    "outputs/cycle04/baseline_search_manifest.csv": "42a1713c133e9e19dc56df9dc3b56e447727aa83de1506510333483120b55b49",
    "outputs/cycle04/historical_manuscript_inventory.csv": "893093a1381bf21050226ac9aa908dddcbdf5616077deb6c04a6f61ee8816b3e",
    "outputs/cycle04/historical_anchor_extraction.json": "8208b0e31883bdcde35360a38d154c94a720b59a5d1be162a659fecabc54455f",
    "outputs/cycle04/LOCKED_RESULTS.json": "2c54b438a3d5b00be1526ec99f7e5374662afe8f3debb946d04bf2161c034242",
    "outputs/cycle04/claim_evidence_traceability.csv": "f00367bac2e202fab13d3c1bf8b204ab4dee305d94aa2c25e876a230052127d7",
    "outputs/cycle04/reproducibility_gap_register.csv": "dcd04284cce0e6f109118d2a2ca0c3e4175dcc59e5db6e518025ff7d437a1f2b",
    "outputs/cycle04/LINEAGE_DECISION.md": "7453fce51c5b0a0da8e2a886d94617f3ad4a982e23ff280ec19c2b44f92e3e65",
    "outputs/cycle04/CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md": "9be0a8bc9c653b7c9517f947b145947fcb82c9a1cf2106bcd088b361d329d5e2",
    "outputs/cycle04/SUBMISSION_READINESS_MATRIX.csv": "80a87d872c8acf7cd42b2debca61d321979222a13f00d0a3b0ade00ba33ca07a",
    "outputs/cycle04/KEEP_HOLD_REMOVE.md": "c5ff9505d1633982b3706662a762ddddda7ad2f072cb33195faa89344739e933",
    "outputs/cycle04/SCIENTIFIC_CHANGELOG.md": "5ce3472643d77def4b807943b5e80c771fa7c251175b47008a197db08f66ccd1",
    "outputs/cycle04/EDITORIAL_RECOMMENDATION.md": "02ab455d68e280c2961c05926d9b9942ab230320166124205dd441b69839f632",
    "outputs/cycle04/reproduction.md": "c29b3549c57b75aadbe6c73bb75a4081e7ccea83119dcb0b197a15222373dce5",
}


class Cycle04PackageLocalTests(unittest.TestCase):
    def test_payload_validates_without_legacy_repository_files(self):
        report = validate_cycle04_payload(ROOT)
        self.assertEqual(report["overall_status"], "HOLD_WITH_EXACT_BLOCKERS")
        self.assertFalse(report["baseline_promoted"])
        self.assertFalse(report["central_results_recomputed"])
        self.assertEqual(report["baseline_search"]["candidate_artifact_count"], 0)
        self.assertEqual(report["reproducibility_gaps"]["pending_external_channel_count"], 2)
        self.assertEqual(report["reproducibility_gaps"]["submission_blocker_count"], 4)
        self.assertEqual(report["reproducibility_gaps"]["nonblocking_archival_gap_count"], 3)
        self.assertEqual(report["readiness"]["blocked_gate_count"], 6)
        self.assertEqual(report["readiness"]["nonblocking_limitation_gate_count"], 4)
        self.assertEqual(len(report["exact_blockers"]), 4)
        self.assertEqual(len(report["nonblocking_archival_reproducibility_gaps"]), 3)

    def test_claim_values_and_schema_match_independent_literal_oracle(self):
        path = ROOT / "outputs" / "cycle04" / "LOCKED_RESULTS.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        actual = {
            claim["id"]: (
                claim["layer"],
                claim["metric"],
                claim["value"],
                claim.get("denominator_claim_id"),
            )
            for claim in data["claims"]
        }
        self.assertEqual(actual, EXPECTED_CLAIMS)
        self.assertTrue(all(not claim["recomputed_from_raw"] for claim in data["claims"]))

    def test_candidate_delta_matches_reviewed_canonical_bytes(self):
        path = (
            ROOT
            / "outputs"
            / "cycle04"
            / "CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md"
        )
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            EXPECTED_CANDIDATE_SHA256,
        )

    def test_all_reviewed_static_files_match_independent_literal_oracle(self):
        for relative, expected in EXPECTED_REVIEWED_STATIC_SHA256.items():
            with self.subTest(relative=relative):
                path = ROOT / Path(relative)
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_artifact_manifest_verifies_all_payload_identities(self):
        report = validate_artifact_manifest(
            ROOT, require_exact_tree=not (ROOT / "PROJECT_STATE.md").is_file()
        )
        self.assertEqual(report["manifest_entry_count"], report["identity_match_count"])

    def test_extracted_return_package_is_self_validating(self):
        if (ROOT / "PROJECT_STATE.md").is_file():
            report = validate_artifact_manifest(ROOT, require_exact_tree=False)
            self.assertFalse(report["exact_tree_verified"])
        else:
            report = validate_return_package(ROOT)
            self.assertEqual(report["package_local_validation"], "PASS")
            self.assertTrue(report["artifact_manifest"]["exact_tree_verified"])


if __name__ == "__main__":
    unittest.main()
