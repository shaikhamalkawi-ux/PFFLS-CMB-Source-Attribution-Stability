# Source recovery and permitted-use checkpoint

Audit date: 26 September 2026. This is a recovery record, not a declaration that
every original fit has been reproduced or that third-party data are openly licensed.

## EPA: native inputs recovered

Four archives were recovered from the [official EPA CMB download page](https://www.epa.gov/scram/chemical-mass-balance-cmb-model):
`sjvf_data.zip`, `pacs_data.zip`, `epa-cmb82test.zip`, and `sourcecmb82.zip`.
The adjacent `source_recovery.json` records download URLs, response status,
archive hashes, and individual member hashes. Original archives remain outside
the repository. No downloaded executable or source program was executed.
The audit's new clean-room implementation is separate from those source files.

These objects provide stronger evidence than published aggregate tables. Their
presence alone does not identify the original analysis settings or prove the
reported result counts. Consult the native-reconstruction report for that test.

## Fairbanks: original private workbooks identified

The two Palmer workbooks were recovered through the authorized project Drive.
Their exact hashes match the earlier project identities. They and the private
prior-review evidence package were inspected read-only. Detailed rows, email
attachments, filter identifiers, and original Excel files are not in this public
return package. See `FAIRBANKS_REAUDIT.md` for the corrected aggregate result.

## Previous manuscript delivery archive

The recovered R3nR7 full-delivery archive hashes to
`e36d1a2b650cf33cd396736c00f7c5ad20237f742f3ef0afe92d49df50f9eee9`,
matching the project-state identity. Its top-level contents include manuscript,
journal and editable-source packages, a publication-derived provenance package,
and handoff/audit documents. This establishes that archive's identity; it does
not establish recovery of the original JRC computational ledger.

A bounded search of the project Drive's code-execution, manuscript-history,
active-baseline, direct-reconstruction, and archive folders did not recover a
new JRC raw computational archive. This is not a claim that none exists elsewhere.

## JRC: further download stopped at the displayed usage condition

On the [official DeltaSA portal](https://delta-sa.jrc.ec.europa.eu/html/public/home.jsf),
the Source Apportionment Model Performance panel offers INTERCOMP1, INTERCOMP2,
and INTERCOMP3 participant datasets. The visible panel states that downloading
accepts a DeltaSA-performance-assessment-only use condition, and other uses
require prior JRC approval. This condition was observed directly on 26 September
2026, before any dataset download from that panel in this audit.

No download was initiated, no terms were accepted on the author's behalf, no
results were uploaded to DeltaSA, and no permission request was sent. The site's
example result workbook is not treated as the true reference series. Public
access to a URL is not taken as permission to redistribute or for unrestricted use.

**HOLD:** further JRC source-native analysis or redistribution pending inspection
of any existing written permission or clarification of an applicable permitted
use. This checkpoint does not assert that a previous author obtained no permission;
no such approval was found in the inspected material. Record its scope if supplied.
The new diagnostics here operate on the existing author-owned published summaries,
not a newly acquired JRC dataset.

## Boundaries

KEEP the recovered identities and bounded checks. HOLD unsupported claims of full
raw-data reproduction, unrestricted third-party licensing, and field-accuracy
validation. No manuscript baseline, frozen Zenodo record, or upstream file has
been changed. This is a scientific provenance checkpoint, not legal advice.
