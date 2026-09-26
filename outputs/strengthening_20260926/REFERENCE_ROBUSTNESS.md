# Conditional reference-ranking robustness diagnostic

Exploratory audit, 26 September 2026. No manuscript or baseline change.

## Evidence available

The inspected public archive supplies twelve scalar campaign-level error scores, an eight-component reference vector, and thirty reconstructed comparison rows. It does not supply the twelve fitted eight-component mean vectors, daily reference series, or a joint reference covariance. Consequently, a direct perturbed-reference reanalysis or statistical uncertainty propagation is not currently possible.

This diagnostic uses a consequence of the triangle inequality to give sufficient reference-perturbation budgets. It does not recreate the missing vectors.

## Mathematical guarantee

For fixed fitted allocations a and b and reference r, define D(r) = ||a-r||_1 - ||b-r||_1. Each L1 distance changes by at most ||r'-r||_1, hence |D(r')-D(r)| <= 2||r'-r||_1. A nonzero distance ordering therefore persists whenever ||r'-r||_1 < |D(r)|/2.

The published error scores e_a and e_b are percentages normalized by T0 = 43.09 ug/m3. Allowing an absolute reporting error of b percentage points for each score gives the conservative sufficient open-ball radius:

`radius = max(0, abs(e_a - e_b) - 2*b) * 43.09 / 200`.

The default b = 0.01 pp allows one full displayed unit per score, avoiding an undocumented assumption about rounding-to-nearest. A secondary b = 0.005 pp calculation is included in JSON and applies only if nearest rounding is justified. Neither envelope covers mistakes in the original computations. The displayed reference defines the center; reference rounding or other reference error consumes the same total L1 displacement budget.

The denominator at the perturbed reference may change. As long as it is shared by both candidates and positive, it does not change their ordering. The bound concerns ordering, not constancy of normalized regret.

## Results from the conservative full-unit envelope

All thirty reference-ordering labels, and thus the 9/30 primary discordance count, are certified unchanged for total L1 reference displacement strictly below **0.047399 ug/m3** (0.1100% of the original total). This small sufficient radius does not establish that a reversal occurs outside it.

W4-V2 remains the global minimum-error candidate for displacement strictly below **0.206832 ug/m3** under the same assumptions.

| Discordant comparison | Fit-favored | Reference-closer | Displayed error gap (pp) | Sufficient open-ball radius (ug/m3) |
|---|---|---|---:|---:|
| E01 | W3-V2 | W4-V2 | 0.98 | 0.206832 |
| E04 | W5-V2 | W4-V2 | 2.25 | 0.4804535 |
| E05 | W6-V2 | W4-V2 | 2.49 | 0.5321615 |
| E06 | W6-V2 | W5-V2 | 0.24 | 0.047399 |
| E07 | W3-V3 | W4-V3 | 0.53 | 0.1098795 |
| E10 | W5-V3 | W4-V3 | 0.80 | 0.168051 |
| E11 | W6-V3 | W4-V3 | 2.98 | 0.637732 |
| E12 | W6-V3 | W5-V3 | 2.18 | 0.465372 |
| E18 | W6-V4 | W5-V4 | 4.46 | 0.956598 |

### Declared perturbation-budget scenarios

These budgets are illustrative sensitivity settings, not estimates of actual reference uncertainty or confidence levels. Bounds apply to any reference within the stated closed budget ball; unresolved edge outcomes need not be attainable together because comparisons share the same reference. Falling outside a certificate only means this inequality is inconclusive.

| Budget (% of original total) | Budget (ug/m3) | Certified unchanged orderings / 30 | Guaranteed discordance-count bounds |
|---:|---:|---:|---:|
| 0 | 0.00 | 30 | 9 to 9 |
| 0.1 | 0.04309 | 30 | 9 to 9 |
| 0.5 | 0.21545 | 22 | 5 to 13 |
| 1 | 0.4309 | 20 | 5 to 15 |
| 2 | 0.8618 | 15 | 1 to 16 |

## Decision and limitations

- KEEP this conditional mathematical diagnostic and exact per-edge certificates as a separately labeled audit result.
- HOLD any claim that 9/30 is robust to the actual JRC reference uncertainty: its admissible joint region is unavailable, and the sufficient radii do not recover it.
- HOLD exact reversal thresholds until the fixed fitted allocation vectors are recovered. Even those vectors would not alone identify a statistical uncertainty distribution.
- REMOVE any inference that 20% synthetic construction noise is a standard error or confidence interval for the campaign mean. This audit makes no such conversion.

The fit selector and fitted allocations are frozen. The comparison universe is unchanged. No Monte Carlo draws, covariance, negative/positive dependence assumptions, missing profiles, daily values, or allocation components have been invented. No original CMB fits were rerun. These results do not validate a field profile or alter the accepted baseline.

## Reproduction and provenance

Run from the repository root:

```text
python scripts/audit_reference_robustness.py
python -m unittest discover -s tests -p test_reference_robustness.py -v
```

The adjacent JSON records all inspected CSV headers, row counts, SHA-256 hashes, exact decimal values, both reporting-precision envelopes, and software version. It is generated without network access or third-party Python dependencies. Inputs are read-only from the frozen public archive; reports are separate exploratory outputs.
