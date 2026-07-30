from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException # type: ignore

from app.core.config import settings
from app.services.embedding_pipeline import embed_and_store_pdf_chunks
from app.services.pdf_text_extractor import extract_pdf_text_from_path

router = APIRouter(tags=["embeddings"])


def _locate_stored_pdf(document_id: str) -> str:
    prefix = f"{document_id}__"
    for name in os.listdir(settings.upload_dir):
        if name.startswith(prefix) and name.lower().endswith(".pdf"):
            return os.path.join(settings.upload_dir, name)
    raise FileNotFoundError("Stored PDF not found")


@router.post("/embed-and-store")
def embed_and_store(document_id: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    try:
        pdf_path = _locate_stored_pdf(document_id)
        text = extract_pdf_text_from_path(pdf_path)

        # Minimal doc metadata (matches store_pdf structure)
        doc = {
            "id": document_id,
            "name": f"{document_id}.pdf",
        }

        result = embed_and_store_pdf_chunks(
            text=text,
            document=doc,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return {
            "stored": result["stored"],
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

