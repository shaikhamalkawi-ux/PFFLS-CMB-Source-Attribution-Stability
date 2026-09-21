# Cycle 04 reproduction

## Scope

Cycle 04 reproduces the baseline-search audit, lineage identity checks,
claim-lock validation, readiness decision, and return-package integrity. It
does **not** reproduce the central JRC or EPA calculations because their exact
computational archives are absent.

## Environment

- Tested interpreter: CPython 3.12.14.
- Dependencies: Python standard library only.
- Runtime enforcement: documented and tested, not machine-pinned by this cycle.
- Randomness: none.
- Network: not required for validation, tests, or package construction.
- ZIP method: stored members with a fixed timestamp and fixed Unix file mode.
- New Cycle 04 text paths are normalized to LF by `.gitattributes`.

The historical R3l extraction audit used Poppler `pdftotext` 24.04.0. The PDF
itself is intentionally excluded from the repository and return ZIP.

## Validate and write the QA snapshot

From the repository root:

```text
python scripts/validate_cycle04_submission_gate.py --write-report outputs/cycle04/qa_report.json
```

Expected overall status:

```text
HOLD_WITH_EXACT_BLOCKERS
```

A HOLD is the successful fail-closed outcome; a validator error means the
record no longer satisfies the scientific or packaging constraints.

## Validate an extracted return ZIP without the repository

After extracting the ZIP, change into its single top-level directory and run:

```text
python scripts/validate_cycle04_submission_gate.py --package-local
python -m unittest discover -s tests -p "test_*.py" -v
```

Package-local validation checks the complete claim schema, canonical candidate
delta, evidence-search snapshots, HOLD gates, exact artifact manifest, and exact
extracted-file allowlist. It does not require the repository's Cycle 01–03
files. The builder performs this extraction-and-validation smoke test before it
returns success.

## Run all repository tests

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

Record the final command, interpreter, test count, and result in
`outputs/cycle04/test_results.txt`.

## Refresh the committed artifact manifest

After all cycle-specific files, QA, and test records are final:

```text
python scripts/build_cycle04_package.py --refresh-manifest _deliverables/cycle04
```

`--refresh-manifest` updates only
`outputs/cycle04/artifact_manifest_sha256.csv`, then builds the package. Normal
builds never mutate tracked repository files.

## Verify a normal deterministic build

```text
python scripts/build_cycle04_package.py _deliverables/cycle04-check
```

Build twice to separate directories. The ZIP hashes and sidecars must be
identical. Package members must exactly equal the explicit allowlist plus the
artifact manifest. Any missing file, unexpected Cycle 04 output, manifest
drift, PDF/manuscript artifact, ZIP, database, raw-data file, or symbolic link
fails closed.

The destination must be outside `outputs/cycle04/`; the builder rejects any
destination at or below that controlled source directory.

## Third-party boundary

The historical PDF hashes can be checked against authorized external copies,
but the PDF bytes must not be copied into the repository or return ZIP.
