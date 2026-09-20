# CODEX CYCLE 01 — Find a genuinely reconstructable external field-validation case

## Goal

Find and reconstruct an independent field campaign that can test:

> Does the source profile favored by the frozen CMB fit criterion also minimize error against an independent external tracer/reference?

The task is not to find another generic CMB dataset. It is to find a **profile-resolved external-validation dataset**.

## Required objects

A candidate field campaign is admissible only if we can recover, at sample/day level:

1. receptor chemical-speciation vector;
2. receptor uncertainties;
3. numerical source profiles;
4. source-profile uncertainties;
5. exact fitting species / source selection;
6. CMB model rule / EVLS implementation details sufficient for reproduction;
7. independent external tracer/reference for the same sample or exact interval;
8. unambiguous mapping from the CMB output to the quantity compared with that external reference.

Potential external references include radiocarbon or another independently measured source-discriminating tracer, but do not broaden the endpoint after seeing results.

## Candidate discovery

Search official and archival sources first:
- EPA / AQS / HERO / NEPIS
- state environmental agencies
- university repositories
- report appendices / supplementary data
- archived CMB project datasets
- original laboratory / field-campaign repositories

NFRAQS and Libby have already been audited:
- NFRAQS: exact historical profiles recovered, but primary CMB-to-fM endpoint mapping remains HOLD.
- Libby: real field campaign, but public record is not sufficiently profile-resolved for the same rerun.

Do not spend the cycle merely rediscovering those limitations unless you find genuinely new source material that closes them.

## Output

Create:
- `outputs/cycle01/source_inventory.csv`
- `outputs/cycle01/candidate_campaigns.csv`
- `outputs/cycle01/admission_report.md`
- `outputs/cycle01/KEEP_HOLD_REMOVE.md`
- any retrieval/parsing scripts under `scripts/`
- tests under `tests/`

For each campaign report:
- exact source URL;
- retrieval date;
- SHA-256 for downloaded inputs;
- rights / redistribution status if known;
- which required objects are present;
- which are missing;
- final status: KEEP / HOLD / REMOVE.

## Stop rule

If no campaign passes all required evidence gates, return **HOLD**.

Do not invent missing profile vectors, uncertainties, selectors, tracer mappings, endmembers, denominators, or sample crosswalks.

## Manuscript boundary

This cycle does **not** authorize a manuscript revision.

A new manuscript version may be proposed only after an admissible new scientific result exists and is independently reviewed.
