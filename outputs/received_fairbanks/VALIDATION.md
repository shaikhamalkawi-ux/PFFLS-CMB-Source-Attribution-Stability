# Validation record - 2026-09-25

Environment: Windows, CPython 3.12.14, openpyxl 3.1.5. All original XLSX files were opened read-only; source ZIP/member SHA-256 identities were checked before parsing. No formulas were executed and no workbook was saved.

## Independent checks completed

- Root and independent reviewer directly inspected both formula and cached views of the missing native endpoints. The 52/53/54 separation is source-grounded, not a forced count match.
- Independent reviewer reproduced the native and sensitivity cohorts, categorical comparisons, and denominator behavior. Three minor review findings were corrected: partial-fill now preserves any existing native endpoint; inclusion language is marker-specific; 13.3 is explicitly identified as sensitivity-only.
- Primary public aggregate reproduces from original hash-locked inputs. Formula caches agree with arithmetic at tolerance 1e-9 pp for all 455 comparable endpoints.
- Published Peger revised-OMNI header order visually checked; regression tests cover two published rows. Original EPA/OMNI wood-smoke outputs unchanged.
- Historical Cycle 04 validator now validates its SHA-locked archived administrative snapshot, not obsolete phrases in today's mutable project documents. The historical QA report remains byte-identical; scientific gates remain fail-closed. Only the changed validator's current manifest entry is refreshed.
- Final full repository suite with private integration enabled: **88/88 tests PASS** (38.131 seconds). This includes 17 received-data tests and 15 synthetic private-return builder tests. No skipped tests in this run. `git diff --check` passes; existing line-ending notices are not test failures.
- Author PDF/source: independent author-line, superscript/affiliation, removed-name, metadata, unchanged-science, supplement, and visual checks PASS. Detailed candidate QA and member hashes accompany the private return.

## Commands

```text
python scripts/audit_received_fairbanks.py --input-zip <original-private-attachment.zip> --output-dir private/received_fairbanks/independent_reproduction --public-summary outputs/received_fairbanks/aggregate_summary.json
python -m unittest discover -s tests -v
git diff --check
```

The optional integration test requires `FAIRBANKS_RECEIVED_ZIP` to reference the original archive. Without private data that test intentionally skips; the synthetic public tests require no private observations.

No successful test is a claim of source-native CMB rerun or external accuracy validation. The scientific gate remains HOLD.
