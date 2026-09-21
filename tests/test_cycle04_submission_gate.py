import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_cycle04_package import (  # noqa: E402
    MANIFEST_RELATIVE_PATH,
    PACKAGE_NAME,
    PACKAGE_RELATIVE_PATHS,
    build,
)
from validate_cycle04_submission_gate import (  # noqa: E402
    ANCHOR_SHA256,
    EXPECTED_CLAIMS,
    EXPECTED_CYCLE01_MISMATCHES,
    LOCKED_BASELINE,
    validate_artifact_manifest,
    validate_repository,
)


class Cycle04SubmissionGateTests(unittest.TestCase):
    def setUp(self):
        self.output = ROOT / "outputs" / "cycle04"

    def copy_repository(self, destination: Path) -> Path:
        target = destination / "repository"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(
                ".git", "_deliverables", "tmp", "__pycache__", "*.pyc"
            ),
        )
        return target

    @staticmethod
    def rewrite_csv(path: Path, mutate) -> None:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            rows = list(reader)
        mutate(rows)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def rewrite_json(path: Path, mutate) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

    def test_repository_closes_hold_with_exact_blockers(self):
        report = validate_repository(ROOT)
        self.assertEqual(report["overall_status"], "HOLD_WITH_EXACT_BLOCKERS")
        self.assertEqual(report["baseline"], LOCKED_BASELINE)
        self.assertFalse(report["baseline_promoted"])
        self.assertFalse(report["manuscript_change_authorized"])
        self.assertFalse(report["central_results_recomputed"])
        self.assertEqual(report["reproducibility_gaps"]["submission_blocker_count"], 4)
        self.assertEqual(report["reproducibility_gaps"]["nonblocking_archival_gap_count"], 3)
        self.assertEqual(report["readiness"]["blocked_gate_count"], 6)
        self.assertEqual(report["readiness"]["nonblocking_limitation_gate_count"], 4)
        self.assertEqual(len(report["exact_blockers"]), 4)
        self.assertEqual(len(report["nonblocking_archival_reproducibility_gaps"]), 3)
        self.assertEqual(report["locked_results"]["claim_count"], 13)
        self.assertEqual(report["locked_results"]["recomputed_claim_count"], 0)
        self.assertEqual(report["baseline_search"]["exact_artifact_found"], False)
        self.assertEqual(report["historical_inventory"]["historical_anchor"], "R3l")
        self.assertEqual(
            report["historical_inventory"]["historical_anchor_sha256"],
            ANCHOR_SHA256,
        )

    def test_locked_number_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "LOCKED_RESULTS.json"

            def mutate(data):
                next(
                    claim for claim in data["claims"] if claim["id"] == "EPA_LARGEST"
                )["value"] = 63

            self.rewrite_json(path, mutate)
            with self.assertRaisesRegex(ValueError, "locked claim changed"):
                validate_repository(repo)

    def test_baseline_promotion_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "LOCKED_RESULTS.json"

            def mutate(data):
                data["baseline"]["binary_status"] = "RECOVERED"
                data["baseline"]["promoted_by_cycle04"] = True

            self.rewrite_json(path, mutate)
            with self.assertRaisesRegex(ValueError, "promoted without evidence"):
                validate_repository(repo)

    def test_unverified_recomputation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "claim_evidence_traceability.csv"

            def mutate(rows):
                rows[0]["recomputed_from_raw"] = "yes"

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "overstates recomputation"):
                validate_repository(repo)

    def test_unverified_baseline_search_hit_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "baseline_search_manifest.csv"

            def mutate(rows):
                rows[0]["exact_artifact_found"] = "yes"

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "unverified exact baseline recovery"):
                validate_repository(repo)

    def test_candidate_identity_warning_is_mandatory(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = (
                repo
                / "outputs"
                / "cycle04"
                / "CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md"
            )
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(" — NOT R3nR7-AE — NOT BASELINE", ""),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "candidate delta differs"):
                validate_repository(repo)

    def test_claim_metric_and_denominator_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "LOCKED_RESULTS.json"

            def mutate(data):
                claim = next(
                    item for item in data["claims"] if item["id"] == "EPA_ORDERING"
                )
                claim["metric"] = "accuracy_wins"
                claim["denominator_claim_id"] = "EPA_ELIGIBLE"

            self.rewrite_json(path, mutate)
            with self.assertRaisesRegex(ValueError, "locked claim schema changed"):
                validate_repository(repo)

    def test_explicit_false_accuracy_and_baseline_claims_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = (
                repo
                / "outputs"
                / "cycle04"
                / "CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md"
            )
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\nEPA data demonstrate external predictive accuracy.\n"
                + "R3l is the authoritative locked baseline.\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "candidate delta differs"):
                validate_repository(repo)

    def test_readiness_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "SUBMISSION_READINESS_MATRIX.csv"

            def mutate(rows):
                overall = next(row for row in rows if row["gate_id"] == "OVERALL")
                overall["status"] = "READY_FOR_SUBMISSION"
                overall["disposition"] = "KEEP"

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "improperly promotes"):
                validate_repository(repo)

    def test_pending_external_channel_cannot_be_closed_silently(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "reproducibility_gap_register.csv"

            def mutate(rows):
                next(row for row in rows if row["gap_id"] == "GAP-09")["status"] = (
                    "FAILED"
                )

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "treated as closed"):
                validate_repository(repo)

    def test_search_result_count_and_snapshot_hash_are_locked(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "baseline_search_manifest.csv"

            def mutate(rows):
                row = next(
                    item for item in rows if item["search_id"] == "drive_archive"
                )
                row["result_count"] = "2"

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "baseline search record changed"):
                validate_repository(repo)

    def test_historical_hash_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            path = repo / "outputs" / "cycle04" / "historical_manuscript_inventory.csv"

            def mutate(rows):
                next(row for row in rows if row["version"] == "R3l")["sha256"] = (
                    "0" * 64
                )

            self.rewrite_csv(path, mutate)
            with self.assertRaisesRegex(ValueError, "historical identity changed"):
                validate_repository(repo)

    def test_reviewed_scientific_and_provenance_text_cannot_drift(self):
        mutations = {
            "false_readme_claim": (
                Path("outputs/cycle04/README.md"),
                lambda path: path.write_text(
                    path.read_text(encoding="utf-8")
                    + "\nR3l is the exact locked baseline and EPA proves external accuracy.\n",
                    encoding="utf-8",
                    newline="\n",
                ),
            ),
            "resolved_baseline_gap": (
                Path("outputs/cycle04/reproducibility_gap_register.csv"),
                lambda path: self.rewrite_csv(
                    path,
                    lambda rows: next(
                        row for row in rows if row["gap_id"] == "GAP-01"
                    ).update(status="RESOLVED", evidence="Exact baseline recovered"),
                ),
            ),
            "external_validation_gate": (
                Path("outputs/cycle04/SUBMISSION_READINESS_MATRIX.csv"),
                lambda path: self.rewrite_csv(
                    path,
                    lambda rows: next(
                        row for row in rows if row["gate_id"] == "SCI-02"
                    ).update(
                        status="PASS_EXTERNAL_VALIDATION",
                        evidence="EPA proves external accuracy",
                    ),
                ),
            ),
            "anchor_provenance": (
                Path("outputs/cycle04/historical_anchor_extraction.json"),
                lambda path: self.rewrite_json(
                    path,
                    lambda data: data.update(
                        drive_file_id="unreviewed-id",
                        observed_title="R3l is the locked baseline",
                    ),
                ),
            ),
        }
        for name, (relative, mutate) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                repo = self.copy_repository(Path(directory))
                mutate(repo / relative)
                with self.assertRaisesRegex(ValueError, "reviewed static content changed"):
                    validate_repository(repo)

    def test_exact_tree_rejects_unallowlisted_root_pyc(self):
        with tempfile.TemporaryDirectory() as directory:
            package_root = Path(directory) / PACKAGE_NAME
            for relative in PACKAGE_RELATIVE_PATHS:
                source = ROOT / relative
                destination = package_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            manifest_source = ROOT / MANIFEST_RELATIVE_PATH
            manifest_destination = package_root / MANIFEST_RELATIVE_PATH
            manifest_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(manifest_source, manifest_destination)
            (package_root / "unexpected_payload.pyc").write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "extra=.*unexpected_payload.pyc"):
                validate_artifact_manifest(package_root, require_exact_tree=True)

    def test_restricted_or_unexpected_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = self.copy_repository(Path(directory))
            (repo / "outputs" / "cycle04" / "candidate_manuscript.pdf").write_bytes(
                b"not a PDF"
            )
            with self.assertRaisesRegex(ValueError, "restricted artifact"):
                validate_repository(repo)

    def test_legacy_manifest_audit_records_known_state(self):
        report = validate_repository(ROOT)["legacy_manifest_audit"]
        self.assertEqual(
            set(report["cycle01"]["mismatched"]), EXPECTED_CYCLE01_MISMATCHES
        )
        self.assertEqual(report["cycle01"]["missing"], [])
        for name in ("cycle02", "cycle03", "outreach03"):
            self.assertEqual(report[name]["missing"], [])
            self.assertEqual(report[name]["mismatched"], [])

    def test_builder_is_deterministic_and_members_are_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            zip_one, sidecar_one = build(ROOT, destination / "one")
            zip_two, sidecar_two = build(ROOT, destination / "two")
            digest_one = hashlib.sha256(zip_one.read_bytes()).hexdigest()
            digest_two = hashlib.sha256(zip_two.read_bytes()).hexdigest()
            self.assertEqual(digest_one, digest_two)
            expected_sidecar = f"{digest_one}  {zip_one.name}\n"
            self.assertEqual(sidecar_one.read_text(encoding="ascii"), expected_sidecar)
            self.assertEqual(sidecar_two.read_text(encoding="ascii"), expected_sidecar)

            expected_members = {
                f"{PACKAGE_NAME}/{path.as_posix()}" for path in PACKAGE_RELATIVE_PATHS
            }
            expected_members.add(
                f"{PACKAGE_NAME}/{MANIFEST_RELATIVE_PATH.as_posix()}"
            )
            with zipfile.ZipFile(zip_one) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), expected_members)
                self.assertFalse(
                    any(
                        name.casefold().endswith(
                            (".pdf", ".docx", ".xlsx", ".zip", ".mdb", ".accdb")
                        )
                        for name in archive.namelist()
                    )
                )
                manifest_member = (
                    f"{PACKAGE_NAME}/{MANIFEST_RELATIVE_PATH.as_posix()}"
                )
                manifest_rows = list(
                    csv.DictReader(
                        archive.read(manifest_member).decode("utf-8").splitlines()
                    )
                )
                self.assertEqual(len(manifest_rows), len(PACKAGE_RELATIVE_PATHS))
                for row in manifest_rows:
                    member = f"{PACKAGE_NAME}/{row['relative_path']}"
                    self.assertIn(member, expected_members)
                    payload = archive.read(member)
                    self.assertEqual(len(payload), int(row["bytes"]))
                    self.assertEqual(
                        hashlib.sha256(payload).hexdigest(), row["sha256"]
                    )

    def test_builder_fails_on_missing_allowlisted_file(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            repo = self.copy_repository(destination)
            (repo / "scripts" / "validate_cycle04_submission_gate.py").unlink()
            with self.assertRaisesRegex(FileNotFoundError, "required Cycle 04 package"):
                build(repo, destination / "build")

    def test_builder_fails_on_manifest_drift_without_mutating_it(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            repo = self.copy_repository(destination)
            manifest = repo / MANIFEST_RELATIVE_PATH
            before = manifest.read_bytes()
            requirements = repo / "requirements-cycle04.txt"
            requirements.write_text(
                requirements.read_text(encoding="utf-8") + "# reviewed drift\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "reviewed static content changed"):
                build(repo, destination / "build")
            self.assertEqual(manifest.read_bytes(), before)

    def test_builder_fails_on_stale_qa_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            repo = self.copy_repository(destination)
            test_record = repo / "outputs" / "cycle04" / "test_results.txt"
            text = test_record.read_text(encoding="utf-8")
            current_count = int(
                next(
                    line.split(":", 1)[1].strip()
                    for line in text.splitlines()
                    if line.startswith("tests_run:")
                )
            )
            test_record.write_text(
                text.replace(
                    f"tests_run: {current_count}", f"tests_run: {current_count + 1}"
                ),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "qa_report.json is stale"):
                build(repo, destination / "build")

    def test_builder_rejects_destination_inside_controlled_output(self):
        with self.assertRaisesRegex(ValueError, "must not be at or below"):
            build(ROOT, ROOT / "outputs" / "cycle04" / "package")

    def test_claim_registry_has_exact_expected_values(self):
        data = json.loads((self.output / "LOCKED_RESULTS.json").read_text(encoding="utf-8"))
        actual = {claim["id"]: claim["value"] for claim in data["claims"]}
        self.assertEqual(actual, EXPECTED_CLAIMS)


if __name__ == "__main__":
    unittest.main()
