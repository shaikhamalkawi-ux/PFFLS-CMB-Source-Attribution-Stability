# Current reading order: literature additions after the computational freeze

2026-09-27 UTC. Start with [candidate status](REVIEW_CANDIDATE_STATUS.md), then
read these two short additions before relying on the earlier literature limits:

- [EVLS full-text check](EVLS_FULLTEXT_ACCESS_ADDENDUM.md): the licensed main
  article is now read. Earlier abstract-only statements describe the historical
  access state, not the current one. Exact pipeline replication and calibration
  remain unresolved.
- [Hemann prior art](HEMANN_PRIOR_ART_ADDENDUM.md): known-truth contribution-bias
  analysis and the distinction between stability and accuracy have established
  receptor-model precedents. A contribution-level PMF bootstrap is a possible
  future comparator, not a computation conducted in this candidate.

The 135-file computational release at commit
`46de6cc5efc788af3c5cf9f4c5c05d9160642f4c` remains byte-identical, including
`PUBLIC_RELEASE_MANIFEST.json`. The separate
`LITERATURE_ADDENDUM_MANIFEST.json` inventories only this reading-order note and
the two additions. Its inclusion makes a four-file documentation increment,
not a new calculation or a replacement manifest.

The 441 executed tests and four explicitly skipped integration tests belong to
the computational release. No numerical rerun is claimed for these literature
notes. No source material, contribution ledger, manuscript, accepted baseline
or published archive has been added or modified by this increment.

Disposition remains **KEEP** the conditional audit and verified reproduction;
**HOLD** environmental accuracy, calibrated coverage and superiority; **REMOVE**
unfounded novelty or revolutionary-method language. The manuscript inserts
remain proposals for human review, not approved publication text.

These three original notes and their additive manifest are CC BY 4.0. This
does not relicense the cited articles or change the base release's code licences.
