# Issue #8 — Status, Acceptance Checklist and Follow-ups

Owner: Member 8 · Updated: 2026-09-23 · Target: final integration review, Wed 23 Sep 2026

## 1. Acceptance checklist (Issue #8's 13 tasks)

| # | Task | Drafted | Confirmed by team | Notes |
|---|---|---|---|---|
| 1 | My Ekiti Story submission process | Yes | Partial | Fields await Member 2 (D6, D16) |
| 2 | Ekiti 2056 submission process | Yes | Partial | Same as above |
| 3 | Information required from contributors | Yes | Partial | D6/D16 |
| 4 | Content review process | Yes | Yes | D1, D10 confirmed |
| 5 | Moderation process | Yes | Yes | |
| 6 | Approval/rejection process | Yes | Yes | D10 confirmed |
| 7 | Corrections/clarifications | Yes | Yes | Retention timing open (D14) |
| 8 | Contributor credit | Yes | Yes | D7 |
| 9 | Anonymous submissions | Yes | Yes | D8 |
| 10 | Inappropriate/misleading content | Yes | Yes | |
| 11 | Personal story vs verified fact | Yes | Yes | Core rule, confirmed |
| 12 | Community engagement plan | Yes | Partial | Launch date, wording await Member 1 |
| 13 | Verification workflow with leads | Yes | Partial | Routing (D11) awaits Members 4, 5, 7 |
| — | Implementable by Engineering | Yes | No | Awaiting Member 2 (section 2 below) |

**12 of 13 tasks drafted and internally consistent. Remaining gaps are external confirmations, not missing design work.**

## 2. Member 2 (Engineering) — accepted follow-up work

Tracked from `ENGINEERING_HANDOFF.md` section 14 and `DECISIONS.md` D2, D6, D16.

| Item | Asked | Status |
|---|---|---|
| D2: status model (3 fields, per-claim verification) | Yes | No reply by deadline. Accepted as follow-up work per Member 1's instruction; does not block launch or merge. |
| D6/D16: form fields and limits | Yes | Same as above. |
| Q1–Q15 in ENGINEERING_HANDOFF.md §14 (stack, verifier access, corrections model, estimate, etc.) | Yes | Same as above. |

**Resolved (2026-09-23):** Member 2 did not reply by the agreed deadline. Per Member 1's instruction, these items are recorded as accepted follow-up work rather than launch blockers, and PR #9 proceeds to review without them.

## 3. Privacy and retention — APPROVED by Member 1 (2026-09-23)

D14 retention periods are approved as launch defaults (see below), confirmed by Member 1 on 2026-09-23.

| Data | Approved period | Action after |
|---|---|---|
| Contact details, item public | While published | Deleted when unpublished/removed |
| Contact details, item rejected/withdrawn | 90 days | Deleted |
| Rejected/withdrawn content + reason code | 12 months | Deleted |
| Correction records + reporter contact | 12 months | Deleted |
| Message log | 12 months | Deleted |
| Media files (unapproved) | 90 days | Deleted |
| Audit trail (no contact details) | Indefinite | Reviewed annually |

**Privacy notice**: short-form text already drafted in `MY_EKITI_STORY_SPEC.md` section 7, pending Member 1's approval of exact wording.

**Status: approved.** These are now the confirmed launch defaults, recorded in `DECISIONS.md` D14.

## 4. Yoruba-capable reviewer role — CONFIRMED (2026-09-23)

Assigned to **Faith Ogunlade**. Active from launch, not a follow-up. Recorded in `DECISIONS.md` D13. Open: a backup reviewer.

## 5. Consistency

Last consistency sweep: 2026-09-22, `check_consistency.py`, 0 failures (after removing a false-positive check for "guardian_consent", which is legitimately referenced as *not existing* at launch).

All 12 documents are marked **READY FOR REVIEW (v1.0)**. Confirmed decisions (D1, D7–D10, D13 principle) are consistently reflected across `CONTRIBUTION_WORKFLOW.md`, `MODERATION_GUIDE.md`, `VERIFICATION_WORKFLOW.md`, `CREDIT_AND_ANONYMITY.md`, and `ENGINEERING_HANDOFF.md`.

## 6. Summary for Member 1

- PR #9 is open, not draft, not merged, per your instruction.
- 12 of 13 tasks are drafted and internally consistent.
- All three items you needed to decide are resolved: D13 — Yoruba reviewer is Faith Ogunlade, active from launch. D14 — retention is 90 days for rejected/withdrawn contact details, 12 months for rejected/withdrawn content, corrections and messages. Member 2's silence is recorded as accepted follow-up work, per your instruction.
- Everything else is external confirmation (Members 2, 4, 5, 7), tracked here and does not block merge.
