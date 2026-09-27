# Cold producer: independent static implementation review

Status: **PASS for the reviewed implementation and schema; not field-run
authorization.** A specific run still requires the final synthetic/metadata
gates, an approved immutable preparation manifest, and subsequent independent
replay of every generated proof. No native fit, LP, or field replay was run by
this reviewer for this review.

## Exact scope

The complete producer, complete synthetic-test source, and complete schema were
read, including the final operational changes and added tests. The reused
leader-only inspector, component/union decision rules, and exact Farkas-margin
prerequisites were also inspected. Final file hashes were checked directly:

| File | SHA-256 |
| --- | --- |
| `scripts/reproduce_interval_union.py` | `2f96dd9629ea8093360596506e2b04aff4c40d6839e659f41c35518f20a27bb1` |
| `tests/test_cold_interval_union.py` | `48b211da94a5a4d3c0d3de02f059e1b4175757d9e88fc27e3204c9488ac859f8` |
| `outputs/decision_research_20260926/COLD_RUN_RECORD_SCHEMA.md` | `929e78ded6029bfa2f2130820629277ea89a7919c7724d0b37a020fdc197b710` |

This is a source-level review, not an independent rerun of the test suite. The
final 52-test source includes a small two-source synthetic writer/independent
reader integration test; its runtime gate must be recorded separately. Likewise,
the original-input 4,200-model metadata comparison is a separate gate, not a
new field calculation performed by this reviewer.

## Findings

No remaining blocking implementation defect was identified in the reviewed
scope. In particular:

- The numerical entry point consumes authorized original archives and public,
  hash-pinned dependencies, not historical private cases, target partitions,
  point-fit outputs, or expected outcome totals. Preparation reconstructs all
  35-by-120 model identities without solving. Every chosen profile contributes
  its own means and uncertainties; family labels remain stable.
- Scientific scope remains 35 ordered samples, 20 species, seven families,
  120 actual tuples, k=2 joint independent boxes, nonnegative contributions,
  no mass constraint, no pruning, and the unchanged strict margin. The central
  pass precedes fixed-order remaining tuples. No old 31/2/2 partition is used.
- Every numerical helper call is routed through the patched core solver entry
  point. A call is charged before durable `LP_BEGIN`; failed or pre-dispatch
  aborted attempts retain the charge. Recorded solver invocations and charged
  non-invocations are distinguished. The frozen ceilings cannot be increased
  through the run command.
- A fresh post-flush time gate limits solver allowance. Cooperative time checks
  also cover exact scientific Python work. The schema correctly does not claim
  a hard operating-system deadline for an uninterruptible native operation or
  filesystem write. Record closure is allowed after expiry; further scientific
  work is not.
- An early negative union conclusion requires two distinct exactly witnessed
  co-leaders. A positive conclusion needs all 120 components accounted for,
  at least one exactly nonempty component, and the same strictly above-margin
  leader in every compatible component. An all-infeasible union is labelled
  empty, never a leadership certificate. Missing, interrupted, or unresolved
  evidence remains HOLD.
- The Farkas fallback preserves the original objective results. It requires an
  exact base witness, the winner's joint witness, and all rival exclusions;
  exact residual/sign/row checks precede the gamma/B calculation, and every
  margin must strictly exceed the unchanged delta. It makes no extra LP call.
- Output is exclusively created in a new bounded private child, with symlink
  and junction guards, path-length preflight, unchanged dependency/environment
  checks, and exact approval-hash matching. Existing or populated attempts are
  not resumed. Failed case writes preserve any partial bytes and cannot supply
  a proof. A missing terminal seal remains an incomplete attempt.
- The independent reader's relevant integration logic was additionally checked:
  hash-checked bytes at read time, original-model reconstruction, earlier-witness
  provenance, solver-charge reconciliation, fixed traversal, conservative
  stopped/failed-write handling, and final inventory/dependency rechecks.
  This observation does not replace that reader's own final QA and field replay.

## Operational correction found during review

An earlier candidate computed an LP allowance at admission, then recorded a
later journal timestamp. Comparing that allowance with the later time could
reject a valid run after ordinary scheduling delay. The final candidate records
the exact admission elapsed/UTC samples separately for both LP and model starts;
the independent reader brackets those samples and checks allowances against
them. Dispatch still receives a fresh gate after the durable write. No budget,
scientific parameter, proof requirement, or outcome was relaxed.

The test source covers delayed event recording, expiry after admission,
charged-but-not-invoked calls, restoration after interruption, incomplete and
all-empty unions, missing/equal Farkas margins, failed writes, dependency and
environment drift, alternative-specific uncertainty, mocked containment links,
and actual synthetic writer-to-independent-reader consistency.

## Remaining release/execution gates

This review is valid only for the three exact identities above. A changed file
requires a reviewed diff and renewed relevant tests. The final synchronized
producer/verifier test results, original-input metadata agreement, clean-snapshot
dependency closure, explicit approval of the particular run manifest and time
limits, and independent proof replay remain separate requirements. No historical
result total is an acceptance oracle, and a successful cold reproduction would
not be an independent environmental-data replication, confidence guarantee, or
new discovery.
