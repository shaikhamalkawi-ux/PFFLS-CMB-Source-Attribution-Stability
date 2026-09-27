# Independent review of post-hoc Farkas margin completion

Date: 26 September 2026. Status: **independent implementation, adverse tests and complete saved-record replay PASS**. The separate post-hoc layer certifies the unchanged margin for the remaining union, conditional on its declared models; the original Stage3 HOLD is preserved.

This separate review does not alter the frozen Stage3 result of 34 unions
without a guaranteed unique leader and one fixed-margin HOLD. The question is
whether already-saved exact infeasibility certificates imply the same declared
margin by a different algebraic proof path, without new LPs or new assumptions.

## Frozen identities

| Artifact | SHA-256 |
|---|---|
| Approved proof-only protocol | `f67d9288b8ed6e546c01f7a24af1993b37bb4a95b78a7bd1b5b4222a69391783` |
| Proof-only producer | `b5a95a583c533e9dd28cccd6a2737de1bf4b06425b986cad2b20510fe84f54a0` |
| Producer synthetic tests | `88f1dd649e9bc8bda30da3535e056d9972d20b50380e93ec226dd8ba5c421b78` |
| Pre-evaluation configuration | `eb76edf1493a94e7aae172039ea636f47557f0e98f102865036e702a9d6a005b` |
| Frozen exact bound ledger | `b4148121cec2e76b91a6ed4ec8f5818c9d2118b2eaac9f80e56df7bf61854c80` |
| Original Stage3 index | `383b73ca7b0ebdb79b04008adff2085acbca48f2be8b5355062ec73d86452d92` |
| Original Stage3 configuration | `33f10f141aad7d8dc5f72bf7cfd06e89c7a2f61c839f1fd8f3b50477f086331a` |
| Independent Stage3 validator | `2c68cb669ceaff1d95b419e517be4f96f32c37425f2529cab2f2a4ee437dbd5b` |
| Independent exact-primitives validator | `53d1682413236b394fc24adae1d2dea75c2a621799947111e9a835a5afea1fed` |

The proof-only producer froze configuration after its synthetic tests and before
field gamma/B evaluation. The independent reviewer performed no field gamma/B
calculation before that freeze. There is no solver or multiplier search in the
proof-only producer or independent validator.

## Mathematical assessment

For s>=0 and Gs<=h, competitor j's co-leader rows are
D_j s<=0, one row s_k-s_j for each k other than j in the original source order.
The stored certificate supplies nonnegative multipliers (a,b) satisfying

`aG+bD_j >= 0, a.h = -gamma < 0.`

Multiplying the nonnegative column residual by s>=0 gives
bD_j s >= -aG s >= -a.h = gamma. Equality of the residual to zero is not required.

Only after **all six** competitor co-leader infeasibilities and a feasible W
co-leader point establish that W is the maximum at every base-feasible point may
we use s_k-s_j <= s_W-s_j. Since b>=0,

`gamma <= bD_j s <= B(s_W-s_j), B=sum(b)>0.`

Therefore s_W-s_j >= gamma/B. The implementation must reject zero/negative B,
wrong source-row mappings, negative residuals, missing competitor proofs and
invalid base/W witnesses. Positive rescaling of all multipliers leaves gamma/B
unchanged. This is established linear-inequality/Farkas reasoning, not a new
theorem.

A union certificate additionally needs the same W in every nonempty component,
all120 original systems accounted for, and every derived bound **strictly above**
the unchanged delta=1e-7*max(1,TMAC). Equality fails. An empty union is not a
unique-leader certificate.

## Implementation and adversarial tests

The full producer and tests were read. No blocking error was found in the
universal-maximum prerequisites, original augmented-row construction, multiplier
partition, contradiction sign, rational bound arithmetic, strict threshold
comparison or same-W complete-union rule.

The reviewer independently reran all **33 producer synthetic tests: PASS**.
A separate **19-test independent suite passed** in
`tests/test_interval_farkas_records.py`. It includes a positive nonzero
augmented column residual and a multiplier on a non-W comparison row, checking
the general inequality argument rather than only zero-residual examples.
It also tests wrong signs, row ordering, omitted premises, arbitrary leader
selection, nonfeasible bases, scaling invariance, threshold equality/below,
incomplete unions, different W across systems and empty unions. The independent
suite completed in 1.238 seconds. Host startup/I/O latency before its first
output was kept separate from execution time; no duplicate field run was launched.

## Independent saved-record replay

The separate checker is `scripts/verify_interval_farkas_records.py`. It imports
only the two independent standard-library validators identified above, not a
producer or numerical solver. It reconstructs every selected tuple directly from
identity-checked original native archives, including each profile's own means
and uncertainties, then checks all rational source proofs and all derived scalar
fields. Its own output is
`outputs/decision_research_20260926/interval_farkas_certificate_verification.json`.

The replay checks the original35-sample accounting and faithful Stage3 review
chain; exact120-system ordering; 72 base infeasibility certificates; 48 base and
W co-leader witness pairs; all288 augmented Farkas exclusions; all gamma, B,
column residual, lower-margin and unchanged-threshold values; and all provenance
hashes. It verifies the original Stage3 report/results remain unchanged.

The complete independent replay **passed in 23.015 seconds**, finishing at
**21:34:30 UTC on 26 September 2026**. Verified:

- All **120 original-decimal profile-system models**, including each alternative's
  own means and uncertainties, matched their source hashes and exact matrices.
- All **72 base infeasibility certificates**, **48 base/W witness pairs**, and
  **288 competitor co-leader exclusions** were checked with rational arithmetic.
- The same universally largest family is **vehicle** in every nonempty component.
  All six competitors were excluded before any margin was treated as a bound.
- All **288** computed lower margins are **strictly above the original delta**.
  There are no equal/below/missing bounds and no unresolved component in this
  proof-completion layer.
- **61** augmented certificate residual vectors have at least one strictly
  positive entry. This confirms that the general nonnegative-residual proof,
  rather than an unjustified equality-only simplification, is needed here.
- The exact conservative minimum lower margin is
  `6707647819/84938406600`; the unchanged delta is `85181/50000000000`.
  Their exact ratio is `1676911954750000000/36175692062973`, approximately
  **46,354.66**. This ratio concerns a numerical reporting threshold only.
- All **35** samples remain accounted for: **34** inherited witnessed
  non-unique unions, and this one separately completed conditional margin
  certificate. The original Stage3 result is still **34 plus one HOLD**.
- **Zero LPs, new fits, multiplier searches, or input/threshold changes** were
  used. Original Stage3 report and result hashes were rechecked unchanged.

Independent verifier SHA-256:
`e71f43fd865e2b657109f32bd76f9f47786ab4d1a732315fdb0391c63ad17521`.
The full machine-readable aggregate is in
`outputs/decision_research_20260926/interval_farkas_certificate_verification.json`.

Reproduction, with the private frozen inputs available in their declared paths:

```text
python -m unittest discover -s tests -p test_interval_farkas_records.py -v
python scripts/verify_interval_farkas_records.py
```

The validator depends on the preserved independent Stage2 and Stage3 validators,
their original archive/recovery/selectors and proof-index/case chain, and the
separately frozen proof-only protocol/configuration/manifest/ledger. It reads
existing results and exact certificates; it does not reproduce them by solving
the original optimization problems again.

## Interpretation boundaries

This is a separate **post-hoc proof-completion layer**. The original fixed-margin
HOLD and its numerical proof-gap history must remain visible. The large ratio
of a bound to delta, if confirmed, is a ratio to a **numerical reporting
threshold**, not a confidence level, environmental effect size, validated
uncertainty scale or probability of correct attribution.

Any verified lower margin is conservative and derived from the existing
multipliers, not necessarily the sharp optimum. Conclusions remain conditional
on the declared nonnegative independent receptor/profile boxes, finite historical
profile family and per-sample latent-profile interpretation. Physical profile
attainability, shared profiles across samples, external truth and statistical
coverage are not established. No manuscript, source data, threshold, frozen
producer or original classification was edited by this independent review.
