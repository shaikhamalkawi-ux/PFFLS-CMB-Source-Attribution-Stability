# PFFLS publication-derived consistency and provenance archive

## Scope

This curated data-and-code archive accompanies the study **Source Attribution Can
Change Despite Favorable Fit Diagnostics: Evidence from Source-Profile Choice in
Chemical Mass Balance** by Ghassan O. Malkawi, Ahmed Abdelaziz Elsayed, Mohammed
Alhagyan, and Bakeel Hussein. Archive version: `1.0.0`, corresponding to the
R3nR8 editorial package dated 26 September 2026.

It contains publication-derived summary tables, reconstruction and consistency
verification code, provenance records, and explicit reproducibility limitations.
It is **not** the manuscript, a new scientific analysis, a complete original CMB
computational archive, or an independent environmental accuracy validation.

The nested `publication_derived/` directory preserves all 21 files of the
previously released package byte-for-byte. Its source revision is
[`d72e1fcf4b878684187dd107fca53ac63400c20a`](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/tree/d72e1fcf4b878684187dd107fca53ac63400c20a/outputs/journal_editorial_20260926/publication_derived).
The wrapper adds citation, licensing, installation instructions, and a current
verification-environment record; it does not change the original numerical data.

## Contents

- The 12 reported JRC profile-set summaries, campaign-level point-reference
  vector, profile-admission crosswalk, and reconstruction of 30 local comparisons.
- Reported EPA substitution/attrition and outcome summaries, profile-family
  shifts, and a five-row worked Fresno example.
- A 12-row controller summary and one reported aggregate common-362 outcome.
  These are not sample-level rerun outputs or a reconstructed common-sample mask.
- Three Python scripts, a profile-choice traceability schema, source-acquisition
  records, historical environment information, and the original SHA-256 manifest.
- Outer citation and scoped license notices, dependency instructions, and current
  verification-environment information.

## Install and run

The current verification used Python 3.12.14 and pandas 3.0.1 on Windows 11.
Using a clean Python environment, run these commands from this archive directory:

```bash
python -m pip install -r requirements.txt
python publication_derived/code/reproduce_publication_derived_data.py
python publication_derived/code/verify_release.py
python publication_derived/code/verify_supplementary_consistency.py
```

The first command installs the sole direct third-party package dependency.
The reconstruction script writes three CSV files inside `publication_derived/`;
their bytes reproduce the supplied CSVs, including LF line endings. Run in an
extracted working copy if you want to keep the downloaded archive untouched.
The verification scripts only read the package and print their results.

Expected results:

- Reconstruction: 30 comparisons, including 9 lower-chi-square discordances.
- Original verifier: **14/14 publication-summary arithmetic checks** and
  **20/20 original manifest entries** pass.
- Supplementary verifier: **25/25 publication-summary consistency checks** pass.

The original verifier's inherited console phrase "scientific release checks"
denotes those 14 summary checks only. It must not be interpreted as validation
of the original CMB fits. The nested manifest covers 20 payload files, not itself;
the nested directory therefore contains 21 files. It does not cover this wrapper.

`verification_environment.txt` records the present run. The nested
`publication_derived/environment.txt` remains the distinct historical environment
record from 22 August 2026; its versions were not silently replaced.

## Reproducibility boundaries

The included scripts operate on supplied or explicitly embedded publication-level
summaries and do not require private data or unavailable original inputs. They
do not independently rerun the original JRC or EPA CMB analyses. The original
unrounded comparison ledgers, complete source-native executable archive,
sample-level reference series, and row-level EPA substitution outputs are not
included. Some reported statistics therefore cannot be independently recomputed
from this release. Read these original records before reuse:

- `publication_derived/REPRODUCIBILITY_LIMITS.md`
- `publication_derived/EDITORIAL_EXTENSION_SCOPE.md`
- `publication_derived/SOURCE_ACQUISITION_AND_PROVENANCE.md`

In particular, the rounded primary table gives a different rank correlation from
the reported unrounded result; the original unrounded outputs are unavailable.
The discrepancy is disclosed in the extension-scope record, not silently repaired.
The field-data component concerns sensitivity, not independently established
allocation accuracy.

## Exclusions and rights

This archive excludes the manuscript and supplement PDFs, journal correspondence,
cover letter, author biography files, private Fairbanks spreadsheets and emails,
and all third-party JRC/EPA binary source packages. No permissions to redistribute
those excluded source materials are asserted. Citations, source identities,
retrieval instructions, and hashes identify the upstream objects without copying
them into this deposit.

Author-owned data and documentation are offered under **CC BY 4.0**. Original
software is offered under **MIT**. These are scoped grants, not permission to
relicense upstream datasets, publications, software dependencies, or third-party
content. See `LICENSE_SCOPE.md` and `licenses/` for the exact scope and notices.

## Citation

Use the creator order, title, and archive version in `CITATION.cff`. Cite the
archive separately from the research article. The GitHub source revision above
identifies the preserved package; it is not a journal DOI.

Archive DOI: **10.5281/zenodo.22976190**
(https://doi.org/10.5281/zenodo.22976190).
Archive date: **26 September 2026**. This identifier was reserved before packaging
so that it could be included in these files. Publication status and the canonical
citation are provided by the Zenodo landing page. A DOI reservation alone does
not establish that a record is public or that DOI resolution is active.

Suggested citation upon publication:

Malkawi, G. O., Elsayed, A. A., Alhagyan, M., & Hussein, B. (2026).
*Publication-derived consistency and provenance package for Source Attribution
Can Change Despite Favorable Fit Diagnostics: Evidence from Source-Profile Choice
in Chemical Mass Balance* (Version 1.0.0) [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.22976190
