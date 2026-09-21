# Cycle 04 lineage decision

## Decision

Use **R3l** as the sole historical reconstruction anchor, identified by:

- filename: `PFFLS_R4_3_30R3l_AE_Manuscript_and_Supplement.pdf`;
- SHA-256:
  `681c04cc0d95a0b819b42f1403f601d0b0d7d1418aa9b9eff1a567615ca6eb8c`;
- byte length: 795,081;
- Drive file ID: `1EZOrRc0syIBa6OQdalVtBqfvsmQHa2nu`.

R3l is **not** R3nR7-AE and must never be labeled as the locked baseline.

## Why R3l

R3l is the latest identity-verified historical manuscript in the Drive bridge.
It contains the complete Main and Supplement in one 27-page PDF, preserves all
locked JRC and EPA counts, and preserves the critical boundary that the EPA
layer is sensitivity evidence rather than external accuracy.

R3f, R3a, R2, and R4.3.15 are retained only for lineage and omission checks.
The locally available R3d and R3i binaries were also hashed, but no Drive
mapping was established for them. No text is cherry-picked from multiple
versions to create an untraceable composite.

## Visual and extraction checks

All 27 R3l pages were rendered and inspected. No obvious clipping, overlap,
broken tables, black boxes, or broken equations was observed. A normalized
text-extraction hash and the Poppler version are recorded in
`historical_anchor_extraction.json`. These checks establish a stable historical
reference; they do not verify the calculations or establish identity with the
missing baseline.

## Resulting manuscript boundary

Cycle 04 produces only
`CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md`. It does not produce a synthetic
Main/Supplement PDF, because doing so would imply fidelity that the missing
authoritative source cannot support.
