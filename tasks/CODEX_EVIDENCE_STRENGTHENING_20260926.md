# Evidence-strengthening audit, 26 September 2026

Authorized by the corresponding author after a critical assessment of the
current R3nR8 editorial candidate. This task does not change the accepted
baseline, overwrite the manuscript, merge a PR, submit to a journal, or send
outreach. Existing public Zenodo v1.0.0 remains immutable.

## Work plan

1. Recover and identify available source-native inputs and prior computational
   archives. Distinguish a reported-result reconstruction from a model rerun.
2. Audit JRC 9/30 and EPA 133/283 and 62/283 at the strongest recoverable level.
   Test displayed-precision robustness without assuming missing unrounded values.
3. Test what reference-uncertainty statements can be justified from the available
   information. Do not invent fitted vectors, covariance, or confidence intervals.
4. Re-read the original Palmer spreadsheets and independently reproduce the
   previously reported Fairbanks joins where possible. Keep originals and
   row-level derivatives private; publish only code and non-sensitive aggregate
   findings with explicit evidence boundaries.
5. Return deterministic tests, source identities, KEEP/HOLD/REMOVE, a reviewer
   report, and a separate review PR/package. Manuscript-facing scientific changes
   remain candidates pending independent review.

## Success criteria for this work unit

Each headline result has a documented provenance and verification status;
every new calculation has tests and stated assumptions; the Fairbanks admission
decision follows the source-universe and independent-marker gates. Missing
evidence is recorded as missing, not imputed. A null finding is acceptable.
