# Scripts

Place reproducible retrieval, parsing, audit, and experiment-entry scripts here.

Retrieval scripts should prefer official sources and record hashes/provenance.

Cycle 01 provides:

- `fetch_cycle01_sources.py` for allowlisted out-of-repository retrieval;
- `validate_cycle01_evidence.py` for the fail-closed admission gate; and
- `build_cycle01_package.py` for the deterministic review ZIP and manifests.

Cycle 02 adds `extract_cycle02_fairbanks.py`. It recovers the published
Appendix C day-level EPA/OMNI estimates and joins State Building dates to the
43-species EPA AirData records. The join is intentionally labeled as a
candidate reconstruction, not as proof of the historical CMB input vector.

Cycle 03 adds:

- `audit_cycle03_evidence.py`, which verifies out-of-repository source hashes,
  rebuilds the three exact/subset crosswalks, and enforces the ten-gate rule;
- `build_cycle03_package.py`, which writes the deterministic review ZIP,
  internal artifact manifest, and ZIP SHA-256 sidecar.

Issue #8 outreach adds:

- `validate_outreach_package.py`, which fail-closes status, provenance,
  contact, request-scope, and manuscript-boundary checks; and
- `build_outreach_package.py`, which writes the deterministic outreach review
  ZIP, internal manifest, and ZIP SHA-256 sidecar.

Cycle 04 adds:

- `validate_cycle04_submission_gate.py`, which locks the baseline identity,
  reported JRC/EPA numbers, claim boundary, lineage, HOLD blockers, legacy
  manifest state, and project-state semantics. Its `--package-local` mode
  validates an extracted return ZIP without legacy repository files; and
- `build_cycle04_package.py`, which validates first and then builds an
  allowlisted, fixed-timestamp, stored-member ZIP. Normal builds are
  non-mutating; `--refresh-manifest` is required to update the tracked Cycle 04
  manifest deliberately. Every build is extracted and package-locally validated
  before success is returned.
