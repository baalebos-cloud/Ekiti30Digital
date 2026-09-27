from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
def get_health() -> dict:
    """Simple liveness check used to verify the backend is running."""
    return {"status": "ok"}
