# ask_ekiti_route_reference.py
#
# REFERENCE ONLY -- this file is not part of the FastAPI backend and is not
# imported by it. It exists because PR #38's reviewer asked us to either
# connect the retrieval layer to the backend route, or clearly isolate this
# PR as a tested retrieval foundation with a separate integration step.
# We're taking the second path deliberately: backend/app/api/routes/
# ask_ekiti.py belongs to Member 2 (Engineering Lead), and this repo copy
# has no visibility into the actual FastAPI app, its DB session dependency,
# or its auth setup. Editing that file blind risks breaking something we
# can't test. This shows the intended wiring so Member 2 can adapt it into
# the real route in a follow-up PR, or ask us to pair on it directly.
#
# What this demonstrates:
#   1. Loading kb_chunks.jsonl (or, once embeddings/pgvector are wired up,
#      querying the vector store instead -- see the swap point below).
#   2. Calling answer_question() from ask_ekiti_retrieval.py.
#   3. Gating on is_language_production_ready() before returning a Yoruba
#      answer to a real user (spec A8/A9.9).
#   4. Returning exactly the agreed API contract:
#      {answer, answer_status, language, citations[]}
#
# --------------------------------------------------------------------------
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
#
# from ask_ekiti_retrieval import (
#     answer_question,
#     is_language_production_ready,
#     load_chunks,
#     KeywordRetriever,
#     # EmbeddingRetriever,  # add once Member 2 confirms the provider;
#                            # must implement the same Retriever.score()
#                            # interface -- nothing else in this route changes.
# )
#
# router = APIRouter()
#
#
# class AskRequest(BaseModel):
#     question: str
#     language: str = "en"
#
#
# class Citation(BaseModel):
#     doc_id: str
#     source_ids: list[str]
#     source_titles: str
#     tier: str
#     last_verified: str
#     path: str
#
#
# class AskResponse(BaseModel):
#     answer: str
#     answer_status: str  # "answered" | "insufficient" | "conflict"
#     language: str
#     citations: list[Citation]
#
#
# # Load once at startup, not per request. Swap this for a pgvector query
# # once embeddings are wired up; answer_question()'s signature does not
# # change, only what's passed as `chunks` (or a DB-backed Retriever).
# _CHUNKS = load_chunks("13_Knowledge_Base/kb_chunks.jsonl")
# _RETRIEVER = KeywordRetriever()  # swap for an EmbeddingRetriever later
#
#
# @router.post("/api/ask-ekiti", response_model=AskResponse)
# def ask_ekiti(req: AskRequest) -> AskResponse:
#     if req.language not in ("en", "yo"):
#         raise HTTPException(400, "language must be 'en' or 'yo'")
#     if not is_language_production_ready(req.language):
#         # Do not serve an unreviewed Yoruba answer to a real user.
#         # Adjust this fallback to whatever the frontend expects for a
#         # not-yet-available language (spec A8/A9.9 requires human review
#         # before shipping Yoruba responses).
#         raise HTTPException(503, "Yoruba responses are not yet reviewed for production")
#     result = answer_question(req.question, _CHUNKS, retriever=_RETRIEVER, language=req.language)
#     return AskResponse(**result)
# --------------------------------------------------------------------------
#
# Open items for whoever wires this in for real:
#   - _CHUNKS is currently loaded from a static file; decide whether the
#     backend re-reads it on a schedule/webhook after re-ingestion, or reads
#     from Postgres directly once chunks are stored there instead of a
#     JSONL file.
#   - Confirm ASK_EKITI_EMBEDDING_DIM (see ask_ekiti_retrieval.py) matches
#     whatever column dimension the pgvector migration uses, before either
#     side hard-codes a number.
#   - Add the citation-object mapping to whatever shape the frontend's
#     /ask-ekiti page currently expects, if it differs from Citation above.
