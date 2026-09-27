# Proposed proof-only completion of the frozen union margin HOLD

**No field gamma/B values have been evaluated. Root must read and approve this
protocol before field bound evaluation.** Synthetic implementation and tests may
precede approval. The original Stage3 outcome remains unchanged.

## Fixed question and inputs

Can the existing exact co-leader infeasibility certificates, without a new LP,
certify the already frozen strict-leader margin for the one fully visited
profile-system union that remains HOLD? This is post-hoc proof completion, not
new data, a new uncertainty model, a numerical refit, or a novelty claim.

Use only the frozen Stage3 index
`383b73ca7b0ebdb79b04008adff2085acbca48f2be8b5355062ec73d86452d92`, its linked
case records, and inherited Stage2 records. The Stage3 configuration is
`33f10f141aad7d8dc5f72bf7cfd06e89c7a2f61c839f1fd8f3b50477f086331a`.
The selected remaining union contains all120 actual historical profile systems:
72 exact-infeasible components and48 exact-feasible components. Source universe
is the original seven families; k=2; independent receptor/profile boxes; no
mass constraint. Every alternative retains its own released profile values and
uncertainties. No inputs, selectors, profile rows, or thresholds may change.

The threshold remains exactly `delta=1e-7*max(1,TMAC)`. Equality to the threshold
is not a passing certificate. All35 original samples remain accounted for:
34 previously witnessed non-unique unions are inherited; only this one HOLD is
examined by the proof-completion layer.

## Exact rational argument and required preconditions

For a component write the base model as `s>=0, Gs<=h`. Require a verified exact
base feasible point. Require a single family W that has an exactly verified
joint co-leader point, and for every other family j require an exact Farkas
certificate for the infeasibility of j being a co-leader. Such a certificate has
nonnegative multipliers `(a,b)` with `aG+bD_j>=0` componentwise and
`ah=-gamma<0`, where the augmented rows of `D_j` are exactly `s_k-s_j<=0`
for all k other than j, in the frozen source-index order. All these conditions
must be checked directly with rational arithmetic, not trusted from labels.

The six co-leader impossibilities jointly prove that W is the unique largest
family at every base-feasible point: otherwise a different coordinate attaining
the finite vector's maximum would itself be a possible co-leader. This universal
maximum premise is required before the next inequality may be used.

For each competitor j, nonnegativity of s and `aG+bD_j>=0` give
`bD_j*s >= -aG*s >= -ah = gamma`. Since every `s_k<=s_W` and `b>=0`,
`bD_j*s <= B*(s_W-s_j)`, where `B=sum(b)`. Hence
`s_W-s_j >= gamma/B`. Require `B>0`; zero B is a failed gate rather than a
division convention. Scaling all certificate multipliers by the same positive
rational factor must leave gamma/B unchanged.

The implementation must verify row dimensions, source names/identity, competitor
mapping, augmentation ordering, all coefficient signs, `aG+bD_j>=0`, `ah<0`,
and original base feasibility. A stored float status or precomputed scalar is
not itself a proof. Negative or missing multipliers, mismatched rows, duplicate
families, missing competitor certificates, or an unverified feasible point cause
HOLD/error, never a favorable assumption. The proof applies only to the original
per-sample independent-box sets and does not assert physical attainability or
probabilistic confidence.

## Frozen evaluation and outputs

1. Preserve hashes of producer, protocol, tests, configuration, original Stage3
   index/results/configuration and every consumed case file. Freeze a manifest
   and configuration after synthetic tests pass and before any field gamma/B
   arithmetic. Record root's protocol approval explicitly.
2. Reconstruct or read each exact stored model with checked hashes. The separate
   independent reviewer reconstructs original tuple-specific coefficients and
   replays proof objects before any final positive claim.
3. Retest all72 base infeasibility certificates and all48 base feasibility and
   W co-leader witnesses. For each feasible component check every one of the six
   competitor co-leader Farkas certificates before deriving any margin.
4. Evaluate all288 exact gamma/B bounds. Report all above/equal/below-delta or
   missing/invalid outcomes; no screening of inconvenient certificates, alternate
   multipliers, new LPs, rescaling searches, or choice of a different uncertainty
   multiplier is allowed. Positive multiplier scaling is tested only as an
   algebraic invariance, not used to tune a field result.
5. A separate completed union-margin certificate requires a nonempty union,
   exact infeasibility or all six same-W margins strictly above the unchanged
   delta for every one of its120 components, and no unresolved component.
   Otherwise the new layer remains HOLD. Empty unions are never called stable.
6. Preserve the original Stage3 report and its HOLD. Write a separate public
   aggregate report and a private exact bound/provenance ledger, clearly labeled
   post-hoc proof completion. No public sample rows or third-party source vectors.

Synthetic tests must cover zero B; negative multipliers; wrong dimensions and
row order; missing competitor proofs; wrong W/source mapping; incorrect Farkas
residual/sign; invariance to positive certificate scaling; exact threshold
equality and values below/above it; unresolved, incompatible and all-empty unions;
and absence of any numerical solver dependency. Independent review is required
before promoting a positive interpretation.
