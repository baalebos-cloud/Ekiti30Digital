# My Ekiti Story — Submission Specification

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `workflow/DECISIONS.md` (D6–D9, D13, D14, D16) and `workflow/CONTRIBUTION_WORKFLOW.md`. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and scope

My Ekiti Story is where citizens share personal experiences, memories, community stories, historical accounts and photographs about Ekiti.

This document specifies what a contributor sees and provides, what the system stores, and what the public sees. What happens after submission (moderation, classification, verification, editorial review) is in `workflow/CONTRIBUTION_WORKFLOW.md`.

A story is published as a **citizen account**. It is not automatically presented as verified history. Specific factual claims inside it can be verified separately.

## 2. Who can submit

- Anyone aged **18 or over**, from any LGA or outside Ekiti (D9). Under-18 contributions are not accepted at launch.
- In **English or Yoruba** (D13). The contributor chooses the language of the submission.

## 3. Contributor journey

1. **Landing page.** Explains what My Ekiti Story is, what happens to a submission, and that a story is a citizen account, not verified history. Links to the writing guide (section 10).
2. **Form.** The fields in section 4.
3. **Preview.** The contributor sees the story as it would appear, including the credit line they chose, and can go back and edit.
4. **Submit.** The system validates the form (section 5), assigns a Submission ID and sets the status to `PENDING` (T1).
5. **Confirmation screen.** Shows the Submission ID and what happens next in plain words. The same message is sent to the contact address or number.
6. **Follow-up.** The contributor is contacted only when we need a clarification, when the story is approved or published, or when it cannot be published. Wording comes in Phase 4 (`workflow/MESSAGE_TEMPLATES.md`).
7. **Status lookup (optional).** The contributor can check status with the Submission ID and contact. `[OPEN-M2]`

## 4. Form fields

| Field | Key | Type | Required | Rules | Public |
|---|---|---|---|---|---|
| Language of submission | `language` | Choice: English / Yoruba | Yes | | Yes (label) |
| Name | `contributor_name` | Text, max 80 | Yes | Full name recommended. Used according to the credit choice. | Per credit choice |
| Contact method | `contact_method` | Choice: Email / Phone / WhatsApp | Yes | | Never |
| Contact | `contact_value` | Text | Yes | Valid email or phone number | Never |
| Location / LGA | `lga` | Choice | Yes | The 16 Ekiti LGAs, plus "Outside Ekiti State" (D16) | Yes |
| Story title | `story_title` | Text, max 100 | Yes | | Yes |
| Story | `story_text` | Long text | Yes | 100 to 2,000 words | Yes |
| Year / period | `year_period` | Text, max 40, plus a "Not sure" option | Yes | Examples: "1998", "late 1990s", "2015 to 2018" | Yes |
| Photo / media | `media_files` | Image upload | No | See section 6 | Only if approved |
| Caption | `media_caption` | Text, max 200 per image | If media | | Yes, with the image |
| Media credit | `media_credit` | Text, max 80 | No | Defaults to the contributor's credit line | Yes, with the image |
| I have the right to share this media | `media_rights_confirmed` | Checkbox | If media | | No |
| Anyone recognisable in the photos has agreed to it being published | `media_people_ok` | Checkbox | If media shows people | | No |
| Permission to publish | `permission_to_publish` | Checkbox | Yes | Wording in section 7 | No |
| Also share on EKITI@30 DIGITAL social media | `promote_on_social` | Checkbox | No | Separate from publishing on the platform (D16) | No |
| Contributor credit | `credit_choice` | Choice | Yes | Full name + LGA / First name + LGA / Anonymous (`workflow/CREDIT_AND_ANONYMITY.md`) | Applied |
| I am 18 or over | `age_18_confirmed` | Checkbox | Yes | | No |
| I have read the privacy notice | `privacy_ack` | Checkbox | Yes | Wording in section 7 | No |

**System fields**, set by the platform and never by the contributor:

| Key | Description |
|---|---|
| `submission_id` | Unique ID |
| `submitted_at` | Timestamp |
| `submission_type` | `MY_EKITI_STORY` |
| `status` | Lifecycle status (`DECISIONS.md` D2) |
| `classification`, `sensitive` | Set at classification (D3) |
| `verification_status`, `editorial_status` | Set during review (D2) |
| `assigned_reviewer`, `escalated_to` | Reviewer and specialist assignments |
| `version`, `related_submission_id` | Version number, and link to an earlier submission if any |

The Issue's "Review Status" field is `status` plus the two review statuses. Contributors see the plain-language version in section 8.

**Not collected:** date of birth, home address, ID numbers, precise location (D6, D14).

## 5. Validation and limits — PROPOSED, to be tuned after testing

- All required fields must be filled, and all required checkboxes ticked.
- Story length is 100 to 2,000 words. Title is at most 100 characters.
- Email or phone must be in a valid format.
- Links in the text are allowed but are checked in moderation (`workflow/MODERATION_GUIDE.md`, check 4).
- Unicode is fully supported so that Yoruba letters and tone marks are stored and shown correctly (D13).
- A contributor may submit more than one story, and each is a separate submission.
- The form protects against spam and repeat posting. `[OPEN-M2]` Method to be chosen by Engineering.

## 6. Media rules — PROPOSED `[OPEN-M2]`

- Images only at launch: JPG or PNG, up to 3 per story, up to 5 MB each. Video and audio are a later decision.
- The contributor confirms they have the right to share the media. Copyright is checked in moderation (check 8).
- **Location and device data are removed** from uploaded images (EXIF metadata), so that a photo cannot reveal where someone lives (D14).
- Photos showing identifiable people need those people's agreement. Photos of children are not published without a parent's or guardian's permission (D9, moderation check 6).
- Media is published only if the story is approved and the contributor's permission covers it (D14).
- Every image needs a caption. The credit defaults to the contributor's credit line.
- For anonymous contributors, images that reveal the contributor's face or location are flagged for the contributor's decision before publication (`workflow/CREDIT_AND_ANONYMITY.md`).

## 7. Consent and privacy wording — DRAFT `[OPEN-M1]`

Final wording needs Member 1's approval. It is not legal advice.

**Permission to publish (checkbox, required)**

> I give EKITI@30 DIGITAL permission to review my contribution, edit it for clarity without changing its meaning, and publish it on the platform, credited as I have chosen. I understand that my story is published as my own account and is not automatically presented as verified history. I can ask for a correction or for removal at any time.

**Ownership (part of the same section)**

> This story is mine to share, or I have permission to share it. I have not included other people's private details such as phone numbers or home addresses.

**Social media (checkbox, optional)**

> EKITI@30 DIGITAL may also share my published story on its social media channels.

**Privacy notice (short form, shown above the submit button)**

> We collect your name, contact details, LGA and your story so that we can review it, contact you and publish it. Your contact details are never shown publicly and are seen only by the reviewers who need them. If your contribution is not published, we keep your contact details for 90 days and then delete them. Related content and messages are kept for up to 12 months for records, then deleted. To ask for changes or removal, contact [contact address to be set].

The retention sentence is a placeholder until the retention policy exists (`DECISIONS.md` D14).

## 8. What the contributor sees

Contributors see plain-language statuses, never internal status names.

| Internal status | Contributor sees |
|---|---|
| `PENDING` | Received |
| `IN_MODERATION`, `IN_CLASSIFICATION`, `IN_EDITORIAL_REVIEW` | Under review |
| `IN_VERIFICATION` | Under review. We may be checking some details. |
| `NEEDS_REVISION` | We need something from you (with the specific request) |
| `APPROVED` | Approved, publishing soon |
| `PUBLIC` | Published (with the link) |
| `REJECTED` | Not published (with the reason and, where possible, how to submit again) |
| `WITHDRAWN` | Withdrawn |
| `UNPUBLISHED` | Removed from public view while we resolve a concern |

Contributors are never shown reviewer names, internal notes or the notes of a verifier.

## 9. Public presentation

Each published story shows:

- The title and the label **Citizen account**.
- The credit line (`Shared by …`) and the LGA.
- The period, and the language of the submission.
- The story text, as edited under the editing rule (`workflow/CONTRIBUTION_WORKFLOW.md` section 5).
- Media, each with its caption and credit.
- A **Verified facts** box, only when at least one claim is `VERIFIED`, listing the claim and its source.
- A note "Edited for clarity" where edits went beyond spelling and grammar (`workflow/CREDIT_AND_ANONYMITY.md` section 6).
- The publication date, and any correction notice (`workflow/CORRECTIONS_AND_CLARIFICATIONS.md`).
- A **Suggest a correction** link.

Standing statement on each page:

> This is a personal account shared by a citizen. It is not automatically verified history. Facts marked Verified have been checked against a source.

Contact details, reviewer notes and anonymous identities never appear on public pages.

## 10. Writing guide for contributors

Shown on the landing page and beside the form.

**Prompts**
- A place in your community as you remember it
- A person who shaped your community
- A day or event you will never forget
- How your town or village has changed since 1996
- A festival, tradition or skill in your family or community
- What life was like at a school, market, clinic or workplace

**Do**
- Write about what you saw, felt or lived through.
- Say roughly when it happened. "Around 2005" is fine.
- Say if something is what you were told and not what you saw.

**Don't**
- Include other people's phone numbers, addresses or private details.
- Make serious accusations against named people.
- Copy text from books or websites.
- Upload photos you do not have the right to share.

You do not need to prove anything. We may ask about a specific date or fact, and that is a check on one detail, not on your story.

## 11. Open items

| Item | Who decides |
|---|---|
| Final consent and privacy wording, contact address for removal requests, retention sentence | Member 1 |
| Length limits, media limits and file types, spam protection, status lookup | Member 2 (Engineering) |
| Public layout and labels (with Member 6) | Member 2 |
| LGA list source: names and spellings must match Member 5's LGA dataset (Issue #5) | Member 5 |
| Interface text in Yoruba: who translates it | Member 1 + Member 8 |
