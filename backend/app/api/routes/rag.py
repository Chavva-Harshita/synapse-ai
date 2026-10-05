from __future__ import annotations

from fastapi import APIRouter, HTTPException # type: ignore

from app.api.routes.rag_models import RAGChatRequest, RAGChatResponse
from app.core.config import settings
from app.services.file_service import find_stored_pdf
from app.services.ollama_client import (
    OllamaError,
    OllamaModelNotFoundError,
    OllamaUnavailableError,
)
from app.services.retriever import DocumentNotIndexedError, similarity_search_chunks
from app.services.response_generation import generate_grounded_reply
from app.services.vector_store import VectorStoreUnavailableError

router = APIRouter(tags=["rag"])


def _locate_stored_pdf(document_id: str) -> str:
    return find_stored_pdf(settings.upload_dir, document_id)


@router.post("/rag-chat", response_model=RAGChatResponse)
def rag_chat(req: RAGChatRequest) -> RAGChatResponse:
    """Retrieve upload-indexed chunks for one stored PDF and generate an answer."""
    document_id = str(req.document_id)
    try:
        _locate_stored_pdf(document_id)
        hits = similarity_search_chunks(
            req.message,
            top_k=req.top_k,
            document_id=document_id,
        )
        retrieved_chunks: list[dict] = []
        for h in hits:
            doc_chunk = h.get("doc")
            if doc_chunk is None:
                continue
            retrieved_chunks.append(
                {
                    "source_text": doc_chunk.page_content,
                    "metadata": dict(doc_chunk.metadata or {}),
                    "similarity": h.get("score"),
                }
            )

        if not retrieved_chunks:
            return RAGChatResponse(
                reply="I couldn't find relevant information in this document.",
                retrieved_chunks=[],
                document_id=document_id,
            )

        result = generate_grounded_reply(
            question=req.message,
            retrieved_chunks=retrieved_chunks,
        )

        return RAGChatResponse(
            reply=result.reply,
            retrieved_chunks=retrieved_chunks,
            document_id=document_id,
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found. Upload the PDF first.")
    except DocumentNotIndexedError:
        raise HTTPException(
            status_code=409,
            detail="This document has no indexed text chunks. Upload a readable, text-based PDF.",
        )
    except OllamaModelNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="The configured Ollama model is unavailable. Verify OLLAMA_MODEL.",
        ) from exc
    except OllamaUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable. Verify OLLAMA_HOST and that the configured model is running.",
        )
    except (VectorStoreUnavailableError, OllamaError):
        raise HTTPException(
            status_code=503,
            detail="The Chroma index or Ollama service is unavailable.",
        )
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).exception("RAG chat failed")
        raise HTTPException(status_code=500, detail="RAG chat failed unexpectedly.")
