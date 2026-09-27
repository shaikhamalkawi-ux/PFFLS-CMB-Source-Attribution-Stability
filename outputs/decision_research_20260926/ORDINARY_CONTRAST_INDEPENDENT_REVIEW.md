# Independent review of the ordinary joint-contrast comparator

Date: 26 September 2026. Review began at 20:40:56 UTC and was bounded to fifteen
minutes. Status: **KEEP as a correctly qualified post-hoc comparator**. No
blocking mathematical or numerical error was found in the current 35-sample
result. This is not a novelty endorsement, coverage validation or environmental
accuracy assessment. No frozen comparator file or manuscript was modified.

## 1. Reviewed scope and identities

Read the complete plan, script and tests, and verified their identities against
the comparator configuration:

- Plan SHA-256: `3bdb140ff571c179c4dd31eae71d703738405d4b815a5451be622d64315690b3`.
- Script SHA-256: `02582945e9eda03d9706501febfa013f38ae89a189eeb2165a496036b3bb1def`.
- Tests SHA-256: `bc4d6d5679b1f4aeefdd009fed776d955a77059d75bd92ef8fe0d055ca837c94`.
- Private ledger SHA-256: `a631420b2eb349715aba2fcc61da1f4a1094813432f3dddf68f298c3d3ce528f`.

The unchanged native solver and joint-ledger identities were also checked.
The public result, private ledger and configuration agree. The comparator is
explicitly post hoc: the prior joint-profile results were already known when
its plan was written. Writing the plan before computing this comparator does
not make it a preregistered primary analysis or independent validation.

The reviewer independently ran all **11 supplied tests: PASS**.

## 2. Mathematical and weighting review

With a declared fixed design F and fixed final-solve variance matrix D, the
implemented plug-in covariance is

\[
 V=(F^TD^{-1}F)^{-1}.
\]

The SVD implementation is correct: if the whitened design has right singular
vectors R and singular values d, it forms `R diag(d^-2) R^T`. It does not invert
a poorly conditioned normal-equation matrix as its primary numerical method.

The contribution contrast variance correctly includes covariance:

\[
 \operatorname{Var}(\hat s_j-\hat s_k)=V_{jj}+V_{kk}-2V_{jk}.
\]

Therefore this comparator is stronger than treating estimated source contributions
as independent or comparing separate marginal error bars. Positive and negative
off-diagonal covariance are handled in the appropriate directions.

The variance used is the variance of the **last weighted least-squares solve**,
not a newly recomputed variance after the terminal contribution estimate. Replaying
the frozen iteration count from zero in the final retained universe matches the
native controller's last restarted fit. It does not recreate or adjust the earlier
source-pruning decisions.

Profile uncertainties are already present in the effective diagonal variance
through the squared contribution-weighted profile uncertainty terms. It would be
incorrect to characterize this ordinary comparator as simply ignoring all profile
uncertainty. Its omissions concern uncertainty in the plug-in weights, the selected
source/profile system, source pruning, dependence, and model/systematic errors.

The absence of residual-chi-square scaling follows the stated absolute supplied-
variance convention. This is internally consistent, but does not establish that
those supplied uncertainties are calibrated Gaussian error variances or that
the reported plug-in covariance is the actual conditional covariance after
selection. The plan correctly disclaims native EPA estimability equivalence.

## 3. Multiplicity and the candidate-set interpretation

For p retained sources there are `m=p(p-1)/2` unordered pairwise contrasts. The
two-sided Bonferroni critical value `Phi^-1(1-alpha/(2m))` is correct for the
declared within-fit family. No independence of the pairwise contrasts is required
for the ordinary union-bound argument under a valid marginal model.

This does not provide familywise control across all 35 samples, all three alpha
panels, profile choices, or the data-dependent source selection. The code and
report should retain the specific phrase **within-fit source pairs**. Alpha 0.05
is the descriptive primary panel of this post-hoc comparator, not a new validated
coverage level for the field study.

Eliminating a candidate when another source has a strictly positive lower
contrast is logically coherent. A sole remaining candidate may also rely on a
chain of significant pairwise relations; it need not have a directly significant
contrast with every other source. Such a chain is valid if all its component
relations hold simultaneously. The resulting singleton must not be described as
passing an independently tested direct leader-versus-every-rival margin unless
that stronger condition is separately checked.

Ties are not arbitrarily broken. The field audit found no zero contrast variances;
the zero-SE and one-source behavior is relevant only to synthetic or future cases
here. Neither a conditional singleton nor a non-singleton determines the true
environmental leading source.

## 4. Independent QR replay and aggregate reconciliation

An independently written review calculation replayed all 35 frozen central fits
using reduced QR solves instead of the producer's `lstsq` path. It formed the
covariance as `R^-1 R^-T` from the final whitened design, rather than using the
producer's SVD covariance routine. Critical values were computed using the
normal survival-quantile function and candidates reconstructed from all pairwise
contrasts. The comparator's numerical functions were not imported for this check.

| Independent comparison | Maximum discrepancy |
|---|---:|
| Central contributions, absolute | 6.58e-14 |
| Final-solve variances, relative | 1.87e-14 |
| Covariance, relative Frobenius norm | 8.84e-15 |
| Normal critical value, absolute | 3.02e-14 |
| Candidate-set disagreements | 0 |

All **54 cross-tabulation panels** were independently reconstructed and matched.
All 35 covariances were valid under the declared numerical checks; none was
unresolved. The independently verified descriptive alpha-0.05 counts are:

| Scope | Samples | Conditional singleton | Joint top witness | Both |
|---|---:|---:|---:|---:|
| All samples, any basic-qualified joint witness | 35 | 9 | 29 | 4 |
| All samples, completely OAT-stable basic joint witness | 35 | 9 | 2 | 1 |
| Central-strict samples, strict paired joint witness | 4 | 2 | 1 | 0 |

Thus 25 of the 29 basic-witness samples are already non-singletons under this
ordinary conditional comparator. That is a substantive challenge to any claim
that a new decision-set construction newly discovers all such uncertainty.
Conversely, four conditional central-model singletons also have an admitted
joint-profile witness. This shows a difference in uncertainty scope; it is **not**
a 4/9 false-positive rate, a coverage failure rate, or proof that the proposed
method is more accurate. The joint alternatives are not observed ground truth.

## 5. Nonblocking reporting caveat and matched comparisons

`cross_tab` currently defines `no_conditional_singleton_and_joint_witness` as all
witnesses minus singleton witnesses. If a future dataset has unresolved covariance,
that residual count will include unresolved cases as well as valid non-singleton
sets. For reuse, split it into **valid non-singleton witnesses** and **covariance-
unresolved witnesses** before interpreting it as an ordinary uncertainty warning.
This does not change the current results because all 35 covariances are valid.
No change to the frozen artifact is requested solely for this latent reporting
caveat.

Comparisons with the new interval analysis should also align source universes.
The ordinary comparator conditions on the central-retained universe; the interval
full-seven-source panel is intentionally different. The retained-universe bridge
is the appropriate matched source-scope comparison, but alpha and k still are
not interchangeable confidence calibrations. Gaussian plug-in contrast intervals
and deterministic independent-error boxes make different assumptions and are
not generally nested.

**Disposition:** KEEP this comparator and its negative challenge to novelty;
KEEP the narrowly descriptive overlap counts; HOLD coverage, superiority,
environmental truth, and new-method claims. Do not retrofit thresholds or remove
ordinary-comparator warnings because they weaken the proposed story.
