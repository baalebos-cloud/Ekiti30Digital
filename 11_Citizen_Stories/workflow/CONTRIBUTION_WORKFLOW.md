# Contribution Workflow — My Ekiti Story and Ekiti 2056

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `DECISIONS.md` (D1–D5, D9–D11, D13). Items marked PROPOSED there stay proposals until confirmed. Unresolved items in this document are tagged `[OPEN-Mx]`, where x is the member who must decide.

## 1. Purpose

This document defines how a citizen contribution moves from submission to publication: who checks it, what is checked, and what can happen to it. It covers the Issue #8 tasks on content review, the approval/rejection process, and the distinction between personal stories and verified facts.

Related documents: `MODERATION_GUIDE.md`, `VERIFICATION_WORKFLOW.md`. Form fields are proposed in `DECISIONS.md` D6 and fully specified in Phase 3.

## 2. Core principle

**Community moderation ≠ fact verification ≠ editorial approval.**

| Check | Question it answers | Who | What it records |
|---|---|---|---|
| Moderation | Is this safe and suitable to enter review? | Member 8 or a designated moderator | Moderation decision and reason code |
| Verification | Is this factual claim supported by a reliable source? | The relevant research/content lead | Outcome per claim, source, source level |
| Editorial review | Is it clear, fairly attributed and not misleading? | Member 8 | Editorial decision and edits made |

Passing one check never replaces another. A story can pass moderation and still contain an unsupported claim. A verified claim can still sit in a story that fails editorial review because it exposes private information.

## 3. Personal account vs verified fact

| | Personal account | Verified fact |
|---|---|---|
| What it is | What the contributor experienced, saw, remembered or was told | A claim that can be checked against a record or reliable source |
| Example | "I attended this school as a child. I remember the old library beside the assembly hall." | "The school was established in 1978." |
| Evidence needed to publish | None, provided it is safe and presented as the contributor's account | A source at Level 1–3 (see `VERIFICATION_WORKFLOW.md`) |
| How it is shown | Labelled as a citizen account, credited per the contributor's choice | Marked verified, with the source shown |

Rules:
- A story can contain valuable information and still be labelled a citizen account. The label describes the status of the information, not its worth.
- A personal account does not automatically become established history. Only specific claims inside it can be verified.
- A factual claim that is not verified is never presented as verified.

## 4. Classification guide

Ask these questions in order. Record the result as `classification` (`DECISIONS.md` D3).

1. Does it describe what the contributor wants or proposes for Ekiti's future? → `VISION_PROPOSAL` (the default for all Ekiti 2056 submissions).
2. Does it describe something the contributor experienced, saw, remembered or was told? → `PERSONAL_ACCOUNT`.
3. Is it a belief, judgement or interpretation ("the best", "should have")? → `OPINION`.
4. Does it state something that could be checked as fact? → `FACTUAL_CLAIM`.
5. Does it combine more than one of the above? → `MIXED`.

**When in doubt, choose `MIXED` and route the claim.** A short check costs little. Publishing an unchecked claim as fact costs credibility.

A vision can rest on a factual premise (for example, a statement about how things are today). In that case classify it `MIXED` and route the premise.

**What counts as a checkable claim.** A statement is routed for verification when it gives a date, name, number or event; uses words like "first", "only" or "largest"; states a cause; or says something about a person, institution or place that a reader would take as established fact. Personal detail ("the library was beside the assembly hall", "it felt bigger then") is part of the account and is not routed.

**Sensitive flag.** Set `sensitive = true` when the submission alleges wrongdoing (crime, corruption, abuse, misconduct), or discloses health, family, religious or other private matters about an identifiable person or institution. The flag applies on top of any classification. It requires sign-off by Member 1 or a designated senior reviewer (D10).

## 5. The stages

| Stage | Status | Who | What happens | Outcomes |
|---|---|---|---|---|
| 0. Submission | `PENDING` | System | Form is validated: required fields, language, 18+ confirmation, permission to publish, credit choice, media-rights confirmation if media is attached. Submission ID and timestamp are assigned. Contributor receives a confirmation. | Goes to moderation |
| 1. Moderation | `IN_MODERATION` | Member 8 or designated moderator (a reviewer who reads Yoruba for Yoruba submissions) | Safety and suitability check (`MODERATION_GUIDE.md`). | Accept, request revision, or reject |
| 2. Classification | `IN_CLASSIFICATION` | Member 8 or designated moderator | Classify, set the sensitive flag, list checkable claims and routing. | To verification, or straight to editorial review |
| 3. Verification | `IN_VERIFICATION` | The relevant research/content leads | Each routed claim is checked (`VERIFICATION_WORKFLOW.md`). Skipped when there are no checkable claims. | Outcome recorded per claim |
| 4. Editorial review | `IN_EDITORIAL_REVIEW` | Member 8 (with a Yoruba reviewer for Yoruba submissions) | Editorial checklist below. | Approve, request revision, or reject |
| 5. Approval | `APPROVED` | Member 8. Also Member 1 or a designated senior reviewer if `sensitive = true`. | Approval rules in section 8. | Ready to publish |
| 6. Publication | `PUBLIC` | Member 8 | Content goes live with its public label and credit line. | Live |

**Editorial checklist**
- Accuracy: no unsupported factual claim is presented as fact.
- Clarity: a general reader can understand it.
- Attribution: it is clear whose experience or opinion this is.
- Context: edits do not create a misleading impression.
- Privacy: unnecessary private or sensitive information is removed.
- Language: spelling, grammar and readability are corrected.
- Meaning: the contributor's intended meaning is unchanged.

**Editing rule.** Light edits (spelling, grammar, formatting) may be made without asking. Anything that changes meaning, removes a claim or removes an identifying detail goes back to the contributor first. Editors never silently change a contributor's meaning.

**Language handling (D13).** Submissions may be in English or Yoruba. Both follow the same stages, checks and statuses, with no shortcuts. Member 8 coordinates the review, and a Yoruba-capable reviewer is involved where language-specific review is required, for example moderation and editing of a Yoruba submission. Verification requests carry the original wording and a clearly marked working translation. Editors respect Yoruba spelling and tone marks and never change meaning. Machine translation is a working aid only, never the sole basis for a decision. The launch Yoruba-capable reviewer is Faith Ogunlade. The role is implemented as an assignable attribute, so a backup reviewer can be added the same way if needed.

**Overview**

    Contributor
        |
    Submission form ------> PENDING
                               |
                          IN_MODERATION --(fixable)--> NEEDS_REVISION --(resubmits)--> IN_MODERATION
                               |
                               |--(cannot be fixed, incl. under 18)--> REJECTED
                               v
                        IN_CLASSIFICATION
                               |
              factual claim?---+--- no claim (story, opinion, vision)
                   |                          |
             IN_VERIFICATION                  |
                   |                          |
                   +-----------+--------------+
                               v
                      IN_EDITORIAL_REVIEW
                               |
              approve ---------+--------- revise ---> NEEDS_REVISION
                 |             |
             APPROVED       reject
                 |             |
               PUBLIC       REJECTED

**Ekiti 2056 path.** Visions normally skip stage 3. Review concentrates on safety, relevance, clarity, respect, correct category and suitability for publication. A vision is never treated as a historical fact.

## 6. State transitions

Statuses are defined in `DECISIONS.md` D2. This table is the complete list of allowed changes to the lifecycle `status`. Any change not listed is not allowed.

| # | From | To | Trigger | Who | Must be recorded |
|---|---|---|---|---|---|
| T1 | (new) | `PENDING` | Form submitted and validated | System | Submission ID, timestamp, type, language, contributor details, consent, 18+ confirmation, credit choice |
| T2 | `PENDING` | `IN_MODERATION` | Reviewer opens the submission | Moderator | Assigned reviewer |
| T3 | `IN_MODERATION` | `IN_CLASSIFICATION` | Passes moderation | Moderator | Moderation note |
| T4 | `IN_MODERATION` | `NEEDS_REVISION` | Fixable problem | Moderator | Reason code, message to contributor |
| T5 | `IN_MODERATION` | `REJECTED` | Rule violation that cannot be fixed, including `UNDER_AGE` | Moderator | Reason code |
| T6 | `IN_CLASSIFICATION` | `IN_VERIFICATION` | `FACTUAL_CLAIM` or `MIXED` with at least one routed claim | Moderator | Classification, claim records, `escalated_to` |
| T7 | `IN_CLASSIFICATION` | `IN_EDITORIAL_REVIEW` | `PERSONAL_ACCOUNT`, `OPINION` or `VISION_PROPOSAL` with no checkable claim | Moderator | Classification, `verification_status = NOT_REQUIRED` |
| T8 | `IN_VERIFICATION` | `IN_EDITORIAL_REVIEW` | Every claim has an outcome | Moderator | Claim outcomes |
| T9 | `IN_VERIFICATION` | `NEEDS_REVISION` | Contributor must supply evidence or clarification | Moderator | Claim records, message to contributor |
| T10 | `IN_EDITORIAL_REVIEW` | `APPROVED` | Editorial checklist passed and approval rules met (section 8) | Member 8. Also Member 1 or a designated senior reviewer if `sensitive = true`. | Approver(s), final edited version |
| T11 | `IN_EDITORIAL_REVIEW` | `NEEDS_REVISION` | Contributor must change or clarify something | Editor | Requested changes |
| T12 | `IN_EDITORIAL_REVIEW` | `REJECTED` | Not suitable for publication | Editor | Reason code |
| T13 | `NEEDS_REVISION` | `IN_MODERATION` | Contributor resubmits | System | New version stored, previous version kept |
| T14 | `NEEDS_REVISION` | `REJECTED` | No reply within the reply window (section 10) | Member 8 | Reason code `NO_RESPONSE` |
| T15 | `APPROVED` | `PUBLIC` | Published | Member 8 | Publish timestamp, public label |
| T16 | `PUBLIC` | `UNPUBLISHED` | Privacy or harm concern, or contributor asks for removal | Member 8 (immediately; inform Member 1) | Reason |
| T17 | `UNPUBLISHED` | `IN_EDITORIAL_REVIEW` | Concern is being resolved | Member 8 | Note on the concern |
| T18 | `UNPUBLISHED` | `REJECTED` | Concern cannot be resolved | Member 8 | Reason code |
| T19 | any of: `PENDING`, `IN_MODERATION`, `IN_CLASSIFICATION`, `IN_VERIFICATION`, `IN_EDITORIAL_REVIEW`, `NEEDS_REVISION`, `APPROVED`, `UNPUBLISHED` | `WITHDRAWN` | Contributor withdraws the submission | Moderator | Withdrawal request |

**Not allowed**
- Nothing moves from `PENDING` straight to `PUBLIC`.
- `PUBLIC` is only reachable from `APPROVED` (T15).
- `REJECTED` and `WITHDRAWN` are final. A contributor who wants to try again submits a new contribution, which may be linked to the earlier one through `related_submission_id`.

## 7. Rules for engineering

- A submission has exactly one lifecycle `status` at a time.
- Every transition writes an audit entry: `submission_id`, `from_status`, `to_status`, `actor`, `timestamp`, `reason_code`, `note`.
- Escalation is an assignment (`escalated_to`), not a status. The submission stays in its current stage while the specialist reviews it.
- Each resubmission is stored as a new version. Earlier versions are kept.
- On T13, the moderator can fast-pass unchanged content. Claim outcomes for unchanged claims carry over. Only new or changed claims are re-verified.
- T10 is blocked while any claim is `NOT_STARTED` or `NEEDS_EVIDENCE` without a recorded resolution (section 8).
- The `language` field (English or Yoruba) decides which reviewers can be assigned.
- Contact details and anonymous identities are visible only to designated reviewers, and never included in public output, exports, or messages to verifiers (D14).
- Retention periods are a configurable setting per data type, not fixed in code (D14).
- If a published item is set to `UNPUBLISHED`, it must disappear from public pages immediately.

## 8. Approval rules

A submission can move to `APPROVED` only when **all** of these are true:

1. Moderation accepted it.
2. Classification is recorded and the sensitive flag is set or cleared.
3. If it has checkable claims, the relevant lead has recorded a finding for **every** claim before publication, and none is left open (see the table below).
4. The editorial checklist is complete and no edit changed the contributor's meaning.
5. Permission to publish and the 18+ confirmation are on record, and the contributor's credit choice is applied.
6. Any attached media has confirmed rights, and any identifiable child in a photo has parent or guardian permission.
7. If `sensitive = true`, sign-off by the designated senior reviewer is recorded. For the initial launch, Member 1 is the designated senior reviewer, unless Member 1 explicitly designates another (D10).

**Approval paths (from D10)**

| Submission | Path |
|---|---|
| No checkable claims | Member 8 approves after moderation and editorial review |
| Contains factual claims | The relevant lead verifies every claim, then Member 8 approves |
| Sensitive allegation | As above, plus Member 1 or a designated senior reviewer signs off |

**Effect of claim outcomes on publication**

| Claim outcome | What it allows |
|---|---|
| `VERIFIED` | May be stated as fact, with the source shown. |
| `ATTRIBUTED` | Where the lead cannot verify a claim and it is appropriate to keep it, it may stay as part of the contributor's clearly labelled citizen account ("The contributor recalls..."), never presented as verified fact and never placed in the Verified facts box. Not allowed for claims that are harmful, defamatory, seriously accusatory or otherwise unsuitable for publication: those are removed or sent back for revision. Also not allowed for sensitive claims (a stricter application of D10, which Member 1 may relax). |
| `OPINION_VISION` | Published and labelled as opinion or vision. |
| `NEEDS_EVIDENCE` | Blocks approval. The contributor is asked for a source or clarification (T9). If none arrives, the reviewer decides: mark it `ATTRIBUTED` (only if low-harm and not sensitive), remove the claim with the contributor's agreement, or reject. |
| `UNSUPPORTED_FALSE` | Not published as stated. The contributor may revise or remove the claim. It may be rewritten as a clearly attributed recollection only with the contributor's agreement and only if that is not misleading. Otherwise reject. |

**Sensitive claims** are never published as attributed-only. They are either `VERIFIED` or removed, and senior sign-off decides.

**Rejection.** A reason code is always recorded. The internal record is kept, and how long is set by the retention policy (`DECISIONS.md` D14, period still open). The contributor receives a clear explanation and, where the problem is fixable, an invitation to revise. Message wording comes in Phase 4.

## 9. Public labels — PROPOSED `[OPEN-M2]` (needs Members 2 and 6)

| Label | Used for |
|---|---|
| Citizen account | `PERSONAL_ACCOUNT`, and `MIXED` where claims are attributed rather than verified |
| Citizen opinion | `OPINION` |
| Citizen vision | `VISION_PROPOSAL` (Ekiti 2056) |
| Verified, with source | Shown per claim, only where the outcome is `VERIFIED` |

Every public item also shows the credit line (`DECISIONS.md` D7), its language, and its publication date. A translation, if shown, is labelled as a translation.

## 10. Response times — PROPOSED, to be tuned after testing

| Step | Target |
|---|---|
| Acknowledgement to contributor | Immediately (automatic) |
| Moderation decision | 3 working days |
| Verification by a lead | 7 working days, with a reminder on day 5 and escalation to Member 1 if still open |
| Contributor reply to a revision request | 30 days, with a reminder at day 14, then T14 |
| Action on a privacy or harm concern about published content | Same day |

## 11. Related documents

- `DECISIONS.md` — decisions and open questions
- `MODERATION_GUIDE.md` — moderation checks, reason codes, misleading content
- `VERIFICATION_WORKFLOW.md` — claim records, source hierarchy, routing
