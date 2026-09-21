# ADEC submission instructions — user action required

## Current official route

- DEC Online Services: `https://dec.alaska.gov/online-services/`
- That page links the current downloadable form:
  `https://dec.alaska.gov/media/x5yl25jk/public-records-request-form.docx`
- No mandatory public-records web portal, myAlaska login, or submission CAPTCHA
  was found.
- Under 2 AAC 96.310, use of the agency form is optional. Official Alaska
  guidance permits an electronic written request to an employee of the correct
  agency and recommends putting the request in the email body, not only in an
  attachment.

## Recommended routing

```text
To: nick.czarnecki@alaska.gov
Cc: cory.mcdonald@alaska.gov; amqa-data-request@alaska.gov
Subject: Alaska Public Records Request — native Fairbanks PM2.5 CMB electronic package, 2005–2014
```

- Nick Czarnecki: Program Manager, Air Non-Point and Mobile Sources, the DEC
  program that publishes the Fairbanks research materials.
- Cory McDonald: DEC's current first contact for Fairbanks PM2.5.
- AMQA Data Requests: coordination route for monitoring/analytical data.

Fallback only if routing fails: Jason Olds, Division of Air Quality Director,
`jason.olds@alaska.gov`, 907-465-5100. Mailing fallback: Division of Air Quality,
Department of Environmental Conservation, P.O. Box 111800, Juneau, AK
99811-1800.

## Email-body field map

| Item | Value/action |
|---|---|
| Requester name | `[FULL LEGAL NAME]` — user supplies |
| Affiliation | `[AFFILIATION, IF APPLICABLE]` — user supplies |
| Mailing address | `[MAILING ADDRESS]` — user supplies |
| Telephone | `[PHONE]` — user supplies |
| Email | `[EMAIL]` — user supplies |
| Date/place | `[DATE]`, `[CITY, COUNTRY/STATE]` — user supplies |
| Subject | Use the subject above |
| Records description | Paste the full body from `03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md` |
| Short field | Use `03_ADEC_WEB_FORM_SHORT_VERSION.md` only if space is limited |
| Fee cap | USD 25, preserving the Cycle 03 draft cap; change only on explicit user instruction |
| Non-litigation statement | Insert only after the requester confirms it is true |

The optional DEC DOCX/hard-copy form is a separate route. Direct retrieval of
the current DOCX bytes was blocked during this audit, so verify the downloaded
form before entry. Based on the indexed official form text, use this conditional
map:

| Optional-form field | Value/action |
|---|---|
| Certifier name after “I” | `[FULL LEGAL NAME]` |
| Certification clause 1 | Confirm truthfully: requester is not a party to relevant litigation |
| Certification clause 2 | Confirm truthfully: requester is not acting for or representing a party to relevant litigation |
| Certification clause 3 | Confirm truthfully: neither a notary nor another oath-administering official is available at the time |
| DATED | `[DATE]` |
| “at” / place | `[CITY, COUNTRY/STATE]` |
| Requester’s Signature | User signs; Codex must not sign |
| Requester’s Name (print) | `[FULL LEGAL NAME]` |
| Mailing Address | `[MAILING ADDRESS]` |
| Telephone | `[PHONE]` |
| Facsimile | `[FAX]` or leave blank if the current form permits |
| Subject / records description | Use the full body from `03_ADEC_FINAL_PUBLIC_RECORDS_REQUEST.md` |

Affiliation and email are supplemental email-routing fields, not fields shown in
the indexed form. Do not sign the optional form unless all three certification
clauses are true. Otherwise use the plain written-email route or ask DEC for
guidance. Codex must not sign or make the legal certification for the requester.

## Submission checklist

1. Confirm the requester identity/contact fields. The preserved fee cap is USD
   25 unless the user explicitly changes it.
2. Confirm whether the non-litigation statement is truthful. Do not submit a
   false certification. Relevant litigation may require court/administrative
   discovery procedures under AS 40.25.122 and 2 AAC 96.220.
3. Paste the full request into the email body. The DOCX may also be completed and
   attached, but is not the only copy of the request.
4. Review the recipient list and the explicit exclusion of the separate
   Palmer/Ward spreadsheet.
5. Send only after explicit user approval. Preserve the provider receipt, sent
   timestamp, To/CC, exact body, attachments, and message ID.
6. Record any DEC acknowledgment or tracking number and hash every attachment
   before analysis.

## Fee boundary

Alaska may charge search/copy personnel time when the task exceeds five
person-hours in a calendar month, and may charge all required time for an
electronic service/product such as a new query or conversion. This request asks
only for existing native records and requires an itemized estimate before USD 25
is exceeded. The cap is a pause-and-estimate instruction, not a guarantee of
free completion.

## Status

Codex did not transmit, sign, certify, or submit this request. It remains
`BLOCKED_USER_ACTION`.
