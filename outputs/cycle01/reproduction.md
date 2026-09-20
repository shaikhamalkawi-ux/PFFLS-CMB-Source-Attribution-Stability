# Reproduction instructions

The Cycle 01 repository checks use only the Python standard library.

From the repository root:

```powershell
python -m unittest discover -s tests -v
python scripts/validate_cycle01_evidence.py `
  --candidates outputs/cycle01/candidate_campaigns.csv `
  --inventory outputs/cycle01/source_inventory.csv `
  --output outputs/cycle01/admission_summary.json
```

Expected decision: `HOLD`, with zero KEEP campaigns.

To retrieve and verify the three public audit inputs outside the repository:

```powershell
python scripts/fetch_cycle01_sources.py C:\path\outside\repository
```

The retrieval script deletes a newly downloaded file if its SHA-256 differs
from the recorded digest. Downloaded third-party bytes must not be copied into
this public repository merely because the fetch succeeds.

## NFRAQS dossier rerun

The reviewed dossier is stored in the project-controlled Google Drive and is
not duplicated here. After downloading it outside the repository, verify:

```powershell
Get-FileHash -Algorithm SHA256 PFFLS_NFRAQS_EXTERNAL_VALIDATION_R4_PORTABLE_REVIEWED_FINAL.zip
```

Expected SHA-256:

```text
e0b12c522aaf914803832ba66a1186155d5504fe3d091eeeaa973c488d4ef01e
```

Extract the archive and execute its `RUN_ALL.ps1`. The 2026-09-20 clean-room
rerun completed successfully and its validator returned PASS. This verifies
the dossier's released calculations, not the absent historical CMB-to-fM rule.
