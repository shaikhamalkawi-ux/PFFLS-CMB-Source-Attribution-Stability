# CODEX CYCLE 04 — Audited submission-candidate reconstruction and reproducibility gate

## Authority and objective

This cycle operates under GitHub Issue #9 and
`tasks/CODEX_CONTINUOUS_TO_SUBMISSION.md`. Its purpose is to resolve the most
important internal barrier to a submission-ready paper: the exact locked
R3nR7-AE artifact and the central JRC/EPA computational archive are not present
in the accessible repository or Drive bridge.

The locked baseline remains:

**PFFLS R4.3.30R3nR7-AE — Field-Data Positioning and Final Editorial Closure**

Cycle 04 must not rename an older file as R3nR7-AE, replace the baseline, merge
itself, send an evidence request, or submit the paper.

## Prespecified decision rule

1. Search accessible project storage for the exact R3nR7-AE binary and source.
2. If it is recovered, record its identity before any edit.
3. If it is not recovered, select one hashed historical artifact only as a
   reconstruction anchor.
4. Produce a section-level candidate delta, not a synthetic full manuscript.
5. Mark every central claim as reported-but-not-recomputed unless its exact
   input, code, selector, and row-level output chain is available.
6. Fail closed on any baseline promotion, unsupported validation language,
   silent selector change, or third-party manuscript byte.

The only admissible closing states are:

- `READY_FOR_INDEPENDENT_REVIEW`; or
- `HOLD_WITH_EXACT_BLOCKERS`.

## Locked numerical registry

### JRC controlled reference-anchored layer

- daily samples: 364;
- species: 38;
- frozen profile sets: 12;
- prespecified one-profile comparisons: 30;
- primary lower-mean-reduced-chi-square discordances: 9.

### EPA archived field-data sensitivity layer

- eligible substitutions: 345;
- converged substitutions: 323;
- substitutions preserving the R² and reduced-chi-square target ranges: 283;
- ordering changes among those 283: 133;
- largest-source changes among those 283: 62;
- stricter percent-mass-preserving subset: 26;
- ordering changes in that subset: 10;
- largest-source changes in that subset: 2.

The EPA layer is reference-free field-data sensitivity evidence. It is not a
field experiment, external accuracy validation, or evidence that a substituted
profile is environmentally correct.

## Required outputs

- baseline-search manifest;
- historical-manuscript inventory with SHA-256 identities;
- historical-anchor extraction and render-QA record;
- machine-readable locked-results registry;
- claim-to-evidence traceability matrix;
- reproducibility-gap register;
- lineage decision;
- `CANDIDATE_DELTA_FROM_R3l_NOT_BASELINE.md`;
- submission-readiness matrix;
- KEEP/HOLD/REMOVE decision;
- scientific changelog;
- editorial recommendation;
- reproduction instructions;
- fail-closed validator and tests;
- allowlisted deterministic package builder;
- QA report, test record, artifact manifest, ZIP, and ZIP SHA-256 sidecar.

## Package boundary

The public repository and return ZIP may contain metadata, hashes, derived
audits, code, and tests. They must not contain historical manuscript PDFs,
private/restricted source files, or a file presented as the missing baseline.

The complete return package belongs in Drive `02_FROM_CODEX/`. A pull request
must be opened for independent review and must not be merged by Codex.

## Outreach boundary

- Palmer/Ward: preserve `USER-REPORTED SENT / PENDING — UNVERIFIED`; do not
  resend.
- Watson/Chow: preserve `USER-REPORTED SENT / PENDING — UNVERIFIED`; do not
  resend.
- ADEC: preserve `DRAFT ONLY / NOT SENT`; do not submit.
