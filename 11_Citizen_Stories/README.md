# Citizen Stories — My Ekiti Story

Owner: **Member 8 — Community, Media & Verification Lead**
Related issue: **#8 — Design citizen stories and Ekiti 2056 contribution workflow**
Status: **Ready for review (v1.0)**

## Purpose

My Ekiti Story is the citizen contribution space for personal experiences, memories, community stories, historical accounts and photographs about Ekiti.

Citizen contributions are valuable community knowledge. They are always clearly distinguished from independently verified factual information.

## Core principle

**Community moderation ≠ fact verification ≠ editorial approval.**

These are three separate checks with separate records.

## Start here

1. `workflow/CONTRIBUTION_WORKFLOW.md`: the journey from submission to publication.
2. `MY_EKITI_STORY_SPEC.md` and `../12_Ekiti_2056/EKITI_2056_SPEC.md`: what contributors see and provide.
3. `workflow/DECISIONS.md`: what is confirmed and what is still open.
4. `workflow/ENGINEERING_HANDOFF.md` and `workflow/TEST_SUBMISSIONS.md`: how to build and test it.

Items still waiting for someone's decision are tagged `[OPEN-Mx]` in the files, where x is the member who decides. Find them with `grep -rn "OPEN-M" .`

## Contents

This folder holds the My Ekiti Story specification and the workflow documents shared by My Ekiti Story and Ekiti 2056. Vision-specific documents live in `12_Ekiti_2056/`.

| Path | Description | Status |
|---|---|---|
| `MY_EKITI_STORY_SPEC.md` | Submission process, form fields, media rules, consent wording, public presentation | Ready for review |
| `workflow/DECISIONS.md` | Decisions log: confirmed decisions and proposals awaiting confirmation | Ready for review |
| `workflow/CONTRIBUTION_WORKFLOW.md` | Stages, classification, state transitions, approval rules | Ready for review |
| `workflow/MODERATION_GUIDE.md` | Moderation checklist, reason codes, misleading content, language | Ready for review |
| `workflow/VERIFICATION_WORKFLOW.md` | Claim records, source hierarchy, routing to leads | Ready for review |
| `workflow/CREDIT_AND_ANONYMITY.md` | Contributor credit, anonymous submissions, protecting anonymity | Ready for review |
| `workflow/CORRECTIONS_AND_CLARIFICATIONS.md` | Clarification requests, corrections, removal requests | Ready for review |
| `workflow/COMMUNITY_ENGAGEMENT_PLAN.md` | Audiences, phases, channels, ambassadors, risks, metrics | Ready for review |
| `workflow/MESSAGE_TEMPLATES.md` | Contributor messages: received, clarification, approved, published, not published, corrections | Ready for review |
| `workflow/ENGINEERING_HANDOFF.md` | Build requirements for Engineering: roles, data model, transitions, public output, acceptance criteria | Ready for review |
| `workflow/TEST_SUBMISSIONS.md` | 27 test scenarios with fictional sample content, and a results log | Ready for review |

Further documents are added as each phase of Issue #8 is completed.
