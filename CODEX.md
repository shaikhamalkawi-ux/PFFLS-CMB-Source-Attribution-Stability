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

The active scientific submission baseline is **PFFLS R4.3.30R3nR8-AE**, as recorded in the later protocol-closure entry of `PROJECT_STATE.md`. The exact R3nR7 source was recovered before that update; the original bridge's missing-source warning is historical, not a current blocker.

Before editing manuscript prose, verify the exact input source and SHA-256. Historical versions in `05_MANUSCRIPT_HISTORY/` are not interchangeable with the active baseline. Prepare a clearly labeled candidate and delta for review; never promote a candidate silently. The 2026-09-25 user-requested author update and Fairbanks independent audit are review candidates, not a new scientific baseline. See `outputs/received_fairbanks/` for the current cohort correction and claim boundaries.

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

Work continuously under `tasks/CODEX_CONTINUOUS_TO_SUBMISSION.md` and GitHub
Issue #9. Read `PROJECT_STATE.md`, open issues/PRs, and the latest Drive returns
before acting.

Cycle 04 is closed and merged through PR #11 after independent correction.
The exact R3nR7-AE artifact/editable source remains unavailable in accessible
storage. R3l remains historical-anchor-only and must never be relabeled as the
baseline.

The missing JRC/EPA raw computational archives remain explicit reproducibility
limitations, but they are **not** a newly created mandatory submission-science
gate. Keep `recomputed_from_raw = false` and never claim full raw-data
reproducibility unless those archives are recovered.

Choose the next highest-value task autonomously. Priority should be given to:
1. authoritative R3nR7-AE manuscript/source recovery or a separately named,
   explicitly authorized reconstruction path if exact recovery proves impossible;
2. final repository DOI/URL and licence;
3. target-journal/package requirements;
4. final author metadata and author-approved declarations;
5. any genuinely new admissible evidence returned through the pending outreach
   channels.

Do not resend Palmer/Ward or Watson/Chow while their requests remain pending.
Do not send the ADEC public-records request without the required user identity
and truthful legal certification.

Open a PR and return a Drive package for each meaningful work unit. Do not
promote or merge a new manuscript baseline without independent review.
