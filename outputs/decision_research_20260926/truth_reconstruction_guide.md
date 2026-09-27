# Restoring the omitted truth inputs without rerunning the experiment

The private return deliberately omits `truth_frozen_arrays.npz` because it contains released source/profile/receptor arrays. Frozen manifests and numerical ledgers remain in the return. This omission is a packaging choice, not a claim that the independently verified CC BY 4.0 dataset is inaccessible.

Use the **separate** `scripts/reconstruct_truth_inputs.py`. It imports only the existing frozen release-reader and deterministic generation functions for reconstruction; it does not invoke fitting, decision scoring, bootstrap scoring, or the original test-gate writer. It verifies the original gate/implementation/configuration identities, the original input-manifest SHA256, all 15 array keys/shapes/dtypes/hashes, RNG states and the compressed NPZ hash before exclusively creating an absent target. It refuses an existing target even if the bytes match. A mismatched runtime, input or hash must cause a stop, not an overwrite or a new “equivalent” freeze.

## Inputs, attribution and environment

Acquire the original *Datasets used in the BAMF+horseshoe manuscripts* from [Zenodo DOI 10.5281/zenodo.19223353](https://doi.org/10.5281/zenodo.19223353), released 2026-03-25. The independently preserved record declares CC BY 4.0. The direct original archive endpoint is [datasets_bamf_horseshoe.zip](https://zenodo.org/api/records/19223353/files/datasets_bamf_horseshoe.zip/content); no signed URL or credentials are needed. Attribution metadata is retained in `truth_benchmark_sources.json` and the original Zenodo metadata record. The scientific article is Via et al. (2026), [DOI 10.5194/amt-19-2175-2026](https://doi.org/10.5194/amt-19-2175-2026), with its separate CC BY 4.0 licence.

Dataset creator names, as supplied in the preserved record: Via, Marta; Demšar, Jure; Manousakas, Manousos; Rusanen, Anton; Jiang, Jianhui; Grange, Stuart; Jafrezzo, Jean-Louis; Dinh Ngoc, Thuy Vy; UZU, Gaëlle; Griša, Močnik; Dällenbach, Kaspar Rudolf. These are record metadata, not an independently corrected author list. Our compensated profile normalization and generated controls are modifications; they are not the release authors' original output or an endorsement.

- Archive SHA256: `e4f6e055a3db15e22f7c0c449a84d2d23a1f86270d658ff3f1a63fc435367501`.
- Selected member: `datasets/online_SDs/Zurich/Zurich_0.h5`, SHA256 `fa62a734a1dda779df572e0c975e3103a2c9ad06d2a3eaffc2ed8affd3d89d64`.
- Default archive path, relative to repository root: `_inputs/decision_research_20260926/truth_benchmark/datasets_bamf_horseshoe.zip`.
- Default destination: `private/decision_research_20260926/truth_frozen_arrays.npz`.
- Original environment: Python 3.12.14, NumPy 2.3.5, SciPy 1.18.1, h5py 3.16.0. The frozen reader first checks the task-local dependency directory `tmp/decision_research_hdf5_deps`, then ordinary import paths. Runtime dependencies are not included in the return. Install dependencies in an isolated environment or the documented task-local target, not by modifying the archived files.

Keep original `audit_truth_decisions.py`, `audit_epa_native_strengthening.py`, `test_truth_decisions.py`, the v2 audit/source files, v3 protocol, test gate, configuration and input manifest byte-for-byte. The helper rejects drift. The expected reconstructed NPZ SHA256 is `78ec90aa3adb31c7d4e83237bcec79643579161d9e6407d9479995ed494581c1`. Compression/runtime differences are not silently waived even if some values agree.

## Commands from the repository root

Run synthetic tests directly, without replacing the historical test gate:

```text
python -m unittest discover -s tests -p test_reconstruct_truth_inputs.py -v
python -m unittest discover -s tests -p test_truth_decisions.py -v
```

Check reconstruction entirely in memory, with no file creation:

```text
python scripts/reconstruct_truth_inputs.py --check-reconstruction
```

Restore the omitted NPZ only when the target is absent:

```text
python scripts/reconstruct_truth_inputs.py
```

An alternative acquired archive path can be passed with `--release PATH`. A different populated snapshot directory can be passed with `--private PATH`; its original metadata is still identity checked. Do not use this to overwrite the live research directory. If the target already exists, the restore command refuses it; use:

```text
python scripts/reconstruct_truth_inputs.py --verify-only
python scripts/audit_truth_decisions.py verify
python outputs/decision_research_20260926/truth_saved_ledger_verification.py
```

The first two commands verify frozen input identity; the third checks the saved numerical ledgers and aggregate relationships. None is a new benchmark fit. `--verify-only` does not read the release or generate controls; it verifies the existing NPZ and original metadata. `--check-reconstruction` does regenerate inputs in memory, not fitted estimates or scores. The helper reports only hashes/counts/status, never raw array contents.

Do **not** run `audit_truth_decisions.py test` in this populated archived snapshot: it refuses to replace the gate after the input freeze. Likewise, `prepare` sees the existing manifest and verifies rather than recreates the omitted NPZ. This separate helper fixes that delivery workflow without changing the original producer.

## Fresh isolated numerical rerun is a different operation

The historical `test -> prepare -> score` sequence belongs to a fresh isolated workspace containing the unchanged source/tests and prerequisite protocol files, but no already-frozen destination records. New run timestamps and gate/configuration digests are new artifacts; preserve the original snapshot separately. A future full rerun must compare array/scientific outputs explicitly and label the new run, not replace original records or claim fresh timestamps preceded the historical outcomes. No fresh fit/scoring rerun is part of this reconstruction task.

Similarly, `audit_interval_profile_union.py` contains the original session's 2026-09-27 05:00 UTC cutoff. Keep it as an archived-session runner. Independent saved-proof replay is distinct from a new numerical run and does not need that historical solve budget. A minimal future Stage3 reproduction wrapper could supply a separately declared current bounded clock/budget to the existing solver-budget interface, preserve all model/order/stop semantics, and write a new isolated ledger. That wrapper requires separate review; none is implemented or executed here.

## Verification record

The separate helper's synthetic safety tests and real-input in-memory/verify-only checks are recorded in `truth_reconstruction_verification.json` when complete. The original frozen script, test, configuration, manifest and NPZ must retain their recorded hashes. This is input-delivery verification only, not new evidence for model novelty, source truth, confidence coverage, or the benchmark's already-negative profile-union comparison.
