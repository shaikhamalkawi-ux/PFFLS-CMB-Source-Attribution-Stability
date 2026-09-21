# Derived outputs

Only derived, redistributable outputs should be committed here.

Do not commit raw third-party datasets or reports.

Cycle 01's external-field-validation audit is in `cycle01/`. Its final
decision is HOLD; see `cycle01/README.md` for the review order.

Cycle 02's Fairbanks recovery is in `cycle02/`. Cycle 03's remaining-evidence
audit is in `cycle03/`; it closes HOLD with no manuscript change and adds exact
Fairbanks, Barrow, and APHH crosswalks plus an unsent ADEC request draft.

The Issue #8 administrative evidence-recovery package is in `outreach03/`.
It preserves the two investigator requests as user-reported SENT / PENDING but
unverified, while assigning the controlled status BLOCKED_USER_ACTION because
no provider-side confirmation is present. It does not resend them. The ADEC
request also remains BLOCKED_USER_ACTION and was not sent.

Cycle 04's audited submission-candidate reconstruction gate is in `cycle04/`.
It records the unsuccessful exact-baseline search, uses R3l only as a hashed
historical anchor, locks every central count, and closes
`HOLD_WITH_EXACT_BLOCKERS`. It contains a section-level candidate delta, not a
replacement manuscript or new baseline.
