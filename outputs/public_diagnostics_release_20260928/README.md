# PFFLS source-profile sensitivity diagnostics

**JRC family structure and EPA rank margins — version 1.0.0, 28 September 2026.**

Release creator: Ghassan O. Malkawi, ORCID [0000-0002-5320-7561](https://orcid.org/0000-0002-5320-7561).

This public code-and-derived-results increment describes sensitivity of archived chemical-mass-balance source-attribution results. It contains no manuscript or new manuscript-authorship declaration. The manuscript author list remains unchanged. The new release creator is distinct from the authors of the unchanged upstream materials; their attribution is retained in [UPSTREAM_ATTRIBUTION.md](UPSTREAM_ATTRIBUTION.md).

## Scientific contribution and limits

The JRC component re-evaluates the complete fixed grid of 12 archived profile combinations and 30 comparisons from two previously published scalar-summary tables. All nine reported discordances occur among the 18 wood-profile comparisons; none occurs among the 12 vehicle-profile comparisons. This locates the previously observed discrepancy. It neither reconstructs missing fitted source vectors nor demonstrates a chemical mechanism, population frequency, source-family reliability, or environmental accuracy.

The EPA component reports exploratory descriptive margins from previously saved reconstructions. There are 345 eligible substitutions, 323 converged outcomes, and 22 nonconverged outcomes retained as exclusions, not silently removed from the denominator. The two-diagnostic subset contains 283 substitutions; 62 largest-source changes span 22 samples. The stricter subset contains 26 substitutions over four samples, and its two largest-source changes occur on one sample. For the group of 62 changes, median within-fit leading gaps are 1.63% and 3.19% of measured ambient PM, and the median unhalved whole-allocation absolute change is 23.20%. These are descriptive magnitudes, not significance tests, uncertainty intervals, transferred mass, independent validation, or policy-loss measurements. Small-group aggregates can reveal event-level magnitudes; they are not an anonymization guarantee.

This is retrospective post-review interpretation, not a pre-outcome superiority trial. No new native model fit, optimization, random draw, bootstrap, or measurement was used for this increment. The earlier finite-union and Lake negative findings remain unchanged and are not presented as positive evidence here. No claim of revolutionary novelty or a superior estimator is made.

## Contents and reuse

The archive preserves the original repository-relative paths and exact bytes of four scientific source/test files, two upstream-derived journal-editorial CSV tables, and four saved aggregate-result files. The CSV content comes from the earlier collaboration; the preserved journal-editorial line-ending representation is not byte-identical to the older Zenodo container. Public-release documentation and packaging/verification code are at the extracted root. `PACKAGE_INVENTORY.json` identifies each payload, its SHA-256, its role, and its license. `SHA256SUMS` covers every payload and the inventory; the separately supplied ZIP sidecar covers the complete archive.

Python 3.12 or later, standard library only, is recommended. Extract the archive into an otherwise empty directory, open a terminal there, and run:

```text
python verify_public_release.py .
```

Use the **Zenodo release ZIP** for this byte-preserving verification. GitHub provides source and review history, but Git checkout settings can normalize the older tracked CSV line endings and thus change their hashes without changing their table contents. A generic Git clone is not asserted to preserve those historical working-file bytes. Do not change the producer's input pins or rewrite the old record to force a check to pass. `build_public_release.py` is a maintainer packaging tool requiring the exact pinned source inputs; failure on a differently normalized checkout is expected and is not repaired by silently relaxing the hashes.

This read-only verification checks every inventoried byte, manifest membership, and the saved JRC arithmetic by calling `analyse()` in memory. It does not call the producer's write-enabled `main()`, refit a model, or execute a test suite. The JRC comparison is repeatability of the supplied arithmetic, not an independent algorithmic validation. The expected EPA status is `NOT_REPRODUCED_MISSING_EXTERNAL_INPUTS`, explicitly listed separately from successful archive and JRC checks. A successful verifier exit is **not** a claim of native EPA or JRC reproduction.

The EPA artificial-fixture tests can separately be invoked with `python tests/test_epa_rank_margins.py`; they test algebra on invented data, not the real experiment. The preserved JRC fixture file contains an original environment-specific assertion that the extraction root is named `PFFLS-CMB-continuous-20260927`. Consequently, its whole test suite is not advertised as portable or all-passing under arbitrary extraction-directory names. Do not run broad repository test discovery or infer native-data validation from fixture results.

Do not run either producer to overwrite the included result files. Both preserve historical outputs and require a deliberately separate reconstruction context. The EPA producer needs seven exact external objects, including a private ledger and the original execution-plan object; these are not supplied. See [DEPENDENCIES.md](DEPENDENCIES.md). This archive is **not a self-contained native-data reproduction package**.

## Licensing, attribution, and status

Original included code uses MIT; original derived summaries and documentation use CC BY 4.0. Rights are assigned file by file in the inventory. The prior code copyright notice is preserved verbatim; the upstream CSV attribution remains Malkawi, Elsayed, Alhagyan, and Hussein, [Zenodo DOI 10.5281/zenodo.22976190](https://doi.org/10.5281/zenodo.22976190). These grants do not relicense third-party inputs. See [LICENSE_SCOPE.md](LICENSE_SCOPE.md).

No manuscript, manuscript source, figure, private row-level ledger, private correspondence, raw receptor/profile data, or restricted fulltext is redistributed. Missing JRC original fitted vectors and execution provenance remain a scientific limitation. This release is an evidence increment, not journal-submission approval, baseline promotion, or a replacement of the upstream frozen record.

The repository is [PFFLS-CMB-Source-Attribution-Stability](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability). Use this increment's `CITATION.cff` when citing the increment; cite the prior four-author record when using its underlying tables. The new increment's reserved DOI is [10.5281/zenodo.23019083](https://doi.org/10.5281/zenodo.23019083). Reservation is not itself publication: the public landing page and final deposition receipt determine whether the record has been published.
