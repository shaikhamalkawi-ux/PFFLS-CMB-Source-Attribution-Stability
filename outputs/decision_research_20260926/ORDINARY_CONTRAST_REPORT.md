# Ordinary joint-contrast comparator — post-hoc diagnostic audit

This is a nominal plug-in WLS summary, not validated coverage or field source truth.
All35 replayed central fits agree; maximum contribution difference 0.

Primary nominal alpha0.05 panel (Bonferroni across within-fit source pairs):

| Sample scope / existing witness flag | n | Conditional singleton | Witness | Both |
|---|---:|---:|---:|---:|
| all35/basic/joint_changed_count | 35 | 9 | 29 | 4 |
| all35/basic/observed_local_stable_joint_witness | 35 | 9 | 7 | 4 |
| all35/basic/complete_local_stable_joint_witness | 35 | 9 | 2 | 1 |
| central_strict/strict/joint_changed_count | 4 | 2 | 1 | 0 |

All alpha0.10/0.05/0.01 tables and eligibility denominators are in ordinary_contrast_results.json.
A central covariance warning may already reveal uncertainty that a point-fit comparison misses.
A central conditional singleton plus a profile-choice reversal shows different uncertainty scopes;
it is not evidence that either side knows the environmental truth.

Limitations:
- No field source truth or nominal coverage guarantee
- Estimated effective weights and central source pruning treated as fixed
- Covariance ignores correlations/systematic errors and profile-family selection
- Joint grid retains unresolved alternatives; no full-grid certificate
- Post-hoc diagnostic overlap, not a new uncertainty method
