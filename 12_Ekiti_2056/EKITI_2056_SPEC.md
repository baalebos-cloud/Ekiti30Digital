# Ekiti 2056 — Submission Specification

Issue: #8 · Owner: Member 8 · Status: **READY FOR REVIEW (v1.0)**
Depends on: `11_Citizen_Stories/workflow/DECISIONS.md` (D6–D9, D13, D14, D16) and `11_Citizen_Stories/workflow/CONTRIBUTION_WORKFLOW.md`. Unresolved items are tagged `[OPEN-Mx]`.

## 1. Purpose and scope

Ekiti 2056 is where citizens share ideas, hopes, proposals and aspirations for the next 30 years of Ekiti.

A vision is not a historical fact and is never presented as one. Review concentrates on safety, relevance, clarity, respect, correct category and suitability for publication. Verification is not applied, unless the vision rests on a factual premise (section 7).

Moderation, statuses, credit, anonymity and corrections are shared with My Ekiti Story. See `11_Citizen_Stories/workflow/`.

## 2. Who can submit

- Anyone aged **18 or over**, from any LGA or outside Ekiti (D9). Under-18 contributions are not accepted at launch.
- In **English or Yoruba** (D13).

## 3. Contributor journey

1. **Landing page.** Explains Ekiti 2056, that visions are personal ideas and not government policy, and what happens to a submission. Links to the prompts in section 9.
2. **Form.** The fields in section 4.
3. **Preview.** The contributor sees how the vision would appear, including the credit line.
4. **Submit.** The system validates the form, assigns a Submission ID and sets the status to `PENDING` (T1).
5. **Confirmation screen** with the Submission ID and what happens next, also sent to the contact address or number.
6. **Follow-up** only when we need a clarification, when the vision is approved or published, or when it cannot be published. Wording comes in Phase 4.

Contributors see the same plain-language statuses as My Ekiti Story (`MY_EKITI_STORY_SPEC.md` section 8 in `11_Citizen_Stories/`).

## 4. Form fields

| Field | Key | Type | Required | Rules | Public |
|---|---|---|---|---|---|
| Language of submission | `language` | Choice: English / Yoruba | Yes | | Yes (label) |
| Name | `contributor_name` | Text, max 80 | Yes | Used according to the credit choice | Per credit choice |
| Contact method | `contact_method` | Choice: Email / Phone / WhatsApp | Yes | | Never |
| Contact | `contact_value` | Text | Yes | Valid email or phone number | Never |
| Location / LGA | `lga` | Choice | Yes | The 16 Ekiti LGAs plus "Outside Ekiti State" | Yes |
| Vision in one line | `vision_headline` | Text, max 100 | Yes | A short summary that becomes the heading (D16) | Yes |
| Vision / idea | `vision_text` | Long text | Yes | 30 to 500 words | Yes |
| Category | `category` | Choice | Yes | See section 5 | Yes |
| Why it matters | `why_it_matters` | Long text | Yes | 20 to 200 words | Yes |
| Photo / media | `media_files` | Image upload | No | Same rules as `MY_EKITI_STORY_SPEC.md` section 6 | Only if approved |
| Caption, media credit, rights and people confirmations | `media_caption`, `media_credit`, `media_rights_confirmed`, `media_people_ok` | As in My Ekiti Story | If media | | With the image |
| Permission to publish | `permission_to_publish` | Checkbox | Yes | Wording adapted from `MY_EKITI_STORY_SPEC.md` section 7 for a vision | No |
| Also share on EKITI@30 DIGITAL social media | `promote_on_social` | Checkbox | No | | No |
| Contributor credit | `credit_choice` | Choice | Yes | Full name + LGA / First name + LGA / Anonymous | Applied |
| I am 18 or over | `age_18_confirmed` | Checkbox | Yes | | No |
| I have read the privacy notice | `privacy_ack` | Checkbox | Yes | Same notice as My Ekiti Story | No |

**System fields** are the same as in My Ekiti Story, with `submission_type = EKITI_2056` and `classification` defaulting to `VISION_PROPOSAL`.

**Review Status.** The Issue's "Review Status" field is the system field `status`, together with `verification_status` and `editorial_status`. Reviewers set it and the contributor never does. Contributors see the plain-language version (`MY_EKITI_STORY_SPEC.md` section 8).

**Not collected:** age range, date of birth, home address, ID numbers, precise location. The optional age range in the v1.0 draft is removed (D6).

## 5. Categories — PROPOSED `[OPEN-M6]`

The contributor picks one. A reviewer may recategorise with a note.

| Category | Examples |
|---|---|
| Education | Schools, skills, libraries, lifelong learning |
| Health | Clinics, hospitals, prevention, mental health |
| Agriculture | Farming, processing, storage, markets |
| Technology & Innovation | Digital services, startups, research |
| Youth & Entrepreneurship | Jobs, small business, mentoring |
| Economy & Jobs | Industry, trade, investment |
| Infrastructure & Environment | Roads, water, power, waste, climate |
| Culture, Heritage & Tourism | Festivals, language, sites, museums |
| Governance & Community Development | Public services, community projects, civic life |
| Other | Anything else about Ekiti's future |

## 6. Validation and limits — PROPOSED, to be tuned after testing

- All required fields filled and all required checkboxes ticked.
- Vision 30 to 500 words. Why it matters 20 to 200 words. Headline at most 100 characters.
- Unicode fully supported (Yoruba letters and tone marks).
- A contributor may submit several visions, and each is a separate submission.
- Similar ideas from different people are welcome and are not rejected as duplicates. Only an identical copy of a submission already received is a duplicate (moderation check 10).

## 7. Review focus

Moderation (`MODERATION_GUIDE.md`, section 9 there) and editorial review of a vision look at:

| Check | Question |
|---|---|
| Safety | Is it free of abuse, threats, hate, spam and private information? |
| Relevance | Is it about Ekiti's future? |
| Respect | Is any criticism of policy or performance respectful, and free of defamatory statements about individuals? |
| Clarity | Can a general reader understand the idea and why it matters? |
| Category | Does the category fit? Recategorise with a note if not. |
| Suitability | Is it suitable for publication? |

**What is not grounds for rejection**
- The idea is ambitious, unusual or unlikely.
- The reviewer disagrees with it.
- It criticises government policy or performance respectfully.
- It has no source. A vision does not need one.

**What is not published:** proposals that require illegal action, and campaign or party promotion (moderation check 13, `[OPEN-M1]`).

**Factual premises.** If a vision rests on a claim about how things are today ("Ekiti has no…", "Only 10% of…"), classify it `MIXED` and route that claim for verification like any other. The vision itself is still not a fact.

**Sensitive content.** A vision that accuses named people or institutions is handled as `sensitive`, with sign-off by Member 1 or a designated senior reviewer (D10).

## 8. Public presentation

Each published vision shows:

- The headline and the label **Citizen vision**.
- The credit line (`Shared by …`) and the LGA.
- The category and the language of the submission.
- The vision and why it matters, as edited under the editing rule.
- Media with caption and credit, where approved.
- A **Verified facts** box, only when a factual premise was verified.
- A note "Edited for clarity" where edits went beyond spelling and grammar.
- The publication date, any correction notice, and a **Suggest a correction** link.

Standing statement on each page:

> This is a personal vision shared by a citizen. It is not government policy or a commitment, and it is not endorsed by EKITI@30 DIGITAL.

**Showcase.** Visions can be grouped by category on a collection page. Featuring a vision is an editorial choice and never implies endorsement.

## 9. Prompts for contributors

- In 2056, what should a child growing up in your community find there?
- What is one problem you want solved by 2056, and how?
- What should Ekiti be known for in 30 years?
- What should we protect from Ekiti's past, and what should we change?
- What could young people in Ekiti build by 2056?

**Do:** be specific ("a skills centre in every LGA" is easier to understand than "better education"), and say why it matters.
**Don't:** attack named people, promote a candidate or party, or include anyone's private details.

## 10. Open items

| Item | Who decides |
|---|---|
| The category list, and the wording of the standing statement (with Member 6) | Member 6 + Member 8 |
| Word limits, headline field, spam protection | Member 2 (Engineering) |
| Whether the campaign-material rule applies as drafted | Member 1 |
| LGA list source | Member 5 |
| Interface text in Yoruba | Member 1 + Member 8 |
