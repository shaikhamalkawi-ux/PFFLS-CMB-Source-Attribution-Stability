"""Public return ZIP invariants; no native/private input is needed."""
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('package', ROOT / 'scripts/build_strengthening_package.py')
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_sensitive_paths_rejected(self):
        for name in ('private/a.json', 'raw/data.csv', '../secret', '/abs', 'a\\b',
                     'original.xlsx', 'archive.zip', 'mail.eml', 'C:/data.txt', 'C:relative.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                package.safe_member(name)

    def test_zip_reproducible_and_crc(self):
        first = package.zip_bytes({'b.txt': b'b', 'a.txt': b'a'})
        self.assertEqual(first, package.zip_bytes({'a.txt': b'a', 'b.txt': b'b'}))
        with zipfile.ZipFile(io.BytesIO(first)) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.namelist(), ['a.txt', 'b.txt'])

    def test_payload_manifest_and_private_exclusion(self):
        members = package.payload(ROOT)
        rows = members['SHA256SUMS.txt'].decode().splitlines()
        self.assertEqual(len(rows), len(members) - 1)
        for row in rows:
            digest, name = row.split('  ', 1)
            self.assertEqual(digest, hashlib.sha256(members[name]).hexdigest())
        self.assertFalse(any('/private/' in f'/{name}' for name in members))
        self.assertFalse(any(name.endswith(('.xlsx', '.pdf', '.zip')) for name in members))

    def test_frozen_archive_copied_exactly(self):
        members = package.payload(ROOT)
        archived = [n for n in members if n.startswith(package.ARCHIVE + '/')]
        self.assertEqual(len(archived), 30)
        for name in archived:
            self.assertEqual(members[name], (ROOT / name).read_bytes())

    def test_repository_destination_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            package.build(ROOT / 'outputs/should_not_exist.zip')

    def test_frozen_manifest_itself_is_pinned(self):
        with patch.object(package, 'OUTER_MANIFEST_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'outer manifest identity'):
                package.payload(ROOT)


if __name__ == '__main__':
    unittest.main()
