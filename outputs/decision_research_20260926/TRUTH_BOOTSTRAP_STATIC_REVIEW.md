# Independent static review of saved-mask bootstrap replay

Date: 2026-09-26 UTC. Verdict: **PASS for the reviewed implementation; actual saved-ledger replay not performed by this reviewer.**

This bounded check read the complete new verifier and its nine synthetic tests,
then the unchanged producer's metric, paired-bootstrap and ledger-storage
functions. It did not import either module, run tests, open field/synthetic-truth
ledgers, fit models, or modify any frozen result. The root separately reported
successful synthetic test execution; that is not represented here as an
independent execution by this reviewer.

Reviewed identities:

- `scripts/verify_truth_bootstrap.py`: SHA-256
  `e2bbe4b5eca29eedbc3f25ed9d21c3b1892c6bb16ba4933428108ad28b92cb12`.
- `tests/test_truth_bootstrap_records.py`: SHA-256
  `7310036f8fbba87cacbc83742f6f7093216bacfa0c4cc3c50acd7132e44c4030`.

## Findings

1. The result and configuration are independently hash-pinned. Each of the
   seven ledgers is tied to the hash in that pinned result. NPZ parsing uses
   `BytesIO` containing the already checked bytes, with `allow_pickle=False`;
   it does not reopen an unchecked file after hashing.
2. Counts are reconstructed by integer row iteration, rather than importing
   the producer's metrics. Empty predictions, ambiguous predictions, and tied
   truth are distinguished correctly. A singleton within the true co-leader
   set is not a wrong singleton, but need not cover every true co-leader.
3. The independently constructed cluster multiplicity matrix matches the
   frozen shared PCG64 resampling design: 2,000 draws of 32 clusters, preserving
   all 24 paired rows within each cluster. The released descriptive panel is
   correctly required to have no bootstrap.
4. Integer count aggregation precedes division. Wrong-singleton risk is
   undefined when no singleton is retained; it is not changed to zero. Paired
   subtraction leaves a risk difference undefined when either component risk
   is undefined. Finite filtering therefore uses the intersection of defined
   paired resamples. Marginal and paired defined/total counts are checked
   exactly against the frozen report.
5. All 14 methods, the frozen alpha grid, and the complete recorded comparison
   set are checked. The quantiles use an explicit type-7 interpolation formula,
   not the producer's `np.quantile` call. The declared pre-replay absolute
   tolerance of `4e-15` addresses interpolation-order rounding only.
6. The implementation imports no producer or numerical solver and makes no
   model-fit call. Output is exclusively created. Its conclusion is restricted
   to saved-decision arithmetic replay and does not imply calibrated population
   coverage, matched decision coverage, independent data validation or zero risk.

No blocking defect was found. A useful additional synthetic test would give two
methods different subsets of defined-risk resamples and check explicitly that
the paired denominator is their intersection. The current code already has the
correct NaN propagation; this is a test-coverage recommendation, not a required
method change or a result-driven tolerance adjustment.

This static verdict permits a separately controlled replay; it is not that
replay's PASS result. Any later script change requires its own identity/review.

## Pre-replay test-only follow-up

The root added the suggested tenth test before actual ledger replay. This
reviewer inspected that addition: risks `[0, NaN, 0, 1]` and
`[NaN, 0, 1, 0]` yield two jointly defined differences out of four, with type-7
endpoints `[-0.95, 0.95]`. The assertions correctly test that intersection and
close the specific coverage recommendation above. The verifier is unchanged.
Updated test-file SHA-256:
`61a42672cf92e2efae4949f18d72f75115f6a6fe71e940dcd03786b6b4ed6558`.
This follow-up is static inspection, not a claim about the separate test-run or
saved-ledger replay outcome.
