# Decision-focused CMB research: candidate evidence, not a manuscript baseline

This is a **code-and-aggregate research review**, extending the EPA native-input
reconstruction in [PR14](https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability/pull/14).
Its prerequisite commit is `2437750f8223304231ab9afcc9ec4a54956c8d97` on
`codex/evidence-strengthening-20260926`. Review this increment against that branch,
not against `main`: PR14 and its own prerequisite PR13 remain separate, unmerged
reviews. No manuscript, accepted R3nR8 baseline, published Zenodo archive, or
previous scientific result is replaced here.

The work asks whether source-attribution decisions remain identifiable when
uncertainty and simultaneous historical profile choices are considered. It does
**not** identify the environmentally correct profile or establish revolutionary
novelty. Consensus rankings, uncertainty sets, interval feasibility, Farkas
certificates, and model-discrimination design have substantial prior art; see
[NOVELTY_AUDIT.md](NOVELTY_AUDIT.md) and the linked primary-source ledger.

## Results and limits

| Experiment | Verified finding | What it does not establish |
| --- | --- | --- |
| Historical joint point profiles | 3,900 choices in central-retained-source grids (removed sources not reintroduced); 1,102 unresolved fits; all 35 grids unresolved. Two of four fully resolved local-stability cases have a joint top-change witness under the basic screen. | No complete-grid certificate; both central mass closures fail the stricter 80–120% screen. Unlike the primary interval panel, this is not the full-seven-family universe. |
| Held-out tracer choice | At cutoffs 1/2/3, selected tracer resolves 5/3/0 of 29 ambiguous cases, versus fixed sulfur 6/2/0. | No general superiority, independent source truth, or calibrated confidence. |
| Ordinary within-fit contrasts | At nominal alpha 0.05, 9/35 central fits are conditional singletons; 25/29 basic joint-witness cases are already ordinary non-singletons. | Estimated EVLS weights, pruning and the central profile are treated as fixed; no demonstrated coverage. |
| Central-system interval boxes | At k=1/2/3, the primary full-seven-source, no-mass panel has 5/33/35 feasible samples and 0/2/0 unique leaders. | k is not a simultaneous confidence level; infeasibility is not certainty, and independent boxes need not be physically realizable. |
| Actual historical profile-system union at k=2 | Original targeted numerical run: 34 witnessed non-unique unions and one HOLD across all 35 samples. | Do not erase the original HOLD or label every original numerical objective solved. |
| Separate proof-only completion | Existing Farkas records exclude all competing leaders in the remaining case. Across all 120 systems, 72 are infeasible; 48 feasible systems give the same leader and 288 exact margins exceed the unchanged tolerance. Thus the additive result is 1 conditional unique / 34 non-unique. | Post-hoc proof completion, zero new LPs, not a new theorem, probability statement, physical truth, or meaningful-effect-size claim. |
| Released synthetic-truth benchmark and controls | 4,944 rows / 44,496 fits. Every nonempty accepted profile family contains profile 0 only; the finite-point union gives no gain over the corresponding selected-profile method. Near-tie point decisions make 72 errors among 721 accepted rows; ordinary contrasts at alpha 0.05 issue 135 singleton decisions with no observed errors. | Zero observed errors is not zero risk. The endpoint is modeled signal over 82 channels, not total PM. This does not validate the interval method, field accuracy, or the separate JRC endpoint. |

The principal contribution is a testable, independently checked **conditional
decision audit**, with explicit unresolved and incompatible outcomes. The
scientific value is stronger limits on what fit-based source decisions can
support, not a demonstrated universally better estimator.

## Chronology and completed independent QA

Frozen producer reports preserve what was known when written. In particular,
`interval_union_report.md` and `interval_farkas_report.md` retain their original
pending-review wording. That wording is historical; the following later records
document completed independent checks, in order:

1. [Stage2 independent review](INTERVAL_INDEPENDENT_REVIEW.md) and
   [exact certificate verification](interval_certificate_verification.json):
   492 unique models / 840 sample-by-scenario records across 24 panels, including original-input matrix
   reconstruction and exact primal, dual, infeasibility and ray checks.
2. [Stage3 verification](interval_union_certificate_verification.json): faithful
   replay of the actual historical tuples and original 34 non-unique / one HOLD
   result. The filename-only Windows path correction retains its original and
   corrected configurations, cumulative budget and earlier lineage.
3. [Separate Farkas independent review](INTERVAL_FARKAS_INDEPENDENT_REVIEW.md)
   and [verification](interval_farkas_certificate_verification.json): all 120
   systems and 288 margins checked from original decimal inputs. Nonempty
   feasibility and strict comparison with the unchanged positive tolerance are
   required; empty sets and unresolved competitors cannot certify a leader.

The original Stage3 result is **not rewritten** by the later proof completion.
The proof completion is post-hoc. Protocol filenames ending in `PROPOSED` retain
their historical bytes; later frozen configurations and independent reviews
document execution. Likewise, the ordinary comparator is explicitly post-hoc;
freezing its own configuration before scoring does not make it a pre-outcome
study. Truth controls and tracer choices have their own recorded freeze/order.

## What can be reproduced from this public subset

The public increment provides original code, synthetic/adversarial unit tests,
protocols, aggregate results, source identities and review records. **It is not a
self-contained replay of the saved field certificates.** Original data download
alone does not reconstruct the omitted exact proof objects.

Synthetic tests do not require the owner-only return. Use a disposable public
checkout with neither EPA input root nor private records present. From that
repository root, run individual modules with Python 3.12, NumPy and SciPy:

```text
python -m unittest discover -s tests -p test_interval_decisions.py
python -m unittest discover -s tests -p test_interval_certificate_records.py
python -m unittest discover -s tests -p test_interval_farkas_margin.py
python -m unittest discover -s tests -p test_interval_farkas_records.py
python -m unittest discover -s tests -p test_truth_decisions.py
python -m unittest discover -s tests -p test_reconstruct_truth_inputs.py
python scripts/test_decision_certificate_counterexamples.py
```

The remaining included `tests/test_*` modules can be run the same way **in that
input-free checkout**. The three `JointNativeIntegrationTests` automatically
skip when the EPA archives are absent; if the archives are present, that class
refits the complete 3,900-choice field grid. Do not run that full module in a
populated research checkout merely to check synthetic logic. A measurement
integration test also skips without the private saved records. Report these
skips explicitly; an input-free test pass is not a new field reproduction or
full saved-ledger replay. The
recorded runtime is Python 3.12.14, NumPy 2.3.5 and SciPy 1.18.1; truth archive
reconstruction additionally uses h5py 3.16.0. Standard-library proof verifiers
avoid the producer's numerical solver for certificate arithmetic, but their
data/prerequisite requirements still apply.

Full saved-field-proof replay requires:

- All four original, hash-pinned EPA archives named in the prerequisite
  `outputs/strengthening_20260926/source_recovery.json`, normally under
  `ROOT.parent/_inputs/strengthening_20260926/epa`.
- The owner-controlled private case/index, joint-profile, pre-path-fix lineage,
  Stage3 and Farkas records. These are **not published in this PR**. Authorized
  review must be arranged with the project owner; no automatic public access
  or permission to redistribute these records is implied.
- The earlier verified stages as prerequisites to the later ones. A Stage3
  verification JSON is not a substitute for its missing source proof records.

Stage2 accepts an input-directory option. The frozen Stage3 and Farkas verifier
entry points use the fixed default EPA input root. Run saved-proof verification
in a **disposable copy** with the authorized records, because it writes fresh
verification metadata; do not overwrite archived review records.

Truth reconstruction instead expects the public licensed source archive under
`ROOT/_inputs/decision_research_20260926/truth_benchmark`. See the exact source
identity and attribution in [truth_dataset_attribution.json](truth_dataset_attribution.json).
[truth_reconstruction_guide.md](truth_reconstruction_guide.md) documents restoring
the deliberately omitted input NPZ; its saved-ledger commands additionally
require the owner-return snapshot's private prerequisites. The helper restores
inputs, not missing fitted ledgers, and does not itself rerun scoring.

The frozen Stage3 numerical producer has a historical **2026-09-27 05:00 UTC
cutoff**. It is an archived experiment, not a timeless fresh-solve entry point.
New numerical regeneration needs a separately reviewed bounded workflow and
newly labeled outputs; do not silently reset its timestamps or overwrite a
freeze. Saved-proof replay and synthetic tests do not require reopening that
numerical experiment.

## Release boundary and disposition

Only the explicit public allowlist is eligible for this review. Excluded are
all private proof matrices/vectors and sample ledgers, receptor/source arrays,
raw archives and truth NPZ/HDF5, Fairbanks spreadsheets/correspondence,
manuscripts, paper fulltexts, institutional-access notes, account credentials,
delivery/download records, machine/session checkpoints and runtime files.
Interval lower/upper matrices can reveal original inputs and are not harmless
anonymous aggregates. The owner-only Drive return must **not** be published as
the public reproduction package.

**KEEP:** qualified decision audits, exact proof checks, ordinary comparator,
truth-bearing stress tests including null findings, and primary-source overlap.
**HOLD:** environmental accuracy, physical mass-bound assumptions, calibrated
coverage, unrestricted source-native JRC use, manuscript integration and any
new publication archive. Radius proposals have no authorized field result.
**REMOVE from proposed claims:** revolutionary mathematical novelty, general
tracer/union superiority, empty-set certificates, and the assertion that this
public subset alone reproduces every saved field calculation.

No merge, submission, outreach, declaration, baseline promotion or Zenodo
replacement is part of this candidate review.
