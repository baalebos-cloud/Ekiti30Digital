from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.knowledge_pipeline import retrieve

router = APIRouter(prefix="/api/ask-ekiti", tags=["ask_ekiti"])


@router.get("")
def ask_ekiti_status() -> dict:
    return {"status": "ready", "answer_mode": "sourced facts"}


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    category: str | None = None
    language: str = "en"


@router.post("")
def ask_ekiti(request: AskRequest, db: Session = Depends(get_db)) -> dict:
    """Return sourced facts as the answer until the gateway contract is confirmed."""
    if request.language != "en":
        raise HTTPException(status_code=503, detail="Yoruba responses await human review")
    try:
        hits = retrieve(request.question, db, category=request.category)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not hits:
        return {"answer": "The available verified knowledge isn't enough to answer that yet.",
                "answer_status": "insufficient", "language": "en", "citations": []}
    return {"answer": " ".join(hit["content"] for hit in hits),
            "answer_status": "answered", "language": "en",
            "citations": [{key: hit[key] for key in ("doc_id", "source_ids", "source_titles",
                                                   "source_urls", "source_url", "category", "tier",
                                                   "last_verified", "path")}
                          for hit in hits]}
