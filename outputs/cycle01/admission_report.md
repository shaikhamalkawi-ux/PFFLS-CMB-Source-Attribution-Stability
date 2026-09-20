# Cycle 01 admission report

## Decision

**HOLD.** No located campaign passes the eight required evidence gates for a
reproducible, profile-resolved comparison between a frozen CMB fit criterion
and an independent same-sample endpoint.

This is a failure of evidence completeness, not evidence that fit-favored
profiles agree or disagree with external truth. The locked manuscript baseline
remains **PFFLS R4.3.30R3nR7-AE**. No manuscript revision is proposed.

## Protocol

The admission rule was fixed by `tasks/CODEX_CYCLE_01.md` before screening.
An admissible campaign must expose, at sample/day level:

1. receptor chemical-speciation vector;
2. receptor uncertainty;
3. numerical source profiles;
4. source-profile uncertainty;
5. exact fitting-species and source selection;
6. sufficient CMB/EVLS implementation detail;
7. an independent reference for the same sample or exact interval; and
8. an unambiguous mapping from CMB output to that reference.

For the Cycle 01 question, the evidence must additionally permit a frozen
**source-profile choice** comparison and a present clean-room reproduction.
`scripts/validate_cycle01_evidence.py` enforces this rule without imputing
missing objects.

## Search and verification scope

The search prioritized project-controlled Drive material, EPA/agency archives,
state reports, publisher pages, PubMed Central/NCBI, university repositories,
and open journal archives. The complete URL, retrieval date, hash when bytes
were downloaded, and repository action are in `source_inventory.csv`.

The exact locked R3nR7-AE manuscript/source package was searched for by exact
version strings in the shared Drive tree. It was not found. Historical R3l,
R3f, R3a, and R2 files were therefore treated only as references and were not
renamed or used as the active manuscript.

The reviewed NFRAQS portable dossier was downloaded and independently rerun.
Its SHA-256 was
`e0b12c522aaf914803832ba66a1186155d5504fe3d091eeeaa973c488d4ef01e`.
The full pipeline and validator passed. The rerun reproduced:

- six profiles by 121 species, with paired one-sigma uncertainties and no
  imputation;
- Welby control reduced chi-square `0.6125054042990437`, R-squared
  `0.9188440945857521`, and percent mass `93.76721920463399`; and
- fit-only NWSOWHL reduced chi-square `0.5821002059331434`, R-squared
  `0.9221464531649032`, and percent TC `99.7883402055745`.

Those values verify the prior fit audit. They do not supply the missing CMB to
radiocarbon transformation and do not convert NWSOWHL into an external-accuracy
winner.

## Candidate findings

### NFRAQS, Denver

NFRAQS remains the closest profile-choice case because the receptor data,
uncertainties, six exact alternative wood profiles, profile uncertainties,
frozen fitting array, and EVLS calculation are available. The independent
radiocarbon side is also documented. The decisive gap remains the original
Chapter 7 arithmetic behind `fM(CMB)`: the source classification, carbon
conversion, numerator/denominator, source endmembers, inclusion rules, and
treatment of negative contributions are not stated. Constructing those choices
now would introduce outcome-aware analyst discretion. **HOLD.**

### Libby, Montana

The article publishes 19 dated radiocarbon measurements, dated grouped CMB
outputs, and 17 matched dates. It does not publish the daily receptor vectors
and uncertainties, numerical profile vectors and uncertainties, or exact daily
profile/species selections. The published CMB share is a PM-mass fraction,
whereas the radiocarbon result is a carbon fraction. The public record cannot
adjudicate alternative wood profiles. **HOLD.**

### Fairbanks, Alaska

The 171-page Alaska DEC report is a substantial near-case. It prints 91 source
profiles (including uncertainties), documents 43 candidate chemical species,
and tabulates final daily source contributions with standard errors. It also
states that multiple source-profile/species combinations were tried for each
sample until an optimal fit was obtained. The report does not release the
sample-level receptor chemistry/uncertainty matrix or an exact record of the
final profile/species selector for every sample. The comparison paper uses
radiocarbon and levoglucosan, but no complete input-to-endpoint package was
recovered. The outcome-guided selection cannot be reconstructed as a frozen
profile-choice test. **HOLD.**

### Diesel school buses

This is the strongest methodological positive control found. Eight bus runs
have source-specific synthetic tracers measured on the same runs. Larson et al.
publish the uncertainty-weighted PLS selection procedure, run-specific selected
species, CMB8.2 outputs, and comparison statistics. EVDA-CMB agreed more closely
with the tracer estimates than all-species EV-CMB for tailpipe and crankcase in
the reported analysis.

It still fails Cycle 01 for two independent reasons. First, the complete
101-species receptor/profile matrices and corresponding numerical
uncertainties were not recovered from the papers or accessible supplements.
Second, the intervention is **species selection**, not choice among alternative
source profiles. It cannot be repurposed post hoc into a source-profile test.
**HOLD as contextual methodological evidence.**

### Tennessee Valley and Shenzhen

Both studies compare CMB-derived carbon-source contributions with radiocarbon
evidence, but the publicly recovered material supports aggregate or
period-level interpretation rather than a complete profile-resolved rerun.
Neither supplied the full sample-level receptor/profile/uncertainty objects,
exact source/profile selectors, and endpoint crosswalk required by the protocol.
**HOLD.**

### Fresno Supersite

The open paper is a useful field CMB example, but it lacks a same-sample
independent source-discriminating endpoint. It is outside the Cycle 01 target.
**REMOVE from the admission set.**

## Falsification checks

- A published correlation, average agreement, or favorable fit diagnostic was
  not treated as an externally validated profile ranking.
- A same-campaign tracer was not accepted without a sample-level crosswalk and
  a defined unit/denominator mapping.
- A paper that changes fitting species was not relabeled as a source-profile
  choice experiment.
- Outcome-guided profile/species selection was not reconstructed as though it
  had been prespecified.
- Missing vectors, uncertainties, endmembers, denominators, and negative-value
  rules were not inferred from general domain conventions.
- Historical manuscripts were not substituted for the missing exact baseline.

## Conclusion

Cycle 01 found useful near-cases and one strong species-selection control, but
no admissible profile-resolved external-validation dataset. The correct stop
rule is therefore **HOLD**, with no new scientific claim and no candidate
manuscript revision.
