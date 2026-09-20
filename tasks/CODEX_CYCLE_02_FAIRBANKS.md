# CODEX CYCLE 02 — Fairbanks profile-resolved external-validation recovery

## Status entering Cycle 02

Cycle 01 is closed as **HOLD / NO-GO for manuscript revision**.

Merged audit:
- 0 KEEP campaigns
- 6 HOLD campaigns
- 1 REMOVE campaign

Locked manuscript baseline remains:

**PFFLS R4.3.30R3nR7-AE**

Cycle 02 does not authorize a manuscript revision. It is an evidence-recovery branch.

## Why Fairbanks

The Fairbanks, Alaska wood-smoke source-apportionment campaign is the strongest unresolved near-case identified in Cycle 01.

Already documented from the public record:
- a substantial CMB field campaign;
- 91 published source profiles with uncertainties in the Alaska DEC report;
- 43 candidate chemical species documented;
- daily final source-contribution outputs with standard errors;
- independent wood-smoke comparison evidence involving radiocarbon and levoglucosan;
- multiple source-profile/species combinations were tried until an optimal fit was obtained.

This is promising but not yet admissible for the paper's frozen source-profile-choice question.

## Scientific question

Can Fairbanks be reconstructed at sample/day level well enough to test:

> Among prespecified alternative source profiles belonging to the same source family, does the profile favored by a frozen CMB fit criterion also minimize error against an independent same-sample external reference?

Do not answer this question unless every required evidence gate below is closed.

## Primary recovery targets

Recover, for at least one exact Fairbanks receptor sample/day or a prespecified matched set:

1. **Receptor chemical-speciation vector**
   - measured concentrations used by CMB;
   - exact units;
   - sample/site/date/time identity.

2. **Receptor uncertainty vector**
   - exact uncertainty for every fitting species;
   - detection-limit handling if used;
   - no inferred uncertainty rules unless explicitly documented.

3. **Numerical source profiles**
   - exact candidate source-profile vectors;
   - exact profile IDs/names;
   - full fitting-species overlap;
   - source-profile uncertainties.

4. **Exact final selector**
   - source profiles used for the final fit;
   - fitting species used for that sample;
   - any deleted species;
   - any collinearity/source-exclusion decisions;
   - whether source/profile choices differed by sample.

5. **Independent reference crosswalk**
   - exact same sample/day/interval for radiocarbon and/or levoglucosan;
   - exact units and denominator;
   - explicit sample IDs if available.

6. **Endpoint mapping**
   - an unambiguous, historically documented mapping from CMB outputs to the quantity compared with the independent reference;
   - no post-hoc endmember, normalization, denominator, negative-contribution, or carbon-weighting rules.

7. **CMB implementation**
   - software/version;
   - EVLS or equivalent details;
   - convergence/stopping criteria;
   - enough information to reproduce the published control output.

8. **Frozen alternative-profile landscape**
   - at least two independently measured profiles in one physical source family;
   - candidates must be identified before external-reference outcomes are inspected;
   - no post-hoc addition/removal of candidates.

## Priority source locations

Search systematically, with official/public sources first:

### Alaska / Fairbanks
- Alaska Department of Environmental Conservation (DEC)
- Alaska air-quality technical appendices
- Fairbanks PM2.5 SIP/supporting technical documents
- state FTP/archive mirrors
- Alaska DEC source-apportionment project files
- contractor appendices / electronic data packages

### Federal repositories
- EPA AQS
- EPA NEPIS
- EPA HERO
- EPA CMB archives
- Air Quality System downloadable raw speciation records
- IMPROVE/STN/CSN archives if the campaign used them

### Academic / report sources
- University of Montana / University of Alaska repositories
- author institutional repositories
- journal supplementary files
- archived conference/report appendices
- public data associated with Ward et al. / Busby et al.

### Archive recovery
- Internet Archive / Wayback for dead public links
- agency document mirrors
- DOI-linked supplementary locations

Do not use unauthorized credentials, restricted systems, or non-public data.

## Exact-case requirement

Do not aggregate dates or sites to force a match.

For any candidate exact case, record:
- site;
- date;
- start/end time or duration;
- filter/sample ID;
- PM size fraction;
- CMB sample identifier;
- radiocarbon sample identifier;
- levoglucosan sample identifier where relevant.

If no exact crosswalk exists, return HOLD.

## Fit selector

Do not choose a new selector after seeing results.

Unless the historical Fairbanks study supplies a clearly prespecified selector that must be reproduced, use the existing PFFLS primary comparison convention only after documenting why it is compatible with the reconstructed landscape:

**lower reduced chi-square / lower mean reduced chi-square as applicable to the frozen landscape.**

If the comparison cannot be made without changing the scientific question, return HOLD.

## Outcome rules

A Fairbanks case can become KEEP for profile-resolved external validation only if:

- all eight evidence objects are complete;
- at least two prespecified same-family source profiles are available;
- the released/published control fit is reproduced within declared tolerance;
- the same-sample external endpoint is independent;
- the CMB-to-reference mapping is explicit and reproducible;
- the alternative-profile rerun is completed without post-outcome tuning.

Then report:
- fit-favored profile;
- external-reference-closer profile;
- concordant / discordant / tied;
- external-accuracy regret of the fit-favored profile;
- exact finite-landscape results only.

Do not convert one campaign into a population-prevalence claim.

## Mandatory fail-closed rules

Return HOLD if any of these are missing:
- receptor vector;
- receptor uncertainty;
- profile vector;
- profile uncertainty;
- exact selector;
- exact same-sample crosswalk;
- unambiguous endpoint mapping;
- reproducible control.

Do not:
- digitize figures when an exact table/file may exist without first exhausting exact sources;
- reconstruct missing values from narrative averages;
- infer source-profile uncertainties from unrelated studies;
- substitute SPECIATE profiles for historical Fairbanks profiles without proving identity;
- infer daily selectors from final source-contribution tables;
- treat correlation or study-average agreement as profile-level external accuracy.

## Independent verification

If a complete case is found:

1. implement a clean-room reproduction independent of prior PFFLS code;
2. reproduce the published Fairbanks control;
3. independently verify at least one exact case with a second implementation or calculation path;
4. add regression tests;
5. report all numerical tolerances.

## Deliverables

Commit safe, redistributable materials to GitHub under:

- `outputs/cycle02/`
- `scripts/`
- `tests/`

Required files:
- `outputs/cycle02/source_inventory.csv`
- `outputs/cycle02/fairbanks_evidence_register.csv`
- `outputs/cycle02/exact_case_crosswalk.csv`
- `outputs/cycle02/profile_registry.csv`
- `outputs/cycle02/admission_report.md`
- `outputs/cycle02/KEEP_HOLD_REMOVE.md`
- `outputs/cycle02/SCIENTIFIC_CHANGELOG.md`
- `outputs/cycle02/EDITORIAL_RECOMMENDATION.md`
- `outputs/cycle02/reproduction.md`
- `outputs/cycle02/artifact_manifest_sha256.csv`

If full reconstruction succeeds, additionally return:
- exact input matrices;
- clean-room scripts;
- control-reproduction table;
- frozen candidate comparison table;
- external-reference error table;
- machine-readable result JSON;
- tests.

## Google Drive return

Large/non-redistributable working material must remain outside the public GitHub repository.

Return the complete review package to:

`PFFLS_4_CODEX_BRIDGE/02_FROM_CODEX/`

Recommended filename:

`PFFLS_CODEX_CYCLE02_FAIRBANKS_RETURN.zip`

Include a SHA-256 sidecar.

## Git workflow

Create a branch:

`codex/cycle-02-fairbanks-recovery`

Open a pull request when the audit is complete.

Do not merge it yourself.

## Manuscript boundary

Do not edit or replace the locked R3nR7-AE manuscript during evidence recovery.

If and only if Cycle 02 produces an admissible new result, prepare a **candidate manuscript delta** separately. Do not label it as the new baseline until independent review accepts it.

## Final stop rule

The valid final states are:

- **KEEP** — a complete profile-resolved external-validation case exists;
- **HOLD** — Fairbanks remains promising but one or more essential objects are missing;
- **REMOVE** — recovered evidence shows Fairbanks cannot answer this question.

A null or discordant scientific result is fully acceptable.
