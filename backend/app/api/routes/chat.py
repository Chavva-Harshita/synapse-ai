from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel, Field, field_validator # type: ignore

from app.core.config import settings
from app.services.file_service import find_stored_pdf
from app.services.ollama_client import OllamaError
from app.services.retriever import DocumentNotIndexedError, similarity_search_chunks
from app.services.response_generation import generate_grounded_reply
from app.services.vector_store import VectorStoreUnavailableError

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    document_ids: Optional[List[UUID]] = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Question must not be empty")
        return normalized


class ChatResponse(BaseModel):
    reply: str
    retrieved_chunks: list[dict]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Grounded chat using local Ollama via retrieved Chroma context.

    Grounding requirement:
    - Ollama is instructed: "If answer is not in context, say you do not know." (see prompt template).
    """

    try:
        if req.document_ids:
            document_ids = list(dict.fromkeys(str(doc_id) for doc_id in req.document_ids))
            for document_id in document_ids:
                find_stored_pdf(settings.upload_dir, document_id)
            hits = []
            for document_id in document_ids:
                hits.extend(
                    similarity_search_chunks(
                        req.message,
                        top_k=5,
                        document_id=document_id,
                    )
                )
            hits.sort(key=lambda hit: hit["score"])
            hits = hits[:5]
        else:
            hits = similarity_search_chunks(req.message, top_k=5)

        retrieved_chunks: list[dict] = []
        for h in hits:
            doc = h.get("doc")
            if doc is None:
                continue

            retrieved_chunks.append(
                {
                    "source_text": doc.page_content,
                    "metadata": dict(doc.metadata or {}),
                    "similarity": h.get("score"),
                }
            )

        if not retrieved_chunks:
            return ChatResponse(
                reply="I couldn't find relevant information in the indexed documents.",
                retrieved_chunks=[],
            )

        result = generate_grounded_reply(
            question=req.message,
            retrieved_chunks=retrieved_chunks,
        )
        return ChatResponse(reply=result.reply, retrieved_chunks=retrieved_chunks)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="One or more documents were not found.")
    except DocumentNotIndexedError:
        raise HTTPException(
            status_code=409,
            detail="One or more selected documents have no indexed text chunks.",
        )
    except (OllamaError, VectorStoreUnavailableError):
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable. Check the Chroma index and Ollama configuration.",
        )
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).exception("Chat generation failed")
        raise HTTPException(status_code=500, detail="Chat generation failed unexpectedly.")
