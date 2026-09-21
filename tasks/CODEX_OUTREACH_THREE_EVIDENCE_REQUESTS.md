# CODEX OUTREACH TASK — Three pending evidence requests

## Purpose

Prepare and, where technically and account-authorized, submit the three evidence-recovery requests needed for the PFFLS/CMB project.

Locked manuscript baseline remains:

**PFFLS R4.3.30R3nR7-AE**

This task is administrative/evidence-recovery only. It does not authorize a manuscript revision.

---

# Request 1 — Palmer / Ward: Fairbanks sample-level spreadsheet

## Target

Recover the original sample-level Fairbanks spreadsheet(s) containing, if available:

- site;
- date;
- filter/sample ID;
- levoglucosan concentrations;
- PM2.5 values/shares;
- radiocarbon subset IDs and results;
- any lookup/crosswalk linking those samples to CMB dates or sample IDs.

## Primary contacts

Prepare the final email for:
- Christopher Palmer — University of Montana
- Tony Ward — University of Montana

Use the currently verified institutional email addresses from the project evidence register / current official directories.

## Message requirements

The email must:
- identify the project as **PFFLS-CMB**;
- state that this is a reproducibility request, not a request for unpublished conclusions;
- mention that the Palmer report explicitly states the raw site/date levoglucosan results were supplied in a spreadsheet;
- ask specifically for the original XLS/XLSX/CSV file or archived copy;
- ask for any sample-ID/radiocarbon lookup;
- if they no longer hold the file, ask for the last known custodian/location;
- avoid asking them to create a new analysis.

## Sending rule

If you have an authenticated and authorized email-sending capability connected to the user's account, send it and preserve:
- sent timestamp;
- To/CC;
- subject;
- exact body;
- message ID if available.

If no such authorized channel exists, do not simulate sending. Produce:
- ready-to-send email;
- one-line subject;
- contact list;
- short follow-up version for 5–7 business days later.

---

# Request 2 — Watson / Chow: original NFRAQS CMB-to-fM mapping

## Target

Recover the original calculation or transformation used to convert CMB source contributions into the contemporary/fossil-carbon quantity compared with NFRAQS radiocarbon results.

Ask for any surviving:
- spreadsheet;
- code;
- text file;
- CMB output;
- database query;
- project archive;
- calculation note;
- report appendix;
- file inventory;
- archived working directory.

## Required technical items

Ask specifically for the original definitions/rules for:
- contemporary versus fossil source classification;
- conversion from source contribution to carbon contribution;
- numerator and denominator;
- source-specific endmembers, if any;
- treatment of negative CMB contributions;
- sample inclusion/exclusion rules;
- exact sample IDs used in the comparison.

## Primary contacts

Prepare the final email for:
- John Watson — Desert Research Institute
- Judith Chow — Desert Research Institute

Use currently verified institutional contact details.

## Sending rule

Same as Request 1:
- send only through an authenticated, authorized channel;
- otherwise return a ready-to-send email package plus follow-up text.

---

# Request 3 — ADEC Public Records Request: native Fairbanks CMB electronic package

## Target

Request the original native electronic package underlying the Fairbanks PM2.5 CMB work.

Use the already drafted file:

`outputs/cycle03/Fairbanks_ADEC_Public_Records_Request_DRAFT.md`

Review it against the current ADEC public-records process before submission.

## Required record classes

Request, if retained:

1. EPA-CMB8.2 ambient/receptor input files.
2. Per-species receptor uncertainty inputs.
3. Source-profile matrices and profile uncertainties.
4. CMB control/run-definition files, including historical `IN*.in8` or equivalents.
5. Selector files such as `AD*.sel`, `SP*.sel`, `PR*.sel` or functional equivalents.
6. Species deletion and final selector records.
7. Native outputs, residuals, logs, databases, CSVs, and diagnostics.
8. Sample/run crosswalks.
9. Contractor-delivered ZIP/CD/DVD/electronic appendices.
10. RTI/DRI analytical-result deliveries used by CMB.
11. OMNI trial/profile-construction files relevant to profiles 100–108 and the hybrid wood-smoke carbon fraction.
12. Delivery manifests, archived project directories, or retention/disposition records if the package no longer exists.

## Scope rules

- Do not ask ADEC to perform a new analysis.
- Ask for native electronic files and original folder structure where possible.
- Ask for preservation of filenames/timestamps if feasible.
- State that the request is for noncommercial scientific reproducibility.
- Preserve the fee cap currently specified in the draft unless the user has supplied a different one.
- Exclude the separately requested Palmer/Ward spreadsheet so the requests are not duplicative.

## Submission rule

If you have an authenticated and authorized browser/account path that can submit the ADEC public-records request without requiring a private credential or user confirmation step, submit it and preserve the confirmation/receipt.

If submission requires login, identity confirmation, CAPTCHA, signature, payment, or any user-only step:
- do not bypass it;
- prepare the exact final form text;
- identify every field and the value to enter;
- provide the official submission page;
- create a one-page "SUBMIT_THIS_NOW.md" with copy-paste-ready content.

---

# Deliverables

Create:

`outputs/outreach03/`

with:

- `01_Palmer_Ward_READY_TO_SEND.md`
- `01_Palmer_Ward_FOLLOWUP.md`
- `02_Watson_Chow_READY_TO_SEND.md`
- `02_Watson_Chow_FOLLOWUP.md`
- `03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md`
- `03_ADEC_WEB_FORM_SHORT_VERSION.md`
- `03_ADEC_SUBMISSION_INSTRUCTIONS.md`
- `CONTACTS_VERIFIED.csv`
- `OUTREACH_STATUS.csv`
- `OUTREACH_LOG.md`
- `SHA256SUMS.txt`

Status values must be one of:
- SENT
- SUBMITTED
- READY_TO_SEND
- READY_TO_SUBMIT
- BLOCKED_USER_ACTION

Do not claim SENT/SUBMITTED unless an actual provider confirmation exists.

---

# Git / Drive workflow

Use branch:

`codex/outreach-three-evidence-requests`

Open a PR when complete.

Do not merge it yourself.

Return the full package to:

`PFFLS_4_CODEX_BRIDGE/02_FROM_CODEX/`

Recommended package:

`PFFLS_CODEX_OUTREACH_THREE_REQUESTS_RETURN.zip`

Include a SHA-256 sidecar.

---

# Stop rule

Stop after:
- sending/submitting through authorized channels where possible; or
- preparing a complete ready-to-send/ready-to-submit package where direct sending is not possible.

Do not start a new scientific cycle.
Do not modify the manuscript.
