# Engineering Handoff — Citizen Contribution Workflow

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
For: Member 2 (Engineering). Written without assuming a technology stack. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and how to use this document

This document turns the My Ekiti Story and Ekiti 2056 workflow into build requirements: who can do what, what is stored, which status changes are allowed, what the public sees, and how to tell that it works.

**Sources.** This is a summary. If it differs from a source file, the source file wins. Please tell Member 8 so the summary can be corrected.

| Topic | Source file (in `11_Citizen_Stories/`) |
|---|---|
| Decisions and confirmations | `workflow/DECISIONS.md` |
| Stages, classification, transitions T1 to T19, approval rules | `workflow/CONTRIBUTION_WORKFLOW.md` |
| Moderation checks and reason codes | `workflow/MODERATION_GUIDE.md` |
| Claim records and verification outcomes | `workflow/VERIFICATION_WORKFLOW.md` |
| Credit and anonymity | `workflow/CREDIT_AND_ANONYMITY.md` |
| Corrections, removal, second review | `workflow/CORRECTIONS_AND_CLARIFICATIONS.md` |
| Contributor messages M01 to M20 | `workflow/MESSAGE_TEMPLATES.md` |
| My Ekiti Story form and public page | `MY_EKITI_STORY_SPEC.md` |
| Ekiti 2056 form and public page | `../12_Ekiti_2056/EKITI_2056_SPEC.md` |
| Tests | `workflow/TEST_SUBMISSIONS.md` |

**Status of the requirements.** Confirmed by Member 1: 18+ only at launch (D9), sign-off and unverified-claim rules (D10), English and Yoruba (D13), data minimisation with approved launch retention periods (D14: 90 days for rejected contact details, 12 months for rejected content, corrections and messages). D2, D6 and D16 remain PROPOSED — Member 2 did not respond by the agreed deadline, so these are recorded as accepted follow-up work and do not block launch. Please pick these up when you are able; everything marked `[OPEN-M2]` follows the same status.

**Three rules to keep in mind throughout**
1. Moderation, verification and editorial approval are separate checks with separate records.
2. A personal story is a citizen account. Only specific claims inside it can be verified.
3. Contributor identity and contact details are never public, and are seen only by designated reviewers.

## 2. Scope: launch build and later

| Area | Launch (must have) | Later |
|---|---|---|
| Forms | My Ekiti Story and Ekiti 2056 forms with validation, preview and confirmation. No contributor account. | Contributor status lookup by reference number and contact |
| Review | Reviewer queue, moderation, classification, claim records, editorial review, approval with permission checks | Bulk tools, analytics beyond counts |
| Verification | Claim routing to leads, with a limited verifier view or an equivalent process (Q4) | |
| Publication | Public pages with labels, credit line, Verified facts box, correction notes, Suggest a correction | Public search across citizen content |
| Messages | M01 to M20 by email, with preview and placeholder blocking. Phone and WhatsApp contributors are contacted by a person, with a log entry. | SMS or WhatsApp sending |
| Corrections | Correction and removal handling, unpublish, credit changes | |
| Privacy | Role-based access, identity access log, EXIF stripping, configurable retention, deletion | |
| Media | Images only | Audio and video |
| Contributors | 18 and over only (D9) | Under 18, once a guardian and consent workflow exists |
| Knowledge base | **None.** Citizen content is never added to the knowledge base or Ask Ekiti automatically (`workflow/VERIFICATION_WORKFLOW.md` section 9). | Verified claims proposed through Member 4 `[OPEN-M3]` |

**Suggested build order**
1. Forms, storage, and the split between identity data and content.
2. Roles, reviewer queue, status transitions and audit log.
3. Claim records and the verifier view.
4. Public pages, credit line and labels.
5. Contributor messages.
6. Corrections, unpublish and removal.
7. Retention settings and deletion.

## 3. Roles and permissions

One person may hold several roles. Every action is checked against a role on the server, never only in the interface.

| Role | Who at launch | Notes |
|---|---|---|
| Contributor | Anyone. No account. | Identified only by the submission reference and contact |
| Moderator | Member 8, and any designated moderator | Stages 1 and 2 |
| Editor | Member 8 | Editorial review, approval, publication |
| Verifier | Members 4, 5 and 7, as routed (D11) | Sees only the claims assigned to them |
| Senior reviewer | Member 1 (D10). Another person only if Member 1 designates one. | Sign-off on sensitive items |
| Admin | Engineering | Technical administration. No content or identity access by default. |
| Yoruba-capable reviewer | Launch assignment: Faith Ogunlade (D13). Implemented as an assignable attribute (`reviewer_role = YORUBA_REVIEWER`) so a backup can be added the same way. | Given to any moderator or editor who reads Yoruba |

| Action | Moderator | Editor | Verifier | Senior reviewer | Admin |
|---|---|---|---|---|---|
| See submission content and versions | Yes | Yes | Assigned claims only | Yes | No (break-glass, logged) |
| See contributor identity and contact | Yes, logged | Yes, logged | **No** | Yes, logged | No (break-glass, logged) |
| Moderate and classify (T2 to T7) | Yes | No | No | No | No |
| Record a claim finding | No | No | Yes | Yes | No |
| Record a claim outcome (T8, T9) | Yes | No | No | No | No |
| Edit content, which creates a version | No | Yes | No | No | No |
| Approve (T10) | No | Yes | No | Sign-off only (sensitive items) | No |
| Publish (T15) | No | Yes | No | No | No |
| Unpublish (T16) | Yes | Yes | No | Yes | No |
| Reject or withdraw (T5, T12, T14, T18, T19) | Yes | Yes | No | Yes | No |
| Send messages | Yes | Yes | No | Yes | No |
| Change a credit choice | Yes | Yes | No | No | No |
| Edit message templates | No | Yes | No | No | No |
| Configure retention, roles, lists | No | No | No | No | Yes |
| View audit and identity-access logs | No | Yes | No | Yes | Yes |
| Export data without identity fields | No | Yes | No | Yes | Yes |
| Export data with identity fields | No | No | No | No | No |

"Break-glass" means access for a real support need, with a reason recorded in the identity-access log and Member 1 informed `[OPEN-M1]`. Export with identity fields is off at launch.

## 4. Data model

Names are for clarity. Use your own conventions. **Identity data must live apart from content data,** so that no public query or export can reach it by accident.

**contributor** (restricted access)

| Field | Type | Notes |
|---|---|---|
| `contributor_id` | ID | One per submission. No profile is built across submissions at launch (D14). |
| `contributor_name` | text, max 80 | As entered, with spelling and diacritics kept |
| `contact_method` | enum | `EMAIL`, `PHONE`, `WHATSAPP` |
| `contact_value` | text | Validated for the method |

**submission**

| Field | Type | Notes |
|---|---|---|
| `submission_id` | ID | Shown to the contributor as the reference number |
| `submission_type` | enum | `MY_EKITI_STORY`, `EKITI_2056` |
| `language` | enum | `ENGLISH`, `YORUBA` |
| `contributor_id` | ID | |
| `lga` | text | One of the 16 LGAs, or "Outside Ekiti State" (D16) |
| `lga_display_override` | text, optional | For example "Ekiti State", only with the contributor's agreement (`workflow/CREDIT_AND_ANONYMITY.md` section 8) |
| `credit_choice` | enum | `FULL_NAME`, `FIRST_NAME`, `ANONYMOUS` |
| `credit_first_name` | text, optional | Used for `FIRST_NAME`. Confirmed by the contributor in the preview (Q12). |
| `permission_to_publish` | boolean | Must be true |
| `promote_on_social` | boolean | Separate, optional |
| `age_18_confirmed` | boolean | Must be true (D9) |
| `privacy_ack` | boolean | Must be true |
| `consent_text_version` | ID | The exact consent and privacy wording the contributor saw |
| `status` | enum | Lifecycle status (section 5) |
| `classification` | enum | Section 5 |
| `sensitive` | boolean | Default false |
| `verification_status` | enum | Section 5 |
| `editorial_status` | enum | Section 5 |
| `assigned_reviewer` | user | For Yoruba, a user with the `YORUBA_REVIEWER` attribute |
| `escalated_to` | user, optional | An assignment, never a status |
| `live_version` | ID | The version the public sees |
| `related_submission_id` | ID, optional | Link to an earlier submission |
| `submitted_at`, `updated_at`, `published_at` | timestamp | Africa/Lagos for display |

**submission_version**

| Field | Type | Notes |
|---|---|---|
| `version_id`, `submission_id`, `version_no` | | Earlier versions are never overwritten or deleted, except under retention rules |
| `kind` | enum | `SUBMITTED`, `EDITED`, `REVISION`, `CORRECTION_DRAFT` |
| `title` | text | `story_title` or `vision_headline`, max 100 |
| `body` | long text | `story_text` (100 to 2,000 words) or `vision_text` (30 to 500 words) |
| `year_period` | text, max 40 | Stories only |
| `category` | enum | Visions only (`EKITI_2056_SPEC.md` section 5) |
| `why_it_matters` | long text | Visions only, 20 to 200 words |
| `created_at`, `created_by` | | |

**media**

| Field | Type | Notes |
|---|---|---|
| `media_id`, `submission_id`, `version_id` | | |
| `file_reference` | | Stored with location and device metadata removed |
| `caption` | text, max 200 | Required |
| `media_credit` | text, max 80 | Defaults to the credit line |
| `rights_confirmed`, `people_ok` | boolean | |
| `approved_for_publication` | boolean | Default false |

**claim** (one per checkable claim, `workflow/VERIFICATION_WORKFLOW.md` section 5)

| Field | Type | Notes |
|---|---|---|
| `claim_id`, `submission_id`, `version_id` | | |
| `claim_text`, `claim_translation` | text | Original wording, and a marked working translation for Yoruba |
| `subject_area`, `routed_to` | | Routing per D11 |
| `date_routed`, `date_resolved` | date | |
| `finding` | enum | `SUPPORTED`, `CONTRADICTED`, `NOT_ESTABLISHED` |
| `outcome` | enum | Section 5 |
| `sources`, `source_level`, `notes` | | Levels 1 to 4 |
| `attributed_confirmed_by` | user | Required when the outcome is `ATTRIBUTED` (section 6) |
| `reviewer` | user | The lead who made the finding |

**correction** (`workflow/CORRECTIONS_AND_CLARIFICATIONS.md` section 9)

`correction_id`, `submission_id`, `reported_by` (`CONTRIBUTOR`, `READER`, `REVIEWER`, `LEAD`), `reporter_contact` (optional, restricted), `date_received`, `date_resolved`, `type`, `description`, `evidence`, `status` (`OPEN`, `IN_REVIEW`, `APPLIED`, `DECLINED`, `WITHDRAWN`), `decision_reason`, `decided_by`, `public_note`, `draft_version`, `live_version`.

**Supporting records**

| Record | Fields | Notes |
|---|---|---|
| `audit_log` | `audit_id`, `entity_type`, `entity_id`, `action`, `from_value`, `to_value`, `actor`, `actor_role`, `timestamp`, `reason_code`, `note` | Append only. Holds no contact details. |
| `identity_access_log` | `user`, `submission_id`, `timestamp`, `reason` | Written on every view of identity or contact |
| `message_log` | `message_id`, `submission_id` or `correction_id`, `template_id`, `language`, `channel`, `sent_at`, `sent_by`, `state` (`SENT`, `HELD`, `FAILED`) | Holds no story text |
| `message_template` | `template_id` (M01 to M20), `language`, `subject`, `body`, `version`, `state`, `approved_by` | Stored as data, never in code |
| `consent_text` | `version`, `type`, `text`, `effective_from` | |
| `retention_setting` | `data_type`, `period_days` (seeded with approved defaults: 90 for rejected contact details, 365 for rejected content/corrections/messages), `action` (`DELETE`, `ANONYMISE`), `updated_by`, `updated_at` | Section 11 |
| `user` | `user_id`, `name`, `roles`, `reviewer_role`, `active` | |
| Reference lists | 16 LGAs plus "Outside Ekiti State" (names from Member 5's dataset), 10 vision categories | Editable by an admin |

## 5. Enumerations

| Name | Values |
|---|---|
| Lifecycle `status` | `PENDING`, `IN_MODERATION`, `IN_CLASSIFICATION`, `IN_VERIFICATION`, `IN_EDITORIAL_REVIEW`, `NEEDS_REVISION`, `APPROVED`, `PUBLIC`, `REJECTED`, `WITHDRAWN`, `UNPUBLISHED` |
| `classification` | `PERSONAL_ACCOUNT`, `FACTUAL_CLAIM`, `OPINION`, `VISION_PROPOSAL`, `MIXED` |
| `verification_status` (submission) | `NOT_STARTED`, `NOT_REQUIRED`, and the claim outcomes below |
| Claim `outcome` | `VERIFIED`, `ATTRIBUTED`, `OPINION_VISION`, `NEEDS_EVIDENCE`, `UNSUPPORTED_FALSE` |
| `editorial_status` | `NOT_REVIEWED`, `REVIEWED`, `REVISION_REQUESTED` |
| Moderation reason codes | `SPAM`, `ABUSIVE_OR_HATEFUL`, `THREAT_OR_HARASSMENT`, `EXPLOITATIVE`, `PRIVACY_CONCERN`, `COPYRIGHT_ISSUE`, `INSUFFICIENT_INFORMATION`, `UNSUPPORTED_CLAIM`, `MISLEADING`, `DUPLICATE`, `OFF_TOPIC`, `UNDER_AGE`, `CAMPAIGN_CONTENT`, `NO_RESPONSE`, `OTHER` |
| `credit_choice` | `FULL_NAME`, `FIRST_NAME`, `ANONYMOUS` |
| Vision categories | Education; Health; Agriculture; Technology & Innovation; Youth & Entrepreneurship; Economy & Jobs; Infrastructure & Environment; Culture, Heritage & Tourism; Governance & Community Development; Other |

**Submission-level `verification_status`** is derived: `NOT_STARTED` when claims are routed and none is resolved, `NOT_REQUIRED` when there are no checkable claims, and otherwise the set of claim outcomes. The individual claim outcomes are the source of truth.

**No `guardian_consent_status` exists at launch.** Under-18 contributors are not accepted (D9).

## 6. Status transitions with permissions and rules

The full list of allowed changes is in `workflow/CONTRIBUTION_WORKFLOW.md` section 6. This table adds who may make each change, what must be true, and what happens. **Any change not listed is refused.**

| # | From to | Who | Must be true | Effects |
|---|---|---|---|---|
| T1 | (new) to `PENDING` | System | Required fields valid, `permission_to_publish`, `age_18_confirmed`, `privacy_ack`, `credit_choice`, media confirmations if media | M01 sent. Audit entry. |
| T2 | `PENDING` to `IN_MODERATION` | Moderator | A reviewer is assigned. For Yoruba, one with the `YORUBA_REVIEWER` attribute. | `assigned_reviewer` set |
| T3 | `IN_MODERATION` to `IN_CLASSIFICATION` | Moderator | Moderation note recorded | |
| T4 | `IN_MODERATION` to `NEEDS_REVISION` | Moderator | Reason code and message to contributor | M02, M03 or M04. Reply timer starts. |
| T5 | `IN_MODERATION` to `REJECTED` | Moderator | Reason code | M09, M11 or M12. **No message** for `SPAM`, `THREAT_OR_HARASSMENT`, `EXPLOITATIVE` `[OPEN-M1]`. |
| T6 | `IN_CLASSIFICATION` to `IN_VERIFICATION` | Moderator | Classification set, `sensitive` set or cleared, at least one claim record with `routed_to` | Verification status `NOT_STARTED`. Request to lead. Timer starts. |
| T7 | `IN_CLASSIFICATION` to `IN_EDITORIAL_REVIEW` | Moderator | `PERSONAL_ACCOUNT`, `OPINION` or `VISION_PROPOSAL`, with no checkable claim | Verification status `NOT_REQUIRED` |
| T8 | `IN_VERIFICATION` to `IN_EDITORIAL_REVIEW` | Moderator | Every claim has an outcome | |
| T9 | `IN_VERIFICATION` to `NEEDS_REVISION` | Moderator | A claim is `NEEDS_EVIDENCE` or `UNSUPPORTED_FALSE`, with a message to contributor | M03 or M10 |
| T10 | `IN_EDITORIAL_REVIEW` to `APPROVED` | Editor. Also the senior reviewer if `sensitive`. | Approval rules below | Every approver recorded |
| T11 | `IN_EDITORIAL_REVIEW` to `NEEDS_REVISION` | Editor | Requested changes recorded | M02, M04 or M06 |
| T12 | `IN_EDITORIAL_REVIEW` to `REJECTED` | Editor | Reason code | M09 or M10 |
| T13 | `NEEDS_REVISION` to `IN_MODERATION` | System | Contributor resubmits | New version stored. Unchanged claims keep their outcomes. |
| T14 | `NEEDS_REVISION` to `REJECTED` | System or Editor | 30 days with no reply | `NO_RESPONSE`. M13. M05 was sent at day 14. |
| T15 | `APPROVED` to `PUBLIC` | Editor | Credit line generated, public output valid (section 8) | `published_at` set. M08 sent. |
| T16 | `PUBLIC` to `UNPUBLISHED` | Moderator, Editor or Senior reviewer | Reason recorded | **Removed immediately** from pages, search index and share previews. M14. Member 1 informed. |
| T17 | `UNPUBLISHED` to `IN_EDITORIAL_REVIEW` | Editor | Note on the concern | |
| T18 | `UNPUBLISHED` to `REJECTED` | Editor | Reason code | |
| T19 | Any status except `PUBLIC`, `REJECTED`, `WITHDRAWN`, to `WITHDRAWN` | Moderator or Editor | Request confirmed from the contact on record | If it was ever public, T16 comes first. M18. |

**Approval rules for T10** (all must be true)
1. Moderation accepted it.
2. Classification is recorded, and `sensitive` is set or cleared.
3. Every claim has a recorded finding, and none is `NOT_STARTED`, or `NEEDS_EVIDENCE` without a recorded resolution.
4. The editorial checklist is complete, and any edit that could change meaning has the contributor's agreement recorded.
5. `permission_to_publish` and `age_18_confirmed` are true, and the credit choice is applied.
6. Any attached media has `rights_confirmed`, and any identifiable child has a parent's or guardian's permission (`people_ok`).
7. If `sensitive`, the senior reviewer's sign-off is recorded.

**Rules for the `ATTRIBUTED` outcome**
- Refused when `sensitive` is true (D10, stricter application).
- Setting it needs a confirmation by a named reviewer that the claim is not harmful, defamatory, seriously accusatory or otherwise unsuitable (`attributed_confirmed_by`).
- An `ATTRIBUTED` claim never appears in the Verified facts box.

**Not allowed**
- Nothing moves from `PENDING` straight to `PUBLIC`. `PUBLIC` is reachable only from `APPROVED` (T15).
- `REJECTED` and `WITHDRAWN` are final. A contributor tries again with a new submission, which may point to the earlier one through `related_submission_id`.

**Corrections do not change `status`.** A content correction creates a `CORRECTION_DRAFT` version, and swaps `live_version` when approved. The exception is a privacy or harm concern, which uses T16 first `[OPEN-M2]` (Q9).

## 7. Forms and validation

Full field lists, keys and limits are in the two specs. Requirements for the build:

- Validation runs on the server. The form gives clear, specific errors.
- **Story:** `story_title` up to 100 characters, `story_text` 100 to 2,000 words, `year_period` up to 40 characters with a "Not sure" option, `contributor_name` up to 80.
- **Vision:** `vision_headline` up to 100 characters, `vision_text` 30 to 500 words, `why_it_matters` 20 to 200 words, one category from the list.
- **Media:** images only, JPG or PNG, up to 3 per submission and 5 MB each. Type checked by content, not only by file extension. Location and device metadata removed on upload. Caption required. Rights confirmation required, and the people confirmation when people appear.
- **Required confirmations:** permission to publish, 18 or over, privacy notice read. The exact wording shown is stored as `consent_text_version`.
- `lga` from Member 5's official list plus "Outside Ekiti State". The list is editable data.
- Full Unicode support, including Yoruba letters and tone marks, everywhere (section 12).
- Preview step showing the credit line as the public will see it. Confirmation screen with the reference number, also sent as M01.
- Spam protection that does not collect more personal data than the field lists. If IP-based limits are used, IP addresses are not stored with the submission and are discarded quickly `[OPEN-M2]` (Q6).
- **Correction form** ("Suggest a correction"): needs no account and no contact details. Fields: the item, a description, optional evidence, optional contact.
- **Not collected:** date of birth, home address, ID numbers, precise location, age range.

## 8. Public output

Build one **public view** that includes only allowed fields. Public pages, search, share previews and feeds use it and nothing else.

| Shown | Never shown |
|---|---|
| Title or headline, label, credit line, LGA, language, period or category | Contact details, `contributor_name` (except as the credit line), `contributor_id` |
| The published version's text | Reviewer names, moderation and verification notes, claim notes |
| Approved media with caption and credit | Internal statuses, reason codes, consent records |
| Verified facts box (only claims with outcome `VERIFIED`, with their sources) | Anything from a non-live version |
| "Edited for clarity" note where edits went beyond spelling and grammar | Reporter contact details on corrections |
| Correction notes (Updated, Correction, Editor's note), dated | |
| Publication date, "Suggest a correction" link, standing statement | |

**Labels:** Citizen account (`PERSONAL_ACCOUNT`, and `MIXED` where claims are attributed), Citizen opinion, Citizen vision, and "Verified, with source" per claim `[OPEN-M2]` (with Member 6).

**Credit line** is generated, never typed by a reviewer.

| `credit_choice` | Credit line |
|---|---|
| `FULL_NAME` | Shared by {name}, {LGA} |
| `FIRST_NAME` | Shared by {credit_first_name}, {LGA} |
| `ANONYMOUS` | Shared by an anonymous contributor, {LGA} |

For "Outside Ekiti State" the LGA reads "Outside Ekiti State". If `lga_display_override` is set, it replaces the LGA.

**Standing statements** (fixed text on every page)
- Story: "This is a personal account shared by a citizen. It is not automatically verified history. Facts marked Verified have been checked against a source."
- Vision: "This is a personal vision shared by a citizen. It is not government policy or a commitment, and it is not endorsed by EKITI@30 DIGITAL."

**Unpublishing (T16)** must take the item out of pages, the search index, share previews and any cache, immediately.

**Ask Ekiti.** Citizen content is not available to it. No feed or API exposes unverified citizen content to the knowledge base `[OPEN-M3]`.

## 9. Notifications

Wording is in `workflow/MESSAGE_TEMPLATES.md`.

| Trigger | Message |
|---|---|
| T1 | M01 Received (immediate, automatic) |
| T4, T9, T11 | M02 Clarification, M03 Evidence request, M04 Privacy detail, M06 Edits confirmation, M10 Claims cannot be supported |
| Day 14 of a pending reply | M05 Reminder (automatic) |
| T10 | M07 Approved |
| T15 | M08 Published |
| T5, T12 | M09 Not published, M11 Under 18, M12 Duplicate |
| T14 (day 30) | M13 Closed, no reply (automatic) |
| T16 | M14 Temporarily removed |
| Correction received, applied, declined | M15, M16, M17 |
| T19 after publication | M18 Removal confirmed |
| Credit change after publication | M19 |
| Second review finished | M20 |

**Rules**
- Choose the template by the submission's `language`. If no Yoruba version exists, **hold the message** for a person. Never send it silently in English (D13).
- **Block sending while any `{{placeholder}}` is unresolved,** and tell the moderator. A visible placeholder must never reach a contributor.
- Show a preview. Moderators may edit free-text fields. Changes to fixed wording need the Editor's approval.
- Send only to the contact on record, by the contributor's chosen method. No attachments, no story text, and only the title and reference number.
- Sender name: "The EKITI@30 DIGITAL team". No reviewer names.
- Nothing is sent for `SPAM`, `THREAT_OR_HARASSMENT` or `EXPLOITATIVE` `[OPEN-M1]`.
- Log every message in `message_log`.
- Phone and WhatsApp contributors are contacted by a person at launch, with a logged entry (Q7).

## 10. Reviewer dashboard

Builds on the field list in the earlier v1.0 draft.

**Queues:** Pending; In moderation; Needs classification; In verification; Editorial review; Needs revision; Approved, not published; Unpublished; Open corrections; Escalated; Sensitive.

**Filters:** type, language, LGA, classification, sensitive flag, assigned reviewer, days in stage.

**List columns:** Submission ID, type, language, LGA, title, status, classification, sensitive flag, verification, editorial, assigned reviewer, escalated to, days in stage with a colour for approaching or missed targets, credit choice (never the name).

**Submission page**
- Content and version history with differences. Links in text are shown as plain text, never clickable, so staff do not open unknown links (moderation check 4).
- Media, claims panel, editorial checklist.
- **Only the actions valid for the current status and the user's role** are offered.
- Reason-code dropdown, message preview.
- **"Show identity"** button. It writes to the identity-access log with a reason.
- Suggestions for possible duplicates.

**Targets** (`workflow/CONTRIBUTION_WORKFLOW.md` section 10), tracked in Africa/Lagos time, with working days Monday to Friday excluding public holidays `[OPEN-M2]`: moderation decision 3 working days; verification 7 working days with a reminder on day 5 and escalation to Member 1; reply to a revision request 30 days with a reminder on day 14; privacy or harm concerns the same day.

**Verifier view:** only the assigned claims. It shows the claim text (with the marked working translation for Yoruba), context without identity, the source offered, and a form for the finding, sources and level. It never shows contributor name, contact, credit choice or other claims.

## 11. Audit, privacy and retention

**Audit.** Every status change, decision, claim outcome, message, credit change and correction writes an `audit_log` entry. The log is append only and holds no contact details. Every view of identity or contact writes an `identity_access_log` entry.

**Retention periods are approved as launch defaults** (D14): 90 days for rejected contact details; 12 months for rejected content, corrections and messages. Provide one configurable setting per data type below, seeded with these approved values, so a period can still be adjusted later without a code change.

| Data type | Notes |
|---|---|
| Published content and credit line | Removed on request or when unpublished |
| Contact details, item is public | |
| Contact details, item rejected or withdrawn | |
| Rejected or withdrawn content and reason code | |
| Correction records and reporter contact | |
| Message log | |
| Media files | |
| Audit trail | Kept without contact details |

**Also required**
- A deletion job that applies the settings, and a way to delete one submission and its personal data on request.
- Deleted data also leaves backups on a stated schedule `[OPEN-M2]` (Q14).
- Contact details and identity are excluded from public output, exports, search indexes, share previews and verifier views.
- No profile of contributors is built across submissions.
- **Retention periods are set** (D14: 90 days / 12 months, approved by Member 1). `[OPEN-M1]` Final privacy notice wording still needs Member 1's sign-off before public launch.
- How the record of an under-age attempt is deleted is open (`workflow/MESSAGE_TEMPLATES.md` M11).

## 12. Non-functional requirements

- **Unicode end to end:** Yoruba letters and tone marks must survive storage, display, search, sorting, email, exports and print. Test with the character set in `TEST_SUBMISSIONS.md` (TS27).
- **Mobile first,** working on slow connections. No contributor account is needed.
- **Accessibility:** clear labels, readable contrast, keyboard use.
- **Security:** HTTPS, server-side permission checks, upload validation, rate limiting, protection against automated spam, malware scanning of uploads if available `[OPEN-M2]`.
- **Time:** display and timers in Africa/Lagos.
- **Configurable, not hard-coded:** timings, message templates, reference lists, retention, the Yoruba reviewer attribute.
- **Backups** with a defined restore test.

## 13. Acceptance criteria

Each criterion is checked by the scenarios in `workflow/TEST_SUBMISSIONS.md`.

| # | Requirement | Tests |
|---|---|---|
| AC-01 | Nothing reaches `PUBLIC` except from `APPROVED` | TS25 |
| AC-02 | Only the transitions in section 6 are possible | TS25 |
| AC-03 | T10 is refused unless every approval rule is met | TS02, TS04, TS06 |
| AC-04 | A sensitive item cannot be approved without the senior reviewer | TS06 |
| AC-05 | `ATTRIBUTED` follows the rules in section 6 | TS03, TS04, TS06 |
| AC-06 | Identity and contact never appear publicly, in exports, search, share previews or verifier views | TS02, TS24 |
| AC-07 | Anonymous credit line and the identifying-detail check work | TS07 |
| AC-08 | Unpublishing removes the item at once from pages, search and previews | TS19, TS20 |
| AC-09 | Every transition writes an audit entry | TS01 |
| AC-10 | Yoruba text and tone marks are stored and shown correctly | TS08, TS27 |
| AC-11 | Yoruba submissions go to a Yoruba-capable reviewer, and a missing Yoruba template holds the message | TS08, TS26 |
| AC-12 | A message with an unresolved placeholder cannot be sent | TS26 |
| AC-13 | Reminder at day 14 and closure at day 30 run on schedule | TS16 |
| AC-14 | Location metadata is removed from uploaded images | TS22 |
| AC-15 | A content correction does not change the lifecycle status | TS18 |
| AC-16 | An under-18 submission is refused with `UNDER_AGE` | TS09 |
| AC-17 | Form validation follows the field limits | TS09, TS22 |
| AC-18 | Retention settings exist, and deletion of a submission works | TS20 |
| AC-19 | Every view of identity is logged | TS24 |
| AC-20 | Labels, credit line and standing statements are correct | TS01, TS10 |

## 14. Questions for Engineering

Please answer or comment on each. Answers go into `DECISIONS.md`.

| # | Question |
|---|---|
| Q1 | What stack and hosting are planned, and where does this module sit in the application structure (Issue #2)? |
| Q2 | Are the three status fields and transitions T1 to T19 workable as written (D2)? |
| Q3 | Are the field keys and limits workable, including the D16 additions (D6, D16)? |
| Q4 | How should verifiers work at launch: a limited login with the verifier view, or emailed requests with a reply form? |
| Q5 | Is contributor status lookup by reference number possible at launch, or is it later? |
| Q6 | Which spam protection can avoid collecting extra personal data? |
| Q7 | Which email service? Who sends messages to phone and WhatsApp contributors at launch? |
| Q8 | Can uploads be content-checked, have metadata removed, and be malware-scanned? |
| Q9 | Is the `live_version` and `draft_version` approach workable for corrections? |
| Q10 | Can unpublishing clear pages, search and previews immediately? |
| Q11 | How will working-day timers and the public-holiday calendar be handled? |
| Q12 | For `FIRST_NAME` credit, may the preview ask "How should we write your first name?" and store `credit_first_name`? Guessing a first name from a full name is unreliable for Yoruba names. If yes, Member 8 will add it to D16. |
| Q13 | Can the LGA list be loaded from Member 5's dataset, so spelling matches the rest of the platform? |
| Q14 | On what schedule do deleted records leave backups? |
| Q15 | What is your estimate, and what order would you build in (section 2)? |

## 15. Open items and dependencies

| Item | Who decides |
|---|---|
| Privacy notice wording, contact address for removal requests (retention periods and launch gate already approved) | Member 1 |
| Whether messages are sent for spam, threats and exploitative content; campaign-material rule | Member 1 |
| Break-glass access rules and export with identity fields | Member 1 |
| Questions Q1 to Q14 | Member 2 (Engineering) |
| Official LGA list and place names | Member 5 |
| Public labels, visual design, standing statements | Member 6 |
| Boundary between citizen content and the knowledge base | Member 3 |
| Routing confirmation for claims (D11) | Members 4, 5, 7 |
| Work estimate and build order (section 2) | Member 2 (Engineering) |
