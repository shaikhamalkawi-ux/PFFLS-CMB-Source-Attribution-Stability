# Verified limit of the three existing extra tracers

Disposition: **KEEP the narrow structural result; no augmented field experiment.**

A separately implemented, original-input metadata replay completed on
2026-09-26 at 23:12:38 UTC. It checked the SJVF archive and both native text
members before parsing them, used explicit concentration/uncertainty field
mappings and exact decimal comparisons, and did not import the original
checker, numerical solvers or historical private records. Seven synthetic
tests passed. A separate static reviewer inspected the complete new code,
tests and output without claiming a second archive execution.

At the already specified multiplier k=3, all 15 added lower coefficients
for SUXC/CUXC/ZNXC across MOVES1–MOVES5 are zero. Four of the five vehicle
profiles also have an all-zero vehicle lower column in the original 20
species. Therefore 96 of the 120 historical **input systems** retain that
column after adding all three tracers. This is not a count of compatible
systems: augmented compatibility was not computed.

For nonnegative contributions and independent coefficient boxes, write the
constraints as `Ls <= c_upper` and `-Us <= -c_lower`. If the vehicle column of
L is zero and U is nonnegative, increasing only that contribution follows a
recession direction from any feasible point. Changing receptor precision
changes the right-hand sides, not that direction. Added observations could
instead remove the entire branch; this replay does not test such exclusion.

The useful stop rule is specific: do not promise that these existing tracers
will bound this vehicle direction under the unchanged boxes. A justified
positive lower source abundance or finite mass upper constraint could block
it, but neither boundedness nor improved assay precision by itself establishes
a unique leader. Other tracer benefits remain possible and untested.

This is post-outcome verification of a recorded negative result, not held-out
validation, a new theorem, a confidence statement or a reason to narrow the
uncertainty assumptions after seeing the result. The original draft and its
private exact-value ledger are unchanged.

Reproduction: `python scripts/verify_tracer_recession_metadata.py --inputs
<original-EPA-archive-directory> --output <new-output.json>`. Output creation is
exclusive. See `tracer_recession_independent_verification.json` for aggregate
results and archive/code/test hashes. The script and synthetic tests are
`scripts/verify_tracer_recession_metadata.py` and
`tests/test_tracer_recession_metadata.py`; no raw values are distributed here.
