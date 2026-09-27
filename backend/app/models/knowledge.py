"""Ask Ekiti knowledge base storage models.

Infrastructure only: this is the storage layer for the knowledge base that
will back the Ask Ekiti assistant. Chunking and embedding generation are not
implemented here — see app/services/ingestion.py for the ingestion skeleton
and its TODOs.
"""

from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# Output dimension of the configured embedding model,
# paraphrase-multilingual-MiniLM-L12-v2 (384). Must match
# EMBEDDING_DIMENSIONS in app/core/config.py — changing the model or this
# value requires a new migration.
EMBEDDING_DIMENSIONS = 384


class KnowledgeDocument(Base):
    """A single sourced document from the knowledge base manifest."""

    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    # The manifest's `id` column (see app/services/ingestion.py).
    doc_id: Mapped[str] = mapped_column(unique=True, index=True)

    # Not present in kb_manifest.csv, so nullable until they're looked up
    # from elsewhere (see the TODO in ingest_documents).
    source_title: Mapped[str | None]
    source_url: Mapped[str | None]

    # The manifest's `category` column. `class` is a reserved word in
    # Python, so the attribute is `class_` while the DB column is `class`.
    class_: Mapped[str] = mapped_column("class")

    # The manifest's `source_tier` column.
    tier: Mapped[str]
    last_verified: Mapped[date] = mapped_column(Date)
    ingestible: Mapped[bool] = mapped_column(Boolean)

    # Source file path relative to 13_Knowledge_Base/, and its SHA-256 from
    # the manifest — the latter lets future ingestion skip unchanged files.
    path: Mapped[str | None]
    file_sha256: Mapped[str | None]

    # Source content prior to chunking. Nullable since a document row can
    # exist (from the manifest) before its content has been ingested.
    raw_content: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    """A chunk of a document's content, with its embedding vector."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE")
    )

    # Position of this chunk within the document's raw_content.
    chunk_index: Mapped[int]

    content: Mapped[str] = mapped_column(Text)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
