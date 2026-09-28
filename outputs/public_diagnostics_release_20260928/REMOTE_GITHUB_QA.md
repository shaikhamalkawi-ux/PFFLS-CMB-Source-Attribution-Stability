# Independent GitHub publication and full-download verification

**PASS.** Checked through anonymous official GitHub REST endpoints and complete asset downloads on **28 September 2026 at 15:40:08 UTC**. This review made no authenticated request, network-state change, scientific execution, archive rebuild, or file substitution.

## Release and source identity

- Published [release `diagnostics-v1.0.0`](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/releases/tag/diagnostics-v1.0.0), release ID `398389456`, title `PFFLS diagnostics companion v1.0.0`.
- `draft=false`, `prerelease=false`; published at `2026-09-28T15:38:30Z`.
- The tag reference points to annotated tag object `24cf5dec42ce3653a39b74ab1134553d653f44e4`. Independently dereferencing that object gives commit **`f474e265352fa907e94edb85ceec355551f32963`**, matching the reviewed source commit.
- The release API's historical `target_commitish` field says `main`; it does not override the actual existing tag target. The verified tag object, not that display/default field, establishes this release's source commit.
- Release notes name **Ghassan O. Malkawi** as creator of the new code/derived-summary companion only and preserve the paper author list and earlier collaborative attribution. They distinguish the explicit curated asset from GitHub's automatically generated whole-repository archives.

## Actual public asset downloads

Exactly three uploaded release assets were present. Downloaded each complete file once from its returned public `browser_download_url` into a fresh local temporary subfolder with basename `pffls-github-roundtrip-20260928-8f3c1e54`, outside the Git repository. Independently computed SHA-256 over the downloaded bytes and compared it with both the local reviewed original and GitHub's reported digest. All three sizes and hashes matched.

| Asset | ID | Bytes | Full downloaded SHA-256 |
|---|---:|---:|---|
| [PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/releases/download/diagnostics-v1.0.0/PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip) | 595756696 | 50,396 | `87446073a89c34f6614f6eab77c12d3c908cec86d154277cd721a34a171ef3a0` |
| [PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip.sha256](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/releases/download/diagnostics-v1.0.0/PFFLS_PUBLIC_DIAGNOSTICS_20260928_v1.0.0.zip.sha256) | 595756873 | 111 | `69c0956ca522cb8c06301d7ee49345afbc551fd6e4e1cafca98a9ff5a6f02dba` |
| [PUBLIC_ARCHIVE_QA.md](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/releases/download/diagnostics-v1.0.0/PUBLIC_ARCHIVE_QA.md) | 595756894 | 4,583 | `e87a6a6ac4f4d8681370bba419ac4899023b10ca499a66f76e183a109792fe05` |

This is full downloaded-byte verification, not merely a comparison of remote metadata. The returned API asset states were all `uploaded`. No automatically generated source archive was substituted for the curated ZIP. The downloaded ZIP was not extracted or scientifically executed again; the original independent local archive review remains in `PUBLIC_ARCHIVE_QA.md`.

## Pull request state

The anonymous [PR #16 record](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/pull/16) reports:

- State: `open`; `merged=false`; `merged_at=null`.
- Base: `codex/decision-certificates-20260926`.
- Head: `codex/public-diagnostics-20260928`.
- Head commit: `f474e265352fa907e94edb85ceec355551f32963`.

The API also returns a test merge-commit SHA for the open PR; that field is not evidence of a completed merge. No merge was performed in this verification.

## Boundaries

This verifies the GitHub release and three assets at the stated time, not permanent immutability of the mutable GitHub release. It does not establish Zenodo publication or DOI resolution; those require a separate final check. Publication of these descriptive results does not close the missing EPA public-input chain or JRC native provenance gap and is not journal submission, manuscript-author modification, baseline promotion, or evidence of method superiority.
