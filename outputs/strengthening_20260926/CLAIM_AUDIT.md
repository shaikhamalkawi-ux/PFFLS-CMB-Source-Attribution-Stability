# Independent publication-derived claim audit — 26 September 2026

## Scope and result

This new audit leaves the active manuscript baseline and published archive unchanged.
It does not rerun CMB, reconstruct missing model outputs, or validate environmental accuracy.
The original public package's 20 manifest entries match their hashes.
The full machine-readable result, input hashes, edge decisions and all rank refinements
are in `claims_audit.json`.

**Scope update:** This report assesses only the frozen publication-derived archive.
The later, separately executed native-input EPA clean-room reconstruction is in
`EPA_NATIVE_RECONSTRUCTION.md` and `epa_native_reconstruction.json`. That independent
work reproduces the EPA worked case and headline aggregates from recovered native
inputs. The false raw-reconstruction flags and gaps below are local to this
publication-summary audit, not a claim that the new combined work still lacks an
EPA numerical reconstruction. The original historical executable ledger remains
distinct from a new clean-room calculation.

## JRC primary result: KEEP with explicit provenance

Reconstructing the complete 4-by-3 grid independently gives 30 one-profile
comparisons: 18 wood-profile and 12 vehicle-profile comparisons, with five neighbors
per profile set. The reported 9/30 lower-mean-chi-square discordances are reproduced;
all nine occur within wood-profile comparisons. Every reconstructed endpoint agrees
with the frozen publication-derived ledger. This does NOT recover the original
unrounded CMB ledger or validate the source-native fits.

| Edge | Compared sets | Fit-favored | Reference-closer | Displayed regret (pp) |
|---|---|---|---|---|
| E01 | W3-V2 / W4-V2 | W3-V2 | W4-V2 | 0.98 |
| E04 | W4-V2 / W5-V2 | W5-V2 | W4-V2 | 2.25 |
| E05 | W4-V2 / W6-V2 | W6-V2 | W4-V2 | 2.49 |
| E06 | W5-V2 / W6-V2 | W6-V2 | W5-V2 | 0.24 |
| E07 | W3-V3 / W4-V3 | W3-V3 | W4-V3 | 0.53 |
| E10 | W4-V3 / W5-V3 | W5-V3 | W4-V3 | 0.80 |
| E11 | W4-V3 / W6-V3 | W6-V3 | W4-V3 | 2.98 |
| E12 | W5-V3 / W6-V3 | W6-V3 | W5-V3 | 2.18 |
| E18 | W5-V4 / W6-V4 | W6-V4 | W5-V4 | 4.46 |

Discordant median regret is 2.18 pp and maximum
regret is 4.46 pp, calculated from displayed values.

### New displayed-precision robustness check

Assume each displayed mean chi-square was rounded to the nearest 0.0001 and each
displayed error to the nearest 0.01 pp. Give every value its conservative closed
half-last-place interval. All 30/30 comparison classifications
remain unchanged throughout those intervals: even the smallest residual chi-square
separation is 0.00030, and the smallest residual error separation
is 0.230 pp. This is an interval proof, not a Monte Carlo sample.

Thus ordinary display rounding cannot explain away the reconstructed 9/30 result.
This check concerns numerical display precision only. It is not uncertainty
propagation for the external reference, receptor measurements or source profiles.
The 30 comparisons share profile sets and are not independent random trials;
no binomial confidence interval or population p-value is added.

## Secondary R-squared correlation: compatible, not verified

Using exact ties in displayed R-squared values gives Spearman rho
0.927725666496, rather than the manuscript's 0.909. Exhaustively
refining only the two displayed tie groups (sizes 3 and 2) gives
39 weak rank orderings, including 12 fully
strict orderings. Their possible rho range is 0.902097902098
to 0.937062937063;
3 weak orderings, of which
3 are strict, round to 0.909.

The reported value is therefore **compatible with unrounded ranks**. This is not a
recovery of the actual ordering: possibilities have no probabilities, and no latent
R-squared values are imputed. HOLD exact verification pending the original outputs.
Do not silently replace 0.909 by the rounded-table correlation or call it a proven error.

## EPA aggregate counts: KEEP as reported; HOLD row-level verification

The ten alternative-level attrition rows sum to 345 eligible substitutions,
323 converged and 22 nonconverged. The reported converged / two-diagnostic /
three-diagnostic subsets have respectively 323 / 283 / 26 rows, ordering-change
counts 167 / 133 / 10 and largest-source-change counts 81 / 62 / 2.
The displayed percentages 47.0% and 21.9% follow from 133/283 and 62/283.

Conditional on the stated nesting and consistent strict ranking, the complementary
strata contain 40 / 257 rows, with 34 / 123 ordering changes and 19 / 60 largest-source
changes. All count inequalities are consistent. These are arithmetic consequences
of aggregate assertions, not recovered row identities or a verification of actual nesting.

The archived worked Fresno example does not supply complete contribution vectors
for every source or the full substitution ledger. Therefore neither it nor the
aggregate CSVs can independently regenerate 133 or 62 event classifications.
Raw rerun and row-level event checks remain explicitly false in the JSON audit.

## What would close the remaining gaps

1. JRC: original receptor/profile inputs, exact settings, unrounded contributions and
   diagnostics for all 12 profile sets; the canonical 30-comparison ledger and
   reference mapping. A precision audit is not a replacement.
2. EPA: exact sample/alternative IDs; full unrounded central and alternative source
   vectors; convergence/diagnostic masks; source-label and tie-handling rules;
   then regenerate all 345 / 323 / 283 / 26 masks and 133 / 62 event labels.
3. Keep field sensitivity separate from external accuracy. Do not add a claim of
   full reproducibility or external validation based on this audit.

## Reproduce

From the repository root, using Python 3 (standard library only):

```text
python scripts/audit_strengthening_claims.py
python -m unittest discover -s tests -p test_strengthening_claims.py -v
```

Outputs are deterministic for a fixed Python version and input archive. The script
fails closed on missing/corrupt inputs and cannot write within the frozen archive.
No manuscript, published archive, baseline or scientific count was changed.
