"""Isolate existing Cycle 04 test failures without changing repository snapshots.

Reads Git HEAD and the three Cycle 02 files. Replays the legacy suite in temporary
Git-archive representations with explicit EOL settings. The historical CRLF bytes
are verified against hashes observed before root's mechanical EOL fix. No Git
index/worktree mutation is made by this script.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "ebaed99aa9f7d2dec993fcfd11d62f3dd7eb95cf"
OUTPUT = ROOT / "outputs/strengthening_20260926"
PATHS = (
    "outputs/cycle02/appendix_c_2008_2009_daily.csv",
    "scripts/extract_cycle02_fairbanks.py",
    "tests/test_cycle02_fairbanks.py",
)
MANIFEST = "outputs/cycle02/artifact_manifest_sha256.csv"
OBSERVED_PRE_FIX_SHA256 = {
    PATHS[0]: "540e305ce6704f62e09476c01ba76a3ebf8404644e6a769c3e3acffd0e2a6301",
    PATHS[1]: "594adfbc6fa1a0646acd4e3ec9d15009dc2eeda66954c97fbfc41f76d0941427",
    PATHS[2]: "d869c25e8ceb17c5e8d6f2f16f2a4736b216abc643b96be3c48291b08dbae6c7",
}


def git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          check=True, timeout=60).stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_legacy(snapshot: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests",
         "-p", "test_cycle04_submission_gate.py", "-v"],
        cwd=snapshot, capture_output=True, text=True, encoding="utf-8", timeout=180,
    )
    transcript = (completed.stdout + completed.stderr).replace(str(snapshot), "<isolated-snapshot>")
    statuses = []
    for line in transcript.splitlines():
        match = re.match(r"^(test_\w+) \(([^)]+)\) \.\.\. (ok|ERROR|FAIL|skipped.*)$", line)
        if match:
            statuses.append({"test": match[1], "qualified": match[2], "status": match[3]})
    if not statuses or "Ran " not in transcript:
        raise ValueError("Legacy suite did not produce a complete unittest result")
    problems = re.findall(r"(?:ValueError|AssertionError):[^\n]+", transcript)
    return {
        "returncode": completed.returncode,
        "tests_run": len(statuses),
        "passed": sum(item["status"] == "ok" for item in statuses),
        "failed": sum(item["status"] == "FAIL" for item in statuses),
        "errors": sum(item["status"] == "ERROR" for item in statuses),
        "skipped": sum(item["status"].startswith("skipped") for item in statuses),
        "problem_messages": sorted(set(problems)),
        "tests": statuses,
    }


def extract_git_snapshot(archive_bytes: bytes, destination: Path) -> None:
    """Git-created archive only, with explicit size and destination checks."""
    base = destination.resolve()
    with ZipFile(io.BytesIO(archive_bytes)) as archive:
        entries = archive.infolist()
        if len(entries) > 10000 or sum(entry.file_size for entry in entries) > 200_000_000:
            raise ValueError("Unexpectedly large Git snapshot")
        for entry in entries:
            name = PurePosixPath(entry.filename)
            target = (base / entry.filename).resolve()
            if name.is_absolute() or ".." in name.parts or ":" in entry.filename or not target.is_relative_to(base):
                raise ValueError("Unsafe Git archive path")
        archive.extractall(base)


def audit() -> dict:
    head = git_bytes("rev-parse", "HEAD").decode().strip()
    if head != EXPECTED_HEAD:
        raise ValueError("HEAD changed; this bounded audit must be reviewed for the new snapshot")
    manifest_bytes = git_bytes("show", f"{head}:{MANIFEST}")
    manifest = {row["relative_path"]: row for row in csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8")))}
    files, canonical_bytes = [], {}
    for path in PATHS:
        current = (ROOT / path).read_bytes()
        blob = git_bytes("show", f"{head}:{path}")
        canonical_bytes[path] = blob
        pre_fix = blob.replace(b"\n", b"\r\n")
        if digest(pre_fix) != OBSERVED_PRE_FIX_SHA256[path]:
            raise ValueError("Historical CRLF reconstruction does not match pre-fix observation")
        expected = manifest[path]
        files.append({
            "path": path,
            "manifest_bytes": int(expected["bytes"]), "manifest_sha256": expected["sha256"],
            "head_blob_bytes": len(blob), "head_blob_sha256": digest(blob),
            "head_blob_crlf_count": blob.count(b"\r\n"),
            "observed_pre_fix_bytes": len(pre_fix), "observed_pre_fix_sha256": digest(pre_fix),
            "observed_pre_fix_crlf_count": pre_fix.count(b"\r\n"),
            "pre_fix_added_cr_bytes": len(pre_fix) - len(blob),
            "current_working_tree_bytes": len(current), "current_working_tree_sha256": digest(current),
            "current_working_tree_crlf_count": current.count(b"\r\n"),
            "current_working_tree_equals_head_blob": current == blob,
            "head_blob_matches_manifest": len(blob) == int(expected["bytes"]) and digest(blob) == expected["sha256"],
            "working_tree_equals_head_after_crlf_to_lf_only": current.replace(b"\r\n", b"\n") == blob,
        })
    if not all(row["head_blob_matches_manifest"] and row["working_tree_equals_head_after_crlf_to_lf_only"] for row in files):
        raise ValueError("Differences are not exclusively the expected checkout line-ending conversion")
    lf_archive = git_bytes("-c", "core.autocrlf=false", "-c", "core.eol=lf",
                           "archive", "--format=zip", head)
    windows_archive = git_bytes("-c", "core.autocrlf=true", "-c", "core.eol=crlf",
                                "archive", "--format=zip", head)
    if max(len(lf_archive), len(windows_archive)) > 100_000_000:
        raise ValueError("Unexpectedly large compressed Git snapshot")
    with tempfile.TemporaryDirectory(prefix="pffls_legacy_line_endings_") as directory:
        no_auto = Path(directory) / "no_auto_conversion"
        snapshot = Path(directory) / "windows_representation"
        no_auto.mkdir()
        snapshot.mkdir()
        extract_git_snapshot(lf_archive, no_auto)
        extract_git_snapshot(windows_archive, snapshot)
        for row in files:
            if digest((no_auto / row["path"]).read_bytes()) != row["head_blob_sha256"]:
                raise ValueError("Git archive does not preserve the inspected HEAD blob")
            if digest((snapshot / row["path"]).read_bytes()) != row["observed_pre_fix_sha256"]:
                raise ValueError("Windows archive does not reproduce observed pre-fix bytes")
        no_auto_result = run_legacy(no_auto)
        windows_before = run_legacy(snapshot)
        # Only disposable snapshot files are changed. Main worktree stays intact.
        for path, blob in canonical_bytes.items():
            (snapshot / path).write_bytes(blob)
        windows_after = run_legacy(snapshot)
    return {
        "audit_date": "2026-09-26",
        "head": head,
        "environment": {"python": platform.python_version(), "os": platform.system(),
                        "core_autocrlf": git_bytes("config", "--get", "core.autocrlf").decode().strip()},
        "scope": "Historical pre-fix byte evidence and synthetic Git-archive EOL experiments; these do not reconstruct the original mixed-EOL checkout. Root has mechanically restored the three Cycle 02 files and pinned their EOL attributes; final actual-worktree suite status is separate.",
        "files": files,
        "git_attributes": git_bytes("check-attr", "text", "eol", "--", *PATHS).decode().splitlines(),
        "head_archive_without_auto_conversion": no_auto_result,
        "synthetic_head_crlf_representation": windows_before,
        "same_synthetic_crlf_tree_three_cycle02_lf_restored": windows_after,
        "audit_script_modified_current_worktree_or_manifests": False,
        "root_restored_current_cycle02_bytes_to_head": all(row["current_working_tree_equals_head_blob"] for row in files),
        "historical_full_suite_observation": {
            "tests_run": 114, "passed": 109, "failures_plus_errors": 5,
            "provenance": "Full-suite run reported by the root agent before forthcoming EPA-native tests; this audit independently replays the affected legacy suite only.",
        },
        "actual_worktree_post_eol_fix_observation": {
            "tests_run": 22, "passed": 17, "failed": 1, "errors": 4,
            "provenance": "Root-reported actual Cycle 04 run after targeted EOL restoration; not another synthetic archive experiment.",
            "current_blocker": "Historical validator requires literal PROJECT_STATE status phrases that do not match current project state.",
            "missing_legacy_literals": ["PR #10 has been merged", "Issue #8 is closed", "USER-REPORTED SENT / PENDING — UNVERIFIED"],
            "disposition": "Do not insert obsolete status phrases or weaken the frozen validator merely to make legacy tests pass. Report this historical-gate failure separately from passing new numerical tests.",
        },
        "interpretation": "The three Cycle 02 manifest hashes match HEAD Git bytes, and explicit CRLF expansion exactly reproduces their pre-fix hashes. A separate legacy Cycle 01 known-stale-set assertion is itself EOL-sensitive under no automatic conversion. Therefore generic canonical-HEAD portability and the targeted Windows fix are distinct questions; all three suite outcomes are reported separately.",
        "limitations": [
            "Git archive is invoked with per-command core.autocrlf=false/core.eol=lf and the three file hashes verified against Git blobs; it is not an actual Windows checkout or dependency reinstall.",
            "The synthetic CRLF replay uses explicit core.autocrlf=true/core.eol=crlf plus committed attributes. It does NOT reconstruct the actual mixed-EOL checkout. Its targeted correction changes exactly three disposable Cycle 02 files to HEAD blob bytes, but earlier Cycle 01 failures still prevent a causal replay of the original five Cycle 02-related failures.",
            "Legacy Cycle 04 readiness assertions encode that historical cycle, not the current manuscript's submission status.",
            "Any later-added tests require a fresh total; the 114-test observation is not a final package-wide count.",
        ],
    }


def render(report: dict) -> str:
    no_auto = report["head_archive_without_auto_conversion"]
    original = report["synthetic_head_crlf_representation"]
    restored = report["same_synthetic_crlf_tree_three_cycle02_lf_restored"]
    rows = "\n".join(
        f"| `{item['path']}` | {item['head_blob_bytes']} | {item['observed_pre_fix_bytes']} | {item['observed_pre_fix_crlf_count']} | yes |"
        for item in report["files"]
    )
    problems = "\n".join(f"- `{item['test']}`: {item['status']}" for item in original["tests"] if item["status"] != "ok")
    return f"""# Legacy test status and line-ending isolation

Audit date: 26 September 2026. **Historical pre-fix byte evidence plus synthetic
EOL experiments, not a reconstruction of the mixed-EOL checkout.** This audit
script does not change the repository. Root separately
restored the three Cycle 02 files to existing HEAD bytes and added targeted EOL
attributes. Final full-suite status must be verified separately.

**Actual post-fix status:** root's Cycle 04 run still reports **22 tests: 17 pass,
1 failure and 4 errors**. The blocker has changed: the historical validator now
expects these literal project-state phrases: `PR #10 has been merged`,
`Issue #8 is closed`, and `USER-REPORTED SENT / PENDING — UNVERIFIED`. This is a
stale historical-status gate, not an unresolved Cycle 02 byte mismatch. Do not
insert obsolete phrases or modify the frozen validator to obtain a green result.
The new numerical audit tests and final full-suite totals must be reported
separately. This actual-worktree observation was provided by root.

## Finding

The three pre-fix Cycle 02 hash mismatches were exclusively LF-to-CRLF checkout
conversion. Their Git blobs at commit `{report['head']}` match the frozen Cycle 02
manifest exactly. Before root's fix, removing only CR bytes forming CRLF sequences
reproduced those Git blobs exactly. The pre-fix bytes/hashes were directly recorded
before normalization; independently expanding each HEAD LF to CRLF recreates those
exact observed hashes. These historical bytes are not confused with the now-LF
worktree. `core.autocrlf` remains `{report['environment']['core_autocrlf']}`; the
three files now have targeted `text eol=lf` attributes.

| File | Manifest/HEAD bytes | Observed pre-fix bytes | Added CR bytes | HEAD hash equals manifest? |
|---|---:|---:|---:|---|
{rows}

Full SHA-256 values and line-ending counts for HEAD, the observed historical
pre-fix form, and the current worktree are recorded separately in
`legacy_test_status.json`. No manifest was updated to hide the mismatch, and the
root's restoration changes no scientific values or Python instructions.

## Isolated EOL experiments and their limitation

Two temporary Git archives were built at the recorded HEAD, one with per-command
`core.autocrlf=false/core.eol=lf`, one with `core.autocrlf=true/core.eol=crlf`.
Committed attributes were honored in both. No global Git configuration changed.
The inspected three files in the first archive match HEAD blobs; those in the
second match the exact observed pre-fix hashes. This second archive is a synthetic
all-auto-CRLF representation, NOT the actual mixed-EOL checkout. It was
then rerun after replacing only those three temporary files with HEAD LF bytes.
No strengthening scripts or private datasets were present in these snapshots.

| Snapshot | Tests | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| HEAD archive, no automatic EOL conversion | {no_auto['tests_run']} | {no_auto['passed']} | {no_auto['failed']} | {no_auto['errors']} | {no_auto['skipped']} |
| Synthetic HEAD auto-CRLF archive; three Cycle 02 files match pre-fix hashes | {original['tests_run']} | {original['passed']} | {original['failed']} | {original['errors']} | {original['skipped']} |
| Same synthetic CRLF archive, only three Cycle 02 LF files restored | {restored['tests_run']} | {restored['passed']} | {restored['failed']} | {restored['errors']} | {restored['skipped']} |

Affected tests in the synthetic CRLF experiment:

{problems}

The no-auto-conversion archive exposes a **different legacy portability issue**:
Cycle 01 validation locks an expected set of stale files. That set changes with
line endings: the LF archive makes `admission_summary.json` and
`candidate_campaigns.csv` match their old manifests, while
`tasks/CODEX_CYCLE_01.md` differs. The audit preserves the exact exception details
in JSON. It therefore does not claim every canonical-HEAD representation passes.

The all-auto-CRLF archive changes additional Cycle 01 files compared with the
actual mixed-EOL checkout and therefore also fails that earlier known-stale-set
gate. Restoring three Cycle 02 files cannot remove the unrelated earlier failure.
Consequently these experiments DO NOT prove a passing canonical-HEAD suite or
causally reproduce the original five Cycle 02-related failures. The exact
three-file byte comparison proves absence of substantive content changes; root's
actual worktree post-fix run is the appropriate test of the targeted maintenance
action. The strengthened scientific code is absent from all synthetic snapshots.

## Full-suite accounting and limits

The root agent's earlier full-suite observation was **114 tests: 109 pass and
5 failures/errors**, before forthcoming EPA-native tests. This bounded audit
independently reruns only the affected Cycle 04 module. Do not use 114 as the final
package-wide total after adding tests, or state that every current-worktree test
passes. Exact legacy failure/error counts appear separately above.

The temporary replay is not a fresh Windows checkout or dependency installation.
Cycle 04's historical readiness assertions do not describe the current journal
package. Root's targeted restoration has already made the three actual worktree
files match HEAD exactly; final full-suite verification is separate. The five
pre-fix failures/errors are not asserted to persist after that fix. The broader
Cycle 01 stale-set portability issue remains explicitly documented.

Reproduce using `python scripts/audit_strengthening_legacy.py` while HEAD remains
the recorded commit. The historical CRLF form is reconstructed only after matching
the directly observed pre-fix hashes. The script fails closed on a different HEAD
or substantive changes in the three inspected files. It requires Git and Python's
standard library.
"""


def main() -> None:
    report = audit()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "legacy_test_status.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "LEGACY_TEST_STATUS.md").write_text(render(report), encoding="utf-8")
    print(json.dumps({key: {field: value for field, value in report[key].items() if field not in ("tests", "problem_messages")}
                      for key in ("head_archive_without_auto_conversion", "synthetic_head_crlf_representation",
                                  "same_synthetic_crlf_tree_three_cycle02_lf_restored")}, indent=2))


if __name__ == "__main__":
    main()
