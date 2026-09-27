# Contributor Message Templates

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `CONTRIBUTION_WORKFLOW.md`, `MODERATION_GUIDE.md`, `CORRECTIONS_AND_CLARIFICATIONS.md`, `CREDIT_AND_ANONYMITY.md`, `DECISIONS.md` D8, D9, D13, D14. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and scope

This document gives the wording for messages sent to contributors and to people who suggest corrections. It covers the Issue #8 tasks on approval, rejection, clarification and corrections. Templates are written in English. Yoruba versions come from the Yoruba-capable reviewer role (section 6).

## 2. Style rules

1. **Send in the language of the submission** (D13).
2. **Short and warm.** Plain words, usually under 150 words, one purpose per message.
3. **One clear ask,** as numbered, specific questions, with a reply-by date and what happens next.
4. **Never accuse.** Say "we couldn't confirm", not "you were wrong". People misremember and repeat what they were told.
5. **Never reveal internal information:** reviewer names, internal notes, verifier findings, the `sensitive` flag, or that Member 1 is reviewing. Say "needs additional review".
6. **Never include the full story.** Use the title and the reference number.
7. **Use only the contact on record,** by the method the contributor chose. Never a group, and never a forwarded copy.
8. **Anonymous contributors** get the same messages. Never mention their name in any public place, and never ask why they chose anonymity.
9. **Do not promise publication or fixed timelines,** beyond the stated targets.
10. **Do not state a retention period** until the retention policy exists (D14). Refer to the privacy notice.
11. **Do not reply to spam,** or to abusive or exploitative submissions `[OPEN-M1]`. Threats go to Member 1 (`MODERATION_GUIDE.md` section 6).
12. Sign as **"The EKITI@30 DIGITAL team"**, never a person's name, so reviewers are not exposed.

## 3. When each message is sent

| Message | Sent when | Related step |
|---|---|---|
| M01 Received | Right after submission | T1 |
| M02 Clarification | A fixable problem, or a question | T4, T9, T11 |
| M03 Evidence request | A factual claim needs support | T9 |
| M04 Privacy detail | A private detail must be removed or generalised | T4, T11 |
| M05 Reminder | Day 14 of a pending reply | `CONTRIBUTION_WORKFLOW.md` section 10 |
| M06 Edits confirmation | Edits beyond spelling and grammar | T11 |
| M07 Approved | The submission is approved | T10 |
| M08 Published | The submission goes live | T15 |
| M09 Not published | The submission is rejected | T5, T12 |
| M10 Not published, can revise | Claims could not be supported and a revision is possible | T12 |
| M11 Under 18 | Contributor is under 18 (D9) | T5 |
| M12 Duplicate | An identical submission already exists | T5 |
| M13 Closed, no reply | No reply by day 30 | T14 |
| M14 Temporarily removed | Item set to `UNPUBLISHED` | T16 |
| M15 Correction received | A correction request arrives | `CORRECTIONS_AND_CLARIFICATIONS.md` section 5 |
| M16 Correction applied | A correction is made | Section 5 |
| M17 Correction declined | A correction is not made | Section 5 |
| M18 Removal confirmed | Removal request handled | Section 7 |
| M19 Credit change confirmed | Credit or anonymity changed | `CREDIT_AND_ANONYMITY.md` section 9 |
| M20 Second review outcome | A second review is finished | `CORRECTIONS_AND_CLARIFICATIONS.md` section 8 |

## 4. Plain-language reasons for not publishing

Used in M09. Never include the internal reason code in the message.

| Reason code | Plain wording |
|---|---|
| `OFF_TOPIC` | It is not about Ekiti, or does not fit this section |
| `PRIVACY_CONCERN` | It includes personal details of other people that we cannot publish |
| `COPYRIGHT_ISSUE` | Some of the material may belong to someone else, and we could not confirm we can publish it |
| `INSUFFICIENT_INFORMATION` | It did not have enough information for us to review it, or was not in English or Yoruba |
| `ABUSIVE_OR_HATEFUL` | It does not meet our community guidelines |
| `CAMPAIGN_CONTENT` | Content that promotes a candidate or party is outside what this platform publishes |
| `MISLEADING`, `UNSUPPORTED_CLAIM` | Use M10 instead |
| `DUPLICATE` | Use M12 instead |
| `UNDER_AGE` | Use M11 instead |
| `NO_RESPONSE` | Use M13 instead |
| `OTHER` | A short plain reason written by the moderator, checked by a second person |

No message is sent for `SPAM`, `THREAT_OR_HARASSMENT` or `EXPLOITATIVE` `[OPEN-M1]`.

## 5. Templates

Placeholders in double curly braces are filled by the system or the moderator.

### M01 Received

> **Subject:** We received your contribution ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for sharing "{{title}}" with EKITI@30 DIGITAL. Your reference number is {{submission_id}}.
>
> Our team will review it and we aim to send you a first response within {{first_response_days}} working days. We may contact you if we need to check a detail. Nothing is published until it has been reviewed, and it will only appear credited the way you chose.
>
> To ask a question or withdraw your contribution, reply to this message and quote your reference number.
>
> The EKITI@30 DIGITAL team

### M02 Clarification request

> **Subject:** A quick question about your contribution ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for "{{title}}". Before we can continue, we would like to check:
>
> 1. {{question_1}}
> 2. {{question_2}}
>
> Please reply by {{reply_by_date}}. This is a check on a detail only. We are not asking you to change your story or your voice. If we do not hear from you, we will close the submission, and you are welcome to submit again at any time.
>
> The EKITI@30 DIGITAL team

### M03 Evidence request

> **Subject:** Could you help us check one detail? ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for "{{title}}". We would like to check one detail: "{{claim_short}}". We have not been able to confirm it yet.
>
> Could you tell us where this comes from? For example a document, a photograph, someone who was there, or your own memory. Any of these is fine.
>
> If it is your own memory, we may be able to publish it as your account, clearly labelled as such.
>
> Please reply by {{reply_by_date}}.
>
> The EKITI@30 DIGITAL team

### M04 Privacy detail

**Variant A: another person's details**

> **Subject:** A small change before we can publish ({{submission_id}})
>
> Hello {{first_name}},
>
> Your contribution "{{title}}" includes {{detail_type}} of another person (for example a phone number or home address). To protect people's privacy, we cannot publish this kind of detail.
>
> Would you like us to remove it, or would you prefer to send a new version? We have not changed anything yet. Please reply by {{reply_by_date}}.
>
> The EKITI@30 DIGITAL team

**Variant B: a detail that could identify an anonymous contributor**

> **Subject:** Protecting your privacy ({{submission_id}})
>
> Hello {{first_name}},
>
> You chose to be credited anonymously. Your contribution mentions {{detail}}, which could help someone work out who you are.
>
> Would you like us to remove it or make it more general? We will not change anything without your agreement. Please reply by {{reply_by_date}}.
>
> The EKITI@30 DIGITAL team

### M05 Reminder

> **Subject:** A gentle reminder ({{submission_id}})
>
> Hello {{first_name}},
>
> We are still waiting for your reply about "{{title}}". Please reply by {{reply_by_date}} so we can continue. If we do not hear from you, we will have to close the submission, and you are welcome to submit again at any time.
>
> The EKITI@30 DIGITAL team

### M06 Edits confirmation

> **Subject:** Please confirm our edits ({{submission_id}})
>
> Hello {{first_name}},
>
> Before publishing "{{title}}", we would like your agreement to these edits:
>
> 1. {{edit_1}}
> 2. {{edit_2}}
>
> These are to make it clearer to readers. They do not change what you meant. If you prefer the original wording, tell us and we will keep it. Please reply by {{reply_by_date}}.
>
> The EKITI@30 DIGITAL team

### M07 Approved

> **Subject:** Your contribution has been approved ({{submission_id}})
>
> Hello {{first_name}},
>
> Good news: "{{title}}" has been approved and will be published soon as a citizen account, credited as "{{credit_line}}". We will send you the link when it goes live.
>
> If you want to change how you are credited, tell us before {{change_by_date}}.
>
> The EKITI@30 DIGITAL team

### M08 Published

> **Subject:** Your contribution is now live ({{submission_id}})
>
> Hello {{first_name}},
>
> "{{title}}" is now published: {{link}}
>
> It appears as a citizen account, credited as "{{credit_line}}". {{social_line}}
>
> If you spot a mistake or want a change, use "Suggest a correction" on the page, or reply to this message.
>
> Thank you for helping build a record of Ekiti.
>
> The EKITI@30 DIGITAL team

`{{social_line}}` is "As you agreed, we may also share it on our social media." only where `promote_on_social` is ticked, and is otherwise left out.

### M09 Not published

> **Subject:** About your contribution ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for sharing "{{title}}". After review, we are not able to publish it. The reason is that {{plain_reason}}.
>
> {{revision_line}}
>
> We are sorry to disappoint you, and we appreciate your interest in EKITI@30 DIGITAL.
>
> The EKITI@30 DIGITAL team

`{{plain_reason}}` comes from the table in section 4. `{{revision_line}}` is "You are welcome to send a new version that fixes this." where a revision is possible, and is otherwise left out.

### M10 Not published, can revise (claims)

> **Subject:** About your contribution ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for your contribution. We could not publish it in its current form because some of the claims in it need supporting sources.
>
> You can send a new version with more information or references, or leave those claims out. If you would like to describe it as what you remember or were told, you can do that too. Please reply by {{reply_by_date}}.
>
> The EKITI@30 DIGITAL team

### M11 Under 18

> **Subject:** Thank you for your interest ({{submission_id}})
>
> Hello,
>
> Thank you for wanting to share your story with EKITI@30 DIGITAL. At the moment, we can only accept contributions from people aged 18 or over, so we are not able to publish this one.
>
> We hope to include younger contributors in the future. Please do not send any more personal information. Your contribution will not be published.
>
> The EKITI@30 DIGITAL team

Use no name and no details from the contribution. `[OPEN-M1]` Member 1 to confirm how the record of an under-age submission is deleted (D14).

### M12 Duplicate

> **Subject:** We already have this contribution ({{submission_id}})
>
> Hello {{first_name}},
>
> We already have this contribution as {{original_id}}, so we have kept the original and there is nothing more for you to do. You are welcome to send us a different story or vision at any time.
>
> The EKITI@30 DIGITAL team

### M13 Closed, no reply

> **Subject:** We have closed your submission ({{submission_id}})
>
> Hello {{first_name}},
>
> We did not hear back about "{{title}}", so we have closed the submission. You are welcome to submit it again at any time, with the information we asked for.
>
> The EKITI@30 DIGITAL team

### M14 Temporarily removed

> **Subject:** "{{title}}" is temporarily off our site ({{submission_id}})
>
> Hello {{first_name}},
>
> We have taken "{{title}}" off public view while we look at a concern about {{plain_concern}}. This is a precaution.
>
> We will be in touch by {{update_by_date}}. If you have questions in the meantime, reply to this message.
>
> The EKITI@30 DIGITAL team

Never say who raised the concern.

### M15 Correction received

> **Subject:** We received your suggestion ({{correction_id}})
>
> Hello,
>
> Thank you for your suggestion about "{{title}}". We will look at it, and we will let you know the outcome if you left contact details.
>
> The EKITI@30 DIGITAL team

### M16 Correction applied

> **Subject:** We have updated "{{title}}" ({{correction_id}})
>
> Hello,
>
> Thank you. We have updated "{{title}}": {{what_changed}}. The page shows a dated note explaining the change.
>
> The EKITI@30 DIGITAL team

### M17 Correction declined

> **Subject:** About your suggestion ({{correction_id}})
>
> Hello,
>
> Thank you for your suggestion about "{{title}}". We looked at it carefully and have left the page as it is, because {{plain_reason}}.
>
> A personal account is the contributor's own memory, and we do not rewrite it. Where reliable records give a different fact, we may add a clearly separate editor's note. If you have a document or source, you are welcome to send it to us.
>
> The EKITI@30 DIGITAL team

### M18 Removal confirmed

> **Subject:** Your contribution has been removed ({{submission_id}})
>
> Hello {{first_name}},
>
> As you asked, we have removed "{{title}}" from public view. Copies that other people have shared elsewhere, such as screenshots, are outside our control.
>
> We handle your personal information as described in our privacy notice: {{privacy_link}}.
>
> The EKITI@30 DIGITAL team

### M19 Credit change confirmed

> **Subject:** Your credit has been updated ({{submission_id}})
>
> Hello {{first_name}},
>
> As you asked, "{{title}}" is now credited as "{{new_credit_line}}". The change is live on the page.
>
> Copies that other people have shared elsewhere, such as screenshots, are outside our control. Posts we made on our own channels have been updated or removed.
>
> The EKITI@30 DIGITAL team

### M20 Second review outcome

> **Subject:** The result of the second review ({{submission_id}})
>
> Hello {{first_name}},
>
> Thank you for asking us to look again at "{{title}}". Someone who was not involved in the first decision has reviewed it. The result: {{outcome_line}}.
>
> {{next_step_line}}
>
> The EKITI@30 DIGITAL team

## 6. Yoruba versions

Member 1 confirmed that Yoruba submissions follow the same process, with a Yoruba-capable reviewer where language-specific review is required, and that no reviewer is hard-coded (D13). These templates therefore have **no Yoruba text yet**.

The Yoruba-capable reviewer role, once filled, should:
1. Translate every template, using Yoruba spelling with tone marks.
2. Keep the same meaning, warmth and structure, and adjust for natural Yoruba, not word for word.
3. Have a second Yoruba reader check it before use.
4. Agree the terms in the table below, and keep them the same everywhere.
5. Not rely on machine translation as the only basis (D13).

| Term | Where it must be used the same way |
|---|---|
| Submission, contribution | All messages |
| Citizen account (personal account) | M07, M08, M17 |
| Verified fact | Public labels, M17 |
| Credit line | M07, M08, M19 |
| Anonymous contributor | M04, credit lines |
| Reference number | All messages |
| Correction, editor's note | M15 to M17 |

The status of each template: M01 to M20 are all **Needed**.

## 7. Rules for engineering

- Templates are stored as versioned text files or database records with a `language` field. They are not written into the code.
- The system picks the template by the submission's `language`. If no Yoruba version exists, the message is held for a person to send. It is not silently sent in English.
- Messages are sent by the contributor's `contact_method`, to `contact_value` only.
- **Block sending if any `{{placeholder}}` is unresolved,** and tell the moderator. A message with a visible placeholder must never reach a contributor.
- Each message writes an audit entry: `submission_id`, template, `language`, `time`, `sent_by`. It does not store the story text.
- Messages contain no attachments and no story text.
- Moderators can see a preview and edit the free-text fields (`plain_reason`, `question_1`, and so on) before sending. Edits to fixed wording need Member 8's approval.
- Reminders (M05) and closures (M13) are sent on schedule by the system, using the response windows in `CONTRIBUTION_WORKFLOW.md` section 10.
- The message log is visible only to designated reviewers (D14).

## 8. Open items

| Item | Who decides |
|---|---|
| Whether no reply is sent to spam, abusive or exploitative submissions | Member 1 |
| How the record of an under-age submission is deleted | Member 1, with the retention policy |
| The privacy notice link and contact address for removal requests | Member 1 |
| Yoruba versions of all templates (reviewer confirmed: Faith Ogunlade) | Member 8 + Faith Ogunlade |
| Message delivery, sending and audit logging | Member 2 (Engineering) |
| Whether messages also go out by SMS or WhatsApp, and by whom | Member 2 + Member 1 |
