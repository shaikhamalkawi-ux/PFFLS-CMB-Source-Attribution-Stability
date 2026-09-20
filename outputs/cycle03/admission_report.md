# Cycle 03 admission report

## Outcome

**HOLD / NO-GO for manuscript revision.** Four candidates were audited: zero KEEP, three HOLD, and one REMOVE from the target external-validation set. The locked baseline remains **PFFLS R4.3.30R3nR7-AE**.

No fit-favored profile, externally closest profile, concordance label, or external-accuracy regret was calculated. Each such quantity would require at least one missing or outcome-contaminated object.

## Strongest new lead: Fairbanks 2011/2012 Table 12

The Wayback Machine preserves a 35-page ADEC/University of Montana report dated 1 March 2013 that is not exposed on the current report page. Its identity is fixed by SHA-256 `d546f2eec1fe69f871302cee0ec01190fa5add438875a83b1b08b0e98e1d1c03`.

Table 12 publishes 39 exact site/date radiocarbon-derived wood-smoke intervals across State Building, North Pole, RAMS, NCORE, and NPF3. Thirty-seven rows also publish the CMB wood-smoke percentage for that site/date. A direct transcription and arithmetic audit finds:

- CMB above the published radiocarbon-derived interval: **32/37**;
- CMB inside the interval: **4/37**;
- CMB below the interval: **1/37**.

Against the midpoint of each published interval, the mean signed CMB difference is **+27.86 percentage points** and the mean absolute difference is **28.51 percentage points**. These are clean-room arithmetic summaries of the printed table, not uncertainty-aware validation statistics.

This is a meaningful exact-date comparison of two published systems, but not the requested profile-choice validation. The report says that the CMB runs did not use OMNI profiles, while the conversion of radiocarbon carbon to percent wood-smoke PM2.5 uses `yC,biomass = 0.837` from an OMNI hybrid wood-smoke profile. The report also describes iterative source/species combinations selected by fit. Without native input, uncertainty, selector, and output files, the comparison cannot be rerun under two frozen same-family profiles.

## Barrow 2012/2013

The ACS supporting information gives six radiocarbon intervals and four exact matching CMB intervals. Tables S1 and S2 report fossil and contemporary OC/EC concentrations with uncertainties on both the radiocarbon and CMB sides. Table S3 gives seven wood-smoke levoglucosan/EC ratios. No filter IDs are published, so the link is exact at the unique sampling-interval level rather than independently proven at the filter-ID level.

The case fails for two independent reasons:

1. The complete CMB receptor vectors and uncertainties, final source-profile vectors and uncertainties, exact fitted-species/source selector, and native run files are not public. The CMB resolved-primary OC total is only about 23–54% of radiocarbon total OC, making the OC endpoint mapping incomplete even though EC approximately closes.
2. The independent reference was not held out. The radiocarbon-derived contemporary EC result was used to calculate levoglucosan half-lives across the wood ratios, and the Maine profile was then selected for CMB. That selection sequence leaks the external outcome into profile choice.

The four-row crosswalk is retained as published-method evidence only. The seven ratios are not relabeled as a prespecified CMB profile landscape.

## APHH-Beijing

The Birmingham eData workbook is authentic and useful: it contains two calculation sheets describing the same 25 radiocarbon/extended-Gelencsér samples, 13 urban IAP and 12 rural PG. The dates exactly cover the radiocarbon subsets discussed by Xu et al.

The article explicitly restricts its CMB comparison to these same 25 radiocarbon-analyzed samples, so the same-sample-reference gate passes at the subset level. The final CMB species and seven source categories are also stated. However, the CMB comparison is aggregated into four site/season means (`IAP winter n=7`, `IAP summer n=6`, `PG winter n=7`, `PG summer n=5`). The workbook contains no daily CMB rows or uncertainties. The public files therefore cannot map an individual dated CMB result to its individual radiocarbon value, and they do not expose the full CMB receptor/error/profile/control package.

## Chengdu 2018

The open workbook contains 64 dated samples and 19 organic-species columns. It has no uncertainty columns, no inorganic receptor matrix, no source profiles, and no CMB outputs. One dated row contains seven formulas that divide values from the preceding row by two; the audit preserves that fact and does not treat those cells as independent measurements.

The article evaluates two coal profiles and a named gasoline landscape (local, Schauer non-catalyst, and five Cai profiles), so the contextual alternative-profile gate passes; the reported gasoline contribution spans 1–8%. It does not supply an independent source-discriminating reference for those choices. The EC-tracer SOA estimate reuses the same OC/EC chemistry and a fixed primary OC/EC ratio of 2.3, rather than providing external truth for coal or gasoline attribution. OM-CMB versus IOM-CMB also changes markers and parts of the source universe. Chengdu is therefore REMOVE for the target external-validation set and KEEP only as context.

## Ten-gate decision summary

| Candidate | Strongest passed object | Decisive failures | Decision |
|---|---|---|---|
| Fairbanks 2011/2012 | Exact site/date CMB–radiocarbon table | Native receptor/uncertainty/profile/selector/control package absent; reference conversion includes an OMNI-profile assumption; no frozen landscape | HOLD |
| Barrow 2012/2013 | Four exact same-interval CMB–radiocarbon rows | No filter IDs; incomplete CMB inputs/profiles and OC mapping; external-reference leakage into wood-profile selection | HOLD |
| APHH-Beijing | Same 25 radiocarbon samples and exact final selector identified | CMB values available only as site/season means; no daily receptor/error/profile/control package or frozen alternatives | HOLD |
| Chengdu 2018 | Named gasoline-profile landscape and partial receptor matrix | No independent source-specific external reference; incomplete reproducibility; OM/IOM changes the system | REMOVE |

The machine-readable status of every gate is in `candidate_dataset_matrix.csv`. A KEEP is rejected unless all ten gates are exactly `yes`.

## Fairbanks electronic-package recovery

No public native CMB electronic package was recovered from current ADEC material, EPA repositories, university repositories, or the audited archive paths. The Wayback report is a new report-level record, not the requested electronic appendix. A complete, unsent ADEC public-records request is provided separately and targets the native files, folder structure, and run/sample mapping without asking the agency to create a new analysis.

## External-request boundary

The Palmer/Ward spreadsheet request and Watson/Chow NFRAQS mapping request remain **SENT / PENDING**. Non-response is not negative evidence. The ADEC request is **DRAFT ONLY / NOT SENT** and concerns a distinct government custodian/archive.

## Stop rule

Cycle 03 stops at **HOLD**. No CMB rerun, candidate manuscript delta, or baseline change is justified by the currently public record.
