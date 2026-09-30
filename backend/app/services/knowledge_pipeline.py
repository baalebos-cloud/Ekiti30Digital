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
    """Embed and atomically replace changed verified documents; report rejected rows."""
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
            if not doc_id or counts[doc_id] != 1 or row.get("status") != "verified":
                raise ValueError("unverified or duplicate document ID")
            if not row.get("last_verified") or not row.get("source_tier"):
                raise ValueError("missing verification metadata")
            verified = date.fromisoformat(row["last_verified"])
            if verified > date.today():
                raise ValueError("verification date is in the future")
            path = _safe_file(root, row["path"])
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest != row.get("file_sha256", ""):
                raise ValueError("SHA-256 mismatch")
            content = data.decode("utf-8")
            metadata = _frontmatter(content)
            if metadata.get("id") != doc_id or metadata.get("status") != "verified":
                raise ValueError("manifest disagrees with document identity or verification status")
            if (metadata.get("last_verified") != row["last_verified"] or
                    not metadata.get("verified_by") or
                    metadata.get("source_tier") != row["source_tier"] or
                    metadata.get("category") != row["category"]):
                raise ValueError("manifest disagrees with document verification metadata")
            declared_sources = set(re.findall(r"SRC-\d{3}", metadata.get("source_ids", "")))
            if not declared_sources or declared_sources != set(row.get("source_ids", "").split(";")):
                raise ValueError("manifest disagrees with declared source IDs")
            facts = verified_facts(content)
            if any(not set(ids.split(";")).issubset(declared_sources) for _, ids, _, _ in facts):
                raise ValueError("fact cites a source absent from the document registry list")
            existing = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.doc_id == doc_id))
            if (existing and existing.file_sha256 == digest and existing.chunks and
                    existing.ingestible and existing.last_verified == verified):
                result["unchanged"] += 1
                continue
            vectors = embed([fact[0] for fact in facts])
            if len(vectors) != len(facts) or any(len(v) != EMBEDDING_DIMENSIONS for v in vectors):
                raise ValueError("embedding count or dimension mismatch")
            if any(not all(math.isfinite(float(x)) for x in v) for v in vectors):
                raise ValueError("embedding contains a non-finite value")
            if existing is None:
                existing = KnowledgeDocument(doc_id=doc_id)
                db.add(existing)
            existing.class_ = row["category"]
            existing.tier = row["source_tier"]
            existing.last_verified = verified
            existing.ingestible = True
            existing.path = row["path"]
            existing.file_sha256 = digest
            existing.raw_content = content
            existing.source_title = metadata.get("source_name", "").strip() or doc_id
            existing.source_url = metadata.get("source_url", "").strip() or None
            existing.chunks.clear()
            for index, ((claim, ids, titles, urls), vector) in enumerate(zip(facts, vectors)):
                existing.chunks.append(Chunk(chunk_index=index, content=claim,
                                             source_ids=ids, source_titles=titles,
                                             source_urls=urls,
                                             embedding=list(vector)))
            db.commit()
            result["ingested"] += 1
        except (ValueError, OSError, UnicodeError, KeyError) as exc:
            db.rollback()
            result["rejected"].append({"doc_id": doc_id, "reason": str(exc)})
    # A retired document must stop appearing in answers after the next run.
    rejected_ids = {item["doc_id"] for item in result["rejected"]}
    active_ids = {row["id"] for row in rows if row.get("ingestible", "").lower() == "yes"
                  and row.get("status") == "verified" and row.get("id") not in rejected_ids}
    for document in db.scalars(select(KnowledgeDocument)).all():
        if document.doc_id not in active_ids:
            document.ingestible = False
    db.commit()
    return result


def local_embed(texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return model.encode(texts).tolist()


def retrieve(question: str, db: Session, embed=local_embed, limit=5, category=None):
    if db.bind.dialect.name != "postgresql":
        raise RuntimeError("Ask Ekiti vector search requires PostgreSQL with pgvector")
    if settings.ASK_EKITI_RETRIEVAL_MODE == "fulltext":
        from app.services.knowledge_fulltext import retrieve_fulltext
        return retrieve_fulltext(question, db, limit=limit, category=category)
    # An empty approved corpus should decline immediately, without downloading
    # or running the embedding model for a question that cannot be answered.
    eligible = select(KnowledgeDocument.id).where(KnowledgeDocument.ingestible.is_(True))
    if category:
        eligible = eligible.where(KnowledgeDocument.class_ == category)
    if db.scalar(eligible.limit(1)) is None:
        return []
    check_embedding_dimensions(db)
    vector = embed([question])[0]
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError("question embedding dimension mismatch")
    distance = Chunk.embedding.cosine_distance(vector)
    query = (select(Chunk, KnowledgeDocument, distance.label("distance"))
             .join(KnowledgeDocument).where(KnowledgeDocument.ingestible.is_(True),
                                            Chunk.embedding.is_not(None)))
    if category:
        query = query.where(KnowledgeDocument.class_ == category)
    hits = db.execute(query.order_by(distance).limit(limit)).all()
    return [{"doc_id": doc.doc_id, "content": chunk.content,
             "category": doc.class_, "source_ids": chunk.source_ids.split(";"),
             "source_titles": chunk.source_titles.split(";"),
             "source_urls": chunk.source_urls.split(";"),
             "source_url": doc.source_url, "tier": doc.tier,
             "last_verified": doc.last_verified.isoformat(), "path": doc.path,
             "distance": float(score)}
            for chunk, doc, score in hits if score is not None and score <= 0.65]
