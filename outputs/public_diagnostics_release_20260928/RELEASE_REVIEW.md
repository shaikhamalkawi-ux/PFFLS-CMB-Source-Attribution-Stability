# Review provenance and claim limits

This document distinguishes the historical scientific review from verification of a newly packaged archive. It does not certify a new run that has not occurred.

The retained editorial-response review records report:

- Independent source/fixture review of the two new postprocessors before the saved calculations were accepted.
- JRC saved-result review against the two pinned publication-summary CSVs, with all 30 comparisons and seven fixed-profile strata retained. Review record SHA-256: `c58b06fdf0e09697ad7135e25c07e6cdfe88ceae91c0200cdec670941ffe8299`.
- EPA independent saved-result review against all 345 preserved substitution rows and all 35 measured-mass joins, including 323 derived outcomes and 22 null exclusions. Review record SHA-256: `b77c0ae0b2319a65524327a4536aa3b97b966f5fc80a0652e1c65fcf7c9b9b39`.

These historical review documents and their private inputs are not included. Their reported checks are provenance, not a claim that an external reader can repeat private-input verification with this public archive alone. The included artificial fixtures do not supply physical ground truth.

For this release, `verify_public_release.py` separately checks its inventory, SHA-256 manifest, exact scientific-file identities, and repeatability of the included JRC arithmetic. It explicitly does not repeat EPA native fitting or saved-ledger postprocessing. Any publication receipt or final archive QA must state the actual verifier result and the missing-input status; neither may be inferred from this note.

**KEEP:** descriptive source-family localization, EPA effect magnitudes, all denominators, one-sample dependence of the two strict changes, complete documented failures, and transparent provenance.

**HOLD:** native JRC reconstruction, missing fitted-vector checks, reference-uncertainty interpretation, independent field-accuracy claims, and journal-submission readiness.

**REMOVE from claims:** method superiority, revolutionary novelty, statistical significance based on descriptive margins alone, independent-event interpretation of same-sample substitutions, and claims that this public archive is a complete native-data reproduction.
