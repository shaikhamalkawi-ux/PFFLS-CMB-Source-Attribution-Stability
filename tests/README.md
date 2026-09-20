# Tests

`test_cycle02_fairbanks.py` checks the day-table parser and the fail-closed
classification of EPA-versus-OMNI as profile-system sensitivity.

Required test categories:
- exact-case regression;
- numerical tolerance checks;
- parser identity checks;
- fail-closed behavior on missing evidence;
- no silent imputation;
- claim-gate boundary tests.

`test_cycle01_evidence.py` covers the Cycle 01 registry schema, KEEP fail-closed
logic, source hashes, and the repository's final HOLD decision.
