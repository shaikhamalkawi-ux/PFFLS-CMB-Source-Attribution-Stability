# Source acquisition and provenance boundary

## JRC Round-2 objects

A fresh official participant-package acquisition was provided on 22 August 2026 and recorded by SHA-256 without modification:

- `RM_INTERCOMP2_PACKAGE.zip` — SHA-256 `44d9ee67aa6dd89c93ea904c247fd1dea655a96796a56d12a26733cc52014778`
  - `RM_INTERCOM2_DB.xls` — `3da5366459fe5d20964bd65295989c3ac9663bc4c8a380baa6195b1f2fe0e7d2`
  - `RM_INTERCOM2_EMISSION _INV.xls` — `65379f7d609da65b4a9844b61996d586c666924a394020b026bb6b2328847885`
  - `RM_INTERCOM2_METEO.xls` — `d49abee0214f44a516666d9afb4f5151ef87c1b08c00b2dd7e9bfc6292e51959`
  - `RM_INTERCOM2_INSTRUCTIONS.pdf` — `da85f1eea6d3e42438bdc28bba6937cbebe66f46e9ba2823b67fc5f33dd29bb1`
  - `RM_INTERCOM2_RESULTS_blank.xls` — `f72cf7e08e43257440ac7c8c18ec14eff6586a820180cd12f91522a986015299`

The instructions identify Step 2 as a synthetic 2005 Milan PM2.5 dataset with 364 daily samples and 38 species and state that source contributions are known for evaluation. The participant package does **not** contain the a priori daily source-contribution reference series. It instead distributes the receptor dataset, meteorology, an emissions inventory, instructions, and a blank reporting template.

The archived scientific record separately identifies a source-profile workbook:

- `RM INTERCOM2 SOURCE PROFILES.xls` — `699c04cf1479b882b0b7cd523ba1e79fe1b1c1f6956cd67d8a6043cd111503ed`

That object is not a member of the newly acquired participant package and has not been silently reconstructed or substituted.

An earlier provenance record also listed an instructions-PDF hash `838c59a1e90f25fcb8186205c26ed8386b988141017da96466aef4fb1d9c081f`. The newly acquired official package member hashes to `da85f1eea6d3e42438bdc28bba6937cbebe66f46e9ba2823b67fc5f33dd29bb1`. Their byte lineage has not been resolved; they are therefore recorded as distinct provenance objects. The reported numerical results do not depend on instructions-PDF byte identity.

## Additional JRC acquisitions held outside the analytical evidence set

The following were also provided and recorded by SHA-256 but are not admitted to the current numerical analysis:

- `RM_INTERCOMP1_PACKAGE.zip` — `8025cb5d9df208e5ba91504c433925ee9d8a03904f1902fb0cf3e43a182da744`
- `RM_INTERCOMP3_PACKAGE.zip` — `e59f787b276a0f6e2241d89eb7ac5297295fd13f01a9eedceaf24520766322ee`
- `EXAMPLE_INTERCOMP2.xlsx` — `1e8ebb682647174214c8989def8e846f3126cb57be177542b90b0ad31a10dd86`

`EXAMPLE_INTERCOMP2.xlsx` is treated as a DeltaSA-format/example result object, **not** as canonical reference truth. Its `TREND (µg/m3)` matrix contains 344 dated rows and eight candidate-source columns; this is not the 364-sample a priori reference object required for a sample-level reference evaluation.

## Redistribution boundary

The newly acquired INTERCOMP2 instructions state that the documentation and dataset are copyright protected, that downloading accepts use for testing, and that other uses should be agreed with the organisers. Accordingly, these third-party binaries are **not redistributed** in the journal/reproducibility package. The release records exact source identity and hashes and retains acquisition instructions instead.

## EPA-CMB8.2 evaluation objects

The earlier project recovery notebook records the following official EPA locations:

- `https://www.epa.gov/sites/default/files/2020-10/sjvf_data.zip`
- `https://www.epa.gov/sites/default/files/2020-10/pacs_data.zip`
- `https://www.epa.gov/sites/production/files/2020-10/sourcecmb82.zip`
- `https://www.epa.gov/sites/production/files/2020-10/epa-cmb82test.zip`

The reproducibility release does not redistribute these third-party binaries. Deposit/reviewer packages should preserve exact acquired bytes and hashes from the canonical prior reproducibility archive when that archive is restored.

## Claim boundary

This package is sufficient to reproduce the derived tables reported in the manuscript and headline arithmetic from archived set-level summaries. It is not a replacement for the prior complete source-native computational archive and must not be described as a fresh source-native JRC/EPA rerun. The canonical 364-day JRC a priori source-contribution reference series also remains unrecovered and is not reconstructed from figures, OCR, participant outputs, or the DeltaSA example workbook.

## 22 August 2026 web-acquisition follow-up

A fresh search of the publisher and institutional records for Belis et al. (2015, Part II; DOI `10.1016/j.atmosenv.2015.10.068`) confirmed that the article explicitly states that the Round-2 synthetic dataset used known, unbiased, participant-independent reference values and identifies those values as **Supplementary Material S1**. The open article record also confirms that supplementary data are associated with the DOI. The present execution environment did not expose the supplementary binary through a stable machine-download endpoint, so the object was **not** substituted with participant/example output and was **not** reconstructed from figures or OCR.

Authoritative retrieval path to continue outside this runtime:

1. Publisher article record: `https://www.sciencedirect.com/science/article/pii/S1352231015304854`
2. DOI landing page: `https://doi.org/10.1016/j.atmosenv.2015.10.068`
3. Locate **Appendix A / Supplementary data** and retrieve the original Supplementary Material S1 object without renaming or editing it.
4. Hash the acquired file before inspection and verify that it contains the a priori Round-2 reference object rather than a participant-output example.

The JRC source-apportionment portal independently states that DeltaSA Model Performance uses a testing dataset and reference values generated in European Commission JRC intercomparison exercises. This supports the existence and role of the reference layer but does not by itself provide the raw 364-day reference series.

Current status: `CANONICAL_DAILY_REFERENCE_NOT_YET_RECOVERED`. This remains the only data acquisition that would justify opening a new sample-level scientific analysis.
