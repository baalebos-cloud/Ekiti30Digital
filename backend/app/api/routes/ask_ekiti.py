from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from app.core.config import settings
from app.services.ask_answers import response
from app.services.knowledge_fulltext import retrieve_fulltext
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.knowledge_pipeline import retrieve

router = APIRouter(prefix="/api/ask-ekiti", tags=["ask_ekiti"])


@router.get("")
def ask_ekiti_status() -> dict:
    return {"status": "ready", "answer_mode": "sourced facts",
            "languages": ["en", "yo"] if settings.ASK_EKITI_YORUBA_REVIEWED else ["en"]}


class AskRequest(BaseModel):
    question: str = Field(max_length=10000)
    category: str | None = None
    language: Literal["en", "yo"] = "en"


@router.post("")
def ask_ekiti(request: AskRequest, db: Session = Depends(get_db)) -> dict:
    """Return only cited facts; language templates do not add factual claims."""
    if request.language == "yo" and not settings.ASK_EKITI_YORUBA_REVIEWED:
        raise HTTPException(status_code=503, detail="Yoruba responses await human review")

    def search(question, *, category, doc_ids, fact_kind, limit):
        if settings.ASK_EKITI_RETRIEVAL_MODE == "fulltext":
            if db.bind.dialect.name != "postgresql":
                raise RuntimeError("Ask Ekiti text search requires PostgreSQL")
            return retrieve_fulltext(question, db, category=category, doc_ids=doc_ids,
                                     fact_kind=fact_kind, limit=limit)
        return retrieve(
            question,
            db,
            category=category,
            doc_ids=doc_ids,
            fact_kind=fact_kind,
            limit=limit,
        )

    try:
        return response(request.question.strip(), request.language, search, request.category)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
