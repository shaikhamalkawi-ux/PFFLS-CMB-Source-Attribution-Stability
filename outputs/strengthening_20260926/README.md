# Evidence-strengthening review package — 26 September 2026

Status: **candidate evidence for independent review; not a new manuscript baseline**.
R3nR8 and the existing Zenodo v1.0.0 record remain unchanged.

## What materially improved

| Question | Audit finding | Decision |
|---|---|---|
| Can the EPA main counts be recomputed from native inputs? | First fixed-settings clean-room run reproduces 133/283 and 62/283, all attrition/subset counts, and the five worked-case runs at reported precision. | KEEP numerical reconstruction; not field-accuracy validation. |
| Can display rounding explain JRC 9/30? | Reconstructed 30-edge grid retains all classifications throughout the declared rounding intervals. | KEEP 9/30 at publication-summary level. |
| Does reference uncertainty leave 9/30 unchanged? | A rigorous sufficient L1-displacement certificate is available, but the actual joint reference-uncertainty region is not. | KEEP conditional diagnostic; HOLD unconditional robustness. |
| Do original Fairbanks outputs give 53 complete pairs? | They give 52. Partial endpoint completion gives 53; full positive-input recomputation gives 54. | Correct project-state wording; retain sensitivities separately. |
| Is the reported Spearman 0.909 wrong? | Three admissible strict refinements of displayed ties give 0.909. | Compatible, not independently verified; do not label it an error. |
| Can JRC originals be freely downloaded/republished? | The portal displays a purpose restriction and prior-approval requirement for other uses. | HOLD further use outside that scope until permission is documented. |

The strongest new result is **source-native EPA numerical reconstruction**, not
another manuscript version. It closes an important reproducibility gap while
leaving the scientific limits intact.

All **87 new audit tests pass locally**, including 13 native/private integration
tests. The full repository suite is **135/140 passing**: five historical Cycle04
tests still require superseded literal project-status strings. Those legacy
failures are disclosed, not suppressed, and do not occur in the new numerical
audits. The return package is reviewable, not a claim of globally green legacy CI.

## Read in this order

1. `EPA_NATIVE_RECONSTRUCTION.md` — model, frozen settings, comparisons, limits.
2. `CLAIM_AUDIT.md` — publication-derived JRC/EPA arithmetic and rounding checks.
3. `REFERENCE_ROBUSTNESS.md` — mathematical certificate and explicit assumptions.
4. `FAIRBANKS_REAUDIT.md` — original-workbook audit and 52/53/54 distinction.
5. `SOURCE_RECOVERY_STATUS.md` — identities, recovery scope, JRC usage checkpoint.
6. `LEGACY_TEST_STATUS.md` and `QA_SUMMARY.json` — regression and packaging checks.

## Scientific interpretation

For fixed fitted vectors a and b, moving the reference by L1 distance epsilon
changes their distance difference by at most 2 epsilon. With a conservative
one-displayed-unit envelope for the published scores, the nine-discordance
classification is certified unchanged for total L1 displacement **strictly less
than 0.047399 micrograms/m3**. This is a sufficient bound, not an estimated
uncertainty, a confidence interval, or the exact threshold at which a reversal
occurs. At an illustrative 1%-of-total budget, at least five discordances are
certified; that scenario is not an assertion about the true reference uncertainty.

Fairbanks still does not isolate one profile substitution: the EPA/OMNI source
systems differ, the conversion-factor reference is partly dependent on source
experiments, and radiocarbon overlap is sparse. More matched dates do not by
themselves overcome those design limitations. The correction to 52 does not
change the manuscript's reported analyses, which do not use these workbooks.

## Reproduction

Python 3.12.14 was used. Install the pinned optional numerical/spreadsheet
dependencies from this directory's `requirements.txt` if those audits are needed.
From the repository root (or the extracted return package root):

```text
python scripts/audit_strengthening_claims.py
python scripts/audit_reference_robustness.py
python -m unittest discover -s tests -p test_strengthening_claims.py -v
python -m unittest discover -s tests -p test_reference_robustness.py -v
python -m unittest discover -s tests -p test_source_recovery.py -v
python -m unittest discover -s tests -p test_epa_native_strengthening.py -v
python -m unittest discover -s tests -p test_fairbanks_strengthening.py -v
```

For EPA source-native reproduction, acquire the four exact official archives
listed in `source_recovery.json` using `scripts/recover_strengthening_sources.py`
with `--raw-dir` outside the repository and a **new separate** `--report` path.
Then pass that input directory to `scripts/audit_epa_native_strengthening.py`.
Source hashes are verified before fitting. The row-level reconstruction ledger
is written only under ignored `private/` and is not included in the public ZIP.

Fairbanks integration requires authorized copies of the exact two private
workbooks. Supply them to `scripts/audit_fairbanks_strengthening.py --input-dir`.
Public users without private/native inputs run synthetic tests; integration
tests skip explicitly. A skipped integration test is not a successful source
reproduction. No Excel workbook is modified or filled in by the audit.

## Candidate manuscript changes after review only

- Add a concise EPA clean-room reproduction statement and link the reviewed
  audit separately from frozen Zenodo v1.0.0. Do not imply the original historical
  executable or ledger was recovered, or that JRC/PACS were also rerun.
- Add the displayed-rounding check to the supplement. If the conditional
  reference certificate is included, keep its assumptions and limited scope.
- Preserve the distinction between internal fit, allocation stability, and
  accuracy against an independent environmental reference.
- Do not add Fairbanks as a validated profile-choice test or inflate the main
  dataset count. Preserve its reserve-evidence role.

No manuscript text or baseline was changed in this task. No PR was merged,
request sent, journal submission made, or Zenodo record updated.

## Licensing and exclusions

Under the corresponding author's approved terms, new original audit code/tests
and the package builder are MIT-licensed; author-owned audit documentation and
derived summaries are CC BY 4.0. The full texts are included in
`outputs/publication_archive_20260926/licenses/`. That frozen archive retains its
own scope notice. These grants do not relicense third-party raw data, source
code, dependencies, private Fairbanks material, or the rest of the repository.

No manuscript, biography, correspondence, private Excel file, raw third-party
archive, credential, or row-level private ledger is included in the public return.
