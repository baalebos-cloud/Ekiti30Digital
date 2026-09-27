# Verification Workflow

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `DECISIONS.md` D3, D4, D5, D10, D11, D13; `CONTRIBUTION_WORKFLOW.md`. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and scope

Verification decides whether a **factual claim** inside a submission is supported by a reliable source. It applies only to checkable claims. It is not applied to personal memories as such, to opinions, or to visions.

Member 8 **coordinates** verification: identifies claims, routes them, records results. Member 8 is not the final authority on every subject. The relevant lead makes the finding, and a claim must have that finding before the submission is published (D10).

Consistent with `CONTRIBUTING.md` sections 4, 5, 10 and 11.

## 2. Roles

| Role | Responsibility |
|---|---|
| Member 8 | Identify claims, create claim records, route them, record the outcome, keep the contributor informed |
| Member 4 — Research & History | History, governance, institutions, education, health, agriculture, statistics. Also decides disputed history. |
| Member 7 — Culture, Tourism & Content | Culture, tradition, festivals, tourism, heritage |
| Member 5 — Geospatial & LGA | Geography, LGA boundaries, headquarters, landmarks |
| Member 1 or designated senior reviewer | Sensitive claims and unresolved disputes |
| Member 3 — AI & Data | Downstream use of verified information in the knowledge base (section 9) |

Routing follows `DECISIONS.md` D11.

## 3. Steps

1. **Identify.** During classification, list each checkable claim (`CONTRIBUTION_WORKFLOW.md` section 4).
2. **Record.** Create one claim record per claim (section 5).
3. **Route.** Send each claim to the lead for its subject, using the message in section 11. Set `escalated_to`. The submission status becomes `IN_VERIFICATION`.
4. **Check.** The lead checks the claim against the source hierarchy (section 4) and reports a finding.
5. **Record the outcome.** Member 8 records the outcome (section 6) and the sources.
6. **Return if needed.** If evidence is missing, ask the contributor (T9).
7. **Continue.** When every claim has an outcome, the submission moves to editorial review (T8).

A story with several claims may have several outcomes. That is expected.

## 4. Source hierarchy

| Level | Type | Examples |
|---|---|---|
| 1 | Official sources | Government websites, official institutional records and publications |
| 2 | Recognised authoritative sources | NBS, educational institutions, museums, established archives, recognised organisations |
| 3 | Reputable secondary sources | Established publications, credible historical references |
| 4 | Community evidence | Interviews, photographs, documents, first-hand testimony |

Use the highest level available. Level 4 evidence is valuable, and is always attributed clearly. It is not automatically treated as independent verification.

**Rule (PROPOSED `[OPEN-M4]`):** `VERIFIED` needs at least one source at Levels 1–3. Level 4 evidence alone gives `ATTRIBUTED`, unless Member 4 documents in the claim note why corroborated testimony is sufficient.

## 5. Claim record

| Field | Description |
|---|---|
| `claim_id` | Unique ID, linked to the submission ID |
| `claim_text` | The claim exactly as written, in its original language |
| `claim_translation` | Working English translation, if the original is Yoruba, marked as a working translation |
| `subject_area` | History, culture, geography, etc. |
| `routed_to` | Lead the claim was sent to |
| `date_routed`, `date_resolved` | Dates |
| `finding` | Lead's finding (section 6) |
| `outcome` | Recorded outcome (section 6) |
| `sources` | Source title, publisher or holder, date, link or location |
| `source_level` | 1–4 for each source |
| `notes` | Limits, conflicts, context |
| `reviewer` | Who made the finding |

## 6. Findings and outcomes

Leads report one of three findings. Member 8 turns it into the recorded outcome.

| Lead's finding | Recorded outcome | Meaning |
|---|---|---|
| Supported by a reliable source | `VERIFIED` | Can be stated as fact, with the source shown |
| Contradicted by evidence | `UNSUPPORTED_FALSE` | Evidence contradicts it, or it cannot reasonably stand as presented |
| Not established either way | `NEEDS_EVIDENCE` | Potentially publishable, but supporting information is needed |

Two further outcomes are set by Member 8 rather than reported by leads:
- `ATTRIBUTED`: the claim stays in the submission as part of the contributor's clearly labelled citizen account, verification not established, and is never presented as verified fact. Allowed only under the approval rules in `CONTRIBUTION_WORKFLOW.md` section 8: not for claims that are harmful, defamatory, seriously accusatory or otherwise unsuitable for publication, and not for sensitive claims (`DECISIONS.md` D10).
- `OPINION_VISION`: not a factual claim.

What each outcome allows in publication is in `CONTRIBUTION_WORKFLOW.md` section 8.

## 7. Conflicting sources and disputed history

If sources disagree, record all of them in the claim note. Do not silently choose one (`CONTRIBUTING.md` section 11). Refer the claim to Member 4. Until resolved it is `NEEDS_EVIDENCE`, or `ATTRIBUTED` if the claim can be presented as the contributor's account without misleading readers and is not sensitive.

## 8. Privacy, anonymous contributors and language

- Verifiers receive the claim and the relevant context only. They do not receive the contributor's name or contact details. This keeps anonymous contributors protected (`DECISIONS.md` D8, D14) and keeps verification independent of who said it.
- For Yoruba submissions, the request carries the original wording and a working English translation, clearly marked as such. A lead who reads Yoruba checks the original. A working translation is never the basis for a finding on its own (D13).

## 9. Knowledge base and Ask Ekiti boundary — PROPOSED `[OPEN-M3]`

- Citizen submissions are not added to the knowledge base automatically.
- Only claims marked `VERIFIED`, with their sources, may be proposed to the knowledge base, through Member 4.
- If Ask Ekiti ever shows citizen content, it must show the citizen label from `CONTRIBUTION_WORKFLOW.md` section 9.

This protects the project principle that Ask Ekiti is grounded in reviewed sources.

## 10. Turnaround

Targets are in `CONTRIBUTION_WORKFLOW.md` section 10 (7 working days, reminder on day 5, escalation to Member 1). Member 8 tracks open claims.

## 11. Routing message template

> **Verification request — Submission [ID]**
> Type: [My Ekiti Story / Ekiti 2056] · Area: [history / culture / geography] · Language: [English / Yoruba]
> Claim (original wording): "[exact claim as written]"
> Working English translation, if Yoruba: "[translation]" (working translation only)
> Context: [one or two lines from the story, without the contributor's identity]
> Source offered by the contributor: [none / describe]
>
> Please reply with:
> 1. Finding: Supported / Contradicted / Not established
> 2. Source(s) used and source level (1–4)
> 3. Any note on conflicts or limits
>
> Reply by: [date]

## 12. Worked examples

**Example 1 — personal account, no verification.**
"I attended this school as a child. I remember the old library beside the assembly hall."
- Classification: `PERSONAL_ACCOUNT`. There is no checkable claim, since this is the contributor's own memory.
- `verification_status = NOT_REQUIRED`. Goes T7 to editorial review.
- Published as a citizen account.

**Example 2 — factual claim.**
"The school was established in 1978."
- Classification: `FACTUAL_CLAIM`. Route to Member 4.
- If an official or institutional record confirms it: `VERIFIED`, source shown.
- If records show a different year: `UNSUPPORTED_FALSE`. Ask the contributor to revise, or agree to present it as their recollection alongside the correct year.
- If nothing is found: `NEEDS_EVIDENCE`. Ask the contributor for a source (T9).

**Example 3 — mixed.**
"I remember the old market square before it was relocated. It was moved in 2004, and people said it was because of a dispute."
- Classification: `MIXED`.
- Claim 1: "moved in 2004" — checkable. Route by subject (Member 4 or Member 5).
- Claim 2: "people said it was because of a dispute" — a reported cause. Publish only as what the contributor heard, and set `sensitive = true` if it points at identifiable people or institutions.
- Possible result: claim 1 `VERIFIED`, claim 2 `ATTRIBUTED`. Published as a citizen account, with the date verified and the reason shown as hearsay. If claim 2 is sensitive, it is either verified or removed.

**Example 4 — Yoruba submission.**
A story in Yoruba gives the year a town's market was founded.
- Moderation and editorial review are done with a reviewer who reads Yoruba.
- Classification: `MIXED`. The year is routed to Member 4 with the original wording and a marked working translation.
- The lead checks the original wording against sources and reports a finding. The story is published in Yoruba. If an English translation is shown, it is labelled as a translation.
