"""Private-return packaging tests with exclusively synthetic file contents."""

from io import BytesIO
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_received_fairbanks_return as builder  # noqa: E402


def synthetic_zip(names):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in names:
            archive.writestr(name, b"Synthetic fixture; not investigator data.")
    return buffer.getvalue()


class ReceivedFairbanksPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        for name in builder.REPOSITORY_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Synthetic repository fixture.\n")
        self.private = self.root / "private/received_fairbanks/independent_reproduction"
        self.private.mkdir(parents=True)
        for name in builder.PRIVATE_FILES:
            (self.private / name).write_bytes(b"Synthetic private fixture.\n")
        summary = b'{"synthetic": true}\n'
        (self.private / "aggregate_summary.json").write_bytes(summary)
        (self.root / "outputs/received_fairbanks/aggregate_summary.json").write_bytes(summary)
        self.candidate = Path(self.temp.name) / "candidate"
        self.candidate.mkdir()
        for name in builder.CANDIDATE_FILES:
            path = self.candidate / name
            path.write_bytes(synthetic_zip(["source.tex"]) if name.endswith(".zip") else b"Synthetic candidate.\n")
        self.refresh_candidate_manifest()
        self.source = Path(self.temp.name) / "private_original.zip"
        self.source.write_bytes(synthetic_zip(sorted(builder.EXPECTED_ORIGINAL_MEMBERS)))
        # Production is fail-closed to the registered private hash. Tests replace
        # that literal only within this synthetic fixture's controlled context.
        self.hash_patch = patch.object(builder, "EXPECTED_ZIP_SHA256", builder.sha256(self.source.read_bytes()))
        self.hash_patch.start()
        self.addCleanup(self.hash_patch.stop)
        self.output = self.root / "private/received_fairbanks/return/fixture"

    def refresh_candidate_manifest(self):
        lines = [f"{builder.sha256((self.candidate / name).read_bytes())}  {name}"
                 for name in sorted(set(builder.CANDIDATE_FILES) - {"SHA256SUMS.txt"})]
        (self.candidate / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def build(self, output=None):
        return builder.build(self.root, self.source, self.candidate, output or self.output)

    def test_deterministic_bytes_manifest_crc_and_sidecar(self):
        first, first_sha, digest, count = self.build()
        second, _, second_digest, second_count = self.build(self.output.parent / "second")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(digest, second_digest)
        self.assertEqual(count, second_count)
        self.assertEqual(count, len(builder.REPOSITORY_FILES) + len(builder.PRIVATE_FILES) + len(builder.CANDIDATE_FILES) + 2)
        self.assertEqual(first_sha.read_text(encoding="ascii"), f"{digest}  {first.name}\n")
        with zipfile.ZipFile(first) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))
            self.assertTrue(all(item.date_time == builder.FIXED_ZIP_TIME for item in archive.infolist()))
            readme = archive.read(f"{builder.PACKAGE_NAME}/README.md").decode("utf-8")
            self.assertIn("NOT PUBLIC", readme)
            self.assertIn("52", readme)
            self.assertIn("53-row", readme)
            self.assertIn("54-row", readme)
            self.assertNotIn(str(self.temp.name), readme)
        contents = builder.payloads(self.root, self.source, self.candidate)
        contents["artifact_manifest_sha256.csv"] = builder.manifest_bytes(contents)
        self.assertEqual(builder.verify_return(first, contents), digest)

    def test_same_output_is_idempotent_but_changed_output_is_preserved(self):
        target, _, digest, _ = self.build()
        self.assertEqual(self.build()[2], digest)
        (self.root / "README.md").write_text("Changed synthetic contents.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Existing private return differs"):
            self.build()
        self.assertEqual(builder.sha256(target.read_bytes()), digest)
        self.assertFalse(list(self.output.glob(".private-return-*")))

    def test_raw_output_cannot_be_routed_to_public_directory(self):
        with self.assertRaisesRegex(ValueError, "must remain below"):
            self.build(self.root / "outputs/public")

    def test_missing_required_report_is_fail_closed(self):
        (self.root / "outputs/received_fairbanks/AUDIT_REPORT.md").unlink()
        with self.assertRaisesRegex(ValueError, "Required repository file missing"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_unexpected_candidate_file_rejected(self):
        (self.candidate / "unrequested.txt").write_text("Unexpected", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unexpected/missing directory files"):
            self.build()

    def test_unexpected_private_file_or_directory_rejected(self):
        (self.private / "extra").mkdir()
        with self.assertRaisesRegex(ValueError, "Unexpected/missing directory files"):
            self.build()

    def test_changed_original_private_zip_rejected(self):
        self.source.write_bytes(self.source.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "Original attachment SHA256 mismatch"):
            self.build()

    def test_changed_candidate_sha_rejected(self):
        (self.candidate / "CHANGE_NOTE.md").write_text("Changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Candidate SHA256 mismatch"):
            self.build()

    def test_candidate_sha_manifest_must_be_complete_and_nonduplicated(self):
        manifest = self.candidate / "SHA256SUMS.txt"
        lines = manifest.read_text(encoding="utf-8").splitlines()
        manifest.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exactly four"):
            self.build()
        manifest.write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unexpected/duplicate"):
            self.build()

    def test_private_and_public_aggregates_must_match(self):
        (self.private / "aggregate_summary.json").write_text('{"different":true}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "aggregate summaries differ"):
            self.build()

    def test_local_absolute_user_path_in_prose_rejected(self):
        (self.root / "outputs/received_fairbanks/AUDIT_REPORT.md").write_text(
            "Accidental path C:\\Users\\synthetic\\private.xlsx", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Local absolute user path leaked"):
            self.build()

    def test_path_traversal_and_absolute_archive_names_rejected(self):
        for member in ("../x", "/absolute", "a/../x", "a\\x", "C:/absolute", "a//b", "./x"):
            with self.subTest(member=member), self.assertRaises(ValueError):
                builder.safe_member(member)
        with self.assertRaisesRegex(ValueError, "Path traversal"):
            builder.checked_path(self.root / "private/../outputs")

    def test_filesystem_symlink_rejected_without_following_it(self):
        target = self.candidate / "CHANGE_NOTE.md"
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda path: path == target or original(path)):
            with self.assertRaisesRegex(ValueError, "Symlink/junction"):
                self.build()

    def test_unsafe_candidate_source_zip_rejected(self):
        zip_name = next(name for name in builder.CANDIDATE_FILES if name.endswith(".zip"))
        (self.candidate / zip_name).write_bytes(synthetic_zip(["../escaped.tex"]))
        self.refresh_candidate_manifest()
        with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
            self.build()

    def test_duplicate_and_symlink_zip_entries_rejected(self):
        duplicate = BytesIO()
        with zipfile.ZipFile(duplicate, "w") as archive:
            archive.writestr("same", b"one")
            with self.assertWarns(UserWarning):
                archive.writestr("same", b"two")
        with self.assertRaisesRegex(ValueError, "Duplicate ZIP member"):
            builder.validate_zip_bytes(duplicate.getvalue())
        linked = BytesIO()
        with zipfile.ZipFile(linked, "w") as archive:
            item = zipfile.ZipInfo("link")
            item.create_system = 3
            item.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(item, "target")
        with self.assertRaisesRegex(ValueError, "ZIP symlink"):
            builder.validate_zip_bytes(linked.getvalue())


if __name__ == "__main__":
    unittest.main()
