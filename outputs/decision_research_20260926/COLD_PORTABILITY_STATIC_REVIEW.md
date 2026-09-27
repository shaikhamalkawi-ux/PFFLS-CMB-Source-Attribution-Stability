# Cold metadata portability: independent static review

**PASS for the exact corrected source/test/schema identities below.** This is
a narrow implementation review, not permission to run a field model or a claim
that the corrected isolated reproduction has completed. Renewed runtime gates,
LF-snapshot metadata agreement, and exact-manifest execution approval remain
separate requirements. No test suite, native-model reconstruction, fit, or LP
was run by this reviewer for this review.

## Baseline and independently checked diagnosis

The complete root decision was read. The preserved 23-member owner-private
archive was authenticated as SHA-256
`e92755fbf13ab9ee1b1c0dc75a86cfd64a39b39ec6d9e47697b352e3d98f32e6`.
Only public source/metadata members needed for the comparison were read; no
owner-path or failure-log contents are reproduced here.

An independent read-only comparison of its recovery metadata with the exact
Git blob in base `2437750f8223304231ab9afcc9ec4a54956c8d97` confirmed:

- Preserved CRLF: 9,074 bytes, 257 CRLF pairs, SHA-256
  `4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2`.
- Tracked LF: 8,817 bytes, zero CRLF pairs, SHA-256
  `32762085a73ee0b5ad703bc68ab8194303ca0769c49494202343b622e356c0e2`.
- Replacing only CRLF with LF in the preserved bytes reproduces the Git blob
  exactly; independently parsed JSON values are equal.

This comparison diagnoses the two known byte representations. It does not
authorize runtime normalization or acceptance of any third representation.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `scripts/reproduce_interval_union.py` | `070980559bac2c3d7ea02882d47ebbd0a5b502fd39c10e815678faa983b966ac` |
| `tests/test_cold_interval_union.py` | `2d243738470dc01fe18af9bcd91587a7f9c2f317ed3069eff23f4d0352e17319` |
| `scripts/verify_cold_interval_union.py` | `0709e1e8ab72b846c124d57c145e438d63f6ad90c80dbf4391ab9548d8057e49` |
| `tests/test_cold_interval_union_records.py` | `ee5413e360b2410a3f501cc0765511874a6571e920f3ee7d2fb5d5dadb11ad55` |
| `outputs/decision_research_20260926/COLD_RUN_RECORD_SCHEMA.md` | `eac3516951fd6a795ee1e48271a8023f8470d40cc7556d2a0449789237bb9752` |
| `outputs/decision_research_20260926/COLD_PORTABILITY_ROOT_DECISION.md` | `7fede98bd7f789ba8f228667912be15c80e592195b508859c4ca01fecfd8078e` |

The full textual differences against the preserved candidate were read. Among
its 21 repository-public members, exactly the two new adapters, their two test
modules and their schema changed; the other 16 members, including previous QA
and review records and frozen prerequisites, remain byte-identical.

## Findings

No blocking defect was identified in the correction. It is limited to one
declared metadata path and its two exact approved SHA-256 values. Every other
frozen dependency remains exact-byte pinned. The portability decision is itself
pinned, increasing the declared dependency closure from 18 to 19 files.

The producer reads and authenticates recovery bytes once, then supplies that
same immutable payload through a read-only `read_bytes()` adapter to the
unchanged native inventory validator. Its parser therefore cannot reopen an
unchecked replacement. The original archive/member validation and returned
actual recovery hash remain in use. Preparation additionally requires that
hash to equal the dependency-map hash before creating the output directory.
An approved-form switch between checks is rejected, not silently frozen.

The independent reader performs its own exact-two-form check and parses its own
checked payload. Its dependency verifier requires the declared variant map to
match exactly, requires dependency and consumed-input provenance to agree, and
then checks every actual file against the hash named by that particular
manifest. Naming the other allowed form is consequently not sufficient.
The normal input-metadata equality check and final dependency recheck remain.

AST comparisons confirmed that changes to producer functions/classes are
limited to the recovery byte reader/buffer/validator adapter, dependency map,
metadata declaration and the preparation consistency guard. Reader changes
are limited to the dependency-byte helper, original-input reader and dependency
verification. Model construction, scientific parameters, margin proof logic,
solver budgeting, journal state machine, traversal, union conclusions and
case-record verification are unchanged.

The newly read tests cover both approved forms and equal parsed values, a third
semantically equal encoding, changed archive/member identity, same checked
payload versus an unchecked reopen, actual-hash recording, the 19-file closure,
unrelated pins, manifest/actual-form mismatch, mixed provenance, declaration
broadening and a form switch before output creation. These are source-level
coverage observations; final runtime results are reported separately.

## Conditions retained

Keep the first candidate's QA/reviews and failed disposable snapshot as
historical evidence. Do not relabel that attempt as a successful prepare or
discard its failure. The corrected snapshot must use the reviewed Git LF bytes
without editing frozen metadata, and record its actual deployed dependency map.
The original-input sample/tuple/model digests must still be checked without
solving before any separately approved field run. Outcome totals are not an
acceptance oracle. All generated manifests, sample records and proof matrices
remain private pending their distinct reporting/release rules.
