# Mathematical and falsification audit: joint profile-choice decisions

Date: 26 September 2026. Status: independent candidate-method audit, **not** a
manuscript revision or a validation of environmental truth. The EPA native
reconstruction and frozen EVLS implementation were read; neither was modified.

## Bottom line

**KEEP** a narrowly scoped, uncertainty-honest finite-ensemble decision audit.
One-at-a-time (OAT) source-profile checks do not logically establish joint-choice
stability, even for positive normalized profiles, full-rank designs, nonnegative
contributions, exact reconstruction and exact mass closure. A fully transparent
two-source counterexample below proves this without relying on numerical errors.

**HOLD** claims of a new general theory, a revolutionary algorithm, formal
floating-point/error certification, statistical confidence or environmental
accuracy. Enumerating a finite model set and retaining only unanimous decisions
is a standard idea. The possible contribution is the CMB-specific scientific
finding, an auditable failure-aware implementation, and evidence that it changes
which practical source-priority decisions are supportable.

**REMOVE** any inference that a numerically nonconverged choice is scientifically
inadmissible, or that a joint reversal by itself establishes nonlinear interaction.

## 1. Exact, positive CMB counterexample

This is deliberately constructed mathematical data. It is **not** an EPA sample,
an experimental result or external field validation. Let a normalized profile be

\[
 p(t)=(3/10+t/20,\;3/10-t/25,\;2/5-t/100)^T.
\]

All the profiles used below have strictly positive entries summing to one. Two
source families have options

\[
 a\in\{-2,-14/5\},\qquad b\in\{3,5/2\}.
\]

The first option in each family is central. The observed receptor is
\(y=10p(0)=(3,3,4)^T\), with ambient total mass 10. For every choice,
\(F=[p(a)\;p(b)]\) has column rank two and positive residual degrees of freedom.
The unique exact contribution vector is

\[
 s_A=\frac{10b}{b-a},\qquad s_B=\frac{-10a}{b-a}.
\]

| Choice | Source A | Source B | Leading source |
|---|---:|---:|---|
| Central | 6 | 4 | A |
| A profile only changed | 150/29 | 140/29 | A |
| B profile only changed | 50/9 | 40/9 | A |
| Both profiles changed | 250/53 | 280/53 | B |

Every row has zero residual, positive contributions and total contribution 10.
With any common positive receptor uncertainty and zero profile uncertainty, the
reconstructed EPA-style diagnostics are \(R^2=1\), reduced \(\chi^2=0\), and
100% mass closure. Both OAT checks preserve the complete two-source ordering;
the joint choice reverses it. The four unweighted matrix 2-norm condition numbers
are approximately 3.601, 3.997, 3.102 and 3.401: this is not a near-singular
floating-point construction.

It is also not restricted to an exact-fit point. For each fixed design, let
\(L=(F^TF)^{-1}F^T\) and \(v=L_{A,:}-L_{B,:}\). The sign of its contribution
contrast is unchanged whenever

\[
 \|\delta y\|_\infty < |vy|/\|v\|_1.
\]

Exact rational algebra gives the minimum of this sufficient radius over all four
designs as \(1427/33758\approx0.04227146\). This is a deterministic perturbation
bound for fixed equal-weight linear least squares, **not** a confidence interval
or an EVLS nonlinear-solver error bound. All 32 combinations of the four designs
and receptor perturbation corners \(\delta y_i=\pm0.01\) additionally retain
positive contributions, the same respective leading-source decisions and the
three declared fit gates with receptor uncertainty 0.05. These cases include
nonzero residuals; reduced chi-square never exceeds 0.12.

An important negative result: the top-source condition is simply \(a+b>0\).
The parameter-coordinate boundary is additive. Therefore this example proves
**joint-choice reversal missed by OAT**, not a nonlinear statistical interaction.
That distinction should also be maintained when interpreting the EPA results.

## 2. Failure-aware minimum-substitution certificate

Fix a sample, its retained source-category slots, all admissible profile options,
the fitting procedure, fit gates, decision definition and numerical policy
**before** inspecting outcomes. Let the complete finite universe be
\(H=\prod_j P_j\), with central choice \(h_0\). Define

\[
 d(h,h_0)=\sum_j\mathbf{1}\{h_j\ne h_{0j}\}.
\]

The central fit must be admissible and have a unique leading source \(c\).
Otherwise a preservation radius anchored at that central decision is undefined.
For unique-winner preservation, an admissible tie counts as failure to preserve
the decision; a strictly larger competitor is the narrower *strict reversal*
endpoint. Keep these two endpoints distinct.

For each enumerated choice use one of four states:

- **Stable:** admissible and the declared decision is preserved.
- **Bad:** admissible and the declared decision is not preserved.
- **Excluded:** inadmissibility is established by the frozen scientific rule.
- **Unknown:** convergence, admissibility, or the relevant decision is unresolved.

Let \(b\) be the smallest distance of a known bad witness and \(u\) the smallest
distance of an unknown choice; take the minimum of an empty set as infinity. If
\(r_*\) is the actual smallest bad distance after all unknowns are resolved, then

\[
 \boxed{\min(b,u)\le r_*\le b.}
\]

**Proof.** Every choice closer than \(\min(b,u)\) is already stable or excluded,
so none can be bad. A known bad witness at distance \(b\), if present, establishes
the upper bound independently of unresolved choices. No distributional
assumption or asymptotic approximation is involved.

Thus decisions are certified through every integer distance
\(k<\min(b,u)\), conditional on this finite universe and decision procedure.
When \(b\le u\), a finite witness proves the exact minimum substitution count
\(r_*=b\). If \(u<b\), only an interval is justified. If both are infinite,
every enumerated choice has been resolved without an admissible counterexample;
the result is stability over **this finite declared set only**.

Dropping unknown fits wrongly replaces \(u\) by infinity and can manufacture a
stability certificate. Missing combinations must likewise be treated as unknown,
not silently omitted. An ensemble with no admissible member is not evidence of
stability; the required central anchor prevents that vacuous conclusion here.

The executable test checks all \(4^3\) labelings of the three noncentral choices
in a binary two-family universe, and every stable/bad/excluded completion of its
unknown states. Every completed minimum obeys the interval above.

## 3. What “certificate” can and cannot mean

There are at least four distinct layers; none implies the next without evidence.

1. **Enumeration coverage:** all declared combinations were visited, identities
   and category mappings are correct, and unresolved results are counted.
2. **Computed-decision robustness:** the declared numerical procedure produces
   the same decision on the resolved, qualified choices.
3. **Numerical solution certification:** validated error bounds ensure that the
   computed decisions equal decisions of well-defined exact solutions.
4. **Statistical or environmental validity:** the uncertainty set contains the
   real process with justified probability, or same-sample independent reference
   evidence establishes that the decision is accurate.

The frozen 1% EVLS iterate-change stopping criterion is **not** an upper bound on
coefficient error. Small successive updates alone do not bound distance to a
fixed point; nor do they prove uniqueness. Therefore the EPA application currently
supports layers 1–2, not automatically layer 3. Tighter tolerances, larger budgets,
alternative initializations, independently implemented solvers and margin checks
are valuable falsification tests, but agreement is not a formal interval proof.

If validated coefficient intervals were available, a strict pairwise relation
could be certified only when its lower contrast bound is positive for every
admissible choice. Diagnostics near their acceptance boundaries would also need
interval classification. Without those intervals, use the explicit description
“finite-ensemble computed-decision audit” and disclose the termination rule.

Full-rank reconstruction is conditional on a profile choice, not identification
of that choice. The counterexample has the same receptor data under two plausible
profile choices with opposite true leading sources. No rule using only those
data and the identical fit diagnostics can be uniformly correct in both worlds.
Abstention or an extra identifying assumption/reference is necessary for such a
guarantee. This is a standard identification argument, not a new theorem claim.

## 4. CMB-specific design hazards

- **Active-set dependence.** The prior audit prunes negative central sources and
  freezes the retained slots for alternatives. The primary joint-choice audit
  should use exactly those retained slots per sample. A profile choice for an
  absent category creates no new model and must not inflate ensemble size or
  substitution distance. Repruning every alternative mixes profile choice with
  source-presence/controller sensitivity and belongs in a separate analysis.
- **Signed versus physical allocations.** The historical alternative EVLS fits
  are unconstrained. Diagnostic-qualified signed vectors are not automatically
  physically nonnegative source allocations. Report negative-contribution
  attrition and a prospectively specified nonnegative subset separately. Do not
  clip negatives or choose a tolerance to preserve an attractive finding.
- **Common categories.** Map alternate profile identifiers back to fixed source
  categories before comparing ranks. A changed mnemonic is not a source-rank
  change. Alternative universes must not be treated as a pure profile-choice test.
- **Finite-set selection.** More alternatives can only weaken a universal
  consensus statement, if earlier accepted choices retain their status. A
  stability claim is vulnerable to omitted plausible profiles; the declared
  historically grounded universe is a scope statement, not proof of completeness.
- **Diagnostic filtering.** Fit gates condition the scientific question. A
  stricter gate can remove witnesses and increase apparent consensus without
  supplying a closer-to-truth allocation. Report unfiltered/converged, basic,
  mass-closure and nonnegative subsets transparently; do not switch primary gates
  after observing the outcome.
- **Distance interpretation.** Hamming distance counts changed families, not the
  magnitude, prior plausibility or cost of a chemical-profile perturbation. A
  distance-two witness is not “twice as unlikely” as distance one.

## 5. Novelty and decisive next tests

Consensus partial orders over good-fitting model sets, with abstention where
rankings disagree, already have direct mathematical precedent in
[Laberge et al., JMLR 24(364), 2023](https://www.jmlr.org/papers/v24/23-0149.html).
Their feature-attribution setting is different from chemical source apportionment,
but prevents claiming the generic consensus/partial-order construction as new.
The minimum-distance bound above is elementary finite-set bookkeeping; it should
be presented as a transparent proposition, not the main theoretical novelty.

A potentially worthwhile CMB-specific result needs the following decisive tests:

1. Enumerate the frozen EPA joint universe and ask whether any sample is fully
   OAT-resolved and stable yet has a joint, admissible, nonnegative reversal.
   Count separately cases with an unresolved OAT fit: these do not establish that
   OAT certified stability and then failed.
2. Refit each decisive witness independently, with stricter termination and a
   larger iteration budget as a **labelled sensitivity run**, not a retroactive
   replacement of the frozen primary run. Check witness contributions, source
   mapping, margins, residuals, mass closure and active-set identity.
3. If no such case survives the physical/solver checks, reject the proposed
   EPA headline. Retain the illustrative counterexample and negative empirical
   finding, but do not call them a major practical upgrade.
4. Assess whether abstention/partial ranking preserves useful information that
   “all source rankings are unstable” loses. Report resolved and unresolved
   coverage, not just a visually interesting partial-order diagram.
5. A genuinely stronger second-stage contribution would design an additional
   measurement that separates opposing-source decisions, and test it on an
   independently held-out measured species or same-sample reference. Prediction
   intervals for every competing model must be fixed using valid profile and
   uncertainty information. Choosing the species after examining held-out truth,
   or claiming accuracy from disagreement alone, would invalidate that test.

No existing external-truth gate is relaxed by the mathematics. Fairbanks remains
separate from this EPA profile-choice experiment, and the JRC access/permission
restrictions remain in force.

## 6. Executable verification

Created only the present report and
`scripts/test_decision_certificate_counterexamples.py`. The script reads no native
EPA inputs and writes no outputs. It uses exact fractions for the construction,
left inverse, perturbation margins and finite-label tests, plus a cross-check
against the frozen EVLS function with constant weights.

```text
python scripts/test_decision_certificate_counterexamples.py -v
```

Result: **17 tests passed** on the local Python 3.12.14 / NumPy 2.3.5 runtime.
The numerical EPA enumeration is intentionally owned by the separate empirical
audit and is not duplicated here.
