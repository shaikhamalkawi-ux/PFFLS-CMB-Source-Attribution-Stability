# Truth-bearing source-apportionment benchmark audit

Date: 2026-09-26 UTC. Status: primary-source and released-file audit; **no benchmark fits, decisions, or outcome comparisons have been run**. This is a bounded search, not evidence that an unlocated dataset does not exist.

## Current decision

**One usable numerical construction-truth benchmark was located, with limits that prevent treating it as a fully instrumented uncertain-profile CMB or field benchmark.** It is the openly released synthetic aerosol data accompanying Via et al. (2026), [*Chemical sparsity in Bayesian receptor models for aerosol source apportionment*](https://doi.org/10.5194/amt-19-2175-2026). Its release is [Zenodo 19223353](https://doi.org/10.5281/zenodo.19223353). Both article and dataset independently declare CC BY 4.0. Exact file inventory and HDF5 matrices have been inspected. Source-index ranking is usable; physical-unit and named-source mapping remain unresolved, and profile uncertainty is absent.

The paper constructs synthetic observations from specified source profiles and contributions plus noise. Such contributions are **construction truth**, not independently measured environmental source truth. The online case uses five organic-aerosol factors (HOA, BBOA, SOAbio, SOAbb, SOAtr), with CAMx-derived temporal templates and literature-derived profiles. This is external to the present historical EPA reconstruction, but remains an inverse-model simulation rather than a field validation. The paper's profile normalization convention is a unit-sum profile with mass-loaded contributions. These article statements alone do not establish the contents or units of any particular machine file.

Preselected bounded candidate, before examining any fitting results: `datasets/online_SDs/Zurich/Zurich_0.h5`. It is **not yet approved for analysis**. The `_0` suffix is not assumed to denote a replicate rather than a time segment until timestamps or a data dictionary establish that. No search for the easiest city, time segment, noise realization, or most favorable risk-coverage result is permitted.

## Released artifact and legal provenance

- Article: [HTML](https://amt.copernicus.org/articles/19/2175/2026/), [PDF](https://amt.copernicus.org/articles/19/2175/2026/amt-19-2175-2026.pdf). Published 2026-03-30. The article header explicitly declares Creative Commons Attribution 4.0.
- Dataset: *Datasets used in the BAMF+horseshoe manuscripts*, released 2026-03-25, DOI `10.5281/zenodo.19223353`. The independently retrieved [record API](https://zenodo.org/api/records/19223353) reports `access_right: open` and `license.id: cc-by-4.0`.
- Exact download: [datasets_bamf_horseshoe.zip](https://zenodo.org/api/records/19223353/files/datasets_bamf_horseshoe.zip/content).
- Published and observed archive length: **14,572,677 bytes**. Independently calculated MD5 agrees with the release: **f9865bf2c2259f1fdd32251c9560cf55**. Independent SHA256: **e4f6e055a3db15e22f7c0c449a84d2d23a1f86270d658ff3f1a63fc435367501**.
- Candidate-member SHA256: **fa62a734a1dda779df572e0c975e3103a2c9ad06d2a3eaffc2ed8affd3d89d64**. It can be read directly from the ZIP without extracting or executing anything.
- Preserved local original files: `_inputs/decision_research_20260926/truth_benchmark/datasets_bamf_horseshoe.zip` and `zenodo_19223353_metadata.json`. Metadata snapshot SHA256: **eb86d8feb02c8c935529463602d30fca54e46bf7d44290232df19fe8eef785c7**.
- Repository pointer supplied by Zenodo: [datasets directory](https://github.com/martavia0/BAMF-horseshoe/tree/main/datasets). Use the versioned Zenodo archive, not mutable `main`, for analysis provenance.
- No license is inferred merely from public GitHub visibility. Any later redistribution must retain dataset attribution and identify modifications separately from the original release.

### Machine-file inventory, independently inspected

The ZIP contains 35 HDF5 files and directory entries, with no README or field dictionary:

| ZIP path pattern | Count | Bytes per file |
|---|---:|---:|
| `datasets/toy_dataset/Toy_dataset.h5` | 1 | 132,344 |
| `datasets/megacity/Megacity_0.h5` through `_9.h5` | 10 | 498,128 |
| `datasets/online_SDs/Krakow/Krakow_0.h5` through `_5.h5` | 6 | 529,520 |
| `datasets/online_SDs/Milan/Milan_0.h5` through `_5.h5` | 6 | 529,520 |
| `datasets/online_SDs/Paris/Paris_0.h5` through `_5.h5` | 6 | 529,520 |
| `datasets/online_SDs/Zurich/Zurich_0.h5` through `_5.h5` | 6 | 529,520 |

**Important mismatch:** the article and repository README describe an offline synthetic dataset, but no file or folder identified as that case is present in either the inspected archive or the current repository tree. Do not silently relabel the megacity files as the four-source offline case. The online case is selected instead because its exact released file is present.

### Exact candidate endpoint mapping

Read with `h5py 3.16.0` and NumPy `2.3.5`, installed only in `tmp/decision_research_hdf5_deps`. The read-only inspector is `tmp/decision_research_hdf5_inspect.py`. It neither imports archive code nor decodes pickled/object data. Runtime dependencies are not part of the redistribution package.

| Meaning | HDF5 numeric dataset | Shape | Mapping / limits |
|---|---|---|---|
| Generating profile matrix `F0` | `F/block0_values` | 5 × 82 | Rows indexed by `F/axis1`; columns by `F/axis0` |
| Generating contribution matrix `G0` | `G/block0_values` | 336 × 5 | Columns indexed by `G/axis0`; rows by `G/axis1` |
| Synthetic receptor observations `X` | `data/block0_values` | 336 × 82 | Columns indexed by `data/axis0`; rows by `data/axis1` |
| Receptor error scales `sigma` | `error/block0_values` | 336 × 82 | Columns indexed by `error/axis0`; rows by `error/axis1` |

All four arrays are finite and strictly positive. The released groups are named `F`, `G`, `data`, and `error`, not fitted-model outputs. Their interpretation as generation inputs comes from their inclusion in the article's synthetic-data release together with its construction description. No fitted source vector is being relabelled as environmental truth.

The source axes contain only numeric IDs `[0,1,2,3,4]`. Do not map ID 0 to HOA or any other environmental name without an original mapping. The shared 82 channels are numeric mass-to-charge labels (13 through 115 with omissions), not the 16 chemical species of the unreleased offline case.

No root-level metadata, physical-unit attribute, named-source dictionary, profile-uncertainty array, or covariance matrix is present. Treat concentrations as **released simulation-scale units** unless original unit provenance is recovered. Raw `G0` coefficient ranking depends on source-specific profile scaling and is **not** the primary physical decision endpoint. The row axes have datetime-related attributes but are stored as 32-bit integers; do not turn them into calendar dates by guessing an epoch.

Root review resolved the endpoint before any fits: let `r[k]=sum_j F0[k,j]`, `P0[k,j]=F0[k,j]/r[k]`, and `M0[t,k]=G0[t,k]*r[k]`. Then `M0 @ P0 = G0 @ F0` exactly up to roundoff. The primary truth is `argmax_k M0[t,k]` and pairwise contrasts of `M0`: the **largest modeled integrated signal over the 82 released channels**, not total atmospheric source mass. Both matrices must be transformed together. This endpoint is invariant to arbitrary positive source-specific reparameterization `F'[k,:]=a[k]*F0[k,:]`, `G'[:,k]=G0[:,k]/a[k]`. Raw-G coefficient ranking may be reported separately with that label, never substituted for the primary endpoint.

Numerical scale sanity checks passed: compensated normalization preserves `GF` within `rtol=atol=1e-12`; source-specific factors `[0.5,2,3,0.25,4]` preserve the integrated-signal truth within the same tolerance and preserve all rowwise integrated-signal argmax identities. No fitted-method decisions were involved in these checks.

This supplies a realistic externally designed spectral mixing control with exact numerical source-index truth. It does **not** supply independent physical source measurements, verified named-source endpoint mapping, or empirical profile-error calibration. A zero-profile-error run is an oracle control; adding uncertain profile alternatives would be a new, separately declared simulation.

### Integrity caveat that prevents an off-the-shelf coverage claim

The row/column axes match exactly across the four matrices. Row axes are exactly integers `0..335`, despite datetime-related attributes. Profile row sums are `[0.981926732, 0.903950324, 0.810483439, 0.773449161, 0.892754982]`, not one. Do not independently renormalize `F`: that would change the contribution scale and potentially its leader.

The construction residual `(X - G0 @ F0) / sigma` is finite, with mean **-0.001628414** and population SD **0.026407500** over the released matrix. This is an **input integrity check, not a fitted-method score**. It is inconsistent with casually treating every released `error` entry as the actual standard deviation of an independent unit-standardized Gaussian generation residual. The original generator/noise-processing code was not in the dataset release or inspected repository tree. Do not rescale `sigma` to this empirical residual SD, because that would silently reverse-engineer a noise model from the evaluated realization.

Accordingly, the released file can support descriptive truth-index decisions, but **not an unqualified nominal-coverage experiment using its uncertainty field**. The following separately generated control is frozen before any method outcomes to make its noise law unambiguous.

## Frozen numerical-control design v2 — review required before execution

Frozen here before model runs; this is a proposed bounded protocol for root review, not a claim that execution was authorized or completed. Version 2 amends version 1 in response to root review on 2026-09-26: the endpoint is now scale-invariant integrated channel signal, and the extra noise-scale sweep is removed to bound computation. Only input-integrity results, not method outcomes, were available at this amendment. Any further amendment must be dated and state whether outcomes were already seen. No change may be justified by obtaining favorable performance.

**Inputs and sampling.** Use only the selected, hashed Zurich file, with the compensated `(P0,M0)` transformation above. Retain all 82 channels and the five anonymous source IDs in their released order. Primary external descriptive panel: all 336 released rows. Generated control panel: exactly rows `14*i`, `i=0..23`, regardless of their source labels or margins. Use 32 independent replicates; do not stop when a result becomes significant. NumPy `Generator(PCG64(2026092701))` generates profile directions; `Generator(PCG64(2026092702))` generates receptor noise. Save full RNG states and generated arrays privately before scoring. Profile and noise draws are common to every comparator.

**Finite profile family.** Draw four independent standard-normal `5 x 82` direction matrices in order. For each direction, form two alternatives `P0 * exp(plus_or_minus 0.15 * direction)`, rescaling each row to one so that every candidate uses the same integrated-signal contribution scale. Together with `P0`, these nine matrices define the frozen family. Within-candidate profile errors are zero: this tests **discrete profile-choice ambiguity**, not empirically calibrated EVLS profile uncertainty. The original historical EVLS solver is thus used in its zero-profile-error special case. Draw a fifth independent direction for the excluded-truth regime, with multiplier `0.30`, and the same row-sum normalization. Do not infer that any finite family represents all physically plausible profiles.

**Noise law.** Let `sigma0` be the released positive `error` array at the selected rows. Generate `X = M_true @ P_true + sigma0*Z`; supply `sigma0` to every method unless the regime explicitly underreports it. Draw `Z` once in shape `(32,24,82)` (replicate, row, channel), then independent common-error draws `a` in shape `(32,24)` from the same noise RNG. Here `sigma0` is a convenient external scale template; the Gaussian law is newly imposed, not attributed to the original release. Retain negative noisy observations; do not clip, redraw or delete them. Reuse `Z` across regimes for paired comparisons.

| Regime | Exact difference from the ordinary generated control |
|---|---|
| Included truth | `P_true=P0`; all five integrated-signal source contributions from `M0`; independent `Z` |
| Excluded profile truth | `P_true` is the fifth perturbed direction; it is not added to the nine-matrix candidate family |
| Correlated receptor error | Replace `Z[t,j]` by `sqrt(0.5)*a[t] + sqrt(0.5)*Z[t,j]`; methods still receive diagonal scales |
| Underreported uncertainty | Use the included-truth noise draw, but report `0.5*sigma0` to methods |
| Omitted source | Generate all five sources as in included truth; remove source ID 4 from every fitted profile matrix and from the fitting universe; score against the original five-source truth |
| Near-tied leaders | At each control row let `v=1.2*max(M0[row,:])`; replace integrated-signal contributions 0 and 1 by `v` and `0.99*v`, respectively; leave sources 2–4 unchanged |

**Required comparators.** (1) Historical EVLS numerical solver, selecting minimum weighted residual score within the same nine-profile family. (2) Ordinary joint-contrast uncertainty for that selected fit, retaining covariance terms. (3) A strong ordinary baseline that unions those joint-contrast candidate sets across the same accepted profiles. (4) The finite-ensemble point-leader union/abstention rule. Any continuous-box certificate must be a separately frozen fifth comparator; its exact feasible set, radius, profile normalization constraints and solver tolerances require root review and an implementation hash before scoring. It must not be presented as a novel generic optimization construction.

**Fixed operational rules.** Source ties use `abs(s_j-s_k) <= 1e-10*max(1,max(abs(s)))`; tied truths/outputs remain sets. Basic numerical failures and negative contributions are retained in the failure ledger, not silently clipped. A common residual gate is `Q <= chi2.ppf(0.95,82-p)` with `p` equal to the fitted source count; this is a synthetic operational gate, not transplanted EPA mass-closure or R-squared validation. For ordinary contrast intervals, use `V=(F W F.T)^-1` and simultaneous two-sided Bonferroni normal thresholds across the `p*(p-1)/2` contrasts. Freeze familywise alpha grid `[0.5,0.2,0.1,0.05,0.01,0.001]`. Singular matrices and empty/all-rejected families are explicit failures, never correct singleton answers or successful abstentions. The minimum-Q winner has an unconditional point-decision endpoint and a separate contrast-thresholded curve; these must not be conflated.

For a fit, its ordinary candidate set contains source `j` exactly when no joint-contrast interval proves another source larger (`upper(s_j-s_k) >= 0` for every `k`). The ordinary ensemble set is the union of those sets over accepted fits. The finite-point set is the union of the accepted fits' argmax sets. Covariance baselines declare a pairwise order only when its lower contrast bound is strictly positive; finite-point consensus requires it to hold in every accepted fit. Every empty ensemble remains a failure state. When no singleton is reported, wrong-singleton risk is **undefined**, not zero.

**Evaluation and falsification.** The primary comparison is paired wrong-singleton risk against singleton coverage, not an arbitrary accuracy score on different retained subsets. Also report source-truth-in-set coverage, mean set size, false pairwise orders, and failure frequency. Source IDs stay fixed; no label matching against fitted results. For uncertainty on generated-control differences, resample the 32 replicate IDs jointly across all methods (2,000 bootstrap resamples using `PCG64(2026092703)`); each replicate carries all 24 rows. Report the entire frozen grid. Mark a method practically dominated if another achieves no higher wrong-singleton risk with no lower coverage across its comparison range; do not claim an advantage from abstaining more. A finding that ordinary union-of-contrast intervals match the proposed construction, or that the finite point ensemble undercovers, is a decisive negative result. Misspecification failure is reported even if the fit gate remains acceptable.

## Prior evidence and bounded historical search

Local records were read first: `outputs/strengthening_20260926/SOURCE_RECOVERY_STATUS.md`, its archive inventory, and cycle 01–03 recovery inventories. Recovered native SJVF/PACS/CMB-test inputs provide original receptor/profile data but no known per-sample source contributions. Prior Fairbanks, NFRAQS, school-bus, and ARM field-data leads were not treated as newly discovered independent truth. JRC DeltaSA restricted raw data were neither downloaded nor used.

| Primary source | What it establishes | Benchmark gate |
|---|---|---|
| [NIST SP 305 supplement 18](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication305supp18.pdf), catalog record for Gerlach, Currie and Lewis (1982), *Review of the Quail Roost II Receptor Model Simulation Exercise*, SP48 pp. 96–109, NTIS PB86-207172 | Historical computer-generated intercomparison sets existed. | No machine release located in this bounded search. |
| EPA [*Air Quality Models Pertaining To Particulate Matter*](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=2000XDKH.TXT) | Discusses Quail Roost synthetic profiles, mixtures, and systematic source-profile contamination. | Tables are not a verified complete machine benchmark, and transcribing selected mixtures would constitute a new reconstruction. |
| Lowenthal et al. (1987), [*Quail Roost II revisited*](https://doi.org/10.1016/0004-6981(87)90033-3) | Relevant historical source-error and uncertainty study. | Publisher metadata/abstract inspected; no machine data located. Full text is not presently necessary because a licensed released candidate exists. |
| EPA [*Workshop on UNMIX and PMF as Applied to PM2.5: Final Report*](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=91010J2S.TXT), June 2000; [EPA workshop slides](https://www3.epa.gov/ttnamti1/files/ambient/pm25/workshop/sa.pdf) | Palookaville is a known-contribution synthetic exercise, unlike an ordinary field example. | Exact input/uncertainty/truth machine files not located. |
| RIVM report 863001006 (2007), [*Implementation of source apportionment using Positive Matrix Factorization: Application of the Palookaville exercise*](https://www.rivm.nl/bibliotheek/rapporten/863001006.pdf) | Documents a multi-source atmospheric-dispersion-based synthetic exercise and error generation. | Report alone is insufficient for exact reproducible comparison. |

These are nonrecoveries, not claims of nonexistence. No unrestricted license is inferred for an unpublished historical file. EPA PMF Baltimore examples remain field examples, not source-truth data.

## Gates before any benchmark run

1. Verify candidate HDF5 has the observation matrix, receptor uncertainty matrix, **generating** profile matrix and **generating** contribution matrix, with exact field names and orientation. A fitted or marker-derived table is not a substitute for construction truth.
2. Verify source labels and permutation mapping from machine metadata or original generator; do not align fitted factors to truth opportunistically. Verify measurement labels, timestamps, units and any normalization undoing.
3. Check positive finite uncertainty fields, dimensional consistency, missing-value conventions, row-sum conventions and construction residuals as integrity checks, not as method selection. Record every rejection without choosing another file based on performance.
4. Establish whether profile uncertainty is provided. If absent, `u_F = 0` is an **oracle known-profile control only**. Any added profile perturbation/ensemble is a declared researcher-generated experiment, not a released uncertainty field.
5. Freeze algorithm definitions, scenario grid, seeds, thresholds, pairwise contrasts, abstention rules, tie policy, infeasibility treatment and matched risk-coverage estimands before observing any method outcomes. The release is not a holdout if these are tuned to it.

## Protocol requirements irrespective of which data pass the gates

Compare the historical EVLS fit-winner with both (a) a conventional **joint contrast** uncertainty baseline using `Var(s_j-s_k) = V_jj + V_kk - 2 V_jk`, and (b) the declared set-valued decision/abstention construction. Marginal standard-error overlap is not an adequate conventional baseline. Give all methods the same declared source universe, observations, profile alternatives and admissibility filters; also include a known-profile oracle control where meaningful.

Use paired per-sample decisions. Primary outcomes are wrong-singleton risk among reported singletons, singleton coverage over **all** eligible samples, truth-in-set coverage, and mean/median set size. Report empty sets, nonconvergence, negative estimates, infeasibility and all-rejected cases separately; none count as correct abstentions or successful certificates. Report exact source ties as ties, not arbitrarily broken truths. Include pairwise-order false declarations and the fraction of possible pairwise orders certified.

Risk-coverage comparisons must use a frozen common threshold grid or matched coverage with a rule chosen before seeing outcomes. Do not claim superiority because one method reports less often. Use paired differences and uncertainty that respects dependence (time blocks for one released temporal realization; independent simulation replicate as the unit for regenerated simulations). Report the complete curve and tradeoffs, not only a favorable threshold.

Predeclare stress regimes: correct source universe/profile model; true profile included versus excluded from the ensemble; correlated receptor errors; underestimated uncertainty; an omitted source; and near-tied leaders. Conditional finite-ensemble unanimity makes no probabilistic coverage promise under misspecification. An honest result may be universal abstention, identical outputs to the ordinary baseline, or worse risk at matched coverage. Any of these would falsify a claimed practical upgrade.

## Current limitations

No controlled physical-mixture dataset with independently measured atmospheric source contributions has been recovered. A synthetic released benchmark can test computational correctness and calibrated operating characteristics under its construction, not establish general field truth. Even a successful decision benchmark would not establish novelty of generic robust optimization or consensus partial orders; the primary-source novelty audit still applies.
