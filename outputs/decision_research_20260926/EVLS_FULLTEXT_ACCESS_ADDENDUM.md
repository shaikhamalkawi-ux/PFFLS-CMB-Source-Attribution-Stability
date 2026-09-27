# Dated addition: EVLS full-text comparator check

2026-09-27 00:17 UTC. This additive note supersedes only the **access limitation**
in the frozen EVLS audit and scientific disposition. Those historical files,
their hashes, and every experiment remain unchanged.

The complete main article, equations and references of Chen et al. (2025),
*PMF Source Contribution Uncertainty Estimation via Effective Variance Least
Squares*, ACS ES&T Air 2(12), 3045-3053, were read through normal licensed access.
No supporting-information audit, article download or redistribution is claimed.
[Official article](https://doi.org/10.1021/acsestair.5c00312).

Section 2.2 converts DISP width to relative profile uncertainty using
`100% * (maximum - minimum) / mean`, then uses PMF-derived profiles in EVLS.
Section 3.1 reports 604 solvable cases among 837 observations; 233 remain
unsolved. Section 3.2 discusses negative daily estimates and collinearity.
Section 3.3 evaluates reconstruction of observed species concentrations, not
independently known source contributions. Section 4 acknowledges fixed-profile
and nonconvergence limitations. These are reported study properties, not new
PFFLS calculations. [Methods and results](https://doi.org/10.1021/acsestair.5c00312).

**Our assessment:** a DISP range-based relative uncertainty is not automatically
a calibrated standard deviation. Equation notation and the released R
implementation also require reconciliation before claiming exact pipeline
equivalence. We have not reproduced that pipeline or estimated its coverage.
Better internal reconstruction alone does not establish correct source shares.
Retain this relevant comparator and the ordinary-contrast qualification; do not
claim superiority, a newly invented uncertainty propagation method, or new
physical ground truth. Article rights remain distinct from the separately
licensed [software record](https://doi.org/10.5281/zenodo.17767035).

Original audit note: CC BY 4.0. This licence does not cover the cited article.
