# Initial approved Ask Ekiti batch

Recorded on 2026-09-29 against repository base `2a685da`.

## Approval provenance

The contributor supplied a review message from GitHub reviewer `@smartexploit` approving `history-state-creation-1996`, sources `SRC-001` and `SRC-028`, and the 16 `lga-*` documents. The approval covers the creation date, LGA identities, and headquarters supported by SRC-028. It explicitly excludes coordinates, landmarks, institutions and other secondary claims. The date in the metadata is the date this relayed approval was recorded. No public review permalink was supplied. This record does not claim that an automated validator performed the review.

Source approval does not approve every claim that cites that source. Each document has been narrowed before recording its verified status. SRC-002 and every source other than SRC-001 and SRC-028 retain their previous status.

## Approved content prepared for ingestion

- `history-state-creation-1996`: 1 October 1996 creation date only, citing SRC-001.
- All 16 `02_LGAs/lga-*.md` documents: LGA identity, citing SRC-028.
- Twelve LGA documents additionally retain their headquarters fact. The four exceptions below contain identity facts only.
- Total: 17 documents, 29 individually cited facts and 2 verified source records.

The retained headquarters are Aiyekire (Ode-Ekiti), Efon (Efon-Alaaye), Ekiti East (Omuo-Ekiti), Ekiti South-West (Ilawe-Ekiti), Ekiti West (Aramoko-Ekiti), Emure (Emure-Ekiti), Ido/Osi (Ido-Ekiti), Ijero (Ijero-Ekiti), Ikere (Ikere-Ekiti), Ikole (Ikole-Ekiti), Irepodun/Ifelodun (Igede-Ekiti), and Oye (Oye-Ekiti). Existing canonical spellings are retained where the directory uses shortened town names.

## Four headquarters claims need clarification

The current [SRC-028 directory](https://www.ekitistate.gov.ng/about-ekiti/local-government), checked on 2026-09-29, lists the following CAPITAL values. They do not explicitly establish the existing town wording. The existing claims are therefore deferred, rather than replaced by potentially ambiguous directory labels.

| Document | Existing headquarters claim, deferred | Current directory CAPITAL |
| --- | --- | --- |
| lga-ado-ekiti | Ado-Ekiti | ODO-ADO |
| lga-ilejemeje | Eda-Oniyo-Ekiti | ILEJEMEJE |
| lga-ise-orun | Ise-Ekiti | ISE/ORUN |
| lga-moba | Otun-Ekiti | MOBA |

Reviewer action: provide an approved precise source or explain the mapping for these four headquarters before reinstating them. Their LGA identity approval can proceed independently. This is not a claim that the old headquarters are false.

SRC-001 approval is recorded from the supplied reviewer decision. A fresh automated fetch of its archive URL failed during preparation, so this work does not claim an independent re-fetch of that article.

## Preserved research

All removed LGA fact lines and their original references are retained in [deferred claims](../15_Research_Notes/Ask_Ekiti_Deferred_LGA_Claims.md). That file is a draft outside the ingestion domains. Original CSV, JSON and GeoJSON research datasets are unchanged. No coordinates, landmarks or institution claims are present in the approved Facts sections.

The source workbook summary ranges now include all 46 existing source records, including SRC-028 at row 301. Other source approvals remain unchanged. The workbook's First Documents and Eval Starter Set sheets remain planning material; the current manifest and separate 50-question evaluation workbook are the operational records.

## Validation and remaining limits

The generated manifest and readiness report show 17 verified and 17 ingestible documents. The approved documents have no metadata errors. Repository-wide validation still reports 498 errors and 247 warnings in other research documents. A nonzero exit from that wider validation is expected and must not be described as a completely clean repository.

The KB validator self-test passes all 15 cases. The batch was also checked against the backend's actual fact parser to confirm its 29 source-resolved facts and against the previous documents to confirm that all excluded fact lines remain preserved. This is an offline content check, not PostgreSQL or live retrieval validation.

The existing 50-question evaluation workbook is unchanged. No live evaluation results have been invented or marked complete. Its expected answers must be reviewed against the now-approved scope before interpreting scores. Many topics still correctly require an insufficient-evidence response.

## Deployment and ingestion

Review this change in a new PR, then deploy the merged revision. Ingestion writes to the same Neon database used by Render. It does not upload files to Render and does not require Render Shell.

On the contributor's WSL machine, use the backend virtual environment and current dependencies. Set DATABASE_URL locally to the Neon connection string for the intended database, preserving its SSL parameters. Do not paste credentials into a PR or chat. The embedding settings must match Render and the deployed vector column. Current repository defaults use `paraphrase-multilingual-MiniLM-L12-v2` and 384 dimensions.

From the repository root after updating to the reviewed revision:

```bash
python3 13_Knowledge_Base/tools/kb_validate.py --selftest
python3 13_Knowledge_Base/tools/kb_validate.py
python3 13_Knowledge_Base/tools/kb_readiness.py
```

Inspect the report for exactly this approved batch. The second command also reports the unrelated errors described above. Do not bypass additional new errors in an approved document.

Then, using the backend environment:

```bash
cd backend
source .venv/bin/activate
read -r -s -p 'Neon DATABASE_URL: ' DATABASE_URL
echo
export DATABASE_URL
python scripts/ingest_knowledge.py
unset DATABASE_URL
```

The ingestion command modifies the selected database and may retire previously ingested documents that are no longer eligible. Check the target database and existing corpus with the backend owner before running it. A fresh empty corpus should load 17 documents and 29 facts. The first embedding run may download model weights. If a schema/dimension error occurs, ask the backend owner to confirm the current migration; do not change dimensions merely to suppress the check.

After successful ingestion, check the deployed Ask Ekiti endpoint/page for the creation date and supported headquarters, and confirm citations resolve to SRC-001 or SRC-028. Also check unsupported topics and the four deferred headquarters: identity evidence must not be mistaken for headquarters evidence. Record any irrelevant answers as retrieval failures. Run the 50-question evaluation against that same deployed version and save actual responses, citations and pass/fail decisions before claiming production readiness.
