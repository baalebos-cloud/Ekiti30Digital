# Corrections and Clarifications

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `DECISIONS.md` D8, D10, D12, D14; `CONTRIBUTION_WORKFLOW.md` (T4, T9, T11, T13, T14, T16–T19). Unresolved items are tagged `[OPEN-Mx]`.

## 1. Principles

1. **Never change a contributor's meaning silently.** Anything that may change meaning is agreed with the contributor first.
2. **Corrections are visible.** A change that matters to readers is shown as a dated note, not hidden.
3. **Privacy and harm come first.** A concern about privacy or harm takes content off public view immediately, while it is reviewed (T16).
4. **Facts and accounts are corrected differently.** A verified fact that turns out wrong is corrected. A contributor's personal account is not "corrected" because someone remembers differently (section 4).
5. **Everything is recorded.** Each correction is a record with a decision and a reason.

## 2. Before and after publication

| Situation | Where it happens |
|---|---|
| Something is unclear or missing **before publication** | A clarification request (section 3), using `NEEDS_REVISION` (T4, T9, T11) |
| Something is wrong or needs to change **after publication** | A correction record (sections 4 and 5) |

## 3. Clarification requests before publication

A clarification request is a message from us to the contributor asking for something specific: a source, a date, the meaning of a phrase, a removal of a private detail, or the confirmation of an edit.

**How to ask**
1. One message, with numbered and specific questions. No vague "please improve your story".
2. Use neutral wording. Do not suggest that the contributor is lying or careless.
3. Use the contact channel on record, and never public comments.
4. Write in the language of the submission. A Yoruba submission gets a Yoruba message (D13).
5. Say what will happen next and by when. The reply window is 30 days, with a reminder at day 14 (`CONTRIBUTION_WORKFLOW.md` section 10).
6. Never reveal internal notes, reviewer names, or verifier findings beyond what the contributor needs to reply.

**When the reply arrives**
- Record it, and store the new version (T13). Unchanged claims keep their earlier outcomes.
- If the answer is unclear, ask once more. If it is still unclear, the reviewer decides using the approval rules (`CONTRIBUTION_WORKFLOW.md` section 8).
- If there is no reply by day 30, the submission is rejected with the reason `NO_RESPONSE`, and the contributor can submit again (T14).

Message wording is in Phase 4 (`MESSAGE_TEMPLATES.md`).

## 4. Corrections after publication

**Who can raise one**
- The contributor.
- A reader, through **Suggest a correction** on the page. The reader's contact is optional, so we collect as little as possible (D14).
- A reviewer or team member.
- A research or content lead who finds an error, including new evidence that contradicts a `VERIFIED` claim.

**Types**

| Type | Example | Handling |
|---|---|---|
| Typing or formatting | Spelling, punctuation, a broken image | Member 8 fixes it. Logged. No public note needed. |
| Contributor updates their own story | Adds detail, changes what they wrote | Treated as a new version. Goes through editorial review, and through verification if it adds factual claims. |
| Error in a `VERIFIED` claim | A lead finds a different source, or a reader reports an error | Routed to the relevant lead. If confirmed, the claim is corrected or the Verified label is removed, with a public note. |
| Reader disagrees with a personal account | "It was 1975, not 1978" | The account stays the contributor's account. If the lead can establish the fact, an **Editor's note** may be added next to it, clearly separate from the contributor's text. Nothing is rewritten. |
| Credit or anonymity | Contributor wants a different credit line | `CREDIT_AND_ANONYMITY.md` section 9 |
| Privacy or harm concern | Private detail exposed, a threat, a harmful allegation | Immediate `UNPUBLISHED` (T16), then review (section 5) |
| Removal request | Contributor wants the item taken down | Section 7 |

A reader's report is itself checked for abuse and spam before action.

## 5. Handling a correction

1. **Receive.** Create a correction record (section 9), and acknowledge to the reporter if they gave contact details.
2. **Triage.** Member 8 sets the type and urgency. Privacy or harm concerns are urgent.
3. **Protect.** For privacy or harm, set the item to `UNPUBLISHED` at once (T16), and inform Member 1.
4. **Review.**
   - Typing or formatting: apply directly.
   - Content changes: prepare the changed version as a **draft version linked to the correction**.
   - Fact issues: route to the relevant lead (`VERIFICATION_WORKFLOW.md`).
   - Sensitive issues: Member 1 or the designated senior reviewer signs off.
5. **Decide.** Apply, decline, or escalate. Every decision has a written reason.
6. **Publish the change.** When approved, the draft version replaces the live version, and a public note is added when needed (section 6).
7. **Close and tell.** Inform the contributor, and the reporter if they gave contact details.

**Live status while a correction is reviewed.** Content stays `PUBLIC` while a correction is reviewed, unless privacy or harm is involved (D12). The lifecycle status does not change for a content correction. The draft version is reviewed under its own correction record, and the live version is swapped only when it is approved. For a privacy or harm concern, the item is `UNPUBLISHED` first, and then follows T17 or T18. `[OPEN-M2]` Engineering to confirm this version-swap approach.

## 6. Public notes

Three kinds of note may appear on a published item. Each is dated and clearly separate from the contributor's text.

| Note | When used | Example wording |
|---|---|---|
| **Updated** | The contributor changed their own content | "Updated on [date] by the contributor." |
| **Correction** | A verified fact was wrong, or a factual error was fixed | "Correction, [date]: this page said [X]. The correct information is [Y], according to [source]." |
| **Editor's note** | New evidence relates to a claim in a personal account | "Editor's note: records from [source] give [Y]. The account above is the contributor's recollection." |

Rules:
- Notes state the change and the reason, without blame.
- A note is never used to rewrite a contributor's account in the contributor's voice.
- Previous versions are kept internally (`CONTRIBUTION_WORKFLOW.md` section 7). Public pages show only the latest version and its notes.

## 7. Removal requests

A contributor can ask for their item to be removed at any time, by their contact channel on record.

1. **Confirm the request** comes from the contributor's contact channel on record (same-day, and not a reason to delay).
2. **Unpublish** at once (T16). Social posts made by the platform are removed too.
3. **Withdraw** the submission (T19) once removal is confirmed.
4. **Personal data.** The contributor's data is handled under the retention policy. `[OPEN-M1]` The response time and the deletion period are open until the privacy notice and retention policy exist (D14).
5. **Tell the contributor** what was removed, and that copies shared elsewhere by others cannot be recalled by us.

Requests to remove an item from someone who is not the contributor are handled as privacy or harm concerns (section 4), and are decided by Member 8 with Member 1 informed.

## 8. Disagreeing with a decision

A contributor who disagrees with a rejection or an editorial decision may ask for it to be looked at again.

- One second review, by a person who did not make the original decision (Member 1 or a designated senior reviewer). PROPOSED `[OPEN-M1]`
- The reviewer reads the submission and the reason code, and may ask Member 8 for the record.
- The outcome is final for that submission, and the contributor is told the reason.
- The contributor can always submit a revised version as a new contribution.

## 9. Correction record

| Field | Description |
|---|---|
| `correction_id` | Unique ID |
| `submission_id` | The item concerned |
| `reported_by` | `CONTRIBUTOR`, `READER`, `REVIEWER` or `LEAD` |
| `reporter_contact` | Optional, restricted access, never public |
| `date_received`, `date_resolved` | Dates |
| `type` | Typing, own update, verified-claim error, disagreement, credit, privacy or harm, removal |
| `description` | What is reported |
| `evidence` | Sources or explanation offered |
| `status` | `OPEN`, `IN_REVIEW`, `APPLIED`, `DECLINED`, `WITHDRAWN` |
| `decision_reason` | Why it was applied or declined |
| `decided_by` | Reviewer |
| `public_note` | The note shown on the page, if any |
| `draft_version`, `live_version` | The versions involved |

## 10. Timings — PROPOSED, to be tuned after testing

| Step | Target |
|---|---|
| Privacy or harm concern about published content | Same day |
| Removal request | Same day, once confirmed |
| Acknowledge a correction request | 2 working days |
| Decide a typing, credit or own-update correction | 3 working days |
| Decide a factual correction, with the lead's finding | 7 working days |
| Second review of a decision | 7 working days |

## 11. Rules for engineering

- Corrections are their own records, linked to the submission.
- A submission has a `live_version` and can have one `draft_version` per open correction. Swapping versions writes an audit entry and does not change the lifecycle `status`.
- Public pages show notes (Updated, Correction, Editor's note) with dates. They never show reporter details.
- Every correction writes an audit entry: `correction_id`, `submission_id`, `actor`, `time`, `from`, `to`, `reason`.
- The "Suggest a correction" form works without an account, is protected against spam, and requires no contact details.
- Unpublishing removes the item from public pages, search indexes and share previews immediately.

## 12. Open items

| Item | Who decides |
|---|---|
| Version-swap approach for live content | Member 2 (Engineering) |
| Second-review policy and who performs it | Member 1 |
| Removal response time and personal-data deletion period | Member 1, with the retention policy |
| Whether readers can contact us by email as well as by the form | Member 2 + Member 8 |
