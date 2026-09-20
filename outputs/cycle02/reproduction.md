# Cycle 02 reproduction

## Requirements

- Python 3.9 or newer (standard library only)
- Poppler `pdftotext`
- The source files listed and hashed in `source_inventory.csv`

Keep third-party PDFs and EPA source ZIPs outside the repository. The commands below assume a local input directory.

## Extract

```powershell
python scripts/extract_cycle02_fairbanks.py `
  --ward-pdf <Ward_2013_Fairbanks_CMB_Final_Report.pdf> `
  --aqs-spec-zip <daily_SPEC_2008.zip> `
  --aqs-spec-zip <daily_SPEC_2009.zip> `
  --aqs-mass-zip <daily_88502_2008.zip> `
  --aqs-mass-zip <daily_88502_2009.zip> `
  --out-dir outputs/cycle02
```

Expected counts:

- 294 Appendix C rows;
- 107 EPA/OMNI matched site/date rows;
- 1,951 AQS 43-species candidate rows;
- 47 AQS SASS mass cross-check rows.

## Test

```powershell
python -m unittest discover -s tests -p "test_cycle02_fairbanks.py" -v
```

The tests verify numeric/standard-error parsing, low-mass exclusion, and the fail-closed system-sensitivity label.

## Interpretation boundary

`aqs_state_building_receptor_candidates.csv` is not declared to be the exact historical CMB input. The exact CMB receptor uncertainty vector, final fitting-species set, day-level profile selector, and external-reference sample IDs remain missing. Reproduction therefore stops before any alternative-profile rerun.
