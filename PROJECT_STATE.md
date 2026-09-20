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

## Active work — Cycle 03 remaining evidence recovery

Cycle 03 is active through:

- GitHub task: `tasks/CODEX_CYCLE_03_REMAINING_EVIDENCE.md`
- GitHub Issue #6
- Drive instruction: `01_TO_CODEX/CODEX_CYCLE_03_REMAINING_EVIDENCE`
- Drive workspace: `09_CYCLE03_REMAINING_EVIDENCE`

### External requests already sent by the user

These must be treated as **PENDING RESPONSE**, not as failed evidence:

1. Palmer/Ward request for the Fairbanks sample-level levoglucosan/radiocarbon spreadsheet — SENT.
2. Watson/Chow request for the original NFRAQS CMB-to-fM(CMB) mapping — SENT.

Do not duplicate those requests unless a materially different custodian/archive is found.

### Cycle 03 Track A

Attempt to recover the original Fairbanks CMB electronic package from public/official archives.

If recovery requires a government public-record request:
- prepare the full ADEC request and compact web-form version;
- identify the correct agency/unit/contact/portal;
- do not submit it.

### Cycle 03 Track B

Screen for a complete independent profile-resolved external-validation dataset, starting with:
- Barrow, Alaska 2012–2013;
- APHH-Beijing;
- Chengdu source-profile-sensitivity data.

Apply the full fail-closed admission rule. A candidate is KEEP only if receptor values/uncertainties, source profiles/uncertainties, exact selector, CMB implementation, same-sample independent reference, unambiguous endpoint mapping, frozen same-family alternatives, and present reproducibility are all complete.

## Manuscript boundary

Retain **PFFLS R4.3.30R3nR7-AE** unchanged during Cycle 03.

Cycle 03 does not authorize a new manuscript baseline. If a complete case passes, return the scientific evidence package first for independent review.

## Editorial decision

Cycle 01 and Cycle 02 remain reproducibility/evidence-audit records and do not create a new manuscript baseline.
