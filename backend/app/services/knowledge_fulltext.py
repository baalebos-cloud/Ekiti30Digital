"""PostgreSQL text retrieval without importing an embedding runtime."""
import re

from sqlalchemy import text


def search_text(question: str) -> str:
    # Source facts spell out Local Government Area; users often use LGA.
    # No topic terms, dates, or numbers are dropped to force a match.
    return re.sub(r"\blgas?\b", "local government area", question, flags=re.I)


SEARCH = text("""
    SELECT d.doc_id, c.content, d.class AS category, d.tier,
           d.last_verified, d.evidence_status,
           d.ask_ekiti_approved, d.ask_ekiti_approved_date,
           d.path, d.source_url,
           c.source_ids, c.source_titles, c.source_urls,
           ts_rank_cd(to_tsvector('english', c.content),
                      plainto_tsquery('english', :question)) AS search_rank
    FROM chunks AS c
    JOIN knowledge_documents AS d ON d.id = c.document_id
    WHERE d.ingestible IS TRUE
      AND (
            (
                d.evidence_status = 'verified'
                AND d.last_verified IS NOT NULL
                AND d.last_verified <= CURRENT_DATE
            )
            OR
            (
                d.ask_ekiti_approved IS TRUE
                AND d.ask_ekiti_approved_date IS NOT NULL
                AND d.ask_ekiti_approved_date <= CURRENT_DATE
            )
          )
      AND coalesce(c.source_ids, '') <> ''
      AND coalesce(c.source_titles, '') <> ''
      AND coalesce(c.source_urls, '') <> ''
      AND (CAST(:category AS text) IS NULL OR d.class = CAST(:category AS text))
      AND (CAST(:doc_ids AS text[]) IS NULL OR d.doc_id = ANY(CAST(:doc_ids AS text[])))
      AND (CAST(:fact_kind AS text) IS NULL
           OR (:fact_kind = 'identity' AND c.content ~ 'Local Government Area is one of the [0-9]+ Local Government Areas of Ekiti State\\.')
           OR (:fact_kind = 'headquarters' AND c.content LIKE '%Local Government Area''s headquarters is %.')
           OR (:fact_kind = 'creation' AND c.content LIKE 'Ekiti State was created on %.'))
      AND to_tsvector('english', c.content)
          @@ plainto_tsquery('english', :question)
    ORDER BY search_rank DESC, d.doc_id, c.chunk_index
    LIMIT :limit
""")


def retrieve_fulltext(question, db, limit=5, category=None, doc_ids=None, fact_kind=None):
    """Require all non-stopword search terms in the same cited fact.

    This intentionally returns no evidence when wording does not match.
    It does not combine document titles with unrelated fact text to make
    a match, and does not fall back to the embedding model.
    """
    rows = db.execute(SEARCH, {
        "question": search_text(question), "category": category,
        "limit": max(1, min(int(limit), 20)),
        "doc_ids": doc_ids or None, "fact_kind": fact_kind,
    }).mappings().all()
    hits = []
    for row in rows:
        hit = dict(row)
        for key in ("source_ids", "source_titles", "source_urls"):
            hit[key] = hit[key].split(";")
        hit["last_verified"] = (
            hit["last_verified"].isoformat()
            if hit.get("last_verified") else None
        )
        hit["ask_ekiti_approved_date"] = (
            hit["ask_ekiti_approved_date"].isoformat()
            if hit.get("ask_ekiti_approved_date") else None
        )
        hit["search_rank"] = float(hit["search_rank"])
        hits.append(hit)
    return hits
