# Ask Ekiti data pipeline

`kb_validate.py` generates `kb_manifest.csv` from document front matter. Only
rows with `status=verified` and `ingestible=yes` enter the backend. The current
manifest has no such rows; the API correctly returns insufficient evidence until
the verification team approves documents and regenerates the manifest.

As of the 28 September 2026 audit against the current `main` content, the
manifest contains 82 candidate documents across 01–09, including 16 LGA drafts.
Zero are verified or ingestible. The source inventory has 46 records and zero
with status `Verified`. The validator reports 651 errors and 104 warnings;
many research and metadata files are not KB documents and are not silently
promoted. A document can become ingestible only after its own review **and**
the review of every source it cites. The source inventory and verification lead
remain the authority for that approval.

Only content domains 01–09 are eligible. Citizen Stories and Ekiti 2056 are
excluded by the existing Ask Ekiti KB specification. Photographs, source documents,
research notes, media, design, and project documentation are supporting assets,
not direct answer text. `source_ids`, SHA-256, and per-fact `[S#]` markers are
required; a missing or unresolved marker rejects that document. Files cannot
escape the knowledge base root. Changed files replace their chunks; unchanged
hashes are skipped. No document is implicitly promoted from draft to verified.

The folder mapping follows the KB specification: `01_History` through
`09_Statistics` are canonical factual content; `10_Photographs` and `16_Media`
provide assets, `11_Citizen_Stories` and `12_Ekiti_2056` are contribution and
vision material, `13_Knowledge_Base` holds contracts and the manifest,
`14_Source_Documents` holds original sources and their registry, and
`15_Research_Notes`, `17_Design`, and `18_Project_Documentation` support
research, presentation, and decisions. The actual repository names are
`02_LGAs` and `10_Photographs`. This mapping connects content by source and
document IDs without copying draft or nonfactual files into the answer index.

Inspect validation from the repository root:

```sh
python 13_Knowledge_Base/tools/kb_validate.py --root . --no-manifest
```

The command exits nonzero while errors remain. After source and document
reviews, regenerate the manifest and run ingestion from the repository root:

```sh
python 13_Knowledge_Base/tools/kb_validate.py --root .
cd backend
alembic upgrade head
python scripts/ingest_knowledge.py
```

The manifest's `path` values are relative to the repository root. The script
opens them from that root, while reading the manifest in `13_Knowledge_Base`.
It does not promote source or document status on its own.

Use Postgres with pgvector and the configured 384-dimensional multilingual
MiniLM model. The first local embedding run downloads the model. `POST
/api/ask-ekiti` accepts `{ "question": "...", "category": "history" }`
(`category` optional), returns `answer`, `answer_status`, `language`, and
`citations`. Each citation includes document ID and per-fact source IDs and
titles and URLs. Retrieval filters verified documents and optionally category, orders
by cosine distance, and declines evidence beyond distance 0.65. Answers are
verbatim retrieved facts, not model-generated prose.

The LLM gateway's payload and authentication contract remain to be supplied
by its owner before generation can be connected. A future gateway request
should receive the question and only the selected fact text plus citations;
its output must be checked against those citations before it is shown.
