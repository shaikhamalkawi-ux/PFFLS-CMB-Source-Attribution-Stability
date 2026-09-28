"""Read-only extracted-archive integrity and saved JRC arithmetic verification."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
SCIENCE = "outputs/continuous_research_20260927/editor_response_20260928"
UPSTREAM = "outputs/journal_editorial_20260926/publication_derived/derived_data"
PINNED = {
    f"{SCIENCE}/audit_jrc_family_structure.py": "9429a4b32ed0dbe0ad2db68f57636db078efaa803f69941898a527f26212f186",
    f"{SCIENCE}/JRC_FAMILY_RESULT.json": "9a27b3b19a22e099a2fca45090c35741cba61570c736900ee4648c552194df31",
    f"{UPSTREAM}/jrc_12set_landscape.csv": "b1f0081b9e8943b1e13a09a9ece7c79aca373bff4b4f2e702eb65a1689333356",
    f"{UPSTREAM}/jrc_profile_choice_edges_reconstructed.csv": "9695d1d70ae7f48bc14ee7e51dcd49c99ee82f13ffb7f7529072b18107adca36",
}
EPA_MISSING = ["epa_native_ledger.json", "epa_configuration_frozen.json",
               "epa_native_reconstruction.json", "original source_recovery.json",
               "sjvf_data.zip (including ADsjvf.txt)",
               "audit_epa_native_strengthening.py", "original EPA_MARGIN_PLAN.md"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def decode(data: bytes):
    def reject(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")
    return json.loads(data, object_pairs_hook=unique, parse_constant=reject)


def member(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if (not name or "\\" in name or ":" in name or relative.is_absolute()
            or ".." in relative.parts or str(relative) != name):
        raise ValueError(f"Unsafe path: {name}")
    path = root.joinpath(*relative.parts)
    if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
        raise ValueError(f"Escaping or linked path: {name}")
    return path


def verify(root: Path):
    root = root.resolve(strict=True)
    inventory_path = member(root, "PACKAGE_INVENTORY.json")
    inventory_bytes = inventory_path.read_bytes()
    inventory = decode(inventory_bytes)
    records = inventory["payloads"]
    if inventory["schema_version"] != 1 or not isinstance(records, list) or not records:
        raise ValueError("Invalid inventory schema")
    expected, contents = {}, {}
    for entry in records:
        name, digest = entry["path"], entry["sha256"]
        if (name.casefold() in {p.casefold() for p in expected}
                or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ValueError("Duplicate or invalid inventory identity")
        data = member(root, name).read_bytes()
        if len(data) != entry["bytes"] or sha(data) != digest:
            raise ValueError(f"Inventory bytes/hash mismatch: {name}")
        expected[name] = digest
        contents[name] = data
    expected["PACKAGE_INVENTORY.json"] = sha(inventory_bytes)
    manifest = {}
    for line in member(root, "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None or match[2] in manifest:
            raise ValueError("Invalid or duplicate manifest record")
        manifest[match[2]] = match[1]
    if manifest != expected:
        raise ValueError("Manifest membership or hashes disagree with inventory")
    paths = list(root.rglob("*"))
    if any(p.is_symlink() for p in paths):
        raise ValueError("Symlink member not allowed")
    actual = {p.relative_to(root).as_posix() for p in paths if p.is_file()}
    if actual != set(expected) | {"SHA256SUMS"}:
        raise ValueError("Unexpected or missing extracted file; use a clean extraction directory")
    for path, digest in PINNED.items():
        if path not in contents or sha(contents[path]) != digest:
            raise ValueError(f"Historical scientific pin mismatch: {path}")
    module_path = member(root, f"{SCIENCE}/audit_jrc_family_structure.py")
    spec = importlib.util.spec_from_file_location("pffls_public_read_only_jrc", module_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load pinned arithmetic module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # analyse() is read-only. Never call module.main(): saved outputs are retained.
    calculated = module.analyse()
    normalized = decode(json.dumps(calculated, default=str, allow_nan=False).encode("utf-8"))
    saved = decode(contents[f"{SCIENCE}/JRC_FAMILY_RESULT.json"])
    historical = {"python", "script_sha256", "active_postprocessing_seconds"}
    if set(saved) != set(normalized) | historical:
        raise ValueError("Unexpected saved JRC scientific/provenance fields")
    if normalized != {k: v for k, v in saved.items() if k not in historical}:
        raise ValueError("Saved JRC arithmetic differs from included CSV calculation")
    if saved["script_sha256"] != PINNED[f"{SCIENCE}/audit_jrc_family_structure.py"]:
        raise ValueError("Historical JRC producer identity mismatch")
    return {"archive_integrity": "PASS", "payload_count": len(records),
            "jrc_saved_arithmetic": "PASS", "jrc_native_reproduction": False,
            "jrc_algorithmic_independence_claimed": False,
            "epa": "NOT_REPRODUCED_MISSING_EXTERNAL_INPUTS",
            "epa_required_objects_not_in_release": EPA_MISSING,
            "new_model_fits": 0, "random_draws": 0, "tests_run": 0,
            "producer_main_called": False, "files_written_by_verifier": 0,
            "meaning": "Integrity and JRC scalar-summary repeatability only; EPA/native reproduction not performed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extracted_root", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.extracted_root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"verification": "FAIL", "reason": str(exc)}, indent=2))
        raise SystemExit(1)
    print(json.dumps(result, indent=2))
