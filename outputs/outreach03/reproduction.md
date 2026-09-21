# Outreach 03 reproduction

Requirements: Python 3.12 or newer; standard library only.

From the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate_outreach_package.py
python scripts/build_outreach_package.py C:\path\to\destination
```

The builder writes `outputs/outreach03/SHA256SUMS.txt`, creates
`PFFLS_CODEX_OUTREACH_THREE_REQUESTS_RETURN.zip`, and writes a sidecar named
`PFFLS_CODEX_OUTREACH_THREE_REQUESTS_RETURN.zip.sha256.txt`.

Build twice into separate empty destinations. The two ZIP SHA-256 values must be
identical. The ZIP contains only repository text/code artifacts; it contains no
email-provider export, private credential, manuscript binary, or third-party raw
file.
