import logging

from fastapi import APIRouter # type: ignore
from fastapi.responses import JSONResponse # type: ignore

from app.core.config import settings
from app.services.ollama_client import configured_model_is_available
from app.services.vector_store import VectorStoreManager

router = APIRouter(tags=["health"])
log = logging.getLogger(__name__)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def readiness() -> JSONResponse:
    """Check the local dependencies required to index and answer RAG requests."""
    dependencies = {
        "chroma": "unavailable",
        "embeddings": "unavailable",
        "ollama": "unavailable",
    }
    indexed_chunks: int | None = None
    try:
        manager = VectorStoreManager()
        vector_store = manager.build_or_load(create_if_missing=True)
        manager.check_embedding_model()
        indexed_chunks = vector_store._collection.count()
        dependencies["chroma"] = "ready"
        dependencies["embeddings"] = "ready"
    except Exception:
        log.exception("Readiness check failed for Chroma or embeddings")

    if configured_model_is_available():
        dependencies["ollama"] = "ready"

    ready = all(status == "ready" for status in dependencies.values())
    content = {
        "status": "ready" if ready else "not_ready",
        "dependencies": dependencies,
        "indexed_chunks": indexed_chunks,
    }
    return JSONResponse(status_code=200 if ready else 503, content=content)
