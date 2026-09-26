# Legacy test status and line-ending isolation

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
conversion. Their Git blobs at commit `ebaed99aa9f7d2dec993fcfd11d62f3dd7eb95cf` match the frozen Cycle 02
manifest exactly. Before root's fix, removing only CR bytes forming CRLF sequences
reproduced those Git blobs exactly. The pre-fix bytes/hashes were directly recorded
before normalization; independently expanding each HEAD LF to CRLF recreates those
exact observed hashes. These historical bytes are not confused with the now-LF
worktree. `core.autocrlf` remains `true`; the
three files now have targeted `text eol=lf` attributes.

| File | Manifest/HEAD bytes | Observed pre-fix bytes | Added CR bytes | HEAD hash equals manifest? |
|---|---:|---:|---:|---|
| `outputs/cycle02/appendix_c_2008_2009_daily.csv` | 26799 | 27094 | 295 | yes |
| `scripts/extract_cycle02_fairbanks.py` | 15003 | 15428 | 425 | yes |
| `tests/test_cycle02_fairbanks.py` | 3512 | 3603 | 91 | yes |

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
| HEAD archive, no automatic EOL conversion | 22 | 17 | 1 | 4 | 0 |
| Synthetic HEAD auto-CRLF archive; three Cycle 02 files match pre-fix hashes | 22 | 17 | 1 | 4 | 0 |
| Same synthetic CRLF archive, only three Cycle 02 LF files restored | 22 | 17 | 1 | 4 | 0 |

Affected tests in the synthetic CRLF experiment:

- `test_builder_fails_on_missing_allowlisted_file`: ERROR
- `test_builder_fails_on_stale_qa_snapshot`: FAIL
- `test_builder_is_deterministic_and_members_are_exact`: ERROR
- `test_legacy_manifest_audit_records_known_state`: ERROR
- `test_repository_closes_hold_with_exact_blockers`: ERROR

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
