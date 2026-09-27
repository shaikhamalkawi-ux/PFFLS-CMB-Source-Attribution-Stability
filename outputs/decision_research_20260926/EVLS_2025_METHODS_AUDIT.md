# Chen et al. (2025) EVLS methods access and comparator audit

Date: 2026-09-26 UTC. Status: **ARTICLE ABSTRACT-ONLY; FULL-TEXT METHODS AUDIT HOLD**.

This is a bounded primary-source access/methods check, not a new experiment. It does not modify the frozen interval, ordinary-contrast, or Interim02 artifacts. No model was fitted, released code executed, software installed, message sent, institutional login used, purchase made, or full text saved or redistributed.

## 1. Exact source, access, licence, and read depth

Chen et al. (2025), *PMF Source Contribution Uncertainty Estimation via Effective Variance Least Squares*, **ACS ES&T Air 2(12), 3045-3053**, DOI [10.1021/acsestair.5c00312](https://pubs.acs.org/doi/10.1021/acsestair.5c00312).

The indexed primary publisher page identifies purchase-only access and states that the reader lacks access. Direct retrieval also returned HTTP 403. Exact-DOI/title searches for an authorized public repository or manuscript copy did not recover full text. This is an access result for this bounded search, not proof that no lawful copy exists anywhere. Retrieval stopped at that boundary; no alternative access-control route was attempted. No open article reuse licence was verified.

The publisher abstract describes daily Tianjin PM2.5 source apportionment, using PMF DISP intervals as profile-uncertainty inputs to EVLS, and improved reconstruction of measured concentrations. The abstract does not provide the conversion or validation details needed below. The article body, equations, supporting information, and bibliography were **not read**. [Publisher source](https://pubs.acs.org/doi/10.1021/acsestair.5c00312).

Separately, the associated [Zenodo software record, DOI 10.5281/zenodo.17767035](https://zenodo.org/records/17767035), was read afresh, including its archive preview. It links the exact article and supplies two R scripts plus four input CSV **templates**, not a released Tianjin truth dataset. Actual archive: `EVLS_CMB_code.zip`; published MD5: `120453456bb51d2d00d3a07a8ae12bf4`. The earlier source audit in `BENCHMARK_GAP_SEARCH.md` verified CC BY 4.0 through the record API and inspected the matching archive in memory. This check did not repeat that download or source inspection. The current rendered HTML licence field was blank, so the CC BY statement here is explicitly inherited from that documented API check. The software licence does not establish permission to redistribute the article. [Software record](https://zenodo.org/records/17767035).

## 2. Requested methods questions and evidence limits

| Question | What can be supported now | What remains HOLD |
| --- | --- | --- |
| Exact DISP-to-profile-SD conversion | The abstract connects DISP intervals to profile uncertainty. | Transformation of asymmetric limits; divisor or probability level; absolute versus relative scale; treatment of zero/swapped factors; species dependence. No formula is reconstructed from snippets. |
| Covariance interpretation | Previously inspected released code computes an inverse weighted normal matrix after effective-variance iteration. | The article's derivation, qualifications, and any correction beyond the release cannot be checked. |
| Coverage | The released calculation can be described as a conditional plug-in covariance. | Frequentist calibration, simultaneous coverage, or a joint posterior is not established by that formula alone. Whether the paper studies these is unverified. |
| True-source validation | Receptor reconstruction is the reported abstract-level endpoint. | Reconstruction error is not independent knowledge of source contributions. Any separate known-source or independently measured source validation in the unread body remains unverified, not declared absent. |
| Comparators | The public release gives a concrete established EVLS implementation to acknowledge. | The complete article comparison set, ablations, and performance against alternatives cannot be audited without the full text. |

The unresolved cells are **read-depth limits**, not criticisms of an unread article.

## 3. Released-code evidence versus our ordinary comparator

The existing full-source inspection documented in `BENCHMARK_GAP_SEARCH.md` reports that `EVLS_CMB_core.R` uses diagonal effective variances

`v_i = sigma_C,i^2 + sum_j(s_j^2 sigma_F,ij^2) + 1e-30`,

iterates unconstrained weighted least squares, and returns covariance `(F' W F)^-1` using the available iteration weights. It has no profile cross-covariance input; its supplied standard errors do not themselves integrate a joint distribution over uncertain profiles and contributions. The inspection also recorded no explicit nonnegative constraint and no explicit convergence flag at the iteration cap. These are observations about the release, not claims about every analysis in the article.

This check read `ORDINARY_CONTRAST_BASELINE_PLAN.md` completely and inspected the relevant functions in `scripts/audit_ordinary_contrasts.py`. Our baseline already:

- replays the frozen native fit's final-solve effective weights in its retained source universe;
- uses `variance = uc**2 + uf**2 @ s**2`, so it includes profile-error terms and is **not receptor-error-only WLS**;
- computes `(F' W F)^-1` by weighted-design SVD, without residual chi-square rescaling;
- uses the off-diagonal covariance in `Var(s_j-s_k) = V_jj + V_kk - 2 V_jk` and nominal Bonferroni contrast summaries;
- explicitly treats the final weights, source selection, and source pruning as fixed, without claiming validated coverage.

Thus the algebraic plug-in covariance mechanism documented in the released EVLS code is already represented by our comparator's central construction. This does **not** establish implementation equivalence: initializations, iteration rules, source universes, input-uncertainty provenance, numerical safeguards, and PMF/DISP preprocessing differ or have not been reconciled. In particular, we have not reproduced Chen et al.'s PMF-to-DISP-to-EVLS pipeline.

There is no current evidence that simply adding this release as another covariance calculation would supply a fundamentally omitted joint-uncertainty method. Conversely, there is not enough article access to certify comparator completeness or claim superiority. A faithful description of our existing baseline is **conditional plug-in source-contrast covariance at the fitted EVLS weights**.

## 4. Decision and next gate

**KEEP:** Acknowledge the published PMF/EVLS contribution-uncertainty approach and released implementation as relevant prior work. Retain the ordinary contrast comparator and its explicit limitations. Do not frame established EVLS propagation of profile errors as newly invented here.

**HOLD:** Exact DISP-to-SD mapping; claims about the article's coverage, true-source validation, or complete comparator set; faithful numerical replication of the paper; any assertion that the interval construction outperforms this paper's entire method.

**NO-GO for new computation in this task:** No fitting, additional datasets, substitutions from a different paper, or package execution. If lawful full text is later supplied, a new read-only audit can resolve the missing details before any separately approved comparison protocol. Until then this report is an access-limited methods note, not a completed full-paper review.

Bounded search completed within the allocated 30 minutes. Frozen scientific outputs and original manuscript files are unchanged.
