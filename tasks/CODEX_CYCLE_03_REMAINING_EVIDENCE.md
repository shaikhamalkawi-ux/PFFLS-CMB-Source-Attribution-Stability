# CODEX CYCLE 03 — Remaining evidence recovery after external requests

## Context

The user has already sent the two external requests that are most appropriate for human correspondence:

1. Palmer/Ward request for the Fairbanks sample-level levoglucosan / radiocarbon spreadsheet — **SENT / PENDING RESPONSE**.
2. Watson/Chow request for the original NFRAQS CMB-to-fM(CMB) mapping — **SENT / PENDING RESPONSE**.

Do not duplicate those requests unless new evidence identifies a materially different custodian or archive.

The locked manuscript baseline remains:

**PFFLS R4.3.30R3nR7-AE**

Cycle 03 is evidence recovery only. It does not authorize a manuscript revision.

---

# Track A — Recover the original Fairbanks electronic CMB package

## Goal

Recover, from public/official sources if possible, the electronic files behind the Fairbanks CMB analysis.

Priority records:

- EPA-CMB8.2 ambient/receptor input files;
- per-species receptor uncertainty files;
- source-profile files and uncertainties;
- CMB control/input files (including historical *.in8 or equivalent);
- exact source/species selection files;
- final output/database/CSV files;
- files identifying the final fitting species and source profiles used for each sample;
- contractor-delivered ZIP/CD/DVD/electronic appendices;
- any ADEC archival project directory associated with the Ward 2013 final report.

## Search order

Search systematically:

1. Alaska Department of Environmental Conservation (ADEC)
2. ADEC technical appendices / SIP supporting files
3. ADEC public-record / archive indexes
4. EPA NEPIS
5. EPA HERO
6. EPA AQS / AirData supporting records
7. EPA CMB archives
8. University of Montana repositories
9. University of Alaska repositories
10. Internet Archive / Wayback for dead public links
11. archived contractor folders / attachment directories
12. DOI-linked supplements and conference/project pages

Do not use credentials or restricted systems.

## Public-record-request boundary

If the electronic package is not publicly downloadable but a government public-record request is clearly appropriate:

- do NOT submit the request yourself;
- prepare a complete request text for the user;
- identify the correct agency/unit/contact/portal;
- list the exact records requested;
- explain why each requested file is necessary;
- save the draft under:
  `outputs/cycle03/Fairbanks_ADEC_Public_Records_Request_DRAFT.md`

Also prepare a compact one-paragraph version suitable for a web form.

---

# Track B — Screen independent datasets for a complete profile-resolved external-validation case

## Primary candidates

Start with:

### Candidate B1 — Barrow, Alaska 2012–2013
Investigate whether the campaign exposes:
- sample-level receptor chemistry;
- receptor uncertainties;
- numerical source profiles;
- source-profile uncertainties;
- exact source/species selectors;
- CMB implementation details;
- same-sample radiocarbon / other independent source-discriminating reference;
- explicit mapping from CMB output to the independent endpoint;
- at least two frozen alternative profiles within one physical source family.

Search article supplementary files, ACS supporting information, university repositories, Baylor repositories, EPA/agency archives, and archived project pages.

### Candidate B2 — APHH-Beijing
Investigate whether the APHH-Beijing CMB campaign can be linked exactly to the openly deposited radiocarbon data.

Recover if possible:
- receptor chemistry matrix;
- receptor uncertainties;
- numerical source profiles and profile uncertainties;
- exact CMB source/species selectors;
- exact date/sample crosswalk to radiocarbon observations;
- endpoint mapping;
- alternative same-family source profiles.

Search the University of Birmingham data repository, APHH project repositories, article supplements, author repositories, and official project archives.

### Candidate B3 — Chengdu / source-profile-sensitivity dataset
Use this primarily as a source-profile-choice landscape candidate.

Determine whether an independent same-sample external reference exists. If not, keep it as contextual profile-sensitivity evidence only.

## Additional candidates

You may add additional public field campaigns if they appear materially stronger than the three above.

Do not broaden into a generic literature review. Each added campaign must be justified against the exact PFFLS external-validation question.

---

# Admission rule

A candidate becomes KEEP only if all required objects are recovered:

1. receptor vector;
2. receptor uncertainty;
3. numerical source profiles;
4. source-profile uncertainties;
5. exact final species/source selector;
6. sufficient CMB/EVLS implementation detail;
7. independent external reference for the same exact sample/interval;
8. unambiguous mapping from CMB output to the external reference;
9. at least two frozen, prespecified same-family alternative source profiles;
10. present reproducibility.

If any essential object is missing, return HOLD.

Do not:
- infer missing uncertainties;
- invent endmembers or denominators;
- use study averages as sample-level truth;
- relabel species-selection as profile-selection;
- substitute modern profiles for historical ones without identity proof;
- choose profiles after inspecting external-reference outcomes.

---

# If a complete candidate is found

Only then:

1. reproduce the published control;
2. freeze the candidate profile landscape;
3. run the same fit criterion across the prespecified candidates;
4. compute the independent-reference error for each candidate;
5. report:
   - fit-favored profile;
   - externally closest profile;
   - concordant / discordant / tied;
   - external-accuracy regret;
   - exact finite-landscape counts only;
6. implement an independent verification path;
7. add regression tests.

Do not edit the manuscript.

Prepare a separate candidate manuscript delta only after the scientific package is complete.

---

# Deliverables

Create:

- `outputs/cycle03/source_inventory.csv`
- `outputs/cycle03/candidate_dataset_matrix.csv`
- `outputs/cycle03/fairbanks_electronic_package_recovery.csv`
- `outputs/cycle03/external_request_status.csv`
- `outputs/cycle03/KEEP_HOLD_REMOVE.md`
- `outputs/cycle03/admission_report.md`
- `outputs/cycle03/SCIENTIFIC_CHANGELOG.md`
- `outputs/cycle03/EDITORIAL_RECOMMENDATION.md`
- `outputs/cycle03/reproduction.md`
- `outputs/cycle03/artifact_manifest_sha256.csv`

If a public-record request is needed:
- `outputs/cycle03/Fairbanks_ADEC_Public_Records_Request_DRAFT.md`

If new investigator correspondence is needed:
- draft it under `outputs/cycle03/correspondence/`
- do not send it.

If a full external-validation candidate passes:
- add exact input/crosswalk/profile tables;
- machine-readable result JSON;
- clean-room scripts;
- tests;
- control-reproduction tables.

---

# Git / Drive workflow

Use branch:

`codex/cycle-03-remaining-evidence-recovery`

Open a PR when complete.

Do not merge your own PR.

Return the full package to:

`PFFLS_4_CODEX_BRIDGE/02_FROM_CODEX/`

Recommended filename:

`PFFLS_CODEX_CYCLE03_REMAINING_EVIDENCE_RETURN.zip`

Include a SHA-256 sidecar.

---

# Current external-request status

Mark these as pending and do not treat non-response as negative evidence:

- Palmer/Ward sample-level Fairbanks spreadsheet — SENT / PENDING
- Watson/Chow NFRAQS CMB-to-fM mapping request — SENT / PENDING

If either response arrives during Cycle 03, stop and incorporate it only after preserving the original email/file and provenance.

---

# Stop rule

Valid final states:

- **KEEP** — at least one complete reproducible external-validation case is recovered;
- **HOLD** — promising evidence exists but essential objects remain missing;
- **REMOVE** — candidate cannot answer the target question.

No manuscript baseline change is authorized by Cycle 03 itself.
