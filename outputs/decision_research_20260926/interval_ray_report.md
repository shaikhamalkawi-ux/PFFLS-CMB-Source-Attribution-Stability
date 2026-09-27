# Post-hoc finite witnesses from existing recession proofs

No LP or fit was rerun. The frozen interval producer and geometry artifacts, including their original gap labels, remain unchanged.

For an exactly feasible x and recession ray d with q·d<0, set `t=max(0,(q·x+1)/(-q·d))`. Then `x+t*d` is an exactly feasible finite point with `q·(x+t*d)<=-1`. The number1 is only a convenient proof target; it is not a new interval, confidence level, or empirical measurement. Every constructed point was rechecked with rational arithmetic against all original inequalities.

Read 492 unique cases; attempted 229 previously gap-labeled pair decisions containing an exact unbounded-ray proof.
Derived statuses: `{"EXACT_BOTH_ORDERINGS_COMPLETED": 164, "NO_OPPOSITE_SIGN_IN_STORED_PROOFS": 65}`.

## Previously gap-labeled orders first verified with the mass band

The following compares original mass-band and no-mass results at unchanged inputs. Verified paired mass-band points are additionally checked against every original no-mass inequality before witness reuse; this does not impose a mass assumption on the no-mass model. These are additional proofs of ambiguity already implied by the no-mass model, not increased empirical evidence.

| Universe | k | Uncertainty | Samples | Original mass-only order gaps | No-mass ambiguity completed from stored rays | Not completed |
|---|---:|---|---:|---:|---:|---:|
| central_retained_bridge | 1 | fixed_profile | 35 | 0 | 0 | 0 |
| central_retained_bridge | 1 | joint_intervals | 35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | fixed_profile | 35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | joint_intervals | 35 | 0 | 0 | 0 |
| central_retained_bridge | 3 | fixed_profile | 35 | 0 | 0 | 0 |
| central_retained_bridge | 3 | joint_intervals | 35 | 57 | 1 | 56 |
| full_seven_primary | 1 | fixed_profile | 35 | 0 | 0 | 0 |
| full_seven_primary | 1 | joint_intervals | 35 | 0 | 0 | 0 |
| full_seven_primary | 2 | fixed_profile | 35 | 0 | 0 | 0 |
| full_seven_primary | 2 | joint_intervals | 35 | 0 | 0 | 0 |
| full_seven_primary | 3 | fixed_profile | 35 | 0 | 0 | 0 |
| full_seven_primary | 3 | joint_intervals | 35 | 60 | 1 | 59 |

All24 labeled panels, including zero-attempt and incompatible cases, remain in the JSON; source universes are not pooled. The private ledger links each constructed point to its source case hash and original proof location.
Private witness ledger SHA-256: `d57b3dade0ff1471fb05af4be087084983057e8618d11b7ed0ee210e14c8400f`.

Reproduce: `python scripts/audit_interval_ray_witnesses.py`. No third-party material is newly redistributed.
