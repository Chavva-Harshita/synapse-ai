from __future__ import annotations

from fastapi import APIRouter, HTTPException # type: ignore

from app.api.routes.rag_models import RAGChatRequest, RAGChatResponse
from app.services.embedding_pipeline import embed_and_store_pdf_chunks
from app.services.pdf_text_extractor import extract_pdf_text_from_path
from app.services.retriever import similarity_search_chunks
from app.services.response_generation import generate_grounded_reply

router = APIRouter(tags=["rag"])


def _locate_stored_pdf(document_id: str) -> str:
    # Mirror embeddings route's logic (stored file name uses doc['id']__ prefix)
    import os

    from app.core.config import settings

    prefix = f"{document_id}__"
    for name in os.listdir(settings.upload_dir):
        if name.startswith(prefix) and name.lower().endswith(".pdf"):
            return os.path.join(settings.upload_dir, name)
    raise FileNotFoundError("Stored PDF not found")


@router.post("/rag-chat", response_model=RAGChatResponse)
def rag_chat(req: RAGChatRequest) -> RAGChatResponse:
    """Single end-to-end workflow.

    Assumes the PDF is already uploaded and stored.
    Steps:
      1) Extract text
      2) Chunk + embed + store in Chroma
      3) Retrieve relevant chunks
      4) Generate grounded answer via Ollama
    """

    try:
        pdf_path = _locate_stored_pdf(req.document_id)
        text = extract_pdf_text_from_path(pdf_path)

        doc = {"id": req.document_id, "name": f"{req.document_id}.pdf"}
        embed_and_store_pdf_chunks(
            text=text,
            document=doc,
            chunk_size=1000,
            chunk_overlap=200,
        )

        hits = similarity_search_chunks(req.message, top_k=req.top_k)
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

        result = generate_grounded_reply(
            question=req.message,
            retrieved_chunks=retrieved_chunks,
            model="llama3",
        )

        return RAGChatResponse(
            reply=result.reply,
            retrieved_chunks=retrieved_chunks,
            document_id=req.document_id,
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found. Upload the PDF first.")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"RAG workflow failed: {e}")

