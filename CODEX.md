# Codex Instructions — PFFLS-CMB

You are working inside the PFFLS/CMB source-attribution-stability research project.

## User authorization

The user has explicitly authorized you to do the computational and research work you judge scientifically appropriate to strengthen and complete this project.

You may:
- inspect the Google Drive bridge and the GitHub repository;
- search public/official papers, datasets, reports, archives, and supplementary material;
- write and run retrieval/parsing/reproduction code;
- perform independent clean-room calculations;
- add tests and adversarial/falsification checks;
- recover field/external-validation evidence;
- propose scientifically justified new analyses;
- prepare a **candidate manuscript revision**, supplement, figures/tables, code package, and reproducibility package.

This authorization does **not** permit silent changes to the locked scientific record.

## Google Drive bridge

Use this Drive folder for the full project workspace and large/full return packages:

https://drive.google.com/drive/folders/1PAkw7SDbEU951HcThwr4QRb87IM1T1xD

Important folders:
- `00_ACTIVE_BASELINE/` — active-baseline pointer and, if recovered, the exact active manuscript/source package;
- `01_TO_CODEX/` — master handoff and task instructions;
- `02_FROM_CODEX/` — put complete Codex return packages here;
- `03_EXTERNAL_VALIDATION/` — final reviewed NFRAQS dossier;
- `04_PROJECT_STATE/` — current state, changelog, handoff;
- `05_MANUSCRIPT_HISTORY/` — historical manuscript versions for reference only;
- `06_CODE_EXECUTION/` — execution/Colab artifacts;
- `07_RESEARCH_REVIEWS/` — prior research/reviewer analyses;
- `99_ARCHIVE/` — superseded material.

Read `01_TO_CODEX/PFFLS_CODEX_MASTER_HANDOFF_20260920.md` first.

## Non-negotiable scientific rule

Do not optimize for a positive result.

A null result, discordant result, or HOLD is valid.

## Locked baseline

Read `PROJECT_STATE.md` before making any scientific change.

The active manuscript baseline is **PFFLS R4.3.30R3nR7-AE**.

The exact R3nR7-AE manuscript/supplement binary was not available when the Drive bridge was assembled. Historical versions in `05_MANUSCRIPT_HISTORY/` are **not** the active baseline.

Before editing manuscript prose:
1. search accessible Drive/project storage for the exact R3nR7-AE manuscript/source package;
2. if found, copy it into `00_ACTIVE_BASELINE/` and record its SHA-256;
3. if not found, do **not** silently treat an older manuscript as R3nR7-AE;
4. you may still prepare a clearly labeled candidate reconstruction or exact patch/delta for editor review.

## Git workflow

1. Never push speculative scientific changes directly to `main`.
2. Create a descriptive branch, e.g. `codex/<task-name>`.
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
- the receptor crosswalk is exact;
- the source-profile choice is frozen;
- the external endpoint is independently measured;
- the mapping from CMB outputs to that endpoint is reproducible from the historical record;
- no post-outcome endmember / denominator / normalization choices are introduced.

NFRAQS remains HOLD for the primary profile-resolved radiocarbon endpoint. NWSOWHL is a fit-only winner, not an externally validated winner.

## Third-party material

This repository is public.

Do not commit raw third-party PDFs, databases, reports, archives, or proprietary files unless redistribution rights are explicitly verified.

Instead commit:
- retrieval code;
- source URLs;
- hashes;
- parsing code;
- provenance metadata;
- non-infringing derived outputs.

Full private/restricted working packages belong in the Google Drive bridge, not this public repository.

## Reproducibility

For each computational task:
- record Python / package versions;
- make random seeds explicit;
- provide one-command or one-script reproduction where practical;
- fail closed on missing inputs;
- never silently impute;
- test exact-case behavior;
- keep numerical tolerances explicit.

## Current mandate

Work under `tasks/CODEX_CONTINUOUS_TO_SUBMISSION.md` and GitHub Issue #9. Read
`PROJECT_STATE.md`, the active Cycle 04 task, open issues/PRs, and the latest
Drive returns before acting.

The current highest-value task is a fail-closed submission-candidate
reconstruction and reproducibility gate. Search accessible storage for the
exact R3nR7-AE artifact first. If it remains unavailable, do not rename or
silently substitute an older manuscript; use the best-supported historical
version only as a hashed reconstruction anchor and return a clearly labeled
candidate delta for independent review. Preserve every locked result and claim
boundary. Mark central results as not independently recomputed wherever their
exact computational archive is absent.

PR #10 is merged and Issue #8 is closed. Do not resend the Palmer/Ward or
Watson/Chow requests, and do not send the ADEC public-records request. Open a PR
for Cycle 04, upload its full return package and SHA-256 sidecar to
`02_FROM_CODEX/`, and do not merge or promote a new baseline.
