# Interval implementation corrections before field interpretation

The scientific protocol and input/threshold configuration remain unchanged:
`interval_configuration.json`, SHA-256
`9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a`.

## Independent pre-field review

The first Stage 1 pass contained 26 synthetic tests. Independent review requested
two additional protocol-coverage tests: explicit projected-versus-lifted LP
comparisons and a nominal-zero-source removal counterexample. These were added;
the updated Stage 1 passed 28 tests. No field LP had run before this gate.

After the first Stage 2 process was launched, the independent reviewer identified
a conservative classification defect using a synthetic example: if A >= 2 and
0 <= B <= 1, then A-B >= 1 even though A-B is unbounded above. Requiring both
one-sided optimization runs to be bounded/verified unnecessarily withheld the
valid strict A>B certificate.

The Stage 2 process was interrupted before any field result was inspected.
Read-only checks after interruption found no `interval_cases`, progress, index,
result, or report output to preserve; the code creates the case directory before
its first field solve. The pre-correction script, tests, and 28-test Stage 1 record
were copied to ignored private `interval_precorrection_*` /
`interval_stage1_precorrection.json` files.

The logical gate was corrected to use the relevant one-sided verified bound and
its exactly feasible witness. An unbounded opposite direction no longer blocks
that implication. A new adversarial test covers both A>B and the symmetric B>A
case. This is an independently identified implementation correction, not a
field-result-driven choice of uncertainty settings, data, or thresholds.

The current script and tests must pass Stage 1 again before Stage 2 is restarted.
The final result records their exact hashes and the successful gate. This file
does not assert a new mathematical theorem or any field outcome.
