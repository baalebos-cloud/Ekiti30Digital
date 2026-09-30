# Ask Ekiti on a memory-limited Render service

## Why this change exists

Render reported the deployed instance exceeding 512 MB while loading the
sentence-transformers model. The process restarted and POST /api/ask-ekiti
returned 502. The approved corpus had already been ingested successfully:
17 documents and 29 cited facts. Repeating ingestion does not fix query-time
model loading.

## Activate after merging and deploying this code

Set this environment variable on the Render backend and deploy:

```text
ASK_EKITI_RETRIEVAL_MODE=fulltext
```

Keep DATABASE_URL pointing at the Neon database holding the approved corpus.
Keep the Vercel NEXT_PUBLIC_API_URL set to the backend's public address:
https://ekiti30digital-qgu3.onrender.com

No database migration, HF token, new provider account, or re-ingestion is
required for this search mode. Do not change EMBEDDING_DIMENSIONS. The vector
column and its existing data remain untouched. Ingestion still uses embeddings
and should run separately from the memory-limited web process.

The default remains `vector` for compatibility. Setting the variable without
deploying the new code will not activate this feature. To revert, set it to
`vector` and redeploy, but that restores the known model memory requirement.

## Behavior and limits

Fulltext mode searches the existing cited chunk text with PostgreSQL's English
text search. It requires all remaining query terms to occur in the same fact
after PostgreSQL's stemming and stop-word removal. LGA/LGAs is expanded to
Local Government Area. Question text and category are bound SQL parameters.

Only ingestible documents with non-future verification dates and nonempty
chunk source IDs, titles and URLs are returned. Citations and the existing
answer response shape are preserved. No match returns the existing insufficient
evidence response. No embedding model is imported or loaded by this path,
including when no results match. Raw research folders are never searched.

This is keyword retrieval, not equivalent semantic retrieval. Paraphrases,
multi-fact aggregation and loosely worded questions may return insufficient
evidence. Matching terms alone do not prove that a fact answers every aspect of
a question. Evaluate real responses and citation relevance before claiming
production readiness. Yoruba support is unchanged. No GIN index is needed for
the current 29-fact corpus; larger collections may need indexing later.

The change removes the observed query-time model allocation. It does not
guarantee the whole application fits 512 MB under arbitrary load or remove
free-service cold starts. Check actual Render memory and response latency.

## Checks after deployment

In /docs, execute POST /api/ask-ekiti with category null and language en:

- When was Ekiti State created? Expect the creation-date fact with SRC-001.
- What is the headquarters of Ikere LGA? Expect Ikere-Ekiti with SRC-028.
- What is the headquarters of Moba LGA? Expect insufficient evidence.
- What is Ekiti State population in 2026? Expect insufficient evidence.

Repeat supported queries and confirm no model-download warning, memory failure,
or process restart accompanies them. Then test through Vercel and run the
50-question evaluation, recording actual responses instead of assuming passes.

Tests: `python -m pytest -q tests/test_knowledge_fulltext.py`.
For the real PostgreSQL cases, set ASK_EKITI_TEST_DATABASE_URL to a dedicated
test database; those tests use temporary tables and roll back their fixtures.
Do not use the production database for test execution.

Reference: https://www.postgresql.org/docs/current/textsearch-controls.html

## Review validation (30 September 2026)

Base: main commit af59946. Backend suite: 385 passed, 7 skipped, 2
existing dependency deprecation warnings. The seven optional PostgreSQL tests
were skipped because no dedicated networked test database was configured.
The test environment deliberately omitted PyTorch and sentence-transformers.

Separately, the exact search SQL was exercised in PGlite (a PostgreSQL engine
compiled to WebAssembly): 37 checks passed against the repository's 17 approved
documents / 29 facts and exclusion fixtures. Checks included all 29 fact texts,
creation-date and Ikere-headquarters questions, category filtering, unsupported
questions, SQL-looking input, and draft/future-dated/uncited content exclusion.
An explicit category cast handles null parameters in prepared statements.

These are local validation results, not proof of deployed Neon connectivity,
Render memory usage, or completion of the 50-question live evaluation.
