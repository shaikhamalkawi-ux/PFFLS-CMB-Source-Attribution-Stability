# PFFLS-CMB Source Attribution Stability

This repository is the computational and audit workspace for the research program:

**Source Attribution Can Change Despite Favorable Fit Diagnostics: Evidence from Source-Profile Choice in Chemical Mass Balance**

## Active scientific baseline

The locked manuscript baseline is:

**PFFLS R4.3.30R3nR7-AE — Field-Data Positioning and Final Editorial Closure**

No manuscript claim, numerical result, source universe, or interpretation should be changed unless a new result passes the project evidence gates and is explicitly authorized for a new manuscript version.

## Research question

A favorable Chemical Mass Balance (CMB) fit does not by itself establish that a comparative source-attribution statement is stable to admissible source-profile choice.

This project separates:

1. **fit quality**, from
2. **claim stability / attribution stability**, and from
3. **external accuracy**.

These are not interchangeable.

## Locked empirical results

### JRC controlled reference-anchored layer
- 364 daily samples
- 38 species
- 12 profile sets
- 30 prespecified one-profile comparisons
- primary lower-mean-reduced-chi-square discordance: **9/30**

### EPA archived field-data layer
- 345 eligible SJVF substitutions
- 323 converged
- 283 preserved the predeclared R² + reduced-chi-square target ranges
- among those 283:
  - 133 source-ordering changes
  - 62 largest-source changes
- stricter 26-case subset also preserving percent mass:
  - 10 ordering changes
  - 2 largest-source changes

The EPA layer is **reference-free field-data sensitivity evidence**, not a field experiment, not external validation, and not evidence that any substituted profile is environmentally correct.

## External-validation branch

The NFRAQS / radiocarbon branch remains **HOLD** for its primary external-accuracy endpoint.

The exact six historical hardwood-woodstove profiles were recovered and the EPA Welby control was reproduced, but the original Chapter 7 mapping from CMB source contributions to the plotted CMB-side contemporary-carbon quantity was not recoverable unambiguously. Therefore no post-hoc carbon weighting, endmember choice, denominator, normalization, or treatment of negative contributions is allowed.

The fit-only winner in that branch is **NWSOWHL**. This is **not** an external-accuracy winner.

Libby remains useful contextual field evidence but is not profile-resolved enough for the same rerun.

## Repository role

This repository is intended for:
- reproducible code,
- tests and numerical audits,
- source/provenance metadata,
- Codex work instructions,
- claim-gate logic,
- approved derived results.

It is **not** a redistribution archive for third-party raw data or reports.

## Data / rights boundary

Do not commit third-party source bytes unless redistribution rights are independently established.

In particular, keep raw EPA/DRI/NFRAQS/SPECIATE source files outside this public repository unless the specific file is verified as redistributable.

Use retrieval scripts, hashes, provenance records, and derived non-infringing outputs instead.

## Codex workflow

Read [CODEX.md](CODEX.md), `PROJECT_STATE.md`, and the active task under
`tasks/` before making changes. Continuous execution is governed by
`tasks/CODEX_CONTINUOUS_TO_SUBMISSION.md` and GitHub Issue #9. The Issue #8
outreach package was merged through PR #10 and Issue #8 is closed; it did not
revise the manuscript, and the ADEC public-records request remains unsent.
Cycle 04 is documented in
`tasks/CODEX_CYCLE_04_SUBMISSION_CANDIDATE_RECONSTRUCTION.md` and
`outputs/cycle04/`. It is a fail-closed baseline-recovery, candidate-delta, and
reproducibility-gate cycle—not authorization to replace the locked manuscript.

Codex should work through branches / pull requests and must never promote a HOLD result into a manuscript claim.

## Current manuscript decision

**NO-GO for a new manuscript version from the NFRAQS external-validation branch.**

Retain **PFFLS R4.3.30R3nR7-AE** until genuinely new admissible science or a real reviewer/editor request justifies reopening the manuscript.

Cycle 04 may produce only a clearly labeled candidate delta and audit package
for independent review; it does not establish a new baseline.
