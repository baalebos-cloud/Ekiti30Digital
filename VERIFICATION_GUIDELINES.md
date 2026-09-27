# Citizen Contribution Moderation & Implementation Guidelines
**Role:** Member 8 (Community, Media & Verification Lead)  
**Coverage:** My Ekiti Story & Ekiti 2056

## 1. Workflow Architecture & Lifecycle States
This guide operationalizes citizen submission processing. For the canonical status lifecycle, state machines, database schema, and endpoint definitions, refer directly to:
👉 `11_Citizen_Stories/workflow/CONTRIBUTION_WORKFLOW.md`

All incoming submissions adhere to the official transition lifecycle established in the core workflow documentation.

## 2. Moderation & Fact-Checking Standard Rules

### Stage 1: Safety & Privacy Screening
- **Content Safety:** Reject hate speech, harassment, spam, commercial advertisement, or illegal media.
- **Privacy Enforcement:** Redact or reject personal phone numbers, physical addresses, or personal identity numbers.
- **Geography Check:** Validate that the specified LGA corresponds strictly to one of the 16 official Ekiti LGAs.

### Stage 2: Fact Classification & Isolation
- **Personal Stories (My Ekiti Story):** Flag with `is_community_claim = true`. Treat stories as oral memory and personal accounts. **Strict Isolation:** Do not index or inject citizen personal accounts into the primary RAG Knowledge Base vector store.
- **Future Visions (Ekiti 2056):** Classify as opinion/vision submissions (`OPINION/VISION`). Fact-checking is not applied to future projections.
- **Historical Claims:** Cross-reference formal historical assertions against Level 1/Level 2 authoritative records before approving status transitions.

## 3. Escalation Matrix
When edge cases arise during moderation, escalate as follows:
- **Historical Disputes:** Escalate to Research & Timeline Lead (Member 4).
- **Cultural/Tourism Records:** Escalate to Culture & Tourism Lead (Member 7).
- **Yoruba Language & Cultural Context:** Escalate to **Member 1 — Faith Ogunlade** (Project Lead / Yoruba Reviewer) per Decision D13.
- **Technical/Schema Issues:** Escalate to Engineering Lead (Member 2).

## 4. UI/UX Media Dimension Standards (Member 6 Specification)
When verifying incoming community media assets, confirm they meet Member 6's layout standards prior to Cloudinary upload:
- **Community Story Photos:** 4:3 aspect ratio.
- **Contributor Portraits:** 1:1 aspect ratio (minimum 400×400px square).
