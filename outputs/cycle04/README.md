# Cycle 04 — submission-candidate reconstruction gate

## Outcome

**HOLD_WITH_EXACT_BLOCKERS**

The exact R3nR7-AE artifact was not recovered from accessible project storage.
R3l is used only as a hashed historical anchor. The candidate delta is not
R3nR7-AE, is not a full reconstructed manuscript, and is not the locked
baseline.

The central JRC and EPA results remain locked exactly as reported. Cycle 04
verified their presence and consistency in the R3l historical anchor, but did
not independently recompute them because the exact row-level inputs, selectors,
code, and outputs were not recovered from the repository or Drive bridge. That
missing raw archive is recorded as an archival reproducibility limitation; it
does **not** silently reopen the previously accepted scientific lock as a new
submission requirement.

## Review order

1. `LINEAGE_DECISION.md`
2. `baseline_search_manifest.csv`
3. `historical_manuscript_inventory.csv`
4. `LOCKED_RESULTS.json`
5. `claim_evidence_traceability.csv`
6. `reproducibility_gap_register.csv`
7. `CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md`
8. `SUBMISSION_READINESS_MATRIX.csv`
9. `KEEP_HOLD_REMOVE.md`
10. `EDITORIAL_RECOMMENDATION.md`
11. `reproduction.md`
12. `qa_report.json`
13. `test_results.txt`
14. `artifact_manifest_sha256.csv`

`historical_manuscript_inventory.csv` is the Cycle 04 source/provenance
inventory. It records identities only; no historical PDF is redistributed.

## Current submission blockers

1. The authoritative R3nR7-AE manuscript/supplement binary and editable source
   are absent from accessible storage.
2. A complete manuscript source that can be compiled, redlined, and subjected
   to the final full-text audit is absent.
3. The repository DOI/URL and licence promised by the historical data/code
   statement are unresolved.
4. The target journal/package requirements and final author-controlled metadata
   and declarations are unresolved.

## Non-blocking archival reproducibility gaps

- The JRC row-level computational archive is not currently accessible.
- The EPA row-level substitution archive is not currently accessible.
- Cycle 01's committed manifest represents an earlier snapshot and has known
  current-tree mismatches. This is archival housekeeping debt, not a manuscript
  science gate.

These gaps must remain explicit. The central results must not be described as
independently recomputed or fully raw-data reproducible unless the archives are
recovered, but their current absence does not by itself invalidate or reopen the
accepted R3nR7-AE scientific lock.

## What this cycle does establish

- the accessible-storage search is documented;
- Drive folder/query result IDs and snapshot hashes are frozen;
- historical artifact identities are frozen with SHA-256;
- R3l is the nearest defensible anchor without being renamed;
- all locked counts and claim boundaries are machine checked;
- the manuscript-facing delta is explicit and minimal;
- the return package is allowlisted, deterministic, and contains no manuscript
  PDF or third-party raw data;
- the extracted return package validates without the full repository checkout.

No scientific result, source universe, selector, or accepted baseline is
changed by this cycle.

Outreach is unchanged: Palmer/Ward and Watson/Chow remain user-reported pending
and unverified, and the ADEC public-records request remains draft only and was
not sent.
