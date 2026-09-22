# PFFLS 4 — Project State

## Locked baseline
**PFFLS R4.3.30R3nR7-AE — Field-Data Positioning and Final Editorial Closure**

Title:
**Source Attribution Can Change Despite Favorable Fit Diagnostics: Evidence from Source-Profile Choice in Chemical Mass Balance**

## Scientific lock

### JRC
- 364 daily samples
- 38 species
- 12 profile sets
- 30 prespecified one-profile comparisons
- primary lower-mean-reduced-chi-square discordance = **9/30**

### EPA field-data sensitivity
- eligible substitutions = **345**
- converged = **323**
- preserving R² + reduced-chi-square target ranges = **283**
- ordering changes within those 283 = **133**
- largest-source changes within those 283 = **62**
- stricter percent-mass-preserving subset = **26**
- ordering changes in strict subset = **10**
- largest-source changes in strict subset = **2**

## Claim boundary
- Do **not** call the EPA layer a field experiment.
- Do **not** call it external validation.
- Do **not** infer which profile is environmentally correct.
- Do **not** alter the 12-set / 30-comparison JRC universe.
- Do **not** add post-hoc profiles or selectors.

## NFRAQS external-validation branch
Status: **HOLD for primary external-accuracy endpoint**

KEEP:
- six historical hardwood-woodstove profile vectors recovered
- 6 × 121 abundance / one-sigma uncertainty pairs, no imputation
- Welby control clean-room reproduction
- NWSOWHL = fit-only winner
- exact Welby/NIST same-sample interval crosswalk confirmed

HOLD:
- profile-resolved radiocarbon external-accuracy ranking
- any claim that NWSOWHL is externally more accurate
- Libby profile-resolved rerun

Reason:
the original CMB-to-fM(CMB) mapping underlying Chapter 7 was not recovered unambiguously.

## Cycle 01 closure

Cycle 01 external field-validation audit was independently reviewed, corrected, and merged through PR #3.

Final campaign-level decision:
- KEEP campaigns: 0
- HOLD campaigns: 6
- REMOVE campaigns: 1
- overall decision: **HOLD / NO-GO for manuscript revision**

## Cycle 02 closure — Fairbanks

Cycle 02 Fairbanks evidence recovery was independently reviewed and merged through PR #5.

Verified return package:
`PFFLS_CODEX_CYCLE02_FAIRBANKS_RETURN_20260920.zip`

SHA-256:
`bd329dc222f80a864f95c4354a159e7ffd852975f9af2d0b54fc4bbf043a2e85`

QA:
- ZIP integrity PASS
- internal artifact manifest 18/18 PASS
- Cycle 02 tests 4/4 PASS
- repository tests 9/9 PASS

Recovered evidence:
- 294 Appendix C daily CMB rows;
- 107 exact EPA/OMNI site-date pairs;
- 94 pairs valid in both systems;
- 47 State Building AQS/SASS mass links matching Appendix C at displayed precision;
- partial State Building receptor chemistry recovery;
- nine numerical OMNI profiles, including four residential-wood profiles.

Scientific decision:
**HOLD / NO-GO for manuscript revision.**

Why:
EPA-versus-OMNI does not isolate source-profile choice because the source universe changes, including No. 2 fuel oil and vehicle treatment. The public record also lacks the exact per-sample receptor-uncertainty vectors, final selectors, sample-level radiocarbon/levoglucosan crosswalk, and complete reproducible control required by the admission protocol.

Fairbanks is retained as a strong profile-system sensitivity / provenance case, not as external validation of the fit-favored profile.

## Cycle 03 closure — remaining evidence recovery

Cycle 03 is complete on branch `codex/cycle-03-remaining-evidence-recovery`.

Verified return package:
`PFFLS_CODEX_CYCLE03_REMAINING_EVIDENCE_RETURN.zip`

SHA-256:
`bdab2d54d04ae8d9f20e15792d956562bfa12e0124d7c4456b3f41b0b5b2b4e7`

QA:

- deterministic ZIP hash across two independent builds: PASS;
- ZIP integrity: PASS;
- internal artifact manifest: 20/20 PASS;
- repository tests: 17/17 PASS.

Candidate decision:

- KEEP: 0;
- HOLD: 3 — Fairbanks 2011/2012, Barrow 2012/2013, APHH-Beijing;
- REMOVE from external-validation lane: 1 — Chengdu 2018;
- overall: **HOLD / NO-GO for manuscript revision**.

Strongest recovery:

- An archived 1 March 2013 ADEC/University of Montana report supplies 39 exact site/date radiocarbon rows; 37 also have published CMB wood-smoke percentages.
- On those 37 rows, CMB is above the published radiocarbon interval on 32, inside on 4, and below on 1. Mean signed difference from the interval midpoint is +27.86 percentage points; midpoint MAE is 28.51 percentage points.
- This remains a published-system comparison, not a profile-choice test: native receptor/error/profile/selector/control files are absent, and the radiocarbon conversion itself uses an OMNI hybrid-profile carbon fraction.
- Barrow has four exact weekly-interval CMB/radiocarbon rows, but no filter IDs or native CMB package. Radiocarbon-derived contemporary EC also informed the wood-profile selection, creating direct external-reference leakage.
- APHH identifies the same 25 radiocarbon samples and the final CMB selector, but publishes CMB only as four site/season group means, not daily outputs.
- Chengdu has a named gasoline-profile sensitivity landscape but no independent source-specific external reference; retain it as context only.

No public Fairbanks native electronic CMB package was recovered. A full and compact ADEC public-records request was drafted for the Air Non-Point and Mobile Sources Program, with AMQA coordination, but **not sent**.

The two user-sent investigator requests remain **SENT / PENDING** and are not negative evidence:

1. Palmer/Ward Fairbanks sample-level levoglucosan/radiocarbon spreadsheet.
2. Watson/Chow original NFRAQS CMB-to-fM(CMB) mapping.

## Manuscript boundary

Retain **PFFLS R4.3.30R3nR7-AE** unchanged.

Cycle 03 was independently reviewed and merged through PR #7 as an evidence/audit record only. It does not authorize a new manuscript baseline.

## Cycle 04 closure — submission-candidate reconstruction gate

Cycle 04 was independently reviewed, corrected, and merged through PR #11.

Verified corrected return package:
`PFFLS_CODEX_CYCLE04_SUBMISSION_GATE_RETURN.zip`

SHA-256:
`3b3148ded65a64f2ab000cc57964ada6dbf4f77d2af1b49b7a65a6882b55894e`

QA:
- corrected package-local validator PASS;
- corrected extracted-package tests 6/6 PASS;
- corrected artifact manifest 22/22 PASS;
- ZIP integrity PASS.

Decision:
**HOLD_WITH_EXACT_BLOCKERS**, with no manuscript baseline change.

Current submission blockers are limited to:
1. exact R3nR7-AE manuscript/supplement binary and editable source unavailable in accessible storage;
2. authoritative editable Main/Supplement source unavailable for final compile/redline/full-text audit;
3. final repository DOI/URL and licence unresolved;
4. target-journal/package requirements and author-controlled metadata/declarations unresolved.

The missing JRC/EPA raw computational archives remain explicit **non-blocking archival reproducibility limitations**. Cycle 01 current-tree manifest drift remains **archival housekeeping/snapshot debt**. Neither silently reopens the accepted R3nR7-AE scientific lock.

## Current status

GitHub Issue #9, the continuous Codex mandate, remains open.

Pending external evidence / correspondence status:

1. Palmer/Ward Fairbanks sample-level levoglucosan/radiocarbon spreadsheet — **RESPONSE RECEIVED / DATA LOCATION IN PROGRESS**. Tony Ward asked for the exact report so the group can locate the correct spreadsheet.
2. Watson/Chow NFRAQS CMB-to-fM(CMB) mapping — **ANSWERED / DRI NOT ANALYSIS CUSTODIAN**. John Watson stated that DRI provided archived filter remnants to Klinedinst and Currie but did not participate in the radiocarbon analysis/reporting; the relevant article is Klinedinst & Currie (1999), ES&T 33, 4146–4154. The recovery target therefore shifts to NIST/Klinedinst-Currie archival records.
3. ADEC Fairbanks native CMB electronic package request — **DRAFT ONLY / NOT SENT**.

The locked baseline remains **PFFLS R4.3.30R3nR7-AE**.

## Editorial decision

Cycles 01–04 and the Issue #8 outreach package remain reproducibility,
lineage, and evidence-audit records. None creates or promotes a new manuscript
baseline.

Under Issue #9, Codex should continue autonomously with the next highest-value
task that can materially move the paper toward a submission-ready state,
prioritizing authoritative manuscript/source recovery and the remaining
repository/venue/author-controlled submission items without reopening locked
science absent new admissible evidence or an editor/reviewer request.


## Correspondence update — 2026-09-22

### Fairbanks
Tony Ward replied and asked which Fairbanks report/spreadsheet is being requested. The target was clarified as Christopher P. Palmer, *Fairbanks, Alaska PM2.5 Organic Composition and Source Apportionment Research Study — Final Report*, August 10, 2012, Section 2.2, which states that raw levoglucosan results were supplied in a site/date spreadsheet. Fairbanks remains a live recovery path.

### NFRAQS
John G. Watson replied that DRI supplied remnants of archived NFRAQS filters to Donna B. Klinedinst and Lloyd A. Currie but did not participate in the radiocarbon analysis/reporting. He identified:
Klinedinst, D.B.; Currie, L.A. (1999). *Direct Quantification of PM2.5 Fossil and Biomass Carbon within the Northern Front Range Air Quality Study's Domain*. Environmental Science & Technology 33, 4146–4154. DOI 10.1021/es990355m.

Disposition: stop treating Watson/Chow as the likely custodian of the missing radiocarbon-side analysis. Redirect archival recovery to NIST records associated with Klinedinst/Currie and the 1999/2000 NFRAQS radiocarbon work. This correspondence does not itself recover the historical CMB-to-radiocarbon transformation and does not promote the NFRAQS external-validation endpoint.


## Authoritative R3nR7 recovery — supersedes Cycle 04 source blocker

The exact locked R3nR7-AE journal-stage lineage was recovered from the project Library and copied into the active Drive bridge. The R3l reconstruction lane is archival only and must not be used for submission.

Authoritative identities:
- Journal-stage package SHA-256: `0ed951cb0e3bb31c4bf500fa72322561ee4876e6c437b28e0e13140a3fbf83d6`
- Overleaf source SHA-256: `f4d06310a0fafe77815c76351ca85ed68a77f07ece937042265cd8c2c4c4512d`
- Full-delivery package SHA-256: `e36d1a2b650cf33cd396736c00f7c5ad20237f742f3ef0afe92d49df50f9eee9`

The authoritative package confirms the locked field-data positioning and all locked JRC/EPA results. The prior Cycle 04 statements that the exact R3nR7-AE binary/editable source were unavailable are therefore superseded.

## Final submission freeze — 2026-09-22

The user explicitly authorized completion without waiting for additional Fairbanks or NFRAQS records. Pending/partial correspondence is frozen as non-blocking background evidence for this submission. No new external-accuracy result is added.

Target journal: **Atmospheric Environment**.

The authoritative R3nR7-AE source was finalized with one editorially necessary journal-facing change only: the Data Availability statement now states that the public-safe publication-derived consistency/provenance package accompanies the submission and accurately limits its role to derived consistency verification rather than a source-native rerun of every JRC/EPA fit. No scientific result, equation meaning, candidate universe, selector, or claim boundary changed.

Final QA:
- publication-derived scientific verifier: **14/14 PASS**
- reproducibility SHA manifest: **15/15 PASS**
- JRC edge rebuild: 30 edges and 9 lower-chi-square discordances reproduced
- bibliography: **49/49 cited**, 0 missing citation keys, 0 uncited records
- identified Main: **15 pages**
- anonymous Main: **14 pages**
- Supplement: **14 pages**
- combined Main + Supplement: **29 pages**
- undefined references/citations: **0**
- overfull boxes: **0**
- Type 3 fonts: **0**
- substantive Main/Supplement exact duplicates: **0**
- substantive Main/Supplement near duplicates >=0.90: **0**
- internal-development residue scan: clean
- clean-source compile/render parity: **0 changed pages** for identified Main, anonymous Main, and Supplement
- final journal ZIP integrity: PASS; internal manifest **17/17 PASS**
- final complete working ZIP integrity: PASS; internal manifest **22/22 PASS**

Final packages:
- `PFFLS_R4_3_30R3nR7_AE_AtmosphericEnvironment_SUBMISSION_READY_AUTHOR_ATTESTATIONS_ONLY.zip`
  - SHA-256: `e45552c6f441ac9f2e86bfa8416f2e33a5317d455d6630b2266f7c12f609e74f`
- `PFFLS_R4_3_30R3nR7_AE_AtmosphericEnvironment_COMPLETE_WORKING_PACKAGE.zip`
  - SHA-256: `5fa7da24db0d4f8b232fc4e9be9ca304b3f5292ee155b78b69b4eca3d2f017be`

Google Drive location:
`PFFLS_4_CODEX_BRIDGE/13_FINAL_SUBMISSION_PACKAGE/`

Scientific/editorial execution status: **COMPLETE WITH CURRENT EVIDENCE**.

The only remaining actions before clicking Submit are human author attestations and live portal fields: final all-author approval/order, CRediT, available ORCIDs, final declarations/funding confirmations, originality/concurrent-submission confirmation, permissions, AI-declaration confirmation, and any portal-requested reviewer suggestions. These are not scientific-analysis blockers and must not be inferred.
