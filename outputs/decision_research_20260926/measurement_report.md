# Frozen held-out measurement feasibility experiment

Exploratory screening of a finite historical model set; no confidence, source-truth or novelty claim.

Selection saved at `2026-09-26T19:51:42.655481+00:00` before evaluation started at `2026-09-26T19:52:12.879160+00:00`.
Immutable selection SHA-256: `74bcc1403d63d123ee122b8fdea7315c84ef20f497caeb8f60ea20f42a9fa551`.

## Design and attrition

```json
{
  "samples": 35,
  "attrition_totals": {
    "grid_rows": 3900,
    "unresolved_rows": 1102,
    "central_basic_eligible": 35,
    "basic_rows": 2177,
    "negative_rows": 59,
    "invalid_contribution_rows": 0,
    "physical_rows": 2118,
    "tied_top_rows": 0
  },
  "statuses": {
    "NO_CROSS_TOP_PAIRS": 6,
    "SELECTED": 29
  },
  "selection_counts": {
    "SUXC": 17,
    "ZNXC": 12
  },
  "candidate_status_counts": {
    "SUXC": {
      "VALID": 35
    },
    "CUXC": {
      "VALID": 35
    },
    "ZNXC": {
      "VALID": 35
    }
  }
}
```

## Evaluation

Fixed-candidate rows include all evaluable samples; selected rows include only samples with a preselected candidate. Matched comparisons below remove that denominator difference.

| Cutoff | Strategy | Evaluable samples | Baseline ambiguous | Nonempty top-set reductions | Resolved to one top | All rejected | No top-set reduction |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | selected | 29 | 29 | 5 | 5 | 5 | 19 |
| 1 | SUXC | 35 | 29 | 6 | 6 | 9 | 20 |
| 1 | CUXC | 35 | 29 | 0 | 0 | 14 | 21 |
| 1 | ZNXC | 35 | 29 | 5 | 4 | 7 | 23 |
| 2 | selected | 29 | 29 | 3 | 3 | 1 | 25 |
| 2 | SUXC | 35 | 29 | 2 | 2 | 2 | 31 |
| 2 | CUXC | 35 | 29 | 0 | 0 | 4 | 31 |
| 2 | ZNXC | 35 | 29 | 1 | 1 | 0 | 34 |
| 3 | selected | 29 | 29 | 0 | 0 | 0 | 29 |
| 3 | SUXC | 35 | 29 | 0 | 0 | 0 | 35 |
| 3 | CUXC | 35 | 29 | 0 | 0 | 2 | 33 |
| 3 | ZNXC | 35 | 29 | 0 | 0 | 0 | 35 |

## Comparisons on matched samples

| Cutoff | Fixed candidate | Matched samples | Selected resolves | Fixed resolves | Selected all rejected | Fixed all rejected |
|---|---|---:|---:|---:|---:|---:|
| 1 | SUXC | 29 | 5 | 6 | 5 | 7 |
| 1 | CUXC | 29 | 5 | 0 | 5 | 10 |
| 1 | ZNXC | 29 | 5 | 4 | 5 | 5 |
| 2 | SUXC | 29 | 3 | 2 | 1 | 1 |
| 2 | CUXC | 29 | 3 | 0 | 1 | 2 |
| 2 | ZNXC | 29 | 3 | 1 | 1 | 0 |
| 3 | SUXC | 29 | 0 | 0 | 0 | 0 |
| 3 | CUXC | 29 | 0 | 0 | 0 | 2 |
| 3 | ZNXC | 29 | 0 | 0 | 0 | 0 |

## Limits

- Heuristic scale omits fitted-contribution uncertainty, all covariance and model discrepancy.
- Cutoffs 1, 2 and 3 are sensitivity scenarios, not confidence levels.
- Model-set screening is not identification of the environmentally true source.
- Unresolved joint fits prevent complete-universe guarantees.
- Sulfur is related to fitted sulfate and is not an independent accuracy endpoint.
- Historical Cartesian profile combinations are not independently validated as jointly environmentally plausible.
- No assay cost, independent source truth, or conditioning-design comparator is available in this experiment.
- All-rejected outcomes are model inadequacy warnings, never successful attribution.
- The common physical scenario set is not pruned separately for candidate completeness; an incomplete candidate is unavailable.
- Full predictions, dates, held-out values and row selections stay in ignored private storage.

## Reproduce

```text
python scripts/audit_decision_measurements.py design --inputs <EPA-archive-directory>
python scripts/audit_decision_measurements.py evaluate --inputs <EPA-archive-directory>
python -m unittest discover -s tests -p test_decision_measurements.py -v
```

Design refuses to overwrite an existing frozen selection. Evaluation requires unchanged code, plan, configuration, scenario ledger and source archive.
