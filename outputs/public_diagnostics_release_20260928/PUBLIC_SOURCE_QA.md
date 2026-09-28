# Independent public-release source and scope review

28 September 2026. **GO for one bounded archive build and clean-extraction verification.** This record is outside the archive's fixed allowlist. It does not assert that the archive has yet been built, published, downloaded, or verified.

Read all eight new public source/documentation files completely, including the final README's canonical-ZIP and line-ending caveat and the dependency document's commit-specific links. Also read the root citation, additive README introduction, and attributes file. No scientific producer, fixture suite, optimizer, native model, network write, or packaging script was executed by this reviewer. This review used the read-only spreadsheet/scientific-audit guidance for units, source identity, dependency limits, and preservation of original records.

## Exact reviewed identities

Paths below are relative to this release directory unless marked repository root.

| File | SHA-256 |
|---|---|
| README.md | `7483e997687756c11d6d18a415dae4954b2f265594756dbaab746e914e98d4e6` |
| CITATION.cff | `643bea11ce788d1241720e792a57b6836c56b237a0332895192a91ff1a55a6ff` |
| LICENSE_SCOPE.md | `03740e112432fbbf102c28b43bff5f63bc6726bf658f3e3077171f1e695d88c6` |
| UPSTREAM_ATTRIBUTION.md | `0f69a3d1fdd4204f80294d694862dd334c94dfdf8b59757ed331d8f07ec1239c` |
| DEPENDENCIES.md | `c371eb4e3d7d5af8a416640ae3f02468fcc40f1bfb95f0101ac5fba064400f51` |
| RELEASE_REVIEW.md | `64e3a57cbbe51f95d79b8c1ee943518f2d55c5af04dc5b4220f4b627a07958b7` |
| build_public_release.py | `a3458814828c90c34054312d2e39509adf0a7f976d30e16fd23afc2c2ba92cc6` |
| verify_public_release.py | `d065d07b41c6b240eeaed246c6ee596b89170e6e663ceb238110678e11417006` |
| Repository root CITATION.cff | `8e5529d99805394664cb7cb818209b14b55ee4fffe06839509e6890dac8fc656` |
| Repository root README.md | `5082f104c2adc1817d783329a071f36170038de6d81cc1c239bf30e3a5ee5bf2` |
| Repository root .gitattributes | `ecd572410c25810ea687a7b88e26651377a2525cff695625d3a7506436065d0c` |

## Allowlist, rights, and disclosure

The builder selects exactly 19 payloads: four unchanged scientific source/test files, two unchanged journal-editorial CSV inputs, four saved aggregate files, the unchanged MIT notice, six new documentation/metadata files, and two new packaging/verification scripts. Inventory and manifest add two generated members, for 21 expected ZIP members. There is no directory traversal or glob-based payload selection. It refuses existing target archives/receipts and changed pinned scientific bytes.

The selection excludes manuscript PDFs, TeX, figures, raw data, private ledgers, correspondence, restricted papers, owner-only Drive records, and the original execution plan containing local computer context. A bounded textual scan of the public-release sources found no local absolute Windows path, credential pattern, personal-email address, or private Drive file link. This is not a malware certification or an exhaustive security claim.

The sole creator of the new release is Ghassan O. Malkawi, as separately authorized. Both root and release citations expressly scope this to the new software/data increment, not manuscript authorship or all repository work. Earlier four-author CSV attribution and DOI 10.5281/zenodo.22976190 remain explicit. The MIT notice retains `PFFLS research contributors`; it is not rewritten as sole ownership. The old citation and frozen archive are not changed. The reserved new DOI is not represented as publication already completed.

The root README's older baseline nomenclature remains historical, pre-existing content; its new introduction does not silently promote a manuscript baseline. Attributes preserve bytes only for the specified new files/directories and do not renormalize old upstream CSVs or frozen archives. Git staging must still use a literal public allowlist, not an entire directory or all untracked files.

## Reproduction and scientific interpretation

The verifier is designed for a clean ZIP extraction under any directory name. It checks path safety, duplicate identities, payload sizes and hashes, exact inventory/manifest/file membership, and the pinned JRC scientific objects before importing the guarded producer. It disables bytecode writing and calls only read-only `analyse()`, comparing all scientific fields with the saved JSON while treating historical runtime/source metadata separately. It does not call a producer `main()` or execute a scientific test suite. Actual execution and archive-byte verification remain a separate step.

The preserved JRC fixture has a historical checkout-name assertion. The README accurately discloses this and does not advertise that whole test suite as universally portable. The two CSVs use the exact journal-editorial byte representation pinned by the producer, distinct from the old Zenodo container's line endings. Their old collaborative content attribution is retained. A generic Git checkout is not claimed to satisfy those byte pins.

EPA verification is expressly `NOT_REPRODUCED_MISSING_EXTERNAL_INPUTS`. Its seven exact whole-file dependencies and receptor-member hash are listed, including the private original ledger/configuration, distinct original recovery record, and hash-pinned original plan. The new public dependency note is not a substituted plan. Public report/script links are pinned to the prior reconstruction commit; the stated hashes remain authoritative. Invented-fixture tests do not close those input gaps.

The numerical descriptions agree with the saved reviewed results: nine discordances among 18 wood comparisons and zero among 12 vehicle comparisons; EPA 345 eligible, 323 converged, 22 excluded nonconverged, 283 two-target, 62 top changes over 22 samples, and two strict top changes on one sample. Small-group aggregates are not falsely described as anonymized. No full private vectors are included. The text preserves retrospective chronology, nested dependence, missing JRC provenance, and absence of superiority, uncertainty-coverage, field-truth, policy-benefit, or submission-readiness claims.

## Remaining release checks

Root must build once, verify the actual ZIP's members and CRC, extract into a clean directory, execute the new read-only verifier once, and retain its EPA missing-input status. GitHub staging/PR and Zenodo publication must receive only the reviewed allowlisted material. Public landing metadata, actual downloaded bytes and SHA-256 still require verification before reporting successful publication. No such external result is inferred from this source review.
