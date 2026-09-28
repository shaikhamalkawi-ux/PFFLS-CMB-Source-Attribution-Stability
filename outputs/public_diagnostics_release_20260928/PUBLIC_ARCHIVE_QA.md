# Independent actual public-archive review

**PASS for the reviewed code-and-derived-results publication scope.** Completed 28 September 2026 at 15:26:58 UTC. This note is a post-build companion, not a member of the frozen archive. It does not assert that publication or remote download verification has already occurred.

## Exact archived object

| Object | Bytes | SHA-256 |
|---|---:|---|
| PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip | 50,396 | `87446073a89c34f6614f6eab77c12d3c908cec86d154277cd721a34a171ef3a0` |
| ZIP .sha256 sidecar | 111 | `69c0956ca522cb8c06301d7ee49345afbc551fd6e4e1cafca98a9ff5a6f02dba` |

Independently checked all 21 unique, normalized ZIP members, every member CRC, all 19 inventoried payloads against their corresponding source bytes, and all 20 manifest hashes. The inventory and manifest are the two generated members. Paths are relative and contain no traversal components or linked-file member types. No source or archive was changed or rebuilt.

The actual payloads are exactly four scientific code/test files, two upstream-derived CSVs, four aggregate-result files, one unchanged MIT notice, six new documentation/metadata files, and two new packaging/verification scripts. Seven payloads carry MIT, counting the retained notice; twelve carry CC BY 4.0, including the explicitly attributed upstream tables. No manuscript, TeX, figure, raw receptor/profile data, private complete ledger, correspondence, restricted paper, execution-plan file, or private Drive receipt is present. A bounded textual privacy scan passed; this is not antivirus certification.

## Cold extraction and actual verification

Extracted this exact ZIP once into a fresh directory with basename `pffls-public-cold-20260928-c44mmnnt`. This deliberately differs from the historical checkout name. Ran the included verifier once, from that clean extraction, using Python 3.12.14:

```text
python verify_public_release.py .
```

The process exited **0**, with empty standard error, in **0.370824 seconds**. Total local archive checking and verifier execution took **1.058448 seconds** before receipt serialization. These are bounded verification timings, not research-session time.

Actual returned statuses:

- Archive integrity: `PASS`, 19 payloads.
- Saved JRC scalar-summary arithmetic: `PASS`.
- JRC native reproduction: `false`.
- JRC algorithmic independence claimed: `false`.
- EPA: `NOT_REPRODUCED_MISSING_EXTERNAL_INPUTS`.
- New model fits, random draws, tests run, and verifier file writes: all zero.
- Producer `main()` called: `false`.

The verifier repeated the supplied JRC arithmetic in memory; it did not call a write-enabled producer, refit any CMB model, run artificial fixtures, or regenerate EPA saved-ledger results. All 21 extracted files had identical membership and hashes before and after verification; no bytecode/cache file appeared. The EPA missing-input status is an expected limitation, not a skipped check counted as native reproduction success.

## Creator, attribution, and claim scope

The archived citation names **Ghassan O. Malkawi only** as creator of this new diagnostics increment. Its upstream attribution explicitly retains **Malkawi, Elsayed, Alhagyan, and Hussein** and DOI `10.5281/zenodo.22976190` for the reused collaborative tables. The code notice remains `Copyright (c) 2026 PFFLS research contributors`. The new DOI is recorded as reserved `10.5281/zenodo.23019083`; this local check does not itself publish it.

The reviewed root GitHub citation and additive README introduction likewise restrict sole-creator metadata to the new release. They do not remove the paper's authors, rewrite earlier attribution, promote a manuscript baseline, or replace the prior frozen record. Exact root-file hashes are recorded in `PUBLIC_SOURCE_QA.md`.

The package correctly retains descriptive interpretation, dependent comparisons, the one-sample origin of the two strict EPA changes, missing JRC provenance, and incomplete EPA public-input reproducibility. It does not establish superior estimation, calibrated uncertainty, independent physical truth, or journal readiness.

## Remaining external verification

Publication may proceed with this exact archive and scoped metadata. Verify the actual public GitHub/Zenodo targets and creator/license/related-record metadata, then download and compare complete deposited file hashes. Do not infer successful upload, DOI resolution, merge, or submission from this local PASS. Detailed local execution receipt and checker source remain outside the public archive and need not be committed.
