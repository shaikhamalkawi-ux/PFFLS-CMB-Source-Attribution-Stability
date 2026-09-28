"""Small independent artificial fixtures; never read the scientific CSV inputs."""
from decimal import Decimal
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("jrc_family_review_target", HERE / "audit_jrc_family_structure.py")
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


def invented():
    # Chi grows with either index; error decreases with Wood but grows with Vehicle.
    rows = [{"profile_set": f"W{w}-V{v}", "mean_reduced_chi2": str(100*w+v),
             "EL1_percent_reference_mass": str(100-10*w+v)}
            for w in (3, 4, 5, 6) for v in (2, 3, 4)]
    edges = []
    for family, fixed_values, changed_values in (
            ("Wood", (2, 3, 4), (3, 4, 5, 6)),
            ("Vehicle", (3, 4, 5, 6), (2, 3, 4))):
        for fixed in fixed_values:
            for a in changed_values:
                for b in changed_values:
                    if a >= b:
                        continue
                    aid = f"W{a}-V{fixed}" if family == "Wood" else f"W{fixed}-V{a}"
                    bid = f"W{b}-V{fixed}" if family == "Wood" else f"W{fixed}-V{b}"
                    wood = family == "Wood"
                    edges.append({"edge_id": f"E{len(edges)+1:02d}",
                                  "profile_a_id": aid, "profile_b_id": bid,
                                  "source_family": family, "fit_favored_endpoint": aid,
                                  "reference_closer_endpoint": bid if wood else aid,
                                  "discordance": str(wood),
                                  "selection_regret_pp_from_published_values": str(10*(b-a) if wood else 0)})
    return rows, edges


def calculate(rows, edges):
    def mocked(name):
        return rows if name == "jrc_12set_landscape.csv" else edges
    with patch.object(target, "load", side_effect=mocked):
        return target.analyse()


class IndependentFixtures(unittest.TestCase):
    def test_path_is_active_repository(self):
        self.assertEqual(target.ROOT.name, "PFFLS-CMB-continuous-20260927")
        self.assertEqual(target.INPUT, target.ROOT / "outputs/journal_editorial_20260926/publication_derived/derived_data")

    def test_full_grid_and_signed_groups(self):
        value = calculate(*invented())
        self.assertEqual((value["all"]["n"], value["all"]["discordant"], value["all"]["concordant"]), (30, 18, 12))
        wood, vehicle = value["families"]["Wood"], value["families"]["Vehicle"]
        self.assertEqual(wood["signed_delta_pp_min_median_max"], [10, 15, 30])
        self.assertEqual(wood["chi2_gap_min_median_max"], [100, 150, 300])
        self.assertEqual(vehicle["signed_delta_pp_min_median_max"], [-2, -1, -1])
        self.assertIsNone(vehicle["discordant_delta_pp_median_max"])
        self.assertEqual(len(value["strata"]), 7)
        self.assertEqual([v["n"] for v in value["strata"].values()], [6, 6, 6, 3, 3, 3, 3])
        self.assertEqual([e["edge_id"] for e in value["edges"]], [f"E{i:02d}" for i in range(1, 31)])
        self.assertFalse(value["source_native_reproduction"])
        self.assertEqual((value["native_fits"], value["random_draws"]), (0, 0))

    def test_summary_keeps_negative_zero_and_positive(self):
        edges = [{"edge_id": str(i), "signed_EL1_delta_pp": Decimal(x), "chi2_gap": Decimal(i+1)}
                 for i, x in enumerate(("-2", "0", "3", "7"))]
        got = target.summaries(edges)
        self.assertEqual((got["discordant"], got["concordant"], got["reference_ties"]), (2, 1, 1))
        self.assertEqual(got["signed_delta_pp_min_median_max"], [-2, Decimal("1.5"), 7])
        self.assertEqual(got["discordant_delta_pp_median_max"], [5, 7])

    def test_missing_duplicate_and_selector_tie_refuse(self):
        rows, edges = invented()
        with self.assertRaises(ValueError):
            calculate(rows[:-1], edges)
        rows[-1] = dict(rows[0])
        with self.assertRaises(ValueError):
            calculate(rows, edges)
        rows, edges = invented()
        rows[3]["mean_reduced_chi2"] = rows[0]["mean_reduced_chi2"]
        with self.assertRaisesRegex(ValueError, "selector tie"):
            calculate(rows, edges)

    def test_cached_direction_and_regret_refuse(self):
        rows, edges = invented()
        edges[0]["discordance"] = "False"
        with self.assertRaisesRegex(ValueError, "identity/direction"):
            calculate(rows, edges)
        rows, edges = invented()
        edges[0]["selection_regret_pp_from_published_values"] = "9.5"
        with self.assertRaisesRegex(ValueError, "regret"):
            calculate(rows, edges)
        rows, edges = invented()
        edges[-1] = dict(edges[0])
        with self.assertRaisesRegex(ValueError, "duplicate cached"):
            calculate(rows, edges)

    def test_existing_output_refuses_before_analysis(self):
        with tempfile.TemporaryDirectory(prefix="pffls-jrc-fixture-") as tmp:
            folder = Path(tmp)
            existing = folder / "JRC_FAMILY_RESULT.json"
            # Fixture-local bytes only, not a scientific output.
            with existing.open("x", encoding="utf-8") as handle:
                handle.write("invented fixture sentinel")
            with patch.object(target, "HERE", folder), patch.object(target, "analyse") as forbidden:
                with self.assertRaises(FileExistsError):
                    target.main()
                forbidden.assert_not_called()
            self.assertEqual(existing.read_text(), "invented fixture sentinel")


if __name__ == "__main__":
    unittest.main(verbosity=2)
