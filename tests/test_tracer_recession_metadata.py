import ast
from decimal import InvalidOperation, localcontext
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_tracer_recession_metadata.py"
spec = importlib.util.spec_from_file_location("tracer_metadata_replay", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class MetadataReplayTests(unittest.TestCase):
    def test_exact_threshold(self):
        self.assertFalse(check.positive_lower("0.3", "0.1"))
        self.assertTrue(check.positive_lower("0.30000000000000000000000001", "0.1"))
        self.assertFalse(check.positive_lower("0.29999999999999999999999999", "0.1"))

    def test_zero_and_positive(self):
        self.assertFalse(check.positive_lower("0", "0"))
        self.assertTrue(check.positive_lower("1e-30", "0"))

    def test_caller_precision_does_not_change_sign(self):
        with localcontext() as context:
            context.prec = 2
            self.assertTrue(check.positive_lower("0.30000000000000000000000001", "0.1"))

    def test_bad_values(self):
        for token in ("NaN", "Infinity", "-Infinity", "1e100", "1e-100", "", "bad"):
            with self.subTest(token=token), self.assertRaises((ValueError, InvalidOperation)):
                check.number(token)
        for mean, unc in (("-1", "1"), ("1", "-1")):
            with self.assertRaises(ValueError):
                check.positive_lower(mean, unc)

    def test_table_and_guard(self):
        self.assertEqual(check.table(b"ID SIZE\nA FINE\n"), [{"ID": "A", "SIZE": "FINE"}])
        for payload in (b"", b"A A\n1 2", b"A B\n1", b"A B\n1 2 3"):
            with self.assertRaises(ValueError):
                check.table(payload)

    def test_explicit_mapping_and_universe(self):
        self.assertEqual(check.TRACERS, {"SUXC": "SUXU", "CUXC": "CUXU", "ZNXC": "ZNXU"})
        self.assertEqual(len(check.ORIGINAL), 20)
        self.assertEqual(len(set().union(*map(set, check.FAMILIES))), 17)
        self.assertEqual([len(x) for x in check.FAMILIES], [4, 3, 2, 5, 1, 1, 1])

    def test_no_solver_or_producer_import(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        names = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        names += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        self.assertFalse(any(name.startswith(("scipy", "numpy", "audit_", "truth_tracer")) for name in names))


if __name__ == "__main__":
    unittest.main()
