# Independent review of the interval-compatibility extension

Review status: **COMPLETE: PRE-FIELD REVIEW AND ALL 492 FINAL MODEL PROOF RECORDS
PASS INDEPENDENT VERIFICATION; ALL 840 INDEX RECORDS AND 24 PANELS RECONCILED**.
Date: 26 September 2026. Approved execution scope communicated by root: synthetic
stage and central-profile-system stage only. No full historical-system sweep or
new manuscript claim is approved by this review.

The complete `INTERVAL_FEASIBILITY_PROPOSAL.md` was read. This review owns no
implementation file and has not independently duplicated field LP computations.
Implementation findings and concrete verification cases will be appended after
the implementation agent supplies the code and tests.

## 1. Proposal-level mathematical findings

The nonnegative-orthant projection is correct **under the explicit independent
entrywise interval model**:

\[
 \{s\ge0:\exists F\in[L,U],\ z\in[l,u],\ Fs=z\}
 =\{s\ge0:Ls\le u,\ Us\ge l\}.
\]

Conditions include finite, ordered intervals and independently selectable matrix
rows/entries. For a fixed nonnegative contribution vector, each row's possible
product is the entire interval `[(Ls)_i,(Us)_i]`; intersecting it with the receptor
interval is necessary and sufficient. The proposed convex interpolation constructs
each compatible row without division by a source contribution, so zero sources
and zero-width product intervals are correctly covered.

This is an **existential compatibility set**, not the set of contributions that
fit every profile matrix. Source decisions may subsequently be universal over
that compatibility set. Both quantifiers must remain visible in the manuscript.

The correlated-column lifted formulation is also exact when each declared column
polytope is **nonempty and bounded**, source columns are independent, and only one
sample is represented. At positive contribution, dividing the lifted column by
the contribution recovers an admissible profile. At zero contribution, finite
interval bounds force the lifted column to zero, and nonemptiness supplies any
profile in that column's polytope. Cross-column chemistry or one common latent
profile across several samples does not generally have this simple independent
per-sample representation.

The correct set for several alternative historical profile systems is their
**union**. An entrywise envelope is an outer relaxation, not that union. Infeasible
systems contribute no point; unresolved systems cannot simply be excluded from a
universal union certificate.

## 2. Exact input and implication requirements

Construct interval coefficients using exact rational conversions of the released
decimal strings and rational `k`. Converting a floating-point calculation such
as `f - k*uF` back to a rational proves a statement about that rounded endpoint,
not necessarily the declared released-decimal model.

The nominal coefficients must be nonnegative for the proposed fixed-profile set
to be nested inside the nonnegative clipped joint-profile set. Reject missing,
sentinel or semantically invalid values before clipping. Check `L <= U` and
`l <= u` explicitly. Receptor lower bounds may be negative: nonnegative predicted
concentrations already impose the relevant restriction. A negative receptor
upper bound with nonnegative profiles gives an exact incompatibility, not a
negative source upper bound to insert into later calculations.

Valid source upper bounds may be obtained from a **nonnegative coefficient row**
`Ls <= u`: if `L_ij > 0`, nonnegativity implies `s_j <= u_i/L_ij`. An explicitly
declared mass upper constraint also supplies an upper bound. Do not infer a
coordinate bound merely because its coefficient is positive in an arbitrary
constraint containing other negative coefficients; their effects can cancel.

Adversarial example: `s_1 - s_2 <= 1`, `s >= 0` has no finite upper bound on
`s_1`. Assigning the cap `s_1 <= 1` from that row would produce false dual bounds.

## 3. Verified residual-corrected lower bounds

For the actual exact problem

\[
 Gs\le h,\quad s\ge0,\quad \min q^Ts,
\]

take any exact vector `lambda <= 0`, not necessarily an exactly feasible
floating-point dual solution, and define `r = q - G^T lambda`. If each source
having `r_j < 0` has an independently valid finite upper bound `B_j`, then

\[
 q^Ts\ge\lambda^Th+\sum_{j:r_j<0}r_jB_j.
\]

This follows by multiplying each primal inequality by its nonpositive multiplier
and using `s_j >= 0` on positive residuals and `s_j <= B_j` on negative residuals.
The arithmetic and all sign tests must be exact or outward-rounded. Converting a
candidate multiplier to an exact rational and setting positive components to
zero is safe if the residual is then recomputed exactly; the resulting bound may
simply be weaker.

If `r_j >= 0`, an infinite or absent `B_j` is harmless and contributes zero. If
`r_j < 0` and no valid finite bound exists, no finite corrected lower bound is
available from this candidate. Avoid arithmetic expressions like `0 * infinity`.
Never supply an arbitrary concentration cap solely to complete this formula.

A positive bound proves a pairwise strict order only after nonemptiness is
established. A nonpositive bound does **not** prove ambiguity or reversal: there
may be a gap between the bound and the optimum. A reversal requires an exactly
feasible point with negative contrast. An exact tie requires a feasible point
with zero contrast; tolerance-close numbers are not a verified tie.

## 4. Feasibility, incompatibility and unboundedness

A float solver success flag is a candidate, not a proof. An exact rational primal
point with `s >= 0` and `Gs <= h` proves compatibility. Active-basis rational
reconstruction is acceptable only after every original inequality, including
inactive rows and nonnegativity, has been checked exactly.

For `s >= 0, Gs <= h`, an exact Farkas certificate is a vector satisfying

\[
 y\ge0,\quad G^Ty\ge0,\quad h^Ty<0.
\]

The first two inequalities imply `y^T Gs >= 0`, while primal feasibility would
imply `y^T Gs <= y^T h < 0`, a contradiction. A phase-I LP can supply a candidate
multiplier, but exact verification of all three conditions is still required.
Without a verified certificate, an infeasible solver status remains unresolved.

For formal objective unboundedness, verify both an exact feasible point `s_0`
and a ray `d` with

\[
 d\ge0,\quad Gd\le0,\quad q^Td<0.
\]

Then `s_0 + t*d` is feasible for every `t >= 0` and the objective decreases
without bound. A normalized ray search such as `sum(d) <= 1` is a valid way to
find a candidate; the normalization is not a cap on source contributions.

Feasibility phase-I bounds must be checked against the phase-I constraints, not
silently borrowed from constraints whose violations the phase-I slack relaxes.
The implementation agent has chosen exact Farkas verification, which avoids
relying on such a shortcut.

## 5. Possible co-leaders and mandatory adversarial cases

Possible co-leadership of source `a` requires **one common feasible point** obeying
`s_a >= s_b` for every competitor. Separate pairwise possibilities are insufficient.
A guaranteed unique leader requires strict positive lower margins against every
competitor and a verified nonempty original set. An infeasible set has no
declared winner; universal statements over it must not be reported as scientific
certificates.

The following small exact examples were supplied to the implementation agent:

1. **Separate pairwise possibility is not possible co-leadership.** Let
   `a = 1`, `b + c = 3`, and `b,c >= 0`. There is a feasible point with `a >= b`
   and another with `a >= c`, but none with both. Source `a` is not a possible
   co-leader.
2. **Independent-box witness can be chemically inadmissible.** Let source A's
   profile be `(1,t)`, `0 <= t <= 1`, source B's profile be `(0,1)`, and the
   exact receptor be `(1,1.5)`. The box permits contributions A=1, B=0.5 at t=1,
   so A leads. If these toy species form a complete composition and the A column
   is constrained to sum to one, t=0 and B=1.5>A. Such a composition constraint
   is justified in this constructed example, not automatically for EPA species.
3. **Profile envelope is not alternative-system union.** With one source and
   alternative profiles `(1,0)` or `(0,1)`, receptor `(1,1)` is incompatible with
   either exact system. The entrywise envelope allows profile `(.5,.5)` and
   contribution 2. An envelope-only fit does not establish union feasibility.

Additional required guards are nonempty and empty sets, an exact tie, a genuine
unbounded ray, a near-zero false floating-point margin, an invalid candidate
primal, invalid Farkas signs, and a negative dual residual for an unbounded source.

Nesting should be checked for all comparable panels: increasing k, fixed-profile
to joint-profile uncertainty, and embedding a retained-source bridge point into
the full-seven-source model by inserting zeros. A verified point cannot disappear
under these relaxations. A narrower numerical bound is not itself a contradiction
if certification is incomplete; distinguish the mathematical optimum from a
possibly loose verified bound.

## 6. Scope and interpretation

The proposed set differs from an EVLS optimizer and its uncertainty estimate.
It is appropriate not to screen LP cases by EVLS convergence or diagnostics.
The fixed-versus-joint interval contrast must retain the same sample, source
system, uncertainty multiplier and mass assumptions.

Multipliers 1, 2 and 3 are deterministic scenarios, not automatically Gaussian
coverage or confidence levels. A physically valid source/profile system must
actually lie inside a claimed outer box for a box-based guarantee to transfer.
An independent-box reversal may be possible only because real dependence has
been discarded. Agreement of computational certificates does not establish the
environmental truth of any source ranking.

The proposal correctly identifies its interval/set-membership mathematics as
established. Scientific value must come from the verified CMB results, useful
decisions and well-controlled scope, not from claiming a new interval theorem.

## 7. Initial implementation review

The complete `scripts/audit_interval_decisions.py`, original 26-test
`tests/test_interval_decisions.py`, and frozen configuration were inspected.
Configuration SHA-256:
`9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a`.
The reviewer independently ran those **26 tests: all passed**.

No unsound exact feasibility, Farkas, recession, or residual-corrected dual proof
path was found in that version. Rational active-basis repair is followed by all-
inequality verification, so a failed or unsuitable basis cannot silently become
a proof. Rounded primal values that already satisfy every exact inequality are
valid witnesses, even when they are not exact optimal points; the reported dual
gap must therefore be retained.

Three actionable findings were sent before field interpretation:

1. **Protocol test coverage:** add an explicit lifted-versus-projected LP
   comparison, not only a constructive membership check. The agent added it.
2. **Pruning test coverage:** demonstrate that removal of a nominal-zero source
   can change interval bounds, not only that retained points embed by zero. The
   agent added it. These additions produce a 28-test gate.
3. **One-sided strict-order classification:** the initial `pair_classification`
   requires both signed objective runs to have finite verified bounds. This is
   unnecessarily strong. For `A >= 2`, `0 <= B <= 1`, the exact minimum of `A-B`
   is 1, so A strictly dominates B, although its maximum is unbounded. The initial
   code labels the pair unresolved and can miss a verified unique leader. This
   is a conservative under-ascertainment defect, not a false certificate. The
   requested repair is to use the verified relevant one-sided bound, retain the
   already established nonempty base set, and add an adversarial test. No input,
   threshold or scientific model change is required.

The implementation agent repaired the one-sided gating without altering input
models or thresholds, added a symmetric unbounded-opposite-objective test, and
preserved the pre-correction implementation/gate privately. The reviewer inspected
that repair and independently ran the final **29 tests: all passed**. Reviewed
script SHA-256:
`ecb4e8f01f4028eb0a43d85870b3f458b75fce91d8bad9bdddaa815c3597da93`.
Reviewed test-file SHA-256:
`777862955c40b41a147886e701914840ff8eae6a061cd96a510f9e4de5e25033`.

No blocking mathematical-certification defect remains from this pre-field review.
Proceeding with the root-approved **central-system Stage 2 only** is supported once
the matching Stage 1 metadata/test gate passes. This is not approval of a full
profile-grid Stage 3, a manuscript claim, or environmental validity. Stored field
proof objects were subsequently checked first for three distinct proof classes,
then exhaustively as documented below, without rerunning the field LP experiment.

## 8. Independent exact-vertex oracle

The following bounded synthetic audit enumerates all vertices of 12 rational
two-dimensional bounded polytopes without invoking an LP solver for its ground
truth. It checks each reported primal/dual bracket against exact extrema and
checks many arbitrary dual candidates. No field data or field LP is used.

The oracle correctly checks a **bracket**, not equality between a decimalized
feasible solver point and the true rational optimum. An initial stronger equality
assertion was rejected as an invalid audit expectation: an exact feasible witness
need not be an exact optimizer, and the implementation explicitly records its
verified gap.

```python
from fractions import Fraction as Q
from itertools import combinations, product
import sys
sys.path.insert(0, "scripts")
import audit_interval_decisions as audit

def exact_vertices(G, h):
    rows = [tuple(map(Q, row)) for row in G] + [(Q(-1), Q(0)), (Q(0), Q(-1))]
    rhs = list(map(Q, h)) + [Q(0), Q(0)]
    result = set()
    for i, j in combinations(range(len(rows)), 2):
        a, b = rows[i]
        c, d = rows[j]
        determinant = a*d-b*c
        if determinant == 0:
            continue
        x = ((rhs[i]*d-b*rhs[j])/determinant,
             (a*rhs[j]-rhs[i]*c)/determinant)
        if all(row[0]*x[0]+row[1]*x[1] <= bound for row, bound in zip(rows, rhs)):
            result.add(x)
    return result

counts = {"models": 0, "exact_feasible": 0, "exact_infeasible": 0,
          "objectives": 0, "verified_dual_trials": 0, "unresolved_objectives": 0}
objectives = [(Q(1), Q(0)), (Q(-1), Q(0)), (Q(0), Q(1)),
              (Q(0), Q(-1)), (Q(1), Q(-1)), (Q(-1), Q(1))]
for t in range(12):
    G = [[1, 0], [0, 1], [-1, -1], [1, 2]]
    h = [1, 1, -Q(t, 5), Q(t % 5 + 1, 3)]
    model = audit.make_model(G, h, bounds=[1, 1])
    vertices = exact_vertices(G, h)
    feasible = audit.feasibility(model)
    counts["models"] += 1
    if not vertices:
        assert feasible["status"] == "EXACT_INFEASIBLE"
        y = feasible["farkas"]["y"]
        assert all(v >= 0 for v in y)
        assert all(sum(y[i]*Q(G[i][j]) for i in range(len(G))) >= 0 for j in range(2))
        assert sum(y[i]*Q(h[i]) for i in range(len(G))) < 0
        counts["exact_infeasible"] += 1
        continue
    assert feasible["status"] == "EXACT_FEASIBLE"
    counts["exact_feasible"] += 1
    for q in objectives:
        truth = min(sum(q[j]*x[j] for j in range(2)) for x in vertices)
        result = audit.objective_bound(model, list(q), feasible["primal"]["point"])
        if "verified_lower_bound" in result:
            assert result["verified_lower_bound"] <= truth
        if "feasible_objective" in result:
            assert truth <= result["feasible_objective"]
        if result["status"] != "VERIFIED_BOUND_AND_WITNESS":
            assert result["status"] == "NUMERICALLY_UNRESOLVED"
            counts["unresolved_objectives"] += 1
        for multipliers in product([0, -.125, -.999999999999], repeat=len(G)):
            bound = audit.lower_certificate(model, list(q), multipliers)
            assert bound["verified"] and bound["lower_bound"] <= truth
            counts["verified_dual_trials"] += 1
        counts["objectives"] += 1
near = audit.make_model([[1], [-1]], [1, -Q("1.000000000001")], bounds=[1])
assert audit.feasibility(near)["status"] != "EXACT_FEASIBLE"
counts["near_infeasibility_not_false_certified"] = True
print(counts)
```

Execution result: **PASS**. Twelve exact polytopes: **5 feasible, 7 infeasible**;
**30 objective brackets**, **2,430 arbitrary dual-candidate bounds**, and **zero
unresolved objective checks**. The `1e-12` contradictory near-feasibility case was
not falsely certified feasible. Exact vertex enumeration supplied the ground
truth independently of the implementation's LP solver and rational repair.

## 9. Independent replay of all final field proof objects

Result: **PASS**, completed at 2026-09-26 20:39:20 UTC in **47.875 seconds**.
The final index SHA-256 is
`381d20db9a35e1e8a725b535b588a60291def382a6f3196a10ef4a4302b66d40`.
All **492 unique models** and **840 labelled panel records** were checked. The
initial estimate of 480 unique models was not used as an acceptance condition;
the actual full-versus-retained source universes were reconstructed from the
identity-checked native inputs and frozen bridge ledger.

The separate verifier
`scripts/verify_interval_certificate_records.py` imports only Python standard-
library modules. It does **not** import the interval producer, the native audit,
NumPy, SciPy, or any LP solver. It independently parses the native tables and
source/species selectors, reconstructs every model from the released decimal
strings, and re-derives every source upper bound. It uses rational arithmetic
throughout its mathematical checks; its guards are not Python `assert` statements
and therefore remain active under optimized execution.

Four original archive hashes, all 39 archive-member identities, the frozen bridge
ledger, the reviewed producer/test code, configuration, final case hashes, exact
model hashes, sample identities, source mappings, cache reuse, and the complete
35-by-2-by-3-by-2-by-2 panel index were checked. Public summaries were recomputed
from independently verified case records, not accepted on the producer's status
flags alone.

| Independently checked item | Count |
|---|---:|
| Exact primal witnesses | 10,113 |
| Residual-corrected exact dual bounds | 9,133 |
| Exact Farkas certificates | 985 |
| Exact recession certificates, including feasible base points | 281 |
| Pairwise decisions | 3,603 |
| Joint possible-co-leader decisions | 1,227 |
| Reconciled public panels, each retaining all 35 samples | 24 |
| Unbounded claims under the historical mass band | 0 |

These counts refer to the **unique model proof objects**, not independent samples
or independently collected datasets. Cached models remain correctly represented
in their separate labelled panel denominators. A Farkas certificate for a
co-leader-constrained problem is also included in the Farkas count; it must not
be mistaken for incompatibility of the unconstrained chemistry model.

The independent verifier has **24 passing adversarial tests** covering invalid
primal points, inactive constraints, dual sign/residual/gap corruption, fake cap
provenance, missing bounds, invalid Farkas signs, invalid rays/base points,
historical-mass unbounded claims, joint co-leader restrictions, one-sided order
certificates and malformed rationals. All acceptance guards remain enabled under
`python -O` by construction.

Verifier SHA-256:
`53d1682413236b394fc24adae1d2dea75c2a621799947111e9a835a5afea1fed`.
Machine-readable aggregate verification:
`outputs/decision_research_20260926/interval_certificate_verification.json`.

```text
python -m unittest discover -s tests -p test_interval_certificate_records.py -v
python scripts/verify_interval_certificate_records.py --max-seconds 1800
```

No LP was rerun, no source profile was changed, and no manuscript was edited by
this validation. The PASS establishes exact consistency with the declared
deterministic interval problems and their recorded proof objects. It does **not**
establish probability coverage, physical attainability of every independent-box
member, shared-profile validity across samples, environmental accuracy, or
methodological novelty. All such limits in the proposal remain in force.

## 9. Independent post-hoc finite-ray witness replay

Date: 26 September 2026. Status: **PASS**, with no new LP or fit. This is an
additive review of the separate post-hoc ray audit, not a replacement of the
frozen Stage2 classifications.

Reviewed identities:

- Ray producer: `207f7a2f5529d67bbf176b9d43bf3b00c1090465d6e0be9e7f9b55c79f3f80c4`.
- Private ray ledger: `d57b3dade0ff1471fb05af4be087084983057e8618d11b7ed0ee210e14c8400f`.
- Public ray results: `d8fcc8aa82e810c62bbc502d3ecdac2a131896fd209b49db63e70edd22031db5`.
- Original complete index: `381d20db9a35e1e8a725b535b588a60291def382a6f3196a10ef4a4302b66d40`.
- Frozen Stage2 results: `14751cf3683999c4fab06e652487c3f3f4fcf69867177e4723cb1d145da4fbda`.
- Frozen geometry results: `62e5ca81e947901cff0ed1476b16c871cfa8faa5428f0c550b2f037d0dc5227c`.

The reviewer ran all **18 ray-construction unit tests: PASS** and performed an
independent **33.453-second** exact rational replay. The latter imported only the
previously reviewed independent input/proof validator, not either producer.

All **492 original models** were reconstructed again from original-decimal
native archives and selectors, and checked against saved hashes. The exact set
of eligible gap-labelled pairs containing an unbounded proof was reconstructed,
so omissions and extra claimed completions were checked as well as the records
that happened to be present.

Verified quantities:

- 41 models with attempted completion.
- 229 eligible pair attempts and **229 exact finite-ray constructions**.
- **2,503 distinct feasible model/point pairs**, cached only after exact checking.
- **11,897 witness records**, including exact source-record provenance.
- **10,329 cross-record mass-band point reuses**, each checked in its source model
  and again in the unchanged no-mass target model.
- Every stored negative/positive/tie witness selection, contrast, ray step, and
  derived status.
- All **24 labelled panel aggregates** and **12 mass/no-mass comparison groups**.

For each saved recession proof, the replay checked nonnegative feasible base
point x, nonnegative ray d, Gd <= 0, and q.d < 0. It independently calculated
`t=max(0,(q.x+1)/(-q.d))`, checked x+t*d against every original inequality, and
checked q.(x+t*d) <= -1. The target -1 is a convenient finite construction, not
a scientific threshold or an uncertainty adjustment. Exact paired mass-band
constraints were confirmed to be the original no-mass constraints plus two
extra inequalities before any source-point reuse.

All **164 both-orderings completions** are supported. The other **65** attempts
remain without an opposite-sign witness in the stored proofs; that does not
prove an order or impossibility of the opposite order.

Crucially, among previously gap-labelled no-mass pairs that acquired a verified
order under the mass band, completion supports only **1 of 60** primary-universe
cases and **1 of 57** retained-bridge cases. The remaining **59 and 56 gaps** are
unchanged. These are labelled conditional pair counts, not independent samples,
new measurements, or increased confidence. The audit must not relabel every
mass-only order as demonstrated no-mass ambiguity.

No source case, original classification, input, producer, geometry result, or
manuscript was edited. This addendum establishes exact proof-record consistency
with the declared models, not physical attainability or environmental truth.

## 10. Faithful Stage3 union replay and operational-correction review

Date: 26 September 2026. Status: **PASS for the frozen Stage3 conclusions**.
The original outcome remains **34 unions without a guaranteed unique leader,
and one fixed-margin HOLD**. No frozen classification was changed.

The new independent standard-library validator is
`scripts/verify_interval_union_records.py`, with **19 passing synthetic
adversarial/logic tests** in `tests/test_interval_union_records.py`.
It imports only the previously reviewed independent Stage2 validator for exact
input parsing and rational proof primitives, never either producer or SciPy.
The Stage2 validator file remains byte-preserved. Machine-readable verification,
including current verifier/dependency hashes and the individual HOLD proof-gap
references, is in
`outputs/decision_research_20260926/interval_union_certificate_verification.json`.

Frozen Stage3 identities:

- Revised configuration: `33f10f141aad7d8dc5f72bf7cfd06e89c7a2f61c839f1fd8f3b50477f086331a`.
- Final index: `383b73ca7b0ebdb79b04008adff2085acbca48f2be8b5355062ec73d86452d92`.
- Producer: `d02e65ad5799f82b8960276d3c9eeee1e43c31cbcc78faddc22924d7431ff21b`.
- Producer tests: `1370b1c1f6576548de09b16cd14df151f395c50349453cf0c7d467cc661e50c9`.
- Original v1 configuration: `bba9d04eb6ffb20d55f754cfc4ad4876cb4c92af176aef39044d06ae54100e44`.

### Windows-path interruption and scientific equivalence

The reviewer read the full v1/v2 code diff, original/revised configurations,
preserved v1 artifacts, correction note and approved-scope proposal. **15
scientific configuration fields** are identical; **eight scientific function
ASTs** are identical; and the candidate manifests are **byte-identical**.
Preserved v1 script and test identities are checked against the frozen v1
configuration. The source tuples, their ordering, uncertainty fields, source
universe, k, threshold, solver and decision logic are unchanged.

All **476** possible corrected case paths passed saved roundtrip preflight and
were independently matched to reconstructed exact model hashes. Maximum saved
path length is **248 characters**. The filenames retain the full model hash.

The first failed write happened after a solver invocation and is correctly
described as a post-execution operational correction, not a pre-field change.
The original scientific freeze at **21:00:01.913195 UTC** remains the clock
origin. The lost attempt has no invented exact call count: the budget charges
the conservative **27-call** upper allowance, justified by one successful base
feasibility call, seven co-leader checks at at most two calls each, and six
margin objectives at at most two calls each. An infeasible base takes at most
two calls and exits. Exact algebraic repairs add no LP calls.

The final ledger's **1,463 observed calls + 27 allowance = 1,490 charged calls**
and **126 completed new models + one failed-write attempt = 127 charged model
attempts** were reconciled, including every saved model's primary/helper/crosscheck
call path. The final time remains inside the original two-hour and QA limits.
The reviewer also ran the producer's **27 synthetic tests: PASS**; no field LP
was repeated in the independent proof replay.

### Exact input and proof coverage

All **35 inherited central models** and **126 new tuple-specific models** were
independently reconstructed from original-decimal archive records. Every chosen
profile carries both its own mean and its own uncertainty, while scientific
family labels stay fixed. No componentwise envelope of the historical systems
was substituted for their union.

Verified proof counts, including inherited records, are 2,385 primal points,
514 Farkas certificates, and 1,892 dual bounds. All 359 new joint co-leader
problems and 300 new candidate-leader margin objectives were replayed, alongside
the inherited co-leader/pair decisions. These are proof-object counts, not
independent observations.

The verifier reconstructs co-leader constraints jointly in source order,
checks each one-sided margin objective, rederives source caps, validates early
stopping and remaining tuple lists, rejects a positive conclusion with any
unresolved component/margin, and independently recomputes every all35-sample
conclusion and public count. Test coverage includes wrong Farkas signs,
incorrect joint-leader points, missing rival bounds, changed margins,
unresolved-margin promotion, incomplete unions, and qualitative uniqueness
being insufficient for the frozen fixed-margin contract.

The 31 central-system ambiguity witnesses persist in the larger union without
new solves. Three additional samples acquire a second exact co-leader witness
after visiting three/four systems. Their full possible-leader sets and complete
system statistics are not claimed. One sample visits all120 systems but remains
HOLD under the frozen fixed-margin reporting rule.

### Precise reason for the remaining HOLD

The fully visited union has **72 exactly infeasible and 48 exactly compatible
components**. All48 compatible components have the same sole exactly possible
co-leader and six exactly verified competitor co-leader infeasibilities. There
is no unresolved base feasibility or co-leader exclusion in this union.

Of its288 original one-sided margin objectives, **256** are labelled numerically
unresolved. All256 have an exactly feasible primal point and an agreeing numerical
cross-check, but lack a verified dual lower bound. Every failure reason is
`DUAL_RESIDUAL_REQUIRES_UNAVAILABLE_UPPER_BOUND`: a negative residual in the
dual verification would need a finite source cap absent from the declared model.
The other32 margin records pass the stated threshold. No stored verified
below-threshold margin explains this HOLD.

Thus the retained HOLD is a limitation of the original proof-generation path,
not evidence of a contradictory source ordering, failed base compatibility,
cross-solver disagreement or demonstrated inadequate true margin. It cannot be
silently relabelled. Reusing other stored exact certificates requires a separate,
explicitly post-hoc proof-completion layer.

## 11. Draft mathematical assessment of Farkas-derived margins

This is a proof assessment only; no new field margin result is asserted here.

Write the base as s>=0, Gs<=h. For competitor j, its co-leader restrictions are
D_j s<=0, with one row s_k-s_j for every k other than j in source-index order.
A stored exact certificate (a,b)>=0 satisfies

`aG+bD_j>=0,  ah=-gamma<0`.

Equality of the first expression to zero is unnecessary: nonnegativity of s
gives `bD_j s >= -aG s >= -ah = gamma` on the base. If all other co-leader
exclusions have first established that W is the maximum at every base-feasible
point, every term s_k-s_j <= s_W-s_j. Consequently,

`gamma <= bD_j s <= B(s_W-s_j), B=sum(b)`,

so `s_W-s_j >= gamma/B`. Base feasibility makes B=0 impossible for a valid
certificate; an implementation must nevertheless reject it explicitly. Positive
rescaling of all certificate multipliers leaves gamma/B unchanged.

The universal-W premise is essential. A single infeasibility certificate for j
does not establish that an arbitrarily chosen W is the maximum. Likewise,
proofs must share the same W across every nonempty historical component before
taking a union-wide minimum. Existing saved rational multipliers and h-dot-y
values contain the needed information, but augmentation row order, source
mapping, all six exclusions, feasible base/W witnesses and all120 component
identities must be reverified.

Comparing all derived bounds with the **unchanged** fixed delta is a sound
separate proof-completion question. Qualitative uniqueness alone is not the
frozen quantitative certificate. This is standard Farkas-certificate reasoning,
not a new theorem, new measurement, physical-profile model or confidence claim.
The original Stage3 HOLD remains preserved regardless of the new layer's result.
