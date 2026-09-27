# Post-execution operational correction: Windows path length

The original union configuration was frozen at 2026-09-26T21:00:01.913195Z,
SHA-256 `bba9d04eb6ffb20d55f754cfc4ad4876cb4c92af176aef39044d06ae54100e44`.
The first field model's numerical solver was invoked. Writing its completed
record then failed with `FileNotFoundError` because the long Windows path and
`interval_union_case_<64-character hash>.json` filename exceeded the host's path
limit. No computed result was persisted or displayed. This is **post-execution
operational correction**, not a pre-field change. It is not a numerical failure
and does not justify discarding a scientifically inconvenient outcome.

Root approved an output-path-only repair plus explicit interruption accounting.
The original script, tests, configuration, gate, and candidate manifest are
preserved under `private/decision_research_20260926/interval_union_pre_pathfix/`.
The revised filename is `u_<full64-character model hash>.json`; no hash is
truncated. Before the retry, all476 possible intended case-file paths are rebuilt
without any LP, written with an explicit probe marker, read back, and removed.
The exact probe files were created by this check and contain no user data.

All scientific scope, tuple order, uncertainty fields, sample predicates,
certificate definitions, thresholds, and solver methods are unchanged. A revised
configuration and tests are frozen before the retry. The two-hour budget retains
the original21:00 scientific-freeze clock, which is conservatively earlier than
the actual first solver call; it is not restarted by this repair.

The failed attempt did not persist its solver counter. Its worst-case call count
is bounded by27: one successful base-feasibility call, seven joint co-leader
checks with at most two calls each (primary plus phaseI), and six leader-contrast
bounds with at most two calls each (primary plus cross-check, phaseI, or ray).
Exact rational repairs make no numerical LP calls. An infeasible base instead
takes at most two calls and stops. The retry therefore charges27 calls and one
attempted model against the unchanged20,000-call/476-model ceilings. The report
separates observed retry calls from this conservative unrecorded-call allowance;
it never fabricates an exact count for the lost attempt.

The independent reviewer must compare the preserved v1 and revised v2 code and
configuration before accepting any union claims. Frozen Stage2 and ray/geometry
artifacts are not modified by this correction.
