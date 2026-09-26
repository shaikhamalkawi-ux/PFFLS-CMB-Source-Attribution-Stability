# Publication-derived supplementary-table extension, 26 September 2026

This extension does not add a new scientific analysis or change a reported result.
It adds three machine-readable transcriptions of existing R3nR8 supplementary
material so that the delivered inventory matches the manuscript's description:

- `derived_data/jrc_controller_publication_summary.csv`: the 12 displayed rows
  of Supplementary Table S4, including displayed precision only.
- `derived_data/jrc_common_sample_reported_summary.csv`: the reported aggregate
  common-362 outcome in Supplement S5. This is not the sample-level mask, any
  rerun output, or a reconstruction of the missing source-native analysis.
- `derived_data/epa_fresno_1989_05_10_publication_summary.csv`: five displayed rows
  from Supplementary Table S10. It does not contain all source contributions,
  and therefore cannot independently regenerate pairwise ranking changes.

The original release's 14 arithmetic checks remain unchanged. The additional
verifier checks consistency among the displayed tables and arithmetic; it does
not independently validate the original CMB fits, environmental accuracy, or
unavailable source-native records. SHA-256 values in the updated manifest cover
the extended release. Original release ZIP SHA-256:
`6e90b1d8e86914e9dc039ed4f38878c265c66525a9001acbd5386a23f6baa798`.

The sole change to the original reconstruction script pins CSV line endings to
LF, making output byte identities reproducible on Windows as well as Linux.
No numerical expression, selector, profile, datum, or result was changed.

## Verification and unresolved traceability

Run the original reconstruction and verification, then the supplementary check:

```
python code/reproduce_publication_derived_data.py
python code/verify_release.py
python code/verify_supplementary_consistency.py
```

The rounded primary landscape gives Spearman correlation 0.927726 between
point-reference error and one minus median R-squared, whereas the manuscript
reports 0.909. Displayed R-squared values contain ties that may arise through
rounding; the unrounded original outputs are absent, so the reported value cannot
be verified from this release. No replacement value has been inserted into the
manuscript. Similarly, median percent-mass values, the full secondary-selector
comparison ledgers, source-native EPA output rows and pairwise margin records
are not present. Their reported aggregate summaries are not independently
recomputed here. Do not call this package a complete source-native reproduction.
