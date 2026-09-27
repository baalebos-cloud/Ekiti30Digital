from fastapi import APIRouter

router = APIRouter(prefix="/api/ask-ekiti", tags=["ask_ekiti"])


@router.get("")
def ask_ekiti_status() -> dict:
    """Placeholder for the Ask Ekiti AI assistant feature.

    TODO: wire up to the knowledge base / RAG pipeline (see
    13_Knowledge_Base/) once the AI/Data lead's ingestion service is
    ready in app/services/.
    """
    return {"message": "ask_ekiti endpoint not yet implemented"}
