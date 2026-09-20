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
