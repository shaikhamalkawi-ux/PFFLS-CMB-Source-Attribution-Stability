# Codex Instructions — PFFLS-CMB

You are working inside the PFFLS/CMB source-attribution-stability research project.

## Non-negotiable scientific rule

Do not optimize for a positive result.

A null result, discordant result, or HOLD is valid.

Do not rewrite the manuscript unless explicitly asked after an evidence gate has passed.

## Locked baseline

Read `PROJECT_STATE.md` before making any scientific change.

The active manuscript baseline is **PFFLS R4.3.30R3nR7-AE**.

## Git workflow

1. Never push speculative scientific changes directly to `main`.
2. Create a descriptive branch:
   - `codex/<task-name>`
3. Preserve all input identities with SHA-256 where possible.
4. Add scripts, tests, derived outputs, and a short audit report.
5. Open a pull request.
6. In the PR body separate:
   - KEEP
   - HOLD
   - REMOVE
   - unresolved evidence
7. Do not merge your own scientific PR unless explicitly authorized.

## Evidence hierarchy

Prefer:
1. original raw / official source;
2. original report tables / machine-readable source;
3. official archive / repository;
4. exact published supplementary data;
5. secondary metadata only for cross-checks.

Never replace an unavailable historical profile with a newer profile and then treat it as identical.

## External validation

Fit quality is not external accuracy.

Do not infer an external-accuracy ranking unless:
- the receptor crosswalk is exact,
- the source-profile choice is frozen,
- the external endpoint is independently measured,
- the mapping from CMB outputs to that endpoint is reproducible from the historical record,
- no post-outcome endmember / denominator / normalization choices are introduced.

## Third-party material

This repository is public.

Do not commit raw third-party PDFs, databases, reports, archives, or proprietary files unless redistribution rights are explicitly verified.

Instead commit:
- retrieval code,
- source URLs,
- hashes,
- parsing code,
- provenance metadata,
- non-infringing derived outputs.

## Reproducibility

For each computational task:
- record Python / package versions;
- make random seeds explicit;
- provide one-command or one-script reproduction where practical;
- fail closed on missing inputs;
- never silently impute;
- test exact-case behavior;
- keep numerical tolerances explicit.

## Current task

See `tasks/CODEX_CYCLE_01.md`.
