# PFFLS 4 — Project State

## Current scientific submission baseline
**PFFLS R4.3.30R3nR8-AE — Protocol Closure**

The later protocol-closure entry supersedes the earlier R3nR7 pointer. The exact R3nR7 source was recovered before R3nR8; older missing-source statements below are historical. The 2026-09-25 author-update PDF is a separately labeled review candidate, not a new scientific baseline.

## Latest independent Fairbanks audit — 2026-09-25

See `outputs/received_fairbanks/AUDIT_REPORT.md` and its reproducible aggregate. This audit supersedes the unqualified 53-row native-bracket characterization in the historical 2026-09-24 entry below, without deleting that record.

- **52 complete native conversion brackets**: 24 State Building, 13 North Pole, 15 Peger; EPA/OMNI/tie closeness counts 17/32/3; mean interval distances 32.35/24.73 pp using published Appendix C PM denominators.
- **53 partial-fill sensitivity**: fills one missing endpoint only where the other exists; it reconstructs earlier cohort and relation counts but is not a complete-native analysis. EPA distance is 33.13 pp, not the earlier 33.14 pp; OMNI 25.71 pp.
- **54 full-derived sensitivity**: additionally reconstructs a wholly absent bracket from positive marker inputs. The cause of source blank cells is unknown; no values are clipped to 100%.
- The 12 radiocarbon matches and three dual-marker dates reproduce. Prior 13.73/13.36 pp radiocarbon distances use native summary-workbook PM denominators; published Appendix C PM gives 13.72/13.34 pp. Both are explicitly reported, not mixed.
- Corrected revised-OMNI Peger autos/diesel/fuel-oil column mapping in the public Appendix C parser: 26 rows, 108 cells. Wood-smoke outputs and original EPA/OMNI comparisons are unchanged.
- **KEEP** secondary historical marker concordance and reproducibility; **HOLD** profile-choice accuracy validation or a unique system winner; **REMOVE** unqualified native-n=53 and the old revised-Peger column assignment.

The user's requested author candidate removes Azmi Alazzam, Said Badreddine, Eyad Adnan, and Bakeel Hussein; adds Mohammed Alhagyan with the supplied UAEU Mathematical Sciences affiliation; preserves the first two authors; and retains the specific Palmer/Ward/Turner acknowledgement. Scientific manuscript results and supplement remain unchanged. Final author consent, contributions, and submission declarations are not inferred.

No scientific baseline promotion, merge, ADEC records request, collaborator email, or journal submission is authorized by this audit return.

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


## Protocol closure — R3nR8 supersedes R3nR7 as active submission baseline

The three author protocols on contribution-first framing, reader-facing mathematical transparency, and final pre-submission auditing were applied to the authoritative R3nR7-AE source. The resulting active baseline is **PFFLS R4.3.30R3nR8-AE — Protocol Closure**.

R3nR8 is not a science rebuild. It removes off-story supplementary material from the older PFFLS line, adds equation labels and minor symbol/domain/denominator clarification, and keeps the paper centered on the single source-profile-choice question plus safeguards. Main numerical tokens were preserved 339/339 with no additions or removals. The connected reference set remains 30 (>25 protocol minimum). Main/Supplement visual, citation, equation, duplication, residue, and production QA passed. The locked JRC/EPA numerical results and claim boundaries are unchanged.

## Historical Fairbanks investigator-data audit — 2026-09-24

**Superseded in part by the 2026-09-25 independent audit above:** retain this entry as the prior review record. Its 53-row claim requires a partial-endpoint reconstruction and must not be reused as a complete-native analysis. Exact factors, small numerical differences, and PM-denominator conventions are documented in the new audit.

Christopher P. Palmer supplied two original historical Excel files from the Fairbanks organic-composition work:
- `Fairbanks summary 08-11_cpp.xlsx`, SHA-256 `973917d6c504f25980938a8a45da62ce766099734e053a65882c2c05391d8ee7`
- `LevoglucosanResults_final1.xlsx`, SHA-256 `1541b1102f49fec9d461fbfb9c3095c13d7b8a23cbce54c81f1744fe7572691a`

The received mail/attachment ZIP SHA-256 is `e0498220b12ef493bd3d3a16fa27c17becefd8495f0123463a78053cc85d05ac`.

The spreadsheets close the previously missing site/date external-marker crosswalk gate. The levoglucosan workbook contains 241 dated rows across State Building, North Pole, Peger Road, and RAMS. The summary workbook contains 361 dated rows and 26 rows with published radiocarbon wood-smoke intervals. The 2008/09 matched rows lack filter IDs, but sample identity is strongly anchored by site/date and PM2.5 mass: all 53 exact CMB–levoglucosan matches agree with the frozen Appendix C PM2.5 mass to within 0.04 µg/m3.

### Exact sample-level CMB–levoglucosan comparison

There are **53** exact both-valid EPA/OMNI CMB site/date matches with recovered levoglucosan data: 24 State Building, 14 North Pole, and 15 Peger Road.

Using the spreadsheet's Fine-CF=9.01 to OMNI-CF≈13.3 wood-smoke conversion-factor bracket (a conversion-factor bracket, **not** a confidence interval):
- EPA CMB: 3/53 inside, 50/53 above, 0 below; mean distance outside bracket 33.14 percentage points.
- OMNI CMB: 10/53 inside, 43/53 above, 0 below; mean distance outside bracket 25.71 percentage points.
- OMNI is closer on 32/53 dates, EPA on 18/53, tie on 3/53.

This must **not** be interpreted as OMNI being validated as more accurate. The OMNI and EPA CMB systems do not share a fixed source universe/treatment, and the OMNI levoglucosan conversion factor itself uses, in part, OMNI-generated source-filter information.

### Exact sample-level CMB–radiocarbon comparison

There are **12** exact 2008/09 both-valid CMB site/date matches with recovered radiocarbon wood-smoke intervals:
- EPA CMB: 3 inside, 8 above, 1 below; mean interval distance 13.73 pp; midpoint MAE 17.76 pp.
- OMNI CMB: 2 inside, 7 above, 3 below; mean interval distance 13.36 pp; midpoint MAE 17.51 pp.
- EPA is closer to the radiocarbon interval on 7/12 dates, OMNI on 4/12, tie on 1/12.

The direction therefore differs from the levoglucosan comparison. Only three exact dates contain both positive levoglucosan and radiocarbon marker structures; the two marker intervals overlap on one of the three dates and do not overlap on two.

### Evidence-gate decision

**KEEP** the Palmer spreadsheets as secondary sample-level historical field-marker concordance evidence and provenance.
**HOLD** any claim that Fairbanks externally validates profile-choice accuracy, identifies a unique CMB-system winner, or establishes environmental truth.

Reasons:
1. EPA versus OMNI is a profile-system comparison with different source universes/treatments, not an isolated one-profile substitution.
2. Per-alternative final selectors and fit diagnostics are not recovered in these spreadsheets.
3. Levoglucosan-to-wood-smoke mapping is conversion-factor dependent and the OMNI factor is not fully independent of OMNI source experiments.
4. Radiocarbon overlap is sparse.
5. The independent-marker structures themselves do not yield a uniform system preference.

**Manuscript disposition:** do not open R3nR9 solely for these files. R3nR8 remains the active submission baseline. The Fairbanks result is retained as reviewer-response / secondary-evidence reserve unless an editor/reviewer asks for it or a later complete frozen-profile/selector package closes the target validation gate.
