# Exploratory joint-profile decision audit

This is a new finite-grid analysis, not a manuscript change, field validation, or novelty claim.

Configuration frozen before the first joint fit: `f6aebb0bca2ef417ef6e8bff892ac2286b0a61e0fe47c62a5ae3608ab3c97314`.
All 35 initial samples retained; 35 converged central fits.
Grid choices including central fits: **3900**.

## Attrition by number of coordinated substitutions

| Changed slots | Attempted | Converged | Unresolved | Basic admitted | Basic top changes | Strict admitted | Strict top changes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 35 | 35 | 0 | 35 | 0 | 4 | 0 |
| 1 | 345 | 323 | 22 | 283 | 62 | 26 | 2 |
| 2 | 1180 | 950 | 230 | 764 | 283 | 56 | 7 |
| 3 | 1620 | 1080 | 540 | 805 | 447 | 42 | 6 |
| 4 | 720 | 410 | 310 | 290 | 215 | 10 | 0 |

## Sample-level comparisons

A local-stability count requires at least one admitted distance-one alternative. Complete local stability additionally requires every distance-one choice to be resolved. Thus a numerically unresolved choice is not silently removed from a stability claim.

| Screen | Central eligible / initial | Observed local top stable | Complete local top stable | Observed-local-stable with joint top witness | Complete-local-stable with joint top witness | Complete joint top stable |
|---|---:|---:|---:|---:|---:|---:|
| converged | 35/35 | 9 | 1 | 7 | 1 | 0 |
| basic | 35/35 | 13 | 4 | 7 | 2 | 0 |
| strict | 4/35 | 3 | 0 | 0 | 0 | 0 |

Full-order and witness-distance histograms, partial-order counts, and all screen-specific denominators are in `joint_profile_results.json`.

## Limits and disposition

- KEEP: exhaustive counts, reproducible witnesses, and unresolved-state-aware finite-grid statements.
- HOLD: novelty, generalization to unenumerated profiles, probability coverage, environmental accuracy, and unrestricted source universes.
- REMOVE: any inference that a screened-out converged fit proves physical impossibility, or that nonconvergence proves inadmissibility.
- Profiles are combined only for the central-retained slots. A source removed from the central solution is not reintroduced; these are conditional source-universe results.
- Basic/strict screening is a declared numerical eligibility convention, not independent scientific validation of profiles.
- Negative alternative contributions are retained, not clipped. Their presence limits physical interpretation.
- The Cartesian combinations are exploratory mathematical combinations of historical family alternatives; simultaneous environmental plausibility is not independently established.
- Minimum observed witness distance is exact only when every smaller-distance choice was resolved. A witness remains valid even if other grid choices are unresolved.
- No baseline manuscript, previous reconstruction outputs, Zenodo archive, or raw data were changed.

Private ledger SHA-256: `ba73f7f41de50d4b40edf1fe5be0513120dfb109c9a10730f1007e7f6c3143a2`. Full source vectors, dates, margins, and per-sample witnesses stay in ignored private storage.

## Reproduce

```text
python scripts/audit_joint_profile_decisions.py --inputs <official-EPA-archive-directory>
python -m unittest discover -s tests -p test_joint_profile_decisions.py -v
```
