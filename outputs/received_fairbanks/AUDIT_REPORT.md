# Independent Fairbanks received-data audit

Date: 2026-09-25. Base: `4d434e8455f5264f4d0e9c89ebb26f5a34f32d8e`.

## Decision and scope

**KEEP** the received historical workbooks as secondary field-marker concordance evidence, the reproducible exact-site/date comparison, explicit missingness/denominator sensitivity analyses, and the published-table parser correction.

**HOLD** independent profile-choice accuracy validation, a unique EPA/OMNI accuracy winner, source-native CMB reconstruction, and insertion of these results into the active manuscript. This audit does not change locked JRC/EPA results or promote a new baseline.

**REMOVE** the unqualified description of 53 comparisons as complete source-native conversion brackets. Also remove an unqualified 33.14 pp reproduction claim, and the old Peger revised-OMNI autos/diesel/fuel-oil column assignment. Preserve prior records as historical; superseding definitions are below.

## Inputs and provenance

The received archive contains two XLSX files, not an email-message record. Provider attribution is based on the user's supplied correspondence screenshots, not inferred from ZIP membership. The names acknowledged are Chris P. Palmer, Tony J. Ward, Jay Turner, and colleagues. Khalifa University is unrelated to this PFFLS work.

| Input | SHA-256 |
|---|---|
| Received attachment ZIP | `e0498220b12ef493bd3d3a16fa27c17becefd8495f0123463a78053cc85d05ac` |
| Fairbanks summary 08-11_cpp.xlsx | `973917d6c504f25980938a8a45da62ce766099734e053a65882c2c05391d8ee7` |
| LevoglucosanResults_final1.xlsx | `1541b1102f49fec9d461fbfb9c3095c13d7b8a23cbce54c81f1744fe7572691a` |
| Ward 2013 report PDF used for Appendix C | `9d71371a413b517a4cbaa441be01477bab4ef58d831aac55caab5c0658ca534e` |
| Corrected published Appendix C CSV | `42400f44d257a8802989726e6b63886f6f9f39c1f2d4e87849f8c8d2a29ab040` |

The public report source is [ADEC's Fairbanks CMB report](https://dec.alaska.gov/media/17116/fairbanks-cmb-final-report-122313.pdf). [Busby et al.](https://aaqr.org/articles/aaqr-15-04-simts-0235.pdf) supplies interpretive context, not additional rows silently appended to the workbooks.

The levoglucosan workbook has 241 native Excel-date rows plus three separately retained text-date candidates. The summary has 361 native-date rows and 26 numeric radiocarbon-derived wood-smoke intervals. The published extraction has 294 system rows, 107 original EPA/OMNI site/date pairs, and 94 both-valid pairs. Revised OMNI runs are not substituted into the original-system comparison.

## Cohort correction: 52, 53, and 54 are different analyses

Primary inclusion requires a unique exact site/calendar-date key, original EPA and OMNI runs both marked valid, positive measured PM and levoglucosan, and both native cached marker-output bounds present. Missing, zero, negative, censored, or textual values are not silently converted or imputed. No PM-difference filter is used to achieve a target count.

Of 54 exact both-valid pairs with positive marker inputs, one has only one native bound, and one has neither. Root and independent reviewers checked the underlying formula and cached cells; the missing endpoints are truly blank. The reason for the blanks is unknown and is not inferred. Exact cells/dates are retained in the private evidence files.

| Analysis | n | State Building / North Pole / Peger | EPA closer / OMNI closer / tie |
|---|---:|---|---|
| Native complete brackets, primary | 52 | 24 / 13 / 15 | 17 / 32 / 3 |
| Fill only a partially present bracket, diagnostic sensitivity | 53 | 24 / 14 / 15 | 18 / 32 / 3 |
| Recompute every positive-input bracket, sensitivity | 54 | 25 / 14 / 15 | 18 / 33 / 3 |

The 53-row sensitivity reconstructs the earlier cohort size and relation counts; it does **not** establish how the earlier reviewer handled that missing endpoint. The 54-row sensitivity includes a derived bracket whose lower bound exceeds 100%. Values are retained, not clipped; this is not evidence of literal wood-smoke mass greater than total PM.

## Endpoint definitions and primary results

Native marker endpoints correspond to `100 * CF * 0.001 * levoglucosan_ng_m3 / measured_PM_ug_m3`, using Fine CF = 9.01 and OMNI CF = 13.27. All 455 available formula/cache comparisons agree within 1e-9 pp. These are conversion-factor alternatives, not confidence limits or two CMB runs.

CMB percentages in the primary audit are `100 * published_wood_smoke_ug_m3 / Appendix_C_PM_ug_m3`. Interval distance is `max(low - estimate, estimate - high, 0)`, not absolute distance from the midpoint. Ties use unrounded distances. Source-contribution standard errors are retained but are not receptor uncertainty and are not propagated into marker brackets.

| Native-complete levoglucosan, n=52 | Inside / above / below | Mean interval distance, pp |
|---|---|---:|
| EPA | 3 / 49 / 0 | 32.35 |
| OMNI | 10 / 42 / 0 | 24.73 |

All 52 sample PM differences are at most 0.04 ug/m3. Historical filter IDs are absent; site/date and mass agreement support identity but do not replace an original filter crosswalk.

The 53-row partial-fill sensitivity gives mean interval distances EPA 33.132109 (33.13 pp) and OMNI 25.706365 (25.71 pp). The prior EPA 33.14 pp is not exactly reproduced. No undocumented rounding adjustment is applied to force agreement. Fully recomputed n=54 gives EPA 33.85 and OMNI 26.52 pp.

## Radiocarbon and denominator sensitivity

Twelve exact both-valid original CMB pairs have received numeric radiocarbon-derived intervals: nine State Building, two North Pole, one Peger. The native workbook labels I=max and J=min; the script preserves that order. These are derived wood-smoke percentage intervals, not raw radiocarbon observations or a universal truth standard.

| CMB denominator, n=12 | EPA interval distance / midpoint MAE, pp | OMNI interval distance / midpoint MAE, pp |
|---|---|---|
| Published Appendix C PM, primary | 13.72 / 17.75 | 13.34 / 17.49 |
| Summary-workbook PM, sensitivity | 13.73 / 17.76 | 13.36 / 17.51 |

The workbook-denominator sensitivity reproduces the earlier rounded radiocarbon results. For either denominator, EPA has 3 inside, 8 above, 1 below; OMNI has 2 inside, 7 above, 3 below. EPA is closer on seven dates, OMNI on four, with one tie. Only three primary exact dates have both marker structures: the brackets overlap on one and are disjoint on two. The radiocarbon assumptions described in Busby are not a measurement-confidence interval.

For levoglucosan, using native-workbook PM for CMB normalization changes small decimals (n=52 mean distances EPA 32.35, OMNI 24.72 pp) without changing the categorical counts. The aggregate JSON also exposes a 13.3-versus-13.27 conversion-factor sensitivity. Every variant is labeled; denominators are not mixed under one result label.

## Published-table extraction correction

Appendix C revised OMNI at Peger Road (PDF page 122) orders columns sulfate, nitrate, autos, diesel, fuel oil, wood smoke. The old parser reused the different State Building revised order. A site-specific field mapping corrects 108 cells across 26 valid Peger revised rows. Source-page visual inspection and two exact-row regression fixtures confirm the correction. Original EPA/OMNI rows, wood-smoke values, 107/94 pair counts, and the present wood-smoke comparisons are unchanged.

The current Cycle 02 manifest has refreshed hashes for the three changed CSV/parser/test files. Previously delivered ZIPs remain historical objects and are not claimed to have been regenerated with the correction.

## Scientific boundary

EPA and OMNI use different source universes/treatments; this is profile-system sensitivity, not an isolated one-profile substitution. Final per-alternative selectors, fit diagnostics, and source-native CMB controls remain unrecovered. The OMNI marker conversion factor partly depends on OMNI source experiments. Radiocarbon overlap is sparse and the marker structures do not agree on a uniform system preference. Therefore the external profile-choice accuracy gate remains HOLD.

This is a transparent reconstruction of publication-derived CMB outputs against received historical marker workbooks, not a clean-room rerun of CMB fitting. The active paper's scientific content is unchanged. Human review is required before adopting any manuscript result or changing the scientific baseline.
