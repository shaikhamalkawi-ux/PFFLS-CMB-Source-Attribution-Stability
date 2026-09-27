# Independent audit of the two OAT-to-joint EPA witness samples

Date: 26 September 2026. Scope: the two samples flagged by the frozen joint-grid
analysis as completely resolved and top-stable under the **basic** OAT screen,
but with a joint top-source-change witness. No additional samples were searched.
No primary settings, manuscript, frozen outputs, or profile choices were changed.

## Verdict

**KEEP, with an explicit basic-screen limitation.** Both samples have positive,
distance-two joint witnesses. All **nine** such witnesses survived independent
QR-based reconstruction, a much tighter stopping criterion and three initial
contribution vectors. They are not artifacts of negative source estimates.

**Do not claim a strict mass-closure-qualified paired counterexample.** Both
central fits fail the 80–120% mass-closure screen. Six of the nine alternative
witnesses individually pass that screen; this does not qualify the central-and-
alternative pair. The strictly screened paired witness count is **zero**.

## Evidence checked

The ledger identity read for this audit is
`ba73f7f41de50d4b40edf1fe5be0513120dfb109c9a10730f1007e7f6c3143a2`.
All four native archives and 39 member identities were rechecked before fitting.
The two samples retain the same seven source slots and neither underwent central
source removal. All ten OAT alternatives per sample converged with positive
contributions; neither sample has an OAT top-source tie.

| Check | Independent result |
|---|---:|
| Central plus complete OAT fits audited | 22 |
| Basic-qualified distance-two top-change witnesses audited | 9 |
| Primary-setting QR refits | 31 |
| Tight-setting refits, three initializations each | 93 |
| Witnesses positive and basic-qualified before/after tightening | 9/9 |
| Witnesses individually meeting mass closure after tightening | 6/9 |
| Witness pairs with both central and alternative meeting mass closure | 0/9 |
| Basic-OAT-stable samples also stable across **all** converged OAT fits | 1/2 |

One sample's basic-screen OAT stability is conditional on excluding one
already-reversing single-profile alternative with reduced chi-square above 4.
The other sample preserves its largest source under **all ten** converged,
nonnegative OAT alternatives, including those excluded by the basic fit screen.
This second sample is therefore the stronger OAT-to-joint illustration.

Across the two central fits, primary mass closure ranges from **66.75% to 69.99%**.
Tightening the solver does not repair it: the range becomes **66.77% to 69.99%**.
The independent audit therefore does not support replacing the existing basic
screen limitation with a claim of mass-complete reconstruction.

## Independent numerical check

The fitting recurrence was rewritten for this audit using
`scipy.linalg.lstsq(..., lapack_driver="gelsy")`, a pivoted-QR-based solver,
instead of the native reconstruction's `numpy.linalg.lstsq` route. The species,
uncertainty fields, initial source slots and diagnostic definitions were held
fixed. No source estimate was clipped, pruned or constrained after selection.

- At the frozen settings (1% relative iterate-change criterion, 20 solves), all
  31 refits reproduced convergence flags and iteration counts. The maximum
  absolute contribution difference was **5.56e-14**.
- In a separately labelled sensitivity check, the relative criterion was
  **1e-10** and the iteration budget **2,000**. Each of the 31 fits was started
  from zero, from all ones, and from its sample's central retained contribution
  vector. Every run converged. The maximum discrepancy between initializations
  was **2.86e-10** in contribution units.
- Neither complete OAT neighborhood acquired a basic-qualified top-source change
  under the tight settings. All nine distance-two witnesses remained reversed,
  strictly positive and basic-qualified.
- Across the nine tight witnesses, the leading-source margin ranges from
  approximately **0.0240 to 3.7454** contribution units. The smallest positive
  source estimate is approximately **0.2610**. One small-margin witness should
  not be portrayed as substantively large merely because its sign is stable to
  numerical tightening.

These are strong numerical cross-checks, **not** validated interval error bounds,
a proof of global fixed-point uniqueness, or robustness to measurement and
source-profile uncertainty beyond the enumerated alternatives. Different seeds
agreeing does not establish that all possible initializations must agree.

## Interpretation and limits

The meaningful empirical result is that **a fully resolved OAT assessment can
miss a positive joint-choice top-source reversal in this historical CMB grid**.
For one of the samples, even unfiltered OAT ranking stability misses it. Its
minimum number of changed profile families is two because all distance-one
choices were actually resolved, not because unresolved choices were discarded.

The grid still has unresolved choices at larger distances in both samples. The
two witnesses establish instability; they do not make the possible-top set or a
universal partial order complete. Nor do they prove that any simultaneous
historical profile combination represents the true environmental sources.

The mass-closure limitation is material, not editorial. A paper can reasonably
use these as counterexamples to a **basic numerical-screen** inference while
clearly reporting the failed strict check. It cannot describe them as examples
where all prescribed scientific diagnostics support both allocations.

The result also does not by itself prove a nonlinear interaction. “Joint-choice
reversal missed by OAT” is the supported phrase. General consensus ranking,
abstention and finite-grid minimum-distance calculations still require the
separate novelty audit; this check does not establish a revolutionary method.

Case identities, changed profile combinations and detailed sensitivity metrics
are retained only in
`private/decision_research_20260926/independent_witness_audit.json`.
No native input archive or row-level source-contribution vector is copied here.

## Reproduction code

Run the following Python block from the repository root. It reads the existing
private ledger and verified official input archives, prints only audit aggregates,
and writes no files. Selection includes the complete OAT neighborhoods, not only
the attractive joint outcomes. The 2,000-step, 1e-10 runs are sensitivity analyses
and must not overwrite the frozen primary results.

```python
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import lstsq

sys.path.insert(0, "scripts")
import audit_epa_native_strengthening as native

ledger_path = Path("private/decision_research_20260926/joint_profile_ledger.json")
payload = ledger_path.read_bytes()
assert hashlib.sha256(payload).hexdigest() == "ba73f7f41de50d4b40edf1fe5be0513120dfb109c9a10730f1007e7f6c3143a2"
ledger = json.loads(payload)
inventory = native.archive_inventory(native.DEFAULT_INPUT)
native.verify_recovery_identities(inventory, Path("outputs/strengthening_20260926/source_recovery.json"))
receptors, profiles, _ = native.load_inputs(native.DEFAULT_INPUT)

def refit(rec, ids, tolerance, budget, seed):
    names = native.CONFIG["species"]
    y = np.array([float(rec[n]) for n in names])
    sy = np.array([float(rec[n[:-1] + "U"]) for n in names])
    F = np.array([[float(profiles[s][n]) for s in ids] for n in names])
    E = np.array([[float(profiles[s][n[:-1] + "U"]) for s in ids] for n in names])
    old = np.array(seed, dtype=float)
    converged = False
    for i in range(budget):
        variance = sy**2 + (E**2) @ (old**2)
        root = np.sqrt(variance)
        new, _, rank, _ = lstsq(F/root[:, None], y/root, lapack_driver="gelsy")
        assert rank == len(ids)
        relative = np.abs(new-old)/np.where(new != 0, np.abs(new), 1)
        relative = np.where(new == 0, np.where(old == 0, 0, np.inf), relative)
        old = new
        if np.max(relative) <= tolerance:
            converged = True
            break
    residual = y - F @ new
    wrss = float(np.sum(residual**2 / variance))
    r2 = 1 - wrss/float(np.sum(y**2/variance))
    chi2 = wrss/(len(y)-len(ids))
    mass = 100*float(np.sum(new))/float(rec["TMAC"])
    basic = converged and 0.8 <= r2 <= 1 and 0 <= chi2 <= 4
    return {"x": new, "converged": converged, "iterations": i+1,
            "basic": basic, "strict": basic and 80 <= mass <= 120,
            "top": int(np.argmax(new))}

fits = witnesses = individually_strict = 0
max_primary_error = max_seed_error = 0.0
selected = [s for s in ledger["samples"]
            if s["summaries"]["basic"]["top"]["complete_local_stable_joint_witness"]]
assert len(selected) == 2
for sample in selected:
    matches = [r for r in receptors if all(r[k] == v for k, v in sample["sample"].items())]
    assert len(matches) == 1
    rec = matches[0]
    central = sample["central"]
    central_top = int(np.argmax(list(central["source_contributions"].values())))
    assert not (80 <= central["percent_mass"] <= 120)
    for row in sample["rows"]:
        result = row["result"]
        is_witness = (result["converged"] and row["distance"] == 2
                      and row["ranking"]["largest_source_change"]
                      and 0.8 <= result["R2"] <= 1
                      and 0 <= result["reduced_chi2"] <= 4)
        if not (row["distance"] <= 1 or is_witness):
            continue
        ids = row["source_ids"]
        primary = refit(rec, ids, .01, 20, np.zeros(len(ids)))
        expected = np.array([result["source_contributions"][sid] for sid in ids])
        error = float(np.max(np.abs(primary["x"]-expected)))
        assert error < 1e-10 and primary["converged"] == result["converged"]
        assert primary["iterations"] == result["iterations"]
        seeds = [np.zeros(len(ids)), np.ones(len(ids)),
                 list(central["source_contributions"].values())]
        tight = [refit(rec, ids, 1e-10, 2000, seed) for seed in seeds]
        assert all(r["converged"] for r in tight)
        max_primary_error = max(max_primary_error, error)
        max_seed_error = max(max_seed_error,
                             *(float(np.max(np.abs(tight[0]["x"]-r["x"]))) for r in tight[1:]))
        if is_witness:
            assert all(r["basic"] and r["top"] != central_top and np.min(r["x"]) > 0 for r in tight)
            witnesses += 1
            individually_strict += int(tight[0]["strict"])
        else:
            assert all(not r["basic"] or r["top"] == central_top for r in tight)
        fits += 1
assert (fits, witnesses, individually_strict) == (31, 9, 6)
print({"audited_fits": fits, "tight_refits": 3*fits,
       "confirmed_witnesses": witnesses, "individual_strict_witnesses": individually_strict,
       "strict_paired_witnesses": 0, "max_primary_error": max_primary_error,
       "max_seed_error": max_seed_error})
```
