# Candidate interval-feasibility audit: proof and frozen test proposal

Prepared: 2026-09-26, 19:47:41 UTC. Status: **PROTOCOL ONLY — ROOT REVIEW REQUIRED BEFORE FIELD LP EXECUTION**.

No new field LP, uncertainty sweep, data-dependent threshold selection, or manuscript edit has been performed for this proposal. Existing native-input and joint-profile outcomes were already known; any subsequent analysis is an explicitly exploratory extension, not blinded validation or retrospective preregistration.

## 1. What this can add, and what it cannot

The existing joint-profile audit compares particular effective-variance least-squares (EVLS) solutions. The proposed audit instead asks which **nonnegative source-contribution vectors are compatible with a declared bounded-error model**, and which pairwise source decisions hold throughout that compatibility set.

This addresses a missing *set-valued treatment* of within-profile uncertainty. It does not imply that CMB/EVLS ignores profile uncertainties: the prior solver already includes them in its effective variances. The proposed object is different from an EVLS optimizer, its standard error, a likelihood region, or a confidence set. It must be reported separately.

The underlying mathematics is established interval linear algebra / set-membership estimation, not a new theorem. Oettli's 1965 paper is an early primary source for solution sets and linear-programming treatment of inaccurate coefficients. [Oettli, DOI 10.1137/0702009](https://epubs.siam.org/doi/10.1137/0702009). Zhen and den Hertog explicitly discuss orthant-wise polyhedral sets and develop column-wise convex uncertainty representations. [Zhen and den Hertog, 2017, DOI 10.1007/s10287-017-0290-9](https://link.springer.com/article/10.1007/s10287-017-0290-9).

Possible scientific value is an auditable application to this source-attribution decision problem, with a declared uncertainty model, exact scope, evidence of failure as well as success, and reproducible decision witnesses. Novelty in CMB applications remains a separate literature question.

## 2. Definitions and exact projection for independent intervals

For one sample, let there be `m` chemical measurements and `p` source families. Define:

- `s_j >= 0`: contribution of source `j`, in the receptor mass-concentration units.
- `F_ij`: abundance of species `i` in source `j`, using the released profile units.
- `c_i`: receptor concentration of species `i`.
- `uF_ij >= 0` and `uc_i > 0`: released uncertainty fields, not newly estimated errors.
- `k`: a prespecified dimensionless interval multiplier.
- `L_ij = max(0, f_ij - k uF_ij)` and `U_ij = f_ij + k uF_ij`.
- `l_i = c_i - k uc_i` and `u_i = c_i + k uc_i`.

Here lowercase `f` and `c` are the released nominal inputs; capital `F` and a latent vector `z` denote compatible values. Missing/sentinel inputs must be rejected before constructing intervals; `max(0, ...)` is not permission to replace a missing value by zero.

The **united compatibility set** is

```text
S(k) = { s >= 0 : there exist F and z with L <= F <= U,
                              l <= z <= u, and F s = z }.
```

All inequalities on vectors/matrices are componentwise. Entrywise independent intervals mean that every combination inside the matrix box is allowed; this is a modeling assumption, not a consequence of marginal uncertainties.

For nonnegative `s`, the exact projection is

```text
S(k) = { s >= 0 : L s <= u and U s >= l }.
```

Thus membership, linear contribution bounds, and pairwise decision bounds can be solved by ordinary linear programs under this box model.

### Direct proof, including degenerate cases

Necessity follows from `L s <= F s <= U s` when `s >= 0`: a compatible `z` must lie both between `L s` and `U s` and between `l` and `u`.

For sufficiency, fix a vector satisfying the projected inequalities. For each row `i`, write `a_i = (L s)_i` and `b_i = (U s)_i`. The two closed intervals `[a_i,b_i]` and `[l_i,u_i]` intersect. Choose any `z_i` in their intersection. If `b_i > a_i`, set

```text
t_i = (z_i - a_i)/(b_i - a_i),
F_ij = L_ij + t_i (U_ij - L_ij) for every j.
```

Then `0 <= t_i <= 1`, all entries satisfy their bounds, and the row product equals `z_i`. If `b_i = a_i`, choose `F_i = L_i`; then necessarily `z_i = a_i`. Rows can be constructed independently, which establishes the result. A zero contribution causes no division by that contribution and is included in the proof.

This is a nonnegative-orthant specialization of the classical Oettli–Prager compatibility characterization. The original 1964 primary-paper record describes coefficient/right-hand-side backward-error compatibility; its DOI link was not retrievable in this session, so no unverified DOI is supplied. [Oettli and Prager, IBM primary publication record](https://research.ibm.com/publications/compatibility-of-approximate-solution-of-linear-equations-with-given-error-bounds-for-coefficients-and-right-hand-sides).

### Quantifier warning

The set uses **there exists** a compatible profile matrix and receptor vector. It does not require the same `s` to fit **every** uncertain matrix. Those are different uncertainty models. A decision certificate subsequently has the form “for every `s` in this existential compatibility set, source A exceeds source B.” Do not replace the first existential quantifier by a universal one or call the two notions equivalent.

## 3. Decisions, alternatives, and nonempty-set safeguards

For a nonempty compatible set, define

```text
lower_ab = min (s_a - s_b) over S(k),
upper_ab = max (s_a - s_b) over S(k).
```

A rigorously positive lower bound certifies `a > b` throughout the specified set. A feasible point with `s_b > s_a` supplies a reversal witness. A zero/touching bound does not establish a strict order. Infeasibility does not establish any order: the correct status is **INCOMPATIBLE ASSUMPTIONS/INTERVALS**, not a vacuous winner.

A source `a` is a possible co-leader exactly when the additional inequalities `s_a >= s_b` for every `b` leave a nonempty set. A guaranteed unique leader requires positive lower margins against every competitor. Feasible ties are retained. Unbounded contribution intervals are reported as unbounded, not capped for presentation.

For a finite collection of historical profile systems `q`, the decision set is a **union** of the corresponding compatible sets `S_q(k)`. Evaluate every system, including systems for which the previous EVLS solver did not converge. EVLS nonconvergence does not imply LP infeasibility, and this LP is not a repaired EVLS run. Bounds over the union are the minimum/maximum of the system-specific bounds. A failed or numerically unresolved LP blocks a complete-union guarantee but does not erase an independently verified reversal witness.

Do not merge the systems by taking the entrywise envelope of all alternative profiles and claim exact equivalence: that box admits mixtures of entries that may correspond to no allowed historical profile. It is, at best, a separately labeled outer relaxation.

## 4. Dependence, composition, and physical caveats

### Why independent boxes can be too permissive

Species abundances may be correlated by shared normalization, chemistry, detection-limit treatment, analytical recovery, or a common source sample. Receptor errors can also be correlated. Entrywise boxes discard these dependencies and can admit chemically impossible combinations. A reversal witness in such a box is only a box-model witness; it need not be a physically attainable source profile. Conversely, a strict decision valid on a documented **outer** box is also valid on a physically valid nonempty subset, provided that subset is genuinely contained in the box. The containment and nonemptiness assumptions must be justified.

The EPA manual states that source abundances ordinarily use fractions of source mass rather than percentages, and warns that some zero-abundance uncertainty fields represent quantification limits. Therefore `k=1,2,3` cannot automatically be read as probabilistic coverage, and unit/uncertainty semantics must be checked. [EPA-CMB8.2 User's Manual, sections 4.2.3 and 6.1.1](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1009R4F.TXT).

No selected-column-sum-equals-one constraint is justified solely by the term “mass fraction.” The selected 20 analytical species need not form a complete, mutually exclusive composition. The existing selection contains multiple analytical species labels, including `KPAC` and `KPXC`; their physical relation must be documented before any compositional sum constraint. No renormalization of selected columns is allowed. If an upper interval bound exceeds one, record it explicitly; do not silently truncate it. Until each quantity is verified to be a true fraction, the general released-unit formulation is primary. A physical `F_ij <= 1` restriction would be a separately specified model, not a reporting fix.

### Metadata-supported correlated column constraints can still be linear

Suppose source column `j` is known to belong to a **nonempty bounded** polytope

```text
P_j = { f_j : L_j <= f_j <= U_j, A_j f_j <= b_j }.
```

Introduce `y_ij = F_ij s_j` and retain the following linear constraints:

```text
s_j >= 0,
L_ij s_j <= y_ij <= U_ij s_j,
A_j y_j <= b_j s_j,
l_i <= sum_j y_ij <= u_i.
```

This lifted formulation is exact for independent source columns. For `s_j > 0`, recover `F_j = y_j/s_j`. For `s_j = 0`, the finite interval bounds force `y_j = 0`, and a member of the nonempty `P_j` can be chosen. Equalities may be represented by paired inequalities. This provides a way to impose independently justified column-level chemistry or normalization without pretending all coefficients vary independently. It is an application of established convex/perspective representations, not a new method claim. No such constraints will be invented in the initial field experiment.

Cross-source constraints may not survive this simple lifting. More importantly, separately solving every sample permits the latent profile within its box to differ across samples. Requiring **one identical unknown profile matrix across all samples** reintroduces shared bilinear restrictions and is not equivalent to independent per-sample LPs. The initial scope is strictly per-sample compatibility.

### Total mass: three different assumptions, kept separate

1. **No added total-mass constraint:** primary bounded-chemistry model. It may be weak or unbounded; that result is retained.
2. **Mass upper bound:** only after confirming units, particle-size alignment, source disjointness, and an appropriate total-mass uncertainty field, impose `sum(s) <= M_upper`. An incomplete list of sources does not justify a positive lower bound on its sum.
3. **Historical 80–120% diagnostic band:** a separately labeled sensitivity `0.8 TMAC <= sum(s) <= 1.2 TMAC`. This is not exact physical conservation, and no equivalence to a mass confidence interval is implied.

An equality `sum(s)=TMAC` or normalized fitting-species columns will not be introduced. If total-mass uncertainty is unavailable or not interpretable, panel 2 remains HOLD rather than filled by an arbitrary percentage.

## 5. Frozen candidate experiment, pending root review

This section fixes the candidate choices before any new field LP is run. Root may accept, reject, or issue a visibly versioned amendment **before execution**. Outcome-based replacement of `k`, species, sources, feasibility tolerances, or comparison panels is prohibited.

### Inputs and scope

- Use the same four hash-verified EPA archives and all 35 FRESNO/FINE samples as the native reconstruction.
- Use the existing frozen 20 species and original uncertainty fields without rescaling or imputation.
- Primary source universe: all seven originally specified source slots, with **no fit-dependent source removal**. This prevents mean-solution pruning from silently removing a source whose interval-compatible contribution could be positive.
- Separate bridge sensitivity: each sample's inherited central-retained slots, exactly as recorded in `joint_profile_ledger.json`. This is for comparison with the existing joint audit; never pool its denominator with the full-seven-source panel.
- Source-system levels: central historical profile system first; complete historical Cartesian grid second. Full-seven grid has 120 systems per sample. The retained-slot bridge has the already enumerated 120/60 systems.
- Primary interval multipliers: **`k = 1, 2, 3`**, all reported. They are deterministic uncertainty-scale scenarios, not 68/95/99.7% regions.
- Profile-uncertainty contrast: (A) fix `F=f` and allow the receptor interval; (B) allow both receptor and within-profile intervals using the displayed definitions. Compare each A/B pair at identical `k`, source system, and source universe.
- No added mass constraint in the primary run. Report the historical 80–120% band separately. The physical mass-upper-bound panel is metadata-gated as above.
- No screening by prior `R2`, reduced chi-square, mass-fit success, or EVLS convergence. LP compatibility is the declared target, not a selected subset of successful fits.
- Do not use the root's held-out-species receptor means for model selection, uncertainty adjustment, or eligibility.

### Staged computation to keep the test bounded

Stage 1: synthetic tests and metadata audit only. Stage 2, if approved: all 35 samples, central system, all three `k` values, and both uncertainty treatments. Stage 3 requires an explicit root review of computational feasibility and metadata, then executes the already frozen full grid rather than selecting favorable samples or systems. The historical-mass and retained-universe sensitivities stay separately indexed.

A stopped stage produces a complete status table showing what was attempted, withheld, unresolved, or not run. No partial grid is called exhaustive. The first read of interval feasibility results must be timestamped, and the accepted plan/configuration hash saved before that read.

### Primary outputs

For every combination, store compatibility status; source lower/upper bounds; pairwise lower/upper margins; possible co-leaders; nonnegative reversal witnesses; unboundedness; and numerical-verification status. Aggregate denominators retain all 35 initial samples. Stratify by `k`, source universe, uncertainty treatment, system coverage, and mass model.

Report all source-system attrition, including infeasibility, numerical failure, and unbounded objectives. Report changes from the **same** fixed-profile receptor-uncertainty panel, not a different EVLS-selected comparison. Widening uncertainty sets is expected mathematically to weaken or preserve restrictions; that nesting alone is not an empirical discovery.

### Numerical reliability rules

- Candidate solver: SciPy HiGHS dual simplex, with explicit primal/dual feasibility tolerances `1e-9`; independent HiGHS IPM comparison for classified margin cases. Record package versions and all solver statuses.
- Model inputs are finite released decimals. Do not introduce hidden objective regularization, concentration caps, or feasibility relaxations.
- Any near-zero margin, inconsistent solver outcome, inadequate residual verification, or unavailable valid dual bound is **NUMERICALLY UNRESOLVED**, not a certified sign.
- A float64 solver's “optimal” flag is not an exact mathematical certificate. Store primal and dual solutions; independently recompute inequalities and duality checks.
- A rigorous bound can be obtained using rational verification or exact/outward-rounded dual bounds. For example, for `G s <= h`, `0 <= s <= B`, objective `q^T s`, and any exactly verified `lambda <= 0`, define `r=q-G^T lambda`. Then

```text
q^T s >= lambda^T h + sum_j min(0,r_j) B_j.
```

  The formula is valid only with independently valid finite `B_j`; arbitrary caps do not qualify. Such bounds can sometimes be obtained from a positive `L_ij` and `u_i`, because nonnegativity implies `s_j <= u_i/L_ij`, or from a justified mass upper bound. If a needed bound is absent, do not use this residual correction to assert a certificate.
- Similarly, a reversal point must be independently verified feasible. Floating-point tolerance acceptance is reported as numerical evidence, not relabeled exact feasibility. Exact-basis/rational repair or outward-rounded verification is required for a rigorous certificate.
- Any statistical-coverage statement requires additional validated simultaneous uncertainty modeling and is out of scope for this plan.

### Required pre-field falsification tests

1. Prove/test equality with the explicit lifted box formulation on deterministic synthetic cases, including zero-contribution sources and zero-width intervals.
2. For exactly generated nonnegative synthetic data with true inputs inside the declared box, retain the known true contribution vector.
3. Confirm that replacing `uF=0` nests its feasible set inside the joint-uncertainty set; increasing `k` cannot remove a verified feasible point.
4. Verify an empty system is labeled incompatible, never a winner; an unbounded system is not capped; a feasible tie is not broken.
5. Supply a synthetic example where marginal boxes permit a reversal but a known compositional/correlation constraint removes it, and explicitly distinguish box witnesses from physically valid witnesses.
6. Check that finite alternative-profile union bounds match explicit per-system enumeration and differ, when expected, from an entrywise profile-envelope relaxation.
7. Check that removing a source from a nominal optimum can alter interval bounds; report the retained-slot panel only as a conditional sensitivity.
8. Verify simple LP optima and dual certificates against analytically solved examples. Inject a small primal/dual residual error and confirm that it does not produce a rigorous certificate.

## 6. Stop/keep/hold rules

**KEEP** a reproducible, correctly qualified interval compatibility analysis, even if every leading-source decision becomes ambiguous or most boxes are incompatible. **KEEP** independently verified conditional positive-order bounds if they occur, but do not call the box a confidence region.

**HOLD** field execution until root accepts this protocol; physical-profile claims until dependence/normalization metadata is adequate; complete-union claims if any necessary system is unresolved; any superiority claim without an independent external endpoint.

**REMOVE** a proposed “new theorem” label for the interval projection; treating standard errors as certain bounds; deriving a probability from `k`; equating box compatibility with EVLS fit success; reusing mass screening as physical law; or silently choosing only cases with favorable certificates.

At this stage the defensible conclusion is **mathematically feasible and potentially useful, but established mathematics with material physical-modeling caveats; no new field result yet**.
