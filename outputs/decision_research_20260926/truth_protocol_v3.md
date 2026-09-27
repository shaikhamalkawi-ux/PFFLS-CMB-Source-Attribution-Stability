# Truth benchmark protocol v3: pre-outcome implementation clarification

Status: root-approved bounded implementation; **no method outcomes observed when these rules were written**. This document supplements, rather than overwrites, v2. The original `TRUTH_BENCHMARK_AUDIT.md` remains byte-preserved at SHA256 `5b5ad892f2ca2c44e498deab3e34118d67b85bad8e96ba08e72e5fdac6675ac0`; its original `truth_benchmark_sources.json` remains at SHA256 `f4530e2093f143f76d72536f18077bee729ecbc6fcc19094d16f671c5ca67bb0`.

## Scope unchanged

Only the 336-row released Zurich panel and the frozen 24-row × 32-replicate × six-regime generated controls are scored. There are no extra profiles, noise levels, scenarios, optimization certificates, or physical-unit claims. All five anonymous IDs stay fixed. The endpoint is the largest modeled **82-channel integrated signal**, `M=G*rowsum(F)`, with compensated normalized profiles `P=F/rowsum(F)` so that `MP=GF`. It is not total atmospheric source mass.

The released error matrix is not assumed to be the actual generation standard deviation: `(X-GF)/error` had SD 0.0264 in the input-integrity check. Generated controls impose a new Gaussian law with the released error matrix used only as a scale template. No empirical rescaling to observed or fitted residuals is allowed.

## Shared fit admission

Every method receives identical fits and source universes. Require finite observations/profiles, finite strictly positive receptor sigma, convergence of the historical clean-room EVLS solver, finite coefficients/Q/covariance, full column rank, and positive residual degrees of freedom. Profile uncertainty is zero within each fixed candidate, so this is the historical solver's weighted-least-squares special case, not a test of empirical profile-uncertainty calibration.

The numerical nonnegativity tolerance is `tau=1e-10*max(1,max(abs(s)))`. A coefficient below `-tau` excludes its entire fit. Tiny negative values within tolerance are retained **without clipping** and counted separately. No source pruning, constrained refit, or source-set change is permitted except the predeclared omitted-source regime. Apply the common gate `Q <= chi2.ppf(0.95,82-p)` inclusively. Record all applicable exclusion flags and an exclusive first-failure category; no failed or all-rejected row disappears from denominators.

Save two distinct winners:

- Diagnostic numerical minimum-Q winner among converged finite full-rank fits **before** nonnegativity and Q admission. This can contain negative coefficients and is not a primary admissible result.
- Primary minimum-Q winner among shared-admissible fits. “Unconditional point decision” means no contrast/CI threshold, not permission to conceal failed rows. If no fit is admissible, this winner and every primary method return an explicit failure state.

Equal numerical Q values select the lowest frozen profile index. This tie rule does not break source-contribution ties.

## Source ties, sets, and contrasts

Use the same `tau` rule for numerical source ties. Every true co-leader is retained. Primary truth-in-set coverage requires the prediction set to contain **all** true co-leaders. A singleton is wrong only if its ID is not a true co-leader. Empty predictions from failed rows are false for truth-in-set coverage, never successful abstentions. Wrong-singleton risk is undefined if no singleton is issued, not zero.

The ordinary covariance is based on the absolute supplied uncertainties: `V=(P W P.T)^-1`, `W=diag(1/sigma^2)`. Do not multiply by residual Q or an estimated scale. For each alpha in `[0.5,0.2,0.1,0.05,0.01,0.001]`, use two-sided Bonferroni normal thresholds over the fitted `p*(p-1)/2` unordered source contrasts. Variance of a contrast is `Vjj+Vkk-2Vjk`, including covariance. Selection of a profile and admission by Q invalidate an automatic nominal-coverage claim; alpha labels are operational thresholds only.

To make numerical tie treatment coherent, include source j in a contrast candidate set when every `upper(s_j-s_k) >= -tau`; certify strict order only when `lower(s_j-s_k) > tau`. This v3 numerical-margin clarification replaces v2's literal zero comparisons. Tiny negative contrast variance attributable to floating-point cancellation may be set to zero within `1e-12*max(1,max(abs(V)))`; more negative variance is a numerical failure, not silently repaired.

Four primary method families are fixed:

1. Shared-admissible minimum-Q point argmax set.
2. Joint-contrast candidate set of that selected fit, at all six thresholds.
3. Union of the joint-contrast candidate sets across all shared-admissible fits, at the same thresholds.
4. Union of shared-admissible point argmax sets.

The fourth set is mathematically a subset of the third at each threshold. This invariant, and selected-point containment in selected-contrast sets, must be tested and checked during scoring. It is a known construction, **not a new-method claim**. The finite-point method has one operating point, not an artificial six-point curve.

## Omitted source and denominators

The source-4-omitted regime generates all five source contributions but fits only IDs 0–3. Truth and singleton metrics retain the full five-ID universe and all rows. Pairwise reporting gives both all **10** possible pairs per row and the **6** within the fitted universe. Pairs involving omitted ID 4 are unreported, not silently removed from the all-source denominator. Any declaration opposite a true order, or strict declaration across a true numerical tie, is false.

Report all-row singleton coverage, conditional wrong-singleton risk, all-co-leader truth-in-set coverage, nonempty ambiguity, empty failures, set size over all rows and over nonempty predictions, pairwise declaration frequency and false-declaration risk. Numerical pre-admission winner statistics are labelled diagnostic and kept separate.

## Paired comparisons and uncertainty

Retain all six alpha operating points. The generated-control bootstrap resamples the 32 replicate IDs jointly across methods, carrying all 24 rows, for 2,000 replicates using the frozen third seed. Report paired risk and coverage differences separately; unlike retained subsets are not falsely described as identical samples or matched coverage. Undefined-risk bootstrap draws are counted and omitted only from that risk quantile, not from coverage. Zero observed errors, or a zero-width empirical bootstrap interval, do not prove zero population risk. The external released panel receives descriptive metrics, not a fabricated independent-sample coverage interval.

Predeclared comparisons: every other endpoint against the selected-point endpoint; union-contrast versus selected-contrast at each shared alpha; finite-point union versus selected-contrast and union-contrast at alpha 0.05. Publish the complete metric grid and failures. No threshold is selected because its risk looks favorable. Any apparent gain from reduced reporting must be shown as a risk–coverage tradeoff, and comparisons with the strong ordinary union baseline remain central.

## Execution gates

1. Pass synthetic unit tests before reading or fitting the benchmark in the scoring stage. Include independent WLS/covariance checks, gate boundaries, nonfinite/invalid scales, negative-coefficient admission, ties, omitted-source denominators, all-rejected cases, the subset invariant, scale invariance, generation reproducibility, and tamper/freeze tests.
2. Save an immutable machine configuration, environment, v2/v3 protocol hashes, implementation/solver/test hashes and test result.
3. Generate and privately save all candidate profiles, observations, sigmas, truth, noise arrays and RNG states; save their individual array hashes and archive hash **before any fitting/scoring**.
4. Send the passing test summary and implementation hash to root before scoring. Score only these frozen inputs. Save each panel's private numerical ledger and public aggregate checkpoint; preserve nulls and failures. An interrupted run may resume only if every frozen hash still agrees.

No manuscripts, external services, or Git state are modified by this experiment.
