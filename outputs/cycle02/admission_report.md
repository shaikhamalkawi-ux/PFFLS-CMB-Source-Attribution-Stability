# Cycle 02 Fairbanks admission report

## Outcome

**HOLD — no manuscript revision and no profile-resolved external-validation claim.**

The recovery materially improves the Fairbanks record, but it does not close all eight admission gates. The strongest defensible result is a date-resolved **profile-system sensitivity** comparison, not an isolated profile-choice test.

## What was recovered

- Appendix C yielded 294 daily rows for the 2008/2009 State Building, North Pole, and Peger Road EPA/OMNI systems, including source-contribution standard errors.
- There are 107 exact site/date EPA-versus-OMNI pairs; 94 have valid rows in both systems: 47 State Building, 21 North Pole, and 26 Peger Road.
- EPA AirData links State Building to AQS site `02-090-0010`. Forty-seven SASS gravimetric mass records (parameter 88502, POC 6, method 810) agree with Appendix C to the report's displayed precision.
- Among the 47 valid EPA CMB days, AirData supplies receptor-species records on 45 dates. Thirty-two contain all 43 report species; thirteen contain 38. The valid CMB dates 2009-02-05 and 2009-02-07 lack a matching SASS speciation vector in AirData.
- Ward Appendix A publishes nine numerical OMNI profiles. Four are same-family wood profiles, and the report says FBK107 fit best generally; FBK100, FBK101, and FBK102 were also significant and used.
- Busby reports 161 matched CMB–levoglucosan samples and 40 matched radiocarbon–levoglucosan samples. Its CMB modeling used the EPA/Missoula system, explicitly not the OMNI profiles.
- Palmer states that raw site/date levoglucosan results were delivered in a spreadsheet. That spreadsheet was not attached to the public report and was not located in the audited current or archived sources.

## Why EPA versus OMNI is not the target test

The source universe is not held fixed. The OMNI system adds No. 2 fuel oil and other Fairbanks trial profiles, while revised OMNI runs also alter the vehicle treatment. On the 94 both-valid pairs, mean OMNI wood smoke is lower than EPA by 1.37 µg/m³ at North Pole, 2.06 µg/m³ at Peger Road, and 2.15 µg/m³ at State Building; OMNI simultaneously assigns mean No. 2 fuel-oil contributions of 2.06, 4.55, and 3.50 µg/m³. Those shifts are scientifically informative, but they combine profile and source-universe changes.

## Eight-gate decision

| Gate | Status | Reason |
|---|---|---|
| Receptor vector | Partial | Same-site/date SASS data are strongly linked, but two valid dates are absent, later dates lack five species, and identity with the exact CMB input/fitting subset is not proven. |
| Receptor uncertainty | Missing | No per-species, per-sample CMB uncertainty vector was recovered. |
| Numerical profiles | Partial | OMNI vectors are public; the exact EPA/Missoula vector set and historical uncertainties were not recovered. |
| Exact final selector | Missing | No day-level profile ID or fitting-species/deletion record is public. |
| Independent-reference crosswalk | Missing | Counts exist, but dates/filter IDs and daily radiocarbon or levoglucosan values are not public. |
| Endpoint mapping | Partial | Methods are documented, but levoglucosan uses a conversion range and the exact paired values are absent. |
| CMB implementation | Partial | Version 8.2 and EVLS are documented; exact inputs and a reproducible control are not. |
| Frozen alternatives | Missing | Historical candidates were selected after iterative fit inspection; EPA and OMNI do not share a fixed source universe. |

## Stop rule

No rerun, fit-favored profile, external-reference regret, or concordance label was computed. Doing so would require inventing receptor uncertainties, final selectors, or external-reference identities. The correct Cycle 02 state is therefore **HOLD**.
