# Ask Ekiti: E-001 to E-050 implementation and remaining requirements

Base commit: 041e79f. Draft for review, not deployed.

## What this patch changes

- Adds a small deterministic query planner for state creation, LGA identities/counts and headquarters. Exact LGA document filters prevent West/South-West leakage.
- Handles paraphrases and source-request wording without embedding-model loading in fulltext mode.
- Returns per-statement numbered citations and marks missing parts of supported mixed questions.
- Adds scope, citizen-content, injection, language-selection and follow-up clarification messages.
- Preserves retrieved differing numeric/date statements and flags the difference rather than choosing one.
- Adds explicit date caveats on time-sensitive questions.
- Adds bounded Yoruba templates for the approved fact shapes and bilingual service messages. Source titles, URLs, proper names and numbers are preserved. These templates are DRAFT pending language-lead review.
- Adds frontend language selection, forwarding, a specific review-unavailable message, and citation numbers aligned with facts.
- Adds graceful empty/long-question backend messages. Requests over 10000 characters still receive schema validation; the frontend retains its 1000-character limit.

## Deployment after code and language review

Keep `ASK_EKITI_RETRIEVAL_MODE=fulltext` on Render. Deploy backend and frontend from the merged change. No schema migration or repeat ingestion is required for these code changes.

`ASK_EKITI_YORUBA_REVIEWED` defaults to false. The existing project language-review requirement remains in force. @smartexploit / the appointed Yoruba reviewer should review `backend/app/services/ask_language.py`, including all templates, month names and policy messages. Set the variable to true only after that review; then test English/Yoruba pairs through the frontend. This is bounded template translation, not a general Yoruba translator. Unknown fact shapes are not translated or silently returned in English.

## Honest completion boundary

The current approved corpus still has 17 documents / 29 facts. This patch does not mark research verified, create new factual claims, or make unsupported forecasts factual. Research approval and language approval are independent of frontend/backend permission to implement code. No workbook expectations were rewritten to manufacture passes.

The 50-case local replay uses actual PostgreSQL text-search SQL in PGlite against the approved repository facts, followed by the real answer composer. It is not a live Render run. It produces 13 factual responses (11 English and 2 Yoruba in the translation-enabled composition check); the other 37 are refusals, policy, clarification or input messages. This is NOT a 50/50 functional pass result. Yoruba is gated in the public route until review. Empty/retired/conflict fixtures and numerical reasoning cannot be scored solely from this populated-corpus replay.

The targeted planner covers current approved fact shapes. Future approved topics still use strict text search and may need their own retrieval and Yoruba translation extensions. It cannot provide universal paraphrase understanding, arbitrary numerical reasoning, or general multi-turn conversation. Follow-ups explicitly ask for clarification.

## Case-by-case review

| Case | Local result | Remaining requirement / interpretation |
|---|---|---|
| E-001 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-002 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-003 | insufficient: no_verified_match | Ado headquarters approval remains deferred because the official directory and draft differ. |
| E-004 | insufficient: no_verified_match | Verified officeholders, names and dated terms. |
| E-005 | insufficient: no_verified_match | Verified census figures, source dates, conflict/reconciliation decision. |
| E-006 | insufficient: no_verified_match | Verified first administrator name and approved name variants. |
| E-007 | answered: partial | Returns the verified date and marks creator identity unsupported. Does not accept the false 1991 premise. |
| E-008 | insufficient: no_verified_match | No invented prediction. A verified projection with assumptions would be required. |
| E-009 | insufficient: no_verified_match | Verified oil evidence; otherwise decline remains required. |
| E-010 | insufficient: no_verified_match | Verified EKSU history and dated leadership record. |
| E-011 | insufficient: no_verified_match | Verified governor record with date; no live assertion from stale evidence. |
| E-012 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-013 | insufficient: scope | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-014 | insufficient: injection | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-015 | insufficient: citizen | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-016 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. Yoruba template review and enablement required. |
| E-017 | insufficient: no_verified_match | Verified projection if one exists; otherwise Yoruba refusal is correct. Yoruba template review and enablement required. |
| E-018 | insufficient: no_verified_match | Verified population/conflict data plus reviewed Yoruba text. Yoruba template review and enablement required. |
| E-019 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. Yoruba template review and enablement required. |
| E-020 | insufficient: mixed | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-021 | insufficient: no_verified_match | Approved Ikogosi location fact. |
| E-022 | insufficient: no_verified_match | Verified geographic boundary/adjacency dataset. |
| E-023 | insufficient: no_verified_match | Verified LGA population, period and source. |
| E-024 | insufficient: no_verified_match | Approved tourism summary facts. |
| E-025 | insufficient: no_verified_match | Verified current opening hours and timestamp. |
| E-026 | insufficient: no_verified_match | Oral tradition classification and explicit permission for Tier D use; no promotion to historical fact. |
| E-027 | insufficient: no_verified_match | Verified institutions list. |
| E-028 | insufficient: no_verified_match | Verified dated operational status; avoid live certainty. |
| E-029 | insufficient: no_verified_match | Verified health-facility list for Ido/Osi. |
| E-030 | insufficient: no_verified_match | Verified agricultural products with statistics kept separate. |
| E-031 | insufficient: no_verified_match | Verified unemployment indicator, date and methodology. |
| E-032 | insufficient: no_verified_match | Approved LGA history, population and tourism facts. |
| E-033 | answered: partial | Ado HQ and population approval; Ikere HQ can be answered now. |
| E-034 | insufficient: injection | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-035 | insufficient: injection | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-036 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-037 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-038 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-039 | insufficient: no_verified_match | Verified census data and conflict handling; numeric comparison feature still needed for this phrasing. |
| E-040 | insufficient: no_verified_match | Isolated retired-only fixture; no production corpus mutation. |
| E-041 | insufficient: citizen | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-042 | insufficient: no_verified_match | Verified operational-count fact if permitted; do not read private submissions. |
| E-043 | insufficient: no_verified_match | Verified title-holder record and date. |
| E-044 | insufficient: clarify | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-045 | insufficient: clarify | Conflicting-source and conversational-context fixture; currently asks clarification. |
| E-046 | answered: supported | Implemented draft behaviour; confirm on deployed API and frontend. |
| E-047 | answered: partial | Verified first military administrator fact; creation date can be answered now. |
| E-048 | answered: supported | Separate empty-KB fixture. Populated-corpus replay instead checks exact Ekiti West identity. |
| E-049 | insufficient: empty | Backend gives explicit guidance; frontend validates locally. No question content is silently truncated. |
| E-050 | insufficient: long | Backend gives explicit guidance; frontend validates locally. No question content is silently truncated. |

## Approval queue

@smartexploit: prioritize officeholders and terms, census/population/conflict records, Ado HQ resolution, Ikogosi facts, institutions, health and agriculture. Approve only the specific claims supported by reviewed sources, then ingest that batch into the same Neon database.

@Aynerd2: review proxy/widget changes and validate deployed response shape, language selector, numbered citations, validation messages and latency. Existing clients remain compatible with `answered` / `insufficient`; `statements`, `coverage`, `missing` and `reason` are additive backend fields. Policy messages retain `insufficient` for compatibility.

AI/Data: expand retrieval rules and translations as each new factual shape is approved; test numeric comparisons against verified figures and explicit periods, run isolated fixture tests, then rerun all 50 cases and update expectations through review.

## Validation

See the accompanying regression tests. Networked PostgreSQL tests require a dedicated test database and were not run here. Live Render memory, UI interaction and final 50-case production results remain to be checked after deployment. This change contains no production database writes.

Validation for this draft: 499 backend tests passed, 7 optional networked PostgreSQL tests skipped, 2 dependency deprecation warnings. Next.js route types were generated; TypeScript and lint checks passed for the changed frontend files. PGlite executed the new SQL for the 50-case local replay against 17 approved documents / 29 facts. These checks do not constitute a browser interaction test or a live deployment evaluation.
