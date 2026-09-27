# Frozen truth benchmark: outcome and scientific decision

## Main result

**This benchmark does not support an incremental advantage for finite-profile point-leader unions.** The selected-point and finite-point-union decisions are identical on every one of **4,944 rows**, including failures. Every nonempty admitted family contains exactly one profile, always frozen profile index 0. None of the eight perturbed alternatives is admitted anywhere. Consequently, the ordinary union-of-contrast baseline also equals the selected-fit contrast baseline throughout this experiment.

That is a negative result for an empirical upgrade claim from this construction **in this frozen experiment**, not a proof that alternative profiles can never remain ambiguous. The historical EPA instability evidence remains a different experiment. The present predeclared profile perturbations and fit gate do not produce an accepted-profile ambiguity regime. They must not be tightened or otherwise retuned after seeing this outcome to manufacture one.

The benchmark uses known synthetic **82-channel integrated-signal** truth, not independently measured atmospheric source mass or named-source field truth. Profile uncertainty within each candidate is zero, and the historical clean-room EVLS solver therefore runs its WLS special case. No continuous-box interval/certificate method was included or validated by these results.

## Complete primary operating points

The two point methods coincide; the two contrast methods coincide. Contrast results below use the prespecified operational alpha 0.05. The machine results preserve all six alpha thresholds and all pairwise outputs.

| Panel | Rows | Point singletons | Point wrong | Contrast singletons | Contrast wrong | Empty failures, every method |
|---|---:|---:|---:|---:|---:|---:|
| Released descriptive | 336 | 336 | 0 | 312 | 0 | 0 |
| Generated included truth | 768 | 721 | 6 | 681 | 0 | 47 |
| Generated excluded profile truth | 768 | 0 | 0 | 0 | 0 | 768 |
| Generated correlated receptor errors | 768 | 765 | 5 | 719 | 0 | 3 |
| Generated uncertainty underreported by half | 768 | 0 | 0 | 0 | 0 | 768 |
| Generated source ID 4 omitted | 768 | 102 | 0 | 102 | 0 | 666 |
| Generated near-tied leaders | 768 | 721 | 72 | 135 | 0 | 47 |

Zero singleton counts give **undefined conditional error risk**, not zero risk. Zero observed errors among issued decisions do not establish zero population risk. Ordinary intervals remove the observed wrong-singleton decisions in the included, correlated, and near-tie panels, but report fewer singletons. This is a risk–coverage tradeoff, not an unconditional dominance claim.

The near-tie panel makes the cost especially clear: point reporting has 72/721 wrong singletons (9.99% observed conditional risk) at 721/768 reporting coverage (93.88%); alpha-0.05 contrasts issue only 135/768 singletons (17.58%) with zero observed errors. Both still have 47 empty failures. The paired whole-replicate bootstrap contrast-minus-point differences are [-0.1192,-0.0801] for conditional risk and [-0.7865,-0.7396] for reporting coverage. These descriptive intervals compare different retained singleton subsets, not matched-coverage populations.

For included truth, the corresponding risk difference interval is [-0.01517,-0.00277] and coverage difference interval [-0.05859,-0.04557]. Their interpretation is conditional on this fixed 24-row design and newly generated error law. The released panel has no independent-noise confidence interval; its supplied error matrix was not assumed to calibrate its construction residuals.

## Failures and source-universe limits

- Excluding the generating profile and underreporting uncertainty each rejects all 768 rows. These are failures/empty sets in every denominator, **not successful abstentions or certificates**.
- Omitting source ID 4 leaves only 102/768 rows with an admitted fit. ID 4 is the true integrated-signal leader in 32 generated rows; all 32 are failures, not recovered or correctly attributed cases. A zero wrong-singleton count among the 102 retained rows does not establish robustness to missing sources.
- Pairwise reporting retains all ten possible source pairs per row. The omitted-source case additionally reports the six within-fitted-universe pairs, while never inferring an order for absent ID 4.
- Admission is based on the unconstrained point estimate, shared nonnegativity tolerance, and residual-Q gate. Rejection of a point fit does not prove that a joint nonnegative confidence region is empty. The gate is frozen and was not altered after these failures appeared.
- All 44,496 attempted fits were numerically available; exclusions arise from the prespecified physical/Q criteria. Only 2,645 fits are shared-admissible. There are 2,299 rows without an admissible family. No negative coefficient was clipped or source pruned.

## Verification and preserved provenance

- Synthetic test gate: **40/40 PASS**, independently rerun by root and the mathematical auditor.
- Mathematical auditor's additional pre-results references: 24 random correlated-profile WLS cases checked against QR, 144 contrast decisions checked against a separate normal-tail implementation, and all 992 valid prediction/nonempty-truth-mask combinations. No blocking discrepancy reported.
- Separate saved-ledger verification: **4,944 rows, 44,496 numerical fits, all 14 method endpoints**. It reconstructs Q from frozen inputs and coefficients, checks weighted-Gram/covariance identities, admission, winners, all point/contrast candidate masks, co-leader truth, and aggregate/all-source denominators. All passed without refitting or changing parameters.
- The point-set/contrast-set containment invariant passed **31,740** checks. This established mathematical relation is not a novelty claim.
- The producer's field `fits_with_retained_tiny_negative_coefficients` technically counts within-tolerance negatives even if another gate rejects their fit. Independent review noted this label nuance; its value is **zero in all seven panels**, so it affects no numerical conclusion. Frozen producer files remain unchanged.

Implementation SHA256: `023d4c74f3dd91711e55144c9831059ed622afae3975b5bf64b1b792ea06b1ad`.

Configuration SHA256: `8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9`.

Generated-array archive SHA256: `78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1`.

Final results SHA256: `e4bf45de87335c853edc15170e3a8706a1540797069766fed552fe5ead49362b`.

Original v2 protocol bytes and source registry remain preserved. V3 clarification, successful tests, machine configuration, RNG states and input-array hashes preceded benchmark scoring. The only preflight correction was a synthetic test fixture, documented in `truth_test_preflight_notes.md`; no benchmark output informed it. Full arrays and per-row ledgers remain private. No manuscript or Git changes were made.

## Research implication

Keep this as an auditable **negative comparison and uncertainty-baseline control**. It strengthens the requirement to compare against ordinary joint-contrast uncertainty and to count selective reporting honestly. It does not establish a major new method, field accuracy, a calibration theorem, or empirical superiority of the separate continuous interval construction. Any later attempt to target accepted-profile ambiguity would require a new explicitly labelled protocol, independent evaluation, and renewed comparison against the strong ordinary baseline—not relabelling or retuning this run.
