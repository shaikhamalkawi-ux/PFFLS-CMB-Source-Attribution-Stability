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
code, and outputs were not recovered from the repository or Drive bridge.

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

## Exact blockers

1. The authoritative R3nR7-AE manuscript/supplement binary and editable source
   are absent from accessible storage.
2. The JRC row-level computational archive is absent.
3. The EPA row-level substitution archive is absent.
4. A complete manuscript source that can be compiled and redlined is absent.
5. The repository DOI/licence promised by the historical data/code statement is
   unresolved.
6. The target journal, final author metadata, and author-only declarations are
   not supplied.
7. Cycle 01's committed current-tree manifest has five known mismatches on this
   branch (four pre-existing plus the Cycle 04 `CODEX.md` state update) and must
   not be silently described as current-tree verification.

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
