# Secondary experiment plan — frozen before held-out observations are read

Status: planned exploratory feasibility test, not a claim of novelty or external source-accuracy validation.

The native table headers expose three concentration/uncertainty pairs outside the frozen 20-species fit: SUXC, CUXC, and ZNXC. TMAC is mass, already used in diagnostics, and is excluded. No values of these three receptor concentrations have been inspected for designing this experiment. Sulfur (SUXC) is chemically related to fitted sulfate; do not call it an independent endpoint, and unknown error covariance limits all screening claims.

## Pre-observation design

Use the joint-profile agent's unmodified converged basic-eligible scenarios per sample. Restrict the secondary physical-feasibility screen to scenarios with all contributions nonnegative, report the attrition, and do not let this change the primary enumeration. Require complete finite source and uncertainty fields and positive receptor uncertainty for each candidate. Predictions are linear sums of source-profile fractions times already-fitted contributions. No new fitting or tuning to held-out means.

For each candidate and each pair of scenarios with different unique top-source labels, calculate absolute prediction separation divided by the sum of their predictive error scales. For a scenario, the scale is sqrt(receptor uncertainty squared + sum over sources of (profile uncertainty times fitted contribution) squared). This is only a heuristic error scale: fitted-contribution uncertainty, covariances, and model discrepancy are not available and are NOT silently assumed accounted for. Score a candidate by its minimum separation across all cross-top pairs. Select the largest score, breaking exact ties lexicographically. Save choices, scores, scenario-set/input/code identities, and a timestamp BEFORE reading held-out receptor means. If no conflicting scenario pair exists, report not applicable. If all scores are zero or negligible, keep that failure rather than choose by hindsight.

## Held-out check after freezing design

Only after the pre-observation record exists, evaluate all three candidates under the same prespecified absolute standardized residual cutoffs 1, 2, and 3. These cutoffs are sensitivity scenarios, not confidence levels. Report retained scenarios, retained top-source sets, rejected-all cases, and no-reduction cases. Compare selected-candidate ambiguity reduction with each fixed candidate, not just the best retrospective candidate. Excluding all scenarios is a misspecification warning, not successful attribution. Retaining one source label demonstrates only conditional model-set screening, not that the surviving label is environmentally true. Unresolved fits still prevent whole-universe certificates.

## Boundaries

Per-sample predictions, held-out values, choices and full vectors stay in private/decision_research_20260926. Public output contains aggregates, code, configuration, provenance, limitations and reproducible tests. No raw third-party re-publication. If the joint experiment yields no eligible ambiguities, record this test as not applicable rather than expand the universe post hoc.
