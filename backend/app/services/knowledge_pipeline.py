"""Verified manifest to pgvector and grounded Ask Ekiti retrieval."""
import csv
import hashlib
import re
import math
from datetime import date
from pathlib import Path

from sqlalchemy import select, text as sql_text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import Chunk, KnowledgeDocument, EMBEDDING_DIMENSIONS

DOMAINS = {"01_History", "02_LGAs", "03_Timeline", "04_Tourism", "05_Culture",
           "06_Education", "07_Health", "08_Agriculture", "09_Statistics"}
SOURCE_RE = re.compile(r"^- \[(S\d+)\] (SRC-\d+): (.+)$")
MARKER_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]\s*$")
URL_RE = re.compile(r"https?://[^\s)]+")

# Prefixes used in canonical Ask Ekiti document IDs. Removing these lets a
# query such as "What is Arinta Waterfall?" match the subject portion of
# "04-tourism-arinta-waterfall" without hard-coding individual entities.
DOC_ID_PREFIXES = {
    "history",
    "government",
    "lga",
    "lgas",
    "timeline",
    "tourism",
    "culture",
    "education",
    "health",
    "agriculture",
    "statistics",
}


def _normalized_phrase(value: str) -> str:
    """Normalize text for conservative document-subject matching."""
    return " ".join(
        re.findall(r"[a-z0-9]+", str(value).casefold())
    )


def _document_subject(doc_id: str) -> str:
    """Return the human-readable subject portion of a canonical document ID."""
    tokens = re.findall(r"[a-z0-9]+", str(doc_id).casefold())

    # Canonical IDs may begin with a numeric section, e.g. 04-tourism-...
    while tokens and tokens[0].isdigit():
        tokens.pop(0)

    # Remove one or more structural prefixes, but keep the actual subject.
    while tokens and tokens[0] in DOC_ID_PREFIXES:
        tokens.pop(0)

    return " ".join(tokens)


def _matching_doc_id(question: str, doc_ids) -> str | None:
    """Resolve an explicit named subject to one ingestible document.

    This is intentionally conservative. It only focuses retrieval when the
    subject encoded in a canonical document ID appears as a complete phrase
    in the user's question. Broad questions therefore remain multi-document.
    """
    normalized_question = _normalized_phrase(question)

    matches = []

    for doc_id in doc_ids:
        subject = _document_subject(doc_id)

        if not subject:
            continue

        pattern = r"\b" + re.escape(subject) + r"\b"

        if re.search(pattern, normalized_question):
            matches.append((len(subject.split()), len(subject), doc_id))

    if not matches:
        return None

    # Prefer the most specific/longest subject if IDs overlap.
    matches.sort(reverse=True)
    best = matches[0]

    equally_specific = [
        item
        for item in matches
        if item[:2] == best[:2]
    ]

    if len(equally_specific) != 1:
        return None

    return best[2]


def _retrieval_focus(question, eligible_ids, requested_doc_ids=None):
    """Focus broad vector search only when the planner did not specify docs.

    Explicit planner document constraints are authoritative. In particular,
    comparisons may intentionally request several documents and must not be
    collapsed to one subject merely because one name is more specific.
    """
    if requested_doc_ids:
        return None

    return _matching_doc_id(question, eligible_ids)


def _sections(body):
    sections = {}
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return sections


def verified_facts(text):
    """Only facts with resolvable local citation markers may enter the index."""
    sections = _sections(text.split("---", 2)[-1] if text.startswith("---") else text)
    sources = {}
    for line in sections.get("Sources", []):
        match = SOURCE_RE.match(line.strip())
        if match:
            url = URL_RE.search(match[3])
            if not url:
                raise ValueError("source line has no URL")
            sources[match[1]] = (match[2], match[3].split(". ")[0], url[0].rstrip(".,"))
    facts = []
    for line in sections.get("Facts", []):
        if not line.strip().startswith("- "):
            continue
        claim = line.strip()[2:]
        marker = MARKER_RE.search(claim)
        if not marker:
            raise ValueError("fact missing [S#] citation")
        keys = [item.strip() for item in marker[1].split(",")]
        if any(key not in sources for key in keys):
            raise ValueError("fact cites an unresolved source")
        facts.append((claim[:marker.start()].strip(),
                      ";".join(sources[key][0] for key in keys),
                      ";".join(sources[key][1] for key in keys),
                      ";".join(sources[key][2] for key in keys)))
    if not facts:
        raise ValueError("document has no sourced facts")
    return facts


def _frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing document front matter")
    end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    if end is None:
        raise ValueError("missing document front matter")
    return {key.strip(): value.strip() for key, value in
            (line.split(":", 1) for line in lines[1:end]
             if ":" in line)}


def check_embedding_dimensions(db):
    """Fail before embedding if settings, ORM, or deployed schema disagree."""
    if settings.EMBEDDING_DIMENSIONS != EMBEDDING_DIMENSIONS:
        raise RuntimeError("embedding dimensions changed after model import; restart required")
    if db.bind.dialect.name == "postgresql":
        actual = db.scalar(sql_text("""
            SELECT format_type(atttypid, atttypmod)
            FROM pg_attribute
            WHERE attrelid = to_regclass('chunks')
              AND attname = 'embedding' AND NOT attisdropped
        """))
        if actual != f"vector({EMBEDDING_DIMENSIONS})":
            raise RuntimeError("database embedding dimension differs from settings; "
                               "apply an explicit migration and rebuild embeddings")


def _safe_file(root: Path, relative: str):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path.suffix.lower() != ".md":
        raise ValueError("unsafe or unsupported document path")
    if relative.split("/", 1)[0] not in DOMAINS:
        raise ValueError("non-content domain")
    return path


def ingest_manifest(manifest: Path, root: Path, db: Session, embed):
    """Embed and atomically replace citation-safe approved documents."""
    check_embedding_dimensions(db)
    result = {"ingested": 0, "unchanged": 0, "rejected": []}

    with manifest.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    counts = {}
    for row in rows:
        counts[row.get("id", "")] = counts.get(row.get("id", ""), 0) + 1

    for row in rows:
        if row.get("ingestible", "").lower() != "yes":
            continue

        doc_id = row.get("id", "")

        try:
            if not doc_id or counts[doc_id] != 1:
                raise ValueError("missing or duplicate document ID")

            status = row.get("status", "")
            approved = row.get("ask_ekiti_approved", "").lower() == "yes"

            if status not in ("verified", "needs_review"):
                raise ValueError("unsupported evidence status")

            if status != "verified" and not approved:
                raise ValueError("document is neither verified nor Ask Ekiti approved")

            if not row.get("source_tier"):
                raise ValueError("missing source tier")

            verified = None
            if row.get("last_verified"):
                verified = date.fromisoformat(row["last_verified"])
                if verified > date.today():
                    raise ValueError("verification date is in the future")

            if status == "verified" and verified is None:
                raise ValueError("verified document is missing last_verified")

            approval_date = None
            if approved:
                if not row.get("ask_ekiti_approved_by"):
                    raise ValueError("approved document is missing approver")
                if not row.get("ask_ekiti_approved_date"):
                    raise ValueError("approved document is missing approval date")

                approval_date = date.fromisoformat(
                    row["ask_ekiti_approved_date"]
                )

                if approval_date > date.today():
                    raise ValueError("Ask Ekiti approval date is in the future")

            file_path = _safe_file(root, row["path"])
            data = file_path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()

            if digest != row.get("file_sha256", ""):
                raise ValueError("SHA-256 mismatch")

            content = data.decode("utf-8")
            metadata = _frontmatter(content)

            if metadata.get("id") != doc_id:
                raise ValueError("manifest disagrees with document identity")

            if metadata.get("status") != status:
                raise ValueError("manifest disagrees with evidence status")

            metadata_approved = (
                metadata.get("ask_ekiti_approved", "").lower() == "true"
            )

            if metadata_approved != approved:
                raise ValueError("manifest disagrees with Ask Ekiti approval")

            if (
                metadata.get("source_tier") != row["source_tier"]
                or metadata.get("category") != row["category"]
            ):
                raise ValueError("manifest disagrees with document metadata")

            if status == "verified":
                if (
                    metadata.get("last_verified") != row["last_verified"]
                    or not metadata.get("verified_by")
                ):
                    raise ValueError(
                        "manifest disagrees with verification metadata"
                    )

            if approved:
                if (
                    metadata.get("ask_ekiti_approved_by")
                    != row["ask_ekiti_approved_by"]
                    or metadata.get("ask_ekiti_approved_date")
                    != row["ask_ekiti_approved_date"]
                ):
                    raise ValueError(
                        "manifest disagrees with Ask Ekiti approval metadata"
                    )

            declared_sources = set(
                re.findall(r"SRC-\d{3}", metadata.get("source_ids", ""))
            )

            manifest_sources = {
                value
                for value in row.get("source_ids", "").split(";")
                if value
            }

            if not declared_sources or declared_sources != manifest_sources:
                raise ValueError(
                    "manifest disagrees with declared source IDs"
                )

            facts = verified_facts(content)

            if any(
                not set(ids.split(";")).issubset(declared_sources)
                for _, ids, _, _ in facts
            ):
                raise ValueError(
                    "fact cites a source absent from the document registry list"
                )

            existing = db.scalar(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.doc_id == doc_id
                )
            )

            if (
                existing
                and existing.file_sha256 == digest
                and existing.chunks
                and existing.ingestible
                and existing.last_verified == verified
                and existing.evidence_status == status
                and existing.ask_ekiti_approved == approved
                and existing.ask_ekiti_approved_date == approval_date
            ):
                result["unchanged"] += 1
                continue

            vectors = embed([fact[0] for fact in facts])

            if (
                len(vectors) != len(facts)
                or any(
                    len(vector) != EMBEDDING_DIMENSIONS
                    for vector in vectors
                )
            ):
                raise ValueError("embedding count or dimension mismatch")

            if any(
                not all(math.isfinite(float(value)) for value in vector)
                for vector in vectors
            ):
                raise ValueError("embedding contains a non-finite value")

            if existing is None:
                existing = KnowledgeDocument(doc_id=doc_id)
                db.add(existing)

            existing.class_ = row["category"]
            existing.tier = row["source_tier"]
            existing.last_verified = verified
            existing.evidence_status = status
            existing.ask_ekiti_approved = approved
            existing.ask_ekiti_approved_by = (
                row.get("ask_ekiti_approved_by") or None
            )
            existing.ask_ekiti_approved_date = approval_date
            existing.ingestible = True
            existing.path = row["path"]
            existing.file_sha256 = digest
            existing.raw_content = content
            existing.source_title = (
                metadata.get("source_name", "").strip() or doc_id
            )
            existing.source_url = (
                metadata.get("source_url", "").strip() or None
            )

            existing.chunks.clear()

            for index, (
                (claim, ids, titles, urls),
                vector,
            ) in enumerate(zip(facts, vectors)):
                existing.chunks.append(
                    Chunk(
                        chunk_index=index,
                        content=claim,
                        source_ids=ids,
                        source_titles=titles,
                        source_urls=urls,
                        embedding=list(vector),
                    )
                )

            db.commit()
            result["ingested"] += 1

        except (ValueError, OSError, UnicodeError, KeyError) as exc:
            db.rollback()
            result["rejected"].append(
                {"doc_id": doc_id, "reason": str(exc)}
            )

    rejected_ids = {
        item["doc_id"]
        for item in result["rejected"]
    }

    active_ids = {
        row["id"]
        for row in rows
        if row.get("ingestible", "").lower() == "yes"
        and row.get("id") not in rejected_ids
    }

    for document in db.scalars(select(KnowledgeDocument)).all():
        if document.doc_id not in active_ids:
            document.ingestible = False

    db.commit()
    return result


def _embedding_model():
    """Load the local embedding model once per process."""
    if not hasattr(_embedding_model, "_model"):
        from sentence_transformers import SentenceTransformer
        _embedding_model._model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )
    return _embedding_model._model


def local_embed(texts):
    model = _embedding_model()
    return model.encode(texts).tolist()


def retrieve_vector(
    question: str,
    db: Session,
    embed=local_embed,
    limit=5,
    category=None,
    doc_ids=None,
    fact_kind=None,
):
    if db.bind.dialect.name != "postgresql":
        raise RuntimeError("Ask Ekiti vector search requires PostgreSQL with pgvector")

    # Generate the query embedding before the first database operation.
    # Loading the local transformer can take long enough for a hosted
    # PostgreSQL SSL connection to go stale if the connection is opened first.
    vector = embed([question])[0]

    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError("question embedding dimension mismatch")

    if not all(math.isfinite(float(value)) for value in vector):
        raise ValueError("question embedding contains a non-finite value")

    eligible = select(KnowledgeDocument.doc_id).where(
        KnowledgeDocument.ingestible.is_(True)
    )

    if category:
        eligible = eligible.where(KnowledgeDocument.class_ == category)

    if doc_ids:
        eligible = eligible.where(
            KnowledgeDocument.doc_id.in_(doc_ids)
        )

    if db.scalar(eligible.limit(1)) is None:
        return []

    check_embedding_dimensions(db)

    # For a question that explicitly names one indexed subject, constrain
    # semantic ranking to that document. Broad questions continue searching
    # across the eligible corpus.
    eligible_ids = list(db.scalars(eligible).all())
    focused_doc_id = _retrieval_focus(
        question,
        eligible_ids,
        requested_doc_ids=doc_ids,
    )

    distance = Chunk.embedding.cosine_distance(vector)
    query = (
        select(
            Chunk,
            KnowledgeDocument,
            distance.label("distance"),
        )
        .join(KnowledgeDocument)
        .where(
            KnowledgeDocument.ingestible.is_(True),
            Chunk.embedding.is_not(None),
        )
    )

    if category:
        query = query.where(
            KnowledgeDocument.class_ == category
        )

    if doc_ids:
        query = query.where(
            KnowledgeDocument.doc_id.in_(doc_ids)
        )

    # Planned fact kinds are structural constraints, not merely semantic
    # hints. Apply them before vector ranking so exact LGA/headquarters and
    # state-creation requests cannot be lost to unrelated nearest neighbours.
    if fact_kind == "identity":
        query = query.where(
            Chunk.content.op("~")(
                r"Local Government Area is one of the [0-9]+ "
                r"Local Government Areas of Ekiti State\."
            )
        )
    elif fact_kind == "headquarters":
        query = query.where(
            Chunk.content.like(
                "%Local Government Area's headquarters is %."
            )
        )
    elif fact_kind == "creation":
        query = query.where(
            Chunk.content.like("Ekiti State was created on %.")
        )
    elif fact_kind is not None:
        return []

    if focused_doc_id:
        query = query.where(
            KnowledgeDocument.doc_id == focused_doc_id
        )

    hits = db.execute(
        query.order_by(distance).limit(limit)
    ).all()
    return [{"doc_id": doc.doc_id, "content": chunk.content,
             "category": doc.class_, "source_ids": chunk.source_ids.split(";"),
             "source_titles": chunk.source_titles.split(";"),
             "source_urls": chunk.source_urls.split(";"),
             "source_url": doc.source_url, "tier": doc.tier,
             "last_verified": (
                 doc.last_verified.isoformat()
                 if doc.last_verified else None
             ),
             "evidence_status": doc.evidence_status,
             "ask_ekiti_approved": doc.ask_ekiti_approved,
             "ask_ekiti_approved_date": (
                 doc.ask_ekiti_approved_date.isoformat()
                 if doc.ask_ekiti_approved_date else None
             ),
             "path": doc.path,
             "distance": float(score)}
            for chunk, doc, score in hits
            if score is not None
            and (fact_kind is not None or score <= 0.65)]



def fuse_hybrid_hits(vector_hits, fulltext_hits, limit=5):
    """Fuse semantic and lexical evidence using reciprocal-rank fusion.

    A fact found by both retrieval methods receives more weight, while
    evidence unique to either method remains eligible. Results are
    deduplicated by document and exact cited fact.
    """
    limit = max(1, min(int(limit), 20))
    rrf_k = 60

    records = {}
    scores = {}
    channels = {}

    for channel, hits in (
        ("vector", vector_hits),
        ("fulltext", fulltext_hits),
    ):
        for rank, hit in enumerate(hits, start=1):
            key = (hit["doc_id"], hit["content"])

            if key not in records:
                records[key] = dict(hit)
                scores[key] = 0.0
                channels[key] = set()

            scores[key] += 1.0 / (rrf_k + rank)
            channels[key].add(channel)

            # Preserve channel-specific diagnostics when the same fact
            # appears in both result sets.
            for field in ("distance", "search_rank"):
                if field in hit:
                    records[key][field] = hit[field]

    ranked = []

    for key, hit in records.items():
        hit["hybrid_score"] = scores[key]
        hit["retrieval_sources"] = sorted(channels[key])
        ranked.append(hit)

    ranked.sort(
        key=lambda hit: (
            -hit["hybrid_score"],
            hit["doc_id"],
            hit["content"],
        )
    )

    return ranked[:limit]


def retrieve(
    question: str,
    db: Session,
    embed=local_embed,
    limit=5,
    category=None,
    doc_ids=None,
    fact_kind=None,
):
    """Retrieve grounded Ask Ekiti evidence using the configured strategy."""
    mode = settings.ASK_EKITI_RETRIEVAL_MODE

    if mode == "fulltext":
        from app.services.knowledge_fulltext import retrieve_fulltext

        return retrieve_fulltext(
            question,
            db,
            limit=limit,
            category=category,
            doc_ids=doc_ids,
            fact_kind=fact_kind,
        )

    if mode == "hybrid":
        from app.services.knowledge_fulltext import retrieve_fulltext

        final_limit = max(1, min(int(limit), 20))
        candidate_limit = min(20, max(final_limit * 3, final_limit))

        vector_hits = retrieve_vector(
            question,
            db,
            embed=embed,
            limit=candidate_limit,
            category=category,
            doc_ids=doc_ids,
            fact_kind=fact_kind,
        )

        fulltext_hits = retrieve_fulltext(
            question,
            db,
            limit=candidate_limit,
            category=category,
            doc_ids=doc_ids,
            fact_kind=fact_kind,
        )

        return fuse_hybrid_hits(
            vector_hits,
            fulltext_hits,
            limit=final_limit,
        )

    return retrieve_vector(
        question,
        db,
        embed=embed,
        limit=limit,
        category=category,
        doc_ids=doc_ids,
        fact_kind=fact_kind,
    )
