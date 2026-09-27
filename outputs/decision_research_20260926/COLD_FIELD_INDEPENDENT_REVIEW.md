# Independent review of the completed cold reproduction

Completed 2026-09-26 23:52:21 UTC. **PASS; producer run status COMPLETE.**
The new private result was regenerated from public-input archives, and its saved
mathematical certificates passed a separate independent no-LP replay. This
closes the tested regeneration gap without relying on historical private
ledgers. It does not reproduce historical output bytes, establish environmental
truth, or add independent field observations.

## Frozen identities and execution boundary

- Approved prepared manifest: `a857a7ca962cc1d23b0e6bf9a69a630a12ff46af40fe81734524f162ff07e6cd`.
- Producer terminal manifest: `1d37217328852e137eedad348cff46a0f51d70bcfcbe6dac8341a5cacedbf800`.
- Producer final index: `106dc388df0371296232833f340a21c59b0611f3118657c4533f9da83d03186c`.
- Independent verifier: `0709e1e8ab72b846c124d57c145e438d63f6ad90c80dbf4391ab9548d8057e49`.
- Independent verification record: `5c8417f3fcaecac24a43b8b5ce346c5fb2e71878529d950efcf2bbaf797e2c9d`.

The terminal and index identities were checked before invoking the frozen
snapshot's verifier. The verifier then independently checked original inputs,
model identities, exact proof objects, journal chronology, budgets, coverage
and final file inventory. It checked the actual bytes consumed, not just a
producer PASS flag. Dependency and inventory identities were rechecked after
the replay. The only new file written inside the run directory was the
schema-authorized `independent_verification.json`.

## Independently verified result

All 35 samples, 120 fixed profile tuples and 4,200 exact model definitions were
reconstructed from the four original archives and 39 original members. There
were 161 completed model attempts and 1,720 journaled charged LP attempts;
all 1,720 were recorded as invocation attempts, with zero pre-invocation aborts.
The verifier itself ran zero LPs and read zero historical private ledgers.

The distinction between 4,200 model definitions and 161 solved components is
intentional: exact witnesses permitting two different co-leaders support early
termination of a sample's search. Such negative decisions do not require an
exhaustive contribution range or all 120 component solves. A positive union
decision still requires complete coverage, nonemptiness, a common leader and
strictly sufficient margins in every compatible component.

The independently derived sample classifications were:

- 34: exact witnesses rule out a guaranteed unique leader over the declared
  model/interval union.
- 1: a common unique leader is certified above the unchanged strict numerical
  margin throughout the declared union.
- 0: incomplete/unresolved sample-level HOLDs in this new completed run.

These are not 34 newly observed environmental reversals, nor 34 effects
attributable solely to profile choice. Both receptor and profile intervals are
part of the fixed question. No previous outcome count was used as a validation
oracle.

Exact replay checked 516 primal points, 446 Farkas certificates, 56 dual-bound
records, 489 joint co-leader problems and 312 leader-margin objectives. The
prospectively declared fallback involved 48 components and 288 exact derived
margin bounds. Its independent checks include the base nonempty witness,
same-leader and all-competitor exclusions, correct augmented rows and signs,
positive multiplier sum, exact rational bound arithmetic, and a strict
comparison with the original delta. Original objective results remain saved;
fallback proofs do not rewrite numerical failures as successful LP bounds.

## Scope, chronology and limitations

The question remains 20 species, all seven complete source families, 120 actual
historical tuples per sample, nonnegative contributions, joint boxes at k=2,
no mass constraint and no source pruning. The margin is unchanged:
`delta = (1/10000000) * max(1, TMAC)`. It is a numerical decision threshold,
not a substantive environmental effect-size or confidence threshold.

All three ordered metadata digests match the independently reviewed preparation.
The approved tracked LF recovery-metadata form was used; no other dependency
or original archive pin was weakened. The earlier failed snapshot, original
Stage3 34/HOLD1 record and separate historical post-hoc completion remain
unchanged. The new cold procedure's fallback was informed by those historical
findings; this is not blinded validation or a claim of methodological novelty.

The replay took 48.953 seconds within its independent 1,200-second bound. The
new aggregate verification JSON contains no sample identities, matrices or
proof vectors. Original archives and reconstructive case/journal records remain
private; public release and manuscript integration still require their separate
content and scientific-claims reviews.
