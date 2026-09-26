# Fairbanks original-workbook re-audit

Date: 2026-09-26. Scope: independent read-only extraction of the two received
Palmer workbooks and comparison against the public Cycle 02 Appendix C snapshot.
This is a data-admission and provenance audit, not a new field-accuracy result.

## Main finding and correction

The primary native-output levoglucosan comparison has **52 complete site/date
pairs**, not 53. The historical 53-row statement mixes one arithmetically filled
endpoint with the original workbook outputs. Recomputing all available positive
inputs produces 54 pairs. These are different analysis sets and must not be
interchanged. The public project-state 53-row paragraph should therefore be
superseded by this explicit distinction, while preserving its archival history.

This independently reproduces the existing private independent-reproduction
audit's 52-row result. It is a correction to the project-state summary, not a new
claim that the original investigators' recorded formulas were wrong.

## Input identities and inventory

| Input | SHA-256 |
|---|---|
| Fairbanks summary 08-11_cpp.xlsx | `973917d6c504f25980938a8a45da62ce766099734e053a65882c2c05391d8ee7` |
| LevoglucosanResults_final1.xlsx | `1541b1102f49fec9d461fbfb9c3095c13d7b8a23cbce54c81f1744fe7572691a` |
| Public Appendix C CSV, LF-normalized | `9c7d225b394b19ba9354077a50bf24c3f77a3972064c42e8e090168da749b172` |

The original workbook hashes were rechecked after extraction: neither workbook
was saved, recalculated, repaired, or otherwise modified. The Appendix C hash is
explicitly LF-normalized to allow Git line-ending conversion; its exact local
byte hash is recorded separately in the private audit JSON.

| Inventory | State Building | North Pole | Peger Road | RAMS | Total |
|---|---:|---:|---:|---:|---:|
| Levoglucosan native Excel dates | 78 | 68 | 62 | 33 | 241 |
| Additional explicit US-format text dates | 0 | 0 | 3 | 0 | 3 |
| Summary native Excel dates | 140 | 81 | 79 | 61 | 361 |

The three text-date rows yield 244 parseable levoglucosan records when explicitly
included in the inventory. They are from a later season and do not change the
2008/09 comparisons. There are no duplicate site/date keys in either extracted
inventory. Four additional summary text annotations combine a filter ID, site,
and date; they are retained separately and are not silently counted as native
date rows. The summary has 26 native-date rows with two numeric radiocarbon-derived
wood-smoke bounds.

## Formula, unit, and missing-value checks

- The levoglucosan workbook headers give conversion factors **9.01 and 13.27**
  (`F3:G4` on each site sheet). 13.3 is an approximation, not the original factor.
- PM mass is in micrograms per cubic metre; levoglucosan is in nanograms per cubic
  metre. The verified calculation is `100 * CF * 0.001 * levo / PM`.
- **684 existing formula caches**, including all **455 existing wood-smoke
  endpoint formula caches**, agree with independent arithmetic within `1e-8`
  percentage points. No existing formula has a bad cache under this check.
- Nine blank output cells across four rows are arithmetically computable from
  available inputs. They are **missing source outputs**, not formula-cache
  errors. No blank, detection/error flag, or missing result is converted to zero
  in the primary analysis. Two of these rows affect the 2008/09 paired set.
- One affected paired row has a missing upper endpoint but a recorded lower
  endpoint. Filling only that endpoint gives the 53-row sensitivity.
- Another affected paired row has both wood-smoke outputs absent. Recalculation
  gives a bracket wholly above 100%, producing the 54-row sensitivity. It is not
  clipped to 100% and is not silently promoted to an investigator-reported result.
- No Excel error token was found in the scanned caches. Source text flags,
  negative inputs, zeros, and missing cells are retained as separate categories
  in private diagnostics; absence of Excel errors is not absence of data limits.
- Summary radiocarbon columns I/J already contain derived wood-smoke percentage
  bounds. They are not raw radiocarbon measurements or model-free ground truth.

## Reproduced aggregate comparisons

CMB percentages use `100 * published wood-smoke contribution / published PM mass`
from the matched Appendix C system. The marker bracket uses the original
workbook denominator and conversion factors. Distance is
`max(lower - estimate, estimate - upper, 0)`. "Inside" includes endpoints.
No uncertainty distribution, confidence level, or independence assumption is
invented for these brackets. CMB standard errors are retained privately but not
silently combined with conversion-factor brackets.

| Analysis set | n | EPA inside / above / below | OMNI inside / above / below | EPA mean distance (pp) | OMNI mean distance (pp) |
|---|---:|---:|---:|---:|---:|
| Native complete levoglucosan outputs — primary | 52 | 3 / 49 / 0 | 10 / 42 / 0 | 32.345350 | 24.725521 |
| Fill partially present bracket only — sensitivity | 53 | 3 / 50 / 0 | 10 / 43 / 0 | 33.132109 | 25.706365 |
| Recompute all positive-input brackets — sensitivity | 54 | 3 / 50 / 1 | 10 / 43 / 1 | 33.845720 | 26.520453 |
| Native radiocarbon-derived intervals | 12 | 3 / 8 / 1 | 2 / 7 / 3 | 13.722044 | 13.344728 |

The primary 52 rows comprise 24 State Building, 13 North Pole and 15 Peger Road
dates. OMNI is closer on 32, EPA on 17, with 3 ties. All 52 lack filter IDs. Exact
site/date matching and PM-mass agreement within 0.04 micrograms per cubic metre
support the crosswalk but do not establish a recovered filter-ID chain of custody.
No mass-tolerance filter was used to force the sample count.

For radiocarbon, EPA is closer on 7 dates, OMNI on 4, with 1 tie. Midpoint MAEs are
17.751037 pp (EPA) and 17.492537 pp (OMNI). If CMB contributions are instead divided
by the summary workbook PM mass, interval distances become 13.734751 and
13.357361 pp and midpoint MAEs become 17.762952 and 17.505170 pp. These alternate
denominators explain the historical radiocarbon rounded metrics; the denominator
must be named rather than switching silently.

For the 53-row sensitivity, using the marker-workbook PM denominator gives
33.134146 and 25.705482 pp. The old EPA 33.14 pp value is not exactly reproduced
by either stated denominator with the recorded 13.27 conversion factor; do not
retain that rounded value as a verified primary result.

Only three exact paired dates carry both usable marker structures. Their
intervals overlap on one date and are disjoint on two. The two marker subsets
therefore do not identify a uniform system preference.

## Admission decision and value for strengthening

**KEEP** the original spreadsheets and corrected aggregate audit as secondary
historical system-concordance evidence, with protected access to detailed rows.

**HOLD** claims of independently validated profile-choice accuracy, a unique
EPA/OMNI accuracy winner, or field truth. The remaining requirements are:

1. Freeze the same source universe and model treatment when isolating a profile
   substitution. The public report's EPA/OMNI systems differ, including the OMNI
   fuel-oil source and vehicle treatment.
2. Recover per-alternative final selectors, numerical source-profile/error
   vectors, model controls, and fit diagnostics. These investigator marker
   workbooks are not that complete CMB package.
3. Separate reference construction from profile selection. The OMNI conversion
   factor partly depends on OMNI source experiments, and a conversion-factor
   bracket is not an independent statistical confidence interval.
4. Preserve the distinct endpoint definitions and account for sparse
   radiocarbon overlap. Site/date concordance alone does not solve these gates.

**REMOVE from primary reporting** the unqualified phrase "53 original complete
matches". It may remain only as the clearly labeled partial-recomputation
sensitivity. No need to force this reserve evidence into the manuscript's main
claim merely to increase the number of datasets.

## Reproduction and privacy

Run `python scripts/audit_fairbanks_strengthening.py` with the authorized private
workbooks in the documented local input directory, or supply `--input-dir`.
The script verifies source hashes and restricts detailed outputs to the
gitignored `private/strengthening_20260926/fairbanks/` directory. No private
rows, original spreadsheet, investigator email, or filter IDs are published by
this audit.

`python -m unittest discover -s tests -p test_fairbanks_strengthening.py -v`
passes **16 tests** locally: 9 synthetic unit tests and 7 private-source integration
tests. Public users without the private originals can run the 9 unit tests; the
7 integration tests are explicitly skipped, not reported as reproduced.

Sources: original investigator workbooks, the frozen public
`outputs/cycle02/appendix_c_2008_2009_daily.csv` and profile registry, and
[ADEC/University of Montana final report, Appendix C](https://dec.alaska.gov/media/7083/fairbanks-cmb-report-univ-mt-final-122313.pdf).
The source-system and marker-dependency limitations are also recorded in the
repository's Cycle 02 evidence register and project-state Fairbanks section.
