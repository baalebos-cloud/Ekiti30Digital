# Ask Ekiti integration handoff

This describes the API merged through PR #44. It is a sourced-facts endpoint;
the language-model gateway and the frontend page are separate integration work.
The current repository has no verified, ingestible KB documents, so a factual
answer cannot yet be demonstrated against the real corpus.
`GET /api/ask-ekiti` currently reports route availability, not corpus or
gateway readiness; do not use its `status: ready` value as a launch check.

## Backend and data handoff

1. Use PostgreSQL with the `vector` extension and apply `alembic upgrade head`.
   SQLite can run other API routes but Ask Ekiti retrieval returns HTTP 503.
2. The verification lead must approve source records in
   `14_Source_Documents/Ask_Ekiti_Source_Inventory.xlsx` and the relevant topic
   documents under `01_History` through `09_Statistics`. Do not turn a draft
   into `verified` as part of an automated import.
3. From the repository root, regenerate the manifest with
   `python 13_Knowledge_Base/tools/kb_validate.py --root .`. Resolve validation
   errors for the documents intended for ingestion. A row needs both
   `status=verified` and `ingestible=yes`, a verified source record, matching
   SHA-256, review metadata, and facts with resolvable `[S#]` citations.
4. From `backend/`, run `python scripts/ingest_knowledge.py`. The script reads
   `13_Knowledge_Base/kb_manifest.csv`; its document paths start at the
   repository root. It skips unchanged hashes and retires missing/ineligible
   documents. Do not connect the generation gateway until ingestion and cited
   retrieval have been checked on the deployment database.

## HTTP contract implemented today

`POST /api/ask-ekiti` with `Content-Type: application/json`:

```json
{"question":"When was Ekiti State created?","category":"history","language":"en"}
```

`question` is required and must have 3–1000 characters. `category` is an
optional exact category filter; omit it for general questions. `language`
defaults to `en`. An answer uses the retrieved verified fact text and its
source metadata. No language model generates the current answer.

When the verified corpus cannot support a question, the response is HTTP 200:

```json
{
  "answer": "The available verified knowledge isn't enough to answer that yet.",
  "answer_status": "insufficient",
  "language": "en",
  "citations": []
}
```

The following **test-fixture response** illustrates the shape of a sourced
answer. The example.org URL and fixture metadata are placeholders, not an
approved source or a claim that production has answered this question:

```json
{
  "answer": "Ekiti State was created in 1996.",
  "answer_status": "answered",
  "language": "en",
  "citations": [{
    "doc_id": "creation",
    "source_ids": ["SRC-001"],
    "source_titles": ["State announcement"],
    "source_urls": ["https://example.org/announcement"],
    "source_url": "https://example.org/announcement",
    "category": "history",
    "tier": "A",
    "last_verified": "2026-09-21",
    "path": "01_History/creation.md"
  }]
}
```

The arrays in each citation have matching positions: source ID, title, and
URL for the same source. Render each URL from the response; do not construct
citations from question text. A non-English request currently returns HTTP 503
with `detail: "Yoruba responses await human review"`. A short or missing
question returns HTTP 422. PostgreSQL/pgvector is required for search; a
non-PostgreSQL database returns HTTP 503.

The frontend can call the endpoint with the configured backend URL:

```ts
import { API_URL } from "@/lib/config";

type Citation = {
  doc_id: string;
  source_ids: string[];
  source_titles: string[];
  source_urls: string[];
  source_url: string | null;
  category: string;
  tier: string;
  last_verified: string;
  path: string;
};
type AskResult = {
  answer: string;
  answer_status: "answered" | "insufficient";
  language: "en";
  citations: Citation[];
};

export async function askEkiti(question: string): Promise<AskResult> {
  const response = await fetch(`${API_URL}/api/ask-ekiti`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language: "en" }),
  });
  if (!response.ok) throw new Error(`Ask Ekiti returned ${response.status}`);
  return (await response.json()) as AskResult;
}
// Display result.answer and, when present, result.citations[*].source_urls.
```

The frontend owns the input submission, loading/error states, and rendering
of source links. The backend/gateway owner still needs to agree on the LLM
payload and response contract, authenticate calls to the gateway, and validate
generated claims against the retrieved citations. The current route does not
call `ASK_EKITI_LLM_WEBHOOK_URL`.

## Approved-corpus acceptance demonstration

After approved content and PostgreSQL are available, run ingestion and make
a request about one approved document. Confirm that at least one document and
chunk were written, `answer_status` is `answered`, every displayed fact has a
matching document/source citation, and an unsupported question returns
`insufficient` with no citations. Also rerun ingestion to confirm unchanged
hashes are skipped. The unit suite exercises ingestion and the API response
shape with a fixture; it does not replace this live PostgreSQL check.

## Owner handoff and evaluation

The current `frontend/src/components/AskEkitiWidget.tsx` uses a local placeholder
reply function. The frontend owner should replace it with the request above,
show loading, 422/503/network errors, and render citations. The backend/gateway
owner should provide the deployed endpoint URL and agree the gateway contract;
configuration variables alone do not establish a working connection.

The contributor reports the earlier verification steps complete and PR #44
merged. This handoff does not replace that evidence or claim a new live run.
Use `CONTENT_READINESS.md` for this phase's approval queue and evaluation commands.
The handoff is prepared for owners; no owner notification is implied.
