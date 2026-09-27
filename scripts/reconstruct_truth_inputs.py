#!/usr/bin/env python3
"""Restore only the omitted, hash-frozen truth input NPZ; never fit or score.

Uses the unchanged producer's licensed-release reader and deterministic generator.
All scientific configurations, gates, manifests and numerical ledgers stay intact.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path

import numpy as np

import audit_truth_decisions as frozen


EXPECTED_CONFIG = "8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9"
EXPECTED_MANIFEST = "2f1134357b78d61f40dac63e0749961a889c2d608085ecf5e8a3de65e031fed2"
EXPECTED_NPZ = "78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1"
ARRAY_NAME = "truth_frozen_arrays.npz"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_metadata(private: Path) -> dict:
    """Validate frozen implementation/gate/config, without requiring the NPZ."""
    frozen.validate_gate(private)
    payload = (private / "truth_configuration_frozen.json").read_bytes()
    require(frozen.sha(payload) == EXPECTED_CONFIG, "original configuration hash mismatch")
    config = json.loads(payload)
    require(config["config"] == frozen.CONFIG, "configuration values drifted")
    require(config["hashes"] == frozen.implementation_hashes(), "frozen implementation drifted")
    require(config["test_gate_sha256"] == frozen.file_hash(private / "truth_test_gate.json"),
            "test gate hash mismatch")
    manifest_payload = (private / "truth_input_freeze.json").read_bytes()
    require(frozen.sha(manifest_payload) == EXPECTED_MANIFEST, "original input manifest hash mismatch")
    manifest = json.loads(manifest_payload)
    require(manifest["configuration_sha256"] == EXPECTED_CONFIG, "manifest configuration mismatch")
    require(manifest["archive_sha256"] == frozen.TRUSTED["archive"], "release identity mismatch")
    require(manifest["member_sha256"] == frozen.TRUSTED["member"], "member identity mismatch")
    require(manifest["frozen_array_file"] == ARRAY_NAME, "unexpected array filename")
    require(manifest["frozen_array_file_sha256"] == EXPECTED_NPZ, "original NPZ hash mismatch")
    return manifest


def check_arrays(arrays: dict, records: dict) -> None:
    require(set(arrays) == set(records), "array keys mismatch")
    for name, record in records.items():
        values = np.asarray(arrays[name])
        require(not values.dtype.hasobject, "object arrays forbidden: " + name)
        require(list(values.shape) == record["shape"], "array shape mismatch: " + name)
        require(values.dtype.str == record["dtype"], "array dtype mismatch: " + name)
        require(frozen.array_hash(values) == record["sha256"], "array hash mismatch: " + name)


def verify_npz(payload: bytes, manifest: dict) -> None:
    require(frozen.sha(payload) == manifest["frozen_array_file_sha256"], "NPZ bytes mismatch")
    with np.load(BytesIO(payload), allow_pickle=False) as archive:
        require(len(archive.files) == len(set(archive.files)), "duplicate NPZ members")
        check_arrays({name: archive[name] for name in archive.files}, manifest["arrays"])


def rebuild_payload(release_path: Path, manifest: dict) -> bytes:
    release, _ = frozen.load_release(release_path)
    generated, states = frozen.generate_controls(release["P0"], release["M0"], release["released_sigma"])
    require(states == manifest["rng_states"], "RNG state mismatch")
    arrays = {**release, **generated}
    check_arrays(arrays, manifest["arrays"])
    buffer = BytesIO()
    np.savez_compressed(buffer, **arrays)
    payload = buffer.getvalue()
    verify_npz(payload, manifest)
    return payload


def exclusive_restore(target: Path, payload: bytes, manifest: dict) -> None:
    """Validation precedes exclusive creation; even equal existing bytes refuse."""
    verify_npz(payload, manifest)
    # 'xb' also refuses dangling symlinks and a target created after preflight.
    with target.open("xb") as handle:
        handle.write(payload)
    require(target.read_bytes() == payload, "post-write readback mismatch; stop and inspect")


def run(private: Path = frozen.PRIVATE, release: Path = frozen.ARCHIVE,
        verify_only: bool = False, check_reconstruction: bool = False) -> dict:
    require(not (verify_only and check_reconstruction), "choose one verification mode")
    private = Path(private)
    manifest = read_metadata(private)
    target = private / ARRAY_NAME
    require(target.parent.resolve() == private.resolve(), "target escaped private directory")
    if verify_only:
        require(not target.is_symlink(), "symlink target refused")
        verify_npz(target.read_bytes(), manifest)
        status = "EXISTING_INPUTS_VERIFIED_NO_WRITE"
    else:
        if not check_reconstruction and (target.exists() or target.is_symlink()):
            raise FileExistsError("target already exists; use --verify-only, never overwrite")
        payload = rebuild_payload(Path(release), manifest)
        if check_reconstruction:
            status = "RECONSTRUCTION_VERIFIED_IN_MEMORY_NO_WRITE"
        else:
            exclusive_restore(target, payload, manifest)
            status = "MISSING_INPUTS_EXCLUSIVELY_RESTORED"
    return {"status": status, "array_count": len(manifest["arrays"]),
            "configuration_sha256": manifest["configuration_sha256"],
            "npz_sha256": manifest["frozen_array_file_sha256"],
            "fits_or_scores_run": 0, "frozen_records_changed": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, default=frozen.PRIVATE)
    parser.add_argument("--release", type=Path, default=frozen.ARCHIVE)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true", help="verify existing NPZ without release access or writes")
    mode.add_argument("--check-reconstruction", action="store_true", help="rebuild in memory and verify, never write")
    args = parser.parse_args()
    print(json.dumps(run(args.private, args.release, args.verify_only, args.check_reconstruction), indent=2))


if __name__ == "__main__":
    main()
