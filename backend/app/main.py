from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from app.api.routes.chat import router as chat_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.retrieval import router as retrieval_router
from app.api.routes.rag import router as rag_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Synapse AI API",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ROUTES
    app.include_router(health_router, prefix="/api")
    app.include_router(files_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(embeddings_router, prefix="/api")
    app.include_router(retrieval_router, prefix="/api")
    app.include_router(rag_router, prefix="/api")

    return app


app = create_app()