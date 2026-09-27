# Minimal manuscript changes for author review — not an applied revision

These proposed passages follow the completed scientific reviews. They do not
replace R3nR8 or edit an existing manuscript. Keep the original JRC and EPA
estimands and all reported primary counts unchanged. The separately verified
cold reconstruction adds computational reproducibility, not new observations;
it is not used to broaden the scientific claims proposed below.

## 1. Replace a broad stability implication with a scoped statement

Suggested location: Discussion, “Implications for source-profile
characterization and air-quality interpretation,” replacing the sentence that
documented substitutions identify stable rankings. Retain the surrounding
reference/accuracy distinction.

> Documented substitutions establish stability only within the alternatives
> actually tested. Stability under individual substitutions need not persist
> under simultaneous changes. In an exploratory extension retaining each
> central fit's source set, four samples had all one-at-a-time alternatives
> numerically resolved and no largest-source change among alternatives admitted
> by the basic fit screen. Two nevertheless had an admitted joint largest-source
> reversal. Neither central fit satisfied the stricter mass-closure screen.
> Moreover, 1,102 of 3,900 joint choices remained numerically unresolved, so no
> sample's complete point-fit grid supported an exhaustive stability claim.

Support: `joint_profile_results.json`, `joint_profile_report.md`,
`INDEPENDENT_WITNESS_AUDIT.md`. The four-sample denominator is not the full
35-sample population; the two reversals are not new strict-screen failures.
This is an exploratory scope extension, not a new estimator or external truth.

## 2. Add the conventional-uncertainty qualification

Suggested location: the same discussion subsection or exploratory supplement,
immediately after the preceding paragraph. Include it whenever the joint
extension is cited; do not publish only its favorable novelty implication.

> Much of this ambiguity was already visible to conventional within-fit
> uncertainty analysis. A post-hoc comparison using joint source contrasts with
> final effective-variance weights held fixed gave nine conditional singleton
> leaders among 35 central fits at nominal alpha 0.05. Of 29 samples with a
> basic-screen joint largest-source-change witness, 25 were already non-singletons under this
> comparator. The four overlaps are not environmental error rates: neither
> profile substitution nor this conditional covariance analysis supplies
> independent allocation truth or validated confidence coverage.

Support: `ORDINARY_CONTRAST_REPORT.md`,
`ORDINARY_CONTRAST_INDEPENDENT_REVIEW.md`, `ordinary_contrast_results.json`.
Specify the actual Bonferroni contrast rule in the supplement. Do not describe
this baseline as ignoring profile uncertainty: that uncertainty contributes to
the effective-variance weights, although their estimation is treated as fixed.

## 3. Update availability and AI disclosures if the new analysis is included

The existing frozen DOI must retain its original summary-check scope. The
following is an **addition**, not permission to relabel that archive:

> A separate, versioned research candidate provides an independent reconstruction
> from the identified EPA native archives, analysis code, synthetic tests,
> aggregate findings and verification records. It is distinct from the frozen
> Zenodo publication-summary package and does not recover the historical
> original computational archive or reproduce the separate JRC analysis from
> unrestricted source-native inputs. Original third-party inputs and private
> sample-level proof ledgers are not distributed with the public candidate.
> The candidate distinguishes fresh numerical regeneration from replay of
> historical saved proof objects and documents their different prerequisites.

Before insertion, cite the **actual reviewed PR/commit and release manifest**;
do not substitute an uncreated DOI or a claim of public access to private data.
The owner-only Drive return is not a public data repository. No new DOI is
requested or created by this research increment.

If these analyses are used, the present AI disclosure should additionally say:

> AI-assisted work included exploratory analysis design, code generation and
> debugging, literature synthesis, numerical reconstruction and independently
> implemented computational checks. The verification records identify the
> automated checks and their limits. Human scientific review and responsibility
> remain with the authors.

This proposed wording must be reconciled with the authors' actual review and
the journal's requirements before submission. It makes no new author-role,
funding, conflict-of-interest or submission declaration.

## Material not recommended for expansion of the main paper

Keep the exact interval-union analysis, recession-cone audit and synthetic
82-channel benchmark in the clearly labelled research package or a separately
approved exploratory supplement. Their estimands and assumptions differ from
the primary campaign-mean reference comparison. In particular, do not cite the
new benchmark as independent confirmation of the JRC 9/30 result: it showed no
incremental finite-profile-union benefit, and did not test the interval method.

The practical geometric observation is worth retaining in that research note:
at k=3, the three available added tracers leave a zero lower vehicle column in
96 of 120 input systems. In any branch that remains nonempty, additional
ambient precision alone cannot block that recession direction under the same
independent-box model. Added observations might instead exclude the branch;
this was not computed. New source-characterization restrictions would require
independent physical justification. Boundedness alone is not unique leadership.

The result is a more defensible account of what the study does and does not
show, not a claim of revolutionary novelty or a submission-ready replacement.
