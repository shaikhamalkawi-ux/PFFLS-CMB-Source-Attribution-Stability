# Post-hoc interval geometry and mass-assumption audit

This reads the completed frozen Stage2 proof records. It performs no new fit or LP and changes no uncertainty multiplier, input, or threshold. The geometry is established linear algebra, not a novelty claim.

## Exact boundedness criterion and assumptions

For a **nonempty** independent-box model without an added mass constraint, with `0 <= L <= U` and `s >= 0`, the recession cone is

```text
{d >= 0: Ld <= 0, -Ud <= 0} = {d >= 0: Ld = 0}.
```

Because all entries of L and d are nonnegative, a positive d_j is possible exactly when every entry of column L[:,j] is zero. Thus the cone is the nonnegative span of those coordinate directions. A source coordinate is unbounded above if and only if its entire lower-profile column is zero. If none is zero, the compatible set is bounded. Empty sets are not called unbounded. The statement does not cover signed sources, correlated-profile constraints, extra equalities, or a different uncertainty model.

Adding the finite historical mass upper bound blocks every nonzero nonnegative recession ray. This is a consequence of an extra assumption; it is not newly measured information or proof that the bound is physically correct.

## No-mass geometry

| Universe | k | Uncertainty | Compatible /35 | Compatible with zero lower column | Exact ray occurrences | Missing stored rays |
|---|---:|---|---:|---:|---:|---:|
| central_retained_bridge | 1 | fixed_profile | 0/35 | 0 | 0 | 0 |
| central_retained_bridge | 1 | joint_intervals | 5/35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | fixed_profile | 0/35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | joint_intervals | 33/35 | 0 | 0 | 0 |
| central_retained_bridge | 3 | fixed_profile | 5/35 | 0 | 0 | 0 |
| central_retained_bridge | 3 | joint_intervals | 35/35 | 35 | 35 | 0 |
| full_seven_primary | 1 | fixed_profile | 0/35 | 0 | 0 | 0 |
| full_seven_primary | 1 | joint_intervals | 5/35 | 0 | 0 | 0 |
| full_seven_primary | 2 | fixed_profile | 0/35 | 0 | 0 | 0 |
| full_seven_primary | 2 | joint_intervals | 33/35 | 0 | 0 | 0 |
| full_seven_primary | 3 | fixed_profile | 5/35 | 0 | 0 | 0 |
| full_seven_primary | 3 | joint_intervals | 35/35 | 35 | 35 | 0 |

Source-family column occurrences are given explicitly in `interval_geometry.json`, separately for all35 samples and nonempty sets.

## Decisions first verified after imposing the historical mass band

These are paired results with the same receptor, profiles, source universe, uncertainty multiplier and treatment. Counts of new pair orders are restricted to pairs for which both complete sets are exactly compatible. A missing no-mass proof is distinguished from a verified no-mass reversal/tie. Incompatible mass-band cases produce no winner claim.

| Universe | k | Uncertainty | Both sets compatible /35 | Pair orders only after band | Of these: no-mass reversal/tie witnessed | Unique leader only after band | No-mass compatible, band incompatible |
|---|---:|---|---:|---:|---:|---:|---:|
| central_retained_bridge | 1 | fixed_profile | 0/35 | 0 | 0 | 0 | 0 |
| central_retained_bridge | 1 | joint_intervals | 4/35 | 3 | 3 | 2 | 1 |
| central_retained_bridge | 2 | fixed_profile | 0/35 | 0 | 0 | 0 | 0 |
| central_retained_bridge | 2 | joint_intervals | 33/35 | 16 | 16 | 0 | 0 |
| central_retained_bridge | 3 | fixed_profile | 3/35 | 0 | 0 | 0 | 2 |
| central_retained_bridge | 3 | joint_intervals | 35/35 | 180 | 123 | 0 | 0 |
| full_seven_primary | 1 | fixed_profile | 0/35 | 0 | 0 | 0 | 0 |
| full_seven_primary | 1 | joint_intervals | 4/35 | 3 | 3 | 2 | 1 |
| full_seven_primary | 2 | fixed_profile | 0/35 | 0 | 0 | 0 | 0 |
| full_seven_primary | 2 | joint_intervals | 33/35 | 18 | 18 | 0 | 0 |
| full_seven_primary | 3 | fixed_profile | 3/35 | 0 | 0 | 0 | 2 |
| full_seven_primary | 3 | joint_intervals | 35/35 | 191 | 131 | 0 | 0 |

Full feasibility transitions, unchanged orders/leaders, verification gaps, and co-leader exclusions are retained in the JSON. The retained-universe bridge is never pooled with the full-seven-source primary analysis. No narrowed set is interpreted as increased evidence.

Checked 840 labeled records / 492 unique case files; all case/model hashes and expected constraint structures agreed.
Frozen private index SHA-256: `381d20db9a35e1e8a725b535b588a60291def382a6f3196a10ef4a4302b66d40`.

Reproduce: `python scripts/audit_interval_geometry.py` after completing the approved interval Stage2 run.
