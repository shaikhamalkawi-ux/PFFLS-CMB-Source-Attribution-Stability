# Public-subset cleanroom smoke QA

Status: **PASS_WITH_EXPLICIT_INTEGRATION_SKIPS**.

A disposable snapshot was built from git archive base `2437750f8223304231ab9afcc9ec4a54956c8d97` plus exactly the owner-supplied public allowlist. No current private records, raw archives, input NPZ/HDF5, or field ledgers were copied. The snapshot location and raw logs are retained only in the owner-private report.

All 94 allowlisted copies matched the originals byte-for-byte. 28 allowlisted Python files compiled. The 13 allowlisted unittest modules plus the counterexample script reported 306 tests: 302 executed, 4 explicitly skipped.

| Module | Reported | Executed | Skipped | Result |
| --- | ---: | ---: | ---: | --- |
| `tests/test_decision_measurements.py` | 21 | 20 | 1 | PASS_WITH_SKIPS |
| `tests/test_interval_certificate_records.py` | 24 | 24 | 0 | PASS |
| `tests/test_interval_decisions.py` | 29 | 29 | 0 | PASS |
| `tests/test_interval_farkas_margin.py` | 33 | 33 | 0 | PASS |
| `tests/test_interval_farkas_records.py` | 19 | 19 | 0 | PASS |
| `tests/test_interval_geometry.py` | 13 | 13 | 0 | PASS |
| `tests/test_interval_profile_union.py` | 27 | 27 | 0 | PASS |
| `tests/test_interval_ray_witnesses.py` | 18 | 18 | 0 | PASS |
| `tests/test_interval_union_records.py` | 19 | 19 | 0 | PASS |
| `tests/test_joint_profile_decisions.py` | 17 | 14 | 3 | PASS_WITH_SKIPS |
| `tests/test_ordinary_contrasts.py` | 11 | 11 | 0 | PASS |
| `tests/test_reconstruct_truth_inputs.py` | 18 | 18 | 0 | PASS |
| `tests/test_truth_decisions.py` | 40 | 40 | 0 | PASS |
| `scripts/test_decision_certificate_counterexamples.py` | 17 | 17 | 0 | PASS |

## Skips and scope

- `test_saved_integration_records_validate_and_design_precedes_evaluation (test_decision_measurements.MeasurementTests.test_saved_integration_records_validate_and_design_precedes_evaluation)`: completed private experiment not available.
- `test_all_samples_and_every_enumerated_choice_accounted_for (test_joint_profile_decisions.JointNativeIntegrationTests.test_all_samples_and_every_enumerated_choice_accounted_for)`: official EPA archives unavailable; integration explicitly skipped.
- `test_converged_rows_never_clip_negative_values (test_joint_profile_decisions.JointNativeIntegrationTests.test_converged_rows_never_clip_negative_values)`: official EPA archives unavailable; integration explicitly skipped.
- `test_distance_one_reproduces_frozen_prior_one_at_a_time_counts (test_joint_profile_decisions.JointNativeIntegrationTests.test_distance_one_reproduces_frozen_prior_one_at_a_time_counts)`: official EPA archives unavailable; integration explicitly skipped.

The joint-profile native integration class would refit field grids when all official EPA archives are present. Those archives were absent in this isolated snapshot, so its three checks were skipped; the saved-private measurement integration check was also skipped. These are not counted as passing executed tests.

Small constructed numerical cases in the synthetic tests are permitted; no field producer entry point, field fit, fresh field LP, or saved-field certificate replay was run. The current runtime required no additional h5py path or package installation.

## Identity and isolation

- Allowlist SHA-256: `fdf2f07af3c6d8ff83998c5428c7a0e444bd3f2aa6bae3b9556c6c9c1f09fe45`.
- Runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.18.1.
- Snapshot private directory and both possible input roots were absent before every module and after testing.
- Post-run original/snapshot/base byte drift: 0/0/0. Unexpected snapshot files: 0.
- Full module results, skip reasons, and the per-file SHA-256 manifest are in `public_cleanroom_qa.json`.

This verifies the tested public synthetic workflow, not self-contained reproduction of the omitted field proof ledgers. No frozen scientific file, git index, branch, or allowlist was edited.
