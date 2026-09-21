import csv
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_outreach_package import (  # noqa: E402
    LOCKED_BASELINE,
    validate_contacts,
    validate_package,
    validate_status,
)
from build_outreach_package import (  # noqa: E402
    MANIFEST_RELATIVE_PATH,
    PACKAGE_NAME,
    build,
)


class OutreachPackageTests(unittest.TestCase):
    def setUp(self):
        self.package = ROOT / "outputs" / "outreach03"

    def copy_package(self, parent: Path) -> Path:
        destination = parent / "outreach03"
        shutil.copytree(self.package, destination)
        return destination

    @staticmethod
    def rewrite_csv(path: Path, mutate) -> None:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or ())
            rows = list(reader)
        mutate(rows)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_repository_package_validates_fail_closed(self):
        report = validate_package(self.package)
        self.assertEqual(report["status"]["request_count"], 3)
        self.assertEqual(report["status"]["status_counts"], {"BLOCKED_USER_ACTION": 3})
        self.assertEqual(report["status"]["provider_confirmed_count"], 0)
        self.assertEqual(report["status"]["codex_transmission_count"], 0)
        self.assertEqual(report["contacts"]["contact_count"], 8)
        self.assertEqual(report["contacts"]["verified_official_count"], 8)
        self.assertEqual(report["content"]["locked_baseline"], LOCKED_BASELINE)
        self.assertFalse(report["content"]["manuscript_change_authorized"])
        self.assertFalse(report["content"]["direct_transmission_authorized"])

    def test_missing_required_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            (package / "03_ADEC_SUBMISSION_INSTRUCTIONS.md").unlink()
            with self.assertRaisesRegex(ValueError, "missing required package files"):
                validate_package(package)

    def test_invalid_status_and_unconfirmed_codex_send_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            status_path = package / "OUTREACH_STATUS.csv"

            def mutate(rows):
                rows[0]["sent_or_submitted_by_codex"] = "yes"

            self.rewrite_csv(status_path, mutate)
            with self.assertRaisesRegex(ValueError, "without provider confirmation"):
                validate_status(status_path)

    def test_user_reported_send_cannot_be_promoted_without_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            status_path = package / "OUTREACH_STATUS.csv"

            def mutate(rows):
                rows[0]["status"] = "SENT"

            self.rewrite_csv(status_path, mutate)
            with self.assertRaisesRegex(ValueError, "SENT without provider confirmation"):
                validate_status(status_path)

    def test_contact_email_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            contacts_path = package / "CONTACTS_VERIFIED.csv"

            def mutate(rows):
                rows[0]["email"] = "unverified@example.invalid"

            self.rewrite_csv(contacts_path, mutate)
            with self.assertRaisesRegex(ValueError, "contact emails changed"):
                validate_contacts(contacts_path)

    def test_content_guard_rejects_baseline_change(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            readme = package / "README.md"
            text = readme.read_text(encoding="utf-8")
            readme.write_text(
                text.replace(LOCKED_BASELINE, "PFFLS R99-UNREVIEWED"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required content"):
                validate_package(package)

    def test_manuscript_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(Path(directory))
            (package / "candidate_manuscript.docx").write_bytes(b"not a document")
            with self.assertRaisesRegex(ValueError, "manuscript-like artifacts"):
                validate_package(package)

    def test_builder_is_deterministic_and_manifest_matches_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            zip_one, sidecar_one = build(ROOT, temp_root / "build-one")
            zip_two, sidecar_two = build(ROOT, temp_root / "build-two")

            digest_one = hashlib.sha256(zip_one.read_bytes()).hexdigest()
            digest_two = hashlib.sha256(zip_two.read_bytes()).hexdigest()
            self.assertEqual(digest_one, digest_two)

            expected_sidecar = f"{digest_one}  {zip_one.name}\n"
            self.assertEqual(sidecar_one.read_text(encoding="ascii"), expected_sidecar)
            self.assertEqual(sidecar_two.read_text(encoding="ascii"), expected_sidecar)

            manifest_member = (
                f"{PACKAGE_NAME}/{MANIFEST_RELATIVE_PATH.as_posix()}"
            )
            with zipfile.ZipFile(zip_one) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                self.assertIn(manifest_member, names)
                manifest_lines = archive.read(manifest_member).decode("utf-8").splitlines()
                self.assertTrue(manifest_lines)

                manifested_members = set()
                for line in manifest_lines:
                    expected_digest, relative = line.split("  ", 1)
                    member = f"{PACKAGE_NAME}/{relative}"
                    manifested_members.add(member)
                    self.assertIn(member, names)
                    actual_digest = hashlib.sha256(archive.read(member)).hexdigest()
                    self.assertEqual(actual_digest, expected_digest)

                self.assertEqual(names, manifested_members | {manifest_member})


if __name__ == "__main__":
    unittest.main()
