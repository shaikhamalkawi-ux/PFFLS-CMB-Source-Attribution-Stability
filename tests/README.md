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

`test_cycle03_evidence.py` locks the ten-gate HOLD result, Fairbanks Table 12
counts and arithmetic, Barrow leakage boundary, APHH aggregate-only boundary,
source identities, pending-request semantics, and the manuscript lock.

`test_outreach_package.py` verifies the complete Issue #8 return package,
including exact contact addresses, non-duplicative SENT / PENDING semantics,
the ADEC user-action block, technical request scope, official-source records,
the locked manuscript baseline, and deterministic packaging.

`test_cycle04_submission_gate.py` regression-checks all 13 reported claims,
rejects baseline promotion and false recomputation, tests the historical anchor
identity, preserves live pending evidence, audits known legacy-manifest state,
rejects restricted or unexpected files, and verifies exact deterministic ZIP
membership without mutating the tracked manifest.

`test_cycle04_package_local.py` carries a literal claim-schema oracle separate
from the validator and runs inside both the full checkout and the extracted
return package. The builder's integration tests exercise the exact-tree
package-local validator after extraction.
