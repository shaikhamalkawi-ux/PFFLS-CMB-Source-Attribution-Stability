# Cold interval-union records: schema v1

Implementation contract, not a field-run approval or a new scientific result.
The root decision permits implementation and synthetic/metadata-only QA first.
All generated run records described here are **private**, including matrices,
sample identities, proof vectors and per-sample outcomes. This document contains
field names and rules only, not native data.

## Fixed question and bytes

All 35 original ordered Fresno/FINE samples; the original 20 species; all seven
source-family slots; the 120 actual historical profile tuples, central first;
k=2 independent receptor/profile boxes; nonnegative contributions; no mass band,
composition constraint, fitted-source pruning or outcome-dependent selection.
The strict margin is `Fraction(1, 10000000) * max(1, TMAC)`.

Canonical JSON bytes throughout this new schema are UTF-8, `ensure_ascii=False`,
`allow_nan=False`, `sort_keys=True`, `indent=2`, followed by one newline.
Fractions are strings (`str(Fraction)`); tuple/list values become JSON arrays.
SHA-256 identifiers always refer to exact bytes. JSONL events use the same
primitive encoding but compact separators and one complete JSON object per line.
No old private ledger, partition, case record, freeze or result total is an input.

## Directory and modes

The explicit `--output` is a new, absent direct child of the repository's
`private` directory. It must not overlap the input directory, contain symlinked
ancestors, or exceed the declared safe full-path length. The writer never
overwrites, resumes, or adopts an existing arbitrary directory.

`--prepare` verifies inputs, code identities and metadata, reconstructs model
hashes **without any LP**, and exclusively creates:

- `manifest.json`: immutable pre-solve scientific/operational/input/code freeze.
- `preflight.json`: path/write checks and metadata-only counts/digests.
- `cases/`: initially empty, for new immutable records.

`--run` accepts only that prepared layout, exact unchanged code/input identities,
and `--approved-manifest-sha256`. Supplying this hash is the explicit execution
acknowledgment after external review; preparation is not execution approval.
It exclusively creates `run_started.json`, `events.jsonl`, cases, `index.json`
and finally `output_manifest.json`. There is no resume mode. An interrupted
directory remains evidence of an incomplete attempt and must not be reused.

## Pre-solve manifest

Top-level keys:

- `schema`: `cold_interval_union_v1`; `run_id`; `created_utc`.
- `output_relative`: the fixed new repository-relative private directory. Moving
  an approved prepared layout is not implicit approval for a new location.
- `scientific`: fixed constants, family/label mapping, species, central slots,
  source selectors, receptor selector and exact margin convention.
- `budgets`: `max_models` (at most 4200), `max_lp_calls` (at most 20000),
  `elapsed_seconds` (at most 7200), optional timezone-aware `deadline_utc`.
  Relative elapsed time starts when the numerical run starts, not at prepare.
  A deadline is operational and never a permanently embedded historical date.
- `dependencies`: repository-relative file-to-SHA256 map for frozen native/core/
  union/Farkas code, public grid/recovery inputs, approved proposal/decision,
  the portability decision, and new producer, verifier, tests and this schema.
  There are 19 files in the approved portability candidate's closure.
- `approved_dependency_byte_variants`: maps only
  `outputs/strengthening_20260926/source_recovery.json` to the ordered two-hash
  array CRLF `4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2`,
  then Git LF `32762085a73ee0b5ad703bc68ab8194303ca0769c49494202343b622e356c0e2`.
  These are the 9074/8817-byte identities proved equivalent in the separate
  portability decision. No general newline/JSON normalization is accepted.
  The dependency map and input recovery provenance record the **actual** bytes
  used; naming the other approved form does not satisfy that per-run pin.
- `environment`: Python, NumPy, SciPy and platform identities.
- `inputs`: verified archive/member inventory, verification counts and selector/
  descriptor metadata; no archive extraction or archive-controlled output path.
- `samples`: 35 `{sample_index, identity}` records in original order.
- `tuples`: 120 lists of seven source-profile names in frozen Cartesian order.
- `models`: 4200 `{sample_index, tuple_index, model_key, model_sha256, case_file}`
  descriptors in sample-major/tuple-minor order. `model_key` is `s00_t000` style;
  `case_file` is `cases/m_00_000_<first12-model-sha>.json`. Indices make filenames
  unique even if numerical model bytes happen to agree. No cross-case caching.
- `metadata_digests`: `sample_order_sha256`, `tuple_order_sha256`,
  `ordered_model_sha256` (canonical list of all full model hashes).

`model_sha256` is the canonical hash of the exact model generated from the
complete chosen profile records (means **and** uncertainties), with the core
model's `sources` replaced by that chosen tuple. Models retain stable family
`names`, original exact decimal arithmetic and justified upper-bound provenance.
The independent reader reconstructs this itself; it does not import the producer
or trust stored matrices.

Recovery JSON parsing consumes already hash-checked bytes. The producer supplies
those bytes through an in-memory `read_bytes()` adapter to the unchanged native
inventory validator; the independent reader checks and parses its own payload.
Neither route reopens an unchecked recovery file after validating its identity.
All archive/member hashes and every other dependency pin remain unchanged.
Preparation also requires the dependency-map recovery hash to equal the input
recovery-provenance hash before creating the run directory; an approved-form
switch between those checks is rejected, not recorded as a mixed-byte freeze.

## Event journal and budget accounting

Every event has `seq` (zero-based consecutive), `event`, `utc`, `elapsed_seconds`,
`models_started`, `lp_calls`, and `model_key` (null outside a model).

- `RUN_START`, `MODEL_BEGIN`, `MODEL_END`, `RUN_STOP`, `RUN_END` delimit work.
- `MODEL_BEGIN` records `admission_gate_elapsed_seconds` and
  `admission_gate_utc` from the time check which admitted that model.
- `LP_BEGIN` adds `call_id` (one-based consecutive), `method` and
  `remaining_seconds`, plus `admission_gate_elapsed_seconds` and
  `admission_gate_utc` from the same check which computed that allowance;
  its incremented `lp_calls` is durably flushed **before**
  invoking the solver. Remaining time is recomputed after that flush, immediately
  before dispatch; the solver receives no more than the fresh allowance.
- `LP_END` has the same `call_id`, integer `solver_status`,
  `invocation_attempted=true`, `dispatch_gate_elapsed_seconds`, `dispatch_gate_utc`,
  `dispatch_remaining_seconds`, and `solver_time_limit_seconds`.
  The elapsed/UTC samples are exactly those used in that dispatch gate, not a
  later timestamp sampled after computing its remaining allowance.
  Event timestamps are later observations and may include scheduling delay;
  admission/dispatch allowances are checked against their own gate samples,
  never against a later event sample with an artificially widened tolerance.
- `LP_ERROR` has the same `call_id` and exception category, without removing its
  charge. Its `invocation_attempted` and `charged_but_not_invoked` flags distinguish
  a failed dispatch from a post-flush/pre-dispatch abort. Dispatch fields are
  present only if a dispatch gate succeeded. A BEGIN without END/ERROR remains a
  charged incomplete attempt, not evidence that an actual solver started.
- `RUN_STOP` records an explicit `reason`, including elapsed/deadline/LP/model
  exhaustion, interruption or error. A stop is never permission to extend limits.

The journal is created once with exclusive creation and retained through one
append-only handle. Each complete event is flushed/fsynced. A partial final
line, missing terminal manifest or interrupted case cannot support a completed
run claim. Every helper, cross-check and failed LP passes through the same budget
wrapper. A budget exception is not a RuntimeError swallowed by the frozen core.
Exact arithmetic has explicit elapsed/deadline checks in addition to LP limits.
The cooperative Python-line guard applies only to scientific computation, not
record closure or durable journal writes. A single native-library operation or
filesystem write is not forcibly interrupted; no hard operating-system timeout
claim is made. No further scientific work starts after the next budget check.
Recording/closing an expired attempt may take additional non-numerical time.

## Immutable case record

Each attempted sample/tuple has at most one case file, with:

- `schema`, `run_id`, `manifest_sha256`, `sample_index`, `tuple_index`,
  `model_key`, `model_sha256`, and the complete exact rational `model`.
- `completion`: `COMPLETE`, `STOPPED`, or `ERROR`.
- `result`: the unchanged dictionary returned by the frozen leader-only
  `inspect_model(model, prior_possible)` routine. If it did not return, null;
  the missing partial result cannot certify anything.
- `prior_possible`: sorted earlier witnessed family names for that sample.
- `farkas_completion`: null, or the exact encoded return value of frozen
  `component_margins(model, result, delta)`; an insufficient/equal result remains
  stored. Original objective failures are never removed or relabelled.
- `farkas_attempt`: `NOT_ATTEMPTED`, `DERIVED`, or `ERROR`; `farkas_reason` states
  why it was ineligible, unnecessary, interrupted or invalid.
- `description`: `{status, possible, unique, exhaustive_model_decisions,
  margin_route}`. `margin_route` is null, `OBJECTIVE`, or `FARKAS`.
- `calls_before`, `calls_after`, `event_seq_begin`, `event_seq_end`, plus optional
  `stop_reason`/`error_category`. No exception repairs or outcome-driven retries.

The original objective route qualifies only under the frozen exact checks.
The Farkas route is attempted only when that route is insufficient and the base
is exactly nonempty, all seven co-leader questions are present, exactly one W
is exactly witnessed, and all six rivals have saved exact exclusions. Its
output must establish nonnegative residual, gamma>0, B>0, and **all six**
gamma/B strictly above the unchanged delta. Invalid premises cannot promote a
description; equality or insufficient margin remains HOLD. No multiplier search
or additional LP is performed for the fallback.

STOPPED/ERROR cases have a conservative unresolved description and no positive
decision regardless of partial work. Such cases still count as attempted and
their solver charges remain in the journal.

Canonical JSON alphabetizes object keys, including `result.co_leaders`. The
independent verifier first requires its key set to match the fixed model-name
prefix, then restores that traversal order in a copy before invoking the frozen
validator. The original result bytes stay unchanged. `description.possible` is
an ordered list and retains original traversal order without normalization.

## Index and union conclusions

The run first visits the central tuple for all 35 samples, then each remaining
sample's tuples 1..119 in frozen order. A sample stops early only after two
distinct exact family co-leader witnesses. No old target partition is consulted.

`index.json` contains `schema`, `run_id`, `manifest_sha256`, `run_status`,
`stop_reason`, start/completion UTC times, `budget`, and all 35 `samples`.
Each sample has `sample_index`, ordered `visits`, `unvisited_tuple_indices`, and
`conclusion`. Each visit contains `tuple_index`, `model_key`, `case_file`,
`case_sha256`, `case_write_complete`, `completion`, and `description`. Missing/unvisited samples remain
explicit even if a global stop occurs before their first model.
On a case-file write failure, the visit has `case_write_complete=false`, null
hash, `completion=ERROR` and an unresolved description; any partial bytes remain
untouched and inventoried. This is never a proof. A terminal journal-write or
filesystem failure may prevent final sealing entirely; such a directory remains
unverified incomplete, not a completed run or a silently repaired one.

`budget` includes `models_started`, `lp_calls`, `elapsed_seconds`, `max_models`,
`max_lp_calls`, `elapsed_limit_seconds`, `deadline_utc`, `lp_counter_semantics`,
`solver_invocation_attempts`, and `precall_aborted`. The exact counter label is
`charged attempts, including explicit pre-invocation aborts`; the last two
counters distinguish invoked from conservatively charged-but-not-invoked work.
The run status is one of `COMPLETE`, `COMPLETE_WITH_HOLDS`, `STOPPED_BUDGET`,
`STOPPED_INTERRUPT`, or `STOPPED_ERROR`.

Conclusions use the frozen union vocabulary:

- `EXACT_NO_GUARANTEED_UNIQUE_UNION_LEADER`: two exact distinct witnesses.
- `EXACT_EMPTY_UNION`: all 120 components exactly infeasible, not a leader.
- `VERIFIED_UNIQUE_UNION_LEADER_ABOVE_FIXED_MARGIN`: all 120 accounted for,
  at least one nonempty, all other components exactly infeasible, and the same
  above-delta W in every nonempty component.
- `HOLD_INCOMPLETE_OR_UNRESOLVED_UNION`: every other state.

The conclusion also records systems visited/universe, possible-leader lower
bound, unique leader or null, and false flags for complete contribution ranges
or a full possible-leader-set claim. `run_status` distinguishes completed
enumeration/early proof stopping from budget/interruption/error closure; it does
not turn unresolved conclusions into successes. No comparison with historical
totals is an acceptance gate.

## Terminal freeze and independent replay

`output_manifest.json` is written exclusively last, with `schema`, `run_id`,
`manifest_sha256`, `run_status`, `files` (relative path, byte length, SHA256),
and final budget counters. It inventories every run file except itself and a
later independent verification output; no unlisted extra file is silently read.

The independent verifier takes explicit `--inputs` and `--run-directory`, never
imports the new producer/tuple builder, and never opens old private records.
It checks original archive/selector/descriptor order, reconstructs every model,
checks all exact saved proofs, independently rederives any Farkas completion,
reconciles the event budget/order, and rebuilds all 35 conclusions. It performs
no LP, fit or numerical proof search, and has a separate declared replay time
limit. A producer result is not independently verified until this replay passes.
Incomplete/interrupted artifacts must remain labelled incomplete; they must not
be resumed, silently repaired, or presented as matching historical proof bytes.

## Invocation and clean-snapshot boundary

The producer derives its repository root from its own installed script location.
It therefore supports a new short-path snapshot containing only the public code,
tests and hash-pinned public dependency files. `--inputs` may point to the four
authorized original archives outside that snapshot; no old private directory or
ledger is copied or needed. Python 3.12 or later is required for junction checks;
Python, NumPy, SciPy and platform versions are recorded at prepare and must match
at run. The exact frozen source hashes remain authoritative.

Input-free and synthetic QA (the synthetic LPs are not native field fits):

```text
python -m unittest discover -s tests -p test_cold_interval_union.py -v
python -m unittest discover -s tests -p test_cold_interval_union_records.py -v
```

Original-input metadata-only checks reconstruct all 4,200 models without LPs:

```text
python scripts/reproduce_interval_union.py --metadata-only --inputs ARCHIVE_DIRECTORY
```

Preparation requires an explicit new `SNAPSHOT/private/RUN_NAME` output and does
not execute a field model. Operational ceilings may be lowered but not increased
past the schema maxima. An optional `--deadline-utc` must include its timezone.

```text
python scripts/reproduce_interval_union.py --prepare --inputs ARCHIVE_DIRECTORY --output NEW_PRIVATE_DIRECTORY --max-models 4200 --max-lp-calls 20000 --elapsed-seconds 7200
```

Only after separate code/metadata review and explicit approval of the returned
manifest hash can that exact prepared run be executed. No resource override is
accepted by `--run`, and no existing/populated output is resumed:

```text
python scripts/reproduce_interval_union.py --run --inputs ARCHIVE_DIRECTORY --output PREPARED_PRIVATE_DIRECTORY --approved-manifest-sha256 APPROVED_SHA256
```

The independent verifier's separately documented invocation is the next gate;
the producer never self-declares an independent replay pass. A new run is a
reproduction of the fixed model question, not an independent environmental-data
replication or a blinded new discovery. The fallback specification was informed
by the known historical result and is prospective only for this new run.
