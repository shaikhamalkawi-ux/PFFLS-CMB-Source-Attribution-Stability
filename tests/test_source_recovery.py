"""Offline tests for bounded official-source archive inspection."""
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import warnings
import zipfile

PATH = Path(__file__).resolve().parents[1] / 'scripts/recover_strengthening_sources.py'
SPEC = importlib.util.spec_from_file_location('recovery', PATH)
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


def archive(entries):
    buf = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in entries:
                z.writestr(name, data)
    return buf.getvalue()


class SourceRecoveryTests(unittest.TestCase):
    def test_hashes_and_directories(self):
        result = recovery.inventory_zip(archive([('dir/', b''), ('dir/a', b'abc')]))
        self.assertEqual(result, [{'name': 'dir/a', 'bytes': 3,
                                   'sha256': hashlib.sha256(b'abc').hexdigest()}])

    def test_duplicate_names(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            recovery.inventory_zip(archive([('a', b'1'), ('a', b'2')]))

    def test_member_limit_before_decompression(self):
        with patch.object(recovery, 'MAX_MEMBER', 5):
            with self.assertRaisesRegex(ValueError, 'member exceeds'):
                recovery.inventory_zip(archive([('a', b'000000')]))

    def test_total_limit(self):
        with patch.object(recovery, 'MAX_EXPANDED', 5):
            with self.assertRaisesRegex(ValueError, 'total exceeds'):
                recovery.inventory_zip(archive([('a', b'123'), ('b', b'456')]))

    def test_count_limit(self):
        with patch.object(recovery, 'MAX_MEMBERS', 1):
            with self.assertRaisesRegex(ValueError, 'too many'):
                recovery.inventory_zip(archive([('a', b''), ('b', b'')]))

    def test_invalid_archive(self):
        with self.assertRaises(zipfile.BadZipFile):
            recovery.inventory_zip(b'not a ZIP')


if __name__ == '__main__':
    unittest.main()
