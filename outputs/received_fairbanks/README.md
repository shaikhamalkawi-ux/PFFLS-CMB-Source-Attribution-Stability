# Fairbanks received-data independent audit - 2026-09-25

Review candidate under Issue #9, not a new scientific manuscript version. The accepted scientific submission baseline remains R3nR8-AE. See `AUDIT_REPORT.md` for the corrected cohort definitions and claim boundaries, and `AUTHOR_CHANGE_NOTE.md` for the separately requested author-list update.

## Reproduce

Tested with CPython 3.12.14 and openpyxl 3.1.5. Install the latter only if absent: `python -m pip install openpyxl==3.1.5`.

From the repository root, with the investigator-supplied archive available privately:

```text
python scripts/audit_received_fairbanks.py --input-zip <original-private-attachment.zip> --output-dir private/received_fairbanks/independent_reproduction --public-summary outputs/received_fairbanks/aggregate_summary.json
python -m unittest discover -s tests -p "test_received_fairbanks*.py" -v
```

Set `FAIRBANKS_RECEIVED_ZIP` to that same original archive to enable the optional input-hash-guarded integration test. No private inputs are downloaded automatically. The audit refuses an archive or member whose SHA-256 differs from the registered receipt. It opens each workbook read-only in formula and cached-value modes, never saves it, and never evaluates its formulas.

`aggregate_summary.json` contains no sample dates, filter identifiers, cell-level records, or email addresses. Detailed source evidence, exclusions, exact site/date matches, and sensitivity rows go only to the ignored `private/received_fairbanks/` tree. Do not add that tree or the source XLSX/ZIP to the public repository. Redistribution permission has not been established.

The derived marker bracket uses exactly 9.01 and 13.27. A quoted approximate 13.3 is not substituted silently. Formula/cache agreement is tested; missing native endpoints remain missing in the primary analysis. Counts of native Excel dates and text-date candidates are reported separately.

## Review package

The private Drive return contains the author-update PDF/source, audit code and public aggregate/report, original hash-locked receipt, and private row-level evidence. The builder uses an explicit allowlist and a per-member SHA-256 manifest. This is a private review bundle, not a journal-ready redistribution archive. Do not upload the bundle to GitHub or make it public.

No merge, manuscript scientific-result insertion, ADEC request, collaborator email, or journal submission is performed by this audit.
