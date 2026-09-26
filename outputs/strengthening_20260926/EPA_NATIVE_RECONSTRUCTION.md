# EPA native-input clean-room reconstruction — 26 September 2026

## Result and limits

Worked Fresno 10 May 1989: all five central/MOVES runs reproduce all four
published numeric values to six decimal places and the reported largest-source
category: **True**.
Full-run status: **RECONSTRUCTED_MATCH**.

This executes an independently written Python float64 EVLS reconstruction on
newly recovered official EPA input files. It does not execute the original EPA
float32 Fortran/Delphi software, recover the historical original ledger, establish
environmental accuracy, or alter the active manuscript baseline. A successful
result is source-native clean-room numerical reconstruction, not merely checking
publication-summary arithmetic. PACS is inventoried but not numerically audited here.

## Configuration frozen before fitting

Configuration SHA-256: `6d3b10b2090526e3f15e987cc1b796fb02736570e2b3284738001956cacadc39`.
The private freeze record is written and checked before fitting; a changed
configuration is rejected. No profiles, species, tolerances or solver settings
were selected to improve agreement with the reported results. Targets were
already known from the task and manuscript, so this is not a blinded replication.

Native `PRsjvf.sel` array 3 supplies SOIL03, BAMAJC, SFCRUC, MOVES2, AMSUL,
AMNIT and NANO3. Native `SPsjvf.sel` arrays 2 and 4 are identical and provide
20 fitting species. The complete FRESNO/FINE receptor filter gives 35 unique
24-hour samples. Native descriptors independently regenerate all ten declared
alternatives, including PAVED ROAD with UNPAVED excluded.

EVLS starts from zero; uses released receptor and profile uncertainties without
rescaling; allows 20 solves; and stops when every nonzero new contribution changes
by at most 1% relative to its new value. Diagnostics use the weights of the last
solve. Central fits sequentially remove the most negative source after a converged
fit and restart; alternatives retain the final central source set, substituting
only the declared profile and recomputing effective weights. Unconverged
alternatives are excluded from allocation outcomes rather than imputed.

Official `sourcecmb82.zip` / `EPA-CMB82DLLsrc.zip` / `CMB82a.for` was inspected:
lines 542–545 initialize contributions to zero; 623–632 form effective variance;
724–736 use new-contribution relative stopping; 1004–1025 compute diagnostics.
The legacy implementation's undefined exact-zero stopping corner is not copied:
an unchanged exact zero passes and a changed-to-zero contribution fails the
relative test. No profile renormalization, forced nonnegative alternative fit,
extra species, covariance or accuracy reference is introduced.

## Worked-case check

| Run | Converged | Four values match at six decimals | Largest source matches |
|---|---|---|---|
| MOVES2 | True | True | True |
| MOVES1 | True | True | True |
| MOVES3 | True | True | True |
| MOVES4 | True | True | True |
| MOVES5 | True | True | True |

The four quantities are MOVES contribution, R-squared, reduced chi-square and
percent mass. Full calculated values, signed differences and input SHA-256
identities are recorded in `epa_native_reconstruction.json`. The central retained
sources are SOIL03, BAMAJC, MOVES2, AMSUL, AMNIT, NANO3.

## Aggregate comparison

| Quantity | Native clean-room | Manuscript | Difference |
|---|---:|---:|---:|
| eligible | 345 | 345 | 0 |
| converged | 323 | 323 | 0 |
| nonconverged | 22 | 22 | 0 |
| two_diagnostic | 283 | 283 | 0 |
| three_diagnostic | 26 | 26 | 0 |
| ordering_converged | 167 | 167 | 0 |
| largest_converged | 81 | 81 | 0 |
| ordering_two_diagnostic | 133 | 133 | 0 |
| largest_two_diagnostic | 62 | 62 | 0 |
| ordering_three_diagnostic | 10 | 10 | 0 |
| largest_three_diagnostic | 2 | 2 | 0 |

Pairwise and largest-source decisions changing after five-decimal rounding:
**0**.
Converged runs with a top-source tie before or after rounding:
**0**.
All alternative-specific eligibility/convergence counts are retained in the JSON.

The full private ledger retains unrounded contributions, convergence histories,
source-removal decisions, every eligible substitution, complete pairwise changes,
subset masks and the five-decimal ranking check. Its SHA-256 is
`0e3c5c5b74e5f0838a95459ad348de6b49213be0898ff9627915e645881afa9f`. It is not copied to the public return package.
No negative or discordant reconstruction result is hidden.

## Reproduce

```text
python scripts/audit_epa_native_strengthening.py --inputs <official-EPA-archive-directory>
python -m unittest discover -s tests -p test_epa_native_strengthening.py -v
```

Required archives: `sjvf_data.zip`, `pacs_data.zip`, `epa-cmb82test.zip`,
`sourcecmb82.zip`. Exact ZIP and member hashes are in the JSON inventory.
All four archive identities and all 39
member identities are checked against the independent `source_recovery.json`
record before fitting. Configuration and implementing-script hashes are public.
Validated with Python 3.12.14 and NumPy 2.3.5.
Tests of native inputs skip explicitly if these
third-party archives are unavailable; synthetic solver tests remain runnable.
Raw archives remain outside the repository; full row-level derived results stay
under the ignored private directory. Redistribution rights are not inferred.
