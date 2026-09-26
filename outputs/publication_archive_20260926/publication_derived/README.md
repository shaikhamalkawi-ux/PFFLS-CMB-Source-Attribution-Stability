# Publication-derived consistency and provenance package

This archive is intentionally bounded. It reconstructs and verifies publication-level derived values and provenance records used in the manuscript, but it is not represented as a fresh source-native rerun of every JRC and EPA model fit.

## Run

```bash
python code/reproduce_publication_derived_data.py
python code/verify_release.py
```

Expected verifier result: **14/14 publication-summary arithmetic checks PASS**, followed by SHA-256 manifest verification. The legacy verifier's console label is retained; it does not imply independent validation of the original fits.

This release includes an explicitly publication-derived supplementary-table
extension. Run `python code/verify_supplementary_consistency.py` after the original
commands. Read `EDITORIAL_EXTENSION_SCOPE.md` for the added files and unresolved
traceability limits.

## Included
- JRC 12-set reported landscape.
- JRC campaign-level point-reference vector.
- Profile-admission crosswalk.
- Complete 30-comparison lower-mean-reduced-chi-square reconstruction from the displayed 12-set values.
- EPA alternative/attrition and headline summary tables.
- Machine-readable profile-choice traceability JSON Schema.
- Source-acquisition/provenance record and cryptographic hashes.

## Not included / not claimed
- Canonical unrounded 30-comparison machine-output ledger.
- Row-level EPA whole-profile rerun ledger.
- The prior complete source-native executable archive.
- Third-party JRC/EPA binaries where redistribution permission is uncertain.

See `REPRODUCIBILITY_LIMITS.md` before describing this package in a permanent repository.
