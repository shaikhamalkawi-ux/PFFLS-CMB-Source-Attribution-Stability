"""Synthetic restoration safety tests; no third-party input or scoring required."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reconstruct_truth_inputs as helper


class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.arrays = {"a": np.array([[1., 2.], [3., 4.]]), "b": np.array([1, 3], dtype=np.int64)}
        self.manifest = {"arrays": {name: {"shape": list(v.shape), "dtype": v.dtype.str,
                                         "sha256": helper.frozen.array_hash(v)} for name, v in self.arrays.items()},
                         "configuration_sha256": "synthetic-test-only", "rng_states": {"synthetic": 1}}
        buffer = BytesIO()
        np.savez_compressed(buffer, **self.arrays)
        self.payload = buffer.getvalue()
        self.manifest["frozen_array_file_sha256"] = helper.frozen.sha(self.payload)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.target = self.directory / helper.ARRAY_NAME

    def test_good_arrays_and_npz(self):
        helper.check_arrays(self.arrays, self.manifest["arrays"])
        helper.verify_npz(self.payload, self.manifest)

    def test_key_shape_dtype_value_drift(self):
        for arrays in ({"a": self.arrays["a"]},
                       {**self.arrays, "a": self.arrays["a"].reshape(4)},
                       {**self.arrays, "a": self.arrays["a"].astype(np.float32)},
                       {**self.arrays, "a": self.arrays["a"] + 1}):
            with self.subTest(keys=list(arrays)), self.assertRaises(ValueError):
                helper.check_arrays(arrays, self.manifest["arrays"])

    def test_object_array_refused(self):
        with self.assertRaises(ValueError):
            helper.check_arrays({**self.arrays, "a": np.array([[object(), object()], [object(), object()]])},
                                self.manifest["arrays"])

    def test_wrong_npz_bytes_refused_before_write(self):
        with self.assertRaises(ValueError):
            helper.exclusive_restore(self.target, self.payload + b"tamper", self.manifest)
        self.assertFalse(self.target.exists())

    def test_bad_per_array_manifest_refused_before_write(self):
        manifest = deepcopy(self.manifest)
        manifest["arrays"]["a"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            helper.exclusive_restore(self.target, self.payload, manifest)
        self.assertFalse(self.target.exists())

    def test_restore_only_absent_target(self):
        helper.exclusive_restore(self.target, self.payload, self.manifest)
        self.assertEqual(self.target.read_bytes(), self.payload)
        with self.assertRaises(FileExistsError):
            helper.exclusive_restore(self.target, self.payload, self.manifest)
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_existing_different_file_never_overwritten(self):
        self.target.write_bytes(b"preserve")
        with self.assertRaises(FileExistsError):
            helper.exclusive_restore(self.target, self.payload, self.manifest)
        self.assertEqual(self.target.read_bytes(), b"preserve")

    def test_verify_only_reads_existing_without_generation(self):
        self.target.write_bytes(self.payload)
        with patch.object(helper, "read_metadata", return_value=self.manifest), \
             patch.object(helper, "rebuild_payload", side_effect=AssertionError("no generator")):
            result = helper.run(self.directory, verify_only=True)
        self.assertEqual(result["status"], "EXISTING_INPUTS_VERIFIED_NO_WRITE")
        self.assertEqual(result["fits_or_scores_run"], 0)

    def test_verify_only_missing_target_fails_without_write(self):
        with patch.object(helper, "read_metadata", return_value=self.manifest), self.assertRaises(FileNotFoundError):
            helper.run(self.directory, verify_only=True)
        self.assertFalse(self.target.exists())

    def test_reconstruction_check_never_writes(self):
        with patch.object(helper, "read_metadata", return_value=self.manifest), \
             patch.object(helper, "rebuild_payload", return_value=self.payload):
            result = helper.run(self.directory, check_reconstruction=True)
        self.assertEqual(result["status"], "RECONSTRUCTION_VERIFIED_IN_MEMORY_NO_WRITE")
        self.assertFalse(self.target.exists())

    def test_existing_restore_refuses_before_release_read(self):
        self.target.write_bytes(self.payload)
        with patch.object(helper, "read_metadata", return_value=self.manifest), \
             patch.object(helper, "rebuild_payload", side_effect=AssertionError("no generator")), \
             self.assertRaises(FileExistsError):
            helper.run(self.directory)

    def test_run_restores_validated_payload(self):
        with patch.object(helper, "read_metadata", return_value=self.manifest), \
             patch.object(helper, "rebuild_payload", return_value=self.payload):
            result = helper.run(self.directory)
        self.assertEqual(result["status"], "MISSING_INPUTS_EXCLUSIVELY_RESTORED")
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_conflicting_modes_refused(self):
        with self.assertRaises(ValueError):
            helper.run(self.directory, verify_only=True, check_reconstruction=True)

    def test_rebuild_rng_mismatch_refuses_before_pack(self):
        release = {"P0": np.ones((1, 1)), "M0": np.ones((1, 1)), "released_sigma": np.ones((1, 1))}
        with patch.object(helper.frozen, "load_release", return_value=(release, "test")), \
             patch.object(helper.frozen, "generate_controls", return_value=({}, {"bad": 1})), \
             self.assertRaisesRegex(ValueError, "RNG"):
            helper.rebuild_payload(Path("unused"), self.manifest)

    def test_rebuild_calls_only_reader_and_generator(self):
        release = {"P0": np.ones((1, 1)), "M0": np.ones((1, 1)), "released_sigma": np.ones((1, 1))}
        arrays = {**release, "generated": np.zeros((2,))}
        buffer = BytesIO()
        np.savez_compressed(buffer, **arrays)
        manifest = {"rng_states": {"good": 1}, "frozen_array_file_sha256": helper.frozen.sha(buffer.getvalue()),
                    "arrays": {k: {"shape": list(v.shape), "dtype": v.dtype.str,
                                   "sha256": helper.frozen.array_hash(v)} for k, v in arrays.items()}}
        with patch.object(helper.frozen, "load_release", return_value=(release, "test")), \
             patch.object(helper.frozen, "generate_controls", return_value=({"generated": arrays["generated"]}, {"good": 1})), \
             patch.object(helper.frozen, "fit_family", side_effect=AssertionError("no fitting")), \
             patch.object(helper.frozen, "score", side_effect=AssertionError("no scoring")):
            self.assertEqual(helper.rebuild_payload(Path("unused"), manifest), buffer.getvalue())

    def metadata_fixture(self):
        gate = b"synthetic gate"
        config = helper.frozen.json_bytes({"config": helper.frozen.CONFIG, "hashes": {},
                                          "test_gate_sha256": helper.frozen.sha(gate)})
        expected_config = helper.frozen.sha(config)
        manifest = helper.frozen.json_bytes({"configuration_sha256": expected_config,
                    "archive_sha256": helper.frozen.TRUSTED["archive"],
                    "member_sha256": helper.frozen.TRUSTED["member"],
                    "frozen_array_file": helper.ARRAY_NAME,
                    "frozen_array_file_sha256": helper.EXPECTED_NPZ})
        for name, payload in (("truth_test_gate.json", gate), ("truth_configuration_frozen.json", config),
                              ("truth_input_freeze.json", manifest)):
            (self.directory / name).write_bytes(payload)
        return expected_config, helper.frozen.sha(manifest)

    def test_metadata_validation_without_npz(self):
        config_hash, manifest_hash = self.metadata_fixture()
        with patch.object(helper.frozen, "validate_gate", return_value={}), \
             patch.object(helper.frozen, "implementation_hashes", return_value={}), \
             patch.object(helper, "EXPECTED_CONFIG", config_hash), \
             patch.object(helper, "EXPECTED_MANIFEST", manifest_hash):
            self.assertEqual(helper.read_metadata(self.directory)["frozen_array_file"], helper.ARRAY_NAME)
        self.assertFalse(self.target.exists())

    def test_metadata_bytes_drift_refused(self):
        for name in ("truth_configuration_frozen.json", "truth_input_freeze.json", "truth_test_gate.json"):
            with self.subTest(name=name):
                config_hash, manifest_hash = self.metadata_fixture()
                path = self.directory / name
                path.write_bytes(path.read_bytes() + b" ")
                with patch.object(helper.frozen, "validate_gate", return_value={}), \
                     patch.object(helper.frozen, "implementation_hashes", return_value={}), \
                     patch.object(helper, "EXPECTED_CONFIG", config_hash), \
                     patch.object(helper, "EXPECTED_MANIFEST", manifest_hash), self.assertRaises(ValueError):
                    helper.read_metadata(self.directory)

    def test_implementation_drift_refused(self):
        config_hash, manifest_hash = self.metadata_fixture()
        with patch.object(helper.frozen, "validate_gate", return_value={}), \
             patch.object(helper.frozen, "implementation_hashes", return_value={"drift": "yes"}), \
             patch.object(helper, "EXPECTED_CONFIG", config_hash), \
             patch.object(helper, "EXPECTED_MANIFEST", manifest_hash), self.assertRaises(ValueError):
            helper.read_metadata(self.directory)


if __name__ == "__main__":
    unittest.main()
