# Contributor Credit and Anonymous Submissions

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `DECISIONS.md` D7, D8, D14, D16. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose

This document defines how contributors are credited, how anonymous submissions are handled, and how both are protected once a submission is published. It covers the Issue #8 tasks on contributor credit and anonymous handling.

Principle: **the contributor decides how they appear, and the platform keeps that promise.** Anonymity is a controlled option, never the default.

## 2. Credit options

The contributor chooses one option at submission. It is stored on the submission record.

| Option | Key | Public credit line |
|---|---|---|
| Full name + LGA | `FULL_NAME` | "Shared by Adaeze Ogunleye, Ikere" (example names) |
| First name + LGA | `FIRST_NAME` | "Shared by Adaeze, Ikere" |
| Anonymous | `ANONYMOUS` | "Shared by an anonymous contributor, Ikere" |

For contributors outside Ekiti, the LGA is replaced by "Outside Ekiti State" (D16).

## 3. How credit appears

- The credit line sits directly under the title, on every published item.
- The same credit line is used on the platform pages and on official social channels. Social sharing needs the contributor's separate permission (`promote_on_social`).
- The credit line never includes contact details, occupation or employer unless the contributor wrote it into the story and the reviewer has checked it.

## 4. Credit rules

1. The contributor's choice is applied exactly. Reviewers do not change a credit option without the contributor's agreement.
2. **Names are checked for impersonation.** If a name is that of a public figure or official, or the contact details do not fit the name, the moderator confirms through the contact channel before publication (moderation check 7).
3. **Names are shown as the contributor wrote them,** including spelling and diacritics. Yoruba names keep their tone marks.
4. Group or community contributions are credited to the person who submitted them, with any group named in the text only as the contributor wrote it.
5. Credit is applied at publication (T15) and cannot be left empty. If the credit choice is missing or unclear, the submission goes to `NEEDS_REVISION`.
6. The individual verifiers and reviewers are not credited on the item. Sources used for verification are shown, and reviewers are not (`workflow/VERIFICATION_WORKFLOW.md`).

## 5. Media credit

- Each image has a credit, which defaults to the contributor's credit line.
- If someone else took the photo, the contributor can name the photographer, provided the contributor confirms they have the right to share it.
- For an anonymous contributor, the media credit defaults to "Contributor". A photographer's name is shown only if the contributor asks for it and it does not reveal them.
- Archive or third-party images need the rights holder's permission (moderation check 8).

## 6. Transparency about edits

- Light edits (spelling, grammar, formatting) need no note.
- Edits that go further, such as shortening, restructuring or removing a detail with the contributor's agreement, get the note **"Edited for clarity"** on the public page.
- Editors never change meaning, and anything that might is agreed with the contributor first (`workflow/CONTRIBUTION_WORKFLOW.md` section 5).
- Editorial or verification notes are shown as separate notes, clearly marked as not written by the contributor (`workflow/CORRECTIONS_AND_CLARIFICATIONS.md` section 6).

## 7. Anonymous submissions

**When anonymity is appropriate.** Anonymity is available for any My Ekiti Story or Ekiti 2056 submission where the contributor asks for it. It suits stories about personal or family matters, and contributors who fear a negative reaction.

**When extra care is needed.**

| Case | Handling |
|---|---|
| The story alleges wrongdoing (`sensitive = true`) | An anonymous allegation is never published as attributed-only. It must be `VERIFIED` or removed, and needs sign-off from Member 1 or a designated senior reviewer (D10). |
| The story could identify the contributor even without a name | Section 8, text review |
| The contributor's photo shows their face or home | Section 8, media |
| The name is that of a public figure, or the submission may be impersonation | Confirm through the contact channel first. Anonymity is not a way around this check. |

**Anonymity is not a reason to reject** a submission, and it is not a reason for extra suspicion. Contributors are not asked to explain why they want it.

**What is kept.** The internal record keeps the name and contact details, for moderation, follow-up, verification coordination and removal requests (D8, D14).

## 8. Protecting anonymity

1. **Public record.** Shows only "an anonymous contributor" plus the LGA. If the LGA would identify the person (a very small community, or a distinctive story), the moderator offers to show "Ekiti State" instead, with the contributor's agreement.
2. **Text review.** Editorial review looks for details that could identify the contributor: names of close family, an unusual job, a specific address, or an event only they could know. The reviewer asks the contributor whether to remove or generalise them. Nothing is changed without agreement.
3. **Media.** Faces, house numbers, vehicles with plates, and location data are checked. Location metadata is always stripped (`MY_EKITI_STORY_SPEC.md` section 6). The contributor decides whether to replace or remove an image that could identify them.
4. **Access.** Name and contact details are visible only to designated reviewers (D14). Views of identity fields are logged.
5. **Verification.** Verifiers never receive identity or contact details (`workflow/VERIFICATION_WORKFLOW.md` section 8). Verification is about the claim, not the person.
6. **Sharing.** Identity is not discussed in group chats, and is not sent by messages that could be forwarded. Use the workflow tool or a direct message to the designated reviewer.
7. **Publishing channels.** Social posts use exactly the public credit line, never a name found in the internal record.

## 9. Changing credit or anonymity

| Request | When | Handling |
|---|---|---|
| Change credit before publication | Any time before `APPROVED` | Update the record and log it |
| Change credit after approval, before publication | Before T15 | Update the record, log it, and re-check the preview |
| Change credit to be **less identifying** after publication (for example, to anonymous) | After publication | Treated as a privacy request. Apply the change **the same day**, after confirming the request comes from the contributor's contact channel. |
| Change credit to be **more identifying** after publication | After publication | Apply after confirming the request and logging it |

If the contributor asks to become anonymous after publication, tell them plainly that copies already shared elsewhere, such as screenshots or social posts, cannot be recalled by us. Social posts made by the platform are updated or removed.

## 10. Requests to disclose identity

The platform never discloses an anonymous contributor's identity, or any contributor's contact details, on request from readers, media, other contributors or organisations.

Requests from authorities or other formal requests go to Member 1, who decides. `[OPEN-M1]` Member 1 to define this policy with any legal advice needed.

## 11. Rules for engineering

- `credit_choice` is required and cannot be empty at approval.
- The public credit line is generated from `credit_choice`, `contributor_name` and `lga`. It is not free text edited by reviewers.
- Identity and contact fields have restricted access by role, and each read is logged (`user`, `time`, `reason`).
- Public pages, exports, search indexes and social share previews use only the public credit line.
- A credit change after publication writes an audit entry and updates public pages immediately.
- Anonymous submissions are never included in exports that contain identity fields.

## 12. Open items

| Item | Who decides |
|---|---|
| Policy on formal requests for identity | Member 1 |
| Who counts as a designated reviewer with access to identity fields | Member 1 |
| Logging of identity-field access, and the access roles | Member 2 (Engineering) |
| Retention of identity and contact details after removal | Member 1, with the retention policy (D14) |
