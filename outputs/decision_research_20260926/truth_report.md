# Frozen truth-index decision comparison

This is a known-construction synthetic benchmark, not a named-source field validation or total atmospheric mass result. The endpoint is the largest modeled 82-channel integrated signal. All outcomes, including failures, are retained. No continuous-box method was tested.

Source: [Via et al. 2026](https://doi.org/10.5194/amt-19-2175-2026), [CC BY 4.0 dataset](https://doi.org/10.5281/zenodo.19223353). The released error field is not assumed to calibrate its construction noise. Generated controls impose a new, explicit Gaussian law. All source-profile errors within a candidate are zero; the historical EVLS solver therefore reduces to WLS.

## Primary operating points

The table shows point methods and alpha 0.05 contrasts; the JSON preserves the entire six-alpha grid and paired bootstrap differences. Alpha is an operational threshold, not a promised post-selection coverage level. A lower wrong-singleton risk at lower reporting coverage is a tradeoff, not by itself an improvement.

| Panel | Method | Singletons/all rows | Wrong singletons | Conditional risk | All-co-leader truth covered | Empty failures |
|---|---|---:|---:|---:|---:|---:|
| released_descriptive | selected_point | 336/336 | 0 | 0.0000 | 336/336 | 0 |
| released_descriptive | finite_point_union | 336/336 | 0 | 0.0000 | 336/336 | 0 |
| released_descriptive | selected_joint_contrast@0.05 | 312/336 | 0 | 0.0000 | 336/336 | 0 |
| released_descriptive | union_joint_contrast@0.05 | 312/336 | 0 | 0.0000 | 336/336 | 0 |
| included_truth | selected_point | 721/768 | 6 | 0.0083 | 715/768 | 47 |
| included_truth | finite_point_union | 721/768 | 6 | 0.0083 | 715/768 | 47 |
| included_truth | selected_joint_contrast@0.05 | 681/768 | 0 | 0.0000 | 721/768 | 47 |
| included_truth | union_joint_contrast@0.05 | 681/768 | 0 | 0.0000 | 721/768 | 47 |
| excluded_profile_truth | selected_point | 0/768 | 0 | undefined | 0/768 | 768 |
| excluded_profile_truth | finite_point_union | 0/768 | 0 | undefined | 0/768 | 768 |
| excluded_profile_truth | selected_joint_contrast@0.05 | 0/768 | 0 | undefined | 0/768 | 768 |
| excluded_profile_truth | union_joint_contrast@0.05 | 0/768 | 0 | undefined | 0/768 | 768 |
| correlated_receptor_error | selected_point | 765/768 | 5 | 0.0065 | 760/768 | 3 |
| correlated_receptor_error | finite_point_union | 765/768 | 5 | 0.0065 | 760/768 | 3 |
| correlated_receptor_error | selected_joint_contrast@0.05 | 719/768 | 0 | 0.0000 | 765/768 | 3 |
| correlated_receptor_error | union_joint_contrast@0.05 | 719/768 | 0 | 0.0000 | 765/768 | 3 |
| underreported_uncertainty | selected_point | 0/768 | 0 | undefined | 0/768 | 768 |
| underreported_uncertainty | finite_point_union | 0/768 | 0 | undefined | 0/768 | 768 |
| underreported_uncertainty | selected_joint_contrast@0.05 | 0/768 | 0 | undefined | 0/768 | 768 |
| underreported_uncertainty | union_joint_contrast@0.05 | 0/768 | 0 | undefined | 0/768 | 768 |
| omitted_source_4 | selected_point | 102/768 | 0 | 0.0000 | 102/768 | 666 |
| omitted_source_4 | finite_point_union | 102/768 | 0 | 0.0000 | 102/768 | 666 |
| omitted_source_4 | selected_joint_contrast@0.05 | 102/768 | 0 | 0.0000 | 102/768 | 666 |
| omitted_source_4 | union_joint_contrast@0.05 | 102/768 | 0 | 0.0000 | 102/768 | 666 |
| near_tied_leaders | selected_point | 721/768 | 72 | 0.0999 | 649/768 | 47 |
| near_tied_leaders | finite_point_union | 721/768 | 72 | 0.0999 | 649/768 | 47 |
| near_tied_leaders | selected_joint_contrast@0.05 | 135/768 | 0 | 0.0000 | 721/768 | 47 |
| near_tied_leaders | union_joint_contrast@0.05 | 135/768 | 0 | 0.0000 | 721/768 | 47 |

## Fit attrition

| Panel | Shared-admissible fits / attempts | Rows without admissible fits |
|---|---:|---:|
| released_descriptive | 336/3024 | 0/336 |
| included_truth | 721/6912 | 47/768 |
| excluded_profile_truth | 0/6912 | 768/768 |
| correlated_receptor_error | 765/6912 | 3/768 |
| underreported_uncertainty | 0/6912 | 768/768 |
| omitted_source_4 | 102/6912 | 666/768 |
| near_tied_leaders | 721/6912 | 47/768 |

Negative coefficients below the declared tolerance exclude the entire fit; no clipping or pruning occurs. Overlapping rejection flags, first-exclusion counts, tiny retained negatives and pre-admission numerical winner diagnostics are in the JSON. Omitted-source metrics retain all five truth IDs and all ten pairwise opportunities, with the six fitted pairs reported separately.

Point-set containment in ordinary union-of-contrast sets passed 31740 checks. This known subset relation is not a novel method. Source-specific scale-invariance was verified before fitting. Zero observed errors or a degenerate empirical bootstrap interval do not imply zero population risk.

## Reproducibility

Implementation SHA256: `023d4c74f3dd91711e55144c9831059ed622afae3975b5bf64b1b792ea06b1ad`.
Frozen configuration SHA256: `8b77f98045f0ffd608de37b357c65107bbdb333d119b13bc22b614fe25e048c9`.
Frozen generated-array archive SHA256: `78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1`.

Protocol v2 remains byte-preserved; truth_protocol_v3.md clarifies pre-outcome admission, ties, denominators and absolute covariance. Tests, configuration and input hashes preceded scoring. Full arrays and per-row numerical ledgers remain private. Public outputs contain aggregates only.

Reproduce in order: `python scripts/audit_truth_decisions.py test`, `... prepare`, `... score`. Preparation requires the licensed, hash-verified release and scoped h5py dependency. Synthetic tests do not need the release. Scoring checks immutable hashes and refuses stale code or inputs.
