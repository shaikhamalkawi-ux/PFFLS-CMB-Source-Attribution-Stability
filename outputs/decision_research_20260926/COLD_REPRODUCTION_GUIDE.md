# Fresh-clone interval-union reproduction

These are gated instructions, not a claim that a field run has completed. The
fixed question is the original 35 ordered samples, 20 species, seven families
and 120 actual profile tuples, with k=2 joint boxes and no mass constraint.
This prospective reconstruction uses a proof fallback informed by the known
historical result. It is not blinded, independent environmental validation or
a new mathematical method. No expected result total is an acceptance oracle.

The detailed contract is [COLD_RUN_RECORD_SCHEMA.md](COLD_RUN_RECORD_SCHEMA.md).
The reviewed implementation identities and the sole portability exception are
in [cold_implementation_qa_v2.json](cold_implementation_qa_v2.json), SHA-256
`e0108358c61e1d62a06e09767475b0953fee9ec4d633198e6ce3aa00fbbd5a8a`.

## 1. Obtain the reviewed code, not old private records

Use a short, fresh local checkout. Replace `REVIEWED_COMMIT` with the published
review commit containing this guide, QA v2 and its complete 19-file dependency
closure; do not assume the default branch or an older release contains them.

```text
git clone https://github.com/shaikhamalkawi-ux/PFFLS-CMB-Source-Attribution-Stability.git cmb-review
cd cmb-review
git checkout --detach REVIEWED_COMMIT
```

No historical `private/` directory, result partition or proof ledger is needed.
Do not copy one into this checkout. Do not run the historical Stage 2/Stage 3
entry points, modify their archived calendar cutoff, or substitute their saved
results for a fresh run.

Use an isolated Python 3.12-or-later environment. The tested environment was
Python 3.12.14, NumPy 2.3.5 and SciPy 1.18.1; no claim is made about other
versions. After creating/activating your environment, a matching dependency
installation is:

```text
python -m pip install numpy==2.3.5 scipy==1.18.1
```

The numerical run records Python/NumPy/SciPy/platform versions and refuses
environment changes between prepare and run. External packages retain their
own licences.

## 2. Obtain the four exact original archives separately

Use the recorded official [EPA CMB landing page](https://www.epa.gov/scram/chemical-mass-balance-cmb-model)
and recorded final retrieval URLs below, subject to the provider's applicable access/use terms. They are
historically recorded retrieval URLs, not a promise of future availability.
Place all four ZIPs, with these exact names, in an `ARCHIVE_DIRECTORY` outside
the public checkout. Do not re-zip, edit or replace them with similarly named
files. Stop on any identity mismatch; do not weaken the pins.

| Archive / recorded final retrieval URL | SHA-256 |
|---|---|
| [sjvf_data.zip](https://www.epa.gov/sites/default/files/2020-10/sjvf_data.zip) | `3ca5bb3d4273e40f9c0f65a11f60e86fadafb525a086a046a9ef29a171fd229f` |
| [pacs_data.zip](https://www.epa.gov/sites/default/files/2020-10/pacs_data.zip) | `e83d859f6a794504271ff4e84704787fe8b7a03e87940e6dcb105e560a7fef4f` |
| [epa-cmb82test.zip](https://www.epa.gov/sites/default/files/2020-10/epa-cmb82test.zip) | `f653311c3b9d0b89611a337b625e77d82d35650c852f5df8d7cb10c76f86d7ff` |
| [sourcecmb82.zip](https://www.epa.gov/sites/default/files/2020-10/sourcecmb82.zip) | `44acea483c66cd5eb859340ecb7083fff18ab4b0401dde5d4f34972a22fbe8c9` |

All 39 original members are identity-checked without extracting archive-controlled
paths. The EPA executables, DLLs and Fortran are not executed. Recorded member
provenance is in `outputs/strengthening_20260926/source_recovery.json`.

QA v2 lists all 19 exact dependency paths/hashes. **Only** that recovery JSON
allows its two verified original byte forms: 9074-byte working CRLF or
8817-byte tracked Git LF; use the full hashes in QA v2. Preserve the
form supplied by the checkout. There is no generic newline normalization,
semantic-JSON allowance or exception for code files. Each run records the
actual recovery hash in both its dependency map and input provenance.

## 3. Run input-free tests and independent metadata checks

The first two commands use synthetic models only; they do not fit native field
data. The next two independently reconstruct native metadata and all 4,200
model identities without solving LPs:

```text
python -m unittest discover -s tests -p test_cold_interval_union.py -v
python -m unittest discover -s tests -p test_cold_interval_union_records.py -v
python scripts/reproduce_interval_union.py --metadata-only --inputs ARCHIVE_DIRECTORY
python scripts/verify_cold_interval_union.py --metadata-only --inputs ARCHIVE_DIRECTORY --max-seconds 1200
```

Require the expected counts and exact agreement of the sample-order, tuple-order
and ordered-model digests with QA v2. Review the actual 19-file dependency map
against QA v2 as well; the actual recovery hash may differ only by the explicit
approved pair. All other files must match exactly. Passing these checks does
not authorize a field run.

## 4. Prepare, inspect, then explicitly approve the exact manifest

Replace `NEW_PRIVATE_DIRECTORY` with an absent direct child such as
`<this-checkout>/private/cold_run01`. The final component must start with a letter
and contain only letters, digits, underscores or hyphens, at most 41 characters.
Use a short path; symlinks/junctions, input overlap and existing outputs are
rejected. Quote path arguments containing spaces.

```text
python scripts/reproduce_interval_union.py --prepare --inputs ARCHIVE_DIRECTORY --output NEW_PRIVATE_DIRECTORY --max-models 4200 --max-lp-calls 20000 --elapsed-seconds 7200
```

Preparation does not solve an LP. It writes an immutable manifest, preflight and
empty cases directory, and returns the exact manifest SHA-256. Review its input,
code, environment, model and budget identities independently before approving
that hash. For this research session, separate root approval is required.

An optional `--deadline-utc YOUR_TIMEZONE_AWARE_STOP_TIME` belongs on **prepare**
and must be chosen for that execution. Do not reuse a historical session date
as a timeless default. Budgets may be lowered, not raised above 4,200 models,
20,000 charged LP attempts and 7,200 elapsed seconds.

Only after explicit approval:

```text
python scripts/reproduce_interval_union.py --run --inputs ARCHIVE_DIRECTORY --output NEW_PRIVATE_DIRECTORY --approved-manifest-sha256 APPROVED_SHA256
```

The run cannot change its prepared budgets or resume an existing attempt.
Interrupted/failed directories must remain intact. Starting again requires a
different absent output directory and a new reviewed manifest, not cleanup or
repair of the previous run.

## 5. Replay proofs without solving again

After the producer closes its terminal output manifest:

```text
python scripts/verify_cold_interval_union.py --inputs ARCHIVE_DIRECTORY --run-directory NEW_PRIVATE_DIRECTORY --max-seconds 1200
```

The independent reader reconstructs original inputs itself and performs zero
LPs. A successful first replay exclusively creates `independent_verification.json`.
For a later read-only replay, add `--check-only`; do not overwrite that record.
Replay has its own bounded budget, at most 1,800 seconds.

Inspect both verification status **and** producer `run_status`, incomplete
coverage and HOLD counts. A replay PASS can validate an honestly stopped run;
it does not mean every sample was decided. A charged attempt can be aborted
before solver invocation if durable journaling consumes its remaining time;
the separate counters retain that distinction. Exact conditional certificates
do not establish atmospheric truth, probability coverage or unique leadership
outside the declared model family.

## Rights and publication boundary

All raw archives, reconstructed model matrices, sample identities, proof vectors,
case records and per-sample ledgers remain private. Public accessibility is not
blanket redistribution permission. Do not commit raw ZIPs or generated private
outputs. Public release is limited to separately reviewed code/tests,
nonreconstructive metadata and aggregates.

Follow [LICENSE_SCOPE.md](LICENSE_SCOPE.md): MIT applies only to original code
listed in the final public release manifest, and CC BY 4.0 only to the listed
author-created documentation/data. A draft directory is not a completed release;
no new licence is asserted over EPA inputs, third-party software or private
records. Preserve source attribution and identify modifications.
