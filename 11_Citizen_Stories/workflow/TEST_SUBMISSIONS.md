# Test Submissions and Scenarios

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Checks the requirements in `ENGINEERING_HANDOFF.md`. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and rules

These scenarios prove that the workflow works before launch. Each one has sample input, the steps to take, and the expected result. The acceptance criteria (AC-01 to AC-20) in the handoff are checked by them.

**Rules**
1. **All data is fictional.** People, places and facts are invented. The town "Ilu-Test" does not exist. Never use real people, real contact details or real events.
2. Use only test email addresses at `example.org` and fake phone numbers such as 0000 000 0000.
3. Run tests on a test or staging system, never on the live one, and delete the test data afterwards.
4. Each scenario has a result: PASS, FAIL or BLOCKED. Record it in section 7 with the date, the tester, and a note.
5. A FAIL on any scenario is fixed and the scenario is run again. The workflow is not ready to launch while any criterion fails.

## 2. How to run the tests

| Role | Who runs it |
|---|---|
| Contributor (submits the sample) | Member 8 or a tester |
| Moderator and Editor | Member 8 |
| Verifier ("Test Lead") | Any team member acting as a lead, not a real routing decision |
| Senior reviewer | Member 1, or a stand-in on staging |
| Yoruba-capable reviewer | Anyone who reads Yoruba. This is a test, not the launch appointment (the launch role is confirmed: Faith Ogunlade, D13). |
| Engineering | Member 2, for the system checks |

Run the scenarios in order. Some rely on the ones before, such as the corrections that follow publication.

## 3. Scenario index

| # | Scenario | Type | Language | Expected end state | Criteria |
|---|---|---|---|---|---|
| TS01 | Personal story, no claims | Story | English | `PUBLIC` | AC-09, AC-20 |
| TS02 | Story with one claim, verified | Story | English | `PUBLIC` | AC-03, AC-06 |
| TS03 | Mixed: verified date and hearsay | Story | English | `PUBLIC` | AC-05 |
| TS04 | Claim needs evidence | Story | English | `PUBLIC` | AC-03, AC-05 |
| TS05 | Claim contradicted | Story | English | `PUBLIC` or `REJECTED` | |
| TS06 | Sensitive accusation | Story | English | Sent back, then `PUBLIC` | AC-03, AC-04, AC-05 |
| TS07 | Anonymous story with an identifying detail | Story | English | `PUBLIC` | AC-07 |
| TS08 | Yoruba story | Story | Yoruba | `PUBLIC` | AC-10, AC-11 |
| TS09 | Contributor under 18 | Story | English | `REJECTED` | AC-16, AC-17 |
| TS10 | Ekiti 2056 vision | Vision | English | `PUBLIC` | AC-20 |
| TS11 | Vision with a factual premise | Vision | English | `PUBLIC` | |
| TS12 | Campaign content | Vision | English | `REJECTED` | |
| TS13 | Spam | Story | English | `REJECTED` | |
| TS14 | Other people's private details | Story | English | `PUBLIC` after revision | |
| TS15 | Duplicate | Story | English | `REJECTED` | |
| TS16 | No reply to a revision request | Story | English | `REJECTED` | AC-13 |
| TS17 | Contributor withdraws | Story | English | `WITHDRAWN` | |
| TS18 | Corrections after publication | Story | English | Stays `PUBLIC` | AC-15 |
| TS19 | Privacy concern on a published item | Story | English | `UNPUBLISHED` then `REJECTED` | AC-08 |
| TS20 | Removal request | Story | English | `WITHDRAWN` | AC-08, AC-18 |
| TS21 | Credit change after publication | Story | English | Stays `PUBLIC` | |
| TS22 | Media and form validation | Story | English | Errors, then `PUBLIC` | AC-14, AC-17 |
| TS23 | Second review of a rejection | Story | English | Decision recorded | |
| TS24 | Identity is never public (system check) | Both | Both | Pass or fail | AC-06, AC-19 |
| TS25 | Illegal transitions (system check) | Both | Both | Refused | AC-01, AC-02 |
| TS26 | Message safety (system check) | Both | Both | Blocked or held | AC-11, AC-12 |
| TS27 | Yoruba characters round trip (system check) | Both | Yoruba | Unchanged | AC-10 |

## 4. Sample content

**Test contributors.** All contact details are fake.

| Name | Contact | LGA | Credit choice |
|---|---|---|---|
| Test Contributor A | tester.a@example.org (email) | Ado Ekiti | `FULL_NAME` |
| Test Contributor B | tester.b@example.org (email) | Ikere | `ANONYMOUS` |
| Test Contributor C | 0000 000 0000 (phone) | Outside Ekiti State | `FIRST_NAME` |

**Filler paragraph F.** Story texts must have at least 100 words. Add F after the key text of each story. F contains no claim to check.

> This paragraph is neutral filler used only to reach the minimum length in test submissions. It describes a made-up town called Ilu-Test, where the market opens early, the road bends beside a large tree, and neighbours greet one another in the morning. Nothing in this paragraph is a factual claim about any real place or person. It contains no dates, names of real people, numbers or events, so it should never be routed for verification. Testers may repeat it if a longer text is needed.

**Story key texts.** Title is "Test story" plus the sample number, and the period is "1990s" unless stated.

| Sample | Key text (then add F) |
|---|---|
| S1 | "I remember Saturday mornings at the Ilu-Test market when I was a child. My grandmother always bought pepper from the same trader, and I remember the old banana tree beside the entrance." |
| S2 | "Ilu-Test Grammar School was established in 1978. I attended it in the 1990s and I remember the library beside the assembly hall." |
| S3 | "I remember the old Ilu-Test market square before it was moved. It was moved in 2004, and people said it was because of a dispute." |
| S4 | "The Ilu-Test clinic was the first in the district to offer free vaccinations. I was taken there as a child." |
| S5 | "Ilu-Test Grammar School was established in 1985. I remember my first day there." |
| S6 | "Mr. Fictional Person took money from the Ilu-Test community fund and everyone knows it." |
| S7 | "As the only pharmacist in Ilu-Test in the 1990s, I remember the queues outside my shop every Monday." |
| S8 | A Yoruba story written by a Yoruba speaker, at least 100 words, with one dated claim, for example a year for the market. No text is provided here. `[OPEN-M8]` Member 8 to draft with Faith Ogunlade before this test is run. |
| S9 | "I am 16 years old and I want to tell the story of my school in Ilu-Test." |
| S10 | "My neighbour, Mr. Fictional Neighbour, lives at 12 Test Street and his phone number is 0000 000 0000. I remember visiting him." |
| S11 | The same text as S1, submitted a second time by the same contributor. |
| S12 | "BUY CHEAP FOLLOWERS NOW at http://spam.example.invalid" |

**Test source for verification.** For S2 and S3, the Test Lead consults a fictional "Ilu-Test Register of Schools and Places", a Level 1 source. It lists the school as established in 1978, and the market square as moved in 2004. It has no entry for the clinic, and no entry for the year 1985. It is not a real document. It exists only for this test.

**Vision samples**

| Sample | Fields |
|---|---|
| V1 | Headline: "A skills centre in every LGA by 2056". Vision: "By 2056 every local government area in Ekiti should have a skills centre where young people learn a trade, practise digital skills and get help starting a small business. It should be open to everyone, including adults who want to change careers." Why it matters: "Skills give young people a way to earn a living close to home, and they help small businesses in every community grow." Category: Youth & Entrepreneurship. Credit: `FULL_NAME`. |
| V2 | Headline: "A public library for Ilu-Test". Vision: "Ilu-Test has no public library, so by 2056 the town should have one with a quiet reading room, computers and a children's corner that stays open in the evenings for people who work during the day." Why it matters: "A library gives students and adults a place to read and study, especially where homes are crowded." Category: Education. |
| V3 | Headline: "Vote for Candidate X". Vision: "Everyone in Ekiti should vote for Candidate X of the Test Party in the next election because Candidate X will fix everything in the state within one year, so please share this with everyone you know." Why it matters: "Because Candidate X is the best choice and no other party deserves your vote in any election." Category: Governance & Community Development. |

## 5. Workflow scenarios

Each scenario lists its sample, the steps, and the expected result. T numbers are the transitions in `ENGINEERING_HANDOFF.md` section 6.

### TS01 Personal story, no claims
- **Sample:** S1 + F, contributor A.
- **Steps:** Submit. Moderate (T2, T3). Classify as `PERSONAL_ACCOUNT` with no claims (T7). Editorial review, approve (T10), publish (T15).
- **Expected:** Verification status `NOT_REQUIRED`. M01 sent at submission and M08 at publication. The page shows the label **Citizen account**, the credit line "Shared by Test Contributor A, Ado Ekiti", and the standing statement. There is no Verified facts box. The audit log has one entry per transition (AC-09).

### TS02 Story with one claim, verified
- **Sample:** S2 + F, contributor A.
- **Steps:** Classify `MIXED`. One claim: "established in 1978". Route to the Test Lead (T6). Check what the verifier sees. The Test Lead finds it supported by the test register. Record `VERIFIED`. T8, T10, T15.
- **Expected:** The verifier request shows the claim and context, and **no name or contact**. T10 is refused while the claim is still `NOT_STARTED`. After approval, the page shows the claim in the Verified facts box with its source. The library sentence stays a personal account.

### TS03 Mixed: verified date and hearsay
- **Sample:** S3 + F.
- **Steps:** Two claims: "moved in 2004" and "people said it was because of a dispute". The Test Lead finds the first supported and the second not established. Record `VERIFIED` and `ATTRIBUTED`. Try to set `ATTRIBUTED` without confirming the claim is not harmful. Then confirm and continue.
- **Expected:** The system refuses `ATTRIBUTED` without the confirmation. On the page, only the date appears in the Verified facts box. The reason is worded as what people said. The label is Citizen account.

### TS04 Claim needs evidence
- **Sample:** S4 + F.
- **Steps:** Claim: "the first in the district". The Test Lead finds it not established, so the outcome is `NEEDS_EVIDENCE`. T9 sends M03. The contributor replies "my family told me" (T13, new version). **Branch A:** the reviewer marks it `ATTRIBUTED`. **Branch B (rerun):** the contributor removes the word "first", and the claim record closes.
- **Expected:** T10 is refused while the claim is `NEEDS_EVIDENCE`. In Branch A the claim is worded as "the contributor recalls" and never appears as verified. Unchanged claims keep their outcomes on resubmission.

### TS05 Claim contradicted
- **Sample:** S5 + F.
- **Steps:** The Test Lead finds it contradicted (the register says 1978), so the outcome is `UNSUPPORTED_FALSE`. T9 sends M10. **Branch A:** the contributor agrees to keep it as their recollection. **Branch B:** the contributor does not reply, and the item is rejected at day 30 (T14).
- **Expected:** "1985" never appears as verified. In Branch A an Editor's note may add the register's year, clearly separate from the contributor's text. The contributor's meaning is not changed.

### TS06 Sensitive accusation
- **Sample:** S6 + F.
- **Steps:** Classify with `sensitive = true`, and escalate to the senior reviewer. Try to mark the claim `ATTRIBUTED`. Try T10 without sign-off. Send it back (T9 or T11) asking to remove or reword the accusation. On the new version, the accusation is removed. The senior reviewer signs off and the item is approved.
- **Expected:** `ATTRIBUTED` is refused for a sensitive item. T10 is refused without the senior reviewer's sign-off. Both approvers appear in the audit log. The final page carries no accusation about a named person.

### TS07 Anonymous story with an identifying detail
- **Sample:** S7 + F, contributor B (`ANONYMOUS`).
- **Steps:** During editorial review, flag "the only pharmacist in Ilu-Test" as identifying. Send M04 Variant B. The contributor agrees to generalise it (T11, T13). Approve and publish.
- **Expected:** No change is made without the contributor's agreement. The credit line reads "Shared by an anonymous contributor, Ikere". Search, the page source, share previews and any export show no name or contact.

### TS08 Yoruba story
- **Sample:** S8, contributor A, language Yoruba.
- **Steps:** Submit in Yoruba. Assign a reviewer. Route the dated claim to the Test Lead with the original wording and a marked working translation. Approve and publish.
- **Expected:** Only a user with the `YORUBA_REVIEWER` attribute can be assigned. Yoruba letters and tone marks are unchanged at every step (AC-10). The request to the lead carries the original text. The page is in Yoruba. Any English translation is labelled as a translation. Messages M01 and M08: if no Yoruba template exists, they are held for a person (AC-11).

### TS09 Contributor under 18
- **Sample:** S9 + F.
- **Steps (a):** Submit with "I am 18 or over" unticked. **(b):** Submit with it ticked, and text that states the contributor is 16. In moderation, reject with `UNDER_AGE` (T5).
- **Expected:** (a) The form refuses to submit and says why (AC-17). (b) The item is rejected with `UNDER_AGE`, M11 is sent, and it uses no name or details from the submission (AC-16). How the record is deleted follows the retention policy `[OPEN-M1]`.

### TS10 Ekiti 2056 vision
- **Sample:** V1, contributor A.
- **Steps:** Submit. Moderate. It is classified `VISION_PROPOSAL`. T7 skips verification. Approve and publish.
- **Expected:** Verification status `NOT_REQUIRED`. The page shows **Citizen vision**, the category, the vision-specific standing statement ("not government policy"), and "Why it matters". There is no Verified facts box.

### TS11 Vision with a factual premise
- **Sample:** V2.
- **Steps:** Classify `MIXED`. Route "Ilu-Test has no public library" to the Test Lead. The register has no entry, so the finding is not established. Choose the outcome by the D10 rules.
- **Expected:** The premise goes through verification like any claim. The vision itself is never treated as a fact.

### TS12 Campaign content
- **Sample:** V3.
- **Steps:** Reject in moderation with `CAMPAIGN_CONTENT` (T5).
- **Expected:** Rejected, M09 sent in plain wording, and no internal code shown. This depends on the campaign-material rule `[OPEN-M1]`. If Member 1 changes it, update this scenario.

### TS13 Spam
- **Sample:** S12.
- **Steps:** Reject with `SPAM`.
- **Expected:** Rejected, with **no message sent** `[OPEN-M1]`. The link is displayed as plain text and cannot be clicked by staff.

### TS14 Other people's private details
- **Sample:** S10 + F.
- **Steps:** Moderation check 6 finds a phone number and address. Set `sensitive` if a private matter is mentioned. Send M04 Variant A (T4). The contributor agrees to remove them (T13). Continue to publication.
- **Expected:** The phone number and address are gone from the published version, and earlier versions are kept internally. Nothing is changed without the contributor's reply.

### TS15 Duplicate
- **Sample:** S11 after TS01.
- **Steps:** The system suggests a duplicate. Reject with `DUPLICATE` and link to the original.
- **Expected:** M12 names the original reference. Nothing else is sent.

### TS16 No reply to a revision request
- **Sample:** Any item in `NEEDS_REVISION` (use S4).
- **Steps:** Do not reply. Advance the clock, or ask Engineering to trigger the timers, to day 14, then day 30.
- **Expected:** M05 is sent at day 14 automatically. At day 30 the item is `REJECTED` with `NO_RESPONSE` (T14) and M13 is sent (AC-13).

### TS17 Contributor withdraws
- **Sample:** S1 from a new contributor, at `IN_VERIFICATION` or `IN_EDITORIAL_REVIEW`.
- **Steps:** The contributor asks to withdraw. Confirm the request from the contact on record. Withdraw (T19).
- **Expected:** `WITHDRAWN`, final. It cannot be reopened. A new submission may point to the old one through `related_submission_id`.

### TS18 Corrections after publication
- **Sample:** The published item from TS02.
- **Steps:** (a) A typing error: Editor fixes it. (b) A reader reports that the verified claim is wrong, and the Test Lead confirms a different year: a `CORRECTION_DRAFT` version is approved and swapped in. (c) A reader says "it was 1975" about a personal account (S1-type). No lead can establish it. Decline it and send M17.
- **Expected:** (a) No public note. (b) The page shows a dated **Correction** note and the claim is corrected or loses its Verified label. (c) The account is not rewritten, and if a lead can establish the fact, a separate **Editor's note** may be added. In all three, `status` stays `PUBLIC` (AC-15), and reporter contact details are never shown.

### TS19 Privacy concern on a published item
- **Sample:** A published item.
- **Steps:** A privacy concern is raised. Unpublish at once (T16). Send M14. Then either resolve it (T17 back to editorial review) or give up (T18 to `REJECTED`).
- **Expected:** The item leaves the page, the search index and share previews **immediately** (AC-08). Member 1 is informed. M14 does not say who raised the concern.

### TS20 Removal request
- **Sample:** A published item from contributor A.
- **Steps:** The contributor asks for removal. Confirm the request from the contact on record. Unpublish (T16). Withdraw (T19). Send M18. Delete the personal data as set by the retention settings.
- **Expected:** The item is gone at once (AC-08). M18 says copies elsewhere cannot be recalled. Deletion of the submission and its personal data works (AC-18). If no retention period is set yet, deletion is done by the on-request tool.

### TS21 Credit change after publication
- **Sample:** A published item from contributor A.
- **Steps:** The contributor asks to become anonymous. Confirm the request from the contact on record. Change the credit choice. Send M19.
- **Expected:** The change is made the **same day**. The public page and any share previews show the new credit line, and platform social posts are updated or removed. An audit entry is written.

### TS22 Media and form validation
- **Sample:** S1 + F, plus test images.
- **Steps:** Try each in turn: a story under 100 words, a title over 100 characters, a missing permission tick, a missing caption, no rights confirmation, four images, one image over 5 MB, a GIF file, and a photo taken with location turned on.
- **Expected:** Each of the first eight is refused with a clear message (AC-17). The photo is accepted, and the stored and published copy has **no location or device metadata** (AC-14). Only approved media appears on the page.

### TS23 Second review of a rejection
- **Sample:** A rejected item, for example from TS13-style content that was rejected in error.
- **Steps:** The contributor asks for a second look. Someone who did not make the first decision reviews it. Record the outcome. Send M20.
- **Expected:** One second review only. The reviewer is not the original decider. The outcome and reason are recorded, and the contributor may submit a revised version as a new contribution.

## 6. System checks

### TS24 Identity is never public
- **Steps:** Publish TS01 and TS07. Then look in every place: the public page and its source, the search index, share previews, the RSS or feed if any, any export, the verifier view, and message logs. Search for the test names, emails and phone numbers. Then open a submission's identity as a moderator, and check the identity-access log.
- **Expected:** Contact details appear nowhere public (AC-06). Names appear only in the credit line the contributor chose. The verifier view never shows a name or contact. Each view of identity has a log entry with the user, the time and a reason (AC-19).

### TS25 Illegal transitions
- **Steps:** Try each of these through the interface and through the API: `PENDING` to `PUBLIC`; `IN_MODERATION` to `APPROVED`; `REJECTED` back to any status; `WITHDRAWN` back to any status; `NEEDS_REVISION` to `PUBLIC`; a Verifier trying to approve; a Moderator trying to publish.
- **Expected:** All are refused (AC-01, AC-02), and permission checks run on the server. Only actions valid for the status and role are offered on screen.

### TS26 Message safety
- **Steps:** (a) Try to send a message with an unresolved `{{placeholder}}`. (b) For a Yoruba submission with no Yoruba template, trigger M01 and M08. (c) Try to send to a submission marked `SPAM`.
- **Expected:** (a) Blocked, and the moderator is told which field is missing (AC-12). (b) The messages are held for a person and never sent in English silently (AC-11). (c) Nothing is sent `[OPEN-M1]`. Every sent message has a log entry without the story text.

### TS27 Yoruba characters round trip
- **Character set for the test** (letters only, this text has no meaning): Ẹ Ọ Ṣ ẹ ọ ṣ à á è é ẹ̀ ẹ́ ì í ò ó ọ̀ ọ́ ù ú ń
- **Steps:** Put this string in the title, the body and the credit name. Submit, save, edit, publish, search, export, and include it in an email preview.
- **Expected:** The characters, including combined tone marks, are identical at every step and in every output (AC-10). Nothing shows as boxes or question marks, and sorting and search treat them sensibly.

## 7. Results log

Copy this table into a spreadsheet if easier. Result is PASS, FAIL or BLOCKED.

| # | Date | Tester | Result | Notes and defect link |
|---|---|---|---|---|
| TS01 | | | | |
| TS02 | | | | |
| TS03 | | | | |
| TS04 | | | | |
| TS05 | | | | |
| TS06 | | | | |
| TS07 | | | | |
| TS08 | | | | |
| TS09 | | | | |
| TS10 | | | | |
| TS11 | | | | |
| TS12 | | | | |
| TS13 | | | | |
| TS14 | | | | |
| TS15 | | | | |
| TS16 | | | | |
| TS17 | | | | |
| TS18 | | | | |
| TS19 | | | | |
| TS20 | | | | |
| TS21 | | | | |
| TS22 | | | | |
| TS23 | | | | |
| TS24 | | | | |
| TS25 | | | | |
| TS26 | | | | |
| TS27 | | | | |

## 8. Open items

| Item | Who decides |
|---|---|
| Yoruba story sample (S8) and a Yoruba-capable tester | Member 1 + Member 8 |
| Campaign-material rule (TS12) | Member 1 |
| Whether messages are sent for spam, threats and exploitative content (TS13, TS26) | Member 1 |
| How the record of an under-age submission is deleted (TS09) | Member 1, with the retention policy |
| Test system, test accounts, and a way to advance timers (TS16) | Member 2 (Engineering) |
| Who acts as Test Lead and senior reviewer on staging | Member 8 |
