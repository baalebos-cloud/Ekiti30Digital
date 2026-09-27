# Integration Notes for Member 4 --- 06_Education

## Package scope

This package contains: - 19 discrete timeline entries (`EK-EDU-001` to
`EK-EDU-019`); - 9 institution folders; - one policy-history file; - one
Annual School Census summary; - one gaps/follow-up file; - one manifest
fragment.

## Repository placement

Copy the extracted `06_Education/` folder to the repository root,
alongside `01_History/`, `02_LGAs/`, `03_Timeline/`, etc.

## Manifest handling

`kb_manifest_education_rows.csv` is a **fragment**. Do not replace the
repository's root `kb_manifest.csv`. Append these rows to the root
manifest after checking for duplicate `doc_id` values.

Expected column order:
`doc_id,source_title,source_url,class,tier,last_verified,ingestible`

## Ingestion rule

All rows are deliberately `ingestible: no`. Do not change them to `yes`
until: 1. Member 1 completes the required Yoruba review; and 2. Member 8
/ Verification Lead confirms evidence tiers/statuses.

## Political/public-office claims

Entries concerning governors' education policies are descriptive
historical records, not endorsements. Government self-reported
performance figures remain `ATTRIBUTED` where independent
budget/programme/audit evidence was not found.

## Recommended Git history

Use logical commits rather than one bulk upload commit: 1. education
timeline + policy + data; 2. institution records; 3.
gaps/README/integration notes; 4. append manifest rows.

## PR

Open the PR against `main`, reference Issue #4, and state clearly that
all education entries remain non-ingestible pending Yoruba review and
Verification Lead sign-off.
