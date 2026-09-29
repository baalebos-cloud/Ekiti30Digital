# Ask Ekiti content readiness after PR #44

PR #44 is merged. This is a separate, unpushed content-readiness change based
on main `991ce41`. Earlier merge verification is not being reopened.

## Changes and limits

Canonical metadata keys were added to 63 legacy research records. Existing
research bodies and author verification labels are preserved. Missing canonical
approval status becomes `needs_review`. Ambiguous source tiers remain unresolved;
no source IDs, approval dates, reviewers, or factual evidence were invented.
Original noncanonical categories are retained as `research_category`.

| Working-tree validation | Before | After |
| --- | ---: | ---: |
| Parsed documents | 82 | 82 |
| Errors | 651 | 498 |
| Warnings | 104 | 247 |
| Canonically verified documents | 0 | 0 |
| Ingestible documents | 0 | 0 |

Warnings increased because filling missing identity/status fields allowed deeper
validation. This is a partial format repair, not a claim of content readiness.
The source registry still has 46 records and none has status `Verified`.
Some author metadata says `Verified`; those labels do not substitute for the
registry and document approval required by the ingestion gate.

`readiness_report.json` lists each document's errors, warnings, original approval
label, candidate URLs, and remaining actions. It includes 231 candidate URLs;
210 lack an exact registry URL match. These may include aliases, irrelevant links,
or duplicates of existing sources; they are not 210 automatically approved sources.
The inventory distinguishes support files from answer content, including gaps
notes with front matter. This classification does not change ingestion gates.

## Verification lead handoff

1. Review `documents` and `source_registration_queue` in the report. Confirm
   existing aliases before adding source IDs to the inventory workbook.
2. Decide which evidence supports each factual claim. Convert selected documents
   to the required Facts/citation structure, fill genuine source metadata and
   period coverage, and resolve conflicts. Do not infer a source from proximity.
3. Record source and document approvals through the existing review process.
   Research uploads and author labels alone must not promote content.
4. Regenerate the manifest and ingest only approved, passing documents. Check
   cited answers against that approved corpus before enabling generated answers.

The current normalizer deliberately skips unsupported front matter and support
files. Missing dates, source mappings, mixed tiers, historical period assertions,
and per-fact citations require evidence decisions before further conversion.

## Backend/frontend handoff

Use `ASK_EKITI_INTEGRATION.md` for the implemented request/response contract,
sample frontend call, insufficient-evidence response, and error handling.
The widget in this checkout still has a placeholder reply function. The gateway
contract and deployed API URL must come from the responsible owners. This
package prepares the handoff; it does not send messages or implement their UI.

## Evaluation

`evaluation_results.json` contains 50 explicitly blocked cases, not live results.
The connected endpoint URL was not supplied. The workbook is unchanged.
Run from the repository root once the owner supplies the full POST endpoint:

```bash
python 13_Knowledge_Base/tools/evaluate_ask_ekiti.py \
  --api-url 'https://YOUR-BACKEND/api/ask-ekiti' \
  --output 13_Knowledge_Base/evaluation_results.json
```

The runner records requests, actual HTTP status/body, workbook hash, and exact
expected-answer matches. A match is not a behavioural pass. Review citations,
answer relevance, language, multi-turn behaviour, and the connected widget
separately. E-016–019 use the draft Yoruba inputs, E-049 sends an empty string,
and E-050 is not truncated. Current 503/422 responses may differ from workbook
expectations; record those discrepancies rather than rewriting the results.
Forty expected answers are currently abstentions, so matching them does not
establish factual retrieval quality. Update expectations only through evidence
review when approved content becomes available.

## Reproduce checks

```bash
python 13_Knowledge_Base/tools/kb_normalize_metadata.py --selftest
python 13_Knowledge_Base/tools/kb_inventory.py --selftest
python 13_Knowledge_Base/tools/kb_validate.py --selftest
python -m unittest discover -s 13_Knowledge_Base/tools -p 'test_evaluate_ask_ekiti.py'
python 13_Knowledge_Base/tools/kb_readiness.py --today 2026-09-29
```

The normalizer defaults to a dry run. `--apply` makes the reviewed mechanical
changes; repeated application should produce no further edits. A full validator
run still fails on the remaining content issues listed above.
