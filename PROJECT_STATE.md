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
- exact Welby/NIST same-sample interval crosswalk is confirmed

HOLD:
- profile-resolved radiocarbon external-accuracy ranking
- any claim that NWSOWHL is externally more accurate
- Libby profile-resolved rerun

Reason:
the original CMB-to-fM(CMB) mapping underlying Chapter 7 was not recovered unambiguously.

## Cycle 01 closure

Cycle 01 external field-validation audit was independently reviewed, corrected, and merged through PR #3.

Final Cycle 01 campaign-level decision:
- KEEP campaigns: 0
- HOLD campaigns: 6
- REMOVE campaigns: 1
- overall decision: **HOLD / NO-GO for manuscript revision**

The locked manuscript baseline was not changed.

## Active work — Cycle 02

**Cycle 02 is active and focuses only on Fairbanks, Alaska.**

GitHub task:
`tasks/CODEX_CYCLE_02_FAIRBANKS.md`

Issue:
**#4 — Codex Cycle 02 — Fairbanks profile-resolved external-validation recovery**

Primary missing evidence:
1. sample-level receptor chemistry;
2. receptor uncertainties;
3. exact final profile/species selectors;
4. exact same-sample radiocarbon / levoglucosan crosswalk;
5. unambiguous CMB-to-reference endpoint mapping.

Cycle 02 is evidence recovery only. It does not authorize a manuscript revision.

## Editorial decision
**NO-GO for a new manuscript version from Cycle 01.**

Reopen the manuscript only for:
1. recovery of the original reproducible CMB-side radiocarbon transformation;
2. a genuinely profile-resolved independent field dataset;
3. a substantive new scientific result that passes the gates; or
4. an explicit reviewer/editor request.
