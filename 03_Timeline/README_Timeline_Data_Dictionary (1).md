# EKITI@30 Timeline Dataset: Data Dictionary

File: `EKITI30_Timeline_Events_1996-2026.csv` (issue #4, Member 4 - Research & History)

Encoding: UTF-8, **no byte-order mark**, comma-separated, one header row, `\n` line endings. The content is plain ASCII, so it opens correctly in Excel and in code. Blank cells are written as `none`.

IDs (`EK-001` to `EK-050`) are stable. New rows get the next number; rows are sorted by date in the file, not by ID.

## Columns

| Column | Meaning |
|---|---|
| `id` | Stable identifier. |
| `date_display` | Human-readable date for the timeline page. May include a caution such as "day disputed". |
| `date_start` | ISO 8601: `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. Use for sorting and filtering. |
| `date_end` | Same format, for ranges (tenures, two-day elections). `none` for a single date. |
| `date_precision` | `day`, `month`, `year`, `range` or `approximate`. Says how exact `date_start` is. |
| `date_basis` | `confirmed`, `stated_by_source`, `inferred` (worked out from context, for example a weekday), `derived` (calculated from relative wording such as "last year"), `approximate` or `disputed`. May carry a short qualification in brackets, for example where sources give different days. Inferred, derived and disputed dates are never recorded at a finer precision than the evidence allows. |
| `event_title` | Short title. |
| `description` | The claim being made. Only details that the cited source supports are included. |
| `category` | Government, Education, Health, Infrastructure, Tourism, Technology, Agriculture, Sports, Culture or Other. |
| `evidence_type` | Type of evidence behind the core claim: `official_record` (tenure list, gazette, INEC), `official_statement` (government or institution announcing its own action), `institutional_statement`, `news_report`, `reference_work` (Wikipedia and similar), `traditional_account`. |
| `source` / `source_link` / `source_type` | The source that supports the core claim as written. `source_type` is Government website, Institutional website, News outlet, Reference (Wikipedia), Official gazette, International organisation or INEC record. |
| `verification_status` | See below. |
| `claim_source_map` | Which source supports which part of the description, where more than one source is used. |
| `unconfirmed_details` | Parts of the story that are not confirmed and are **left out of the description**. |
| `claims_and_disputes` | Claims by political actors, governments, media, or reported allegations and disputes, kept separate from confirmed facts. |
| `notes_limitations` | Other context, caveats and how conflicts were handled. |
| `additional_sources` | Other URLs, separated by ` \| `. |

## Verification status (rule used in this version)

| Status | Rule |
|---|---|
| **Verified** | Every element of `description` is supported by at least one official or institutional source, or by at least one credible news source cited in `claim_source_map`. Election results and laws need an official source (INEC record, gazette, official text) to be Verified. |
| **Single source** | One credible source supports the claim as written and no second source or primary record has been found. **Treated as not yet verified: publish only as reported, attributed to the source** ("according to ..."). |
| **Needs primary source** | The claim rests on Wikipedia, a derivative or interested-party source, news reports of a result that has an official record, or a statistic whose report has not been read. A primary record is known to exist or should exist. |
| **Conflicting sources** | Credible sources disagree. No value is selected; the basis for each is documented and the date precision is reduced. |

Proposal for alignment with PR #9 (`VERIFIED`, `ATTRIBUTED`, `NEEDS_EVIDENCE`, `UNSUPPORTED_FALSE`): Verified maps to VERIFIED; Single source maps to ATTRIBUTED; Needs primary source and Conflicting sources map to NEEDS_EVIDENCE. This mapping depends on the definitions in VERIFICATION_WORKFLOW.md, which Members 1 and 8 should confirm.

## Conventions

- Nothing from a personal account is in this dataset. Personal and citizen accounts belong in the citizen-stories workflow (issue #8).
- Traditional history (for example the c. 1310 AD origin of Udiroko) appears only in `claims_and_disputes`, labelled as a traditional account.
- Money figures and forecasts published by governments are recorded as claims, not as verified facts.
