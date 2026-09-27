# Moderation Guide

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `DECISIONS.md` D1, D3, D8, D9, D13, D14; `CONTRIBUTION_WORKFLOW.md`. Unresolved items are tagged `[OPEN-Mx]`.

## 1. What moderation is, and is not

Moderation asks one question: **should this content be allowed into the review and publication process?**

It looks at safety and suitability. It does not decide whether facts are true (that is verification) and it does not polish the writing (that is editorial review).

Two consequences:
- A moderator does **not** reject a submission just because its facts cannot be verified. Unverified is normal for personal accounts.
- A moderator **does** act on content that is unsafe, abusive, private, off-topic or clearly misleading (section 5).

## 2. Moderation checklist

| # | Check | What to look for | Typical action |
|---|---|---|---|
| 1 | Hate and discrimination | Attacks on people for ethnicity, community, LGA, religion, gender, disability or similar | Reject. If one phrase can be removed without changing the contributor's point, request revision. |
| 2 | Abuse, harassment, threats | Insults, targeting of individuals, threats | Reject. Threats also follow section 6. |
| 3 | Spam and advertising | Promotions, repeated posting, irrelevant links | Reject |
| 4 | Malicious or unknown links | Unfamiliar links, download prompts | Reject or request removal. Never open unknown links on your main device. |
| 5 | Sexual or exploitative content | Sexual content, any content sexualising a minor, exploitation | Reject immediately and follow section 6 |
| 6 | Privacy | Other people's phone numbers, home addresses, ID numbers, private health or family details, identifiable photos of children | Request revision (remove the detail) or reject. If already published, set `UNPUBLISHED`. |
| 7 | Impersonation | Claims to be an official or public figure, or a submission using someone else's identity | Hold and confirm through the contact details before continuing |
| 8 | Copyright | Media or text the contributor does not own or cannot share | Request revision (confirm rights or replace) or reject |
| 9 | Off-topic | Not about Ekiti or not about the contribution type | Reject with a polite explanation |
| 10 | Duplicate | Same content already submitted | Link to the original and reject the duplicate |
| 11 | Insufficient information | Missing required fields, too short, unreadable, or written in a language other than English or Yoruba | Request revision |
| 12 | Harmful allegations | Alleges wrongdoing by an identifiable person or institution | Do not reject just for making an allegation. Set `sensitive = true`, refer it to Member 1 or the designated senior reviewer, and hold at moderation until direction is received. |
| 13 | Campaign material | Content mainly promoting a candidate or party — PROPOSED `[OPEN-M1]` | Reject. Respectful criticism or ideas about policy and development remain allowed. |
| 14 | Fabricated or misleading material | Invented history, or claims shown to be false | See section 5 |
| 15 | Contributor age | The submission shows the contributor is under 18 (D9: 18+ only at launch) | Do not publish. Decline politely, explain that under-18 contributions are not yet accepted, and use `UNDER_AGE`. |

## 3. Moderation decisions

| Decision | When to use it | Result |
|---|---|---|
| Accept | Nothing in the checklist blocks it | `IN_CLASSIFICATION` (T3) |
| Request revision | The problem is fixable without changing the point of the contribution | `NEEDS_REVISION` (T4) |
| Reject | The content itself is the problem, or no fix would help | `REJECTED` (T5) |
| Escalate | A specialist or senior decision is needed | Assignment only. Status does not change. |

Every decision needs a reason code from section 4. Use `OTHER` only with a written note.

## 4. Reason codes

| Code | Meaning | Revision usually offered? |
|---|---|---|
| `SPAM` | Spam, advertising or malicious links | No |
| `ABUSIVE_OR_HATEFUL` | Abuse, hate or discrimination | Only if a small part can be removed |
| `THREAT_OR_HARASSMENT` | Threats or harassment | No |
| `EXPLOITATIVE` | Sexual or exploitative content | No |
| `PRIVACY_CONCERN` | Exposes private information | Yes |
| `COPYRIGHT_ISSUE` | Rights not confirmed or content copied | Yes |
| `INSUFFICIENT_INFORMATION` | Missing, unclear, or in an unsupported language | Yes |
| `UNSUPPORTED_CLAIM` | A claim could not be supported | Yes |
| `MISLEADING` | Presents inaccurate or invented material as fact | Yes, if the contributor engages |
| `DUPLICATE` | Already submitted | No |
| `OFF_TOPIC` | Outside the platform's scope | No |
| `UNDER_AGE` | Contributor is under 18 and the platform is 18+ only at launch | No. Contributor can submit once under-18 contributions are accepted. |
| `CAMPAIGN_CONTENT` | Promotion of a candidate or party (PROPOSED) | No |
| `NO_RESPONSE` | No reply to a revision request within the window | Contributor may submit a new contribution |
| `OTHER` | Anything else, with a written note | Case by case |

## 5. Misleading or false submissions

**Unverified is not the same as misleading.** Most factual claims from citizens are simply unverified, and that is handled by the verification stage, not by rejection.

Treat a submission as misleading when the claim is shown to be false, is clearly invented as history, or is presented as established fact when the contributor themselves does not claim to know it.

Steps:
1. Flag the specific claim. Do not treat the whole submission as bad.
2. Ask the contributor for clarification, a source or additional context. Use neutral wording and do not accuse anyone of lying. People misremember and repeat what they were told.
3. If the contributor clarifies or provides support, route the claim for verification as normal.
4. If the claim stays unsupported, apply the approval rules. If it is harmful, defamatory, seriously accusatory or otherwise unsuitable, remove it or send the submission back for revision. Otherwise, where appropriate, it may stay as part of the contributor's clearly labelled account and never be shown as verified fact (never for sensitive claims), or it is removed with the contributor's agreement, or the submission is rejected.
5. A misleading claim is never published as verified.

Repeat problems: if a contributor repeatedly submits spam, abuse or invented material, record an internal flag. The decision to stop accepting their submissions is made by Member 8, with Member 1 informed.

## 6. Serious cases

| Situation | Immediate action | Escalate to |
|---|---|---|
| Threat of violence, or a person who may be in danger | Do not publish. Keep the record. | Member 1 the same day. Member 1 decides on contacting authorities. |
| Sexual content involving a minor | Do not publish or share further. Keep only what the record requires. | Member 1 the same day |
| Content suggesting a child is at risk of harm, including a child contributor who appears to be at risk | Do not publish | Member 1 the same day |
| Defamatory or seriously harmful allegation | Hold. Set `sensitive = true`. | Member 1 or the designated senior reviewer |
| Other people's private details published by mistake | Set `UNPUBLISHED` immediately | Member 1 informed |

## 7. Moderator conduct and records

- Apply the same standard to every submission, whatever the contributor's LGA, background, language or views.
- Political or personal disagreement with a submission is not a reason to reject it.
- Log every decision with a reason code. Decisions are auditable (`CONTRIBUTION_WORKFLOW.md` section 7).
- Contact details and anonymous identities are visible only to designated reviewers. Do not share them with verifiers, publishers or other team members unless needed.
- Some submissions may be distressing. Take breaks and pass difficult cases to Member 1 rather than handling them alone.

## 8. Language: English and Yoruba (D13)

- Both languages follow the same checklist, reason codes and statuses. There are no shortcuts for either.
- A Yoruba submission is moderated by a reviewer who reads Yoruba. Member 8 still coordinates and records the decision.
- Never reject or mark down a submission for dialect, spelling, missing tone marks, or a mix of Yoruba and English.
- Do not rely on machine translation alone to judge whether content is abusive, threatening or misleading. Tone and idiom can be lost. If unsure, ask a Yoruba reader.
- Other languages: request revision and ask for English or Yoruba (`INSUFFICIENT_INFORMATION`). PROPOSED.
- A Yoruba-capable reviewer takes part where language-specific review is required. The launch assignment is Faith Ogunlade (D13). The role stays assignable so a backup reviewer can be added the same way.

## 9. Ekiti 2056 specifics

- Check relevance, respect, clarity and that the category fits.
- Respectful criticism of policy or government performance is allowed. Defamatory statements about individuals are not.
- Proposals that require illegal action are not published.
- Campaign or party promotion is out of scope (check 13, PROPOSED).

## 10. Open items

| Item | Who decides |
|---|---|
| Campaign-material rule (check 13) | Member 1 |
| Who besides Member 8 acts as a moderator | Member 1 |
| Whether Member 1 designates another senior reviewer (Member 1 is the senior reviewer for the initial launch) | Member 1 |
