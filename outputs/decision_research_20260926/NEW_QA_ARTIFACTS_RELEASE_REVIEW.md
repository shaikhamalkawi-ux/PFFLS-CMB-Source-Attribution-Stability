# Release-boundary review of new QA artifacts and licence notices

Date: 2026-09-26 UTC. Disposition: **PASS for these exact eight artifacts only**.

This content review read every file in full, including all nested entries in
the cleanroom JSON's 94-file hash inventory and all seven panels in the new
bootstrap verification JSON, followed by both complete licence notices. It did not rerun tests, resampling, fits, LPs or
saved-ledger verification. The bootstrap result was inspected only after the
root confirmed its completed, exclusive write.

## Exact reviewed bytes

Paths below are repository-relative.

| Artifact | SHA-256 |
| --- | --- |
| `outputs/decision_research_20260926/PUBLIC_CLEANROOM_QA.md` | `3e1e7362aec4efcbd183096d2dd8fd6f5ba5fb1f53bfc48efe025b36d6a004bf` |
| `outputs/decision_research_20260926/public_cleanroom_qa.json` | `ddaca8754e469f86d3b2bc271776fdd65500e0c1f1390c4d67f487867040b7c1` |
| `outputs/decision_research_20260926/TRUTH_BOOTSTRAP_STATIC_REVIEW.md` | `d8071d392b50288940467895ec2e899d7314255701616b9e75edc7a3d9885f71` |
| `scripts/verify_truth_bootstrap.py` | `e2bbe4b5eca29eedbc3f25ed9d21c3b1892c6bb16ba4933428108ad28b92cb12` |
| `tests/test_truth_bootstrap_records.py` | `61a42672cf92e2efae4949f18d72f75115f6a6fe71e940dcd03786b6b4ed6558` |
| `outputs/decision_research_20260926/truth_bootstrap_verification.json` | `b02553d5b16e9d71a07fdc21e3f1498816882cd39032dfd12ec7ffbc08c543fd` |
| `outputs/decision_research_20260926/LICENSE_SCOPE.md` | `91760a7bc5cd4b65d8c6e7bc024786fc0fa9713fb47cdfec0a444a26888d0549` |
| `outputs/decision_research_20260926/LICENSE_CODE_MIT.txt` | `4f00b65cc36c64381dddc73fb5aa0f73bb0d1b8318263d78ee5fd29ea394912a` |

## Boundary findings

- No receptor/profile arrays, saved prediction/truth masks, proof vectors,
  sample/case identifiers, personal correspondence, account credentials,
  tokens, absolute owner paths or snapshot locations appear in these files.
- The JSON inventories contain repository-relative public filenames, byte
  sizes, SHA-256 fingerprints, runtime identities and aggregate QA counts.
  The bootstrap result also contains non-reconstructive private-ledger
  fingerprints for provenance. These fingerprints do not release the ledger
  contents or imply permission to obtain or redistribute them.
- Code references to a repository-relative `private` directory and fixed
  ledger-name templates describe required inputs, not machine locations or
  private sample identities. Test arrays are small, explicitly synthetic
  adversarial examples, not excerpts of native observations.
- No blanket third-party licence or redistribution claim is made. This review
  grants no new rights over archives, owner-only proof records, papers or
  neighboring artifacts; existing applicable code/documentation licence scope
  remains separate.
- The two new licence notices apply only to author-created files explicitly
  listed in a final `PUBLIC_RELEASE_MANIFEST.json`: original Python code/tests
  under MIT and author-created documentation/aggregates under CC BY 4.0. An
  initial omission of the original Python verifier under the output directory
  was flagged and corrected by the root; the final scope hash above includes
  that correction. Third-party inputs, dependencies, old archives and private
  returns remain expressly excluded. **Actual release remains HOLD until its
  final explicit manifest exists.**

## Claims and limits

The cleanroom report correctly separates **302 executed passes** from **four
integration skips** and limits its conclusion to the 94-file public subset's
synthetic workflow. The owner-only snapshot/raw-log report is not included.

The static bootstrap review distinguishes source inspection from test or ledger
execution and records the later test-only addition. The completed bootstrap
JSON reports **504 checked interval summaries**, zero endpoint difference in
each of the six resampled panels, and no new fits. These are saved-decision
arithmetic checks, not additional observations, calibrated population coverage,
matched decision coverage, zero-risk evidence, or full public field replay.

No release-blocking content was found in the exact eight files. This is not a
privacy certification of the whole working tree or a publication instruction.
The original 94-file allowlist was not edited. Any addition to a release must
name these files explicitly; do not include the adjacent owner-private report,
snapshot, runtime dependencies, raw archives or underlying ledgers. Changed
bytes require a fresh bounded review.
