# Pre-field decision: one exact metadata-byte portability exception

2026-09-26 23:31 UTC. No prepare or field LP occurred in the failed isolated
snapshot attempt. The previous 52-test producer/54-test verifier candidate,
18-file dependency closure, QA records and owner-local failure details are
preserved in a 23-member owner-private ZIP, SHA-256
`e92755fbf13ab9ee1b1c0dc75a86cfd64a39b39ec6d9e47697b352e3d98f32e6`.
Every member was read back and matched. The partial disposable snapshot is
retained, not silently repaired or reused. Original files remain unchanged.

## Verified cause

Only two of the 18 closure files already exist in base commit
`2437750f8223304231ab9afcc9ec4a54956c8d97`. The native audit script matches
byte-for-byte. The recovery metadata differs solely in line endings:

| `outputs/strengthening_20260926/source_recovery.json` | SHA-256 | Bytes |
| --- | --- | ---: |
| Existing working CRLF form, 257 CRLF pairs | `4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2` | 9074 |
| Tracked Git LF form, zero CRLF pairs | `32762085a73ee0b5ad703bc68ab8194303ca0769c49494202343b622e356c0e2` | 8817 |

Replacing CRLF with LF in the working bytes reproduces the tracked bytes
exactly. Independently parsed JSON values are equal. The existing nested Git
attributes select LF; the working file is Git-clean. Requiring only its raw
working SHA would incorrectly reject a fresh checkout/archive.

## Approved correction and gates

Approve a minimal change to the **new cold producer and new independent reader
only**, with renewed tests/review, before any execution approval:

- Permit exactly the two hashes above for that one recovery-metadata file.
  Do not accept generic newline normalization, reordered JSON, a third
  semantically equivalent encoding, or changed data/member hashes.
- Record and require the actual bytes consumed in each run's dependency map
  and recovery provenance. A manifest naming the other allowed form must
  still fail when it is not the form actually used.
- Parse already hash-checked recovery bytes; do not rely on an unchecked
  reopen. Continue verifying every original archive/member and all model
  identities. Do not edit frozen native/core/verifier files or PR14 outputs.
- Keep all other dependencies exactly pinned. Include this decision in the
  new dependency closure, and expose the two allowed variants explicitly in
  a new `cold_implementation_qa_v2.json`; preserve the first QA unchanged.
- Test both approved forms, third-form rejection, changed metadata rejection,
  manifest/file mismatch, unchanged unrelated pins and unchanged scientific
  metadata digests. Renew the full relevant synthetic suites and static review.
- In a new snapshot, retain the original Git LF metadata bytes after verifying
  this exact exception; record that choice. Check Git filtering for the new
  frozen files as well. Do not patch the retained failed snapshot.

There is no scientific parameter, model, margin, algorithmic proof requirement,
resource-ceiling or result change. No historical outcome becomes an acceptance
oracle. A new isolated prepare, independent review of that exact manifest, and
separate hash-specific root execution approval are still required. Subsequent
field records must independently replay; no cold-run success is claimed now.
