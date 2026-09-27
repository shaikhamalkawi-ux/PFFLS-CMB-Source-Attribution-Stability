# Interval decision audit — central historical profile system only

This is an exploratory application of established interval/set-membership mathematics, not a new theorem or confidence procedure.

Stage 1: **PASS**. Stage 2: **COMPLETE**. No Stage 3 full-profile-grid LP was run.
Frozen configuration SHA-256: `9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a`. All 35 samples retained in every panel.

## Compatibility and decision outcomes

Each row is a separate panel. The historical mass band is a diagnostic sensitivity, not physical conservation. Independent entrywise boxes do not establish physical attainability of every witness.

| Universe | k | Uncertainty | Mass model | Exact feasible | Exact infeasible | Unresolved | Verified unique leader | >=2 exact possible co-leaders |
|---|---:|---|---|---:|---:|---:|---:|---:|
| central_retained_bridge | 1 | fixed_profile | historical_80_120_band | 0 | 35 | 0 | 0 | 0 |
| central_retained_bridge | 1 | fixed_profile | none | 0 | 35 | 0 | 0 | 0 |
| central_retained_bridge | 1 | joint_intervals | historical_80_120_band | 4 | 31 | 0 | 2 | 2 |
| central_retained_bridge | 1 | joint_intervals | none | 5 | 30 | 0 | 0 | 5 |
| central_retained_bridge | 2 | fixed_profile | historical_80_120_band | 0 | 35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | fixed_profile | none | 0 | 35 | 0 | 0 | 0 |
| central_retained_bridge | 2 | joint_intervals | historical_80_120_band | 33 | 2 | 0 | 2 | 31 |
| central_retained_bridge | 2 | joint_intervals | none | 33 | 2 | 0 | 2 | 31 |
| central_retained_bridge | 3 | fixed_profile | historical_80_120_band | 3 | 32 | 0 | 2 | 1 |
| central_retained_bridge | 3 | fixed_profile | none | 5 | 30 | 0 | 3 | 2 |
| central_retained_bridge | 3 | joint_intervals | historical_80_120_band | 35 | 0 | 0 | 0 | 35 |
| central_retained_bridge | 3 | joint_intervals | none | 35 | 0 | 0 | 0 | 35 |
| full_seven_primary | 1 | fixed_profile | historical_80_120_band | 0 | 35 | 0 | 0 | 0 |
| full_seven_primary | 1 | fixed_profile | none | 0 | 35 | 0 | 0 | 0 |
| full_seven_primary | 1 | joint_intervals | historical_80_120_band | 4 | 31 | 0 | 2 | 2 |
| full_seven_primary | 1 | joint_intervals | none | 5 | 30 | 0 | 0 | 5 |
| full_seven_primary | 2 | fixed_profile | historical_80_120_band | 0 | 35 | 0 | 0 | 0 |
| full_seven_primary | 2 | fixed_profile | none | 0 | 35 | 0 | 0 | 0 |
| full_seven_primary | 2 | joint_intervals | historical_80_120_band | 33 | 2 | 0 | 2 | 31 |
| full_seven_primary | 2 | joint_intervals | none | 33 | 2 | 0 | 2 | 31 |
| full_seven_primary | 3 | fixed_profile | historical_80_120_band | 3 | 32 | 0 | 2 | 1 |
| full_seven_primary | 3 | fixed_profile | none | 5 | 30 | 0 | 3 | 2 |
| full_seven_primary | 3 | joint_intervals | historical_80_120_band | 35 | 0 | 0 | 0 | 35 |
| full_seven_primary | 3 | joint_intervals | none | 35 | 0 | 0 | 0 | 35 |

## Verification and interpretation

- Exact feasible status requires a rational point independently satisfying every inequality. Exact infeasible status requires an independently verified rational Farkas certificate.
- A verified order uses a rational, residual-corrected dual lower bound with independently justified source upper bounds, an exactly feasible primal point, and a fixed-method floating solver cross-check. Float solver optimality is never itself called a proof.
- Exact unboundedness requires an exactly feasible point and an exactly verified improving recession ray. Any missing proof component remains unresolved.
- A nonpositive lower bound alone does not establish reversal: reversal/order/tie labels require exactly feasible witnesses.
- Co-leader feasibility imposes all leader inequalities simultaneously. Separate pairwise possibilities are insufficient.
- Nonnegative sources are an explicit modeling restriction. The full-seven universe is primary; the fit-pruned retained universe is a separately labeled bridge sensitivity.
- KEEP the qualified compatibility results and proof objects; HOLD external accuracy, probabilistic coverage, physical box attainability and full-profile-grid claims.
- Private index SHA-256: `381d20db9a35e1e8a725b535b588a60291def382a6f3196a10ef4a4302b66d40`; case files are individually hashed in that private index.

## Reproduce

```text
python scripts/audit_interval_decisions.py --stage1
python scripts/audit_interval_decisions.py --run-field-stage2
```
