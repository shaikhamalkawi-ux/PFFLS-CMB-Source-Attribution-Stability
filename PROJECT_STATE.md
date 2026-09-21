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

Pending external evidence remains live, not negative evidence:

1. Palmer/Ward Fairbanks sample-level levoglucosan/radiocarbon spreadsheet — **USER-REPORTED SENT / PENDING — UNVERIFIED**.
2. Watson/Chow original NFRAQS CMB-to-fM(CMB) mapping — **USER-REPORTED SENT / PENDING — UNVERIFIED**.
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
