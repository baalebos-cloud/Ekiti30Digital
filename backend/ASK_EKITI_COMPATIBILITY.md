# Embedding dimensions and contributor line endings

`Settings.EMBEDDING_DIMENSIONS` is the single application default. The ORM
captures it when imported. Values must be positive. Restart application and
ingestion processes after configuration changes.

Ingestion checks settings against the ORM and, on PostgreSQL, the actual
`chunks.embedding` column before processing the manifest. Retrieval checks the
column before embedding a question against a nonempty corpus. A missing,
unconstrained, or differently sized column fails explicitly. Empty-corpus
retrieval continues returning insufficient evidence without loading the model.

Historical Alembic revisions retain their fixed dimension so migrations are
reproducible. Do not make an applied migration depend on the current environment.
No migration is needed for this refactor while the column and model remain 384.

Before changing the embedding model:

1. Confirm its output dimension; set the model and dimension together.
2. Prepare and review a new explicit migration if the dimension changes.
   Plan index rebuilding and replacement of existing vectors; do not cast old
   embeddings into the new dimension as if that preserved their meaning.
3. Re-embed all eligible documents even if source hashes are unchanged. This
   includes switching models with the same dimension: dimensions alone cannot
   establish embedding compatibility. The existing unchanged-hash shortcut is
   not a model-upgrade mechanism.
4. Restart services and validate ingestion and cited retrieval on PostgreSQL.

Front-matter parsing accepts LF, CRLF, and CR line endings and still requires
opening and closing delimiter lines. The SHA-256 gate uses original file bytes.
If checkout or editing changes line endings, regenerate the manifest for the
files used during ingestion; do not disable hash verification.

Regression tests cover explicit line endings through ingestion, malformed
headers, non-default dimensions in a fresh interpreter, invalid dimensions,
settings mutation, and mismatched database-column responses. Database-response
tests use a stub; live PostgreSQL validation remains a deployment check.
