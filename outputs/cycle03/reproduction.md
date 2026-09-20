# Cycle 03 reproduction

## Scope

The reproducible object in Cycle 03 is the evidence audit, not a CMB rerun. No candidate exposes the full historical input/control package required to reproduce and perturb the model without imputation.

## Environment

- Python tested: 3.12.14
- Runtime dependencies: Python standard library only
- Randomness: none
- Network is not required after the nine out-of-repository source files have been retrieved

## Source-file identities

Place any retrieved source files in an external directory using the exact filenames listed in `dataset_file_audit.csv`. The repository intentionally does not redistribute the raw PDFs or workbooks.

The audit script verifies byte count, SHA-256, and MD5 for every present file and fails on any mismatch. Missing files are reported as `not_present`; they are never silently substituted.

## Build the derived crosswalks and audit

From the repository root:

```text
python scripts/audit_cycle03_evidence.py --input-dir <external-source-directory>
```

The command rewrites:

- `outputs/cycle03/fairbanks_2011_2012_table12_crosswalk.csv`
- `outputs/cycle03/barrow_2012_2013_exact_case_crosswalk.csv`
- `outputs/cycle03/aphh_beijing_radiocarbon_sample_crosswalk.csv`
- `outputs/cycle03/admission_audit.json`

It also enforces the ten-gate rule: `KEEP` is valid only if all ten gate columns are exactly `yes`.

## Run tests

```text
python -m unittest discover -s tests
```

Cycle 03 tests check:

- fail-closed KEEP logic;
- exact Fairbanks counts and interval classification;
- exact Barrow crosswalk and profile-selection leakage flag;
- committed-output identity with the builder;
- source-hash completeness;
- pending-request semantics; and
- the manuscript lock.

## Transcription audit

- Fairbanks values were manually transcribed from Ward's Table 12 on report pages 19–20 and checked against a rendered PDF.
- Barrow values were manually transcribed from Supporting Information Tables S1 and S2 and checked against rendered pages S2–S3.
- Derived differences use decimal arithmetic; no missing value is imputed.
- The Fairbanks `inside/above/below` classification uses the published minimum and maximum as a closed interval.

## Build the deterministic return package

```text
python scripts/build_cycle03_package.py <destination-directory>
```

The builder refreshes `artifact_manifest_sha256.csv`, writes the ZIP with a fixed timestamp, and creates a SHA-256 sidecar. Run it twice and compare hashes to test determinism.
